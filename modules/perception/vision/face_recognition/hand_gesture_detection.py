import cv2
import urllib.request
import os
import ssl
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

model_url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
model_path = "hand_landmarker.task"


def create_hand_detector():
    if not os.path.exists(model_path):
        print("Telechargement du modele MediaPipe...")
        ctx = ssl._create_unverified_context()
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(model_url, model_path)
        print("Modele telecharge!")

    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )

    return vision.HandLandmarker.create_from_options(options)


def open_hand(landmarks):
    finger_tips = [8, 12, 16, 20]
    finger_mcps = [5, 9, 13, 17]

    doigts_leves = 0
    for tip, mcp in zip(finger_tips, finger_mcps):
        if landmarks[tip].y < landmarks[mcp].y:
            doigts_leves += 1

    if abs(landmarks[4].x - landmarks[2].x) > 0.05:
        doigts_leves += 1

    return doigts_leves >= 4


def draw_hand(image, landmarks):
    height, width = image.shape[:2]

    for lm in landmarks:
        x, y = int(lm.x * width), int(lm.y * height)
        cv2.circle(image, (x, y), 4, (0, 255, 0), -1)

    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),
        (0, 5), (5, 6), (6, 7), (7, 8),
        (0, 9), (9, 10), (10, 11), (11, 12),
        (0, 13), (13, 14), (14, 15), (15, 16),
        (0, 17), (17, 18), (18, 19), (19, 20),
        (5, 9), (9, 13), (13, 17)
    ]

    for start_idx, end_idx in connections:
        start = landmarks[start_idx]
        end = landmarks[end_idx]
        pt1 = (int(start.x * width), int(start.y * height))
        pt2 = (int(end.x * width), int(end.y * height))
        cv2.line(image, pt1, pt2, (255, 0, 0), 2)


def main():
    detector = create_hand_detector()
    cap = cv2.VideoCapture(0)
    frame_timestamp_ms = 0

    print("=" * 50)
    print("DETECTION DE MAIN OUVERTE EN MOUVEMENT")
    print("=" * 50)
    print("Instructions:")
    print("- Montrez votre main ouverte devant la camera")
    print("- Bougez-la librement")
    print("- Le message 'MAIN OUVERTE' s'affichera")
    print("- ESC pour quitter")
    print("=" * 50)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        result = detector.detect_for_video(mp_image, frame_timestamp_ms)
        frame_timestamp_ms += 33

        open_hand_detected = False

        if result.hand_landmarks:
            for hand_landmarks in result.hand_landmarks:
                draw_hand(frame, hand_landmarks)
                if open_hand(hand_landmarks):
                    open_hand_detected = True

        if open_hand_detected:
            cv2.putText(frame, "MAIN OUVERTE", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 255, 0), 6)
            print("Main ouverte detectee!")
        elif result.hand_landmarks:
            cv2.putText(frame, "Main fermee", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
        else:
            cv2.putText(frame, "Aucune main", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        cv2.imshow("Detection Main Ouverte", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\nArret du programme")


if __name__ == "__main__":
    main()
