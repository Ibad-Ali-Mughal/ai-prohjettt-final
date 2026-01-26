from ultralytics import YOLO
import cv2

model = YOLO("models/helmet_9.pt")

img = cv2.imread("data/helmet_images/1.jpg")  # <-- change name
results = model(img, conf=0.1, imgsz=640)[0]

print("Boxes detected:", len(results.boxes))
