from pydantic import BaseModel

class SQLResponse(BaseModel):
    sql_query: str
    success: bool = True
    message: str = "SQL 생성 성공"