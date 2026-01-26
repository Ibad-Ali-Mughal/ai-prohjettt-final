# import cv2
# import numpy as np

# def detect_indicator(frame, box):
#     x1, y1, x2, y2 = box
#     roi = frame[y1:y2, x1:x2]

#     hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

#     yellow_mask = cv2.inRange(
#         hsv,
#         (15, 80, 80),
#         (35, 255, 255)
#     )

#     yellow_pixels = cv2.countNonZero(yellow_mask)

#     if yellow_pixels > 250:
#         return 1  # indicator used

#     return 0  # indicator not used

# import cv2
# import numpy as np

# def detect_indicator(frame, box):
#     x1, y1, x2, y2 = box
#     roi = frame[y1:y2, x1:x2]

#     if roi.size == 0:
#         return 0

#     hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

#     yellow_mask = cv2.inRange(
#         hsv,
#         (15, 80, 80),
#         (35, 255, 255)
#     )

#     if cv2.countNonZero(yellow_mask) > 300:
#         return 1

#     return 0
                 
import cv2
import numpy as np

def detect_indicator(frame, box):
    """
    Returns:
        1 = indicator likely ON
        0 = no indicator
    """

    x1, y1, x2, y2 = box

    h, w = frame.shape[:2]

    # Expand box slightly
    x1 = max(0, x1 - 10)
    y1 = max(0, y1 - 10)
    x2 = min(w, x2 + 10)
    y2 = min(h, y2 + 10)

    roi = frame[y1:y2, x1:x2]

    if roi.size == 0:
        return 0

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # Narrow yellow range (indicator only)
    yellow_mask = cv2.inRange(
        hsv,
        (18, 120, 150),
        (32, 255, 255)
    )

    # Remove noise
    kernel = np.ones((3, 3), np.uint8)
    yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, kernel)

    yellow_pixels = cv2.countNonZero(yellow_mask)
    area = roi.shape[0] * roi.shape[1]

    # Indicator must be small but bright
    if 0.002 * area < yellow_pixels < 0.05 * area:
        return 1

    return 0
