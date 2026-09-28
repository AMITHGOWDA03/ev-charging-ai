import os
import joblib
import pandas as pd


# ---------------------------------------------------------
# MODEL PATH
# ---------------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

MODEL_FILE = os.path.join(
    PROJECT_ROOT,
    "04_ML_Model",
    "demand_model_compressed.pkl"
)


# ---------------------------------------------------------
# DEMAND PREDICTION
# ---------------------------------------------------------

def predict_demand(
    location_type,
    vehicle_type,
    battery_capacity_kWh,
    initial_soc,
    charging_power_kW,
    electricity_price,
    renewable_energy_ratio,
    traffic_density,
    weather_condition,
    day_of_week,
    time_slot,
    charging_priority,
    hour,
    month,
    day
):
    """
    Predict EV charging demand level.

    Returns:
        Low, Medium, or High
    """

    # Load trained model
    model = joblib.load(MODEL_FILE)

    # Create input data
    input_data = pd.DataFrame([{
        "location_type": location_type,
        "vehicle_type": vehicle_type,
        "battery_capacity_kWh": battery_capacity_kWh,
        "initial_soc": initial_soc,
        "charging_power_kW": charging_power_kW,
        "electricity_price": electricity_price,
        "renewable_energy_ratio": renewable_energy_ratio,
        "traffic_density": traffic_density,
        "weather_condition": weather_condition,
        "day_of_week": day_of_week,
        "time_slot": time_slot,
        "charging_priority": charging_priority,
        "hour": hour,
        "month": month,
        "day": day
    }])

    # Make prediction
    prediction = model.predict(input_data)

    return prediction[0]


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    result = predict_demand(
        location_type="Urban",
        vehicle_type="SUV",
        battery_capacity_kWh=60,
        initial_soc=35,
        charging_power_kW=22,
        electricity_price=8,
        renewable_energy_ratio=0.3,
        traffic_density="High",
        weather_condition="Rainy",
        day_of_week="Monday",
        time_slot="Evening",
        charging_priority="High",
        hour=18,
        month=9,
        day=28
    )

    print("Predicted Demand:", result)