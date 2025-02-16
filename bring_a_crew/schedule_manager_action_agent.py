from bring_a_crew import action_agent_log
from bring_a_crew.action_agent import ActionAgent

def check_availability(date: str, person: str):
    action_agent_log.info("check_availability: date=%s, person=%s", date, person)
    if person.lower() == "alice":
        return f"{person} is not available in the week starting with {date}."
    elif person.lower() == "bob":
        return f"{person} is available in the week starting with {date} on Monday the 17th of February. Tuesday on the 18th of February. Thursday on the 20th of February."
    elif person.lower() == "charlie":
        return f"{person} is available in the week starting with {date} on Monday the 17th of February in the morning. Tuesday on the 18th of February. Thursday on the 20th of February. Friday on the 21st of February."
    else:
        return f"{person} is unknown to the system."


def book_person(date: str, timeslot: str, person: str):
    action_agent_log.info("book_person: date=%s, timeslot=%s, person=%s", date, timeslot, person)
    return f"{person} is booked for a meeting on {date} at {timeslot}."


schedule_manager = ActionAgent(
    name="schedule_manager",
    intro="This agent manages the schedule of people. You can check for availability of people and book them for a meeting.",
    actions={
        "check_availability": {
            "description": "Ask for the availability of a person during a week, providing the start of the week. Availability for a person is in the morning and or the afternoon.",
            "function": check_availability,
            "arguments": [
                {"name": "date", "type": "str"},
                {"name": "person", "type": "str"}
            ]
        },
        "book_person": {
            "description": "Book a person for a meeting on a given date and time.",
            "function": book_person,
            "arguments": [
                {"name": "date", "type": "str"},
                {"name": "timeslot", "type": "str"},
                {"name": "person", "type": "str"}
            ]
        }
    }
)