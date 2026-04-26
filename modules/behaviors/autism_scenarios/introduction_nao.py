# -*- coding: utf-8 -*-

import sys
import os
import time

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
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

from config.nao_config import ROBOT_IP, PORT
from config.settings import apply_settings
from utils.speech_and_animation_player import say_with_animation

if not ROBOT_IP:
    print("IP du robot non definie")
    sys.exit(1)

session = qi.Session()
try:
    session.connect("tcp://{}:{}".format(ROBOT_IP, PORT))
    print("Connexion reussie")
except RuntimeError as e:
    print("Impossible de se connecter au robot : " + str(e))
    sys.exit(1)

apply_settings(session)

tts              = session.service("ALTextToSpeech")
motion           = session.service("ALMotion")
posture          = session.service("ALRobotPosture")
animation_player = session.service("ALAnimationPlayer")
tts.setLanguage("French")


def introduction_nao(nom):
    try:
        posture.goToPosture("StandInit", 0.5)

        tts.say(u"Bonjour {}. Je m'appelle Nao. "
                u"Je suis tres content de te voir aujourd'hui !".format(nom))

        time.sleep(2.5)

        tts.say(u"Parfois, j'aime prendre un moment pour respirer doucement. "
                u"Tu veux respirer avec moi ?")

        time.sleep(3)

        say_with_animation(tts, animation_player,
                           u"D'accord ! Leve tes bras doucement, on inspire...",
                           "animations/Stand/Gestures/Enthusiastic_4")
        time.sleep(1.5)

        say_with_animation(tts, animation_player,
                           u"Et on souffle tout doucement... On baisse les bras.",
                           "animations/Stand/Gestures/CalmDown_1")
        time.sleep(2)

        tts.say(u"C'est tres bien {}. Tu t'es super bien debrouille !".format(nom))

    except Exception as e:
        print("Erreur introduction : " + str(e))


if __name__ == "__main__":
    nom = sys.argv[1] if len(sys.argv) > 1 else "petit ami"
    introduction_nao(nom)
