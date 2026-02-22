
from flask import Flask, request, jsonify
import csv
from datetime import datetime
import os

app = Flask(__name__)

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
CSV_FILE = "aqi_data.csv"
EXPECTED_HEADER = [
    "timestamp",
    "temperature",
    "humidity",
    "ppm",
    "aqi",
    "latitude",
    "longitude",
    "location_name"   # ✅ new column
]

# ------------------------------------------------------------
# Ensure CSV header is correct
# ------------------------------------------------------------
def ensure_csv_header():
    """
    Ensures the CSV file exists and has the correct header.
    Automatically updates header if missing or mismatched.
    """
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(EXPECTED_HEADER)
        print("🆕 Created new CSV with correct header.")
        return

    # Read first line
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()

    if not first_line:
        # Empty file
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(EXPECTED_HEADER)
        print("⚙ Empty file found — header written.")
    else:
        existing_columns = [x.strip() for x in first_line.split(",")]
        if existing_columns != EXPECTED_HEADER:
            print(f"⚠ Header mismatch detected: {existing_columns}")
            # Backup old file
            os.rename(CSV_FILE, CSV_FILE.replace(".csv", "_backup.csv"))
            # Create new with correct header
            with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(EXPECTED_HEADER)
            print("✅ Header corrected and backup created.")
        else:
            print("✅ Header verified OK.")

# Run header check on startup
ensure_csv_header()

# ------------------------------------------------------------
# API Endpoint: Receive IoT Data
# ------------------------------------------------------------
@app.route('/data', methods=['POST'])
def receive_data():
    try:
        data = request.get_json(force=True)
        print("📡 Received:", data)

        # Extract all expected fields safely
        temperature = data.get("temperature", "")
        humidity = data.get("humidity", "")
        ppm = data.get("ppm", "")
        aqi = data.get("aqi", "")
        latitude = data.get("latitude", "")
        longitude = data.get("longitude", "")
        location_name = data.get("location_name", "Unknown")  # ✅ NEW

        # Create timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Append data row to CSV
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp, temperature, humidity, ppm, aqi,
                latitude, longitude, location_name
            ])

        print(f"✅ Data stored for {location_name} → ({latitude}, {longitude})")
        return jsonify({"message": f"✅ Data stored for {location_name}"}), 200

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500

# ------------------------------------------------------------
# Run Server
# ------------------------------------------------------------
if __name__ == '__main__':
    print("🚀 Flask AQI Receiver Running on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)