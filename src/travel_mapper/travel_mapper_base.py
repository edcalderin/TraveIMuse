from src.agents import ItinerarySuggestion
from src.travel_mapper.route_finder import RouteFinder


class TravelMapperBase:
    def __init__(self):
        self.travel_agent = ItinerarySuggestion()
        self.route_finder = RouteFinder()

    def parse(self, query: str, make_map: bool = True):
        itinerary, list_of_places, validation = self.travel_agent.invoke(query)
        directions, sampled_route, mapping_dict = self.route_finder.generate_route(
            list_of_places=list_of_places, itinerary=itinerary, include_map=make_map
        )
        print(directions, sampled_route, mapping_dict, validation)
