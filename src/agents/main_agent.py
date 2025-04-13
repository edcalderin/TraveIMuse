from dataclasses import dataclass
from typing import NamedTuple

from langchain_core.runnables import RunnableSequence

from src.agents.itinerary import ItineraryAgent, Validation, ValidationAgent
from src.agents.locations import LocationAgent, Trip


class AgentResponse(NamedTuple):
    itinerary: str
    list_of_places: Trip
    validation: Validation


@dataclass(frozen=True)
class ItinerarySuggestion:
    _itinerary_agent: ItineraryAgent = ItineraryAgent()
    _location_agent: LocationAgent = LocationAgent()
    _validation_agent: ValidationAgent = ValidationAgent()

    def _generate_itinerary(self, query_input: dict[str, str]) -> str:
        itinerary_chain: RunnableSequence = self._itinerary_agent.create_chain()
        return itinerary_chain.invoke(query_input)

    def _extract_locations(self, itinerary_response: str) -> Trip:
        location_chain: RunnableSequence = self._location_agent.create_chain()
        return location_chain.invoke({"agent_suggestion": itinerary_response})

    def _validate_query(self, query_input: dict[str, str]) -> Validation:
        validation_chain: RunnableSequence = self._validation_agent.create_chain()
        return validation_chain.invoke(query_input)

    def invoke(self, query: str) -> AgentResponse:
        query_input: dict = {"query": query}
        validation_result: Validation = self._validate_query(query_input)
        if validation_result.plan_is_valid.lower()=="no":
            return AgentResponse(itinerary=None, list_of_places=None, validation=validation_result)

        itinerary: str = self._generate_itinerary(query_input)
        list_of_places: Trip = self._extract_locations(itinerary)

        return AgentResponse(
            itinerary=itinerary,
            list_of_places=list_of_places,
            validation=validation_result,
        )
