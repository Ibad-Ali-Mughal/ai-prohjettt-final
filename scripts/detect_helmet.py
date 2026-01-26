# import cv2
# from ultralytics import YOLO

# # Load helmet detection model
# helmet_model = YOLO("models/yolov82_helmet.pt")

# # Load video
# video_path = "data/videos/helmet_test.mp4"  # change if needed
# cap = cv2.VideoCapture(video_path)

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break

#     # Run inference
#     results = helmet_model(frame, conf=0.4)

#     for r in results:
#         for box in r.boxes:
#             cls = int(box.cls[0])
#             conf = float(box.conf[0])

#             x1, y1, x2, y2 = map(int, box.xyxy[0])

#             if cls == 1:  # Without Helmet
#                 color = (0, 0, 255)
#                 label = f"NO HELMET {conf:.2f}"
#             else:        # With Helmet
#                 color = (0, 255, 0)
#                 label = f"HELMET {conf:.2f}"

#             cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
#             cv2.putText(
#                 frame, label,
#                 (x1, y1 - 10),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.6,
#                 color,
#                 2
#             )

#     cv2.imshow("Helmet Detection", frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()


# finally used 
# import os
# from ultralytics import YOLO

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# helmet_model_path = os.path.join(BASE_DIR, "models", "yolov82_helmet.pt")

# helmet_model = YOLO(helmet_model_path)

# def detect_helmet(frame):
#     results = helmet_model(frame, conf=0.4)

#     person = False
#     helmet = False

#     for r in results:
#         for box in r.boxes:
#             cls = int(box.cls[0])

#             if cls == 0:   # rider/person
#                 person = True
#             elif cls == 1: # helmet
#                 helmet = True

#     if person and not helmet:
#         return 1   # violation

#     return 0

# last working with gui 
# import os
# from ultralytics import YOLO

# # Go one level up from scripts/ to project root
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# # Correct model path
# model_path = os.path.join(BASE_DIR, "models", "yolov82_helmet.pt")

# # Safety check (recommended)
# if not os.path.exists(model_path):
#     raise FileNotFoundError(f"Helmet model not found at: {model_path}")

# helmet_model = YOLO(model_path)

# def detect_helmet(frame):
#     results = helmet_model(frame, conf=0.4, verbose=False)

#     person = False
#     helmet = False

#     for r in results:
#         for box in r.boxes:
#             cls = int(box.cls[0])
#             if cls == 0:        # person
#                 person = True
#             elif cls == 1:      # helmet
#                 helmet = True

#     return 1 if person and not helmet else 0


# from ultralytics import YOLO
# import os
# import cv2

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# model_path = os.path.join(BASE_DIR, "models", "helmet_9.pt")

# helmet_model = YOLO(model_path)

# def detect_helmet(crop):
#     """
#     Returns:
#         helmet_violation (1 = No Helmet, 0 = With Helmet)
#         boxes = [(cls, x1, y1, x2, y2)]
#     """

#     if crop is None or crop.size == 0:
#         return 0, []

#     # Upscale for better detection
#     crop = cv2.resize(crop, None, fx=2.5, fy=2.5)

#     results = helmet_model(crop, conf=0.2, verbose=False)[0]

#     helmet_violation = 0
#     boxes = []

#     for box in results.boxes:
#         cls = int(box.cls[0])   # 0 = With_Helmet, 1 = Without_Helmet
#         x1, y1, x2, y2 = map(int, box.xyxy[0])
#         boxes.append((cls, x1, y1, x2, y2))

#         if cls == 1:
#             helmet_violation = 1

#     return helmet_violation, boxes


from ultralytics import YOLO
import os
import cv2

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "models", "helmet_9.pt")

helmet_model = YOLO(model_path)

def detect_helmet(crop):
    """
    Returns:
        helmet_violation (1 = No Helmet, 0 = With Helmet)
        boxes = [(cls, x1, y1, x2, y2)]
    """

    if crop is None or crop.size == 0:
        return 0, []

    # Original size
    h0, w0 = crop.shape[:2]

    # Upscale for CCTV
    crop = cv2.resize(
        crop, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_LINEAR
    )

    results = helmet_model(
        crop,
        conf=0.15,      # detect more, filter manually
        iou=0.5,
        verbose=False
    )[0]

    helmet_violation = 0
    boxes = []

    if results.boxes is None:
        return 0, []

    for box in results.boxes:
        cls = int(box.cls.item())   # 0=helmet, 1=no-helmet
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        box_w = x2 - x1
        box_h = y2 - y1

        # ------------------------------------
        # ❌ FILTER 1: remove cap-sized boxes
        # ------------------------------------
        if box_w < 40 or box_h < 30:
            continue

        # ------------------------------------
        # ❌ FILTER 2: helmet must be LOWER
        # ------------------------------------
        center_y = (y1 + y2) // 2
        if center_y < 0.35 * crop.shape[0]:
            continue

        boxes.append((cls, x1, y1, x2, y2))

        if cls == 1:
            helmet_violation = 1

    return helmet_violation, boxes
