import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from app.config import sql_prompt, sql_explain_prompt
# from app.config import vector_db_config


load_dotenv(find_dotenv()) #환경 변수 로드하기.

class OpenAIChatClient:
    
    _llm = None
    
    #open AI 키 로드
    def __init__(self):
        
        #싱글톤으로 매번 커넥션을 맽지 않도록 함.
        if OpenAIChatClient._llm is None:
            self._initialize_embeddings()
    
    
    def _initialize_embeddings(self):
        
        openai_api_key = os.getenv('OPENAI_API_KEY')
    
        
        if not openai_api_key:
            raise ValueError("OPENAI API KEY가 없습니다.")
    
        #OpenAI chat도 한 번만 초기화
        OpenAIChatClient._llm = ChatOpenAI(
            openai_api_key = openai_api_key,
            model = "gpt-4o-mini",
            temperature = 0
        )
        
        #TODO : 추후에 별도의 파일로 뺴는게 좋을 듯
        #프롬프트 설정
        OpenAIChatClient._prompt_template = PromptTemplate(
            input_variables = ["context","question"],
            template = sql_prompt
        )
        
    @property
    def chat_llm(self):
        return OpenAIChatClient._llm