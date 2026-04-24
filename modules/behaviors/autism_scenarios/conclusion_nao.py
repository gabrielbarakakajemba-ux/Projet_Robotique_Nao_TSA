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
    sys.exit(1)

import qi

import time
from config.nao_config import ROBOT_IP, PORT
from config.settings import apply_settings
from utils.speech_and_animation_player import say_with_animation

if not ROBOT_IP:
    print("IP du robot non définie")
    sys.exit(1)
#Connexion au Nao
session=qi.Session()

try :
    session.connect("tcp://{}:{}".format(ROBOT_IP, PORT))
    print("Connexion réussie")
except RuntimeError:
    print("Impossible de se connecter au robot"+ str(e))
    sys.exit(1)
    

apply_settings(session)

tts = session.service("ALTextToSpeech")
motion = session.service("ALMotion")
posture = session.service("ALRobotPosture")
animation_player = session.service("ALAnimationPlayer")

# Mettre le robot en posture initiale
posture.goToPosture("StandInit", 0.5) 

say_with_animation(tts, 
                   animation_player, 
                   """Bravo les enfants, vous avez été formidables ! Vous avez très bien travaillé aujourd'hui.""",
                    "animations/Stand/Gestures/Explain_2")

time.sleep(1)

say_with_animation(tts,
                   animation_player,
                   """Je suis très content de vous avoir rencontrés. Vous êtes tous formidables !""",
                   "animations/Stand/Emotions/Positive/Excited_2"
                   )

time.sleep(1)

tts.say("Au revoir les amis !")
animation_player.run("animations/Stand/Gestures/Hey_3")
