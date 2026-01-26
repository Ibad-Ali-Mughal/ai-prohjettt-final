# import pandas as pd
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# import pickle
# import os

# # Paths
# csv_path = "csv_data/fines_dataset.csv"
# models_path = "models/ml_model.pkl"

# # Load CSV dataset
# df = pd.read_csv(csv_path)

# # Features and target
# X = df[["vehicle_type", "speed", "road_priority", "lane_violation", "helmet_violation"]]
# y = df["fine"]

# # Split dataset (80% train, 20% test)
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# # Train RandomForestRegressor
# model = RandomForestRegressor(n_estimators=100, random_state=42)
# model.fit(X_train, y_train)

# # Evaluate model
# y_pred = model.predict(X_test)
# mae = mean_absolute_error(y_test, y_pred)
# rmse = mean_squared_error(y_test, y_pred, squared=False)
# r2 = r2_score(y_test, y_pred)

# print("ML Model trained successfully!")
# print(f"MAE: {mae:.2f}, RMSE: {rmse:.2f}, R2 Score: {r2:.2f}")

# # Create models folder if it doesn't exist
# os.makedirs("models", exist_ok=True)

# # Save trained model
# with open(models_path, "wb") as f:
#     pickle.dump(model, f)

# print(f"ML model saved as '{models_path}'")
print("🔥 SCRIPT STARTED 🔥")

import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import pickle

# ----------------------------
# PATHS
# ----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(BASE_DIR, "csv_data", "fines_dataset.csv")
models_dir = os.path.join(BASE_DIR, "models")
model_path = os.path.join(models_dir, "ml_model.pkl")

print("📄 CSV PATH:", csv_path)
print("📦 MODEL PATH:", model_path)

if not os.path.exists(csv_path):
    print("❌ CSV FILE NOT FOUND")
    exit()

# ----------------------------
# LOAD CSV
# ----------------------------
df = pd.read_csv(csv_path)
print("✅ CSV LOADED | Rows:", len(df))
print("📊 Columns:", list(df.columns))

# ----------------------------
# ENCODE DATA (MATCHES YOUR CSV)
# ----------------------------

# VehicleType: Bike=0, Car=1
df["vehicle_type"] = df["VehicleType"].map({"Bike": 0, "Car": 1})

# Speed
df["speed"] = df["Speed"]

# Violations → flags
df["no_helmet"] = df["Violations"].str.contains("NO_HELMET").astype(int)
df["lane_violation"] = df["Violations"].str.contains("LANE_VIOLATION").astype(int)

# Overspeed derived from speed
SPEED_LIMIT = 60
df["overspeed"] = (df["speed"] > SPEED_LIMIT).astype(int)

# ----------------------------
# FEATURES & TARGET
# ----------------------------
X = df[
    [
        "vehicle_type",
        "speed",
        "no_helmet",
        "lane_violation",
        "overspeed",
    ]
]

y = df["Fine"]

# ----------------------------
# TRAIN / TEST SPLIT
# ----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ----------------------------
# TRAIN MODEL
# ----------------------------
model = RandomForestRegressor(
    n_estimators=150,
    random_state=42
)

model.fit(X_train, y_train)

# ----------------------------
# EVALUATION
# ----------------------------
y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred) ** 0.5

print("✅ TRAINING DONE")
print(f"📉 MAE  : {mae:.2f}")
print(f"📉 RMSE : {rmse:.2f}")

# ----------------------------
# SAVE MODEL
# ----------------------------
os.makedirs(models_dir, exist_ok=True)

with open(model_path, "wb") as f:
    pickle.dump(model, f)

print("💾 MODEL SAVED SUCCESSFULLY")
