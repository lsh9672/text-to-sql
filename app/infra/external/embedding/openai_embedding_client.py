import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import OpenAIEmbeddings
# from app.config import vector_db_config

load_dotenv(find_dotenv()) #환경 변수 로드하기.

class OpenAIEmbeddingClient:
    
    _embeddings = None
    
    #디비 접속 정보 및 open AI 키 로드
    def __init__(self):
        
        #싱글톤으로 매번 커넥션을 맽지 않도록 함.
        if OpenAIEmbeddingClient._embeddings is None:
            self._initialize_embeddings()
    
    
    
    def _initialize_embeddings(self):
    
        #OpenAI 임베딩도 한 번만 초기화
        OpenAIEmbeddingClient._embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            model="text-embedding-3-small"
        )
        
    @property
    def embeddings(self):
        return OpenAIEmbeddingClient._embeddings
    