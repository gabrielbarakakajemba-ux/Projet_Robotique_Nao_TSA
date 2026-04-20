# -*- coding: utf-8 -*-

import subprocess
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from config.python_paths import PYTHON2_PATH
    print(u"[SUCCESS] Python 2 path trouvé : {}".format(PYTHON2_PATH))
except ImportError as e:
    print(u"[ERREUR] Import impossible. Details : {}".format(str(e)))
    print(u"Chemins explores par Python : {}".format(sys.path))
    PYTHON2_PATH = "python2"

def test_connection(ip=None):
    """
    Lance le script Python2.7 pour tester la connexion NAO.
    Si ip est fourni, on l'utilise, sinon le script utilise la config.
    """
    script_path = os.path.join("scripts", "test_connection.py")

    # Ajouter l'IP comme argument optionnel
    args = [PYTHON2_PATH, script_path]
    if ip:
        args.append(ip)

    result = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print("[DEBUG] stdout:", result.stdout)
    print("[DEBUG] stderr:", result.stderr)

    return "OK" in result.stdout
