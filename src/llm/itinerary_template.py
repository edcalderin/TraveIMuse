from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI

from src.llm import TravelAgent
from src.llm.validations import Validation

current_directory: Path = Path(__file__).parent


class ItineraryTemplate:
    system_template: str = (current_directory / "system_template.txt").read_text()

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
