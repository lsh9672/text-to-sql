import os
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv, find_dotenv
from app.config import db_config

load_dotenv(find_dotenv()) #환경 변수 로드하기.

class PostgresManager:
    
    _connection_string = None
    _engine = None
    
    #디비 접속 정보 및 open AI 키 로드
    def __init__(self):
        
        #싱글톤으로 매번 커넥션을 맽지 않도록 함.
        if PostgresManager._engine is None:
            self._initialize_connection_pool()
    
    
    
    def _initialize_connection_pool(self):
        PostgresManager._connection_string = (
            f"postgresql+psycopg://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
            )
        
        # SQLAlchemy 엔진으로 커넥션 풀 생성
        PostgresManager._engine = create_engine(
            PostgresManager._connection_string,
            poolclass=QueuePool,
            pool_size=5,        # 기본 커넥션 수
            max_overflow=10,    # 추가 커넥션 수
            pool_timeout=30,    # 대기 시간
            pool_recycle=3600,  # 1시간마다 커넥션 재생성
            pool_pre_ping=True  # 커넥션 유효성 체크
        )
   
    
    @property
    def engine(self):
        return PostgresManager._engine
    

    
    @classmethod
    def close_all_connections(cls):
        """모든 커넥션 정리"""
        if cls._engine:
            cls._engine.dispose()
            cls._engine = None
            cls._connection_string = None
        
