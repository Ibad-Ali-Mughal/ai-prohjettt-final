import csv
import random

# Output file
filename = "csv_data/fines_dataset.csv"

# CSV Header (MATCHES ML TRAINING CODE)
header = [
    "vehicle_type",      # 0 = bike, 1 = car
    "speed",             # km/h
    "road_priority",     # 0 = normal, 1 = highway
    "lane_violation",    # 0 = no, 1 = yes
    "helmet_violation",  # 0 = helmet, 1 = no helmet
    "fine"
]

rows = []

for _ in range(100):
    # Vehicle type
    vehicle_type = random.choice([0, 1])  # 0=bike, 1=car

    # Speed
    speed = random.randint(30, 120)

    # Road priority
    road_priority = random.choice([0, 1])  # 0=normal, 1=highway

    # Lane violation
    lane_violation = random.choice([0, 1])  # 0=no, 1=yes

    # Helmet violation (only bikes)
    helmet_violation = 0
    if vehicle_type == 0:
        helmet_violation = random.choice([0, 1])

    # Fine calculation logic
    fine = 0

    if vehicle_type == 0 and helmet_violation == 1:
        fine += 2000

    if lane_violation == 1:
        fine += 500

    if road_priority == 1 and fine > 0:
        fine += 500

    rows.append([
        vehicle_type,
        speed,
        road_priority,
        lane_violation,
        helmet_violation,
        fine
    ])

# Write CSV
with open(filename, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(header)
    writer.writerows(rows)

print("✅ fines_dataset.csv created successfully with 100 rows")
