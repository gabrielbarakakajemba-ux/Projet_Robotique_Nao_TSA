# -*- coding: utf-8 -*-
import sys
import os

target_folder = "/home/mr-kajemba/Nao_Autisme/modules/perception/vision/face_recognition/detection"

if target_folder not in sys.path:
    sys.path.insert(0, target_folder)

# 2. Importation directe du fichier
try:
    # On importe directement le NOM DU FICHIER car on est "dedans" grâce au sys.path
    import yolo_detection
    # Si ta classe s'appelle YoloDetector :
    from yolo_detection import YOLODetector
    print("[SUCCESS] YoloDetector est enfin chargé via import direct !")
except ImportError as e:
    print("[ERREUR] Échec de l'importation directe.")
    print("Détail : " + str(e))
    sys.exit(1)

import cv2

def test_vision():
    try:
        # Initialisation du détecteur
        detector = YOLODetector() 
        print("[OK] Modèle YOLO chargé en mémoire.")
        
        # Test rapide sur la webcam du PC
        cap = cv2.VideoCapture(0)
        print("Test webcam lancé... Appuyez sur 'q' pour quitter.")
        
        while True:
            ret, frame = cap.read()
            if not ret: break
            
            # Utilise ta méthode de détection
            faces = detector.detect_faces(frame) 
            
            for face in faces:
                # Adapte selon ce que retourne ton objet face (x1, y1, x2, y2)
                cv2.rectangle(frame, (face[0], face[1]), (face[2], face[3]), (0, 255, 0), 2)

            cv2.imshow("Test Vision PC", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
    except Exception as e:
        print("[ERREUR] Pendant le test : {}".format(e))

if __name__ == "__main__":
    test_vision()