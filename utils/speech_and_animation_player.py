# -*- coding: utf-8 -*-
import sys

def say_with_animation(tts_service, animation_service, text, animation_name):
    """
    Fait parler le robot tout en executant une animation de maniere synchronisee.
    """
    try:
        # On lance la parole et l'animation en parallele (_async=True)
        tts_task = tts_service.say(str(text), _async=True)
        anim_task = animation_service.run(animation_name, _async=True)
        
        # On attend que les deux soient finis
        tts_task.wait()
        anim_task.wait()
    except Exception as e:
        print("Erreur animation: {}".format(e))
        # En cas d'echec de l'animation, on essaie au moins de faire parler le robot
        tts_service.say(str(text))


ANIMS = {
    "HELLO": "animations/Stand/Gestures/Hey_1",
    "THINK": "animations/Stand/Gestures/Thinking_1",
    "EXPLAIN": "animations/Stand/Gestures/Explain_1",
    "HAPPY": "animations/Stand/Emotions/Positive/Happy_1",
    "SAD": "animations/Stand/Emotions/Negative/Sad_1",
    "YOU_DID_IT": "animations/Stand/Gestures/Victory_1",
    "PLEASE": "animations/Stand/Gestures/Please_1"
}

def celebrate(tts_service, animation_service):
    """ Animation rapide pour feliciter l'enfant """
    say_with_animation(
        tts_service, 
        animation_service, 
        "C'est super ! Tu as reussi !", 
        ANIMS["YOU_DID_IT"]
    )