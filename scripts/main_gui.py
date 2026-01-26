# import cv2
# import numpy as np
# import pickle
# import csv
# import os
# import tkinter as tk
# from tkinter import filedialog
# from PIL import Image, ImageTk
# from ultralytics import YOLO

# from detect_helmet import detect_helmet
# from detect_lane import detect_lane_violation
# from detect_indicator import detect_indicator

# # ----------------------------
# # Base directory (project root)
# # ----------------------------
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# # ----------------------------
# # Load models
# # ----------------------------
# vehicle_model = YOLO(os.path.join(BASE_DIR, "models", "yolov8_vehicle.pt"))

# with open(os.path.join(BASE_DIR, "models", "ml_model.pkl"), "rb") as f:
#     fine_model = pickle.load(f)

# # ----------------------------
# # CSV setup
# # ----------------------------
# csv_path = os.path.join(BASE_DIR, "violations.csv")
# file_exists = os.path.isfile(csv_path)

# csv_file = open(csv_path, mode="a", newline="", encoding="utf-8")
# csv_writer = csv.writer(csv_file)

# if not file_exists:
#     csv_writer.writerow([
#         "Frame", "VehicleType", "Speed",
#         "HelmetViolation", "LaneViolation",
#         "IndicatorViolation", "PredictedFine"
#     ])

# # ----------------------------
# # GUI Setup
# # ----------------------------
# root = tk.Tk()
# root.title("AI Traffic Monitoring System")
# root.geometry("1100x700")

# video_label = tk.Label(root)
# video_label.pack(pady=10)

# info_label = tk.Label(root, text="Status: Idle", font=("Arial", 12), fg="blue")
# info_label.pack()

# cap = None
# running = False
# frame_count = 0

# # ----------------------------
# # Start Video
# # ----------------------------
# def start_video():
#     global cap, running, frame_count

#     if running:
#         return

#     path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi")])
#     if not path:
#         return

#     if cap:
#         cap.release()

#     cap = cv2.VideoCapture(path)
#     if not cap.isOpened():
#         info_label.config(text="Status: Failed to open video", fg="red")
#         return

#     running = True
#     frame_count = 0
#     info_label.config(text="Status: Running", fg="green")
#     process_frame()

# # ----------------------------
# # Stop Video
# # ----------------------------
# def stop_video():
#     global running
#     running = False
#     info_label.config(text="Status: Stopped", fg="red")

# # ----------------------------
# # Main Processing Loop
# # ----------------------------
# def process_frame():
#     global frame_count

#     if not running or not cap or not cap.isOpened():
#         return

#     ret, frame = cap.read()
#     if not ret:
#         stop_video()
#         return

#     frame_count += 1

#     # Lane violation for the frame
#     lane_violation = detect_lane_violation(frame)

#     results = vehicle_model(frame, verbose=False)[0]

#     for box in results.boxes:
#         cls = int(box.cls[0])
#         x1, y1, x2, y2 = map(int, box.xyxy[0])

#         # Vehicle type detection (update according to your model)
#         if cls == 3:
#             vehicle_type = "Bike"
#             # Crop the bike region for helmet detection
#             helmet_violation = detect_helmet(frame[y1:y2, x1:x2])
#         elif cls in [2, 5, 7]:
#             vehicle_type = "Car"
#             helmet_violation = 0
#         else:
#             continue  # Skip other classes

#         speed = np.random.randint(40, 120)
#         indicator_violation = detect_indicator(frame, (x1, y1, x2, y2))

#         data = np.array([[0 if vehicle_type == "Bike" else 1,
#                           speed, 1, lane_violation, helmet_violation]])

#         fine = int(fine_model.predict(data)[0])

#         violation = helmet_violation or lane_violation or indicator_violation
#         color = (0, 0, 255) if violation else (0, 255, 0)

#         cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
#         cv2.putText(frame, f"{vehicle_type} | Fine: {fine}",
#                     (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

#         csv_writer.writerow([
#             frame_count, vehicle_type, speed,
#             helmet_violation, lane_violation,
#             indicator_violation, fine
#         ])
#         csv_file.flush()

#     # Convert frame for Tkinter
#     frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     img = Image.fromarray(frame_rgb).resize((900, 500), Image.LANCZOS)
#     imgtk = ImageTk.PhotoImage(image=img)

#     video_label.imgtk = imgtk
#     video_label.configure(image=imgtk)

#     root.after(25, process_frame)

# # ----------------------------
# # Buttons
# # ----------------------------
# btn_frame = tk.Frame(root)
# btn_frame.pack(pady=10)

# tk.Button(btn_frame, text="Start Video", width=15, command=start_video).pack(side=tk.LEFT, padx=10)
# tk.Button(btn_frame, text="Stop", width=15, command=stop_video).pack(side=tk.LEFT, padx=10)

# # ----------------------------
# # Exit cleanup
# # ----------------------------
# def on_close():
#     global running
#     running = False
#     if cap:
#         cap.release()
#     csv_file.close()
#     root.destroy()

# root.protocol("WM_DELETE_WINDOW", on_close)
# root.mainloop()

import cv2
import os
import csv
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from ultralytics import YOLO
from datetime import datetime

from detect_helmet import detect_helmet
from detect_lane import detect_lane_violation
from detect_indicator import detect_indicator
from generate_challan import generate_challan

# ================= CONFIG =================
SPEED_LIMIT = 60
FPS = 30
PIXELS_PER_METER = 40

EVIDENCE_DIR = "evidence"
CHALLAN_DIR = "challans"
os.makedirs(EVIDENCE_DIR, exist_ok=True)
os.makedirs(CHALLAN_DIR, exist_ok=True)

CSV_PATH = "violations.csv"

# ================= CSV =================
csv_exists = os.path.isfile(CSV_PATH)
csv_file = open(CSV_PATH, "a", newline="", encoding="utf-8")
csv_writer = csv.writer(csv_file)

if not csv_exists:
    csv_writer.writerow([
        "DateTime", "VehicleID", "VehicleType",
        "Speed", "Violations", "TotalFine", "EvidenceImage"
    ])

# ================= HELPERS =================
def estimate_speed(prev_y, curr_y):
    if prev_y is None:
        return None

    delta = abs(curr_y - prev_y)
    if delta < 3:
        return None

    meters = delta / PIXELS_PER_METER
    speed = meters * FPS * 3.6

    if speed > 180:
        return None

    return int(speed)

def calculate_fine(violations):
    fine = 0
    if "NO_HELMET" in violations:
        fine += 2000
    if "OVERSPEED" in violations:
        fine += 1500
    if "NO_INDICATOR" in violations:
        fine += 500
    return fine

# ================= MODEL =================
vehicle_model = YOLO("models/yolov8n.pt")

# ================= CONTROLS =================
def start_video():
    global cap, running, paused
    path = filedialog.askopenfilename()
    if not path:
        return
    cap = cv2.VideoCapture(path)
    running = True
    paused = False
    process_frame()

def pause_video():
    global paused
    paused = True

def resume_video():
    global paused
    paused = False
    process_frame()

root = tk.Tk()
root.title("AI Traffic Violation Detection")
root.geometry("1500x820")
root.configure(bg="#f2f2f2")

# ---------- MAIN CONTAINER ----------
main_frame = tk.Frame(root, bg="#f2f2f2")
main_frame.pack(fill="both", expand=True, padx=12, pady=12)

# ---------- VIDEO PANEL ----------
video_frame = tk.Frame(main_frame, bg="black", bd=3, relief="ridge")
video_frame.pack(side="left", padx=10, pady=10)

video_label = tk.Label(video_frame, bg="black")
video_label.pack()

# ---------- RIGHT PANEL ----------
right_panel = tk.Frame(main_frame, width=360, bg="white", bd=3, relief="ridge")
right_panel.pack(side="right", fill="y", padx=10, pady=10)

# ---------- TITLE ----------
tk.Label(
    right_panel,
    text="🚦 Traffic Violation",
    font=("Arial", 18, "bold"),
    bg="white",
    fg="#222"
).pack(pady=(15, 10))

# ---------- DETAILS ----------
details_label = tk.Label(
    right_panel,
    text="No violation detected",
    fg="green",
    bg="white",
    font=("Arial", 12),
    justify="left",
    wraplength=320
)
details_label.pack(padx=15, pady=15)

# ---------- DIVIDER ----------
tk.Frame(right_panel, height=2, bg="#ddd").pack(fill="x", padx=20, pady=10)

# ---------- BUTTON STYLE ----------
btn_style = {
    "font": ("Arial", 12, "bold"),
    "width": 18,
    "bd": 0,
    "cursor": "hand2",
    "pady": 8
}

tk.Button(
    right_panel, text="▶ Start",
    bg="#4CAF50", fg="white",
    command=start_video, **btn_style
).pack(pady=8)

tk.Button(
    right_panel, text="⏸ Pause",
    bg="#FF9800", fg="white",
    command=pause_video, **btn_style
).pack(pady=8)

tk.Button(
    right_panel, text="⏵ Resume",
    bg="#2196F3", fg="white",
    command=resume_video, **btn_style
).pack(pady=8)

# ================= STATE =================
cap = None
running = False
paused = False

prev_positions = {}
speed_history = {}

vehicle_types = {}
vehicle_max_speed = {}
vehicle_violations = {}
vehicle_last_frame = {}
issued_challans = set()

# ================= CONTROLS =================
# def start_video():
#     global cap, running, paused
#     path = filedialog.askopenfilename()
#     if not path:
#         return
#     cap = cv2.VideoCapture(path)
#     running = True
#     paused = False
#     process_frame()

# def pause_video():
#     global paused
#     paused = True

# def resume_video():
#     global paused
#     paused = False
#     process_frame()

# ================= MAIN LOOP =================
def process_frame():
    if not running or paused or cap is None:
        return

    ret, frame = cap.read()
    if not ret:
        return

    display = frame.copy()
    lane_exists = detect_lane_violation(frame)

    results = vehicle_model.track(
        frame, conf=0.4, persist=True, verbose=False
    )[0]

    for box in results.boxes:
        if box.id is None:
            continue

        tid = int(box.id[0])
        label = vehicle_model.names[int(box.cls[0])]

        if label == "motorcycle":
            vtype = "Bike"
        elif label in ["car", "bus", "truck"]:
            vtype = "Car"
        else:
            continue

        vehicle_types[tid] = vtype

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cy = (y1 + y2) // 2

        sp = estimate_speed(prev_positions.get(tid), cy)
        prev_positions[tid] = cy

        if sp is not None:
            speed_history.setdefault(tid, []).append(sp)
            if len(speed_history[tid]) > 6:
                speed_history[tid].pop(0)

        if tid in speed_history and len(speed_history[tid]) >= 5:
            avg_speed = int(sum(speed_history[tid]) / len(speed_history[tid]))
            vehicle_max_speed[tid] = max(
                vehicle_max_speed.get(tid, 0), avg_speed
            )

            if avg_speed > SPEED_LIMIT:
                vehicle_violations.setdefault(tid, set()).add("OVERSPEED")

        # -------- HELMET --------
        if vtype == "Bike":
            crop = frame[max(y1-80,0):y1+50, max(x1-40,0):x2+40]
            helmet_violation, _ = detect_helmet(crop)
            if helmet_violation:
                vehicle_violations.setdefault(tid, set()).add("NO_HELMET")

        # -------- INDICATOR --------
        if lane_exists and not detect_indicator(frame, (x1, y1, x2, y2)):
            vehicle_violations.setdefault(tid, set()).add("NO_INDICATOR")

        # -------- SAVE ZOOMED IMAGE --------
        if tid in vehicle_violations:
            box_w = x2 - x1
            box_h = y2 - y1

            pad_x = int(0.4 * box_w)
            pad_y = int(0.6 * box_h)

            cx1 = max(0, x1 - pad_x)
            cy1 = max(0, y1 - pad_y)
            cx2 = min(frame.shape[1], x2 + pad_x)
            cy2 = min(frame.shape[0], y2 + pad_y)

            vehicle_last_frame[tid] = frame[cy1:cy2, cx1:cx2].copy()
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 0, 255), 2)

    # ================= ISSUE CHALLANS =================
    for tid in list(vehicle_violations.keys()):
        if tid in issued_challans:
            continue
        if tid not in vehicle_max_speed:
            continue
        if tid not in vehicle_last_frame:
            continue

        violations = list(vehicle_violations[tid])
        fine = calculate_fine(violations)
        now = datetime.now()

        img_name = f"{now:%Y%m%d_%H%M%S}_ID{tid}.jpg"
        img_path = os.path.join(EVIDENCE_DIR, img_name)
        cv2.imwrite(img_path, vehicle_last_frame[tid])

        csv_writer.writerow([
            now.strftime("%Y-%m-%d %H:%M:%S"),
            tid,
            vehicle_types.get(tid),
            vehicle_max_speed[tid],
            " + ".join(violations),
            fine,
            img_name
        ])
        csv_file.flush()

        generate_challan(
            os.path.join(CHALLAN_DIR, f"{now:%Y%m%d_%H%M%S}_ID{tid}.pdf"),
            {
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"),
                "vehicle_id": tid,
                "vehicle_type": vehicle_types.get(tid),
                "speed": vehicle_max_speed[tid],
                "violations": violations,
                "total_fine": fine,
                "image_path": img_path
            }
        )

        issued_challans.add(tid)

        details_label.config(
            text=(
                f"Vehicle ID: {tid}\n"
                f"Type: {vehicle_types.get(tid)}\n"
                f"Speed: {vehicle_max_speed[tid]} km/h\n\n"
                f"Violations:\n- " + "\n- ".join(violations) +
                f"\n\nTOTAL FINE: Rs.{fine}"
            ),
            fg="red"
        )

    # img = ImageTk.PhotoImage(
    #     Image.fromarray(cv2.cvtColor(display, cv2.COLOR_BGR2RGB)).resize((880, 520))
    # )
    # video_label.configure(image=img)
    # video_label.image = img
    rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb)
    img = img.resize((1040, 600))
    imgtk = ImageTk.PhotoImage(img)

    video_label.configure(image=imgtk)
    video_label.image = imgtk

    root.after(30, process_frame)


# ================= BUTTONS =================
# tk.Button(root, text="Start", width=12, command=start_video).pack()
# tk.Button(root, text="Pause", width=12, command=pause_video).pack()
# tk.Button(root, text="Resume", width=12, command=resume_video).pack()

root.mainloop()

# import cv2
# import numpy as np
# import os
# import tkinter as tk
# from tkinter import filedialog
# from PIL import Image, ImageTk
# from ultralytics import YOLO

# from detect_helmet import detect_helmet
# from detect_lane import detect_lane_violation
# from detect_indicator import detect_indicator

# # ----------------------------
# # CONFIG
# # ----------------------------
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# SPEED_LIMIT = 60

# # ----------------------------
# # Load models
# # ----------------------------
# vehicle_model = YOLO(os.path.join(BASE_DIR, "models", "yolov8n.pt"))

# # ----------------------------
# # GUI setup
# # ----------------------------
# root = tk.Tk()
# root.title("AI Traffic Violation Detection")
# root.geometry("1200x720")

# video_label = tk.Label(root)
# video_label.pack(side=tk.LEFT, padx=10, pady=10)

# info_label = tk.Label(root, text="Status: Idle", fg="blue", font=("Arial", 12))
# info_label.pack()

# details_label = tk.Label(
#     root,
#     text="No violation",
#     fg="green",
#     font=("Arial", 11),
#     justify="left"
# )
# details_label.pack(pady=5)

# # ----------------------------
# # State variables
# # ----------------------------
# cap = None
# running = False
# paused = False
# frame_count = 0

# # ----------------------------
# # Start video
# # ----------------------------
# def start_video():
#     global cap, running, paused, frame_count

#     path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi")])
#     if not path:
#         return

#     if cap:
#         cap.release()

#     cap = cv2.VideoCapture(path)
#     if not cap.isOpened():
#         info_label.config(text="Failed to open video", fg="red")
#         return

#     running = True
#     paused = False
#     frame_count = 0
#     info_label.config(text="Running", fg="green")
#     process_frame()

# # ----------------------------
# # Pause / Resume
# # ----------------------------
# def pause_video():
#     global paused
#     paused = True
#     info_label.config(text="Paused", fg="orange")

# def resume_video():
#     global paused
#     if paused:
#         paused = False
#         info_label.config(text="Running", fg="green")
#         process_frame()

# # ----------------------------
# # Main processing loop
# # ----------------------------
# def process_frame():
#     global frame_count

#     if not running or paused or not cap:
#         return

#     ret, frame = cap.read()
#     if not ret:
#         info_label.config(text="Video Finished", fg="red")
#         return

#     frame_count += 1
#     display = frame.copy()

#     H, W, _ = frame.shape

#     lane_exists = detect_lane_violation(frame)

#     results = vehicle_model(frame, conf=0.4, verbose=False)[0]

#     violation_text = "No violation"
#     violation_color = "green"

#     for box in results.boxes:
#         cls = int(box.cls[0])
#         label = vehicle_model.names[cls]

#         if label != "motorcycle":
#             continue

#         x1, y1, x2, y2 = map(int, box.xyxy[0])

#         # ----------------------------
#         # Helmet ROI (SAME AS MAIN)
#         # ----------------------------
#         box_h = y2 - y1
#         box_w = x2 - x1

#         cx1 = max(x1 - int(0.20 * box_w), 0)
#         cx2 = min(x2 + int(0.20 * box_w), W)
#         cy1 = max(y1 - int(0.45 * box_h), 0)
#         cy2 = min(y1 + int(0.20 * box_h), H)

#         rider_crop = frame[cy1:cy2, cx1:cx2]

#         cv2.rectangle(display, (cx1, cy1), (cx2, cy2), (255, 255, 0), 2)

#         helmet_violation, helmet_boxes = detect_helmet(rider_crop)

#         for hcls, hx1, hy1, hx2, hy2 in helmet_boxes:
#             color = (0, 255, 0) if hcls == 0 else (0, 0, 255)
#             text = "Helmet" if hcls == 0 else "No Helmet"

#             cv2.rectangle(
#                 display,
#                 (cx1 + hx1, cy1 + hy1),
#                 (cx1 + hx2, cy1 + hy2),
#                 color,
#                 2
#             )
#             cv2.putText(
#                 display,
#                 text,
#                 (cx1 + hx1, cy1 + hy1 - 5),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.6,
#                 color,
#                 2
#             )

#         # ----------------------------
#         # Other violations
#         # ----------------------------
#         speed = np.random.randint(40, 120)
#         overspeed_violation = speed > SPEED_LIMIT

#         indicator_on = detect_indicator(frame, (x1, y1, x2, y2))
#         indicator_violation = not indicator_on

#         lane_violation = lane_exists

#         final_violation = (
#             helmet_violation or
#             overspeed_violation or
#             lane_violation or
#             indicator_violation
#         )

#         box_color = (0, 0, 255) if final_violation else (0, 255, 0)
#         cv2.rectangle(display, (x1, y1), (x2, y2), box_color, 2)

#         if final_violation:
#             reasons = []
#             if helmet_violation:
#                 reasons.append("No Helmet")
#             if overspeed_violation:
#                 reasons.append(f"Overspeed {speed}")
#             if indicator_violation:
#                 reasons.append("No Indicator")
#             if lane_violation:
#                 reasons.append("Lane")

#             violation_text = (
#                 f"Bike\n"
#                 f"Speed: {speed} km/h\n"
#                 f"Violations:\n- " + "\n- ".join(reasons)
#             )
#             violation_color = "red"

#     # ----------------------------
#     # Update GUI
#     # ----------------------------
#     details_label.config(text=violation_text, fg=violation_color)

#     rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
#     img = Image.fromarray(rgb).resize((880, 520))
#     imgtk = ImageTk.PhotoImage(img)

#     video_label.imgtk = imgtk
#     video_label.configure(image=imgtk)

#     root.after(35, process_frame)

# # ----------------------------
# # Buttons
# # ----------------------------
# btn_frame = tk.Frame(root)
# btn_frame.pack(pady=10)

# tk.Button(btn_frame, text="Start Video", width=15, command=start_video).pack(side=tk.LEFT, padx=5)
# tk.Button(btn_frame, text="Pause", width=15, command=pause_video).pack(side=tk.LEFT, padx=5)
# tk.Button(btn_frame, text="Resume", width=15, command=resume_video).pack(side=tk.LEFT, padx=5)

# # ----------------------------
# # Cleanup
# # ----------------------------
# def on_close():
#     global running
#     running = False
#     if cap:
#         cap.release()
#     root.destroy()

# root.protocol("WM_DELETE_WINDOW", on_close)
# root.mainloop()
