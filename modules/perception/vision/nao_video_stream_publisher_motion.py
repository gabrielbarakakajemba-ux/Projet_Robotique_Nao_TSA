# -*- coding: utf-8 -*-
import socket
import struct
import cv2
import numpy as np
import qi
import sys
import os
import pygame
import time
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from config.nao_config import ROBOT_IP, PORT
from config.pc_config import PC_IP, PC_PORT
from utils.nao_movement import pickup_bottle

# ----------------------- CONFIG -----------------------

session = qi.Session()
session.connect("tcp://{}:{}".format(ROBOT_IP, PORT))

video = session.service("ALVideoDevice")
motion = session.service("ALMotion")
posture = session.service("ALRobotPosture")

posture.goToPosture("StandInit", 0.5)
motion.wakeUp()
motion.setStiffnesses("Head", 1.0)

# -------------------------- CAMERA --------------------
name_id = video.subscribeCamera(
    "python_stream",
    0,
    1,      # 320x240
    11,
    15
)

# ------------------------- SOCKET --------------------------
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

# Attendre indéfiniment que le serveur PC écoute (utile si Python3 met du temps à démarrer)
while True:
    try:
        sock.connect((PC_IP, PC_PORT))
        break
    except Exception:
        print("[INFO] Connexion refusée, attente du serveur PC...")
        time.sleep(0.5)

# ------------------------- JOYSTICK ------------------------
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("Aucune manette détectée")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

print("Système prêt")

# Limites tête
YAW_MAX = 2.0
PITCH_MAX = 0.5

# -------------------------- HEAD CONTROL --------------------------------
head_lock = threading.Lock()
head_angles = [0.0, 0.0]  # [yaw, pitch]
head_running = True

def head_worker():
    """Worker thread pour contrôler la tête sans bloquer le stream vidéo"""
    global head_angles
    last_angles = [0.0, 0.0]
    
    while head_running:
        with head_lock:
            target_angles = list(head_angles)
        
        # N'envoyer que si les angles ont changé (debouncing)
        if target_angles != last_angles:
            try:
                motion.setAngles(
                    ["HeadYaw", "HeadPitch"],
                    target_angles,
                    0.15  # vitesse
                )
                last_angles = target_angles
            except Exception as e:
                print("Erreur tête: {}".format(e))
        
        time.sleep(0.05)  # 20 Hz

head_thread = threading.Thread(target=head_worker)
head_thread.daemon = True
head_thread.start()

# ---------------------------MOVEMENT CONTROL ----------------------
movement_lock = threading.Lock()
movement_command = [0.0, 0.0, 0.0]  # [x, y, theta]
movement_running = True

def movement_worker():
    """Worker thread pour controler le mouvement sans bloquer"""
    global movement_command
    last_command = [0.0, 0.0, 0.0]
    
    while movement_running:
        with movement_lock:
            cmd = list(movement_command)
        
        # N'envoyer que si la commande a changé
        if cmd != last_command:
            try:
                x, y, theta = cmd
                if abs(x) > 0.01 or abs(y) > 0.01 or abs(theta) > 0.01:
                    motion.move(x, y, theta)
                else:
                    motion.stopMove()
                last_command = cmd
            except Exception as e:
                print("Erreur mouvement: {}".format(e))
        
        time.sleep(0.05)  # 20 Hz

movement_thread = threading.Thread(target=movement_worker)
movement_thread.daemon = True
movement_thread.start()

try:
    while True:

        # -------------- JOYSTICK (non-bloquant) ------------
        pygame.event.pump()

        # Lecture axes du joystick gauche
        axis_x = joystick.get_axis(2)  # gauche/droite
        axis_y = joystick.get_axis(3)  # haut/bas

        yaw = -axis_x * YAW_MAX  # Inverser gauche/droite
        pitch = axis_y * PITCH_MAX

        # Juste mettre à jour, le worker l'envoie
        with head_lock:
            head_angles = [yaw, pitch]

        button_pickup = 14  # bouton “X” sur ta manette
        btn_start = joystick.get_button(3) 

        pygame.event.pump()
        if joystick.get_button(button_pickup):
            pickup_bottle(motion, posture)

        # Lecture axes du joystick gauche
        axe_x = joystick.get_axis(0)  # gauche/droite
        axe_y = joystick.get_axis(1)  # avant/arrière

        # Déplacements proportionnels au joystick
        if abs(axe_x) > 0.1 or abs(axe_y) > 0.1:
            motion.moveTo(-axe_y*0.2, 0, -axe_x*0.5)

        elif btn_start:
            print("Bouton Start pressé, arrêt du script")
            motion.stopMove()
            pygame.quit()
            sys.exit(0)
       
        # ----------------- CAMERA (priorité haute) --------------
        nao_image = video.getImageRemote(name_id)
        if nao_image is None:
            continue

        width = nao_image[0]
        height = nao_image[1]
        array = nao_image[6]

        frame = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        ret, jpeg = cv2.imencode(
            '.jpg',
            frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), 70]
        )

        if not ret:
            continue

        data = jpeg.tobytes()
        try:
            sock.sendall(struct.pack(">L", len(data)) + data)
        except (BrokenPipeError, ConnectionResetError):
            print("PC déconnecté")
            break

finally:
    head_running = False
    movement_running = False
    motion.stopMove()
    video.unsubscribe(name_id)
    motion.setStiffnesses("Head", 0.0)
    sock.close()
    pygame.quit()
