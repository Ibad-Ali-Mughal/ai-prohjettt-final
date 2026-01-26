import math

class VehicleTracker:
    def __init__(self):
        self.vehicles = {}
        self.next_id = 0

    def update(self, detections):
        updated = {}

        for (x1, y1, x2, y2) in detections:
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            matched_id = None
            min_dist = 50

            for vid, (px, py) in self.vehicles.items():
                dist = math.hypot(cx - px, cy - py)
                if dist < min_dist:
                    matched_id = vid
                    min_dist = dist

            if matched_id is None:
                matched_id = self.next_id
                self.next_id += 1

            updated[matched_id] = (cx, cy)

        self.vehicles = updated
        return updated
