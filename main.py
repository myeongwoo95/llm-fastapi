from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain.memory import ConversationBufferMemory
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from pydantic import BaseModel
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다.")

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 스트리밍 콜백 핸들러
class CustomStreamingHandler(StreamingStdOutCallbackHandler):
    def __init__(self):
        self.tokens = []
        super().__init__()

    def on_llm_new_token(self, token: str, **kwargs):
        self.tokens.append(token)


# LangChain 설정
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.7,
    streaming=True
)

# 대화 메모리 설정
memory = ConversationBufferMemory()

# 대화 체인 설정
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

class Message(BaseModel):
    content: str

@app.post("/chat")
async def chat_endpoint(message: Message):
    async def generate_response():
        print("hello")

        try:
            handler = CustomStreamingHandler()

            conversation.llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.7,
                streaming=True,
                callbacks=[handler]
            )

            response = await conversation.apredict(input=message.content)

            for token in handler.tokens:
                yield token

        except Exception as e:
            yield f"Error: {str(e)}"

    return StreamingResponse(generate_response(), media_type="text/plain")


@app.get("/history")
async def get_history():
    return {"history": memory.chat_memory.messages}

@app.get("/hello")
def hello():
    return {"message": "안녕하세요 파이보"}
