import re
from dotenv import load_dotenv
import logging

from bring_a_crew.setup_logging import setup_logging
from ollama import chat
from ollama import ChatResponse

MODEL = 'phi4'


def create_system_prompt(actions):
    actions_str = "\n".join([f" - `{action}`; for {value["description"]}" for action, value in actions.items()])
    return f"""
You are an AI agent following the ReAct framework, where you **Think**, **Act**, and process **Observations** in response to a given **Question**.  During thinking you analyse the question, break it down into subquestions, and decide on the actions to take to answer the question. You then act by performing the actions you decided on. After each action, you pause to observe the results of the action. You then continue the cycle by thinking about the new observation and deciding on the next action to take. You continue this cycle until you have enough information to answer the original question.

You will always follow this structured format:
Question: [User’s question]
Think: [Your reasoning about how to answer the question using available actions only]
Action: [action]: [arguments]
PAUSE

After receiving an **Observation**, you will continue the cycle using the new observation:
Observation: [Result from the previous action]
Think: [Decide on the next action to take.]
If further action is needed, you continue with the next action and wait for the new observation:
Action: [action]: [arguments]
PAUSE
Else, if the final answer is ready, you will return it:
Answer: [Use Final answer to write a friendly response with the answer to the question]

Rules:
1. Never answer a question directly; always go through the **Think → Action → PAUSE** cycle.
2. Never generate output after "PAUSE"
3. Observations will be provided as a response to an action; never generate your own output for an action.
4. These are the only available actions:
{actions_str}

Example Interactions:
- User Input:
What is the weight for a bulldog?
- Model Response:
Question: What is the weight for a bulldog?
Think: To solve this, I need to perform the dog_weight_for_breed action with the argument bulldog.
Action: dog_weight_for_breed: bulldog
PAUSE

User Provides an Observation:
- Observation: a Bulldogs average weight is 40 lbs

Model Continues:
Observation: a Bulldogs average weight is 40 lbs
Think: Now that I have the result, I can provide the final answer.
Answer: The average weight for a Bulldog is 40 lbs.
""".strip()


class Agent:
    def __init__(self, system="", actions=None):
        self.log = logging.getLogger("main.Agent")
        self.log.info("Initializing Agent")

        # Initialize the messages with the system message
        self.messages = []
        if system:
            self.messages.append({"role": "system", "content": system})
            self.log.debug(f"Agent initialized for system {system}")

        # Initialize the known actions
        self.known_actions = {}
        if actions is not None:
            for action, value in actions.items():
                self.known_actions[action] = value["function"]

        self.max_turns = 10
        self.action_re = re.compile(r'^Action: (\w+): (.*)$')
        self.answer_re = re.compile(r'^Answer: (.*)$')

    def handle_user_message(self, message):
        self.log.info(f"Received message: {message}")
        self.messages.append({"role": "user", "content": message})
        result = self.__execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def ask_question(self, question):
        i = 0
        next_prompt = question
        while i < self.max_turns:
            i += 1
            result = self.handle_user_message(next_prompt)

            # Check if there is an action to run or an answer to return
            actions = [self.action_re.match(a) for a in result.split('\n') if self.action_re.match(a)]
            if actions:
                next_prompt = self.__execute_action(actions)
            else:
                return self.__extract_answer(result)

    def __execute_action(self, actions):
        action, action_input = actions[0].groups()
        if action not in self.known_actions:
            main_log.error("Unknown action: %s: %s", action, action_input)
            raise Exception("Unknown action: {}: {}".format(action, action_input))

        main_log.info(" -- running %s %s", action, action_input)
        observation = self.known_actions[action](action_input)

        main_log.info("Observation: %s", observation)
        return f"Observation: {observation}"

    def __extract_answer(self, result):
        answers = [self.answer_re.match(answer) for answer in result.split('\n') if self.answer_re.match(answer)]
        if answers:
            # There is an answer to return
            main_log.info("Final answer: %s", answers[0].groups()[0])
            return answers[0].groups()[0]
        else:
            main_log.error("No action or answer found in: %s", result)
            raise Exception("No action or answer found in: {}".format(result))

    def __execute(self) -> str:
        response: ChatResponse = chat(
            model=MODEL,
            messages=self.messages,
            options={
                "temperature": 0,
                "stop": [
                    'PAUSE'
                ]
            }
        )
        self.log.info(f"Response: {response.message.content}")
        return response.message.content


def find_person_availability(name: str):
    main_log.info("Finding person availability for '%s'", name)
    compare_name = name.lower().strip()
    if compare_name == "jettro":
        return "Jettro is available on Monday and Tuesday"
    elif compare_name == "daniel":
        return "Daniel is available on Monday till Thursday"
    elif compare_name == "joey":
        return "Joey is available from Monday till Friday"
    else:
        return f"Have no idea about the availability for {name}"


def find_meeting_room_availability(name: str):
    main_log.info("Finding meeting room availability for '%s'", name)
    compare_name = name.lower().strip()
    if compare_name == "room 1":
        return "Room 1 is available on Monday and Tuesday"
    elif compare_name == "room 2":
        return "Room 2 is available on Tuesday and Thursday"
    elif compare_name == "room 3":
        return "Room 3 is available from Monday till Friday"
    else:
        return f"Have no idea about the availability for {name}"


def complete_agent(question=None):
    # Set up the Agent
    meeting_actions = {
        "find_person_availability": {
            "description": "finding a person using the name and returning their availability",
            "function": find_person_availability
        },
        "find_meeting_room_availability": {
            "description": "finding a meeting room using the name and returning its availability",
            "function": find_meeting_room_availability
        }
    }
    system_prompt = create_system_prompt(meeting_actions)
    bot = Agent(system_prompt, meeting_actions)

    # Ask a question
    final_answer = bot.ask_question(sample_question)
    print("Answer:", final_answer)


if __name__ == '__main__':
    _ = load_dotenv()
    setup_logging()
    main_log = logging.getLogger("main")
    main_log.setLevel(logging.INFO)
    logging.getLogger("main.Agent").setLevel(logging.INFO)

    sample_question = """I am Jettro, can you book a meeting for me with Daniel and Joey on Monday in Room 3?"""
    complete_agent(sample_question)
