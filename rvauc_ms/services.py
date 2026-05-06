import os
import httpx
from rvauc_ms.utils import scan_to_request_body
from rvauc_ms.schemas import ApiResponse

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
    async def evaluate_compliance(token: str, uniformTypeId: int, detections: dict[str, bool]):
        url = RvaucMsService.base_url + "/enrollments/uniform-compliance/scan/evaluation"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        body = scan_to_request_body(uniformTypeId, detections)

        response = await client.post(url, json=body, headers=headers)

        try:
            payload = response.json()
        except Exception:
            return ApiResponse(success=False, result=None, message="Invalid json response from server.")

        return ApiResponse.model_validate(payload)


    @staticmethod
    async def confirm_compliance(token: str, uniformTypeId: int, detections: dict[str, bool]):
        url = RvaucMsService.base_url + "/enrollments/uniform-compliance/scan/confirmation"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        body = scan_to_request_body(uniformTypeId, detections)

        response = await client.post(url, json=body, headers=headers)

        try:
            payload = response.json()
        except Exception:
            return ApiResponse(success=False, result=None, message="Invalid json response from server.")

        return ApiResponse.model_validate(payload)
