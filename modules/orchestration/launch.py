# -*- coding: utf-8 -*-

import subprocess
import os
import sys
import time
import requests

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def _resolve_python(path, fallback="python3"):
    """Si le chemin configure n'existe pas, retourne un fallback PATH."""
    import shutil
    if path and os.path.isfile(path):
        return path
    found = shutil.which(os.path.basename(path)) if path else None
    if found:
        return found
    return shutil.which(fallback) or fallback


try:
    from config.python_paths import NAOQI_LIB_PATH, PYTHON2_PATH, PYTHON3_PATH, PYTHON310_PATH
    if NAOQI_LIB_PATH not in sys.path:
        sys.path.insert(0, NAOQI_LIB_PATH)
    print("Configuration chargee avec succes !")
except ImportError as e:
    print("Impossible de charger config.python_paths : " + str(e))
    PYTHON2_PATH   = os.environ.get("PYTHON2_PATH",   "python2")
    PYTHON3_PATH   = os.environ.get("PYTHON3_PATH",   "python3")
    PYTHON310_PATH = os.environ.get("PYTHON310_PATH", "python3.10")

PYTHON2_PATH   = _resolve_python(PYTHON2_PATH,   "python2")
PYTHON3_PATH   = _resolve_python(PYTHON3_PATH,   "python3")
PYTHON310_PATH = _resolve_python(PYTHON310_PATH, "python3")

print("PROJECT_ROOT  = {}".format(PROJECT_ROOT))
print("PYTHON2_PATH  = {}".format(PYTHON2_PATH))
print("PYTHON3_PATH  = {}".format(PYTHON3_PATH))
print("PYTHON310_PATH= {}".format(PYTHON310_PATH))


def launch_scenario():
    base_path = os.path.join(PROJECT_ROOT, "modules", "behaviors", "autism_scenarios")

    while True:
        print("\n=== Scenarios Autisme ===")
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
            print("Choix invalide, reessayez.")
            continue

        print("[INFO] Lancement du script : " + os.path.basename(script))
        try:
            result = subprocess.run(
                [PYTHON2_PATH, script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(result.stdout)
            if result.stderr:
                print("=== Erreurs ===")
                print(result.stderr)
        except Exception as e:
            print("[ERROR] Impossible d'executer le script : " + str(e))


def launch_nao_game():
    base_path   = os.path.join(PROJECT_ROOT, "modules", "behaviors", "games")
    script_load = os.path.join(base_path, "load_data.py")
    script_game = os.path.join(base_path, "nao_game.py")

    while True:
        print("\n=== Nao Game ===")
        print("1 - Charger de nouvelles questions et lancer le jeu")
        print("0 - Retour au menu principal")

        choix = input("Votre choix : ").strip()

        if choix == "1":
            print("[INFO] Lancement de load_data.py (Python 3)...")
            try:
                result = subprocess.run(
                    [PYTHON3_PATH, script_load],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
                if result.returncode != 0:
                    print("[ERROR] load_data.py a echoue, le jeu ne sera pas lance.")
                    continue
            except Exception as e:
                print("[ERROR] Impossible d'executer load_data.py : " + str(e))
                continue

            print("[INFO] Lancement de nao_game.py (Python 2.7)...")
            try:
                result = subprocess.run(
                    [PYTHON2_PATH, script_game],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
            except Exception as e:
                print("[ERROR] Impossible d'executer nao_game.py : " + str(e))

        elif choix == "0":
            break
        else:
            print("Choix invalide, reessayez.")


def launch_motion_control():
    while True:
        print("\n=== Robot Motion Control ===")
        print("1 - Controle scenario (manette PS3)")
        print("2 - Jeu ramassage de bouteilles")
        print("0 - Retour au menu principal")

        choix = input("Votre choix : ").strip()
        script = None

        if choix == "1":
            script = os.path.join(PROJECT_ROOT, "modules", "action", "motion",
                                   "robot_motion_controller.py")

        elif choix == "2":
            script_py3 = os.path.join(PROJECT_ROOT, "modules", "perception", "vision",
                                       "object_detection", "nao_object_detection.py")
            script_py2 = os.path.join(PROJECT_ROOT, "modules", "perception", "vision",
                                       "nao_video_stream_publisher_motion.py")
            print("[INFO] Lancement detection objets (Python 3)...")
            py3_proc = subprocess.Popen([PYTHON3_PATH, script_py3])
            print("[INFO] Lancement flux video NAO (Python 2.7)...")
            try:
                result = subprocess.run(
                    [PYTHON2_PATH, script_py2],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
            except Exception as e:
                print("[ERROR] " + str(e))
            try:
                py3_proc.terminate()
                py3_proc.wait()
                print("[INFO] Detection objets arretee.")
            except Exception:
                pass
            continue

        elif choix == "0":
            break
        else:
            print("Choix invalide.")
            continue

        if script:
            print("[INFO] Lancement : " + os.path.basename(script))
            try:
                result = subprocess.run(
                    [PYTHON2_PATH, script],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
            except Exception as e:
                print("[ERROR] " + str(e))


def launch_intelligent_vision_robot():
    llm_server   = os.path.join(PROJECT_ROOT, "modules", "action", "speech_generation", "llm_server.py")
    face_server  = os.path.join(PROJECT_ROOT, "modules", "perception", "vision", "main.py")
    video_stream = os.path.join(PROJECT_ROOT, "modules", "perception", "vision",
                                 "nao_video_stream_publisher_vision.py")
    chatbot      = os.path.join(PROJECT_ROOT, "modules", "action", "speech_generation", "nao_chatbot.py")

    processes = []

    while True:
        print("\n=== Intelligent Vision Robot ===")
        print("1 - Lancer le systeme complet (LLM + Vision + Chatbot)")
        print("2 - Lancer uniquement le chatbot (serveurs deja actifs)")
        print("3 - Lancer uniquement la reconnaissance faciale")
        print("0 - Retour au menu principal")

        choix = input("Votre choix : ").strip()

        if choix == "1":
            print("\n[INFO] Demarrage des serveurs...\n")

            try:
                proc_llm = subprocess.Popen([PYTHON3_PATH, llm_server])
                processes.append(("LLM Server", proc_llm))
                print("[INFO] Serveur LLM lance (PID {})".format(proc_llm.pid))
            except Exception as e:
                print("[ERROR] LLM : " + str(e)); continue

            try:
                proc_face = subprocess.Popen([PYTHON310_PATH, face_server])
                processes.append(("Face Server", proc_face))
                print("[INFO] Serveur vision lance (PID {})".format(proc_face.pid))
            except Exception as e:
                print("[ERROR] Vision : " + str(e)); continue

            print("[INFO] Verification des serveurs...")
            llm_ok = face_ok = False
            for attempt in range(30):
                time.sleep(1)
                try:
                    if not llm_ok:
                        requests.get("http://127.0.0.1:5000/history", timeout=1)
                        llm_ok = True
                        print("[INFO] Serveur LLM pret")
                except Exception:
                    pass
                try:
                    if not face_ok:
                        requests.get("http://127.0.0.1:5001/last_face", timeout=1)
                        face_ok = True
                        print("[INFO] Serveur vision pret")
                except Exception:
                    pass
                if llm_ok and face_ok:
                    break
                print("[INFO] Attente... ({}/30)".format(attempt + 1))

            if not llm_ok:
                print("[ERROR] Serveur LLM non accessible apres 30 s, abandon.")
                for _, proc in processes: proc.terminate()
                processes.clear(); continue

            if not face_ok:
                print("[WARN] Serveur vision non accessible, on continue sans reconnaissance.")

            try:
                proc_video = subprocess.Popen([PYTHON2_PATH, video_stream])
                processes.append(("Video Stream", proc_video))
                print("[INFO] Flux video lance (PID {})".format(proc_video.pid))
            except Exception as e:
                print("[ERROR] Flux video : " + str(e)); continue

            print("[INFO] Lancement du chatbot NAO (ECHAP pour quitter)...")
            try:
                subprocess.run([PYTHON2_PATH, chatbot])
            except Exception as e:
                print("[ERROR] Chatbot : " + str(e))

            print("\n[INFO] Arret des serveurs...")
            for name, proc in processes:
                try: proc.terminate(); proc.wait(); print("[INFO] {} arrete".format(name))
                except Exception: pass
            processes.clear()

        elif choix == "2":
            try:
                proc_llm = subprocess.Popen([PYTHON3_PATH, llm_server])
                processes.append(("LLM Server", proc_llm))
            except Exception as e:
                print("[ERROR] LLM : " + str(e)); continue
            try:
                subprocess.run([PYTHON2_PATH, chatbot])
            except Exception as e:
                print("[ERROR] Chatbot : " + str(e))
            for name, proc in processes:
                try: proc.terminate(); proc.wait()
                except Exception: pass
            processes.clear()

        elif choix == "3":
            try:
                proc_face = subprocess.Popen([PYTHON310_PATH, face_server])
                processes.append(("Face Server", proc_face))
            except Exception as e:
                print("[ERROR] Vision : " + str(e)); continue
            time.sleep(3)
            try:
                subprocess.run([PYTHON2_PATH, video_stream])
            except Exception as e:
                print("[ERROR] Flux video : " + str(e))
            for name, proc in processes:
                try: proc.terminate(); proc.wait()
                except Exception: pass
            processes.clear()

        elif choix == "0":
            for name, proc in processes:
                try: proc.terminate(); proc.wait()
                except Exception: pass
            processes.clear()
            break
        else:
            print("Choix invalide.")


def main():
    while True:
        print(u"""
================================================
       Systeme NAO TSA - Menu Principal
================================================
  1 - Lancer la session complete (main.py)
  2 - Scenarios (introduction / conclusion)
  3 - Jeux NAO
  4 - Controle mouvement
  5 - Vision + LLM + Chatbot
  0 - Quitter
================================================""")

        choix = input("Votre choix : ").strip()

        if choix == "1":
            main_script = os.path.join(PROJECT_ROOT, "main.py")
            subprocess.run([PYTHON3_PATH, main_script])
        elif choix == "2":
            launch_scenario()
        elif choix == "3":
            launch_nao_game()
        elif choix == "4":
            launch_motion_control()
        elif choix == "5":
            launch_intelligent_vision_robot()
        elif choix == "0":
            print("Au revoir !")
            sys.exit(0)
        else:
            print("Choix invalide.")


if __name__ == "__main__":
    main()
