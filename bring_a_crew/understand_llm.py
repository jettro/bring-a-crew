from dotenv import load_dotenv
import logging

from bring_a_crew.setup_logging import setup_logging
from ollama import chat, generate
from ollama import ChatResponse

# MODEL = "phi4"
MODEL = "llama3.2"


def run_question(question):
    llm_response = generate(
        prompt=question,
        model=MODEL,
        options={
            "temperature": 1
        }
    )
    main_log.debug(llm_response)
    return llm_response.response


def run_question_with_system_msg(question):
    llm_response = generate(
        prompt=question,
        model=MODEL,
        options={
            "temperature": 1,
        },
        system=(
            "You are a scheduling assistant. You help in checking the availability of people."
            "Do not make up availability if you do not know the person's schedule."
            "Answer in short sentences, stick to the answer to the question."
        )
    )
    main_log.debug(llm_response)
    return llm_response.response


def run_chat(question, messages=None):
    if messages is None:
        _messages = [
            {"role": "system", "content": (
                "You are a scheduling assistant. You help in checking the availability of people."
                "Do not make up availability if you do not know the person's schedule."
                "Answer in short sentences, stick to the answer to the question."
            )},
        ]
    else:
        _messages = messages.copy()
    _messages.append({"role": "user", "content": question})

    llm_response = chat(
        model=MODEL,
        options={
            "temperature": 1
        },
        messages=_messages
    )
    main_log.debug(llm_response)
    _messages.append({"role": "assistant", "content": llm_response.message.content})
    return llm_response.message.content, _messages


def run_chat_with_tools(question, messages=None):
    if messages is None:
        _messages = [
            {"role": "system", "content": (
                "You are a scheduling assistant. You help in checking the availability of people."
                "Do not make up availability if you do not know the person's schedule."
                "Answer in short sentences, stick to the answer to the question."
            )},
        ]
    else:
        _messages = messages.copy()
    _messages.append({"role": "user", "content": question})

    llm_response = chat(
        model=MODEL,
        options={
            "temperature": 0
        },
        messages=_messages,
        tools=[find_person_availability]
    )
    main_log.debug(llm_response)

    if llm_response.message.tool_calls:
        for tool in llm_response.message.tool_calls:
            if tool.function.name == "find_person_availability":
                tool_response = find_person_availability(tool.function.arguments["name"])
                main_log.debug(f"Tool response: {tool_response}")
                _messages.append(llm_response.message)
                _messages.append({"role": "tool", "content": tool_response, "name": "find_person_availability"})

                llm_response = chat(
                    model=MODEL,
                    options={
                        "temperature": 1
                    },
                    messages=_messages,
                    tools=[find_person_availability]
                )
                main_log.debug(llm_response)

    _messages.append({"role": "assistant", "content": llm_response.message.content})
    return llm_response.message.content, _messages


def find_person_availability(name: str) -> str:
    main_log.debug(f"Finding availability for {name}")
    if name.lower() == "jettro":
        return "Jettro is available on Tuesday and Thursday."
    elif name.lower() == "daniel":
        return "Daniel is available on Monday to Thursday."
    elif name.lower() == "joey":
        return "Joey is available on Thursday and Friday."
    else:
        return "I do not know the availability of this person."


if __name__ == '__main__':
    _ = load_dotenv()
    setup_logging()
    main_log = logging.getLogger("main")
    main_log.setLevel(logging.DEBUG)

    # Check when Jettro is available
    # Play with temperature to see how it affects the response
    # print(run_question("When is Jettro available?"))

    # Be more explicit in what you need
    # Again, play with temperature to see how it affects the response
    # print(run_question("I need to make an appointment with Jettro, when is he available?"))

    # Adding a system message
    # print(run_question_with_system_msg("When is Jettro available?"))

    # Pass a context with the question
    # print(run_question_with_system_msg(question=(
    #     "When is jettro available?"
    #     "\nThis is the agenda of people in our office:"
    #     "\nDaniel is available on Monday till Thursday;"
    #     "\nJoey is available on Friday;"
    #     "\nJettro is available on Tuesday and Thursday;")
    # ))

    # Start memorizing multiple messages, make it a chat
    # response, current_messages = run_chat(question=(
    #     "When is jettro available?"
    #     "\nThis is the agenda of people in our office:"
    #     "\nDaniel is available on Monday to Thursday;"
    #     "\nJoey is available on Thursday and Friday;"
    #     "\nJettro is available on Tuesday and Thursday;")
    # )
    # print(response)
    # response, current_messages = run_chat(
    #     question="When are Daniel and Jettro both available?",
    #     messages=current_messages
    # )
    # print(response)

    # Use a tool to find the availability of a person
    response, current_messages = run_chat_with_tools(
        question="What days is Jettro available?"
    )
    main_log.debug(current_messages)
    print(f"Response: {response}")