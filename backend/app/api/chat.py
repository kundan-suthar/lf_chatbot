from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from app.services.chat.service import ChatService


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):

    service = ChatService(db)

    return service.chat(
        message=request.message,
        customer_id=request.customer_id,
    )