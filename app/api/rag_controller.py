from app.core.service.rag_generation_service import RagGenerationService
from app.di_container import DIContainer
from app.api.model.response import RAGResponse
from app.api.model.request import RAGRequest
from fastapi import APIRouter


router = APIRouter()

@router.post("/generation/vector", response_model = RAGResponse)
def generate_rag(request : RAGRequest) -> RAGResponse:
    
    ragGenService = DIContainer.get(RagGenerationService)
    
    ragGenService.generation_rag(collection_name = request.collection_name)
    
    
    #응답 형식으로 변경
    return RAGResponse(
        message="SQL 생성 성공"
    )
    
@router.get("/health")
async def health_check():
    """서비스 상태 확인"""
    return {"status": "healthy", "service": "rag-generation"}
    
    


