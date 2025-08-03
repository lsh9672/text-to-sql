import asyncio
from typing import List, Dict, Any
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from mcp.client.stdio import stdio_client
from mcp import ClientSession
from app.infra.external.mcptool.mcp_langchain_convert import DynamicMCPTool



class LangGraphMCPAgent:
    """LangGraph 기반 MCP SQL Agent"""

    def __init__(self, mcp_server_command: List[str], openai_api_key: str):
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model="gpt-4o",
            temperature=0.1
        )
        self.agent = None
        self.tools = []

    async def initialize(self):
        """Agent 초기화"""
        # MCP 도구들을 LangChain 도구로 변환
        self.tools = await DynamicMCPTool.convert_mcp_tools_to_langchain()
        
        # LangGraph Agent 생성
        self.agent = create_react_agent(self.llm, self.tools)
        
        print(f"✅ LangGraph MCP Agent 초기화 완료 ({len(self.tools)}개 도구)")

    async def generate_sql(self, question: str) -> str:
        """사용자 질문을 SQL로 변환하고 실행"""
        if not self.agent:
            await self.initialize()

        try:
            response = await self.agent.ainvoke({
                "messages": [HumanMessage(content=f"""
PostgreSQL 데이터베이스에 대한 질문입니다. 다음 단계로 처리해주세요:

1. 먼저 database_info로 데이터베이스 기본 정보 확인
2. tables_info로 관련 테이블들을 확인
3. 필요한 테이블의 column_info로 컬럼 구조 파악
4. SQL 쿼리 생성
5. sql_validation으로 구문 검증 (옵션)
6. 최종 SQL과 설명 반환

사용자 질문: {question}
""")]
            })
            
            return response["messages"][-1].content
            
        except Exception as e:
            return f"처리 중 오류 발생: {str(e)}"