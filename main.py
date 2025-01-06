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
from domain.user import user_schema as schemas
from database import SessionLocal, engine

from domain.user import user_router

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

app.include_router(user_router.router)

# CORS 설정
origins = [
    "http://localhost:8000",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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