from typing import Any, TypedDict
from pydantic import BaseModel
from rvauc_ms.enums import UniformTypes


class StudentDetails(BaseModel):
    student_number: str
    uniform_type: UniformTypes = UniformTypes.type_a_male
    term_id: int = 1

'''
    Imported schemas from the main server. 
    Lahat ng nandito nakabase sa schemas doon so ***don't change anything***.
'''

class ComplianceRecord(TypedDict):
    '''
    Schema for the compliance record to be sent to the rvauc-ms server\n
    Use this ***after*** you confirm the compliance evaluation with yolo.\n
    Basically ito 'yung laman ng request body for
    /uniform-compliance/new-record
    '''
    studentNumber: str
    uniformTypeId: int # hardcode to 0 for type A uniform male for now,
    validFootwear: bool
    hasId: bool
    validUpperwear: bool
    validBottoms: bool
    termId: int # default to 1 for now

class TokenPayload(BaseModel):
    '''
    Pydantic model for schema validation
    Payload for the access token in the request of the mini web app.
    '''
    role: str
    studentNumber: str
    department: str
    yearLevel: int
    block: str

class ApiResponse(BaseModel):
    '''
    The api response type of RvaucMs server
    '''
    success: bool
    message: str = ""
    result: Any = None

class EvaluationResult(TypedDict):
    isCompliant: bool
    reasons: list[str]

class EvaluationResponse(ApiResponse):
    '''
    Response type of the new-record endpoint
    '''
    result: EvaluationResult | None = None