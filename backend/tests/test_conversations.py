import unittest

from sqlalchemy import delete, select

from app.db.database import SessionLocal
from app.db.models import Conversation, Message
from app.services.conversation_service import ConversationService


class ConversationPersistenceSmokeTest(unittest.TestCase):
    def test_two_turn_history_loads_in_order(self):
        db = SessionLocal()
        conversation_ids = []

        try:
            persistence = ConversationService(db)

            conversation_id, first_history = persistence.start_user_message(
                conversation_id=None,
                customer_id=None,
                content="What documents do I need?",
            )
            conversation_ids.append(conversation_id)
            self.assertEqual(first_history, [])

            persistence.add_assistant_message(
                conversation_id=conversation_id,
                content="You need identity and income documents.",
                route="RAG",
                sources=[],
            )

            second_id, second_history = persistence.start_user_message(
                conversation_id=conversation_id,
                customer_id=None,
                content="How long does approval take?",
            )
            self.assertEqual(second_id, conversation_id)
            self.assertEqual(
                [message["role"] for message in second_history],
                ["user", "assistant"],
            )
            self.assertEqual(
                [message["content"][0]["text"] for message in second_history],
                [
                    "What documents do I need?",
                    "You need identity and income documents.",
                ],
            )
        finally:
            for conversation_id in conversation_ids:
                db.execute(
                    delete(Message).where(
                        Message.conversation_id == conversation_id
                    )
                )
                db.execute(
                    delete(Conversation).where(
                        Conversation.id == conversation_id
                    )
                )
            db.commit()
            db.close()


if __name__ == "__main__":
    unittest.main()
