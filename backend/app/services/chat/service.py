from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.services.llm.route import ChatRouter
from app.services.customer_service import CustomerService
from app.services.llm.bedrock import BedrockClient
from app.rag.retriever import retrieve_relevant_chunks
from app.tools.customer_api import CUSTOMER_API_FUNCTIONS
from app.services.conversation_service import ConversationService


ROUTER_MODEL = "google.gemma-3-12b-it"
CUSTOMER_TOOL_MODEL = "amazon.nova-lite-v1:0"


CUSTOMER_API_TOOLS = [
    {
        "toolSpec": {
            "name": "get_customer",
            "description": (
                "Retrieve the authenticated customer's profile. Use when "
                "the customer asks about their name, email, phone, or "
                "account details."
            ),
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {},
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "get_customer_loans",
            "description": (
                "List the authenticated customer's loans. Use when the "
                "customer asks about their applications, loan statuses, "
                "loan amounts, or tenure."
            ),
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {},
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "get_loan",
            "description": (
                "Retrieve one of the authenticated customer's loans. Use "
                "when a specific loan's amount, status, tenure, or "
                "application date is requested."
            ),
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "loan_id": {"type": "integer"},
                    },
                    "required": ["loan_id"],
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "get_loan_payments",
            "description": (
                "Retrieve payments for one of the authenticated customer's "
                "loans. Use when the customer asks about payment history, "
                "EMIs, due dates, paid dates, or payment status."
            ),
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "loan_id": {"type": "integer"},
                    },
                    "required": ["loan_id"],
                }
            },
        }
    },
]


class ChatService:

    def __init__(self, db: Session):

        self.db = db

        self.llm = BedrockClient()
        self.router = ChatRouter(self.llm)

        self.customer_service = CustomerService(
            db
        )
        self.conversation_service = ConversationService(db)

    def _complete_response(
        self,
        conversation_id: UUID,
        answer: str,
        route: str,
        sources: list[dict[str, Any]],
    ) -> dict[str, Any]:
        self.conversation_service.add_assistant_message(
            conversation_id=conversation_id,
            content=answer,
            route=route,
            sources=sources,
        )
        return {
            "conversation_id": conversation_id,
            "answer": answer,
            "route": route,
            "sources": sources,
        }

    def _execute_customer_tool(
        self,
        tool_name: str,
        arguments: dict,
        customer_id: int,
    ) -> dict:
        tool_function = CUSTOMER_API_FUNCTIONS.get(tool_name)

        if tool_function is None:
            return {"error": f"Unknown customer tool: {tool_name}"}

        if tool_name in {"get_customer", "get_customer_loans"}:
            return tool_function(self.db, customer_id)

        loan_id = arguments.get("loan_id")

        if not isinstance(loan_id, int):
            return {"error": "loan_id is required."}

        return tool_function(self.db, loan_id, customer_id)

    def chat(
        self,
        message: str,
        customer_id: int | None = None,
        conversation_id: UUID | None = None,
    ):

        conversation_id, history = (
            self.conversation_service.start_user_message(
                conversation_id=conversation_id,
                customer_id=customer_id,
                content=message,
            )
        )

        # --------------------------------------------------
        # 1. Decide route
        # --------------------------------------------------

        route = self.router.route(message, history=history)

        # --------------------------------------------------
        # 2. RAG
        # --------------------------------------------------

        if route == "RAG":

            chunks = retrieve_relevant_chunks(
                self.db,
                message,
                top_k=5,
            )

            if not chunks:

                return self._complete_response(
                    conversation_id=conversation_id,
                    answer=(
                        "I couldn't find relevant information "
                        "in the Loanfront knowledge base."
                    ),
                    route="RAG",
                    sources=[],
                )

            context = "\n\n".join(
                [
                    f"""
                        SOURCE:
                        {chunk["metadata"]}

                        CONTENT:
                        {chunk["content"]}
                        """
                    for chunk in chunks
                ]
            )

            prompt = f"""
                            You are the Loanfront customer support assistant.

                            Answer the customer's question using ONLY the
                            provided Loanfront policy context.

                            If the answer cannot be found in the context,
                            say that you do not have enough information.

                            Do not invent policies, fees, eligibility rules,
                            timelines, or requirements.

                            Customer question:

                            {message}

                            Loanfront policy context:

                            {context}
                            """

            answer = self.llm.generate(prompt, history=history)

            sources = []

            for chunk in chunks:

                metadata = chunk["metadata"]

                sources.append(
                    {
                        "document_name": metadata.get(
                            "document_name",
                            "Unknown",
                        ),
                        "policy_id": metadata.get(
                            "policy_id",
                            "Unknown",
                        ),
                        "version": metadata.get(
                            "version",
                            "Unknown",
                        ),
                        "chunk_id": chunk["chunk_id"],
                    }
                )

            return self._complete_response(
                conversation_id=conversation_id,
                answer=answer,
                route="RAG",
                sources=sources,
            )

        # --------------------------------------------------
        # 3. Customer API
        # --------------------------------------------------

        if route == "CUSTOMER_API":

            if customer_id is None:

                return self._complete_response(
                    conversation_id=conversation_id,
                    answer=(
                        "Please provide your customer "
                        "information so I can check "
                        "your account."
                    ),
                    route="CUSTOMER_API",
                    sources=[],
                )

            answer = self.llm.converse_with_tools(
                model_id=CUSTOMER_TOOL_MODEL,
                system_prompt=(
                    "You are the Loanfront customer support assistant. "
                    "For account-specific questions, use the provided tools. "
                    "Answer only from tool results and do not invent data."
                ),
                message=message,
                tools=CUSTOMER_API_TOOLS,
                history=history,
                tool_executor=lambda tool_name, arguments: (
                    self._execute_customer_tool(
                        tool_name,
                        arguments,
                        customer_id,
                    )
                ),
            )

            return self._complete_response(
                conversation_id=conversation_id,
                answer=answer,
                route="CUSTOMER_API",
                sources=[],
            )