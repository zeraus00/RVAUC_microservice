import os
import cv2
import base64
import numpy as np
from ultralytics import YOLO
from pathlib import Path

# FIX: Calculate path relative to this file (avoiding Django settings errors on import)
# File location: project/uniform_service/yolo_utils.py -> Go up 2 levels -> project/
BASE_PATH = Path(__file__).resolve().parent.parent
MODEL_PATH = os.path.join(BASE_PATH, "best.pt")

try:
    model = YOLO(MODEL_PATH)
    print(f"SUCCESS: Loaded YOLO model from {MODEL_PATH}")
except Exception as e:
    model = None
    print(f"ERROR: Could not load model at {MODEL_PATH}. Error: {e}")

def image_from_base64_bytes(b64str):
    # FIX: Handle cases where frontend sends "data:image/jpeg;base64," prefix
    if "," in b64str:
        b64str = b64str.split(",")[1]
        
    try:
        image_bytes = base64.b64decode(b64str)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

def run_yolo_on_cv_image(img_cv, conf_thres=0.25):
    if model is None or img_cv is None:
        return {}, []

    # Run inference
    results = model(img_cv, imgsz=640, verbose=False)[0]
    detected = {}
    boxes = []
    
    for box in results.boxes:
        cls_id = int(box.cls)
        conf = float(box.conf)
        
        # Get label safely
        if hasattr(results, "names") and cls_id in results.names:
            label = results.names[cls_id]
        else:
            label = str(cls_id)
            
        if conf >= conf_thres:
            detected[label] = True
            # box.xyxy is a tensor, convert to list
            xyxy = box.xyxy[0].tolist() 
            boxes.append({"label": label, "conf": conf, "xyxy": xyxy})
            
    return detected, boxes