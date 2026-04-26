# -*- coding: utf-8 -*-

import torch
import numpy as np
from facenet_pytorch import InceptionResnetV1
from torchvision import transforms
import cv2


class FaceRecognizer:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        try:
            self.model = InceptionResnetV1(pretrained='vggface2').to(self.device).eval()
            print("[INFO] Modele FaceNet charge sur : " + self.device)
        except Exception as e:
            print("[ERROR] Impossible de charger FaceNet : " + str(e))

        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((160, 160)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])

    def _normalize(self, emb):
        if emb is None: return None
        norm = np.linalg.norm(emb)
        return emb / norm if norm != 0 else emb

    def get_embedding(self, face_img):
        if face_img is None or face_img.size == 0 or face_img.shape[0] < 50:
            return None
        try:
            face_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
            tensor = self.transform(face_rgb).unsqueeze(0).to(self.device)
            with torch.no_grad():
                embedding = self.model(tensor)
            return self._normalize(embedding.cpu().numpy()[0])
        except Exception:
            return None

    def cosine_distance(self, emb1, emb2):
        if emb1 is None or emb2 is None: return float('inf')
        e1, e2 = np.array(emb1, dtype=float), np.array(emb2, dtype=float)
        return 1.0 - float(np.clip(np.dot(e1, e2), -1.0, 1.0))

    def find_best_match(self, embedding, persons_db, threshold=0.4, confidence_margin=0.03):
        if not persons_db or embedding is None:
            return None, float('inf')

        distances = []
        for person_name, person_emb in persons_db:
            if person_emb is not None:
                distances.append((person_name, self.cosine_distance(embedding, person_emb)))

        if not distances: return None, float('inf')
        distances.sort(key=lambda x: x[1])
        best_name, best_dist = distances[0]

        if best_dist > threshold: return None, best_dist

        if len(distances) > 1:
            if (distances[1][1] - best_dist) < confidence_margin:
                return None, best_dist

        return best_name, best_dist
