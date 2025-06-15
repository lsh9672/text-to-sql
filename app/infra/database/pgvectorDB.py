import os
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv, find_dotenv
from langchain_openai import OpenAIEmbeddings
from app.config import vector_db_config

load_dotenv(find_dotenv()) #환경 변수 로드하기.

class PGVectorManager:
    
    _connection_string = None #멤버변수 선언(java static 개념)
    _embeddings = None
    _engine = None
    
    #디비 접속 정보 및 open AI 키 로드
    def __init__(self):
        
        #싱글톤으로 매번 커넥션을 맽지 않도록 함.
        if PGVectorManager._engine is None:
            self._initialize_connection_pool()
    
    
    
    def _initialize_connection_pool(self):
        PGVectorManager._connection_string = (
            f"postgresql+psycopg://{vector_db_config['user']}:{vector_db_config['password']}@{vector_db_config['host']}:{vector_db_config['port']}/{vector_db_config['database']}"
            )
        
        # SQLAlchemy 엔진으로 커넥션 풀 생성
        PGVectorManager._engine = create_engine(
            PGVectorManager._connection_string,
            poolclass=QueuePool,
            pool_size=5,        # 기본 커넥션 수
            max_overflow=10,    # 추가 커넥션 수
            pool_timeout=30,    # 대기 시간
            pool_recycle=3600,  # 1시간마다 커넥션 재생성
            pool_pre_ping=True  # 커넥션 유효성 체크
        )
        #OpenAI 임베딩도 한 번만 초기화
        PGVectorManager._embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            model="text-embedding-3-small"
        )
    
    @property
    def engine(self):
        return PGVectorManager._engine
    
    @property
    def connection_string(self):
        return PGVectorManager._connection_string
    
    @classmethod
    def close_all_connections(cls):
        """모든 커넥션 정리"""
        if cls._engine:
            cls._engine.dispose()
            cls._engine = None
            cls._connection_string = None
        
