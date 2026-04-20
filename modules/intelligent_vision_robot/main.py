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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from detection.yolo_detection import YOLODetector
from recognition.facenet_recognizer import FaceRecognizer
from database.faces_repository import FacesRepository
from unknown_faces import UnknownFaceManager
from hand_gesture_detection import create_hand_detector, open_hand, mp

# ================= CONFIG =================
HOST = "0.0.0.0"
PORT = 5002
ACCEPT_TIMEOUT = 15.0
RECV_TIMEOUT = 10.0

ENABLE_RECOGNITION = True
PROCESS_EVERY_N_FRAMES = 5
DISPLAY_EVERY_N_FRAMES = 1
# ==========================================

PROJECT_ROOT = Path(__file__).parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "yolov8-face.pt"

MATCH_THRESHOLD = 0.4
CONFIDENCE_MARGIN = 0
RELOAD_DB_EVERY_N_FRAMES = 150

# Dernière reconnaissance — partagée entre threads
last_known_name = {"name": None, "timestamp": 0}

# ================= FLASK API =================
flask_app = Flask(__name__)

@flask_app.route("/last_face", methods=["GET"])
def last_face():
    elapsed = time.time() - last_known_name["timestamp"]
    if last_known_name["name"] and elapsed < 60.0:
        return jsonify({"name": last_known_name["name"]})
    return jsonify({"name": None})

def run_flask():
    flask_app.run(host="0.0.0.0", port=5001, use_reloader=False)
# =============================================


def send_text_message(conn, text):
    data = text.encode("utf-8")
    conn.sendall(struct.pack(">L", len(data)) + data)


def main():
    print("[INFO] Initialisation...")

    detector = YOLODetector(str(MODEL_PATH))
    recognizer = FaceRecognizer()
    unknown_manager = UnknownFaceManager()
    persons_db = FacesRepository.get_all_persons()
    print(f"[INFO] {len(persons_db)} personnes chargees")

    hand_detector = create_hand_detector()
    frame_timestamp_ms = 0
    hand_event_active = False

    frame_queue = queue.Queue(maxsize=2)
    boxes_lock = threading.Lock()
    boxes_and_labels = []
    stop_event = threading.Event()

    def processing_loop():
        nonlocal persons_db
        local_frame_idx = 0

        while not stop_event.is_set():
            try:
                frame_to_process = frame_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            local_frame_idx += 1

            if local_frame_idx % RELOAD_DB_EVERY_N_FRAMES == 0:
                persons_db = FacesRepository.get_all_persons()
                print(f"[INFO] DB rechargée ({len(persons_db)} personnes)")

            faces = detector.detect_faces(frame_to_process, conf=0.6)
            new_boxes = []

            for (x1, y1, x2, y2) in faces:
                face_crop = frame_to_process[y1:y2, x1:x2]
                if face_crop.size == 0:
                    continue

                embedding = recognizer.get_embedding(face_crop)
                if embedding is None:
                    continue

                name, distance = recognizer.find_best_match(
                    embedding, persons_db,
                    threshold=MATCH_THRESHOLD,
                    confidence_margin=CONFIDENCE_MARGIN
                )

                if name:
                    label = f"{name} ({distance:.2f})"
                    color = (0, 255, 0)
                else:
                    label = "INCONNU"
                    color = (0, 165, 255)
                    unknown_manager.add_unknown_face(embedding, frame=face_crop)

                new_boxes.append((x1, y1, x2, y2, label, color))

            with boxes_lock:
                boxes_and_labels[:] = new_boxes

    # Lance Flask en arrière-plan
    threading.Thread(target=run_flask, daemon=True).start()
    print("[INFO] API reconnaissance disponible sur port 5001")

    # --- Socket NAO ---
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    server_socket.settimeout(ACCEPT_TIMEOUT)

    print("[INFO] En attente connexion NAO...")
    try:
        conn, addr = server_socket.accept()
        print("[INFO] Connecté :", addr)
        conn.settimeout(RECV_TIMEOUT)
    except socket.timeout:
        print("[ERROR] Timeout en attente de connexion NAO")
        server_socket.close()
        return

    if ENABLE_RECOGNITION:
        threading.Thread(target=processing_loop, daemon=True).start()

    data_buffer = b''
    frame_count = 0

    print("[INFO] Flux en cours (ESC pour quitter)...")

    try:
        while not stop_event.is_set():

            # --- Lecture header ---
            while len(data_buffer) < 4 and not stop_event.is_set():
                try:
                    packet = conn.recv(4096)
                    if not packet:
                        raise ConnectionError("NAO déconnecté")
                    data_buffer += packet
                except socket.timeout:
                    continue

            if len(data_buffer) < 4:
                break

            msg_size = struct.unpack(">L", data_buffer[:4])[0]
            data_buffer = data_buffer[4:]

            if msg_size == 0 or msg_size > 5_000_000:
                print(f"[WARN] Taille suspecte reçue: {msg_size}, flush buffer")
                data_buffer = b''
                continue

            # --- Lecture payload ---
            while len(data_buffer) < msg_size and not stop_event.is_set():
                try:
                    packet = conn.recv(min(65536, msg_size - len(data_buffer)))
                    if not packet:
                        raise ConnectionError("NAO déconnecté pendant payload")
                    data_buffer += packet
                except socket.timeout:
                    continue

            if len(data_buffer) < msg_size:
                break

            img_data = data_buffer[:msg_size]
            data_buffer = data_buffer[msg_size:]

            # --- Message texte REGISTER ? ---
            try:
                text_msg = img_data.decode("utf-8")
                if text_msg.startswith("REGISTER:"):
                    prenom = text_msg.split(":", 1)[1].strip()
                    print(f"[INFO] REGISTER reçu: {prenom}")
                    unregistered = unknown_manager.get_unregistered_faces()
                    if unregistered:
                        last_id = sorted(unregistered.keys(), reverse=True)[0]
                        emb = unregistered[last_id]["embedding"]
                        FacesRepository.insert_person(prenom, emb)
                        unknown_manager.register_unknown_face(last_id, prenom)
                        persons_db = FacesRepository.get_all_persons()
                        print(f"[INFO] {prenom} enregistré (total: {len(persons_db)})")
                    else:
                        print("[WARN] Aucun visage inconnu pour REGISTER")
                    continue
            except UnicodeDecodeError:
                pass

            # --- Décode image ---
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None:
                continue

            frame_count += 1

            # --- Envoi au thread de reconnaissance ---
            if ENABLE_RECOGNITION and frame_count % PROCESS_EVERY_N_FRAMES == 0:
                try:
                    if frame_queue.full():
                        frame_queue.get_nowait()
                    frame_queue.put_nowait(frame.copy())
                except (queue.Empty, queue.Full):
                    pass

            # --- Détection main ---
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            result = hand_detector.detect_for_video(mp_image, frame_timestamp_ms)
            frame_timestamp_ms += 33

            open_hand_detected = any(
                open_hand(lm) for lm in result.hand_landmarks
            ) if result.hand_landmarks else False

            if open_hand_detected and not hand_event_active and ENABLE_RECOGNITION:
                hand_event_active = True
                print("[INFO] Main ouverte détectée, reconnaissance ponctuelle...")

                faces_for_gesture = detector.detect_faces(frame, conf=0.6)
                if faces_for_gesture:
                    x1, y1, x2, y2 = faces_for_gesture[0]
                    face_crop = frame[y1:y2, x1:x2]
                    emb = recognizer.get_embedding(face_crop) if face_crop.size != 0 else None
                    if emb is not None:
                        name, distance = recognizer.find_best_match(
                            emb, persons_db,
                            threshold=MATCH_THRESHOLD,
                            confidence_margin=CONFIDENCE_MARGIN
                        )
                        if name:
                            print(f"[INFO] Reconnu: {name} ({distance:.2f})")
                            last_known_name["name"] = name        # ← mise à jour API
                            last_known_name["timestamp"] = time.time()
                            send_text_message(conn, f"KNOWN:{name}")
                        else:
                            print("[INFO] Inconnu, sauvegarde embedding")
                            last_known_name["name"] = None        # ← reset
                            unknown_manager.add_unknown_face(emb, frame=face_crop)
                            send_text_message(conn, "UNKNOWN")
                    else:
                        print("[WARN] Embedding impossible")
                else:
                    print("[INFO] Aucun visage au moment du geste")

            if not open_hand_detected:
                hand_event_active = False

            # --- Affichage ---
            with boxes_lock:
                current_boxes = list(boxes_and_labels)

            for (x1, y1, x2, y2, label, color) in current_boxes:
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            cv2.imshow("NAO Face Recognition", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    except ConnectionError as e:
        print(f"[ERROR] {e}")
    finally:
        stop_event.set()
        conn.close()
        server_socket.close()
        cv2.destroyAllWindows()
        print("[INFO] Arrêt du système")


if __name__ == "__main__":
    main()