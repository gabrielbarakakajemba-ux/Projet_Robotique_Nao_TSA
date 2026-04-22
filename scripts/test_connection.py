# -*- coding: utf-8 -*-
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from config.python_paths import NAOQI_LIB_PATH
    if NAOQI_LIB_PATH not in sys.path:
        sys.path.insert(0, NAOQI_LIB_PATH)
except ImportError:
    print("FAIL: Fichier config.python_paths introuvable")
    sys.exit(1)

try:
    import qi
except ImportError:
    print("FAIL: Le SDK NAOqi est introuvable sur ce PC")
    sys.exit(1)

from config.nao_config import PORT, ROBOT_IP

ip_to_test = sys.argv[1] if len(sys.argv) > 1 else ROBOT_IP

session = qi.Session()
try:
    session.connect("tcp://{}:{}".format(ip_to_test, PORT))
    print("OK")
except Exception as e:
    print("FAIL: Connexion impossible a " + ip_to_test)
    sys.exit(1)