from pydantic import BaseModel
from typing import Any, Optional, TypedDict

'''
    Imported schemas from the main server. 
    Lahat ng nandito nakabase sa schemas doon so ***don't change anything***.
'''
class YoloScanRequestBody(TypedDict):
    uniformTypeId: int
    detections: dict[str, int]


class ApiResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    message: Optional[str] = None