from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerLoanResponse(BaseModel):
    id: int
    loan_amount: float
    tenure_months: int
    status: str
    application_date: datetime

    model_config = ConfigDict(from_attributes=True)