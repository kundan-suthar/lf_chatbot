from pydantic import BaseModel, Field
from uuid import UUID


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=2000,
    )

    customer_id: int | None = None
    conversation_id: UUID | None = None


class ChatSource(BaseModel):
    document_name: str
    policy_id: str
    version: str
    chunk_id: int


class ChatResponse(BaseModel):
    conversation_id: UUID
    answer: str
    route: str
    sources: list[ChatSource] = Field(default_factory=list)