from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from app.services.chat.service import ChatService
from app.services.conversation_service import (
    ConversationAccessError,
    ConversationNotFoundError,
)


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

    try:
        return service.chat(
            message=request.message,
            customer_id=request.customer_id,
            conversation_id=request.conversation_id,
        )
    except ConversationNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ConversationAccessError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error