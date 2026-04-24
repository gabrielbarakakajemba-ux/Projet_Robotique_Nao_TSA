# -*- coding: utf-8 -*-
import pygame

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("Aucune manette détectée !")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print("Manette détectée :", joystick.get_name())

print("Appuie sur les boutons pour voir leur numéro. Ctrl+C pour quitter.")

while True:
    pygame.event.pump()
    for i in range(joystick.get_numbuttons()):
        if joystick.get_button(i):
            print("Bouton pressé :", i)
    pygame.time.wait(100)
