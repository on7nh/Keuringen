from __future__ import annotations

import uuid

from pydantic import BaseModel


class AIProposalOut(BaseModel):
    id: uuid.UUID
    field_code: str
    proposed_value: dict
    confidence: float | None
    source_snippet: str | None
    is_reviewed: bool

    model_config = {"from_attributes": True}


class AIProposalCorrectRequest(BaseModel):
    value: str
    reason: str | None = None
