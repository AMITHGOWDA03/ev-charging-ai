def estimate_waiting_time(demand_level, charger_power_kw):
    """
    Estimate approximate waiting time for a charging station.

    This is a heuristic estimate for the project prototype,
    not a trained ML prediction.
    """

    demand_base = {
        "Low": 5,
        "Medium": 12,
        "High": 20
    }

    wait_time = demand_base.get(str(demand_level).title(), 10)

    # Higher-power chargers generally reduce charging-related delay
    if charger_power_kw >= 60:
        wait_time -= 3
    elif charger_power_kw >= 30:
        wait_time -= 2
    elif charger_power_kw <= 3.3:
        wait_time += 3

    return max(0, round(wait_time))