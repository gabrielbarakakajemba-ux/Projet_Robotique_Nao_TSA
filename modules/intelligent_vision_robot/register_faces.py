# -*- coding: utf-8 -*-
import cv2
from pathlib import Path
import sys
import os
import mediapipe as mp

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from recognition.facenet_recognizer import FaceRecognizer
from database.faces_repository import FacesRepository
from unknown_faces import UnknownFaceManager
from hand_gesture_detection import open_hand, create_hand_detector, draw_hand


def main():
    print("Gesture-Based Face Greeting System")
    print("-" * 40)

    recognizer = FaceRecognizer()
    unknown_manager = UnknownFaceManager()

    # Initialisation du detector MediaPipe
    detector = create_hand_detector()
    frame_timestamp_ms = 0

    cap = cv2.VideoCapture(0)
    salutation_faite = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        # Conversion pour MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Détection landmarks
        result = detector.detect_for_video(mp_image, frame_timestamp_ms)
        frame_timestamp_ms += 33

        # Vérifie si une main ouverte est détectée
        gesture_detected = False
        if result.hand_landmarks:
            for hand_landmarks in result.hand_landmarks:
                draw_hand(frame, hand_landmarks)
                if open_hand(hand_landmarks):  # ✅ on passe les landmarks, pas la frame
                    gesture_detected = True

        if gesture_detected and not salutation_faite:
            print("Main détectée, reconnaissance faciale...")

            result_face = recognizer.recognize(frame)

            if result_face["recognized"]:
                name = result_face["name"]
                print("Salut {}".format(name))

            else:
                print("Oh je crois pas te connaitre, donne moi ton prénom : ")
                name = input().strip()

                if name:
                    embedding = result_face["embedding"]
                    FacesRepository.insert_person(name, embedding)
                    unknown_manager.register_unknown_face(result_face["face_id"], name)
                    print("✓ {} enregistré avec succès !".format(name))

            salutation_faite = True

        if not gesture_detected:
            salutation_faite = False

        cv2.imshow("Camera", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Arrêt du système")


if __name__ == "__main__":
    main()