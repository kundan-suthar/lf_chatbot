from datetime import datetime, timedelta
from decimal import Decimal

from app.db.database import SessionLocal
from app.db.models import (
    Customer,
    LoanApplication,
    Payment,
    SupportTicket,
)


def seed():
    db = SessionLocal()

    try:
        # Clear existing demo data
        db.query(Payment).delete()
        db.query(SupportTicket).delete()
        db.query(LoanApplication).delete()
        db.query(Customer).delete()

        # ---------------------------------------------------------
        # Customers
        # ---------------------------------------------------------

        customers = [
            Customer(
                name="Aarav Sharma",
                email="aarav.sharma@example.com",
                phone="9876500001",
            ),
            Customer(
                name="Priya Mehta",
                email="priya.mehta@example.com",
                phone="9876500002",
            ),
            Customer(
                name="Rahul Verma",
                email="rahul.verma@example.com",
                phone="9876500003",
            ),
            Customer(
                name="Sneha Patel",
                email="sneha.patel@example.com",
                phone="9876500004",
            ),
            Customer(
                name="Vikram Rao",
                email="vikram.rao@example.com",
                phone="9876500005",
            ),
            Customer(
                name="Neha Kapoor",
                email="neha.kapoor@example.com",
                phone="9876500006",
            ),
            Customer(
                name="Arjun Nair",
                email="arjun.nair@example.com",
                phone="9876500007",
            ),
            Customer(
                name="Ananya Iyer",
                email="ananya.iyer@example.com",
                phone="9876500008",
            ),
            Customer(
                name="Rohan Gupta",
                email="rohan.gupta@example.com",
                phone="9876500009",
            ),
            Customer(
                name="Kavya Singh",
                email="kavya.singh@example.com",
                phone="9876500010",
            ),
        ]

        db.add_all(customers)
        db.flush()

        # ---------------------------------------------------------
        # Loan Applications
        # ---------------------------------------------------------

        now = datetime.utcnow()

        loans = [
            LoanApplication(
                customer_id=customers[0].id,
                loan_amount=Decimal("500000"),
                tenure_months=36,
                status="DISBURSED",
                application_date=now - timedelta(days=180),
            ),
            LoanApplication(
                customer_id=customers[1].id,
                loan_amount=Decimal("300000"),
                tenure_months=24,
                status="UNDER_REVIEW",
                application_date=now - timedelta(days=5),
            ),
            LoanApplication(
                customer_id=customers[2].id,
                loan_amount=Decimal("750000"),
                tenure_months=48,
                status="APPROVED",
                application_date=now - timedelta(days=12),
            ),
            LoanApplication(
                customer_id=customers[3].id,
                loan_amount=Decimal("200000"),
                tenure_months=18,
                status="DISBURSED",
                application_date=now - timedelta(days=250),
            ),
            LoanApplication(
                customer_id=customers[4].id,
                loan_amount=Decimal("1000000"),
                tenure_months=60,
                status="REJECTED",
                application_date=now - timedelta(days=20),
            ),
            LoanApplication(
                customer_id=customers[5].id,
                loan_amount=Decimal("450000"),
                tenure_months=36,
                status="KYC_PENDING",
                application_date=now - timedelta(days=3),
            ),
            LoanApplication(
                customer_id=customers[6].id,
                loan_amount=Decimal("600000"),
                tenure_months=36,
                status="DISBURSED",
                application_date=now - timedelta(days=400),
            ),
            LoanApplication(
                customer_id=customers[7].id,
                loan_amount=Decimal("250000"),
                tenure_months=24,
                status="DOCUMENT_VERIFICATION",
                application_date=now - timedelta(days=7),
            ),
            LoanApplication(
                customer_id=customers[8].id,
                loan_amount=Decimal("350000"),
                tenure_months=30,
                status="DISBURSED",
                application_date=now - timedelta(days=300),
            ),
            LoanApplication(
                customer_id=customers[9].id,
                loan_amount=Decimal("150000"),
                tenure_months=12,
                status="CLOSED",
                application_date=now - timedelta(days=500),
            ),
        ]

        db.add_all(loans)
        db.flush()

        # ---------------------------------------------------------
        # Payments
        # ---------------------------------------------------------

        payments = [
            # Aarav - paid
            Payment(
                loan_id=loans[0].id,
                amount=Decimal("16150"),
                due_date=now - timedelta(days=30),
                payment_date=now - timedelta(days=31),
                status="PAID",
            ),
            Payment(
                loan_id=loans[0].id,
                amount=Decimal("16150"),
                due_date=now,
                payment_date=now - timedelta(days=1),
                status="PAID",
            ),

            # Priya - no payment yet
            Payment(
                loan_id=loans[1].id,
                amount=Decimal("14500"),
                due_date=now + timedelta(days=15),
                status="UPCOMING",
            ),

            # Rahul
            Payment(
                loan_id=loans[2].id,
                amount=Decimal("19000"),
                due_date=now + timedelta(days=10),
                status="UPCOMING",
            ),

            # Sneha
            Payment(
                loan_id=loans[3].id,
                amount=Decimal("12800"),
                due_date=now - timedelta(days=5),
                payment_date=now - timedelta(days=4),
                status="PAID",
            ),
            Payment(
                loan_id=loans[3].id,
                amount=Decimal("12800"),
                due_date=now,
                status="OVERDUE",
            ),

            # Vikram - rejected application, no payments

            # Neha - KYC pending

            # Arjun
            Payment(
                loan_id=loans[6].id,
                amount=Decimal("19500"),
                due_date=now - timedelta(days=30),
                payment_date=now - timedelta(days=30),
                status="PAID",
            ),
            Payment(
                loan_id=loans[6].id,
                amount=Decimal("19500"),
                due_date=now,
                status="FAILED",
            ),

            # Rohan
            Payment(
                loan_id=loans[8].id,
                amount=Decimal("14200"),
                due_date=now - timedelta(days=15),
                payment_date=now - timedelta(days=15),
                status="PAID",
            ),

            # Kavya - closed loan
            Payment(
                loan_id=loans[9].id,
                amount=Decimal("13500"),
                due_date=now - timedelta(days=400),
                payment_date=now - timedelta(days=400),
                status="PAID",
            ),
        ]

        db.add_all(payments)

        # ---------------------------------------------------------
        # Support Tickets
        # ---------------------------------------------------------

        tickets = [
            SupportTicket(
                customer_id=customers[0].id,
                category="PAYMENT",
                priority="MEDIUM",
                subject="EMI payment confirmation",
                description="Customer wants confirmation that the latest EMI was received.",
                status="RESOLVED",
            ),
            SupportTicket(
                customer_id=customers[3].id,
                category="PAYMENT",
                priority="HIGH",
                subject="EMI marked overdue",
                description="Customer says the EMI was paid but the account still shows overdue.",
                status="OPEN",
            ),
            SupportTicket(
                customer_id=customers[5].id,
                category="KYC",
                priority="MEDIUM",
                subject="KYC verification pending",
                description="Customer uploaded documents and wants to know why verification is still pending.",
                status="OPEN",
            ),
            SupportTicket(
                customer_id=customers[6].id,
                category="PAYMENT",
                priority="HIGH",
                subject="EMI payment failed",
                description="Customer reports that the EMI payment failed despite sufficient balance.",
                status="OPEN",
            ),
            SupportTicket(
                customer_id=customers[4].id,
                category="APPLICATION",
                priority="LOW",
                subject="Loan application decision",
                description="Customer wants more information about the rejected loan application.",
                status="CLOSED",
            ),
            SupportTicket(
                customer_id=customers[7].id,
                category="DOCUMENTS",
                priority="MEDIUM",
                subject="Document verification status",
                description="Customer wants to know which document is still pending verification.",
                status="OPEN",
            ),
        ]

        db.add_all(tickets)

        db.commit()

        print("✅ Demo data seeded successfully.")
        print(f"Customers: {len(customers)}")
        print(f"Loans: {len(loans)}")
        print(f"Payments: {len(payments)}")
        print(f"Support tickets: {len(tickets)}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()