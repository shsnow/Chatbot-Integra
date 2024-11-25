from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages.ai import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import dotenv, os
import google.generativeai as genai
from db import create_ticket, update_ticket, get_user_id_by_rut

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

# Nodo inicial del chatbot con mensaje de bienvenida
def chatbot_with_welcome_msg(state: OrderState) -> OrderState:
    if state["messages"]:
        new_output = llm.invoke([CHATBOT_TECNICHIAN] + state["messages"])
    else:
        new_output = AIMessage(content=WELCOME_MSG)
    return state | {"messages": [new_output]}

# Nodo para lógica de clasificación
def chatbotDes(state: OrderState) -> OrderState:
    if state["messages"]:
        new_output = llmdes.invoke([CLASSIFICATION_PROMPT] + state["messages"])
    else:
        new_output = AIMessage(content=WELCOME_MSG)
    return state | {"messages": [new_output]}

# Nodo humano
def human_node(state: OrderState) -> OrderState:
    last_msg = state["messages"][-1]
    user_input = last_msg.content
    if user_input.lower() in {"q", "quit", "exit", "goodbye"}:
        state["finished"] = True
    return state | {"messages": [("user", user_input)]}

def maybe_exit_human_node(state: OrderState) -> Literal["chatbot", "__end__"]:
    """Decidir la próxima acción basada en la respuesta del usuario."""
    #resolved = ["muchas gracias", "gracias", "solucionado", "resuelto", "me sirvió", "me ayudó","me funcionó"]
    resolved = ["muchas gracias", "gracias"]
    unresolved = ["no me sirvió", "quiero hablar con un técnico", "no resuelto"]
    technical_question = ["pregunta técnica", "técnica", "cómo hago", "cómo funciona"]

    if "rut" not in state or not state["rut"]:
        state["rut"] = "20.404.282-9"  # RUT de prueba

    user_message = state["messages"][-1].content.lower()
    # Verificamos si el usuario quiere resolver el ticket
    if any(word in user_message for word in resolved):
        print("Usuario reportó que su problema fue resuelto.")
        # Crear un ticket con el estado 'Resuelto'
        userId = get_user_id_by_rut(state["rut"])
        #create_ticket(rut, title, description, category_id, state_id, sla_id, user_id=None, asignacion="Chatbot"):
        create_ticket(
            rut=state["rut"],
            title="Problema Resuelto",
            description="El usuario reportó que su problema fue solucionado.",
            category_id=1,  # Ajusta según la categoría predeterminada
            state_id=2,     # Estado 'Resuelto'
            sla_id=1,       # SLA predeterminado
            user_id=userId,   # ID del usuario (opcional)
            )
        state["finished"] = True
        state["messages"].append(AIMessage(content="Ticket resuelto y guardado."))
        return END  # Finalizamos la interacción

    # Si el usuario quiere escalar el ticket
    elif any(word in user_message for word in unresolved):
        # Actualizar el ticket y asignarlo a un Técnico Nivel 2
        userId = get_user_id_by_rut(state["rut"])
        #create_ticket(rut, title, description, category_id, state_id, sla_id, user_id=None, asignacion="Chatbot"):
        create_ticket(
            rut=state["rut"],
            title="Problema Resuelto",
            description="El usuario reportó que su problema fue solucionado.",
            category_id=1,  # Ajusta según la categoría predeterminada
            state_id=1,     # Estado 'abierto'
            sla_id=1,       # SLA predeterminado
            user_id=userId,   # ID del usuario (opcional)
            )
        state["finished"] = True
        state["messages"].append(AIMessage(content="Ticket asignado a Técnico Nivel 2."))
        print("Ticket asignado a Técnico Nivel 2.")
        return END  # Finalizamos la interacción

    # Si el usuario tiene una pregunta técnica
    elif any(word in user_message for word in technical_question):
        print("Usuario tiene una pregunta técnica, regresando al chatbot.")
        return "chatbot"  # Si el usuario tiene una pregunta técnica, regresa al chatbot

    else:
        print("Regresando al chatbot por defecto.")
        return "chatbot"  # Para cualquier otra entrada, regresa al chatbot
