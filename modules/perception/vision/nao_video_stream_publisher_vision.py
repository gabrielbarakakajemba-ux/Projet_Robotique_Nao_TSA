# -*- coding: utf-8 -*-
import socket
import struct
import cv2
import numpy as np
import qi
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from config.nao_config import ROBOT_IP, PORT
from config.pc_config import PC_IP, PC_PORT

# ------------------ Connexion NAO ------------------
session = qi.Session()
session.connect("tcp://{}:{}".format(ROBOT_IP, PORT))

video = session.service("ALVideoDevice")
tts   = session.service("ALTextToSpeech")

# ------------------ CAMERA ------------------
name_id = video.subscribeCamera(
    "python_stream",
    0,   # caméra top
    1,   # 320x240
    11,  # RGB
    15   # FPS
)

# ------------------ SOCKET ------------------
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
# PAS de settimeout global ici — on gère le non-bloquant uniquement en lecture

def recv_text_message():
    """
    Lecture non bloquante d'un message PC.
    Passe le socket en non-bloquant le temps de la lecture,
    puis le remet en bloquant pour les envois.
    """
    try:
        sock.setblocking(False)
        header = sock.recv(4)
    except socket.error:
        # Pas de données dispo, c'est normal
        return None
    except Exception:
        return None
    finally:
        sock.setblocking(True)

    if not header or len(header) < 4:
        return None

    size = struct.unpack(">L", header)[0]
    data = b""
    # Ici le socket est bloquant : on attend le reste du message
    sock.settimeout(2.0)
    try:
        while len(data) < size:
            chunk = sock.recv(size - len(data))
            if not chunk:
                break
            data += chunk
    except socket.timeout:
        print("[WARN] Timeout lecture message PC")
        return None
    finally:
        sock.settimeout(None)  # Remet sans timeout pour les sendall

    return data.decode("utf-8") if data else None


# Attente connexion PC
print("[INFO] Connexion au PC {}:{}...".format(PC_IP, PC_PORT))
while True:
    try:
        sock.connect((PC_IP, PC_PORT))
        print("[INFO] Connecté au PC")
        break
    except Exception as e:
        print("[INFO] Attente serveur PC... ({})".format(e))
        time.sleep(1.0)

JPEG_QUALITY  = 50   # Réduit la taille des frames → moins de charge réseau
FRAME_SKIP    = 2    # Envoie toutes les frames (le PC gère le throttle)

try:
    frame_idx = 0
    while True:

        # 1) Vérifier si le PC a envoyé une réponse
        msg = recv_text_message()
        if msg:
            if msg.startswith("KNOWN:"):
                prenom = msg.split(":", 1)[1]
                print("[INFO] KNOWN: {}".format(prenom))
                tts.say(u"Salut {}!".format(prenom))

            elif msg == "UNKNOWN":
                print("[INFO] UNKNOWN reçu")
                tts.say(u"Je ne te connais pas. Quel est ton prénom ?")
                # raw_input pour Python 2 (NAO), input pour Python 3
                try:
                    prenom = raw_input("Prénom : ").strip()
                except NameError:
                    prenom = input("Prénom : ").strip()

                if prenom:
                    payload = ("REGISTER:" + prenom).encode("utf-8")
                    sock.sendall(struct.pack(">L", len(payload)) + payload)
                    print("[INFO] REGISTER envoyé pour {}".format(prenom))

        # 2) Capture image
        nao_image = video.getImageRemote(name_id)
        if nao_image is None:
            time.sleep(0.02)
            continue

        width  = nao_image[0]
        height = nao_image[1]
        array  = nao_image[6]

        frame = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Optionnel : skip frames pour réduire la charge réseau
        frame_idx += 1
        if FRAME_SKIP > 0 and frame_idx % (FRAME_SKIP + 1) != 0:
            continue

        ret, jpeg = cv2.imencode(
            '.jpg', frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
        )
        if not ret:
            continue

        data = jpeg.tobytes()
        try:
            sock.sendall(struct.pack(">L", len(data)) + data)
        except Exception as e:
            print("[ERROR] Envoi échoué: {}".format(e))
            break

finally:
    print("[INFO] Nettoyage NAO")
    video.unsubscribe(name_id)
    sock.close()