import sys
from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv
from pydantic import BaseModel

# LangChain 관련 imports는 유지
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from starlette.responses import StreamingResponse

# Local imports
import models
import schemas
from database import SessionLocal, engine

# create_all = 테이블이 없으면 생성
# drop_all = 기존 테이블 삭제
models.Base.metadata.create_all(bind=engine)

# .env 파일 로드
load_dotenv()

# 환경변수 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY .env 파일에 설정되지 않았습니다.")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY .env 파일에 설정되지 않았습니다.")

app = FastAPI()

# CORS 설정
origins = [
    "http://localhost:8000", "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 유틸리티 함수들
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 스트리밍 핸들러
class CustomStreamingHandler(StreamingStdOutCallbackHandler):
    def __init__(self):
        self.tokens = []
        super().__init__()

    def on_llm_new_token(self, token: str, **kwargs):
        self.tokens.append(f"data: {token}\n\n")

        # 버퍼를 즉시 플러시
        if hasattr(sys.stdout, 'flush'):
            sys.stdout.flush()


class Message(BaseModel):
    text: str


@app.post("/stream")
async def stream_response(message: Message):
    async def event_stream():
        try:
            chat = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.7,
                streaming=True,
                openai_api_key=OPENAI_API_KEY
            )

            messages = [HumanMessage(content=message.text)]

            async for chunk in chat.astream(messages):
                if chunk.content:
                    yield f"data: {chunk.content}\n\n"

        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.post("/auth/register")
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)

    db_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()

    return {"message": "Registration successful"}


@app.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.name).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token = create_access_token(
        data={"sub": user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


@app.get("/users/me")
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user