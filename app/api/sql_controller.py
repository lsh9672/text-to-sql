from app.core.service import SqlGenerationService, SqlGenerationMcpService
from app.di_container import DIContainer
from app.api.model.request import SQLRequest, SQLMcpRequest
from app.api.model.response import SQLResponse
from fastapi import APIRouter, Request



router = APIRouter()

@router.post("/generation", response_model = SQLResponse)
def generate_sql(request: SQLRequest) -> SQLResponse:
    
    sqlGenService = DIContainer.get(SqlGenerationService)
    """자연어 질문을 SQL로 변환하여 응답함."""
    llmResponse = sqlGenService.generate_sql(
        prompt_type = request.explain,
        question = request.question,
        k = request.k
    )
    
    #응답 형식으로 변경
    return SQLResponse(
        sql_query = llmResponse,
        success = True,
        message="SQL 생성 성공"
    )

## agent를 사용한 방식.
@router.post("/generation/agent", response_model = SQLResponse)
async def generate_mcp_sql(request: SQLMcpRequest) -> SQLResponse:
    
    sqlMcpGenService = DIContainer.get(SqlGenerationMcpService)
    
    """자연어 질문을 SQL로 변환하여 응답함 - mcp 사용"""
    llmResponse = await sqlMcpGenService.generate_sql(
        question = request.question,
    )
    
    #응답 형식으로 변경
    return SQLResponse(
        sql_query = llmResponse,
        success = True,
        message="SQL 생성 성공"
    )
    

    
    
@router.get("/health")
async def health_check():
    """서비스 상태 확인"""
    return {"status": "healthy", "service": "sql-generation"}
    
    


