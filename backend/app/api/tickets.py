from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import SupportTicket

from app.schemas.ticket import TicketCreate, TicketResponse

router = APIRouter(prefix="/support", tags=["Support"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.post("/tickets", response_model=TicketResponse,)
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
):
    ticket = SupportTicket(
        customer_id=ticket_data.customer_id,
        category=ticket_data.category,
        priority=ticket_data.priority,
        subject=ticket_data.subject,
        description=ticket_data.description,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # Return the ORM object directly so Pydantic can read attributes
    return ticket