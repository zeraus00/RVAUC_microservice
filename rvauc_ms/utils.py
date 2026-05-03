from typing import Mapping
import jwt
from rvauc_ms.enums import UniformTypes
from rvauc_ms.schemas import ComplianceRecord, StudentDetails, TokenPayload 

LabelMappers: Mapping[UniformTypes, Mapping[str, str]] = {
    UniformTypes.type_a_male: {
        "validUpperwear": "Polo",
        "validBottoms": "Slack Pants",
        "validFootwear": "Black Shoes",
        "hasId": "id"
    },
    UniformTypes.type_a_female: {
        "validUpperwear": "lu_blouse",
        "validBottoms": "skirt",
        "valitBelt" : "green_belt",
        "validFootwear": "black_shoes",
        "hasId": "id"
    },
    UniformTypes.buffalo: {
        "validUpperwear": "buffalo_uniform",
        "hasId": "id",
    },
    UniformTypes.cs_dept_shirt: {
        "validUpperwear": "cs_dept_shirt_uniform",
        "hasId": "id",
    }
}

# Map uniform strings to Ids for the backend
UNIFORM_ID_MAP = {
    "type_a_male": 1,
    "type_a_female": 2,
    "buffalo": 3,
    "cs_dept_shirt": 4
}

def scan_to_dto(student_details: StudentDetails , detected: dict, detected_type: str):
    #mapper
    unif_enum = UniformTypes(detected_type)
    mapper = LabelMappers.get(unif_enum, {})

    compliance_record: ComplianceRecord = {
        "studentNumber": student_details.student_number,
        "uniformTypeId": UNIFORM_ID_MAP.get(detected_type, 1), #dynamic Id
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