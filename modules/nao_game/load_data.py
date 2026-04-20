import json
import sys
import os
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from database.question_repository import QuestionRepository

# Récupère toutes les questions depuis la DB
all_questions = QuestionRepository.get_all_questions()

# Nombre de questions voulues
N = 2

# Tirage aléatoire sans doublons
questions_list = random.sample(all_questions, min(N, len(all_questions)))

with open(r"C:\Users\Mathieu\Desktop\Projets\PFE\Projet robotique Nao\modules\nao_game\questions.json", "w") as f:
    json.dump(questions_list, f)

print("Nouvelles questions chargées avec succès !")