import logging
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI

logging.basicConfig(level=logging.INFO)

current_directory: Path = Path(__file__).parent


class ItineraryAgent:
    _system_template: str = (
        current_directory / "itinerary_system_template.txt"
    ).read_text()
    _human_template: str = "#### {query} ####"
    _system_message_prompt: SystemMessagePromptTemplate = (
        SystemMessagePromptTemplate.from_template(_system_template)
    )
    _human_message_prompt: HumanMessagePromptTemplate = (
        HumanMessagePromptTemplate.from_template(_human_template)
    )
    _chat_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
        [_system_message_prompt, _human_message_prompt]
    )
    _chat_model = ChatOpenAI(temperature=0, model="gpt-4o")

    def create_chain(self) -> RunnableSequence:
        logging.info("Validation chain")

        return self._chat_prompt | self._chat_model | StrOutputParser()
