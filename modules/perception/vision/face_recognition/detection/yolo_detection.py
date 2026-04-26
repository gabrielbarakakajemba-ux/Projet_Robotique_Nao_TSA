# -*- coding: utf-8 -*-
import os
import torch
from ultralytics import YOLO

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MODEL_PATH = os.path.join(BASE_DIR, "models", "yolov8-face.pt")


class YOLODetector:
    def __init__(self, model_path="yolov8n.pt"):

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = YOLO(model_path)
        self.model.to(self.device)

    def detect_faces(self, frame, conf=0.6):

        results = self.model(frame, conf=conf, imgsz=640, verbose=False, device=self.device)
        faces = []

        if results and len(results) > 0 and results[0].boxes is not None:
            for box in results[0].boxes.xyxy:

                x1, y1, x2, y2 = [int(v) for v in box]

                height = y2 - y1
                width = x2 - x1

                padding = int(max(height, width) * 0.1)

                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = min(frame.shape[1], x2 + padding)
                y2 = min(frame.shape[0], y2 + padding)

                faces.append((x1, y1, x2, y2))

        return faces
