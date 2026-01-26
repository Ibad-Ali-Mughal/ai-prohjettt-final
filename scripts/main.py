
# import cv2
# import numpy as np
# import pickle
# from ultralytics import YOLO

# from detect_helmet import detect_helmet
# from detect_lane import detect_lane_violation
# from detect_indicator import detect_indicator


# # ----------------------------
# # Load models
# # ----------------------------
# vehicle_model = YOLO("models/yolov8_vehicle.pt")

# with open("models/ml_model.pkl", "rb") as f:
#     fine_model = pickle.load(f)

# # ----------------------------
# # Video input
# # ----------------------------
# cap = cv2.VideoCapture("data/videos/demo.mp4")

# frame_count = 0

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break

#     frame_count += 1
#     lane_violation = detect_lane_violation(frame)

#     results = vehicle_model(frame, verbose=False)[0]

#     for box in results.boxes:
#         cls = int(box.cls[0])
#         x1, y1, x2, y2 = map(int, box.xyxy[0])

#         # bike=0, car=1
#         vehicle_type = 0 if cls == 2 else 1

#         speed = np.random.randint(40, 120)
#         road_priority = 1

#         helmet_violation = 0
#         if vehicle_type == 0:
#             helmet_violation = detect_helmet(frame, (x1, y1, x2, y2))

#         indicator_violation = detect_indicator(frame, (x1, y1, x2, y2))

#         data = np.array([[
#             vehicle_type,
#             speed,
#             road_priority,
#             lane_violation,
#             helmet_violation
#         ]])

#         fine = int(fine_model.predict(data)[0])

#         print("🚨 VIOLATION DETECTED")
#         print(f"Frame            : {frame_count}")
#         print(f"Vehicle Type     : {'Bike' if vehicle_type==0 else 'Car'}")
#         print(f"Helmet Violation : {'YES' if helmet_violation else 'NO'}")
#         print(f"Lane Violation   : {'YES' if lane_violation else 'NO'}")
#         print(f"Indicator Issue  : {'YES' if indicator_violation else 'NO'}")
#         print(f"Predicted Fine   : {fine}")
#         print("-" * 40)

# cap.release()
# print("✅ Video processing finished")










# import cv2
# import numpy as np
# import pickle
# import csv
# import os
# from ultralytics import YOLO

# from detect_helmet import detect_helmet
# from detect_lane import detect_lane_violation
# from detect_indicator import detect_indicator

# # ----------------------------
# # Load models
# # ----------------------------
# vehicle_model = YOLO("models/yolov8_vehicle.pt")

# with open("models/ml_model.pkl", "rb") as f:
#     fine_model = pickle.load(f)

# # ----------------------------
# # CSV setup
# # ----------------------------
# csv_path = "violations.csv"
# file_exists = os.path.isfile(csv_path)

# csv_file = open(csv_path, mode="a", newline="")
# csv_writer = csv.writer(csv_file)

# if not file_exists:
#     csv_writer.writerow([
#         "Frame",
#         "VehicleType",
#         "Speed",
#         "HelmetViolation",
#         "LaneViolation",
#         "IndicatorViolation",
#         "PredictedFine"
#     ])

# # ----------------------------
# # Video input
# # ----------------------------
# cap = cv2.VideoCapture("data/videos/demo.mp4")
# frame_count = 0

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break

#     frame_count += 1
#     lane_violation = detect_lane_violation(frame)

#     results = vehicle_model(frame, verbose=False)[0]

#     for box in results.boxes:
#         cls = int(box.cls[0])
#         x1, y1, x2, y2 = map(int, box.xyxy[0])

#         # YOLO: motorcycle=3, car=2 (depends on model)
#         vehicle_type = "Bike" if cls == 3 else "Car"

#         speed = np.random.randint(40, 120)
#         road_priority = 1

#         helmet_violation = 0
#         if vehicle_type == "Bike":
#             helmet_violation = detect_helmet(frame)

#         indicator_violation = detect_indicator(frame, (x1, y1, x2, y2))

#         data = np.array([[ 
#             0 if vehicle_type == "Bike" else 1,
#             speed,
#             road_priority,
#             lane_violation,
#             helmet_violation
#         ]])

#         fine = int(fine_model.predict(data)[0])

#         # ----------------------------
#         # Draw bounding box
#         # ----------------------------
#         color = (0, 0, 255) if helmet_violation else (0, 255, 0)
#         cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

#         label = f"{vehicle_type} | Fine: {fine}"
#         cv2.putText(frame, label, (x1, y1 - 10),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

#         # ----------------------------
#         # Console output
#         # ----------------------------
#         print("🚨 VIOLATION DETECTED")
#         print(f"Frame            : {frame_count}")
#         print(f"Vehicle Type     : {vehicle_type}")
#         print(f"Helmet Violation : {'YES' if helmet_violation else 'NO'}")
#         print(f"Lane Violation   : {'YES' if lane_violation else 'NO'}")
#         print(f"Indicator Issue  : {'YES' if indicator_violation else 'NO'}")
#         print(f"Predicted Fine   : {fine}")
#         print("-" * 40)

#         # ----------------------------
#         # Save to CSV
#         # ----------------------------
#         csv_writer.writerow([
#             frame_count,
#             vehicle_type,
#             speed,
#             helmet_violation,
#             lane_violation,
#             indicator_violation,
#             fine
#         ])

#     # ----------------------------
#     # Live video preview
#     # ----------------------------
#     cv2.imshow("AI Traffic Monitoring System", frame)

#     if cv2.waitKey(1) & 0xFF == ord("q"):
#         break

# cap.release()
# csv_file.close()
# cv2.destroyAllWindows()
# print("✅ Video processing finished")

import cv2
import numpy as np
import os
import csv
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from ultralytics import YOLO

from detect_helmet import detect_helmet
from detect_lane import detect_lane_violation
from detect_indicator import detect_indicator

# ----------------------------
# CONFIG
# ----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEED_LIMIT = 60

EVIDENCE_DIR = os.path.join(BASE_DIR, "evidence")
os.makedirs(EVIDENCE_DIR, exist_ok=True)

CSV_PATH = os.path.join(BASE_DIR, "violations.csv")

# ----------------------------
# CSV setup
# ----------------------------
csv_exists = os.path.isfile(CSV_PATH)
csv_file = open(CSV_PATH, "a", newline="", encoding="utf-8")
csv_writer = csv.writer(csv_file)

if not csv_exists:
    csv_writer.writerow([
        "Frame",
        "VehicleType",
        "Speed",
        "HelmetViolation",
        "OverspeedViolation",
        "IndicatorViolation",
        "LaneExists",
        "ViolationType"
    ])

# ----------------------------
# Load model
# ----------------------------
vehicle_model = YOLO(os.path.join(BASE_DIR, "models", "yolov8n.pt"))

# ----------------------------
# GUI setup
# ----------------------------
root = tk.Tk()
root.title("AI Traffic Violation Detection")
root.geometry("1200x720")

video_label = tk.Label(root)
video_label.pack(side=tk.LEFT, padx=10, pady=10)

info_label = tk.Label(root, text="Status: Idle", fg="blue", font=("Arial", 12))
info_label.pack()

details_label = tk.Label(
    root,
    text="No violation",
    fg="green",
    font=("Arial", 11),
    justify="left"
)
details_label.pack(pady=5)

# ----------------------------
# State
# ----------------------------
cap = None
running = False
paused = False
frame_count = 0

# ----------------------------
# Controls
# ----------------------------
def start_video():
    global cap, running, paused, frame_count

    path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi")])
    if not path:
        return

    if cap:
        cap.release()

    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        info_label.config(text="Failed to open video", fg="red")
        return

    running = True
    paused = False
    frame_count = 0
    info_label.config(text="Running", fg="green")
    process_frame()

def pause_video():
    global paused
    paused = True
    info_label.config(text="Paused", fg="orange")

def resume_video():
    global paused
    if paused:
        paused = False
        info_label.config(text="Running", fg="green")
        process_frame()

# ----------------------------
# Main loop
# ----------------------------
def process_frame():
    global frame_count

    if not running or paused or not cap:
        return

    ret, frame = cap.read()
    if not ret:
        info_label.config(text="Video Finished", fg="red")
        return

    frame_count += 1
    display = frame.copy()

    H, W, _ = frame.shape
    lane_exists = detect_lane_violation(frame)

    results = vehicle_model(frame, conf=0.4, verbose=False)[0]

    violation_text = "No violation"
    violation_color = "green"

    for box in results.boxes:
        cls = int(box.cls[0])
        label = vehicle_model.names[cls]

        # ----------------------------
        # Vehicle type
        # ----------------------------
        if label == "motorcycle":
            vehicle_type = "Bike"
        elif label in ["car", "bus", "truck"]:
            vehicle_type = "Car"
        else:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        helmet_violation = 0

        # ----------------------------
        # Helmet detection (UNCHANGED)
        # ----------------------------
        if vehicle_type == "Bike":
            box_h = y2 - y1
            box_w = x2 - x1

            cx1 = max(x1 - int(0.20 * box_w), 0)
            cx2 = min(x2 + int(0.20 * box_w), W)
            cy1 = max(y1 - int(0.45 * box_h), 0)
            cy2 = min(y1 + int(0.20 * box_h), H)

            rider_crop = frame[cy1:cy2, cx1:cx2]
            helmet_violation, helmet_boxes = detect_helmet(rider_crop)

            for hcls, hx1, hy1, hx2, hy2 in helmet_boxes:
                color = (0, 255, 0) if hcls == 0 else (0, 0, 255)
                cv2.rectangle(
                    display,
                    (cx1 + hx1, cy1 + hy1),
                    (cx1 + hx2, cy1 + hy2),
                    color,
                    2
                )

        # ----------------------------
        # Overspeed
        # ----------------------------
        speed = np.random.randint(40, 120)
        overspeed_violation = speed > SPEED_LIMIT

        # ----------------------------
        # Indicator (ONLY if lane exists)
        # ----------------------------
        indicator_on = detect_indicator(frame, (x1, y1, x2, y2))
        indicator_violation = 1 if (lane_exists == 1 and indicator_on == 0) else 0

        # ----------------------------
        # Build violation list
        # ----------------------------
        violations = []

        if helmet_violation:
            violations.append("NO_HELMET")
        if overspeed_violation:
            violations.append("OVERSPEED")
        if indicator_violation:
            violations.append("NO_INDICATOR")

        final_violation = len(violations) > 0
        violation_type = " + ".join(violations) if violations else "NONE"

        # ----------------------------
        # Draw box
        # ----------------------------
        box_color = (0, 0, 255) if final_violation else (0, 255, 0)
        cv2.rectangle(display, (x1, y1), (x2, y2), box_color, 2)

        if final_violation:
            violation_text = (
                f"{vehicle_type}\n"
                f"Speed: {speed} km/h\n"
                f"Violations:\n- " + "\n- ".join(violations)
            )
            violation_color = "red"

            # ----------------------------
            # Save evidence
            # ----------------------------
            img_name = f"frame_{frame_count}_{vehicle_type}_{violation_type}.jpg"
            cv2.imwrite(os.path.join(EVIDENCE_DIR, img_name), display)

            # ----------------------------
            # Write CSV
            # ----------------------------
            csv_writer.writerow([
                frame_count,
                vehicle_type,
                speed,
                helmet_violation,
                int(overspeed_violation),
                indicator_violation,
                lane_exists,
                violation_type
            ])
            csv_file.flush()

    details_label.config(text=violation_text, fg=violation_color)

    rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb).resize((880, 520))
    imgtk = ImageTk.PhotoImage(img)

    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)

    root.after(35, process_frame)

# ----------------------------
# Buttons
# ----------------------------
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Start Video", width=15, command=start_video).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Pause", width=15, command=pause_video).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Resume", width=15, command=resume_video).pack(side=tk.LEFT, padx=5)

# ----------------------------
# Cleanup
# ----------------------------
def on_close():
    global running
    running = False
    if cap:
        cap.release()
    csv_file.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()