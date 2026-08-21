from sqlalchemy.orm import Session

from app.db.models import Customer


class CustomerService:

    def __init__(self, db: Session):
        self.db = db

    def get_customer_context(
        self,
        customer_id: int,
    ) -> dict | None:

        customer = self.db.get(
            Customer,
            customer_id,
        )

        if not customer:
            return None

        loans = []

        for loan in customer.loans:

            payments = []

            for payment in loan.payments:

                payments.append(
                    {
                        "payment_id": payment.id,
                        "amount": float(payment.amount),
                        "due_date": payment.due_date.isoformat()
                        if payment.due_date
                        else None,
                        "payment_date": payment.payment_date.isoformat()
                        if payment.payment_date
                        else None,
                        "status": payment.status,
                    }
                )

            loans.append(
                {
                    "loan_id": loan.id,
                    "loan_amount": float(loan.loan_amount),
                    "tenure_months": loan.tenure_months,
                    "status": loan.status,
                    "application_date": (
                        loan.application_date.isoformat()
                        if loan.application_date
                        else None
                    ),
                    "payments": payments,
                }
            )

        return {
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
            },
            "loans": loans,
        }