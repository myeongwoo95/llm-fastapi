import os
import sys

from dotenv import load_dotenv
from fastapi import APIRouter
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from starlette.responses import StreamingResponse
from domain.chat import chat_schema

router = APIRouter(
    prefix="/api/chat",
)

# .env 파일 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY .env 파일에 설정되지 않았습니다.")

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


@router.post("/stream")
async def stream_response(message: chat_schema.UserMessage):
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

