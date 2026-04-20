# -*- coding: utf-8 -*-
import subprocess
import os
import time
import requests
import webbrowser
from config.python_paths import PYTHON2_PATH, PYTHON3_PATH, PYTHON310_PATH

def launch_scenario():
    """
    Menu pour choisir le scénario Autisme à exécuter :
    - introduction
    - conclusion
    """
    # Dossier des scripts python
    base_path = os.path.join("modules", "scenarios_autisme")
    
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
        
        print("[INFO] Lancement du script :", os.path.basename(script))
        
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
            print("[ERROR] Impossible d'exécuter le script :", e)

def launch_nao_game():
    """
    Menu pour choisir le script de jeu à exécuter :
    - Nao Game
    - Ajouter une question/réponse
    - Générer les QR codes
    """
    base_path = os.path.join("modules", "nao_game")
    script3 = os.path.join(base_path, "load_data.py")
    script2 = os.path.join(base_path, "nao_game.py")
    while True:
        print("\n=== Nao Game ===")
        print("1 - Charger de nouvelles questions et lancer le jeu")
        print("0 - Retour au menu principal")

        choix = input("Votre choix : ").strip()

        if choix == "1":
            print("[INFO] Lancement de load_data.py")
            try:
                result = subprocess.run(
                    [PYTHON3_PATH, script3],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                print(result.stdout)
                if result.stderr:
                    print("=== Erreurs éventuelles ===")
                    print(result.stderr)

                if result.returncode != 0:
                    print("[ERROR] load_data.py a échoué, arrêt du lancement du jeu.")
                    continue  # ne pas lancer le jeu si erreur

            except Exception as e:
                print("[ERROR] Impossible d'exécuter load_data.py :", e)
                continue

            print("[INFO] Lancement de nao_game.py")
            try:
                result = subprocess.run(
                    [PYTHON2_PATH,  script2],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                print(result.stdout)
                if result.stderr:
                    print("=== Erreurs éventuelles ===")
                    print(result.stderr)
            except Exception as e:
                print("[ERROR] Impossible d'exécuter nao_game.py :", e)

        elif choix == "0":
            break
        else:
            print("Choix invalide, réessayez.")

def launch_motion_control():
    """
    Menu pour le script de contrôle manuel du robot
    à partir d'une manette PS3
    """
    base_path = os.path.join("modules", "motion_control")
    while True:
        print("\n=== Robot Motion Control ===")
        print("1 - Contrôle scénario")
        print("2 - Jeu ramassage de bouteilles")
        print("0 - Retour au menu principal")

        choix = input("Votre choix : ").strip()
        
        # initialiser script à None pour éviter UnboundLocalError
        script = None

        if choix == "1":
            script = os.path.join(base_path, "robot_motion_controller.py")
        elif choix == "2":
            # Lancer le script Python 3 (vision)
            script_py3 = os.path.join(base_path, "nao_object_detection.py")
            print("[INFO] Lancement du script Python 3 :", os.path.basename(script_py3))
            py3_proc = subprocess.Popen(
                [PYTHON3_PATH, script_py3]
            )

            # Lancer le script Python 2.7 (motion & pickup)
            script_py2 = os.path.join(base_path, "nao_video_stream_publisher.py")
            print("[INFO] Lancement du script Python 2.7 :", os.path.basename(script_py2))
            try:
                result = subprocess.run(
                    [PYTHON2_PATH, script_py2],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                print("=== Sortie du script Python 2.7 ===")
                print(result.stdout)
                if result.stderr:
                    print("=== Erreurs éventuelles ===")
                    print(result.stderr)
            except Exception as e:
                print("[ERROR] Impossible d'exécuter le script Python 2.7 :", e)

            # Quand le script Python 2.7 se termine, on tue le script Python 3
            try:
                py3_proc.terminate()
                py3_proc.wait()
            except Exception:
                pass
            print("[INFO] Script Python 3 terminé")
            # script reste None pour éviter ré-exécution en bas
        elif choix == "0":
            break
        else:
            print("Choix invalide, réessayez.")
            continue

        # Si un script a été sélectionné (hors cas choix==2 géré ci-dessus), l'exécuter
        if script is None:
            continue

        print("[INFO] Lancement du script :", os.path.basename(script))

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
            print("[ERROR] Impossible d'exécuter le script :", e)

def launch_intelligent_vision_robot():
    """
    Menu pour le système de chatbot intelligent avec reconnaissance faciale.
    Lance les 3 composants nécessaires :
    - Serveur LLM (Python 3.10, port 5000)
    - Serveur reconnaissance faciale (Python 3.10, ports 5001 + 5002)
    - Flux vidéo NAO (Python 2.7, se connecte sur 5002)
    - Chatbot NAO (Python 2.7, appelle 5000 et 5001)
    """
    base_path = os.path.join("modules", "intelligent_vision_robot")

    llm_server   = os.path.join(base_path, "nao_speech_interaction", "llm_server.py")
    face_server  = os.path.join(base_path, "main.py")
    video_stream = os.path.join(base_path, "nao_video_stream_publisher.py")
    chatbot      = os.path.join(base_path, "nao_speech_interaction", "nao_chatbot.py")

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

            # 1. Serveur LLM
            print("[INFO] Lancement du serveur LLM (port 5000)...")
            try:
                proc_llm = subprocess.Popen(
                    [PYTHON3_PATH, llm_server],
                )
                processes.append(("LLM Server", proc_llm))
                print("[INFO] Serveur LLM lancé (PID {})".format(proc_llm.pid))
            except Exception as e:
                print("[ERROR] Impossible de lancer le serveur LLM :", e)
                continue

            # 2. Serveur reconnaissance faciale 
            print("[INFO] Lancement du serveur reconnaissance faciale (ports 5001+5002)...")
            try:
                proc_face = subprocess.Popen(
                    [PYTHON310_PATH, face_server],
                )
                processes.append(("Face Server", proc_face))
                print("[INFO] Serveur vision lancé (PID {})".format(proc_face.pid))
            except Exception as e:
                print("[ERROR] Impossible de lancer le serveur vision :", e)
                continue

            # Vérification active que les serveurs sont up
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
                print("[ERROR] Serveur LLM non accessible après 15s, abandon.")
                for name, proc in processes:
                    proc.terminate()
                processes.clear()
                continue

            if not face_ok:
                print("[WARN] Serveur vision non accessible, on continue sans reconnaissance.")

            # 3. Flux vidéo NAO 
            print("[INFO] Lancement du flux vidéo NAO...")
            try:
                proc_video = subprocess.Popen(
                    [PYTHON2_PATH, video_stream],
                )
                processes.append(("Video Stream", proc_video))
                print("[INFO] Flux vidéo lancé (PID {})".format(proc_video.pid))
            except Exception as e:
                print("[ERROR] Impossible de lancer le flux vidéo :", e)
                continue

            # 4. Chatbot NAO 
            print("[INFO] Lancement du chatbot NAO...")
            print("[INFO] (ECHAP dans le chatbot pour arrêter tout le système)\n")
            try:
                subprocess.run([PYTHON2_PATH, chatbot])
            except Exception as e:
                print("[ERROR] Impossible de lancer le chatbot :", e)

            # Arrêt propre de tout
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
            print("[INFO] Lancement du chatbot seul...")

            print("[INFO] Lancement du serveur LLM (port 5000)...")
            try:
                proc_llm = subprocess.Popen(
                    [PYTHON3_PATH, llm_server],
                )
                processes.append(("LLM Server", proc_llm))
                print("[INFO] Serveur LLM lancé (PID {})".format(proc_llm.pid))
            except Exception as e:
                print("[ERROR] Impossible de lancer le serveur LLM :", e)
                continue
            
            try:
                subprocess.run(
                    [PYTHON2_PATH, chatbot],
                    stdout=None,
                    stderr=None
                )
            except Exception as e:
                print("[ERROR] Impossible de lancer le chatbot :", e)

        elif choix == "3":
            print("[INFO] Lancement de la reconnaissance faciale uniquement...")

            # 1. Serveur reconnaissance faciale (Python 3.10)
            print("[INFO] Lancement du serveur vision (ports 5001+5002)...")
            try:
                proc_face = subprocess.Popen(
                    [PYTHON310_PATH, face_server],
                    stdout=None,
                    stderr=None
                )
                processes.append(("Face Server", proc_face))
                print("[INFO] Serveur vision lancé (PID {})".format(proc_face.pid))
            except Exception as e:
                print("[ERROR] Impossible de lancer le serveur vision :", e)
                continue

            time.sleep(3)

            # 2. Flux vidéo NAO (Python 2.7) — bloquant
            print("[INFO] Lancement du flux vidéo NAO...")
            try:
                result = subprocess.run(
                    [PYTHON2_PATH, video_stream],
                    stdout=None,
                    stderr=None
                )
            except Exception as e:
                print("[ERROR] Impossible de lancer le flux vidéo :", e)

            # Quand le flux vidéo se termine, on arrête le serveur vision
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


def launch_web_interface():
    """Lance l'interface web du projet."""
    web_app = os.path.join("web", "app.py")
    if not os.path.exists(web_app):
        print("[ERROR] Interface web introuvable : {}".format(web_app))
        return

    try:
        proc = subprocess.Popen([PYTHON3_PATH, web_app])
        url = "http://127.0.0.1:8000"
        print("[INFO] Interface web lancée sur {} (PID {})".format(url, proc.pid))
        try:
            webbrowser.open(url)
        except Exception:
            pass
    except Exception as e:
        print("[ERROR] Impossible de lancer l'interface web : {}".format(e))