def calculate_recommendation_score(
    distance_km,
    charger_power_kw,
    demand_level,
    estimated_waiting_time=10,
    max_distance_km=5
):
    distance_score = max(
        0,
        1 - (distance_km / max_distance_km)
    )

    power_score = min(
        charger_power_kw / 120,
        1
    )

    demand_scores = {
        "Low": 1.0,
        "Medium": 0.6,
        "High": 0.2
    }

    demand_score = demand_scores.get(
        str(demand_level).title(),
        0.5
    )

    waiting_score = max(
        0,
        1 - (estimated_waiting_time / 30)
    )

    score = (
        0.35 * distance_score
        + 0.25 * power_score
        + 0.20 * demand_score
        + 0.20 * waiting_score
    )

    return round(score * 100, 2)