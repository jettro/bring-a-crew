from dotenv import load_dotenv
import logging

from bring_a_crew.food_manager_action_agent import food_manager
from bring_a_crew.orchestration_agent import OrchestrationAgent, ActionAgent
from bring_a_crew.room_manager_action_agent import room_manager
from bring_a_crew.setup_logging import setup_logging


def main(question: str):

    or_agent = OrchestrationAgent(
        name="orchestration_agent",
        description="This agent orchestrates the conversation between the user and the other agents",
        agents=[room_manager, food_manager]
    )

    response = or_agent.call_agent(question)
    main_log.info("Final response: %s", response)


if __name__ == "__main__":
    _ = load_dotenv()
    setup_logging()
    main_log = logging.getLogger("main")
    main_log.setLevel(logging.INFO)
    logging.getLogger("main.OrchestrationAgent").setLevel(logging.INFO)
    logging.getLogger("main.ActionAgent").setLevel(logging.DEBUG)


    main("Book a room for a meeting with 3 persons on Monday the 17th of February 2025 morning with lunch.")