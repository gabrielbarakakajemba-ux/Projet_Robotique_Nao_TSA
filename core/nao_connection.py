# -*- coding: utf-8 -*-

import subprocess
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from config.python_paths import PYTHON2_PATH
    print(u"[SUCCESS] Python 2 path trouve : {}".format(PYTHON2_PATH))
except ImportError as e:
    print(u"[ERREUR] Import impossible. Details : {}".format(str(e)))
    print(u"Chemins explores par Python : {}".format(sys.path))
    PYTHON2_PATH = "python2"

def test_connection(ip=None):
    script_path = os.path.join("scripts", "test_connection.py")
    args = [PYTHON2_PATH, script_path]
    if ip:
        args.append(ip)

    try:
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        print("[DEBUG] stdout:", stdout)
        print("[DEBUG] stderr:", stderr)

        return "OK" in stdout

    except Exception as e:
        print("[ERREUR] Echec du lancement du test : " + str(e))
        return False
