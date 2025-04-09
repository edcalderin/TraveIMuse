import os

import googlemaps
from dotenv import load_dotenv

load_dotenv()

google_api_key: str = os.getenv("GOOGLE_API_KEY")

gmaps = googlemaps.Client(key=google_api_key)


def get_direction_results(start, end, waypoints, transit_type, start_time):
    return gmaps.directions(
        start,
        end,
        waypoints=waypoints,
        mode=transit_type,
        units="metric",
        optimize_waypoints=True,
        traffic_model="best_guess",
        departure_time=start_time,
    )
