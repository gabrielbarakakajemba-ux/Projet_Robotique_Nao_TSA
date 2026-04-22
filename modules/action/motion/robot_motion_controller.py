# -*- coding: utf-8 -*-
import sys
import os
import pygame

# Configuration des chemins

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, root_path)

try:
    from config.python_paths import NAOQI_LIB_PATH
    # On ajoute dynamiquement le chemin de Choregraphe
    sys.path.insert(0, NAOQI_LIB_PATH)
    from naoqi import ALProxy
    print("Succès : Le module naoqi est chargé !")
except ImportError as e:
    print("Erreur critique : " + str(e))
    sys.exit(1)

from config.nao_config import ROBOT_IP, PORT



try:
    print(u"Connexion à {}:{}...".format(ROBOT_IP, PORT))
    
    # Création des proxys via ALProxy
    tts = ALProxy("ALTextToSpeech", ROBOT_IP, PORT)
    motion = ALProxy("ALMotion", ROBOT_IP, PORT)
    posture = ALProxy("ALRobotPosture", ROBOT_IP, PORT)
    # ALAnimationPlayer est disponible sur NAOqi 2.1+
    animation_player = ALProxy("ALAnimationPlayer", ROBOT_IP, PORT)
    
    print(u"Connexion réussie")
except Exception as e:
    print(u"Impossible de se connecter au robot : " + str(e))
    sys.exit(1)

# Mise en position initiale
posture.goToPosture("StandInit", 0.5)

# ---------- INITIALISATION MANETTE ----------
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("Aucune manette detectee !")
    sys.exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print("Manette detectee : " + joystick.get_name())

# ---------- BOUCLE PRINCIPALE ----------
try:
    while True:
        pygame.event.pump()

        # Lecture axes du joystick (Zone morte de 0.1 pour éviter les dérives)
        axe_x = joystick.get_axis(0)
        axe_y = joystick.get_axis(1)

        if abs(axe_x) > 0.1 or abs(axe_y) > 0.1:
            # ALMotion.move(x, y, theta) est mieux pour un contrôle continu au joystick 
            # que moveTo qui est bloquant
            motion.move(-axe_y * 0.5, 0, -axe_x * 0.8)
        else:
            motion.stopMove()

        # Lecture boutons (Vérifie les index selon ta manette PS4/Xbox)
        if joystick.get_button(12): # Triangle
            # Utilisation directe si say_with_animation pose problème
            tts.say("Salut c'est Nao !")
            animation_player.run("animations/Stand/Emotions/Positive/Excited_2")
            
        elif joystick.get_button(15): # Carré
            tts.say("Go helicopter")
            animation_player.run("animations/Stand/Waiting/Helicopter_1")
            
        elif joystick.get_button(14): # Croix
            tts.say("En voiture les amis !")
            animation_player.run("animations/Stand/Waiting/DriveCar_1")
            
        elif joystick.get_button(13): # Rond
            tts.say("1, 2, 3")
            animation_player.run("animations/Stand/Waiting/HappyBirthday_1")
            
        elif joystick.get_button(3): # Start
            print("Arret du script...")
            break

        pygame.time.wait(100) # Un peu plus de repos pour le processeur

except KeyboardInterrupt:
    print("Interrompu par l'utilisateur")

finally:
    motion.stopMove()
    pygame.quit()
    print("Fermeture propre.")