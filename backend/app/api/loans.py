from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.schemas.loan import LoanResponse, PaymentResponse
from app.tools.customer_api import get_loan, get_loan_payments

router = APIRouter(prefix="/loans", tags=["Loans"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{loan_id}", response_model=LoanResponse,)
def get_loan(
    loan_id: int,
    db: Session = Depends(get_db),
):
    loan = get_loan(db, loan_id)

    if "error" in loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found",
        )

    return loan


@router.get("/{loan_id}/payments",   response_model=list[PaymentResponse],)
def get_loan_payments(
    loan_id: int,
    db: Session = Depends(get_db),
):
    loan = get_loan_payments(db, loan_id)

    if isinstance(loan, dict) and "error" in loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found",
        )

    return loan