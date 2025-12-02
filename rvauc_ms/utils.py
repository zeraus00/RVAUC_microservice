from dataclasses import dataclass
from typing import TypedDict, Mapping
import jwt
from enums import UniformTypes
from schemas import ComplianceRecord, TokenPayload

class LabelMapper(TypedDict):
    '''
    Used for mapping yolo labels into dto fields
    '''
    validUpperwear: str
    validBottoms: str
    validFootwear: str
    hasId: str

@dataclass
class StudentDetails:
    student_number: str
    uniform_type: UniformTypes = UniformTypes.type_a_male
    term_id: int = 1

LabelMappers: Mapping[UniformTypes, Mapping[str, str]] = {
    UniformTypes.type_a_male: {
        "validUpperwear": "polo",
        "validBottoms": "black_slacks",
        "validFootwear": "black_shoes",
        "hasId": "id"
    }
}

def scan_to_dto(student_details: StudentDetails , detected: dict[str, bool]):
    mapper = LabelMappers.get(student_details.uniform_type, {})

    compliance_record: ComplianceRecord = {
        "studentNumber": student_details.student_number,
        "uniformTypeId": 0,
        "validFootwear": False,
        "hasId": True,
        "validUpperwear": False,
        "validBottoms": False,
        "termId": student_details.term_id
    }

    # get the detection status of each key in the detected dict.
    # if the detection key isn't in the list, default to false
    for rvaucKey, detectionKey in mapper.items():
        compliance_record[rvaucKey] = detected.get(detectionKey, False)
        

    return compliance_record

def decode_rvauc_ms_jwt(access_token: str):
    try:
        decoded = jwt.decode(access_token, options={"verify_signature": False})
        return TokenPayload(**decoded)
    except Exception:
        return None