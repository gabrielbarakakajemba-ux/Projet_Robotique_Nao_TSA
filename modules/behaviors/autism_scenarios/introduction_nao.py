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
    print("Impossible de se connecter au robot")
    sys.exit(1)

apply_settings(session)

tts = session.service("ALTextToSpeech")
motion = session.service("ALMotion")
posture = session.service("ALRobotPosture")
animation_player = session.service("ALAnimationPlayer")
tts.setLanguage("French")


def introduction_nao(robot_ip, nom):
    try:
        posture.goToPosture("StandInit", 0.5) 

        tts.say(""" Bonjour. Je m'appelle Nao. Je suis très content de vous voir aujourd'hui. """)

        time.sleep(2.5)

        tts.say("Parfois, j'aime prendre un moment pour respirer doucement. Qui veux respirer avec moi ?")

        time.sleep(3)

        # Exercice de mimetisme lent
        say_with_animation(tts, animation_player, "D'accord; Lève tes bras doucement, on inspire...", "animations/Stand/Gestures/Enthusiastic_4")
        time.sleep(1.5)

        say_with_animation(tts, animation_player, "Et on souffle tout doucement... On baisse les bras.", "animations/Stand/Gestures/CalmDown_1")
        time.sleep(2)

        tts.say("C'est très bien. Tu t'es super bien débrouillé.")
    except Exception as e:
        print("Erreur introduction : " + str(e))

