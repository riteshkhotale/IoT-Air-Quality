
# ============================================================
# 🌍 Smart AQI Dashboard — Location-aware AI Analysis & Forecast
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor

# ------------------------------------------------------------
# Streamlit Page Configuration
# ------------------------------------------------------------
st.set_page_config(page_title="Smart AQI Dashboard", layout="wide", page_icon="🌍")

# ------------------------------------------------------------
# Custom CSS (Large Header + Professional Spacing)
# ------------------------------------------------------------
st.markdown("""
    <style>
        .big-title {
            font-size: 2.6rem;          
            font-weight: 800;
            color: #1c1c1c;
            margin-bottom: -5px;
        }
        .caption-text {
            font-size: 1rem;
            color: #444;
            margin-bottom: 25px;
        }
        .color-legend {
            background-color: #f0f0f0;
            border-radius: 10px;
            padding: 10px;
            font-size: 0.95rem;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# Header Section
# ------------------------------------------------------------
st.markdown('<p class="big-title">🌍 Smart AQI Monitoring — AI-based Location Analysis</p>', unsafe_allow_html=True)
st.markdown('<p class="caption-text">Real-time monitoring of air quality across Pune regions with location mapping and AI predictions</p>', unsafe_allow_html=True)

# ============================================================
# 1️⃣ Load Data
# ============================================================
def load_data(path="aqi_data.csv"):
    df = pd.read_csv(path)
    expected_cols = {"timestamp", "temperature", "humidity", "ppm", "aqi", "latitude", "longitude"}
    if not expected_cols.issubset(df.columns):
        raise ValueError(f"CSV file missing expected columns: {expected_cols}")
    if "location_name" in df.columns:
        df["place"] = df["location_name"]
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    for col in ["temperature", "humidity", "ppm", "aqi", "latitude", "longitude"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=["timestamp", "latitude", "longitude"])

try:
    df = load_data("aqi_data.csv")
except Exception as e:
    st.error(f"❌ Failed to load data: {e}")
    st.stop()

if "place" not in df.columns:
    df["place"] = "Unknown Location"

# ============================================================
# 2️⃣ AQI Color Mapping
# ============================================================
def aqi_color(aqi):
    if aqi <= 50: return "#00e400"   # Green
    elif aqi <= 100: return "#ffff00" # Yellow
    elif aqi <= 150: return "#ff7e00" # Orange
    elif aqi <= 200: return "#ff0000" # Red
    else: return "#8f3f97"            # Purple

df["aqi_color"] = df["aqi"].apply(aqi_color)

# ============================================================
# 3️⃣ Aggregate Stats by Location
# ============================================================
place_stats = df.groupby("place").agg(
    count=("aqi", "count"),
    avg_aqi=("aqi", "mean"),
    avg_temp=("temperature", "mean"),
    avg_hum=("humidity", "mean"),
    avg_ppm=("ppm", "mean"),
    last_timestamp=("timestamp", "max")
).reset_index().sort_values("avg_aqi")

# Sidebar
st.sidebar.header("📍 Select Location")
selected_place = st.sidebar.selectbox("Choose a place to analyze:", place_stats["place"].tolist())

# ============================================================
# 4️⃣ Map Visualization
# ============================================================
st.markdown("---")
st.subheader("🗺 Pune AQI Map — Color-coded by Air Quality Level")

# Check if we have valid location data
valid_data = df.dropna(subset=["latitude", "longitude"])

if valid_data.empty:
    st.warning("⏳ Waiting for GPS data... Showing default map of Pune.")
    center_lat, center_lon = 18.5204, 73.8567 # Default to Pune Center
else:
    latest_valid = valid_data.iloc[-1]
    center_lat, center_lon = latest_valid["latitude"], latest_valid["longitude"]

fig_map = px.scatter_mapbox(
    df,
    lat="latitude",
    lon="longitude",
    size="aqi",
    hover_name="place",
    hover_data={"temperature": True, "humidity": True, "ppm": True, "aqi": True},
    zoom=11,
    height=520
)

fig_map.update_traces(
    marker=dict(
        color=df["aqi_color"],
        opacity=0.9,
        sizemode="area"
    )
)

fig_map.update_layout(
    mapbox_style="open-street-map",
    mapbox=dict(center=dict(lat=center_lat, lon=center_lon)),
    margin={"r": 0, "t": 30, "l": 0, "b": 0},
    title="Color-coded Air Quality Index (🟢 Good → 🟣 Very Unhealthy)"
)

st.plotly_chart(fig_map, use_container_width=True)

# ============================================================
# 🎨 Color Legend
# ============================================================
st.markdown("""
<div class="color-legend">
<b>🟢 Good (0–50)</b> — Healthy air<br>
<b>🟡 Moderate (51–100)</b> — Acceptable, minor concern<br>
<b>🟠 Unhealthy for Sensitive Groups (101–150)</b> — Limit outdoor exposure<br>
<b>🔴 Unhealthy (151–200)</b> — Avoid prolonged outdoor activity<br>
<b>🟣 Very Unhealthy (200+)</b> — Hazardous to health
</div>
""", unsafe_allow_html=True)

# ============================================================
# 5️⃣ Average Summary by Location
# ============================================================
st.markdown("---")
st.subheader("📊 Average Summary by Location (Aggregated Data)")

avg_table = place_stats[["place", "avg_aqi", "avg_temp", "avg_hum", "avg_ppm"]].rename(columns={
    "place": "Place",
    "avg_aqi": "Avg AQI",
    "avg_temp": "Avg Temp (°C)",
    "avg_hum": "Avg Humidity (%)",
    "avg_ppm": "Avg PPM"
})
st.dataframe(avg_table.round(2), use_container_width=True, height=250)

# ============================================================
# 6️⃣ Summary Cards
# ============================================================
st.markdown("---")
st.subheader("📍 Place Summaries (Sorted by Air Quality — Best First)")

cols = st.columns(3)
for i, row in place_stats.reset_index(drop=True).iterrows():
    if i % 3 == 0:
        cols = st.columns(3)
    with cols[i % 3]:
        st.metric(label=row["place"], value=f"AQI {row['avg_aqi']:.1f}", delta=f"{row['count']} readings")
        st.write(f"🌡 {row['avg_temp']:.1f}°C | 💧 {row['avg_hum']:.1f}% | 🧪 {row['avg_ppm']:.1f}")

# ============================================================
# 7️⃣ Detailed Analysis
# ============================================================
st.markdown("---")
st.subheader(f"🔍 Detailed View — {selected_place}")

place_df = df[df["place"] == selected_place].sort_values("timestamp")

if place_df.empty:
    st.info("No data available for this location yet.")
else:
    latest = place_df.iloc[-1]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌡 Temperature (°C)", f"{latest['temperature']:.2f}")
    c2.metric("💧 Humidity (%)", f"{latest['humidity']:.2f}")
    c3.metric("🧪 PPM", f"{latest['ppm']:.2f}")
    c4.metric("🌫 AQI", f"{latest['aqi']:.2f}")

    # Historical Trends
    st.markdown("### 📈 Historical Trends — AQI, Temperature, Humidity & PPM")

    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

    fig_aqi = px.line(place_df, x="timestamp", y="aqi", title=f"🌫 AQI Trend — {selected_place}", markers=True)
    fig_temp = px.line(place_df, x="timestamp", y="temperature", title=f"🌡 Temperature Trend — {selected_place}", markers=True)
    fig_hum = px.line(place_df, x="timestamp", y="humidity", title=f"💧 Humidity Trend — {selected_place}", markers=True)
    fig_ppm = px.line(place_df, x="timestamp", y="ppm", title=f"🧪 PPM Trend — {selected_place}", markers=True)

    row1_col1.plotly_chart(fig_aqi, use_container_width=True)
    row1_col2.plotly_chart(fig_temp, use_container_width=True)
    row2_col1.plotly_chart(fig_hum, use_container_width=True)
    row2_col2.plotly_chart(fig_ppm, use_container_width=True)

    # Correlation Heatmap
    st.markdown("### 🔬 Correlation Heatmap")
    corr = place_df[["temperature", "humidity", "ppm", "aqi"]].corr()
    st.plotly_chart(px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r"), use_container_width=True)

    # AI Forecast
    st.markdown("### 🤖 AI Forecast — Predicted AQI (Next 6 Hours)")
    try:
        features = ["temperature", "humidity", "ppm"]
        X, y = place_df[features], place_df["aqi"]
        if len(X) > 10:
            model = RandomForestRegressor(n_estimators=200, random_state=42)
            model.fit(X, y)
            last_row = place_df.iloc[-1][features]
            future_df = pd.DataFrame([{
                "temperature": last_row["temperature"] + np.random.uniform(-0.3, 0.3),
                "humidity": last_row["humidity"] + np.random.uniform(-1, 1),
                "ppm": last_row["ppm"] + np.random.uniform(-4, 4)
            } for _ in range(12)])
            future_df["Predicted AQI"] = model.predict(future_df)
            future_df["timestamp"] = pd.date_range(place_df["timestamp"].iloc[-1], periods=12, freq="30min")

            fig_forecast = go.Figure()
            fig_forecast.add_trace(go.Scatter(x=place_df["timestamp"], y=place_df["aqi"],
                                              mode="lines", name="Actual AQI", line=dict(color="blue")))
            fig_forecast.add_trace(go.Scatter(x=future_df["timestamp"], y=future_df["Predicted AQI"],
                                              mode="lines", name="Predicted AQI",
                                              line=dict(color="red", dash="dot")))
            fig_forecast.update_layout(title="AI Forecast — Future AQI (Next 6 Hours)",
                                       xaxis_title="Time", yaxis_title="AQI",
                                       template="plotly_white")
            st.plotly_chart(fig_forecast, use_container_width=True)
        else:
            st.warning("⚠ Not enough data points to train AI model for this area yet.")
    except Exception as e:
        st.error(f"Forecast failed: {e}")

# ============================================================
# 8️⃣ Comparison & Smart Suggestions (Enhanced with Extra Insights)
# ============================================================
st.markdown("---")
st.subheader("⚖ Comparison & Smart Recommendations")

best_place_row = place_stats.iloc[0]
best_place = best_place_row["place"]
st.write(f"🏆 *Cleanest Location:* {best_place} — Avg AQI: {best_place_row['avg_aqi']:.1f}")

sel_row = place_stats[place_stats["place"] == selected_place].squeeze()

if not sel_row.empty:
    comp_df = pd.DataFrame({
        "Metric": ["Avg AQI", "Avg Temp (°C)", "Avg Humidity (%)", "Avg PPM"],
        selected_place: [sel_row["avg_aqi"], sel_row["avg_temp"], sel_row["avg_hum"], sel_row["avg_ppm"]],
        best_place: [best_place_row["avg_aqi"], best_place_row["avg_temp"], best_place_row["avg_hum"], best_place_row["avg_ppm"]]
    })
    st.table(comp_df.round(2))

    # ✅ Skip insights if selected place is already the cleanest
    if selected_place == best_place:
        st.success("✅ This is the cleanest location with optimal air quality among all monitored regions. No improvement actions required.")
    else:
        st.markdown("### 🧾 Environmental Insight Summary")

        diff_aqi = sel_row["avg_aqi"] - best_place_row["avg_aqi"]
        diff_temp = sel_row["avg_temp"] - best_place_row["avg_temp"]
        diff_hum = sel_row["avg_hum"] - best_place_row["avg_hum"]
        diff_ppm = sel_row["avg_ppm"] - best_place_row["avg_ppm"]

        insight_text = []
        if diff_aqi > 0:
            insight_text.append(f"- 🏭 AQI is {diff_aqi:.1f} points higher than {best_place}, indicating increased pollution.")
        else:
            insight_text.append(f"- 🌱 AQI is {abs(diff_aqi):.1f} points lower than {best_place}, indicating cleaner air quality.")

        if diff_temp > 0:
            insight_text.append(f"- 🌡 Temperature is {diff_temp:.1f}°C higher — possible urban heat or less green cover.")
        else:
            insight_text.append(f"- 🌤 Temperature is {abs(diff_temp):.1f}°C lower — cooler environment.")

        if diff_hum > 0:
            insight_text.append(f"- 💧 Humidity is {diff_hum:.1f}% higher — possibly due to more moisture or vegetation.")
        else:
            insight_text.append(f"- 💨 Humidity is {abs(diff_hum):.1f}% lower — dry air may trap more dust.")

        if diff_ppm > 0:
            insight_text.append(f"- 🧪 PPM is {diff_ppm:.1f} units higher — more particulate matter in air.")
        else:
            insight_text.append(f"- 🧪 PPM is {abs(diff_ppm):.1f} units lower — cleaner particulate levels detected.")

        for line in insight_text:
            st.write(line)

        st.markdown("### 🤖 Smart Improvement Suggestions")

        suggestions = []
        if diff_aqi > 40:
            suggestions.append("🚗 High AQI — promote EVs, public transport, and emission control policies.")
        elif diff_aqi > 20:
            suggestions.append("🌿 Moderate AQI rise — plant roadside trees and reduce industrial emissions.")
        elif diff_aqi > 5:
            suggestions.append("🪴 Slight AQI rise — promote local green initiatives and dust control.")
        else:
            suggestions.append("✅ Excellent air quality comparable to best zone.")

        if diff_temp > 3:
            suggestions.append("🌡 Higher temperature — increase shaded areas, rooftop gardens, and reflective surfaces.")
        elif diff_temp < -2:
            suggestions.append("❄ Cooler temperature — maintain humidity to prevent fog and condensation.")

        if diff_hum < -10:
            suggestions.append("💧 Low humidity — introduce water bodies or tree cover to balance moisture.")
        elif diff_hum > 10:
            suggestions.append("💦 High humidity — inspect for waterlogging or poor drainage areas.")

        if diff_ppm > 10:
            suggestions.append("🧪 High PPM — check for nearby traffic congestion or factories.")
        elif diff_ppm < -5:
            suggestions.append("🌬 Low PPM — environment already clean; continue pollution control practices.")

        # 🌍 Additional Smart Eco Suggestions (NEW)
        if diff_hum > 5 and diff_ppm > 8:
            suggestions.append("🌬 Combine humidity control and air purification — install biofilters or urban green walls.")
        if diff_aqi > 25 and diff_temp > 2:
            suggestions.append("🌞 Implement reflective pavements and solar rooftops to reduce urban heat island effects.")
        if diff_aqi > 15 and abs(diff_hum) < 5:
            suggestions.append("🌾 Introduce dust suppression systems or roadside green belts to reduce PM levels.")

        for s in suggestions:
            st.write(f"- {s}")

# ============================================================
# 9️⃣ Download Data
# ============================================================
st.markdown("---")
st.download_button("⬇ Download Full AQI Data", df.to_csv(index=False).encode("utf-8"), "aqi_data_with_places.csv")
st.info("💡 Tip: Take readings at different Pune sub-locations (Kothrud, FC Road, Katraj, Hinjewadi) for comparative insights.")