
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI

from src.llm.travel_agent import TravelAgent
from src.llm.validations import Validation


class ItineraryTemplate:
    system_template: str = """
    You are a travel agent who helps users make exciting travel plans.

    The user's request will be denoted by four hashtags. Convert the user's request
    into a detailed itinerary describing the places they should visit and the things
    they should do.

    Try to include the specific address of each location.

    Remember to take the user's preferences and timeframe into account, and give them
    an itinerary that would be fun and doable given their constraints.

    Return the itinerary as a bulleted list with clear start and end locations.
    Be sure to mention the type of transit for the trip.
    If specific start and end locations are not given, choose ones that you think are
    suitable and give specific addresses.
    Your output must be the list and nothing else.
    """

    human_template: str = "#### {query} ####"

    system_message_prompt: SystemMessagePromptTemplate = (
        SystemMessagePromptTemplate.from_template(system_template)
    )
    human_message_prompt: HumanMessagePromptTemplate = (
        HumanMessagePromptTemplate.from_template(human_template)
    )
    chat_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )
    chat_model = ChatOpenAI(temperature=0, model="gpt-4o")

    def create_chain(self) -> RunnableSequence:
        return self.chat_prompt | self.chat_model | StrOutputParser()


if __name__ == "__main__":
    travel_agent = TravelAgent()
    query = """
        I want to do a 5 day roadtrip from Monteria to Bogota.
        I want to visit some interesting restaurantes in between.
    """
    response: Validation = travel_agent.validate_travel(query)
    if response.plan_is_valid == "yes":
        itinerary_template = ItineraryTemplate()
        chain = itinerary_template.create_chain()
        response = chain.invoke({"query": query})
        print(response)
