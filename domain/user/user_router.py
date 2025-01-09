from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from datetime import timedelta, datetime
from database import get_db
from domain.user import user_schema, user_crud
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from domain.user.user_crud import pwd_context

router = APIRouter(
    prefix="/api/user",
)

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24시간 (분단위 계산)
SECRET_KEY = "4ab2fce7a6bd79e1c014396315ed322dd6edb1c5d975c6b74a2904135172c03c" # 64자리 (문자열 생성 꿀팁: $openssl rand -hex 32)
ALGORITHM = "HS256"

@router.post("/login", response_model=user_schema.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(get_db)):

    # check user and password
    user = user_crud.get_user(db, form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # make access token
    data = {
        "sub": user.email,
        "exp": datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "id": user.id,
        "name": user.name,
        "email": user.email
    }


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def user_create(_user_create: user_schema.UserCreate, db: Session = Depends(get_db)):
    user = user_crud.get_existing_user(db, user_create=_user_create)
    if user:
        raise HTTPException( # HTTPException이 발생하면 FastAPI가 자동으로 JSON 형식의 에러 응답을 생성한다.
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 존재하는 이메일입니다." # detail 파라미터에 넣은 메시지가 클라이언트에게 JSON으로 전달된다.
        )

    user_crud.create_user(db=db, user_create=_user_create)


@router.get("/list", response_model=list[user_schema.User])
def user_list(db: Session = Depends(get_db)):
    _user_list = user_crud.get_user_list(db)
    return _user_list