# -*- coding: utf-8 -*-

import time

class RobotMotionController:

    def __init__(self, robot_ip="127.0.0.1", port=9559):
        self.robot_ip = robot_ip
        self.port     = port
        self.session  = None
        self.tts              = None
        self.motion           = None
        self.posture          = None
        self.animation_player = None
        self.is_connected     = False

        self._connect_to_robot()

    def _connect_to_robot(self):
        try:
            import qi
            self.session = qi.Session()
            self.session.connect("tcp://{}:{}".format(self.robot_ip, self.port))

            self.tts              = self.session.service("ALTextToSpeech")
            self.motion           = self.session.service("ALMotion")
            self.posture          = self.session.service("ALRobotPosture")
            self.animation_player = self.session.service("ALAnimationPlayer")

            self.tts.setLanguage("French")
            self.is_connected = True
            print(u"[OK] Connecte au robot NAO ({}:{})".format(self.robot_ip, self.port))

        except Exception as e:
            print(u"[SIMULATION] Impossible de se connecter : {}".format(e))
            print(u"[SIMULATION] Mode console active.")
            self.is_connected = False

    def stand_up(self):
        if self.is_connected and self.posture:
            self.posture.goToPosture("StandInit", 0.5)
        else:
            print(u"[ACTION] Le robot se leve (simule)")

    def say(self, text):
        if self.is_connected and self.tts:
            self.tts.say(text)
        else:
            print(u"\n[NAO DIT] : {}".format(text))

    def play_animation(self, animation_path):
        if self.is_connected and self.animation_player:
            self.animation_player.run(animation_path)
        else:
            print(u"[ANIMATION] : {} (simule)".format(animation_path))

    def rest(self):
        if self.is_connected and self.motion:
            self.motion.rest()
        else:
            print(u"[ACTION] Le robot se met au repos (simule)")

    def move(self, x, y, theta):
        if self.is_connected and self.motion:
            self.motion.move(x, y, theta)
        else:
            if abs(x) > 0.1 or abs(theta) > 0.1:
                print(u"[MOVE] x={}, y={}, theta={} (simule)".format(x, y, theta))

    def get_button_pressed(self):
        try:
            import pygame
            pygame.event.pump()
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    mapping = {12: 'A', 15: 'B', 14: 'X'}
                    btn = mapping.get(event.button)
                    if btn:
                        return btn
                    print(u"[MANETTE] Bouton non mappe : index {}".format(event.button))
        except Exception as e:
            print(u"[MANETTE] Erreur lecture : {}".format(e))
        return None
