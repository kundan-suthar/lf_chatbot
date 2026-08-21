import os
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Conversation, Message


MAX_HISTORY_MESSAGES = int(os.getenv("CHAT_HISTORY_MESSAGE_LIMIT", "20"))


class ConversationNotFoundError(ValueError):
    pass


class ConversationAccessError(ValueError):
    pass


class ConversationService:
    def __init__(self, db: Session):
        self.db = db

    def start_user_message(
        self,
        conversation_id: UUID | None,
        customer_id: int | None,
        content: str,
    ) -> tuple[UUID, list[dict[str, Any]]]:
        if conversation_id is None:
            conversation = Conversation(customer_id=customer_id)
            self.db.add(conversation)
            self.db.flush()
        else:
            conversation = self.db.execute(
                select(Conversation)
                .where(Conversation.id == conversation_id)
                .with_for_update()
            ).scalar_one_or_none()

            if conversation is None:
                raise ConversationNotFoundError(
                    "Conversation does not exist."
                )

            if conversation.customer_id != customer_id:
                raise ConversationAccessError(
                    "Conversation does not belong to this customer."
                )

        prior_messages = list(
            reversed(
                self.db.execute(
                    select(Message)
                    .where(Message.conversation_id == conversation.id)
                    .order_by(Message.sequence.desc())
                    .limit(MAX_HISTORY_MESSAGES)
                ).scalars().all()
            )
        )

        next_sequence = (
            self.db.execute(
                select(func.coalesce(func.max(Message.sequence), 0)).where(
                    Message.conversation_id == conversation.id
                )
            ).scalar_one()
            + 1
        )

        self.db.add(
            Message(
                conversation_id=conversation.id,
                role="user",
                content=[{"text": content}],
                sequence=next_sequence,
            )
        )
        conversation.updated_at = func.now()
        self.db.commit()

        return conversation.id, [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in prior_messages
            if message.role in {"user", "assistant"}
        ]

    def add_assistant_message(
        self,
        conversation_id: UUID,
        content: str,
        route: str,
        sources: list[dict[str, Any]],
    ) -> None:
        conversation = self.db.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .with_for_update()
        ).scalar_one()

        next_sequence = (
            self.db.execute(
                select(func.coalesce(func.max(Message.sequence), 0)).where(
                    Message.conversation_id == conversation_id
                )
            ).scalar_one()
            + 1
        )

        self.db.add(
            Message(
                conversation_id=conversation_id,
                role="assistant",
                content=[{"text": content}],
                sequence=next_sequence,
                route=route,
                sources=sources,
            )
        )
        conversation.updated_at = func.now()
        self.db.commit()
