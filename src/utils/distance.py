import pandas as pd
import numpy as np


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two geographic coordinates.
    Returns distance in kilometers.
    """

    earth_radius = 6371.0

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    c = 2 * np.arcsin(np.sqrt(a))

    return earth_radius * c


def find_nearby_stations(
    latitude,
    longitude,
    stations,
    radius_km=5,
    max_results=10
):
    """
    Find nearby EV charging stations.
    """

    stations = stations.copy()

    stations["distance_km"] = haversine_distance(
        latitude,
        longitude,
        stations["Latitude"].values,
        stations["Longitude"].values
    )

    nearby = stations[
        stations["distance_km"] <= radius_km
    ].copy()

    nearby = nearby.sort_values("distance_km")

    return nearby.head(max_results)