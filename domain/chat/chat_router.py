from fastapi import APIRouter

router = APIRouter(
    prefix="/api/chat",
)

@router.get("/stream")
def user_list():
    print("stream works!")