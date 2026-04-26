# -*- coding: utf-8 -*-
import cv2
from pathlib import Path
import sys
import os
import mediapipe as mp

current_dir = os.path.dirname(os.path.abspath(__file__))

root = os.path.abspath(os.path.join(current_dir, "..", "..", "..", ".."))

if root not in sys.path:
    sys.path.insert(0, root)

from database.connection import get_db_connection

try:
    from hand_gesture_detection import open_hand, create_hand_detector, draw_hand
    print("[OK] Modules de gestes charges depuis le sous-dossier.")
except ImportError as e:
    print("[ERROR] Toujours impossible de trouver le module.")
    print("Detail de l'erreur : {}".format(e))
    print("Contenu de {}: {}".format(current_dir, os.listdir(current_dir)))
    sys.exit(1)

from recognition.facenet_recognizer import FaceRecognizer
from unknown_faces import UnknownFaceManager
from database.faces_repository import FacesRepository
from detection.yolo_detection  import YOLODetector


def main():
    print("Gesture-Based Face Greeting System")
    print("-" * 40)

    recognizer = FaceRecognizer()
    unknown_manager = UnknownFaceManager()

    detector_hand = create_hand_detector()
    frame_timestamp_ms = 0

    detector_yolo = YOLODetector()


    print("[INFO] Chargement de la base de donnees faciale...")
    persons_db = FacesRepository.get_all_faces()

    frame_timestamp_ms = 0

    cap = cv2.VideoCapture(0)
    salutation_faite = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        result = detector_hand.detect_for_video(mp_image, frame_timestamp_ms)
        frame_timestamp_ms += 33

        gesture_detected = False
        if result.hand_landmarks:
            for hand_landmarks in result.hand_landmarks:
                draw_hand(frame, hand_landmarks)
                if open_hand(hand_landmarks):
                    gesture_detected = True

        if gesture_detected and not salutation_faite:
            print(">> Main detectee ! Scan du visage en cours...")

            faces = detector_yolo.detect_faces(frame)

            if faces:
                x1, y1, x2, y2 = faces[0]

                y1, y2 = max(0, y1), min(frame.shape[0], y2)
                x1, x2 = max(0, x1), min(frame.shape[1], x2)

                face_img = frame[y1:y2, x1:x2]

                if face_img.size > 0:
                    current_emb = recognizer.get_embedding(face_img)
                    name, dist = recognizer.find_best_match(current_emb, persons_db)

                    if name:
                        print(">> Salut {} ! (Distance: {:.2f})".format(name, dist))
                    else:
                        print(">> Nouveau visage detecte.")
                        user_name = input("Entrez votre prenom : ").strip()

                        if user_name:
                            FacesRepository.insert_person(user_name, current_emb)
                            persons_db.append((user_name, current_emb))
                            print("{} enregistre en base de donnees.".format(user_name))
            else:
                print("[WARN] Main vue, mais YOLO ne detecte aucun visage.")

            salutation_faite = True

        if not gesture_detected:
            salutation_faite = False

        cv2.imshow("Systeme Vision - Nao Autisme", frame)
        if cv2.waitKey(1) & 0xFF == 27: break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
