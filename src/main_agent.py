from dataclasses import dataclass

from langchain_core.runnables import RunnableSequence

from src.itinerary import ItineraryAgent
from src.locations import LocationAgent


@dataclass(frozen=True)
class ItinerarySuggestion:
    _itinerary_agent: ItineraryAgent = ItineraryAgent()
    _location_agent: LocationAgent = LocationAgent()

    def create_chain(self) -> RunnableSequence:
        itinerary_chain: RunnableSequence = self._itinerary_agent.create_chain()
        location_chain: RunnableSequence = self._location_agent.create_chain()
        return {"agent_suggestion": itinerary_chain} | location_chain


if __name__ == "__main__":
    itinerary_suggestion = ItinerarySuggestion()
    query = """
        I want to do a 5 day roadtrip from Monteria to Barranquilla in Colombia.
        I want to visit remote locations with beautiful sights
        """
    itinerary_chain = itinerary_suggestion.create_chain()
    result = itinerary_chain.invoke({"query": query})
    print(result)
