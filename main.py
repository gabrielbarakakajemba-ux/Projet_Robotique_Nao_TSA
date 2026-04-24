# -*- coding: utf-8 -*-
import sys
import os
import time
import subprocess
import json

# ─────────────────────────────────────────────
#  Racine du projet
# ─────────────────────────────────────────────
ROOT_DIR = "/home/mr-kajemba/Nao_Autisme"
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# ─────────────────────────────────────────────
#  Chargement configuration
# ─────────────────────────────────────────────
try:
    from config.python_paths import NAOQI_LIB_PATH, PYTHON2_PATH
    if NAOQI_LIB_PATH not in sys.path:
        sys.path.insert(0, NAOQI_LIB_PATH)
    print("[INFO] Configuration chargee avec succes.")
except ImportError as e:
    print("[ERROR] Impossible de charger config.python_paths : " + str(e))
    sys.exit(1)

# ─────────────────────────────────────────────
#  Imports Python 3 (vision + base de données)
# ─────────────────────────────────────────────
try:
    import cv2
    import numpy as np
    import pygame
    from modules.perception.vision.face_recognition.detection.yolo_detection import YOLODetector
    from modules.perception.vision.face_recognition.recognition.facenet_recognizer import FacenetRecognizer
    from database.faces_repository import FacesRepository
    print("[INFO] Modules Python 3 charges avec succes.")
except ImportError as e:
    print("[ERROR] Module Python 3 manquant : " + str(e))
    sys.exit(1)

# ─────────────────────────────────────────────
#  Chemins des scripts Python 2.7
# ─────────────────────────────────────────────
SCRIPT_INTRODUCTION = os.path.join(ROOT_DIR, "modules", "behaviors", "autism_scenarios", "introduction_nao.py")
SCRIPT_CONCLUSION   = os.path.join(ROOT_DIR, "modules", "behaviors", "autism_scenarios", "conclusion_nao.py")
SCRIPT_GAME         = os.path.join(ROOT_DIR, "modules", "behaviors", "games", "nao_game.py")
SCRIPT_LOAD_DATA    = os.path.join(ROOT_DIR, "modules", "behaviors", "games", "load_data.py")
SCRIPT_VIDEO_STREAM = os.path.join(ROOT_DIR, "modules", "perception", "vision", "nao_video_stream_publisher_vision.py")

# ─────────────────────────────────────────────
#  Constantes manette PS4
# ─────────────────────────────────────────────
BTN_TRIANGLE = 12   # Jeu d'imitation
BTN_ROND     = 13   # Jeu des émotions
BTN_CROIX    = 14   # Jeu questions-réponses
BTN_CARRE    = 15   # (réservé)
BTN_START    = 3    # Confirmer / passer

# ─────────────────────────────────────────────
#  Helpers subprocess
# ─────────────────────────────────────────────
def run_py2(script_path, wait=True):
    """Lance un script Python 2.7 (interaction robot)."""
    print("[INFO] Lancement : " + os.path.basename(script_path))
    if wait:
        result = subprocess.run(
            [PYTHON2_PATH, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("[WARN] " + result.stderr)
        return result.returncode
    else:
        return subprocess.Popen([PYTHON2_PATH, script_path])

def run_py2_with_arg(script_path, arg_json):
    """
    Lance un script Python 2.7 en passant un argument JSON.
    Le script peut lire sys.argv[1] pour récupérer les données.
    """
    print("[INFO] Lancement : " + os.path.basename(script_path))
    result = subprocess.run(
        [PYTHON2_PATH, script_path, arg_json],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("[WARN] " + result.stderr)
    return result.returncode

# ─────────────────────────────────────────────
#  Initialisation manette PS4
# ─────────────────────────────────────────────
def init_manette():
    """Initialise pygame et la manette PS4."""
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("[WARN] Aucune manette détectée — mode clavier activé.")
        return None

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print("[INFO] Manette détectée : " + joystick.get_name())
    return joystick

def attendre_bouton_jeu(joystick):
    """
    Attend que l'enfant choisisse un jeu via la manette.
    Triangle  (12) → Jeu d'imitation
    Rond      (13) → Jeu des émotions
    Croix     (14) → Jeu questions-réponses
    Retourne le nom du jeu choisi.
    """
    print("\n[MANETTE] En attente du choix de jeu...")
    print("  Triangle (12) → Jeu d'imitation")
    print("  Rond     (13) → Jeu des émotions")
    print("  Croix    (14) → Jeu questions-réponses")

    if joystick is None:
        # Mode fallback clavier si pas de manette
        choix = input("Choix (1=imitation / 2=emotions / 3=questions) : ").strip()
        mapping = {"1": "imitation", "2": "emotions", "3": "questions"}
        return mapping.get(choix, "imitation")

    while True:
        pygame.event.pump()
        if joystick.get_button(BTN_TRIANGLE):
            print("[MANETTE] Triangle → Jeu d'imitation")
            return "imitation"
        if joystick.get_button(BTN_ROND):
            print("[MANETTE] Rond → Jeu des émotions")
            return "emotions"
        if joystick.get_button(BTN_CROIX):
            print("[MANETTE] Croix → Jeu questions-réponses")
            return "questions"
        pygame.time.wait(100)

# ─────────────────────────────────────────────
#  Reconnaissance et enregistrement du visage
# ─────────────────────────────────────────────
def identifier_enfant(detector, recognizer, db):
    """
    Capture une image depuis la webcam locale,
    détecte et reconnaît le visage de l'enfant.
    Retourne (prenom, age, est_nouveau).
    """
    print("[INFO] Ouverture de la caméra pour identification...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[WARN] Caméra non disponible — identification manuelle.")
        prenom = input("Prénom de l'enfant : ").strip()
        age    = input("Age de l'enfant   : ").strip()
        return prenom, age, True

    prenom    = None
    age       = None
    est_nouveau = True
    frame_ok  = None

    print("[INFO] Tentative de reconnaissance faciale (5 secondes)...")
    debut = time.time()

    while time.time() - debut < 5:
        ret, frame = cap.read()
        if not ret:
            break

        faces = detector.detect_faces(frame)
        if faces:
            frame_ok = frame.copy()
            # Découpe du visage détecté (premier visage)
            x1, y1, x2, y2 = faces[0]
            face_crop = frame[y1:y2, x1:x2]

            # Reconnaissance via FaceNet
            persons = db.get_all_persons()
            if persons:
                result = recognizer.recognize(face_crop, persons)
                if result is not None:
                    prenom, _ = result
                    est_nouveau = False
                    print("[INFO] Enfant reconnu : " + prenom)
                    break

        time.sleep(0.2)

    cap.release()

    if est_nouveau:
        print("[INFO] Visage non reconnu — enregistrement d'un nouvel enfant.")
        prenom = input("Prénom de l'enfant : ").strip()
        age    = input("Age de l'enfant   : ").strip()

        if frame_ok is not None:
            # Calcul de l'embedding FaceNet et enregistrement en base
            faces = detector.detect_faces(frame_ok)
            if faces:
                x1, y1, x2, y2 = faces[0]
                face_crop = frame_ok[y1:y2, x1:x2]
                embedding = recognizer.get_embedding(face_crop)
                if embedding is not None:
                    db.insert_person(prenom, embedding)
                    print("[INFO] Visage enregistré pour " + prenom)
        else:
            print("[WARN] Pas d'image capturée — visage non enregistré.")

    return prenom, age, est_nouveau

# ─────────────────────────────────────────────
#  Enregistrement du choix de jeu
# ─────────────────────────────────────────────
def enregistrer_choix(prenom, jeu_choisi):
    """
    Sauvegarde le choix de jeu dans un fichier JSON local
    (la base de données ne stocke pas encore les sessions).
    """
    log_path = os.path.join(ROOT_DIR, "temp", "sessions.json")
    sessions = []

    if os.path.exists(log_path):
        try:
            with open(log_path, "r") as f:
                sessions = json.load(f)
        except Exception:
            sessions = []

    sessions.append({
        "prenom"    : prenom,
        "jeu"       : jeu_choisi,
        "timestamp" : time.strftime("%Y-%m-%d %H:%M:%S")
    })

    with open(log_path, "w") as f:
        json.dump(sessions, f, indent=2)

    print("[INFO] Choix enregistré : {} → {}".format(prenom, jeu_choisi))

# ─────────────────────────────────────────────
#  PROGRAMME PRINCIPAL
# ─────────────────────────────────────────────
def main():
    print("\n" + "=" * 50)
    print("   NAO — Accompagnement Enfants TSA")
    print("=" * 50)

    # ── Initialisation des modules Python 3 ──
    detector   = YOLODetector(
        os.path.join(ROOT_DIR, "models", "yolov8-face.pt")
    )
    recognizer = FacenetRecognizer()
    db         = FacesRepository()
    joystick   = init_manette()

    try:
        # ─────────────────────────────────────
        #  ÉTAPE 1 — Présentation du robot
        #  + Introduction en parallèle
        #  + Identification / Enregistrement
        # ─────────────────────────────────────
        print("\n[ETAPE 1] Présentation et identification...")

        # On lance le flux vidéo NAO en arrière-plan (Python 2.7)
        proc_video = run_py2(SCRIPT_VIDEO_STREAM, wait=False)

        # Identification de l'enfant (Python 3 — caméra locale)
        prenom, age, est_nouveau = identifier_enfant(detector, recognizer, db)

        # Arrêt du flux vidéo une fois l'identification terminée
        try:
            proc_video.terminate()
            proc_video.wait()
        except Exception:
            pass

        # ─────────────────────────────────────
        #  ÉTAPE 2 — Introduction NAO
        #  (Python 2.7 — parle et bouge)
        # ─────────────────────────────────────
        print("\n[ETAPE 2] Introduction pour {}...".format(prenom))
        run_py2(SCRIPT_INTRODUCTION)

        # ─────────────────────────────────────
        #  ÉTAPE 3 — Choix du jeu via manette
        # ─────────────────────────────────────
        print("\n[ETAPE 3] Choix du jeu...")
        jeu_choisi = attendre_bouton_jeu(joystick)
        enregistrer_choix(prenom, jeu_choisi)

        # ─────────────────────────────────────
        #  ÉTAPE 4 — Chargement des questions
        #            si jeu Q/R
        # ─────────────────────────────────────
        if jeu_choisi == "questions":
            print("[INFO] Chargement des questions depuis la base...")
            ret = subprocess.run(
                [sys.executable, SCRIPT_LOAD_DATA],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if ret.returncode != 0:
                print("[WARN] load_data.py a échoué — le jeu Q/R peut ne pas fonctionner.")

        # ─────────────────────────────────────
        #  ÉTAPE 5 — Lancement du jeu
        #  (Python 2.7 — NAO joue avec l'enfant)
        # ─────────────────────────────────────
        print("\n[ETAPE 5] Lancement du jeu : {}".format(jeu_choisi))
        run_py2_with_arg(SCRIPT_GAME, jeu_choisi)

        # ─────────────────────────────────────
        #  ÉTAPE 6 — Conclusion
        # ─────────────────────────────────────
        print("\n[ETAPE 6] Conclusion de la session...")
        run_py2(SCRIPT_CONCLUSION)

        print("\n[FIN] Session terminée pour {}.".format(prenom))

    except KeyboardInterrupt:
        print("\n[STOP] Arrêt d'urgence détecté.")

    finally:
        if joystick is not None:
            pygame.quit()
        print("[INFO] Fermeture propre du programme.")

if __name__ == "__main__":
    main()