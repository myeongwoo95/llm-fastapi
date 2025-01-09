from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
from enum import Enum

# 사용자 역할 정의
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

# 기본 모델
class UserBase(BaseModel):
    id: int
    name: str
    email: EmailStr


# 완전한 유저 모델
class User(UserBase):
    is_active: bool
    created_at: datetime
    role: UserRole

    class Config:
        from_attributes = True


# 회원가입 : Request
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator('name', 'email', 'password')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v


# 로그인 : Response
class Token(BaseModel):
    access_token: str
    token_type: str
    id: int
    name: str
    email: EmailStr

