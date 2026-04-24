# -*- coding: utf-8 -*-
import sys
import os

# Importation de tes chemins
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config.python_paths import NAOQI_LIB_PATH
sys.path.insert(0, NAOQI_LIB_PATH)

try:
    import qi
    from config.nao_config import ROBOT_IP, PORT
    
    session = qi.Session()
    session.connect("tcp://{}:{}".format(ROBOT_IP, PORT))
    tts = session.service("ALTextToSpeech")
    tts.say("Test de connexion reussi")
    print("[OK] Le robot a parle. Connexion etablie !")
except Exception as e:
    print("[ERREUR] Echec du test : {}".format(e))