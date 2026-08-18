from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Customer

from app.schemas.customer import (
    CustomerResponse,
    CustomerLoanResponse,
)

router = APIRouter(prefix="/customers", tags=["Customers"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{customer_id}",response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    customer = db.get(Customer, customer_id)

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return {
        "id": customer.id,
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone,
        "created_at": customer.created_at,
    }


@router.get("/{customer_id}/loans", response_model=list[CustomerLoanResponse])
def get_customer_loans(
    customer_id: int,
    db: Session = Depends(get_db),
):
    customer = db.get(Customer, customer_id)

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return [
        {
            "id": loan.id,
            "loan_amount": loan.loan_amount,
            "tenure_months": loan.tenure_months,
            "status": loan.status,
            "application_date": loan.application_date,
        }
        for loan in customer.loans
    ]