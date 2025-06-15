from abc import ABC, abstractmethod
## 타입 명시를 위해 import
from typing import List
from langchain_core.documents import Document
from langchain_postgres import PGVector

class RagRepository(ABC):
    
    @abstractmethod
    def build_vector_storage(self, collection_name: str, documents: List[Document]) -> PGVector:
        pass
    
    @abstractmethod
    def existing_vector_store(self, collection_name: str) -> PGVector:
        pass
    
    def similarity_search_with_score(self, collection_name: str, query:str, k:int = 5) -> List[Document]:
        pass
    
    def similarity_search(self, collection_name: str, query:str, k:int = 5) -> List[tuple]:
        pass