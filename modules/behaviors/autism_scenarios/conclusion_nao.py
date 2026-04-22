# -*- coding: utf-8 -*-
import sys
import os

ROOT_DIR = "/home/mr-kajemba/Nao_Autisme"
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from config.python_paths import NAOQI_LIB_PATH
    if NAOQI_LIB_PATH not in sys.path:
        sys.path.insert(0, NAOQI_LIB_PATH)
except ImportError:
    print("Erreur : Impossible de charger config.python_paths")

import qi

import time
from config.nao_config import ROBOT_IP, PORT
from config.settings import apply_settings
from utils.speech_and_animation_player import say_with_animation

if not ROBOT_IP:
    print("IP du robot non définie")
    exit()

#Connexion au Nao
session=qi.Session()

try :
    session.connect("tcp://{}:{}".format(ROBOT_IP, PORT))
    print("Connexion réussie")
except RuntimeError:
    print("Impossible de se connecter au robot")

apply_settings(session)

tts = session.service("ALTextToSpeech")
motion = session.service("ALMotion")
posture = session.service("ALRobotPosture")
animation_player = session.service("ALAnimationPlayer")

# Mettre le robot en posture initiale
posture.goToPosture("StandInit", 0.5) 

say_with_animation(tts, 
                   animation_player, 
                   """Les enfants, vous avez vu ? Les mangroves, les herbiers et les coraux sont des trésors vivants ! Si on les protège, on protège aussi notre planète.""",
                    "animations/Stand/Gestures/Explain_2")

time.sleep(1)

say_with_animation(tts,
                   animation_player,
                   """Alors, qui veut devenir un gardien de l’océan ? Souvenez-vous qu’un petit geste de votre part pourra aider l’environnement.""",
                   "animations/Stand/Emotions/Positive/Excited_2"
                   )

time.sleep(1)

tts.say("Au revoir les amis !")
animation_player.run("animations/Stand/Gestures/Hey_3")
