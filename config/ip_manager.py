# -*- coding: utf-8 -*-

import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "nao_config.py")

def save_ip(ip):
    # Charger les configurations existantes
    existing_config = {}
    with open(CONFIG_FILE, "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.split("=", 1)
                existing_config[key.strip()] = value.strip()

    # Mettre à jour l'adresse IP
    existing_config['ROBOT_IP'] = "'{}'".format(ip)

    # Réécrire le fichier de configuration
    with open(CONFIG_FILE, "w") as f:
        f.write("# -*- coding: utf-8 -*-\n")
        for key, value in existing_config.items():
            f.write("{} = {}\n".format(key, value))

def load_ip():
    try:
        from config.nao_config import ROBOT_IP
        return ROBOT_IP
    except:
        return None
