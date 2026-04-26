# -*- coding: utf-8 -*-
import sys
import os
import socket
import struct
import cv2
import numpy as np

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, root_path)

try:
    from config.python_paths import NAOQI_LIB_PATH
    if NAOQI_LIB_PATH not in sys.path:
        sys.path.insert(0, NAOQI_LIB_PATH)

    print("[INFO] Chemins charges avec succes : " + NAOQI_LIB_PATH)
except ImportError:
    print("[ERREUR] Impossible de trouver python_paths.py")
    sys.exit(1)

try:
    import qi
    print("[SUCCESS] Le module 'qi' est charge !")
except ImportError:
    print("[ERREUR] 'qi' est toujours introuvable dans : " + NAOQI_LIB_PATH)
    sys.exit(1)

import pygame
import time
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from config.nao_config import ROBOT_IP, PORT
from config.pc_config import PC_IP, PC_PORT
from utils.nao_movement import pickup_bottle


session = qi.Session()
session.connect("tcp://{}:{}".format(ROBOT_IP, PORT))

video = session.service("ALVideoDevice")
motion = session.service("ALMotion")
posture = session.service("ALRobotPosture")

posture.goToPosture("StandInit", 0.5)
motion.wakeUp()
motion.setStiffnesses("Head", 1.0)

name_id = video.subscribeCamera(
    "python_stream",
    0,
    1,
    11,
    15
)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

while True:
    try:
        sock.connect((PC_IP, PC_PORT))
        break
    except Exception:
        print("[INFO] Connexion refusee, attente du serveur PC...")
        time.sleep(0.5)

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("Aucune manette detectee")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

print("Systeme pret")

YAW_MAX = 2.0
PITCH_MAX = 0.5

head_lock = threading.Lock()
head_angles = [0.0, 0.0]
head_running = True

def head_worker():
    global head_angles
    last_angles = [0.0, 0.0]
    while head_running:
        with head_lock:
            target_angles = list(head_angles)
        if target_angles != last_angles:
            try:
                motion.setAngles(["HeadYaw", "HeadPitch"], target_angles, 0.15)
                last_angles = target_angles
            except Exception as e:
                print("Erreur tete: {}".format(e))
        time.sleep(0.05)

head_thread = threading.Thread(target=head_worker)
head_thread.daemon = True
head_thread.start()

movement_lock = threading.Lock()
movement_command = [0.0, 0.0, 0.0]
movement_running = True

def movement_worker():
    global movement_command
    last_command = [0.0, 0.0, 0.0]
    while movement_running:
        with movement_lock:
            cmd = list(movement_command)
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
        time.sleep(0.05)

movement_thread = threading.Thread(target=movement_worker)
movement_thread.daemon = True
movement_thread.start()

try:
    while True:
        pygame.event.pump()

        axis_yaw = joystick.get_axis(2)
        axis_pitch = joystick.get_axis(3)
        with head_lock:
            head_angles = [-axis_yaw * YAW_MAX, axis_pitch * PITCH_MAX]

        button_pickup = 14
        btn_stop = joystick.get_button(3)

        if joystick.get_button(button_pickup):
            with movement_lock:
                movement_command = [0.0, 0.0, 0.0]
            motion.stopMove()
            pickup_bottle(motion, posture)

        if btn_stop:
            print("Arret demande")
            break

        axe_x = joystick.get_axis(0)
        axe_y = joystick.get_axis(1)

        with movement_lock:
            if abs(axe_x) > 0.1 or abs(axe_y) > 0.1:
                movement_command = [-axe_y * 0.2, 0.0, -axe_x * 0.5]
            else:
                movement_command = [0.0, 0.0, 0.0]

        nao_image = video.getImageRemote(name_id)
        if nao_image is None:
            continue

        width, height = nao_image[0], nao_image[1]
        array = nao_image[6]

        frame = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        if not ret:
            continue

        data = jpeg.tobytes()
        try:
            sock.sendall(struct.pack(">L", len(data)) + data)
        except:
            break

finally:
    head_running = False
    movement_running = False
    time.sleep(0.1)
    motion.stopMove()
    video.unsubscribe(name_id)
    motion.setStiffnesses("Head", 0.0)
    sock.close()
    pygame.quit()
