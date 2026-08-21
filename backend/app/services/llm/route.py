from app.services.llm.bedrock import BedrockClient
import json


ROUTER_MODEL = "google.gemma-3-12b-it"


ROUTER_SYSTEM_PROMPT = """
You are a routing classifier for a loan customer support chatbot.

Your job is to classify the customer's message into exactly one route.

Available routes:

RAG:
Use RAG for general loan-related information that can be answered
from the company's documentation.

Examples:
- loan eligibility
- KYC requirements
- fees
- interest rates
- repayment policies
- application requirements
- disbursement policies
- general loan information

CUSTOMER_API:
Use CUSTOMER_API when the customer asks for information
specific to their account, application, loan, payments, or EMI.

Examples:
- loan application status
- my loan status
- my loan amount
- outstanding balance
- payment history
- next EMI
- EMI amount
- whether my loan was approved

Important rules:

1. General questions -> RAG.
2. Questions about the customer's own account -> CUSTOMER_API.
3. Words such as "my", "mine", "my application", "my loan",
   "my payment", or "my EMI" usually indicate CUSTOMER_API.
4. Do not answer the customer's question.
5. Only classify the message.

Return ONLY valid JSON.

Valid outputs:

{"route":"RAG"}

{"route":"CUSTOMER_API"}
"""


class ChatRouter:

    def __init__(self, bedrock: BedrockClient):
        self.bedrock = bedrock

    def route(
        self,
        message: str,
        history: list[dict] | None = None,
    ) -> str:

        response = self.bedrock.converse(
            model_id=ROUTER_MODEL,
            system_prompt=ROUTER_SYSTEM_PROMPT,
            message=message,
            history=history,
        )

        try:
            result = json.loads(response)
            route = result.get("route")

            if route in {"RAG", "CUSTOMER_API"}:
                return route

        except (json.JSONDecodeError, TypeError):
            pass

        return "UNKNOWN"