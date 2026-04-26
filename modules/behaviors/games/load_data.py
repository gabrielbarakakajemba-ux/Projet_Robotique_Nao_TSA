# -*- coding: utf-8 -*-
import json
import sys
import os
import random

current_dir = os.path.dirname(os.path.abspath(__file__))

BASE_DIR = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))

if os.path.basename(BASE_DIR) == "modules":
    BASE_DIR = os.path.dirname(BASE_DIR)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

    try:
        from database.question_repository import QuestionRepository
    except ImportError:
        print("[ERROR] Impossible de trouver le dossier database !")
        print("Dossier parent actuel : " + os.path.basename(BASE_DIR))
        print("Chemin complet tente : " + BASE_DIR)
        sys.exit(1)


def refresh_questions(n_questions=3):
    print("[INFO] Chargement des questions depuis la base de donnees...")

    try:
        all_questions = QuestionRepository.get_all_questions()

        if not all_questions:
            print("[WARN] Aucune question trouvee dans la base de donnees.")
            return

        selected = random.sample(all_questions, min(n_questions, len(all_questions)))

        json_path = os.path.join(BASE_DIR, "modules", "behaviors", "games", "questions.json")

        with open(json_path, "w") as f:
            json.dump(selected, f)

        print("[OK] {} nouvelles questions sauvegardees dans questions.json".format(len(selected)))

    except Exception as e:
        print("[ERROR] Echec du chargement : " + str(e))
