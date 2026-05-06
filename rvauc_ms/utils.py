from rvauc_ms.schemas import YoloScanRequestBody

def scan_to_request_body(uniformTypeId: int, detections: dict[str, bool]):
    body: YoloScanRequestBody = {
        "uniformTypeId": uniformTypeId,
        "detections": { k: 100 for k, v in detections.items()}
    }

    return body