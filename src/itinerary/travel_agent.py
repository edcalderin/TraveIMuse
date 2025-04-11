import logging

from dotenv import load_dotenv
from langchain_core.runnables import RunnablePassthrough, RunnableSequence
from langchain_openai import ChatOpenAI

from src.itinerary.validations import ValidationTemplate

load_dotenv()

logging.basicConfig(level=logging.INFO)


class TravelAgent:
    def __init__(self, temperature: float = 0, model="gpt-4o") -> None:
        self._chat_model = ChatOpenAI(model=model, temperature=temperature)
        self._validation_prompt = ValidationTemplate()
        self._parser = self._validation_prompt.parser

    def create_chain(self) -> RunnableSequence:
        return (
            {
                "query": RunnablePassthrough(),
                "format_instructions": self._parser.get_format_instructions(),
            }
            | self._validation_prompt.chat_prompt
            | self._chat_model
            | self._parser
        )
