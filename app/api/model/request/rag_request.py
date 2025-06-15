from pydantic import BaseModel

class RAGRequest(BaseModel):
    collection_name: str