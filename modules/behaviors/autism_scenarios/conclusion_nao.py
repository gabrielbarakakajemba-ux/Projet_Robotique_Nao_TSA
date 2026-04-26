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


def conclusion_nao(nom):
    try:
        posture.goToPosture("StandInit", 0.5)

        say_with_animation(
            tts, animation_player,
            u"Bravo {} ! Tu as ete formidable ! "
            u"Tu as tres bien travaille aujourd'hui.".format(nom),
            "animations/Stand/Gestures/Explain_2"
        )
        time.sleep(1)

        say_with_animation(
            tts, animation_player,
            u"Je suis tres content de t'avoir rencontre {}. "
            u"Tu es vraiment formidable !".format(nom),
            "animations/Stand/Emotions/Positive/Excited_2"
        )
        time.sleep(1)

        tts.say(u"Au revoir {} ! A tres bientot !".format(nom))
        animation_player.run("animations/Stand/Gestures/Hey_3")

    except Exception as e:
        print("Erreur conclusion : " + str(e))


if __name__ == "__main__":
    nom = sys.argv[1] if len(sys.argv) > 1 else "petit ami"
    conclusion_nao(nom)
