from pydantic import BaseModel

class RAGResponse(BaseModel):
    message: str = "rag 생성 성공"