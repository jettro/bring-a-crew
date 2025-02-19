import logging

from dotenv import load_dotenv

from bring_a_crew.orchestration_agent import OrchestrationAgent
from bring_a_crew.room_manager_action_agent import create_agent as create_agent_room_manager
from bring_a_crew.schedule_manager_action_agent import create_agent as create_agent_schedule_manager
from bring_a_crew.food_manager_action_agent import create_agent as create_agent_food_manager
from bring_a_crew.setup_logging import setup_logging


def main(question: str):

    room_manager = create_agent_room_manager()
    schedule_manager = create_agent_schedule_manager()
    food_manager = create_agent_food_manager()

    or_agent = OrchestrationAgent(
        name="orchestration_agent",
        description="This agent orchestrates the conversation between the user and the other agents",
        agents=[room_manager, food_manager, schedule_manager]
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


    main("Organise a meeting between Bob and Charlie somewhere next week, book a room and order lunch.")