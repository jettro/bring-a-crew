import logging
import re
from abc import ABC

from ollama import ChatResponse
from ollama import chat

from bring_a_crew.action_agent import ActionAgent

MODEL = 'phi4'


def create_system_prompt(agents: list[ActionAgent]):
    agents_str = "\n".join([f" - `{agent.name}`; for {agent.intro}" for agent in agents])
    return f"""
You are an AI Orchestration agent following the ReAct framework, where you **Think**, **Act**, and process **Observations** in response to a given **Question**.  During thinking you analyse the question, break it down into subquestions, and decide on the actions to take to answer the question. You then act by calling other agents. After each action, you pause to observe the results of the action. You then continue the cycle by thinking about the new observation and deciding on the next action to take. You continue this cycle until you have enough information to answer the original question.

You will always follow this structured format:
Question: [User’s question]
Think: [Your reasoning about how to answer the question using available actions only]
Action: [agent]: [subquestion]
PAUSE

After receiving an **Observation**, you will continue the cycle using the new observation:
Observation: [Result from the previous action]
Think: [Decide on the next action to take.]
If further action is needed, you continue with the next action and wait for the new observation:
Action: [agent]: [subquestion]
PAUSE
Else, if the final answer is ready, you will return it:
Answer: [Use Final answer to write a friendly response with the answer to the question]

Rules:
1. Never answer a question directly; always go through the **Think → Action → PAUSE** cycle.
2. Never generate output after "PAUSE"
3. Observations will be provided as a response to an action; never generate your own output for an action.
4. These are the only available actions:
{agents_str}

Example Interactions:
- User Input:
I like to book a room for 4 people for next tuesday in the morning including lunch?
- Model Response:
Question: Is there a room available?
Think: To solve this, I need to call the agent room_manager and ask for availability.
Action: room_manager: check availability for a room on next tuesday in the morning.
PAUSE

User Provides an Observation:
- Observation: Yes I have a room available for next tuesday in the morning with a capacity of 8 people max.

Model Continues:
Observation: Yes I have a room available for next tuesday in the morning with a capacity of 8 people max.
Think: The room is available, I need to book the room.
Action: room_manager: book the room for next tuesday in the morning with a capacity of 8 people.

User Provides an Observation:
- Observation: I have book room with id max_8_people.

Model Continues:
Observation: I have book room with id max_8_people.
Think: The room is available, I need to order lunch.
Action: food_manager: prepare lunch for 4 people on next tuesday in the morning for the room with id max_8_people.

User Provides an Observation:
- Observation: Lunch will be served next tuesday for 4 people in the room max_8_people.
Think: Now that I have the result, I can provide the final answer.
Answer: I have booked a room for 4 people for next tuesday in the morning including lunch in room max_8_people.
""".strip()

class OrchestrationAgent(ABC):
    def __init__(self, name: str, description: str, agents: list[ActionAgent]):
        self.log = logging.getLogger("main.OrchestrationAgent")
        self.log.info("Initializing Orchestration Agent")

        # Initialize the messages with the system message
        self.memory = []
        system_prompt = create_system_prompt(agents=agents)
        self.memory.append(
            {
                "role": "system",
                "content": system_prompt
            }
        )
        self.log.debug(f"Agent initialized for system {system_prompt}")

        # Initialize the known actions
        self.known_agents = {}
        if agents is not None:
            for agent in agents:
                self.known_agents[agent.name] = agent

        self.max_turns = 10
        self.action_re = re.compile(r'^Action: (\w+): (.*)$')
        self.answer_re = re.compile(r'^Answer: (.*)$')

    def call_agent(self, question):
        i = 0
        next_prompt = question
        while i < self.max_turns:
            i += 1
            result = self.__handle_user_message(next_prompt)

            # Check if there is an action to run or an answer to return
            actions = [self.action_re.match(a) for a in result.split('\n') if self.action_re.match(a)]
            if actions:
                next_prompt = self.__execute_action(actions)
            else:
                return self.__extract_answer(result)

    def __execute_action(self, actions):
        action, action_input = actions[0].groups()
        if action not in self.known_agents:
            self.log.error("Unknown action: %s: %s", action, action_input)
            raise Exception("Unknown action: {}: {}".format(action, action_input))

        self.log.info(" -- running %s %s", action, action_input)
        observation = self.known_agents[action].perform_action(command=action_input)

        self.log.info("Observation: %s", observation)
        return f"Observation: {observation}"

    def __extract_answer(self, result):
        answers = [self.answer_re.match(answer) for answer in result.split('\n') if self.answer_re.match(answer)]
        if answers:
            # There is an answer to return
            self.log.info("Final answer: %s", answers[0].groups()[0])
            return answers[0].groups()[0]
        else:
            self.log.error("No action or answer found in: %s", result)
            raise Exception("No action or answer found in: {}".format(result))


    def __handle_user_message(self, message):
        self.log.info(f"Received message: {message}")
        self.memory.append({"role": "user", "content": message})
        result = self.__execute()
        self.memory.append({"role": "assistant", "content": result})
        return result

    def __execute(self) -> str:
        response: ChatResponse = chat(
            model=MODEL,
            messages=self.memory,
            options={
                "temperature": 0,
                "stop": [
                    'PAUSE'
                ]
            }
        )
        self.log.info(f"Response: {response.message.content}")
        return response.message.content
