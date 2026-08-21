from datetime import datetime
from decimal import Decimal
from uuid import UUID as PythonUUID

from sqlalchemy import (
    String,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
    Text,
    Boolean,
    JSON,
    CheckConstraint,
    Index,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pgvector.sqlalchemy import Vector

from app.db.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    loans: Mapped[list["LoanApplication"]] = relationship(
        back_populates="customer"
    )

    support_tickets: Mapped[list["SupportTicket"]] = relationship(
        back_populates="customer"
    )

    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="customer"
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[PythonUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    customer_id: Mapped[int | None] = mapped_column(
        ForeignKey("customers.id"),
        nullable=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        server_default="active",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("now()"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("now()"),
        onupdate=text("now()"),
    )

    customer: Mapped["Customer | None"] = relationship(
        back_populates="conversations"
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.sequence",
    )


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant', 'tool')",
            name="ck_messages_role",
        ),
        Index(
            "ix_messages_conversation_sequence",
            "conversation_id",
            "sequence",
        ),
        UniqueConstraint(
            "conversation_id",
            "sequence",
            name="uq_messages_conversation_sequence",
        ),
    )

    id: Mapped[PythonUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    conversation_id: Mapped[PythonUUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[list | dict] = mapped_column(JSON, nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    route: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sources: Mapped[list | None] = mapped_column(JSON, nullable=True)
    message_metadata: Mapped[dict | None] = mapped_column(
        "message_metadata",
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("now()"),
    )

    conversation: Mapped["Conversation"] = relationship(
        back_populates="messages"
    )


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id: Mapped[int] = mapped_column(primary_key=True)

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id")
    )

    loan_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    tenure_months: Mapped[int] = mapped_column(Integer)

    status: Mapped[str] = mapped_column(String(50))
    application_date: Mapped[datetime] = mapped_column(DateTime)

    customer: Mapped["Customer"] = relationship(
        back_populates="loans"
    )

    payments: Mapped[list["Payment"]] = relationship(
        back_populates="loan"
    )


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)

    loan_id: Mapped[int] = mapped_column(
        ForeignKey("loan_applications.id")
    )

    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    due_date: Mapped[datetime] = mapped_column(DateTime)
    payment_date: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    status: Mapped[str] = mapped_column(String(50))

    loan: Mapped["LoanApplication"] = relationship(
        back_populates="payments"
    )


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id")
    )

    category: Mapped[str] = mapped_column(String(100))
    priority: Mapped[str] = mapped_column(String(20))
    subject: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String(50), default="OPEN")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    customer: Mapped["Customer"] = relationship(
        back_populates="support_tickets"
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)

    policy_id: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    document_name: Mapped[str] = mapped_column(
        String(255)
    )

    version: Mapped[str] = mapped_column(
        String(50)
    )

    file_name: Mapped[str] = mapped_column(
        String(255)
    )

    file_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
    )

    s3_key: Mapped[str] = mapped_column(
        String(500),
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="UPLOADED",
    )

    effective_from: Mapped[datetime] = mapped_column(
        DateTime
    )

    effective_until: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        index=True,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer
    )

    content: Mapped[str] = mapped_column(
        Text
    )

    # Bedrock Titan Text Embeddings V2
    # 1024 dimensions
    embedding: Mapped[list[float]] = mapped_column(
        Vector(1024)
    )

    chunk_metadata: Mapped[dict] = mapped_column(
    "metadata",
    JSON,
    default=dict,
)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    document: Mapped["Document"] = relationship(
        back_populates="chunks"
    )