from pydantic import BaseModel
from typing import Any, Optional, Literal


class WSResponse(BaseModel):
    type: str
    data: Optional[Any] = None
    error: Optional[Any] = None

class DetectionPayload(BaseModel):
    detected_items: dict[str, bool]
    boxes: list
    status: str


class EvaluationPayload(BaseModel):
    evaluation_result: Any


class ConfirmationPayload(BaseModel):
    confirmation_result: Any