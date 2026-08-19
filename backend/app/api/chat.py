from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm.bedrock import BedrockClient

router = APIRouter(prefix="/chat", tags=["Chat"])

bedrock = BedrockClient()


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    reply = bedrock.generate(request.message)
    return {"reply": reply}
