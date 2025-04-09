from dataclasses import dataclass
from pathlib import Path

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.runnables import RunnablePassthrough, RunnableSequence
from langchain_openai import ChatOpenAI

from src.locations import Trip

current_directory: Path = Path(__file__).parent


@dataclass(frozen=True)
class MappingTemplate:
    _system_template: str = (current_directory / "system_template.txt").read_text()
    _human_template: str = """#### {agent_suggestion} ####"""

    _parser = PydanticOutputParser(pydantic_object=Trip)
    _system_message_prompt = SystemMessagePromptTemplate.from_template(_system_template)
    _human_message_prompt = HumanMessagePromptTemplate.from_template(_human_template)
    _chat_prompt = ChatPromptTemplate.from_messages(
        [_system_message_prompt, _human_message_prompt]
    )
    _chat_model = ChatOpenAI(model="gpt-4o", temperature=0.2)

    def _create_agent_chain(self) -> RunnableSequence:
        return (
            {
                "format_instructions": RunnablePassthrough(),
                "agent_suggestion": RunnablePassthrough(),
            }
            | self._chat_prompt
            | self._chat_model
            | self._parser
        )
