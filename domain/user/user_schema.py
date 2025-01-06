from datetime import datetime
from pydantic import BaseModel, EmailStr

# 기본 모델
class UserBase(BaseModel):
    id: int
    email: EmailStr
    name: str

# 회원가입 모델
class UserCreate(UserBase):
    password: str

# 완전한 유저 모델
class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True