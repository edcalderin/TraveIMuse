import logging
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.runnables import RunnablePassthrough, RunnableSequence
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

logging.basicConfig(level=logging.INFO)

current_directory: Path = Path(__file__).parent


class Validation(BaseModel):
    plan_is_valid: str = Field(
        description="This field is 'yes' if the plan is feasible, 'no' otherwise"
    )
    updated_request: str = Field(description="Your update to plan")


class ValidationAgent:
    _system_template: str = Path(
        current_directory / "validation_system_template.txt"
    ).read_text()
    _human_template: str = "### {query} ###"
    _parser: PydanticOutputParser = PydanticOutputParser(pydantic_object=Validation)
    _system_message_prompt: SystemMessagePromptTemplate = (
        SystemMessagePromptTemplate.from_template(_system_template)
    )
    _human_message_prompt: HumanMessagePromptTemplate = (
        HumanMessagePromptTemplate.from_template(_human_template)
    )
    _chat_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
        [_system_message_prompt, _human_message_prompt]
    )
    _chat_model = ChatOpenAI(model="gpt-4o", temperature=0.2)

    def create_chain(self) -> RunnableSequence:
        logging.info("Validation chain")
        return (
            {
                "query": RunnablePassthrough(),
                "format_instructions": self._parser.get_format_instructions(),
            }
            | self._validation_prompt.chat_prompt
            | self._chat_model
            | self._parser
        )
