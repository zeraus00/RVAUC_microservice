from pydantic import BaseModel
from typing import Any

class DetectionPayload(BaseModel):
    detected_items: dict[str, bool]
    boxes: list
    status: str


class EvaluationPayload(BaseModel):
    evaluation_result: Any


class ConfirmationPayload(BaseModel):
    confirmation_result: Any