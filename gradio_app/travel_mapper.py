from gradio_app.constants import VALID_MESSAGE
from gradio_app.utils import (
    generate_generic_leafmap,
    generate_leafmap,
    validation_message,
)
from src.agents import ItinerarySuggestion
from src.travel_mapper import RouteFinder


class TravelMapperForUI:
    def __init__(self) -> None:
        self._travel_agent: ItinerarySuggestion = ItinerarySuggestion()
        self._route_finder: RouteFinder = RouteFinder()

    def generate_without_leafmap(self, query: str):
        itinerary, _, validation = self._travel_agent.invoke(query)

        # make validation message
        validation_string = validation_message(validation)

        if validation_string != VALID_MESSAGE:
            itinerary = "No valid itinerary"

        return itinerary, validation_string

    def generate_with_leafmap(self, query: str):
        itinerary, list_of_places, validation = self._travel_agent.invoke(query)

        # make validation message
        validation_string = validation_message(validation)

        if validation_string != VALID_MESSAGE:
            itinerary = "No valid itinerary"
            # make a generic map here
            map_html = generate_generic_leafmap()

        else:
            (
                directions_list,
                sampled_route,
                mapping_dict,
            ) = self._route_finder.generate_route(
                list_of_places=list_of_places, itinerary=itinerary, include_map=True
            )

            map_html = generate_leafmap(directions_list, sampled_route)

        return map_html, itinerary, validation_string
