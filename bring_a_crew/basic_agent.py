import re

from dotenv import load_dotenv
import logging

from bring_a_crew.setup_logging import setup_logging
from ollama import chat
from ollama import ChatResponse

# MODEL = 'deepseek-r1:8b'
# MODEL = 'deepseek-r1:14b'
MODEL = 'phi4'

system_prompt = """
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
 - `calculate`; for calculator style math operations only
 - `dog_weight_for_breed`; for finding the weight of a dog breed
 
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
    def __init__(self, system=""):
        self.log = logging.getLogger("main.Agent")
        self.system = system
        self.messages = []
        if self.system:
            self.log.debug(f"Agent initialized for system {self.system}")
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message):
        self.log.info(f"Received message: {message}")
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self) -> str:
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


def calculate(what):
    return eval(what)


def average_dog_weight(name: str):
    main_log.info("Calculating average dog weight for '%s'", name)
    compare_name = name.lower().strip()
    if compare_name == "scottish terrier":
        return "Scottish Terriers average 20 lbs"
    elif compare_name == "border collie":
        return "a Border Collies average weight is 37 lbs"
    elif compare_name == "poodle":
        return "a poodles average weight is 27 lbs"
    else:
        return (f"Have no idea about the average weight for {name}, but an "
                f"average dog weights 50 lbs")


def query(question, max_turns=10):
    i = 0
    bot = Agent(system_prompt)
    next_prompt = question
    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        actions = [action_re.match(a) for a in result.split('\n') if action_re.match(a)]
        if actions:
            # There is an action to run
            action, action_input = actions[0].groups()
            if action not in known_actions:
                main_log.error("Unknown action: %s: %s", action, action_input)
                raise Exception("Unknown action: {}: {}".format(action, action_input))
            main_log.info(" -- running %s %s", action, action_input)
            observation = known_actions[action](action_input)
            main_log.info("Observation: %s", observation)
            next_prompt = "Observation: {}".format(observation)
        else:
            main_log.info("About to return the final answer: %s", result)
            return


known_actions = {
    "calculate": calculate,
    "dog_weight_for_breed": average_dog_weight
}

action_re = re.compile(r'^Action: (\w+): (.*)$')

if __name__ == '__main__':
    # https://til.simonwillison.net/llms/python-react-pattern
    _ = load_dotenv()
    setup_logging()
    main_log = logging.getLogger("main")
    main_log.setLevel(logging.INFO)
    logging.getLogger("main.Agent").setLevel(logging.INFO)

    question = """I have 2 dogs, a border collie and a scottish terrier. \
    What is their combined weight?"""
    query(question)
