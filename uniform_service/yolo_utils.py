import os
import cv2
import base64
import numpy as np
from ultralytics import YOLO # type:ignore
from pathlib import Path

# FIX: Calculate path relative to this file
BASE_PATH = Path(__file__).resolve().parent.parent

# 1. Define and Load all models into a dictionary immediately
# Using the name 'MODELS' is clearer than 'MODEL_PATH' for loaded objects
MODELS = {
    "human": YOLO(os.path.join(BASE_PATH, "human_detection.pt")),
    "type_a_male": YOLO(os.path.join(BASE_PATH, "best.pt")),
    "type_a_female": YOLO(os.path.join(BASE_PATH, "Type_A_Female.pt")),
    "buffalo": YOLO(os.path.join(BASE_PATH, "buffalo.pt")),
    "cs_dept_shirt": YOLO(os.path.join(BASE_PATH, "cs_deptshirt.pt"))
}

def image_from_base64_bytes(b64str):
    if "," in b64str:
        b64str = b64str.split(",")[1]
        
    try:
        image_bytes = base64.b64decode(b64str)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return None

        img = cv2.resize(img, (640, 480))
        return img
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

def run_yolo_on_cv_image(img_cv, conf_thres=0.25):
    """
    Human detection first.
    If human is detected, scan all uniform models.
    """
    if img_cv is None:
        return {}, [], "Invalid Image"

    # 1. Human detection
    human_results = MODELS["human"](img_cv, verbose=False)[0]
    human_detected = any(box.conf >= 0.5 for box in human_results.boxes)

    if not human_detected:
        return {}, [], "No Human Detected"

    # 2. Uniform scanning
    all_detected = {}
    all_boxes = []

    # Iterate through each uniform model
    key = "type_a_male"
    current_model = MODELS[key] 
    results = current_model(img_cv, imgsz=640, verbose=False)[0]
    
    for box in results.boxes:
        cls_id = int(box.cls)
        conf = float(box.conf)
        
        # Get label safely from the current model's names dictionary
        label = results.names[cls_id] if cls_id in results.names else str(cls_id)
            
        if conf >= conf_thres:
            all_detected[label] = True
            all_boxes.append({
                "label": label, 
                "conf": conf, 
                "xyxy": box.xyxy[0].tolist(),
                "source_model": key 
            })
        
    return all_detected, all_boxes, "Success"