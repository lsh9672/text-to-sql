from langchain.prompts import PromptTemplate
from langfuse import Langfuse
from langfuse.callback import CallbackHandler
from app.infra.external.mcptool.postgres_mcp_client import PostgresMcpClient
import os


class SqlGenerationMcpService:
    
    def __init__(self):
        
        self.sql_agent = PostgresMcpClient()
        
        ##Langfuse 클라이언트 생성.
        self.langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST")
        )
        
        self.langfuse_handler = CallbackHandler()
        
    
    ##응답 쿼리에서 코드블럭 제거
    def delete_code_block_sql(self, sql_response:str) -> str:
        
        if sql_response.startswith('```sql'):
            sql_response = sql_response[0:3] + sql_response[6:]
        
        if sql_response.endswith('```'):
            sql_response = sql_response[:-3]
            
        return sql_response.strip()
    
    ##응답 쿼리에서 코드블럭 제거
    def delete_code_block(self, sql_response:str) -> str:
        
        if sql_response.startswith('```sql'):
            sql_response = sql_response[6:]
        
        if sql_response.endswith('```'):
            sql_response = sql_response[:-3]
            
        return sql_response.strip()
    
    async def generate_sql(self, question: str) -> str:
        
        
        if not self.sql_agent.is_ready():
            await self.sql_agent.initialize()

        result = await self.sql_agent.query(question)

        return result
        
    