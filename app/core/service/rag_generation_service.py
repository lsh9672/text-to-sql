from app.di_container import DIContainer
from app.core.interface import DBCatalogExtractor, RagRepository
from app.core.service import CatalogDocumentConverter
import json


class RagGenerationService:
    
    def __init__(self):
        self.catalog_converter_service = DIContainer.get(CatalogDocumentConverter)
        self.catalog_extractor_repository = DIContainer.get(DBCatalogExtractor)
        self.vector_repository = DIContainer.get(RagRepository)
    
    def generation_rag(self, collection_name : str):
        
        #1. 카탈로그 추출
        catalog_data = self.catalog_extractor_repository.extractCatalog()
        
        #2 . Document로 변환
        ## 데이터 전달시에는 json으로 전달 - 해당 메서드는 추후에 다른 파일형태로 전달받는 것도 고려해서 json을 받도록 함.
        catalog_document_list = self.catalog_converter_service.convert_to_documents(json.dumps(catalog_data))
        
        #3. 임베딩 후 vector디비에 넣기.
        self.vector_repository.build_vector_storage(
            collection_name = collection_name, 
            documents = catalog_document_list
        )
        
        
        