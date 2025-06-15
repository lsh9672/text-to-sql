from langchain.prompts import PromptTemplate
from app.infra.external.llm import OpenAIChatClient
from app.core.interface import RagRepository
from app.di_container import DIContainer

from app.config import sql_prompt, sql_explain_prompt


class SqlGenerationService:
    
    def __init__(self):
        
        self.chat_client = OpenAIChatClient()
        self.vector_repository = DIContainer.get(RagRepository)
        
    
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
    
    def generate_sql(self, prompt_type: bool, question: str, k: int = 5) -> str:

        #컬렉션은 우선 고정
        ## TODO : 추후에 여러 rag를 참조하려고 하면 컬렉션을 입력으로 받아야 할듯.
        collection_name = "catalog_data"
        
        #1. llm에 요청할 지식 검색
        search_docs = self.vector_repository.similarity_search(
            collection_name = collection_name, 
            query = question, 
            k=k
        )
        
        #2. 검색해서 나온 지식을 정리(컨텍스트 구성)
        context = ""
        for i, doc in enumerate(search_docs, 1):
            context += f"=== 참고 정보 {i} ===\n"
            context += doc.page_content + "\n\n"
    
        #TODO : 추후에 별도의 파일로 뺴는게 좋을 듯
        #3. 사용자 입력에 따라 sql 추출이유 설명 프롬프트와 sql만 추출하는 프롬프트로 구분.
        self.prompt_template = PromptTemplate(
            input_variables = ["context","question"],
            template = sql_explain_prompt if prompt_type else sql_prompt
        )
        
        ##4. LLM에 프롬프트 전달.
        prompt = self.prompt_template.format(
            context = context,
            question = question
        )
        
        #5. llm에 프롬프트 전달.    
        llm_response = self.chat_client.chat_llm.invoke(prompt)
        
        # 데이터가 코드블럭 형태로 오기 때문에 슬랙에 넘겨주면 코드블럭으로 보기 편할듯.
        # 응답쿼리를 바로 실행하는 기능을 만들라면 코드블럭 데이터 제거가 필요할 듯.
        sql_response = self.delete_code_block_sql(llm_response.content)
    
        return sql_response
        
    