from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import LoanApplication

from app.schemas.loan import LoanResponse, PaymentResponse

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
    loan = db.get(LoanApplication, loan_id)

    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found",
        )

    return {
        "id": loan.id,
        "customer_id": loan.customer_id,
        "loan_amount": loan.loan_amount,
        "tenure_months": loan.tenure_months,
        "status": loan.status,
        "application_date": loan.application_date,
    }


@router.get("/{loan_id}/payments",   response_model=list[PaymentResponse],)
def get_loan_payments(
    loan_id: int,
    db: Session = Depends(get_db),
):
    loan = db.get(LoanApplication, loan_id)

    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found",
        )

    return [
        {
            "id": payment.id,
            "amount": payment.amount,
            "due_date": payment.due_date,
            "payment_date": payment.payment_date,
            "status": payment.status,
        }
        for payment in loan.payments
    ]