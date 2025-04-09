from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI

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
