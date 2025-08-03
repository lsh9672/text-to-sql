import os
import logging
import asyncio
import httpx
from typing import List, Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.tools import BaseTool, tool
from langfuse import Langfuse
from langfuse.callback import CallbackHandler


class PostgresMcpClient:
    
    """Text-to-SQL 전문 에이전트 - MCP 연동부터 실행까지 모든 설정을 담당"""
    
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.1):
        self.model = ChatOpenAI(
            model=model_name,
            temperature=temperature
        )
        self.agent = None
        self.tools: List[BaseTool] = []
        self.mcp_server_url = os.getenv("MCP_SERVER_URL")
        self.session = None #mcp 세션유지하기.
        self.read = None #mcp서버로부터 읽어오기 위한 read스트림
        self.write = None #클라이언트(fast api)에서 mcp서버로 요청을 쓰기 위한 write스트림.
        self.sse_context = None
        
        
        ## TODO : mcp 클라이언트의 경우에는 싱글톤으로 되어있지 않아서 나중에 변경 필요.
        ##Langfuse 클라이언트 생성.
        self.langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST")
        )
        
        self.langfuse_handler = CallbackHandler()
        
        
        ## TODO : langfuse에서 관리할 수 있도록 변경해야 함.
        self.system_prompt = self.langfuse.get_prompt("mcp_system_prompt", cache_ttl_seconds=0).prompt
    
    async def _load_mcp_tools(self) -> List[BaseTool]:
        """MCP 서버에서 도구를 로드합니다."""     
        try:
            
            self.sse_context = sse_client(self.mcp_server_url)
            self.read, self.write = await self.sse_context.__aenter__()
            
            self.session = ClientSession(self.read, self.write)
            await self.session.__aenter__()
            await self.session.initialize()
            
            tools = await load_mcp_tools(self.session)
            logging.info(f"✅ MCP 서버에서 {len(tools)}개 도구 로드 완료")
                
            return tools
                
        except httpx.ConnectError as e:
            error_msg = f"MCP 서버에 연결할 수 없습니다: {self.mcp_server_url}"
            logging.error(error_msg)
            raise ConnectionError(error_msg) from e
        except httpx.TimeoutException as e:
            error_msg = f"MCP 서버 연결 시간 초과: {self.mcp_server_url}"
            logging.error(error_msg)
            raise TimeoutError(error_msg) from e
        except Exception as e:
            error_msg = f"MCP 도구 로드 중 예상치 못한 오류 발생: {str(e)}"
            logging.error(error_msg)
            raise Exception(error_msg) from e
    
    async def initialize(self):
        """에이전트 초기화 - MCP 도구 로드 및 에이전트 생성"""
        print("🚀 Text-to-SQL Agent 초기화 중...")
        
        # MCP 도구 로드
        self.tools = await self._load_mcp_tools()
        
        if not self.tools:
            raise Exception("사용 가능한 MCP 도구가 없습니다.")
        
        # LangGraph 에이전트 생성
        self.agent = create_react_agent(self.model, self.tools)
        
        print("✅ 에이전트 초기화 완료!")
        print(f"📦 사용 가능한 도구: {', '.join([tool.name for tool in self.tools])}")
    
    async def query(self, user_question: str) -> str:
        """사용자 질문을 처리하고 결과를 반환합니다."""
        if not self.agent:
            raise Exception("에이전트가 초기화되지 않았습니다. initialize()를 먼저 호출하세요.")
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_question}
        ]
        
        result = await self.agent.ainvoke(
            {"messages": messages},
            config={"callbacks": [self.langfuse_handler]}
        )
        
        print("🔍 전체 대화 과정:")
        for i, msg in enumerate(result["messages"]):
            print(f"  {i+1}. {type(msg).__name__}: {msg.content[:100]}...")
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    print(f"    🔧 도구 호출: {tool_call['name']}({tool_call['args']})")
        
        print(f"llm 응답 => {result}")
        return result["messages"][-1].content
    
    def is_ready(self) -> bool:
        """에이전트가 사용 준비되었는지 확인"""
        return self.agent is not None
    
    def get_available_tools(self) -> List[str]:
        """사용 가능한 도구 목록 반환"""
        return [tool.name for tool in self.tools]
    
    
    async def cleanup(self):
        """세션 정리"""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
                self.session = None
            if self.sse_context:
                await self.sse_context.__aexit__(None, None, None)
                self.sse_context = None
            
            self.read = None
            self.write = None
        except Exception as e:
            logging.warning(f"정리 중 오류: {e}")
            
    ##async 요청시 사용하는 컨텍스트 매니저
    async def __aenter__(self):
        await self.initialize()
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self.cleanup()
