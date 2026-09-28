import sys
import os
from datetime import datetime

import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

# Allow imports from project root
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from src.utils.distance import find_nearby_stations
from src.utils.recommendation import calculate_recommendation_score
from src.models.predict_demand import predict_demand
from src.utils.waiting_time import estimate_waiting_time


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="EV Charging AI",
    page_icon="⚡",
    layout="wide"
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("⚡ AI-Based EV Charging Recommendation System")

st.markdown(
    """
    Find nearby EV charging stations using your location and
    receive AI-based demand prediction, estimated waiting time,
    and station recommendations.
    """
)

st.divider()


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "results" not in st.session_state:
    st.session_state.results = None

if "predicted_demand" not in st.session_state:
    st.session_state.predicted_demand = None


# ---------------------------------------------------------
# SIDEBAR - USER INPUT
# ---------------------------------------------------------

with st.sidebar:

    st.header("🚗 Charging Details")

    st.subheader("📍 Your Location")

    latitude = st.number_input(
        "Latitude",
        value=12.9716,
        format="%.6f"
    )

    longitude = st.number_input(
        "Longitude",
        value=77.5946,
        format="%.6f"
    )

    st.subheader("🔋 Vehicle")

    battery_soc = st.slider(
        "Current Battery (%)",
        min_value=0,
        max_value=100,
        value=35
    )

    battery_capacity = st.number_input(
        "Battery Capacity (kWh)",
        min_value=10.0,
        max_value=200.0,
        value=60.0
    )

    vehicle_type = st.selectbox(
        "Vehicle Type",
        [
            "Sedan",
            "SUV",
            "Hatchback",
            "Two-Wheeler",
            "Other"
        ]
    )

    st.subheader("🌦️ Current Conditions")

    traffic = st.selectbox(
        "Traffic Density",
        [
            "Low",
            "Medium",
            "High"
        ]
    )

    weather = st.selectbox(
        "Weather",
        [
            "Clear",
            "Cloudy",
            "Rainy"
        ]
    )

    time_slot = st.selectbox(
        "Time Slot",
        [
            "Morning",
            "Afternoon",
            "Evening",
            "Night"
        ]
    )

    charging_priority = st.selectbox(
        "Charging Priority",
        [
            "Low",
            "Medium",
            "High"
        ]
    )

    find_stations = st.button(
        "🔍 Find Charging Stations",
        use_container_width=True
    )


# ---------------------------------------------------------
# MAIN PROCESSING
# ---------------------------------------------------------

if find_stations:

    station_file = (
        "data/processed/bengaluru_station_locations_final.csv"
    )

    try:

        stations = pd.read_csv(station_file)

    except FileNotFoundError:

        st.error(
            "Station dataset not found. "
            "Please check the data/processed folder."
        )

        st.stop()

    nearby = find_nearby_stations(
        latitude,
        longitude,
        stations,
        radius_km=5,
        max_results=10
    )

    if nearby.empty:

        st.session_state.results = None
        st.session_state.predicted_demand = None

        st.warning(
            "No charging stations were found within 5 km "
            "of the selected location."
        )

    else:

        # Current date and time
        now = datetime.now()

        current_day = now.strftime("%A")
        current_hour = now.hour
        current_month = now.month
        current_day_number = now.day

        # -------------------------------------------------
        # DEMAND PREDICTION
        # -------------------------------------------------

        predicted_demand = predict_demand(
            location_type="Urban",
            vehicle_type=vehicle_type,
            battery_capacity_kWh=battery_capacity,
            initial_soc=battery_soc,
            charging_power_kW=22,
            electricity_price=8,
            renewable_energy_ratio=0.3,
            traffic_density=traffic,
            weather_condition=weather,
            day_of_week=current_day,
            time_slot=time_slot,
            charging_priority=charging_priority,
            hour=current_hour,
            month=current_month,
            day=current_day_number
        )

        nearby["demand_level"] = predicted_demand

        # -------------------------------------------------
        # ESTIMATED WAITING TIME
        # -------------------------------------------------

        nearby["estimated_waiting_time"] = nearby.apply(
            lambda row: estimate_waiting_time(
                demand_level=row["demand_level"],
                charger_power_kw=row["max_charger_rating"]
            ),
            axis=1
        )

        # -------------------------------------------------
        # RECOMMENDATION SCORE
        # -------------------------------------------------

        nearby["recommendation_score"] = nearby.apply(
            lambda row: calculate_recommendation_score(
                distance_km=row["distance_km"],
                charger_power_kw=row["max_charger_rating"],
                demand_level=row["demand_level"],
                estimated_waiting_time=row[
                    "estimated_waiting_time"
                ]
            ),
            axis=1
        )

        nearby = nearby.sort_values(
            "recommendation_score",
            ascending=False
        ).reset_index(drop=True)

        # Save results
        st.session_state.results = nearby
        st.session_state.predicted_demand = predicted_demand


# ---------------------------------------------------------
# DISPLAY RESULTS
# ---------------------------------------------------------

if st.session_state.results is not None:

    nearby = st.session_state.results
    predicted_demand = st.session_state.predicted_demand

    best_station = nearby.iloc[0]

    # -----------------------------------------------------
    # AI PREDICTION
    # -----------------------------------------------------

    st.subheader("🤖 AI Prediction")

    demand_col1, demand_col2 = st.columns([1, 3])

    with demand_col1:

        st.metric(
            "Charging Demand",
            str(predicted_demand)
        )

    with demand_col2:

        st.info(
            "The demand level is predicted using the trained "
            "machine-learning model based on vehicle details, "
            "traffic, weather, time, and charging conditions."
        )

    st.divider()

    # -----------------------------------------------------
    # RECOMMENDED STATION
    # -----------------------------------------------------

    st.subheader("⭐ Recommended Charging Station")

    st.info(
        "This station received the highest recommendation score "
        "based on distance, charger power, predicted demand, "
        "and estimated waiting time."
    )

    st.markdown(
        f"### {best_station['operators']}"
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "📍 Distance",
            f"{best_station['distance_km']:.2f} km"
        )

    with col2:

        st.metric(
            "⚡ Charger Power",
            f"{best_station['max_charger_rating']} kW"
        )

    with col3:

        st.metric(
            "🤖 Demand",
            str(best_station["demand_level"])
        )

    with col4:

        st.metric(
            "⏱️ Estimated Wait",
            f"{best_station['estimated_waiting_time']} min"
        )

    with col5:

        st.metric(
            "⭐ Score",
            f"{best_station['recommendation_score']:.2f}"
        )

    st.divider()

    # -----------------------------------------------------
    # NEARBY STATIONS TABLE
    # -----------------------------------------------------

    st.subheader("📍 Nearby Charging Stations")

    display_df = nearby[
        [
            "operators",
            "distance_km",
            "max_charger_rating",
            "demand_level",
            "estimated_waiting_time",
            "recommendation_score"
        ]
    ].copy()

    display_df.columns = [
        "Operator",
        "Distance (km)",
        "Charger Power (kW)",
        "Predicted Demand",
        "Estimated Wait (min)",
        "Recommendation Score"
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Operator": st.column_config.TextColumn(
                "Operator",
                width="medium"
            ),
            "Distance (km)": st.column_config.NumberColumn(
                "Distance (km)",
                format="%.2f"
            ),
            "Charger Power (kW)": st.column_config.NumberColumn(
                "Charger Power (kW)",
                format="%.1f"
            ),
            "Predicted Demand": st.column_config.TextColumn(
                "Demand"
            ),
            "Estimated Wait (min)": st.column_config.NumberColumn(
                "Wait (min)"
            ),
            "Recommendation Score": st.column_config.NumberColumn(
                "Score",
                format="%.2f"
            )
        }
    )

    st.divider()

    # -----------------------------------------------------
    # MAP
    # -----------------------------------------------------

    st.subheader("🗺️ Charging Station Map")

    st.caption(
        "🔵 Your location   🟢 Recommended station   🔴 Other stations"
    )

    charging_map = folium.Map(
        location=[
            latitude,
            longitude
        ],
        zoom_start=13
    )

    # User location
    folium.Marker(
        [
            latitude,
            longitude
        ],
        popup="Your Location",
        tooltip="Your Location",
        icon=folium.Icon(
            color="blue",
            icon="user",
            prefix="fa"
        )
    ).add_to(charging_map)

    best_score = nearby[
        "recommendation_score"
    ].max()

    # Station markers
    for _, row in nearby.iterrows():

        popup_text = (
            f"<b>Operator:</b> {row['operators']}<br>"
            f"<b>Distance:</b> "
            f"{row['distance_km']:.2f} km<br>"
            f"<b>Charger:</b> "
            f"{row['max_charger_rating']} kW<br>"
            f"<b>Demand:</b> "
            f"{row['demand_level']}<br>"
            f"<b>Estimated Wait:</b> "
            f"{row['estimated_waiting_time']} min<br>"
            f"<b>Score:</b> "
            f"{row['recommendation_score']:.2f}"
        )

        if row["recommendation_score"] == best_score:

            marker_color = "green"
            marker_icon = "star"

        else:

            marker_color = "red"
            marker_icon = "bolt"

        folium.Marker(
            [
                row["Latitude"],
                row["Longitude"]
            ],
            popup=folium.Popup(
                popup_text,
                max_width=300
            ),
            tooltip=str(row["operators"]),
            icon=folium.Icon(
                color=marker_color,
                icon=marker_icon,
                prefix="fa"
            )
        ).add_to(charging_map)

    st_folium(
        charging_map,
        width=None,
        height=500
    )

    # -----------------------------------------------------
    # PROJECT NOTE
    # -----------------------------------------------------

    st.divider()

    st.caption(
        "Note: Estimated waiting time is a prototype heuristic "
        "based on predicted demand and charger power. It is not "
        "a live occupancy or real-time queue measurement."
    )

else:

    # -----------------------------------------------------
    # INITIAL SCREEN
    # -----------------------------------------------------

    st.subheader("🚗 How It Works")

    step1, step2, step3 = st.columns(3)

    with step1:

        st.markdown("### 1️⃣ Enter Details")

        st.write(
            "Provide your location, vehicle information, "
            "battery level, and current conditions."
        )

    with step2:

        st.markdown("### 2️⃣ AI Analysis")

        st.write(
            "The system predicts charging demand and estimates "
            "the waiting time at nearby stations."
        )

    with step3:

        st.markdown("### 3️⃣ Get Recommendation")

        st.write(
            "Nearby stations are compared using distance, "
            "charger power, demand, and estimated waiting time."
        )

    st.divider()

    st.info(
        "👈 Enter your charging details in the sidebar "
        "and click **Find Charging Stations** to begin."
    )