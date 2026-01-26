def estimate_speed(prev_pos, curr_pos, fps=30):
    if prev_pos is None:
        return 0

    pixel_distance = abs(curr_pos[1] - prev_pos[1])
    speed = pixel_distance * fps * 0.18  # calibration factor
    return int(speed)
