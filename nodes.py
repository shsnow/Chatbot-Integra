# nodes.py
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages.ai import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import dotenv, os
import google.generativeai as genai

# Cargar variables de entorno
dotenv.load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Configurar los modelos LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")
llmdes = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")

# Variables de entorno
WELCOME_MSG = os.getenv("WELCOME_MSG", "Bienvenidos soy el chatbot de soporte técnico nivel 1, ¿en qué puedo ayudarte hoy?")
CLASSIFICATION_PROMPT = os.getenv("CLASSIFICATION_PROMPT", "¿Se ha resuelto tu problema? Si es así, responde 'muchas gracias'. Si no es así, responde 'no me sirvió'. Si deseas hablar con un técnico de nivel 2, por favor, responde 'quiero hablar con un técnico de nivel 2'. Si respondes 'muchas gracias' o algo relacionado, el chatbot responde 'resolved'. Si respondes 'no me sirvió' o deseas un técnico de nivel 2, el chatbot responde 'unresolved'. Si tienes una pregunta técnica, el chatbot responde 'technical question'.")

# Definir el mensaje inicial del chatbot
CHATBOT_TECNICHIAN = (
    "system",
    "Eres un técnico nivel 1 especializado en soporte técnico básico. "
    "Una de las características principales del soporte de nivel 1 es su enfoque en la eficiencia y rapidez. "
    "Los problemas abordados en este nivel suelen resolverse en poco tiempo, permitiendo a la organización manejar un alto volumen de consultas diarias. "
    "Si el problema no puede resolverse en este nivel, el caso se deriva al nivel 2, donde técnicos con mayor experiencia y conocimientos más avanzados se encargan de investigarlo y solucionarlo. "
    "La principal cualidad asociada a los técnicos de nivel 1 es que son generalistas del soporte de IT, ya que conocen los fundamentos de la asistencia de la mayoría (si no de todos) los servicios utilizados por la empresa. "
    "Esto les permite resolver gran parte de los problemas, liberando a los niveles 2 para fallos más complicados. "
    "Proporciona asistencia técnica al usuario final a través de los canales del help desk (teléfono, correo electrónico, Teams o web chat). "
    "Resuelve problemas técnicos. "
    "Se despide formalmente!"
)

class OrderState(TypedDict):
    """State representing the customer's order conversation."""
    messages: Annotated[list, add_messages]
    order: list[str]
    finished: bool

# Funciones de los nodos de interacción

def chatbot_with_welcome_msg(state: OrderState) -> OrderState:
    """Nodo inicial del chatbot con mensaje de bienvenida."""
    if state["messages"]:
        # Continuar la conversación con el modelo Gemini
        new_output = llm.invoke([CHATBOT_TECNICHIAN] + state["messages"])
    else:
        # Iniciar con el mensaje de bienvenida
        new_output = AIMessage(content=WELCOME_MSG)

    return state | {"messages": [new_output]}

def chatbotDes(state: OrderState) -> OrderState:
    """Nodo del chatbot con lógica de clasificación."""
    if state["messages"]:
        # Continuar la conversación con el modelo Gemini usando el prompt de clasificación
        new_output = llmdes.invoke([CLASSIFICATION_PROMPT] + state["messages"])
    else:
        # Iniciar con el mensaje de bienvenida
        new_output = AIMessage(content=WELCOME_MSG)

    return state | {"messages": [new_output]}

def human_node(state: OrderState) -> OrderState:
    """Nodo de interacción con el usuario."""
    last_msg = state["messages"][-1]  # Último mensaje
    user_input = last_msg.content  # Accede directamente al contenido

    if user_input.lower() in {"q", "quit", "exit", "goodbye"}:
        state["finished"] = True

    return state | {"messages": [("user", user_input)]}

def maybe_exit_human_node(state: OrderState) -> Literal["chatbot", "__end__"]:
    """Decidir la próxima acción basada en la respuesta del usuario."""
    resolved = ["muchas gracias", "gracias", "solucionado", "resuelto"]
    unresolved = ["no me sirvió", "quiero hablar con un técnico", "no resuelto"]
    technical_question = ["pregunta técnica", "tecnica", "cómo hago", "cómo funciona"]

    # Asegúrate de que hay mensajes en el estado
    if not state["messages"]:
        return "chatbot"

    # Obtener el último mensaje del usuario
    user_message = state["messages"][-1].content.lower()

    if any(word in user_message for word in resolved):
        state["finished"] = True  # Marcar la conversación como terminada
        return END
    elif any(word in user_message for word in unresolved):
        state["finished"] = True  # Marcar la conversación como terminada
        return END
    elif any(word in user_message for word in technical_question):
        return "chatbot"
    else:
        return "chatbot"

