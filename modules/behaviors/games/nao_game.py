# -*- coding: utf-8 -*-
import sys
import os
import time
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config.nao_config import ROBOT_IP, PORT
from modules.perception.audio_understanding.speech_to_text.nao_speech_recognition import record_audio, transfer_audio_file, speech_to_text

try:
    import qi
except ImportError:
    print("ERREUR : Le module 'qi' est introuvable. Verifiez NAOQI_LIB_PATH.")
    sys.exit(1)

# Connexion aux services
session = qi.Session()
try:
    session.connect("tcp://{}:{}".format(ROBOT_IP, PORT))
    tts = session.service("ALTextToSpeech")
    motion = session.service("ALMotion")
    leds = session.service("ALLeds")
except:
    sys.exit(1)

# --- LES MODULES DE JEU ---

def jeu_imitation():
    tts.say("C'est l'heure de bouger. Regarde bien mon bras !")
    motion.angleInterpolation("RShoulderPitch", -0.5, 1.0, True)
    time.sleep(3)
    motion.angleInterpolation("RShoulderPitch", 1.5, 1.0, True)
    tts.say("Bravo, tu as bien imité mon geste !")

def jeu_emotions():
    tts.say("Devine ce que je ressens !")
    leds.fadeRGB("FaceLeds", "blue", 0.1) # Triste
    motion.setAngles("HeadPitch", 0.3, 0.1)
    
    record_audio()
    transfer_audio_file()
    reponse = speech_to_text()
    
    if reponse and "triste" in reponse.lower():
        tts.say("Exactement !")
    else:
        tts.say("Je faisais la grimace de la tristesse.")
    
    leds.fadeRGB("FaceLeds", "white", 0.1)
    motion.setAngles("HeadPitch", 0.0, 0.1)

def jeu_questions():
    # Charge les questions depuis le JSON généré par load_data.py
    with open(os.path.join(BASE_DIR, "modules/behaviors/games/questions.json"), "r") as f:
        questions = json.load(f)
    
    for q in questions:
        tts.say(q[1]) # q[1] est la question dans ton tuple SQL
        record_audio()
        transfer_audio_file()
        user_say = speech_to_text()
        
        if user_say and q[2].lower() in user_say.lower():
            tts.say("Super !")
        else:
            tts.say("C'était " + str(q[2]))