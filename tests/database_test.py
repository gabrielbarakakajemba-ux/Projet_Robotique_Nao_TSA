# -*- coding: utf-8 -*-
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.join(current_dir, ".."))

if root_path not in sys.path:
    sys.path.insert(0, root_path)

try:
    from database.faces_repository import FacesRepository
    print("[SUCCESS] FacesRepository charge avec succes !")
except ImportError as e:
    print("[ERREUR] Impossible de trouver le module 'modules'.")
    print("Chemin racine recherche : " + root_path)
    print("Detail : " + str(e))
    sys.exit(1)


def test_db():
    try:
        repo = FacesRepository()
        users = repo.get_all_persons()
        print("[OK] Connexion DB reussie. Nombre d'utilisateurs : {}".format(len(users)))
        for user in users:
            print(" - Utilisateur trouve : {}".format(user[0]))   # user[0] = prenom
    except Exception as e:
        print("[ERREUR] La base de données ne répond pas : {}".format(e))

if __name__ == "__main__":
    test_db()