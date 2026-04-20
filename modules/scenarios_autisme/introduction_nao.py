# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import time
import qi
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
tts.setLanguage("French")

# Mettre le robot en posture initiale
posture.goToPosture("StandInit", 0.5) 

tts.say(""" Bonjour. Je m'appelle Nao. Je suis très content de te voir aujourd'hui. """)

time.sleep(2)

tts.say("Parfois, j'aime prendre un moment pour respirer doucement. Veux-tu respirer avec moi ?")

time.sleep(3)

# Exercice de mimetisme lent
say_with_animation(tts, animation_player, "Lève tes bras doucement, on inspire...", "animations/Stand/Gestures/Enthusiastic_4")
time.sleep(1.5)

say_with_animation(tts, animation_player, "Et on souffle tout doucement... On baisse les bras.", "animations/Stand/Gestures/CalmDown_1")
time.sleep(2)

tts.say("C'est très bien. Tu t'es super bien débrouillé.")





