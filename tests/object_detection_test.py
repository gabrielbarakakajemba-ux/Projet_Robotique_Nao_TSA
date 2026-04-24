from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # verbose=False → plus de logs YOLO dans le terminal
    results = model(frame, conf=0.5, verbose=False)

    bottle_detected = False

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]

            if label == "bottle":
                bottle_detected = True

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "Bottle", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    if bottle_detected:
        print("Bouteille détectée")

    cv2.imshow("Bottle Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC pour quitter
        break

cap.release()
cv2.destroyAllWindows()
print("\nArrêt du programme")