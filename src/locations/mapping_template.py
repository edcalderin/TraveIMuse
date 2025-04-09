from dataclasses import dataclass

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.runnables import RunnablePassthrough, RunnableSequence
from langchain_openai import ChatOpenAI

from src.locations import Trip


@dataclass(frozen=True)
class MappingTemplate:
    _system_template: str = """
You an agent who converts detailed travel plans into a simple list of locations.

The itinerary will be denoted by four hashtags. Convert it into list of places that
they should visit. Try to include the specific address of each location.

Your output should always contain the start and end point of the trip, and may also
include a list of waypoints. It should also include a mode of transit. The number of
waypoints cannot exceed 20. If you can't infer the mode of transit, make a best guess
given the trip location.

For example:

####
Itinerary for a 2-day driving trip within London:
- Day 1:
- Start at Buckingham Palace (The Mall, London SW1A 1AA)
- Visit the Tower of London (Tower Hill, London EC3N 4AB)
- Explore the British Museum (Great Russell St, Bloomsbury, London WC1B 3DG)
- Enjoy shopping at Oxford Street (Oxford St, London W1C 1JN)
- End the day at Covent Garden (Covent Garden, London WC2E 8RF)
- Day 2:
- Start at Westminster Abbey (20 Deans Yd, Westminster, London SW1P 3PA)
- Visit the Churchill War Rooms (Clive Steps, King Charles St, London SW1A 2AQ)
- Explore the Natural History Museum (Cromwell Rd, Kensington, London SW7 5BD)
- End the trip at the Tower Bridge (Tower Bridge Rd, London SE1 2UP)
#####

Output:
Start: Buckingham Palace, The Mall, London SW1A 1AA
End: Tower Bridge, Tower Bridge Rd, London SE1 2UP
Waypoints: ["Tower of London, Tower Hill, London EC3N 4AB", "British Museum, Great
Russell St, Bloomsbury, London WC1B 3DG", "Oxford St, London W1C 1JN", "Covent Garden,
London WC2E 8RF","Westminster, London SW1A 0AA", "St. James's Park, London", "Natural
History Museum, Cromwell Rd, Kensington, London SW7 5BD"]
Transit: driving

Transit can be only one of the following options: "driving", "train", "bus" or "flight".

{format_instructions}
    """

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


if __name__ == "__main__":
    mapping_template = MappingTemplate()
    chain = mapping_template._create_agent_chain()
    itinerary: str = """
    Itinerary for a 2-day driving trip within London:
- Day 1:
- Start at Buckingham Palace (The Mall, London SW1A 1AA)
- Visit the Tower of London (Tower Hill, London EC3N 4AB)
- Explore the British Museum (Great Russell St, Bloomsbury, London WC1B 3DG)
- Enjoy shopping at Oxford Street (Oxford St, London W1C 1JN)
- End the day at Covent Garden (Covent Garden, London WC2E 8RF)
- Day 2:
- Start at Westminster Abbey (20 Deans Yd, Westminster, London SW1P 3PA)
- Visit the Churchill War Rooms (Clive Steps, King Charles St, London SW1A 2AQ)
- Explore the Natural History Museum (Cromwell Rd, Kensington, London SW7 5BD)
- End the trip at the Tower Bridge (Tower Bridge Rd, London SE1 2UP)
    """
    response = chain.invoke(
        {
            "format_instructions": mapping_template._parser.get_format_instructions(),
            "agent_suggestion": itinerary,
        }
    )
    print(response)
