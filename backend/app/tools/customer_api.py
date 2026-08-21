from typing import Any

from sqlalchemy.orm import Session

from app.db.models import Customer, LoanApplication


def get_customer(
    db: Session,
    customer_id: int,
) -> dict[str, Any]:
    """Return a customer's profile for GET /customers/{customer_id}."""
    customer = db.get(Customer, customer_id)

    if not customer:
        return {"error": "Customer not found."}

    return {
        "id": customer.id,
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone,
        "created_at": customer.created_at.isoformat(),
    }


def get_customer_loans(
    db: Session,
    customer_id: int,
) -> list[dict[str, Any]] | dict[str, str]:
    """Return a customer's loans for GET /customers/{customer_id}/loans."""
    customer = db.get(Customer, customer_id)

    if not customer:
        return {"error": "Customer not found."}

    return [
        {
            "id": loan.id,
            "loan_amount": float(loan.loan_amount),
            "tenure_months": loan.tenure_months,
            "status": loan.status,
            "application_date": loan.application_date.isoformat(),
        }
        for loan in customer.loans
    ]


def get_loan(
    db: Session,
    loan_id: int,
    customer_id: int | None = None,
) -> dict[str, Any]:
    """Return a loan for GET /loans/{loan_id}."""
    loan = db.get(LoanApplication, loan_id)

    if not loan or (
        customer_id is not None
        and loan.customer_id != customer_id
    ):
        return {"error": "Loan not found."}

    return {
        "id": loan.id,
        "customer_id": loan.customer_id,
        "loan_amount": float(loan.loan_amount),
        "tenure_months": loan.tenure_months,
        "status": loan.status,
        "application_date": loan.application_date.isoformat(),
    }


def get_loan_payments(
    db: Session,
    loan_id: int,
    customer_id: int | None = None,
) -> list[dict[str, Any]] | dict[str, str]:
    """Return loan payments for GET /loans/{loan_id}/payments."""
    loan = db.get(LoanApplication, loan_id)

    if not loan or (
        customer_id is not None
        and loan.customer_id != customer_id
    ):
        return {"error": "Loan not found."}

    return [
        {
            "id": payment.id,
            "amount": float(payment.amount),
            "due_date": payment.due_date.isoformat(),
            "payment_date": (
                payment.payment_date.isoformat()
                if payment.payment_date
                else None
            ),
            "status": payment.status,
        }
        for payment in loan.payments
    ]


CUSTOMER_API_FUNCTIONS = {
    "get_customer": get_customer,
    "get_customer_loans": get_customer_loans,
    "get_loan": get_loan,
    "get_loan_payments": get_loan_payments,
}
