from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TicketCreate(BaseModel):
    customer_id: int
    category: str
    priority: str
    subject: str
    description: str


class TicketResponse(BaseModel):
    id: int
    customer_id: int
    category: str
    priority: str
    subject: str
    description: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)