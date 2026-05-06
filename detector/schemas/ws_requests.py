from pydantic import BaseModel, Field, field_validator
from typing import Dict, Literal

class BaseRequest(BaseModel):
    action: str


# --- FLOW 1: Frame ---
class FrameRequest(BaseModel):
    action: Literal["frame"]
    frame: str = Field(..., min_length=1)


# --- FLOW 2: Evaluation ---
class EvaluationRequest(BaseModel):
    action: Literal["evaluation"]
    uniform_type_id: int = Field(..., gt=0)
    detected_items: Dict[str, bool]
    access_token: str = Field(..., min_length=1)

    @field_validator("detected_items")
    @classmethod
    def validate_detected_items(cls, v):
        if not v:
            raise ValueError("detected_items cannot be empty")

        for key, value in v.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("Invalid detection label key")
            if not isinstance(value, bool):
                raise ValueError("Detection values must be boolean")

        return v

# --- FLOW 3: Confirmation ---
class ConfirmationRequest(BaseModel):
    action: Literal["confirmation"]
    uniform_type_id: int = Field(..., gt=0)
    detected_items: Dict[str, bool]
    access_token: str = Field(..., min_length=1)

    @field_validator("detected_items")
    @classmethod
    def validate_detected_items(cls, v):
        if not v:
            raise ValueError("detected_items cannot be empty")

        for key, value in v.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("Invalid detection label key")
            if not isinstance(value, bool):
                raise ValueError("Detection values must be boolean")

        return v