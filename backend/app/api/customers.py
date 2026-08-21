from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.schemas.customer import (
    CustomerResponse,
    CustomerLoanResponse,
)
from app.tools.customer_api import get_customer, get_customer_loans

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
    customer = get_customer(db, customer_id)

    if "error" in customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return customer


@router.get("/{customer_id}/loans", response_model=list[CustomerLoanResponse])
def get_customer_loans(
    customer_id: int,
    db: Session = Depends(get_db),
):
    customer = get_customer_loans(db, customer_id)

    if isinstance(customer, dict) and "error" in customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return customer