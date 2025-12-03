import os
import httpx
from rvauc_ms.schemas import ApiResponse, StudentDetails
from rvauc_ms.utils import decode_rvauc_ms_jwt, scan_to_dto

def get_environment() -> str:
    environment = os.environ.get("ENVIRONMENT")
    validEnvs = ("dev", "test", "prod")
    isNoneOrBlank = environment is None or len(environment) == 0
    isInvalidEnv = environment not in validEnvs
    if (isNoneOrBlank or isInvalidEnv):
        raise Exception("ENVIRONMENT is not configured properly.")
    
    return environment

def get_rvauc_ms_address() -> str:
    environment = get_environment()

    env_key = "RVAUCMS_ADDRESS_" + environment.upper()

    address = os.environ.get(env_key)

    if (address is None or len(address) == 0):
        raise Exception(f"{env_key} is not configured properly.")
    
    return address

client = httpx.AsyncClient(timeout=5.0)

class RvaucMsService:
    base_url = get_rvauc_ms_address()

    @staticmethod
    async def new_record(token: str, detected: dict[str, bool]) -> ApiResponse:

        try:
            url = RvaucMsService.base_url + "/uniform-compliance/new-record"

            decoded = decode_rvauc_ms_jwt(token)
            student_details = StudentDetails(student_number=decoded.studentNumber)
            record = scan_to_dto(student_details, detected)

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            response = await client.post(url, json=record, headers=headers)

            parsed = ApiResponse(**response.json())
            
            return parsed
        except Exception as e:
            print("Failed storing record in method new_record: " +  str(e))
            return ApiResponse(success=False, message="Failed storing new record.")

