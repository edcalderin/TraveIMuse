from dataclasses import dataclass

from langchain_core.runnables import RunnableSequence

from src.itinerary import ItineraryTemplate
from src.locations import MappingAgent


@dataclass(frozen=True)
class ItinerarySuggestion:
    _itinerary_template: ItineraryTemplate = ItineraryTemplate()
    _mapping_agent: MappingAgent = MappingAgent()

    def create_chain(self) -> RunnableSequence:
        itinerary_chain: RunnableSequence = self._itinerary_template.create_chain()
        mapping_chain: RunnableSequence = self._mapping_agent.create_chain()
        return {"agent_suggestion": itinerary_chain} | mapping_chain


if __name__ == "__main__":
    itinerary_suggestion = ItinerarySuggestion()
    query = """
        I want to do a 5 day roadtrip from Monteria to Barranquilla in Colombia.
        I want to visit remote locations with beautiful sights
        """
    itinerary_chain = itinerary_suggestion.create_chain()
    result = itinerary_chain.invoke({"query": query})
    print(result)
