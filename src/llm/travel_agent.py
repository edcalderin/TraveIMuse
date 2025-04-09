import logging
from time import time

from dotenv import load_dotenv
from langchain_core.runnables import RunnablePassthrough, RunnableSequence
from langchain_openai import ChatOpenAI

from src.llm.validations import ValidationTemplate

load_dotenv()

logging.basicConfig(level=logging.INFO)


class TravelAgent:
    def __init__(self, temperature: float = 0, model="gpt-4o") -> None:
        self._chat_model = ChatOpenAI(model=model, temperature=temperature)
        self._validation_prompt = ValidationTemplate()

    def _create_chain(self) -> RunnableSequence:
        return (
            {
                "query": RunnablePassthrough(),
                "format_instructions": RunnablePassthrough(),
            }
            | self._validation_prompt.chat_prompt
            | self._chat_model
            | self._validation_prompt.parser
        )

    def validate_travel(self, query: str):
        logging.info("Validating query")
        t1 = time()
        logging.info(
            f"Calling validation ({self._chat_model.model_name} model) on user input"
        )
        chain = self._create_chain()
        response = chain.invoke(
            {
                "query": query,
                "format_instructions": 
                    self._validation_prompt.parser.get_format_instructions(),
            }
        )
        t2 = time()
        logging.info(f"Time to validate the request ({round(t2 - t1, 2)})")
        return response


if __name__ == "__main__":
    query = """
        I want to do a 5 day roadtrip from Earth to Mars.
        I want to visit Perito Moreno glaciar.
    """
    travel_agent = TravelAgent()
    response = travel_agent.validate_travel(query)
    logging.info(response)
