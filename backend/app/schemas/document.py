from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    id: int
    policy_id: str
    document_name: str
    version: str
    file_name: str
    file_hash: str
    s3_key: str
    status: str
    effective_from: datetime
    effective_until: datetime | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)