# 기본 모델
from pydantic import BaseModel, EmailStr

class UserMessage(BaseModel):
    text: str

