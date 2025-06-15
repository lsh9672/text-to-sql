from pydantic import BaseModel

class SQLRequest(BaseModel):
    question: str
    k: int = 5
    explain: bool = False