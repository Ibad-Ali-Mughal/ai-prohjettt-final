# import cv2
# import numpy as np

# def detect_lane_violation(frame):
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     blur = cv2.GaussianBlur(gray, (5, 5), 0)
#     edges = cv2.Canny(blur, 50, 150)

#     height, width = edges.shape
#     roi = edges[int(height * 0.6):height, :]

#     lines = cv2.HoughLinesP(
#         roi,
#         1,
#         np.pi / 180,
#         threshold=100,
#         minLineLength=100,
#         maxLineGap=50
#     )

#     if lines is None:
#         return 0

#     if len(lines) > 4:
#         return 1

#     return 0


# import cv2
# import numpy as np

# def detect_lane_violation(frame):
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     blur = cv2.GaussianBlur(gray, (5, 5), 0)
#     edges = cv2.Canny(blur, 50, 150)

#     h, w = edges.shape
#     roi = edges[int(h * 0.65):h, :]

#     lines = cv2.HoughLinesP(
#         roi,
#         1,
#         np.pi / 180,
#         threshold=120,
#         minLineLength=120,
#         maxLineGap=40
#     )

#     if lines is None:
#         return 0

#     if len(lines) > 8:   # stricter condition
#         return 1

#     return 0
import cv2
import numpy as np

def detect_lane_violation(frame):
    """
    Returns:
        1 = lane structure exists (violation logic allowed)
        0 = no reliable lane → no violation
    """

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 80, 160)

    h, w = edges.shape

    # Bottom road region only
    roi = edges[int(h * 0.65):h, int(w * 0.30):int(w * 0.70)]

    lines = cv2.HoughLinesP(
        roi,
        rho=1,
        theta=np.pi / 180,
        threshold=150,
        minLineLength=180,
        maxLineGap=40
    )

    if lines is None:
        return 0

    vertical_lines = 0

    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))

        if 65 < angle < 115:
            length = np.hypot(x2 - x1, y2 - y1)
            if length > 150:
                vertical_lines += 1

    # Require strong lane structure
    if vertical_lines >= 3:
        return 1

    return 0


# import cv2
# import numpy as np

# def detect_lane_violation(frame):
#     """
#     Lane violation is detected ONLY if
#     clear lane markings exist.
#     """

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     blur = cv2.GaussianBlur(gray, (5, 5), 0)

#     edges = cv2.Canny(blur, 80, 160)

#     h, w = edges.shape
#     roi = edges[int(h * 0.7):h, int(w * 0.2):int(w * 0.8)]

#     lines = cv2.HoughLinesP(
#         roi,
#         rho=1,
#         theta=np.pi / 180,
#         threshold=150,
#         minLineLength=200,
#         maxLineGap=30
#     )

#     # ❗ No clear lane markings
#     if lines is None:
#         return 0

#     # Filter near-vertical lane lines only
#     lane_lines = 0
#     for line in lines:
#         x1, y1, x2, y2 = line[0]
#         angle = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))

#         # Vertical-ish lanes
#         if angle > 60:
#             lane_lines += 1

#     # Require strong lane presence
#     if lane_lines >= 4:
#         return 1

#     return 0
