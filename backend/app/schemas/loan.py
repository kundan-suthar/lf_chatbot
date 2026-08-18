from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class LoanResponse(BaseModel):
    id: int
    customer_id: int
    loan_amount: Decimal
    tenure_months: int
    status: str
    application_date: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentResponse(BaseModel):
    id: int
    amount: Decimal
    due_date: datetime
    payment_date: datetime | None
    status: str

    model_config = ConfigDict(from_attributes=True)