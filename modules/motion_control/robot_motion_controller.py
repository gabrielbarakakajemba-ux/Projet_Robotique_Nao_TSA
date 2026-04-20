# -*- coding: utf-8 -*-
import qi
import sys
import os
import pygame

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from config.nao_config import ROBOT_IP, PORT
from config.settings import apply_settings
from utils.speech_and_animation_player import say_with_animation

session = qi.Session()
try:
    session.connect("tcp://{}:{}".format(ROBOT_IP, PORT))
    print("Connexion réussie")
except RuntimeError:
    print("Impossible de se connecter au robot")
    sys.exit(1)

apply_settings(session)

tts = session.service("ALTextToSpeech")
motion = session.service("ALMotion")
posture = session.service("ALRobotPosture")
animation_player = session.service("ALAnimationPlayer")

posture.goToPosture("StandInit", 0.5)

# ---------- INITIALISATION MANETTE ----------
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("Aucune manette détectée !")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print("Manette détectée :", joystick.get_name())

# ---------- BOUCLE PRINCIPALE ----------
try:
    while True:
        pygame.event.pump()  # met à jour l'état de la manette

        # Lecture axes du joystick gauche
        axe_x = joystick.get_axis(0)  # gauche/droite
        axe_y = joystick.get_axis(1)  # avant/arrière

        # Déplacements proportionnels au joystick
        if abs(axe_x) > 0.1 or abs(axe_y) > 0.1:
            motion.moveTo(-axe_y*0.2, 0, -axe_x*0.5)

        # Lecture boutons
        btn_square = joystick.get_button(15)  
        btn_cross   = joystick.get_button(14)  
        btn_circle    = joystick.get_button(13)  
        btn_triangle   = joystick.get_button(12)  
        btn_start = joystick.get_button(3) 

        # Animations avec les boutons triangle, carré, rond et X
        if btn_triangle:
            say_with_animation(tts,
                   animation_player,
                   """Salut c'est Nao !""",
                   "animations/Stand/Emotions/Positive/Excited_2"
                   )
        elif btn_square:
            tts.say("Go hélicopter")
            animation_player.run("animations/Stand/Waiting/Helicopter_1")
        elif btn_cross:
            tts.say("En voiture les amis !")
            animation_player.run("animations/Stand/Waiting/DriveCar_1")
        elif btn_circle:
            tts.say("1, 2, 3")
            animation_player.run("animations/Stand/Waiting/HappyBirthday_1")
        elif btn_start:
            print("Bouton Start pressé, arrêt du script")
            motion.stopMove()
            pygame.quit()
            sys.exit(0)

        pygame.time.wait(50)

except KeyboardInterrupt:
    print("Arrêt du contrôle manette")
    motion.stopMove()
    pygame.quit()
    sys.exit()
