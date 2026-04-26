# -*- coding: utf-8 -*-

def apply_settings(session):
    try:
        tts = session.service("ALTextToSpeech")

        tts.setVolume(0.70)
        print("[INFO] Volume regle a 70%")

        tts.setLanguage("French")
        print("[INFO] Langue par defaut reglee sur Francais")

    except Exception as e:
        print("[ERROR] Impossible d'appliquer les parametres :", e)
