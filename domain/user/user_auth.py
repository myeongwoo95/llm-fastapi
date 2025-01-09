# domain/user/user_auth.py
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import List
from database import get_db
from sqlalchemy.orm import Session
from domain.user import user_crud
from domain.user.user_schema import UserRole

# 기존 로그인 URL과 일치하도록 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")

# 현재 사용자 가져오기
async def get_current_user(token: str = Depends(oauth2_scheme),
                          db: Session = Depends(get_db)):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # router.py에서 가져오기
        from domain.user.user_router import SECRET_KEY, ALGORITHM

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = user_crud.get_user(db, email)
    if user is None:
        raise credentials_exception
    return user

# 권한 확인 데코레이터
def check_roles(allowed_roles: List[UserRole]):
    async def role_checker(current_user = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="권한이 없습니다."
            )
        return current_user
    return role_checker