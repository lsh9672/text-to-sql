import json
from typing import Dict, Any
from app.config import catalog_quries
from app.infra.database import PostgresManager
from app.core.interface import DBCatalogExtractor
from sqlalchemy import text

class PostgreSQLCatalogRepository(DBCatalogExtractor):
    
    #디비 접속 정보 입력 받기.
    def __init__(self):
        self.connection_manager = PostgresManager()
        
        
    ##카탈로그 정보 추출(postgresql에서 테이블 카탈로그 추출후에 변환.)
    def extractCatalog(self) -> Dict[str, Any]:
        
        with self.connection_manager.engine.connect() as connection:
            
            database_catalog_json = {}
        
            ##데이터 베이스명 조회.
            database_info = connection.execute(text(catalog_quries['database_info'])).fetchone()
            
            ## json에 데이터베이스 정보 담기.
            database_catalog_json['database_name'] = database_info.database
            database_catalog_json['description'] = database_info.comment
            
            ##스키마 조회
            schema_info = connection.execute(text(catalog_quries['schema_info'])).fetchall()
            
            schemas = []
            for temp_schema in schema_info:
                
                if not temp_schema: return database_catalog_json
                
                ##스키마 명 넣기.
                schema_dict = {
                    'schema_name' : temp_schema.schema_name,
                    'description' : temp_schema.comment
                }
            
            
                ##테이블 정보
                table_info_list = []
            
                ##테이블 정보 조회.
                table_info = connection.execute(text(catalog_quries['table_info']), {'schema_name': temp_schema.schema_name}).fetchall()
                
                
                for temp_table in table_info:
                    
                    table_dict = {
                        'table_name' : temp_table.table_name,
                        'description' : temp_table.table_comment,
                        'table_type' : temp_table.table_type,
                    }
                    
                    ##컬럼 정보 담기
                    column_info_list = []
                    
                    ##컬럼 정보 조회.
                    column_info = connection.execute(text(catalog_quries['column_info']),{'table_name': temp_table.table_name}).fetchall()
                    
                    for temp_column in column_info:
                        
                        column_dict = {
                            'column_name': temp_column.column_name,
                            'data_type' : temp_column.data_type,
                            'is_nullable' : temp_column.is_nullable,
                            'is_primary_key' : temp_column.is_primary_key,
                            'description' : temp_column.column_comment,
                            'column_default' : temp_column.column_default,
                            'character_maximum_length' : temp_column.character_maximum_length,
                            'numeric_precision' : temp_column.numeric_precision
                        }
                        
                        column_info_list.append(column_dict)
                        
                    table_dict['columns'] = column_info_list
                    table_info_list.append(table_dict)
                    
                schema_dict['tables'] = table_info_list
                schemas.append(schema_dict)
                
            database_catalog_json['schemas'] = schemas
            
        return database_catalog_json