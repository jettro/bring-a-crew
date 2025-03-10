# Bring a crew
This is a sample project to play around with agents. Some of the demos I have used during a talk. Below are pointers to the different demos. That way, you know where to look in case you visited one of my talks.

## Notebooks

- [Learn to work with LLMs](bring_a_crew/learn_llm.ipynb): Shows how to work with LLMs in a simple way. It explains the different elements from an LLM to start building your Agent.
- [Learn more about reasoning](bring_a_crew/learn_reasoning.ipynb): Shows the difference in output from a model trained without and with reasoning. 
- [:earn to create an Agent](bring_a_crew/learn_agent.ipynb): Shows how to create an Agent and how to use it to interact with the environment. It uses as little frameworks as possible to show the basic principles.

## Code
[Basic Agent](bring_a_crew/basic_agent.py): A basic Agent that can interact with the environment. It is a simple example to show how to create an Agent. This is the first iteration Agent that I wrote about on the blog post [Learn AI Agent basics using Python and Ollama](https://jettro.dev/learn-ai-agent-basics-using-python-and-ollama-a62108d80df9).

The other files belong to the multi-agent sample I wrote. They are comparable to the Basic Agent. The [ActionAgent](bring_a_crew/action_agent.py) is the first super class to the more specific action agents. The action agents are:
- [Schedule Manager](bring_a_crew/schedule_manager_action_agent.py): An agent that can schedule a meeting with a group of people.
- [Food Manager](bring_a_crew/food_manager_action_agent.py): An agent that can order food for a group of people during lunch.
- [Room Manager](bring_a_crew/room_manager_action_agent.py): An agent that can book a room for a group of people.

The final class is the [Orchestrator](bring_a_crew/orchestration_agent.py). This class is the proxy between the user and the different action agents. It is the class that is used to interact with the different action agents.