import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from uniform_service.yolo_utils import image_from_base64_bytes, run_yolo_on_cv_image
from channels.db import database_sync_to_async
from evaluations.models import Evaluation, Student
from django.utils import timezone
from rvauc_ms import services

class YOLODetectionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.last_detected = {}
        self.last_uniform_type = "type_a_male" # default
        print("WS: Client Connected")

    async def disconnect(self, close_code):
        print("WS: Client Disconnected")

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return
            
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        action = data.get("action", "frame")

        # flow 1: Real-time Frame Processing human detection first
        if action == "frame":
            frame_b64 = data.get("frame")
            if not frame_b64:
                return

            # Decode and Run YOLO
            img = image_from_base64_bytes(frame_b64)
            detected, boxes, status = run_yolo_on_cv_image(img)

            print("Last Detected: " + json.dumps(detected), flush=True)

            await self.send(text_data=json.dumps({
                "type": "detection",
                "detected_items": detected, # e.g. {'polo': True, 'logo': True}
                "boxes": boxes,
                "status" : status  
            }))

        # --- FLOW 2: Verification (Save to DB) ---
        elif action == "verify":
            student_id = data.get("student_id", "")
            # Save the snapshot to the session memory
            self.last_detected = data.get("detected_items", {})
            
            # Create the record and run completeness logic and Send evaluation to rvauc ms server
            print("Starting evaluation", flush=True)
            eval_data = await self.create_evaluation_entry(student_id, self.last_detected)
            print("Evaluation done", flush=True)

            await self.send(text_data=json.dumps({
                "type": "verify_result",
                "detected_items": self.last_detected,
                "evaluation": eval_data
            }))

            print("Response sent", flush=True)

        # --- FLOW 3: Confirmation (Send to RVAUC-MS) ---
        elif action == "confirm":
            # todo: add validation, dapat verified muna before magconfirm
            token = data.get("access_token", "")
            # detected_items = data.get("detected_items", {})

            # Send evaluation to rvauc ms server
            new_record = await services.RvaucMsService.new_record(
                token,
                self.last_detected,
                self.last_uniform_type
                )

            await self.send(text_data=json.dumps({
                "type": "confirm_result",
                "evaluation": new_record.dict() if hasattr(new_record, 'dict') else new_record
            }))

    @database_sync_to_async
    def create_evaluation_entry(self, student_id_raw, detected_items):
        student = None
        if student_id_raw:
            # Flexible lookup: existing student or create temp
            student, _ = Student.objects.get_or_create(student_id=student_id_raw)

        eval_obj = Evaluation.objects.create(
            student=student,
            student_id_raw=student_id_raw or "UNKNOWN",
            detected_items=detected_items,
            created_at=timezone.now()
        )

        # Calculate score/logic inside the model method
        completeness, missing, score = eval_obj.compute_completeness()
        
        eval_obj.completeness = completeness
        eval_obj.missing = missing
        eval_obj.score = score
        eval_obj.save()

        return {
            "id": eval_obj.id,
            "student_id": eval_obj.student_id_raw,
            "completeness": eval_obj.completeness,
            "missing": eval_obj.missing,
            "score": eval_obj.score,
            "created_at": eval_obj.created_at.isoformat()
        }