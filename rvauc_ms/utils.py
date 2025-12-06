from typing import Mapping
import jwt
from rvauc_ms.enums import UniformTypes
from rvauc_ms.schemas import ComplianceRecord, StudentDetails, TokenPayload 

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
        "uniformTypeId": 1,
        "validFootwear": False,
        "hasId": True,
        "validUpperwear": False,
        "validBottoms": False,
    }

    # get the detection status of each key in the detected dict.
    # if the detection key isn't in the list, default to false
    for rvaucKey, detectionKey in mapper.items():
        compliance_record[rvaucKey] = detected.get(detectionKey, False)
        

    return compliance_record

def decode_rvauc_ms_jwt(access_token: str):
    decoded = jwt.decode(access_token, options={"verify_signature": False})
    return TokenPayload(**decoded)