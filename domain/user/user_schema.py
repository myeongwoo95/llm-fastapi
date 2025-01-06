from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator

# 기본 모델
class UserBase(BaseModel):
    id: int
    name: str
    email: EmailStr

# 회원가입 모델
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator('name', 'email', 'password')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v

# 완전한 유저 모델
class User(UserBase):
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True