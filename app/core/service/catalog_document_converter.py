import json
from typing import List, Dict, Any
from langchain_core.documents import Document

class CatalogDocumentConverter:
    def __init__(self):
        pass
            
    def convert_to_documents(self, catalog_json_data : json) -> List[Document]:
        """카탈로그를 Document 리스트로 변환"""
        
        catalog_dict_data = json.loads(catalog_json_data)
        
        documents = []
        
        for schema in catalog_dict_data['schemas']:
            for table in schema['tables']:
                # 1. 테이블 Document 생성
                table_doc = self._create_table_document(catalog_dict_data, schema, table)
                documents.append(table_doc)
                
                # 2. 각 컬럼 Document 생성
                for column in table['columns']:
                    column_doc = self._create_column_document(catalog_dict_data, schema, table, column)
                    documents.append(column_doc)
        
        return documents

    ##테이블 정보를 도큐먼트 형태로 만듦.
    def _create_table_document(self, catalog_data : Dict, schema: Dict, table: Dict) -> Document:
            """테이블 전체 정보 Document"""
            table_name = table['table_name']
            schema_name = schema['schema_name']
            
            # 컬럼 목록 요약
            column_summary = []
            for col in table['columns']:
                nullable = "NULL가능" if col['is_nullable'] == 'YES' else "NOT NULL불가능"
                default = f", 기본값: {col['column_default']}" if col['column_default'] else ""
                column_summary.append(f"  - {col['column_name']}: {col['data_type']} ({nullable}){default} - {col['description']}")
            
            content = f"""
                        테이블: {schema_name}.{table_name}
                        설명: {table['description']}
                        테이블 타입: {table['table_type']}

                        컬럼 정보 ({len(table['columns'])}개):
                        {chr(10).join(column_summary)}

                        비즈니스 용도:
                        - {table['description']}
                        - Y박스 서비스의 {self._get_business_domain(table_name)} 관련 데이터 저장
                        """.strip()
            
            return Document(
                page_content=content, #vector화 될 내용.
                metadata={
                    'type': 'table',
                    'database': catalog_data['database_name'],
                    'schema': schema_name,
                    'table': table_name,
                    'full_name': f"{schema_name}.{table_name}",
                    'column_count': len(table['columns'])
                } #필터링에 사용할 조건(llm으로 넘길 내용)
            )
            
    def _create_column_document(self, catalog_data : Dict, schema: Dict, table: Dict, column: Dict) -> Document:
            """컬럼 상세 정보 Document"""
            schema_name = schema['schema_name']
            table_name = table['table_name']
            column_name = column['column_name']
            
            # 컬럼 상세 정보
            nullable_text = "NULL 허용" if column['is_nullable'] == 'YES' else "필수 입력"
            
            # 길이/정밀도 정보
            size_info = ""
            if column.get('character_maximum_length'):
                size_info = f", 최대길이: {column['character_maximum_length']}"
            elif column.get('numeric_precision'):
                size_info = f", 정밀도: {column['numeric_precision']}"
            
            # 기본값 정보
            default_info = ""
            if column['column_default']:
                if 'nextval' in column['column_default']:
                    default_info = "자동증가 값"
                elif column['column_default'] == 'now()':
                    default_info = "현재 시간 자동 설정"
                else:
                    default_info = f"기본값: {column['column_default']}"
            
            content = f"""
                        컬럼: {schema_name}.{table_name}.{column_name}
                        소속 테이블: {table_name} ({table['description']})
                        데이터 타입: {column['data_type']}{size_info}
                        제약 조건: {nullable_text}
                        {default_info}

                        설명: {column['description']}

                        비즈니스 의미:
                        - {self._get_column_business_meaning(table_name, column_name, column['description'])}
                        - {table['description']}에서 {column['description']} 역할
                        """.strip()
                        
            print(content)
            
            return Document(
                page_content=content,
                metadata={
                    'type': 'column',
                    'database': catalog_data['database_name'],
                    'schema': schema_name,
                    'table': table_name,
                    'column': column_name,
                    'data_type': column['data_type'],
                    'full_name': f"{schema_name}.{table_name}.{column_name}"
                }
            )
    def _get_business_domain(self, table_name: str) -> str:
        """테이블명으로 비즈니스 도메인 추론"""
        domain_map = {
            'tb_gift': '상품/선물',
            'tb_user': '사용자/회원',
            'tb_event': '이벤트/프로모션',
            'tb_entry': '응모/참여',
            'tb_issue': '발행/지급'
        }
        
        for key, domain in domain_map.items():
            if key in table_name:
                return domain
        return '기타'

    def _get_column_business_meaning(self, table_name: str, column_name: str, description: str) -> str:
        
        # 공통 컬럼 패턴
        if column_name in ['reg_dt', 'mod_dt']:
            return "데이터 등록 및 변경 시간 저장을 위한 시스템 컬럼"
        elif 'seq' in column_name:
            return "고유 식별자로 사용되는 시퀀스 값이자 순번"
        elif 'yn' in column_name:
            return "Y/N 플래그로 상태를 관리"
        elif 'type' in column_name:
            return "분류/구분을 위한 코드 값"
        elif 'dt' in column_name:
            return "날짜/시간 정보"
        elif 'no' in column_name:
            return "번호 형태의 식별 정보"
        elif 'id' in column_name:
            return "식별자 또는 연결키"
        elif 'cnt' in column_name:
            return "수량/개수 정보"
        elif 'url' in column_name:
            return "웹 링크/경로 정보"
        
        # 테이블별 특화 의미
        if 'gift' in table_name:
            return f"상품 관련 {description}"
        elif 'user' in table_name:
            return f"사용자 관련 {description}"
        elif 'event' in table_name:
            return f"이벤트 관련 {description}"
        
        return description
