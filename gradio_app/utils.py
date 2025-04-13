import folium
import leafmap.foliumap as leafmap

from gradio_app.constants import VALID_MESSAGE
from src.agents.itinerary import Validation


def validation_message(validiation_agent_response: Validation) -> str:
    valid_plan = validiation_agent_response.plan_is_valid.lower()

    if valid_plan.lower() == "no":
        validation_body: str = validiation_agent_response.updated_request
        validation_header: str = (
            "The query is not valid in its current state. Here is a "
            "suggestion from the model: \n"
        )
        validation: str = validation_header + validation_body
    else:
        validation: str = VALID_MESSAGE

    return validation


def generate_generic_leafmap():
    map = leafmap.Map(location=[0, 0], tiles="OpenStreetMap", zoom_start=3)
    return map.to_gradio()


def generate_leafmap(directions_list, sampled_route):
    map_start_loc_lat = directions_list[0]["legs"][0]["start_location"]["lat"]
    map_start_loc_lon = directions_list[0]["legs"][0]["start_location"]["lng"]
    map_start_loc = [map_start_loc_lat, map_start_loc_lon]

    marker_points = []

    # extract the location points from the previous directions function
    for segment in directions_list:
        for leg in segment["legs"]:
            leg_start_loc = leg["start_location"]
            marker_points.append(
                ([leg_start_loc["lat"], leg_start_loc["lng"]], leg["start_address"])
            )

    last_stop = directions_list[-1]["legs"][-1]
    last_stop_coords = last_stop["end_location"]
    marker_points.append(
        (
            [last_stop_coords["lat"], last_stop_coords["lng"]],
            last_stop["end_address"],
        )
    )

    map = leafmap.Map(location=map_start_loc, tiles="OpenStreetMap", zoom_start=8)

    # Add waypoint markers to the map
    for location, address in marker_points:
        folium.Marker(
            location=location,
            popup=address,
            tooltip="<strong>Click for address</strong>",
            icon=folium.Icon(color="red", icon="info-sign"),
        ).add_to(map)

    for leg_id, route_points in sampled_route.items():
        leg_distance = route_points["distance"]
        leg_duration = route_points["duration"]

        f_group = folium.FeatureGroup(f"Leg {leg_id}")
        folium.vector_layers.PolyLine(
            route_points["route"],
            popup=f"<b>Route segment {leg_id}</b>",
            tooltip=f"Distance: {leg_distance}, Duration: {leg_duration}",
            color="blue",
            weight=2,
        ).add_to(f_group)
        f_group.add_to(map)

    return map.to_gradio()
