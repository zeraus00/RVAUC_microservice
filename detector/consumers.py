import json
from channels.generic.websocket import AsyncWebsocketConsumer
from pydantic import ValidationError
from uniform_service.yolo_utils import image_from_base64_bytes, run_yolo_on_cv_image
from detector.schemas.ws_requests import (
    FrameRequest,
    EvaluationRequest,
    ConfirmationRequest
)
from detector.schemas.ws_responses import (
    DetectionPayload,
    EvaluationPayload,
    ConfirmationPayload
)
from rvauc_ms import services

class YOLODetectionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("WS: Client Connected")

    async def disconnect(self, close_code):
        print("WS: Client Disconnected")

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return
            
        try:
            raw = json.loads(text_data)
            action = raw.get("action", "frame")

            if action == "frame":
                data = FrameRequest(**raw)
            elif action == "evaluation":
                data = EvaluationRequest(**raw)
            elif action == "confirmation":
                data = ConfirmationRequest(**raw)
            else:
                raise ValueError("Invalid action")

        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            if isinstance(e, ValidationError):
                message = {
                    "kind": "validation_error",
                    "details": e.errors()
                }
            else:
                message = {
                    "kind": "runtime_error",
                    "details": str(e)
                }

            await self.send(json.dumps({
                "type": "error",
                "error": message
            }))
            return

        # flow 1: Real-time Frame Processing human detection first
        if isinstance(data, FrameRequest):
            frame_b64 = data.frame
            if not frame_b64:
                return

            # Decode and Run YOLO
            img = image_from_base64_bytes(frame_b64)
            detected, boxes, status = run_yolo_on_cv_image(img)

            await self.send(text_data=json.dumps({
                "type": "detection",
                "result": DetectionPayload(
                    detected_items=detected,
                    boxes=boxes,
                    status=status
                ).model_dump(),
            }))

        # --- FLOW 2: Evaluation ---
        elif isinstance(data, EvaluationRequest):
            uniform_type_id = data.uniform_type_id
            detected = data.detected_items
            token: str = data.access_token
            
            evaluation_result = await services.RvaucMsService.evaluate_compliance(token, uniform_type_id, detected)

            await self.send(json.dumps({
                "type": "evaluation",
                "result": EvaluationPayload(
                    evaluation_result=evaluation_result
                ).model_dump(),
            }))

        # --- FLOW 3: Confirmation (Send to RVAUC-MS) ---
        elif isinstance(data, ConfirmationRequest):
            uniform_type_id = data.uniform_type_id
            detected = data.detected_items
            token: str = data.access_token
            
            confirmation_result = await services.RvaucMsService.confirm_compliance(token, uniform_type_id, detected)

            await self.send(json.dumps({
                "type": "confirmation",
                "result": ConfirmationPayload(
                    confirmation_result=confirmation_result
                ).model_dump(),
            }))