from pydantic import BaseModel

class SQLMcpRequest(BaseModel):
    question: str
    # explain: bool = False ## TODO : 추후에 sql 설명용으로 사용.