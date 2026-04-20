# -*- coding: utf-8 -*-
import qi
import sys
import os
import time
import json
import unicodedata

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from config.nao_config import ROBOT_IP, PORT
from config.settings import apply_settings
from utils.nao_camera import scan_qr_code

session = qi.Session()
try:
    session.connect("tcp://{}:{}".format(ROBOT_IP, PORT))
    print("Connexion réussie")
except RuntimeError:
    print("Impossible de se connecter au robot")
    sys.exit(1)

apply_settings(session)

tts = session.service("ALTextToSpeech")
video_service = session.service("ALVideoDevice")

questions_list = []
with open("modules/nao_game/questions.json", "r") as f:
    raw = json.load(f)
    for item in raw:
        questions_list.append({
            "id": item[0],
            "question": item[1],
            "answer": item[2]
        })

def rules_presentation():
    tts.say("C'est partie pour le jeu du Qui suis je version animal marin !")
    time.sleep(0.5)
    tts.say("Mais avant de commencer, je vais t'expliquer les règles du jeu. J'espère que t'es prêt.")
    time.sleep(0.5)
    tts.say("""Voici les règles du jeu, je vais décrire plusieurs animaux marins et tu devras deviner lequel c'est.
    Devant toi tu auras plusieurs cartes avec des images d'animaux marins.
    Si tu penses que la réponse est parmi une de ces cartes, prends la et montre moi le QR code derrière, 
    je te dirais après si c'est la bonne réponse ou pas.
    Tu auras trois chances pour répondre correctement. 
    Si ta réponse est vraie tu auras un point, par contre, si tu réponds faux, tu ne gagnes aucun point.
    """)
    time.sleep(2)
    tts.say("Allez on commence !")
    time.sleep(0.5)

def normalize_text(text):
    """Transforme les accents en caractères ASCII simples et met en minuscules"""
    if text is None:
        return ""
    if isinstance(text, str):
        text = text.decode('utf-8')  # Python 2.7 : s'assurer que c'est unicode
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore')  # supprime les accents
    return text.lower().strip()

def answer_verification(question, answer):
    """
    Scanne le QR code et compare à la réponse
    Retourne True si correct, False sinon
    """
    qr_text = scan_qr_code(video_service)
    if qr_text is None:
        tts.say("Je n'ai rien lu, réessaie.")
        return False

    print("QR scanné :", qr_text)
    print("Réponse attendue :", answer)
    print("QR normalisé :", normalize_text(qr_text))
    print("Réponse normalisée :", normalize_text(answer))

    if normalize_text(qr_text) == "repeter":
        tts.say("Okay laisse moi répéter ma question.")
        tts.say(question)
        return None
    elif normalize_text(qr_text) == normalize_text(answer):
        tts.say("C'est la bonne réponse, Tu gagnes 1 points.")
        return True
    else:
        tts.say("C'est la mauvaise réponse")
        return False


# ------------------------- PROGRAMME PRINCIPAL --------------------------------

points = 0

rules_presentation()

for q in questions_list:
    tts.say(q['question'])
    essais = 0
    correct = False

    while essais < 3 and not correct:
        result = answer_verification(q['question'], q['answer'])

        if result is None:
            continue  

        if result is True:
            correct = True
            break  

        essais += 1
        if essais == 3:
            tts.say("Oups, c'est dommage, c'était {} la réponse".format(q['answer']))
        else:
            tts.say("Il te reste {} tentatives".format(3 - essais))

    if correct:
        points += 1

tts.say("Tu as obtenu {} points !".format(points))

