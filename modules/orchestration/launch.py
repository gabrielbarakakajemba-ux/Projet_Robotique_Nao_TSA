# -*- coding: utf-8 -*-
import subprocess
import os
import sys
import time
import requests

PROJECT_ROOT = "/home/mr-kajemba/Nao_Autisme"

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


try:
    from config.python_paths import NAOQI_LIB_PATH, PYTHON2_PATH
    if NAOQI_LIB_PATH not in sys.path:
        sys.path.insert(0, NAOQI_LIB_PATH)
    print("Configuration chargée avec succès !")
except ImportError as e:
    print("Impossible de charger config.python_paths : " + str(e))
    sys.exit(1)



def launch_scenario():
    """
    Menu pour choisir le scénario Autisme à exécuter :
    - introduction_nao.py
    - conclusion_nao.py
    """
    base_path = os.path.join(PROJECT_ROOT, "modules", "behaviors", "autism_scenarios")

    while True:
        print("\n=== Scénarios Autisme ===")
        print("1 - Introduction")
        print("2 - Conclusion")
        print("0 - Retour au menu principal")

        choix = input("Votre choix : ").strip()

        if choix == "1":
            script = os.path.join(base_path, "introduction_nao.py")
        elif choix == "2":
            script = os.path.join(base_path, "conclusion_nao.py")
        elif choix == "0":
            break
        else:
            print("Choix invalide, réessayez.")
            continue

        print("[INFO] Lancement du script : " + os.path.basename(script))

        try:
            result = subprocess.run(
                [PYTHON2_PATH, script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("=== Sortie du script ===")
            print(result.stdout)
            if result.stderr:
                print("=== Erreurs éventuelles ===")
                print(result.stderr)
        except Exception as e:
            print("[ERROR] Impossible d'exécuter le script : " + str(e))



def launch_nao_game():
    """
    Menu pour le jeu NAO :
    - Charger les questions (load_data.py  – Python 3)
    - Lancer le jeu       (nao_game.py    – Python 2.7)
    """
    base_path = os.path.join(PROJECT_ROOT, "modules", "behaviors", "games")
    script_load = os.path.join(base_path, "load_data.py")
    script_game = os.path.join(base_path, "nao_game.py")

    while True:
        print("\n=== Nao Game ===")
        print("1 - Charger de nouvelles questions et lancer le jeu")
        print("0 - Retour au menu principal")

        choix = input("Votre choix : ").strip()

        if choix == "1":
            # Étape 1 : chargement des données (Python 3)
            print("[INFO] Lancement de load_data.py...")
            try:
                result = subprocess.run(
                    [PYTHON3_PATH, script_load],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                print(result.stdout)
                if result.stderr:
                    print("=== Erreurs éventuelles ===")
                    print(result.stderr)

                if result.returncode != 0:
                    print("[ERROR] load_data.py a échoué, le jeu ne sera pas lancé.")
                    continue

            except Exception as e:
                print("[ERROR] Impossible d'exécuter load_data.py : " + str(e))
                continue

            # Étape 2 : lancement du jeu (Python 2.7)
            print("[INFO] Lancement de nao_game.py...")
            try:
                result = subprocess.run(
                    [PYTHON2_PATH, script_game],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                print(result.stdout)
                if result.stderr:
                    print("=== Erreurs éventuelles ===")
                    print(result.stderr)
            except Exception as e:
                print("[ERROR] Impossible d'exécuter nao_game.py : " + str(e))

        elif choix == "0":
            break
        else:
            print("Choix invalide, réessayez.")



def launch_motion_control():
    """
    Menu pour le contrôle manuel du robot :
    - Contrôle scénario via manette PS3
    - Jeu ramassage de bouteilles (vision + motion)
    """
    while True:
        print("\n=== Robot Motion Control ===")
        print("1 - Contrôle scénario (manette PS3)")
        print("2 - Jeu ramassage de bouteilles")
        print("0 - Retour au menu principal")

        choix = input("Votre choix : ").strip()

        script = None

        if choix == "1":
            script = os.path.join(
                PROJECT_ROOT, "modules", "action", "motion", "robot_motion_controller.py"
            )

        elif choix == "2":
            # Script Python 3 : détection d'objets
            script_py3 = os.path.join(
                PROJECT_ROOT, "modules", "perception", "vision",
                "object_detection", "nao_object_detection.py"
            )
            # Script Python 2.7 : flux vidéo + motion
            script_py2 = os.path.join(
                PROJECT_ROOT, "modules", "perception", "vision",
                "nao_video_stream_publisher_motion.py"
            )

            print("[INFO] Lancement de la détection d'objets (Python 3)...")
            py3_proc = subprocess.Popen([PYTHON3_PATH, script_py3])

            print("[INFO] Lancement du flux vidéo NAO (Python 2.7)...")
            try:
                result = subprocess.run(
                    [PYTHON2_PATH, script_py2],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                print("=== Sortie Python 2.7 ===")
                print(result.stdout)
                if result.stderr:
                    print("=== Erreurs éventuelles ===")
                    print(result.stderr)
            except Exception as e:
                print("[ERROR] Impossible d'exécuter le script Python 2.7 : " + str(e))

            # Arrêt du script Python 3 quand Python 2.7 se termine
            try:
                py3_proc.terminate()
                py3_proc.wait()
                print("[INFO] Détection d'objets arrêtée.")
            except Exception:
                pass
            continue  # retour au menu motion

        elif choix == "0":
            break
        else:
            print("Choix invalide, réessayez.")
            continue

        if script is None:
            continue

        print("[INFO] Lancement du script : " + os.path.basename(script))
        try:
            result = subprocess.run(
                [PYTHON2_PATH, script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("=== Sortie du script ===")
            print(result.stdout)
            if result.stderr:
                print("=== Erreurs éventuelles ===")
                print(result.stderr)
        except Exception as e:
            print("[ERROR] Impossible d'exécuter le script : " + str(e))



def launch_intelligent_vision_robot():
    """
    Système complet : LLM + reconnaissance faciale + chatbot NAO.

    Composants :
      - llm_server.py              (Python 3,    port 5000)
      - vision/main.py             (Python 3.10, ports 5001 + 5002)
      - nao_video_stream_publisher_vision.py  (Python 2.7, se connecte sur 5002)
      - nao_chatbot.py             (Python 2.7, appelle 5000 et 5001)
    """
    llm_server   = os.path.join(PROJECT_ROOT, "modules", "action", "speech_generation", "llm_server.py")
    face_server  = os.path.join(PROJECT_ROOT, "modules", "perception", "vision", "main.py")
    video_stream = os.path.join(PROJECT_ROOT, "modules", "perception", "vision", "nao_video_stream_publisher_vision.py")
    chatbot      = os.path.join(PROJECT_ROOT, "modules", "action", "speech_generation", "nao_chatbot.py")

    processes = []

    while True:
        print("\n=== Intelligent Vision Robot ===")
        print("1 - Lancer le système complet (LLM + Vision + Chatbot)")
        print("2 - Lancer uniquement le chatbot (serveurs déjà actifs)")
        print("3 - Lancer uniquement la reconnaissance faciale")
        print("0 - Retour au menu principal")

        choix = input("Votre choix : ").strip()

        if choix == "1":
            print("\n[INFO] Démarrage des serveurs...\n")

            # 1. Serveur LLM (Python 3)
            print("[INFO] Lancement du serveur LLM (port 5000)...")
            try:
                proc_llm = subprocess.Popen([PYTHON3_PATH, llm_server])
                processes.append(("LLM Server", proc_llm))
                print("[INFO] Serveur LLM lancé (PID {})".format(proc_llm.pid))
            except Exception as e:
                print("[ERROR] Impossible de lancer le serveur LLM : " + str(e))
                continue

            # 2. Serveur reconnaissance faciale (Python 3.10)
            print("[INFO] Lancement du serveur reconnaissance faciale (ports 5001+5002)...")
            try:
                proc_face = subprocess.Popen([PYTHON310_PATH, face_server])
                processes.append(("Face Server", proc_face))
                print("[INFO] Serveur vision lancé (PID {})".format(proc_face.pid))
            except Exception as e:
                print("[ERROR] Impossible de lancer le serveur vision : " + str(e))
                continue

            # Vérification que les serveurs sont bien up (max 30s)
            print("[INFO] Vérification des serveurs en cours...")
            llm_ok = False
            face_ok = False

            for attempt in range(30):
                time.sleep(1)
                try:
                    if not llm_ok:
                        requests.get("http://127.0.0.1:5000/history", timeout=1)
                        llm_ok = True
                        print("[INFO] ✓ Serveur LLM prêt")
                except Exception:
                    pass
                try:
                    if not face_ok:
                        requests.get("http://127.0.0.1:5001/last_face", timeout=1)
                        face_ok = True
                        print("[INFO] ✓ Serveur vision prêt")
                except Exception:
                    pass
                if llm_ok and face_ok:
                    break
                print("[INFO] Attente... ({}/30)".format(attempt + 1))

            if not llm_ok:
                print("[ERROR] Serveur LLM non accessible après 30s, abandon.")
                for name, proc in processes:
                    proc.terminate()
                processes.clear()
                continue

            if not face_ok:
                print("[WARN] Serveur vision non accessible, on continue sans reconnaissance faciale.")

            # 3. Flux vidéo NAO (Python 2.7)
            print("[INFO] Lancement du flux vidéo NAO...")
            try:
                proc_video = subprocess.Popen([PYTHON2_PATH, video_stream])
                processes.append(("Video Stream", proc_video))
                print("[INFO] Flux vidéo lancé (PID {})".format(proc_video.pid))
            except Exception as e:
                print("[ERROR] Impossible de lancer le flux vidéo : " + str(e))
                continue

            # 4. Chatbot NAO (Python 2.7) — bloquant, ECHAP pour quitter
            print("[INFO] Lancement du chatbot NAO...")
            print("[INFO] (ECHAP dans le chatbot pour arrêter tout le système)\n")
            try:
                subprocess.run([PYTHON2_PATH, chatbot])
            except Exception as e:
                print("[ERROR] Impossible de lancer le chatbot : " + str(e))

            # Arrêt propre de tous les processus
            print("\n[INFO] Chatbot terminé, arrêt des serveurs...")
            for name, proc in processes:
                try:
                    proc.terminate()
                    proc.wait()
                    print("[INFO] {} arrêté".format(name))
                except Exception:
                    pass
            processes.clear()

        elif choix == "2":
            print("[INFO] Lancement du serveur LLM (port 5000)...")
            try:
                proc_llm = subprocess.Popen([PYTHON3_PATH, llm_server])
                processes.append(("LLM Server", proc_llm))
                print("[INFO] Serveur LLM lancé (PID {})".format(proc_llm.pid))
            except Exception as e:
                print("[ERROR] Impossible de lancer le serveur LLM : " + str(e))
                continue

            print("[INFO] Lancement du chatbot seul...")
            try:
                subprocess.run([PYTHON2_PATH, chatbot])
            except Exception as e:
                print("[ERROR] Impossible de lancer le chatbot : " + str(e))

            # Arrêt du serveur LLM
            for name, proc in processes:
                try:
                    proc.terminate()
                    proc.wait()
                    print("[INFO] {} arrêté".format(name))
                except Exception:
                    pass
            processes.clear()

        elif choix == "3":
            print("[INFO] Lancement de la reconnaissance faciale uniquement...")

            # Serveur vision (Python 3.10)
            print("[INFO] Lancement du serveur vision (ports 5001+5002)...")
            try:
                proc_face = subprocess.Popen([PYTHON310_PATH, face_server])
                processes.append(("Face Server", proc_face))
                print("[INFO] Serveur vision lancé (PID {})".format(proc_face.pid))
            except Exception as e:
                print("[ERROR] Impossible de lancer le serveur vision : " + str(e))
                continue

            time.sleep(3)

            # Flux vidéo NAO (Python 2.7) — bloquant
            print("[INFO] Lancement du flux vidéo NAO...")
            try:
                subprocess.run([PYTHON2_PATH, video_stream])
            except Exception as e:
                print("[ERROR] Impossible de lancer le flux vidéo : " + str(e))

            # Arrêt du serveur vision
            print("\n[INFO] Flux vidéo terminé, arrêt du serveur vision...")
            for name, proc in processes:
                try:
                    proc.terminate()
                    proc.wait()
                    print("[INFO] {} arrêté".format(name))
                except Exception:
                    pass
            processes.clear()

        elif choix == "0":
            if processes:
                print("[INFO] Arrêt des processus en cours...")
                for name, proc in processes:
                    try:
                        proc.terminate()
                        proc.wait()
                        print("[INFO] {} arrêté".format(name))
                    except Exception:
                        pass
                processes.clear()
            break
        else:
            print("Choix invalide, réessayez.")