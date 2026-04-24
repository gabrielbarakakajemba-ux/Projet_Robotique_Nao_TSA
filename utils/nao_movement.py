# -*- coding: utf-8 -*-
import time

def pickup_bottle(motion, posture):
    """
    Ramasser une bouteille en restant debout.
    Bras rapproches au maximum, coudes plies, avant-bras tournes,
    doigts ouverts puis fermes pour tenir la bouteille.
    """
    try:
        speed = 0.2  # Un peu plus lent pour plus de precision
        
        # **Assurer que le robot est bien stable avant de bouger les bras**
        if posture.getFamily() != "Standing":
            posture.goToPosture("Stand", 0.5)

        # 1️⃣ Position de preparation : bras vers le bas et mains ouvertes
        # On fait tout en un seul appel pour un mouvement plus fluide
        joints = ["LShoulderPitch", "RShoulderPitch", "LShoulderRoll", "RShoulderRoll", "LHand", "RHand"]
        angles = [1.2, 1.2, 0.3, -0.3, 1.0, 1.0] # 1.0 = Main ouverte**
        motion.angleInterpolationWithSpeed(joints, angles, speed)

        # 2️⃣ Approche : On rapproche les bras pour entourer la bouteille
        # On plie les coudes (Roll) et on tourne les avant-bras (Yaw)
        motion.angleInterpolationWithSpeed(
            ["LElbowRoll", "RElbowRoll", "LElbowYaw", "RElbowYaw", "LShoulderRoll", "RShoulderRoll"],
            [-1.2, 1.2, -1.0, 1.0, 0.05, -0.05],
            speed
        )

        time.sleep(0.5)

        # 3️⃣ Saisie : On ferme les mains fermement
        motion.closeHand("LHand")
        motion.closeHand("RHand")
        
        # **On augmente la force (Stiffness) des mains pour bien tenir**
        motion.setStiffnesses(["LHand", "RHand"], 1.0)

        time.sleep(0.5)

        # 4️⃣ Levage : On souleve la bouteille doucement
        # On remonte les epaules (Pitch diminue)
        motion.angleInterpolationWithSpeed(
            ["LShoulderPitch", "RShoulderPitch", "LWristYaw", "RWristYaw"],
            [0.6, 0.6, 0.0, 0.0],
            0.1
        )

        print(u"Bouteille saisie avec succes !")

    except Exception as e:
        print("Erreur pickup_bottle: {}".format(e))

def release_bottle(motion):
    """ Relache la bouteille et remet les bras le long du corps """
    try:
        motion.openHand("LHand")
        motion.openHand("RHand")
        time.sleep(0.5)
        motion.angleInterpolationWithSpeed(["LShoulderPitch", "RShoulderPitch"], [1.5, 1.5], 0.2)
        # On baisse la tension pour eviter la chauffe
        motion.setStiffnesses("Arms", 0.0)
    except Exception as e:
        print("Erreur release_bottle: {}".format(e))