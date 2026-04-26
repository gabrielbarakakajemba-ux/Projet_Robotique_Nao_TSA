# -*- coding: utf-8 -*-
import socket
import struct
import sys
import os
import cv2
import numpy as np
from pathlib import Path
import threading
import queue
import time
from flask import Flask, jsonify

current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from modules.perception.vision.face_recognition.detection.yolo_detection import YOLODetector
from modules.perception.vision.face_recognition.recognition.facenet_recognizer import FaceRecognizer
from database.faces_repository import FacesRepository
from modules.perception.vision.face_recognition.unknown_faces import UnknownFaceManager
from modules.perception.vision.face_recognition.hand_gesture_detection import create_hand_detector, open_hand, mp

HOST = "0.0.0.0"
PORT = 5002
MATCH_THRESHOLD = 0.4
PROCESS_EVERY_N_FRAMES = 3

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "yolov8-face.pt"

last_known_name = {"name": None, "timestamp": 0}

flask_app = Flask(__name__)

@flask_app.route("/last_face", methods=["GET"])
def last_face():
    elapsed = time.time() - last_known_name["timestamp"]
    if last_known_name["name"] and elapsed < 5.0:
        return jsonify({"name": last_known_name["name"]})
    return jsonify({"name": None})

def run_flask():
    flask_app.run(host="0.0.0.0", port=5001, use_reloader=False)

def send_text_message(conn, text):
    try:
        data = text.encode("utf-8")
        conn.sendall(struct.pack(">L", len(data)) + data)
    except:
        pass

def main():
    print("[INFO] Initialisation de l'IA (YOLO + FaceNet)...")
    detector = YOLODetector(str(MODEL_PATH))
    recognizer = FaceRecognizer()
    unknown_manager = UnknownFaceManager()

    persons_db = FacesRepository.get_all_persons()
    print("[INFO] {} visages connus charges depuis MariaDB".format(len(persons_db)))

    hand_detector = create_hand_detector()
    frame_queue = queue.Queue(maxsize=2)
    boxes_lock = threading.Lock()
    boxes_and_labels = []
    stop_event = threading.Event()

    def processing_loop():
        nonlocal persons_db
        while not stop_event.is_set():
            try:
                frame_to_process = frame_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            faces = detector.detect_faces(frame_to_process, conf=0.6)
            new_boxes = []

            for (x1, y1, x2, y2) in faces:
                face_crop = frame_to_process[y1:y2, x1:x2]
                if face_crop.size == 0: continue

                embedding = recognizer.get_embedding(face_crop)
                if embedding is None: continue

                name, distance = recognizer.find_best_match(embedding, persons_db, threshold=MATCH_THRESHOLD)

                if name:
                    label = "{} ({:.2f})".format(name, distance)
                    color = (0, 255, 0)
                    last_known_name["name"] = name
                    last_known_name["timestamp"] = time.time()
                else:
                    label = "INCONNU"
                    color = (0, 0, 255)
                    unknown_manager.add_unknown_face(embedding, frame=face_crop)

                new_boxes.append((x1, y1, x2, y2, label, color))

            with boxes_lock:
                boxes_and_labels[:] = new_boxes

    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=processing_loop, daemon=True).start()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print("[INFO] Serveur Vision pret. En attente du script Python 2 sur le NAO...")

    try:
        conn, addr = server_socket.accept()
        print("[INFO] NAO connecte : {}".format(addr))

        data_buffer = b''
        frame_count = 0

        while not stop_event.is_set():
            while len(data_buffer) < 4:
                packet = conn.recv(4096)
                if not packet: break
                data_buffer += packet

            if not data_buffer: break
            msg_size = struct.unpack(">L", data_buffer[:4])[0]
            data_buffer = data_buffer[4:]

            while len(data_buffer) < msg_size:
                data_buffer += conn.recv(min(65536, msg_size - len(data_buffer)))

            img_data = data_buffer[:msg_size]
            data_buffer = data_buffer[msg_size:]

            try:
                text_msg = img_data.decode("utf-8")
                if text_msg.startswith("REGISTER:"):
                    prenom = text_msg.split(":")[1].strip()
                    unregistered = unknown_manager.get_unregistered_faces()
                    if unregistered:
                        last_id = max(unregistered.keys())
                        emb = unregistered[last_id]["embedding"]
                        FacesRepository.insert_person(prenom, emb)
                        persons_db = FacesRepository.get_all_persons()
                        print("[SUCCESS] {} ajoute a la base de donnees !".format(prenom))
                        send_text_message(conn, "REGISTER_OK")
                    continue
            except:
                pass

            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is not None:
                frame_count += 1
                if frame_count % PROCESS_EVERY_N_FRAMES == 0:
                    if not frame_queue.full():
                        frame_queue.put(frame.copy())

                with boxes_lock:
                    for (x1, y1, x2, y2, label, color) in boxes_and_labels:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                cv2.imshow("NAO VISION - Camera de Bord", frame)
                if cv2.waitKey(1) & 0xFF == 27: break

    finally:
        stop_event.set()
        server_socket.close()
        cv2.destroyAllWindows()
