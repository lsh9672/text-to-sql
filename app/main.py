from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.sql_controller import router as llm_sql_router
from app.api.rag_controller import router as rag_router
from app.api.slack_controller import router as slack_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🚀 애플리케이션 시작 시 실행
    print("애플리케이션 시작 - 의존성 주입 설정")
    setup_dependencies()
    yield
    # 🔒 애플리케이션 종료 시 실행  
    print("애플리케이션 종료 - 리소스 정리")
    cleanup_resources() 


app = FastAPI(title="RAG SQL API", version="1.0.0",lifespan=lifespan)


def setup_dependencies():
    from app.infra.repository import PGVectorRepositoryImpl, PostgreSQLCatalogRepository
    from app.core.service import SqlGenerationService
    from app.core.service.rag_generation_service import RagGenerationService
    from app.core.service.catalog_document_converter import CatalogDocumentConverter
    from app.core.interface import RagRepository, DBCatalogExtractor
    from app.di_container import DIContainer
    
    
    DIContainer.register(RagRepository, PGVectorRepositoryImpl())
    DIContainer.register(DBCatalogExtractor, PostgreSQLCatalogRepository())
    DIContainer.register(SqlGenerationService, SqlGenerationService())
    DIContainer.register(CatalogDocumentConverter, CatalogDocumentConverter())
    DIContainer.register(RagGenerationService, RagGenerationService())
    
    

def cleanup_resources():
    ## TODO : 디비 정리등 리소스 정리를 만들어야 함.
    pass
    

# 라우터 등록
## TODO : rag의 경우에는 배치 처리 할 예정
app.include_router(rag_router, prefix="/api/rag", tags=["RAG"])
app.include_router(llm_sql_router, prefix="/api/sql", tags=["SQL"])
app.include_router(slack_router, prefix="/api/slack", tags=["SLACK"])



