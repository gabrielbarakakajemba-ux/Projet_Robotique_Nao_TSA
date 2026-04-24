# -*- coding: utf-8 -*-
import sys
import os
import types

# 1. FIXER LE CHEMIN (Pour que 'database' et 'modules' soient trouvés)
root_path = os.path.dirname(os.path.abspath(__file__))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

print("--- DEMARRAGE DU TEST ---")

# 2. MOCK NAOQI (Pour éviter le crash Python 3)
m_naoqi = types.ModuleType('naoqi')
m_naoqi.ALProxy = lambda *args, **kwargs: None 
sys.modules['naoqi'] = m_naoqi
sys.modules['qi'] = types.ModuleType('qi')

# 3. TENTATIVE D'IMPORTS DES MODULES DU PROJET
try:
    print("[1/3] Chargement de la base de donnees...")
    from database.faces_repository import FacesRepository
    
    print("[2/3] Chargement des scenarios...")
    import modules.behaviors.autism_scenarios.introduction_nao as introduction
    
    print("[3/3] Chargement des jeux...")
    import modules.behaviors.games.nao_game as nao_game
    
    print("-> TOUS LES MODULES SONT CHARGES.\n")
except ImportError as e:
    print("\n[ERREUR] Module introuvable : {}".format(e))
    print("Verifie que tu es bien a la racine de : /home/mr-kajemba/Nao_Autisme")
    sys.exit(1)

class NaoTsaTest:
    def __init__(self):
        # On essaie d'instancier ton FacesRepository (MySQL XAMPP)
        try:
            self.db = FacesRepository()
            print("[OK] Connexion MySQL etablie.")
        except Exception as e:
            print("[ATTENTION] La DB n'a pas pu charger : {}".format(e))
            self.db = None
        
        self.current_child_name = ""

    def run(self):
        print("\n--- DEBUT DE LA SIMULATION ---")
        
        # SIMULATION VISION
        print("🤖 NAO: Je regarde autour de moi...")
        nom = input("Saisir le nom de l'enfant pour simuler la vision : ")
        self.current_child_name = nom if nom else "Ami"

        # SIMULATION INTRODUCTION
        print("\n🤖 NAO: Bonjour {} !".format(self.current_child_name))
        # Ici on appelle ton module
        # introduction.run(self.current_child_name) 

        # SIMULATION CHOIX DU JEU
        print("\n--- CHOIX DU JEU ---")
        print("A: Imitations | B: Emotions | X: Questions")
        choix = input("Appuie sur une touche (A/B/X) : ").upper()

        if choix == "A":
            jeu = "Jeu des imitations"
        elif choix == "B":
            jeu = "Jeu des Emotions"
        else:
            jeu = "Jeu des questions"

        print("\n🤖 NAO: Super ! On va jouer au {}.".format(jeu))
        
        # SIMULATION LOG BDD
        if self.db:
            print("[LOG] Enregistrement de la session dans MySQL...")
            # self.db.log_session_start(1, jeu) # Utilise tes vraies fonctions

        print("\n--- FIN DE LA SESSION ---")

if __name__ == "__main__":
    app = NaoTsaTest()
    app.run()