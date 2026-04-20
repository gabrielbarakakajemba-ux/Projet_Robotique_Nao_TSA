# -*- coding: utf-8 -*-
import requests
import keyboard
from naoqi import ALProxy
import sys
import os
import qi

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from utils.speech_and_animation_player import say_with_animation
from modules.intelligent_vision_robot.voice_transcription.nao_speech_recognition import (
    record_audio,
    stop_recording,
    transfer_audio_file,
    speech_to_text
)

from config.nao_config import ROBOT_IP, PORT
from config.pc_config import PC_IP

LLM_SERVER  = "http://{}:5000/chat".format(PC_IP)
FACE_SERVER = "http://{}:5001/last_face".format(PC_IP)

session = qi.Session()
session.connect("tcp://{}:{}".format(ROBOT_IP, PORT))

tts = session.service("ALTextToSpeech")
animation_player = session.service("ALAnimationPlayer")

def get_face_name():
    try:
        response = requests.get(FACE_SERVER, timeout=2.0)
        name = response.json().get("name")
        if name:
            print("[CLIENT] Visage reconnu : {}".format(name.encode("utf-8")))
        else:
            print("[CLIENT] Aucun visage recent detecte")
        return name
    except Exception as e:
        print("[CLIENT] Erreur get_face_name : {}".format(str(e)))
        return None


def wait_for_face(timeout=10.0):
    """
    Attend qu'un visage soit reconnu avant de continuer.
    Donne un retour vocal à l'utilisateur pendant l'attente.
    Retourne le prénom ou None si timeout.
    """
    print("[CLIENT] Attente reconnaissance faciale (max {}s)...".format(timeout))
    tts.say("Un instant...".encode("utf-8"))

    deadline = __import__("time").time() + timeout
    while __import__("time").time() < deadline:
        name = get_face_name()
        if name:
            return name
        __import__("time").sleep(0.5)

    print("[CLIENT] Timeout reconnaissance, on continue sans prénom")
    return None


def ask_llm(text, prenom=None):
    if prenom:
        enriched = u"[L'utilisateur s'appelle {}] {}".format(prenom, text)
        print("[CLIENT] Message enrichi : {}".format(enriched.encode("utf-8")))
    else:
        enriched = text

    print("[CLIENT] Envoi au serveur LLM : {}".format(text.encode("utf-8")))

    try:
        response = requests.post(
            LLM_SERVER,
            json={"message": enriched},
            timeout=30
        )
        print("[CLIENT] Status code recu : {}".format(response.status_code))

        data = response.json()
        answer = data.get("response", u"")
        print("[CLIENT] Reponse LLM : {}".format(answer.encode("utf-8")))
        return answer

    except requests.exceptions.Timeout:
        print("[CLIENT][ERREUR] Timeout LLM")
        return None
    except requests.exceptions.ConnectionError:
        print("[CLIENT][ERREUR] Serveur LLM inaccessible")
        return None
    except Exception as e:
        print("[CLIENT][ERREUR] {}".format(str(e)))
        return None


def process_audio(prenom=None):
    print("[CLIENT] Transfert du fichier audio...")
    transfer_audio_file()
    print("[CLIENT] Transfert termine")

    print("[CLIENT] Transcription en cours...")
    user_text = speech_to_text()

    if not user_text:
        print("[CLIENT] Transcription vide")
        tts.say("Je n'ai pas compris.")
        return

    print("[CLIENT] Transcription : {}".format(user_text.encode("utf-8")))

    answer = ask_llm(user_text, prenom=prenom)

    if not answer:
        print("[CLIENT] Pas de reponse du LLM")
        tts.say("Je n'ai pas de reponse pour le moment.")
        return

    print("[CLIENT] NAO va dire : {}".format(answer.encode("utf-8")))
    say_with_animation(tts,
                   animation_player,
                   answer.encode("utf-8"),
                   "animations/Stand/Gestures/Explain_10"
                   )
    print("[CLIENT] NAO a fini de parler\n")


def main():
    print("=" * 50)
    print("  NAO Chatbot - Pret !")
    print("  ESPACE  -> Commencer a parler")
    print("  ENTREE  -> Arreter l'enregistrement")
    print("  ECHAP   -> Quitter")
    print("=" * 50)

    prenom=None

    while True:
        print("\n[CLIENT] En attente... (ESPACE pour parler, ECHAP pour quitter)")

        event = keyboard.read_event(suppress=True)
        while event.event_type != "down" or event.name not in ("space", "esc"):
            event = keyboard.read_event(suppress=True)

        if event.name == "esc":
            print("[CLIENT] Arret du programme.")
            break

        print("[CLIENT] Enregistrement en cours... (ENTREE pour arreter)")
        record_audio(start_manual=True)

        keyboard.wait("enter")
        print("[CLIENT] Fin de l'enregistrement")
        stop_recording()

        # Rafraîchit le prénom si une nouvelle reconnaissance a eu lieu
        new_name = get_face_name()
        if new_name:
            prenom = new_name

        process_audio(prenom=prenom)


if __name__ == "__main__":
    main()