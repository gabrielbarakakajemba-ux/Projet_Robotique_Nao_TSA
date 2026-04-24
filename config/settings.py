# -*- coding: utf-8 -*-

def apply_settings(session):
    try:
        tts = session.service("ALTextToSpeech")

        # Réglage du volume à 50%
        tts.setVolume(0.70)
        print("[INFO] Volume réglé à 70%")

        # Réglage de la langue par défaut sur français
        tts.setLanguage("French")
        print("[INFO] Langue par défaut réglée sur Français")

    except Exception as e:
        print("[ERROR] Impossible d'appliquer les paramètres :", e)
