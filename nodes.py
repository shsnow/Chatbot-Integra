
from typing import Annotated
from typing_extensions import TypedDict
import google.generativeai as genai
from langchain_core.messages.ai import AIMessage
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
import dotenv,os
from langgraph.graph.message import add_messages
from typing import Literal
from prompts import *

# Autenticación de la API de Google Gemini
dotenv.load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")
llmdes = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")
#message_history = [CLASSIFICATION_PROMPT] + state["messages"]
#llm.invoke(message_history)]}

class OrderState(TypedDict):
    """State representing the customer's order conversation."""

    # The chat conversation. This preserves the conversation history
    # between nodes. The `add_messages` annotation indicates to LangGraph
    # that state is updated by appending returned messages, not replacing
    # them.
    messages: Annotated[list, add_messages]

    # The customer's in-progress order.
    order: list[str]

    # Flag indicating that the order is placed and completed.
    finished: bool
 

def human_node(state: OrderState) -> OrderState:
    """Display the last model message to the user, and receive the user's input."""
    last_msg = state["messages"][-1]
    print("Model:", last_msg.content)

    user_input = input("Usuario: ")

    # If it looks like the user is trying to quit, flag the conversation
    # as over.
    if user_input in {"q", "quit", "exit", "goodbye"}:
        state["finished"] = True

    return state | {"messages": [("user", user_input)]}


def chatbot_with_welcome_msg(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    if state["messages"]:
        # If there are messages, continue the conversation with the Gemini model.
        new_output = llm.invoke([CHATBOT_TECNICHIAN] + state["messages"])
    else:
        # If there are no messages, start with the welcome message.
        new_output = AIMessage(content=WELCOME_MSG)

    return state | {"messages": [new_output]}

def chatbotDes(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    if state["messages"]:
        # If there are messages, continue the conversation with the Gemini model.
        new_output = llmdes.invoke([CLASSIFICATION_PROMPT] + state["messages"])
    else:
        # If there are no messages, start with the welcome message.
        new_output = AIMessage(content=WELCOME_MSG)

    return state | {"messages": [new_output]}


def maybe_exit_human_node(state: OrderState) -> Literal["chatbot", "__end__"]:
    """Route to the chatbot, unless it looks like the user is exiting."""
    if state.get("finished", False):
        return END
    else:
        user_message = state["messages"][-1].content
        classification = user_message.lower()# isar un modelo para transformar todas las resspuestas a una de esas 3 salidas que se piden
        if "resolved" in classification:
            print("Nos alegra saber que pudimos ayudarte. ¡Gracias por usar nuestro servicio!")
            #cerrar el ticket
            return END
        elif "unresolved" in classification:
            print("Lamentamos que no hayamos podido ayudarte. Te conectaremos con otro técnico.")
            #derivar el ticket a un tecnico nivel 2
            return END
        elif "technical question" in classification:
            return "chatbot"
        else:
            return "chatbot"
