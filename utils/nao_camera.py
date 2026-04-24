# -*- coding: utf-8 -*-
import cv2
import numpy as np
import time
import sys

def get_nao_frame(video_service, name_id):
    """
    Récupère une seule image du robot et la convertit en format OpenCV.
    Utile pour l'analyse ponctuelle.
    """
    try:
        nao_image = video_service.getImageRemote(name_id)
        if nao_image is None:
            return None

        width = nao_image[0]
        height = nao_image[1]
        array = nao_image[6]

        # Conversion efficace de l'image brute vers numpy
        frame = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))
        # Conversion RGB (NAO) vers BGR (OpenCV)
        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    except Exception as e:
        print("[ERROR] Erreur lors de la capture de l'image: " + str(e))
        return None

def setup_camera(video_service, camera_id=0, res_id=1, fps=15):
    """
    Configure et enregistre le flux caméra.
    camera_id : 0 (Top), 1 (Bottom)
    res_id : 1 (320x240), 2 (640x480)
    """
    unique_name = "cam_session_" + str(int(time.time()))
    
    try:
        name_id = video_service.subscribeCamera(unique_name, camera_id, res_id, 11, fps)
        print("[INFO] Camera souscrite avec l'ID : " + name_id)
        return name_id
    except Exception as e:
        print("[ERROR] Impossible de connecter la camera : " + str(e))
        return None

def release_camera(video_service, name_id):
    """ Libère proprement la caméra du robot """
    try:
        if name_id:
            video_service.unsubscribe(name_id)
            print("[INFO] Camera liberee.")
    except Exception as e:
        pass