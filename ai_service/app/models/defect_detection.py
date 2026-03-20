"""
Defect Detection Model
Uses YOLOv8 (ultralytics) for object detection on infrastructure imagery.
Model is loaded once at startup and cached in memory.
"""
import os
from typing import List, Optional
import numpy as np
from app.utils.logging import get_logger

logger = get_logger(__name__)

MODEL_CACHE_DIR = os.environ.get("MODEL_CACHE_DIR", "/app/models_cache")
DEFECT_MODEL_PATH = os.path.join(MODEL_CACHE_DIR, "defect_detection.pt")

# Defect class labels — map to model class indices
DEFECT_CLASSES = {
    0: "crack",
    1: "corrosion",
    2: "erosion",
    3: "delamination",
    4: "spalling",
    5: "broken_component",
    6: "missing_component",
    7: "discoloration",
}

SEVERITY_RULES = {
    "crack": lambda conf, area: "critical" if area > 0.05 else ("high" if conf > 0.8 else "medium"),
    "corrosion": lambda conf, area: "high" if area > 0.1 else "medium",
    "erosion": lambda conf, area: "medium" if conf > 0.7 else "low",
    "delamination": lambda conf, area: "high",
    "spalling": lambda conf, area: "critical" if area > 0.05 else "high",
    "broken_component": lambda conf, area: "critical",
    "missing_component": lambda conf, area: "critical",
    "discoloration": lambda conf, area: "low",
}

RECOMMENDATIONS = {
    "crack": "Schedule immediate structural assessment. Document crack width and propagation direction.",
    "corrosion": "Apply corrosion inhibitor treatment. Assess metal thickness loss.",
    "erosion": "Implement erosion control measures. Monitor progression.",
    "delamination": "Investigate cause of delamination. May indicate moisture intrusion.",
    "spalling": "Remove loose material. Repair exposed reinforcement if present.",
    "broken_component": "Replace broken component immediately. Do not operate until repaired.",
    "missing_component": "Source replacement component. Halt operations if safety-critical.",
    "discoloration": "Monitor for further degradation. May indicate chemical exposure.",
}


class DefectDetectionModel:
    def __init__(self):
        self._model = None
        self._loaded = False

    def load(self):
        """Load or download the model. Called once at startup."""
        try:
            from ultralytics import YOLO
            if os.path.exists(DEFECT_MODEL_PATH):
                logger.info("loading_defect_model_from_cache", path=DEFECT_MODEL_PATH)
                self._model = YOLO(DEFECT_MODEL_PATH)
            else:
                logger.info("downloading_base_model_yolov8n")
                # Use YOLOv8n as base — in production, replace with fine-tuned weights
                self._model = YOLO("yolov8n.pt")
                os.makedirs(MODEL_CACHE_DIR, exist_ok=True)
                self._model.save(DEFECT_MODEL_PATH)
            self._loaded = True
            logger.info("defect_model_loaded")
        except Exception as e:
            logger.error("defect_model_load_failed", error=str(e))
            raise

    def is_loaded(self) -> bool:
        return self._loaded

    def predict(
        self,
        image: np.ndarray,
        confidence_threshold: float = 0.5,
        image_key: Optional[str] = None,
    ) -> List[dict]:
        if not self._loaded:
            raise RuntimeError("Model not loaded")

        h, w = image.shape[:2]
        results = self._model(image, conf=confidence_threshold, verbose=False)
        detections = []

        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                defect_type = DEFECT_CLASSES.get(cls_id, f"unknown_class_{cls_id}")
                bbox = {
                    "x1": round(x1 / w, 4),
                    "y1": round(y1 / h, 4),
                    "x2": round(x2 / w, 4),
                    "y2": round(y2 / h, 4),
                }
                area = (bbox["x2"] - bbox["x1"]) * (bbox["y2"] - bbox["y1"])
                severity_fn = SEVERITY_RULES.get(defect_type, lambda c, a: "low")
                severity = severity_fn(conf, area)

                detections.append({
                    "type": defect_type,
                    "confidence": round(conf, 4),
                    "severity": severity,
                    "bbox": bbox,
                    "image_key": image_key,
                    "description": f"Detected {defect_type.replace('_', ' ')} with {conf:.1%} confidence",
                    "recommendation": RECOMMENDATIONS.get(defect_type, "Consult a structural engineer."),
                    "metadata": {"area_ratio": round(area, 4), "class_id": cls_id},
                })

        return detections


defect_model = DefectDetectionModel()
