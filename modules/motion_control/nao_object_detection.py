import socket
import struct
import cv2
import os
import sys
import numpy as np
import threading
import queue
import time
from ultralytics import YOLO
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# ----------------------- CONFIG --------------------
HOST = "0.0.0.0"
PORT = 5000
# ---------------------------------------------------

# Charger modèle YOLO
model = YOLO("models/yolov8n.pt")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print("En attente de connexion du NAO...")
conn, addr = server_socket.accept()
conn.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
print("Connecté à :", addr)

data_buffer = b''
bottle_present = False  # pour éviter spam print
frame_queue = queue.Queue(maxsize=1)
detections_lock = threading.Lock()
detections = []
# 
prev_boxes = []
prev_age = 0
MAX_PERSIST_FRAMES = 6
running = True


def inference_worker():
    global detections
    while running:
        try:
            frame = frame_queue.get(timeout=0.2)
        except queue.Empty:
            continue

        # Exécuter l'inférence YOLO (potentiellement lente) en arrière-plan
        results = model(frame, conf=0.5, verbose=False)

        boxes = []
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                label = model.names[cls]

                if label == "bottle":
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    boxes.append((x1, y1, x2, y2))

        with detections_lock:
            # modifier sur place pour que la référence côté thread principal reste valide
            detections[:] = boxes


# Démarrer le thread d'inférence
worker_thread = threading.Thread(target=inference_worker)
worker_thread.daemon = True
worker_thread.start()

try:
    while True:
        # Lire taille image
        while len(data_buffer) < 4:
            packet = conn.recv(4096)
            if not packet:
                break
            data_buffer += packet

        if len(data_buffer) < 4:
            continue

        packed_size = data_buffer[:4]
        data_buffer = data_buffer[4:]
        msg_size = struct.unpack(">L", packed_size)[0]

        # Lire image complète
        while len(data_buffer) < msg_size:
            packet = conn.recv(4096)
            if not packet:
                break
            data_buffer += packet

        if len(data_buffer) < msg_size:
            continue

        img_data = data_buffer[:msg_size]
        data_buffer = data_buffer[msg_size:]

        # IMPORTANT : vider le buffer restant
        data_buffer = b''

        # Décoder image
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Mettre la frame dans la file pour inférence en arrière-plan (conserver uniquement la plus récente)
        try:
            if frame_queue.full():
                try:
                    _ = frame_queue.get_nowait()
                except queue.Empty:
                    pass
            frame_queue.put_nowait(frame.copy())
        except queue.Full:
            pass

        # Dessiner les détections produites par le thread d'inférence
        with detections_lock:
            boxes_copy = list(detections)

        # Si pas de détection sur cette frame, réutiliser les boxes précédentes pendant un court instant pour éviter le scintillement
        if boxes_copy:
            prev_boxes = boxes_copy
            prev_age = 0
        else:
            if prev_boxes and prev_age < MAX_PERSIST_FRAMES:
                boxes_copy = prev_boxes
                prev_age += 1
            else:
                boxes_copy = []
                prev_boxes = []
                prev_age = 0

        bottle_detected = False
        for (x1, y1, x2, y2) in boxes_copy:
            bottle_detected = True
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, "Bottle", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Afficher une seule fois quand la bouteille apparaît
        if bottle_detected and not bottle_present:
            print("Bouteille détectée")
            bottle_present = True

        if not bottle_detected:
            bottle_present = False

        # -------------------------------------------

        cv2.imshow("NAO YOLO Bottle Detection", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    # arrêter proprement le thread d'inférence
    running = False
    try:
        worker_thread.join(timeout=1.0)
    except Exception:
        pass

    conn.close()
    server_socket.close()
    cv2.destroyAllWindows()
    print("\nArrêt du programme")
