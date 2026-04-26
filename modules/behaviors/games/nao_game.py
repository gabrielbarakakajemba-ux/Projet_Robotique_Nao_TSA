# -*- coding: utf-8 -*-

import sys
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config.nao_config import ROBOT_IP, PORT
from database.question_repository import QuestionRepository
from database.defis_repository import DefisRepository
from modules.perception.audio_understanding.speech_to_text.nao_speech_recognition import (
    record_audio, transfer_audio_file, speech_to_text
)

try:
    import qi
except ImportError:
    print("ERREUR : Le module 'qi' est introuvable. Verifiez NAOQI_LIB_PATH.")
    sys.exit(1)


def connect():
    session = qi.Session()
    try:
        session.connect("tcp://{}:{}".format(ROBOT_IP, PORT))
    except RuntimeError as e:
        print("Impossible de se connecter au robot : " + str(e))
        sys.exit(1)
    tts              = session.service("ALTextToSpeech")
    motion           = session.service("ALMotion")
    leds             = session.service("ALLeds")
    posture          = session.service("ALRobotPosture")
    animation_player = session.service("ALAnimationPlayer")
    tts.setLanguage("French")
    return tts, motion, leds, posture, animation_player


def ecouter_enfant():
    """Enregistre la voix de l'enfant et renvoie un texte minuscules ou ''."""
    try:
        record_audio()
        transfer_audio_file()
        text = speech_to_text()
        if text:
            return text.strip().lower()
    except Exception as e:
        print("Erreur ecoute : " + str(e))

    try:
        saisie = raw_input("Reponse de l'enfant (clavier) -> ").strip().lower()
        return saisie
    except Exception:
        return ""


def reponse_correcte(reponse_enfant, defi):
    if not reponse_enfant:
        return False
    cible = defi['reponse'].lower()
    if cible in reponse_enfant:
        return True
    for syn in defi['synonymes']:
        if syn and syn.lower() in reponse_enfant:
            return True
    return False


def jouer_defi(tts, animation_player, defi, nom):
    """Joue un defi (emotion ou imitation). Renvoie True si l'enfant trouve."""
    tts.say(defi['consigne'])
    time.sleep(0.5)

    try:
        animation_player.run(defi['animation'])
    except Exception as e:
        print("Erreur animation : " + str(e))

    time.sleep(0.5)
    tts.say(u"A toi {} ! Dis ta reponse.".format(nom))

    reponse = ecouter_enfant()
    if reponse_correcte(reponse, defi):
        tts.say(u"Bravo {} ! C'est bien ca.".format(nom))
        return True

    if defi.get('indice'):
        tts.say(u"Pas tout a fait. Je te donne un indice : " + defi['indice'])
        time.sleep(0.5)
        tts.say(u"Essaie encore.")
        reponse = ecouter_enfant()
        if reponse_correcte(reponse, defi):
            tts.say(u"Tres bien {} ! Tu as trouve.".format(nom))
            return True

    tts.say(u"La bonne reponse etait : " + defi['reponse'])
    tts.say(u"Ce n'est pas grave {}, on continue ensemble.".format(nom))
    return False


# =========================================================
#  JEU EMOTIONS
# =========================================================
def jeu_emotions(tts, animation_player, nom):
    tts.say(u"On va jouer aux emotions {}. Je vais te montrer une emotion, "
            u"et tu vas deviner laquelle.".format(nom))
    time.sleep(1)

    defis = DefisRepository.get_by_type('emotion', limit=4)
    if not defis:
        tts.say(u"Desole, je n'ai pas trouve les emotions dans ma memoire.")
        return 0, 0

    bonnes = 0
    for i, defi in enumerate(defis, 1):
        tts.say(u"Emotion numero {}.".format(i))
        if jouer_defi(tts, animation_player, defi, nom):
            bonnes += 1
        time.sleep(1)

    tts.say(u"Tu as trouve {} emotions sur {} {} ! Bravo !".format(
        bonnes, len(defis), nom))
    return bonnes, len(defis)


# =========================================================
#  JEU IMITATION
# =========================================================
def jeu_imitation(tts, animation_player, nom):
    tts.say(u"On va jouer a l'imitation {}. Je vais faire quelque chose, "
            u"et tu devras deviner ce que c'est.".format(nom))
    time.sleep(1)

    defis = DefisRepository.get_by_type('imitation', limit=4)
    if not defis:
        tts.say(u"Desole, je n'ai pas trouve les imitations dans ma memoire.")
        return 0, 0

    bonnes = 0
    for i, defi in enumerate(defis, 1):
        tts.say(u"Imitation numero {}.".format(i))
        if jouer_defi(tts, animation_player, defi, nom):
            bonnes += 1
        time.sleep(1)

    tts.say(u"Tu as trouve {} imitations sur {} {} !".format(
        bonnes, len(defis), nom))
    return bonnes, len(defis)


# =========================================================
#  JEU QUESTIONS / REPONSES
# =========================================================
def jeu_questions(tts, nom):
    tts.say(u"On va jouer aux questions {} ! Je te pose des questions, "
            u"tu reponds avec ta voix.".format(nom))
    time.sleep(1)

    questions = QuestionRepository.get_all_questions()
    if not questions:
        tts.say(u"Desole {}, je n'ai pas de questions pour le moment.".format(nom))
        return 0, 0

    import random
    random.shuffle(questions)
    questions = questions[:5]

    bonnes = 0
    for i, q in enumerate(questions, 1):
        question_text = q[1]
        bonne_reponse = q[2]

        tts.say(u"Question numero {}.".format(i))
        time.sleep(0.3)
        tts.say(question_text)

        reponse = ecouter_enfant()
        if reponse and bonne_reponse.lower() in reponse:
            tts.say(u"Super {} ! Bonne reponse !".format(nom))
            bonnes += 1
        else:
            tts.say(u"La bonne reponse etait : " + str(bonne_reponse))
            tts.say(u"Ce n'est pas grave, on continue.")
        time.sleep(1)

    tts.say(u"Tu as eu {} bonnes reponses sur {} {} !".format(
        bonnes, len(questions), nom))
    return bonnes, len(questions)


# =========================================================
#  ENTREE
# =========================================================
if __name__ == "__main__":
    selected_game = sys.argv[1] if len(sys.argv) > 1 else "jeu_questions"
    nom           = sys.argv[2] if len(sys.argv) > 2 else "petit ami"

    print(u"[INFO] Jeu : {} | Enfant : {}".format(selected_game, nom))

    tts, motion, leds, posture, animation_player = connect()

    try:
        posture.goToPosture("StandInit", 0.5)
    except Exception:
        pass

    score, total = 0, 0

    if selected_game == "jeu_imitation":
        score, total = jeu_imitation(tts, animation_player, nom)
    elif selected_game == "jeu_emotions":
        score, total = jeu_emotions(tts, animation_player, nom)
    elif selected_game == "jeu_questions":
        score, total = jeu_questions(tts, nom)
    else:
        print(u"Jeu inconnu : " + selected_game)
        tts.say(u"Je ne connais pas ce jeu.")
        sys.exit(1)

    try:
        DefisRepository.log_session(None, selected_game, score,
                                    "Score {}/{} pour {}".format(score, total, nom))
    except Exception as e:
        print("Erreur log session : " + str(e))

    tts.say(u"Merci d'avoir joue avec moi {} !".format(nom))
