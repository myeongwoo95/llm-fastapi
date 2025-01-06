from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.user import user_schema, user_crud

router = APIRouter(
    prefix="/api/user",
)

@router.get("/list", response_model=list[user_schema.User])
def user_list(db: Session = Depends(get_db)):
    _user_list = user_crud.get_user_list(db)
    return _user_list

@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def user_create(_user_create: user_schema.UserCreate, db: Session = Depends(get_db)):
    user = user_crud.get_existing_user(db, user_create=_user_create)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 존재하는 사용자입니다."
        )
    # HTTPException이 발생하면 FastAPI가 자동으로 JSON 형식의 에러 응답을 생성한다.
    # detail 파라미터에 넣은 메시지가 클라이언트에게 JSON으로 전달된다.

    user_crud.create_user(db=db, user_create=_user_create)