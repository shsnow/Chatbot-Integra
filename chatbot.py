# chatbot.py
import json
from datetime import datetime
from PIL import Image as PILImage
import tempfile
from langgraph.graph import StateGraph, START, END

from typing_extensions import TypedDict

from nodes import chatbot_with_welcome_msg, human_node, maybe_exit_human_node, OrderState
import dotenv, os
import google.generativeai as genai

# Cargar variables de entorno
dotenv.load_dotenv()

WELCOME_MSG = os.getenv("WELCOME_MSG", "Bienvenidos soy el chatbot de soporte técnico nivel 1, ¿en qué puedo ayudarte hoy?")
CLASSIFICATION_PROMPT = os.getenv("CLASSIFICATION_PROMPT", "¿Se ha resuelto tu problema? Si es así, responde 'muchas gracias'. Si no es así, responde 'no me sirvió'. Si deseas hablar con un técnico de nivel 2, por favor, responde 'quiero hablar con un técnico de nivel 2'. Si respondes 'muchas gracias' o algo relacionado, el chatbot responde 'resolved'. Si respondes 'no me sirvió' o deseas un técnico de nivel 2, el chatbot responde 'unresolved'. Si tienes una pregunta técnica, el chatbot responde 'technical question'.")

def save_and_display_graph(graph):
    try:
        # Crear archivo temporal
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        graph_image = graph.get_graph().draw_mermaid_png()
        with open(temp_file, "wb") as f:
            f.write(graph_image)

        # Abrir la imagen usando PIL para asegurarse de que es válida
        img = PILImage.open(temp_file)
        img.show()  # Mostrar la imagen

        print(f"La imagen del grafo se guardó en: {temp_file}")
    except Exception as e:
        print("Error al mostrar el grafo:", e)

def generate_ticket(rut, problem_description, status="En progreso", sla="48 horas", category="Soporte general", assignment="Chatbot"):
    """
    Crea un ticket con los detalles del problema y el estado actual.
    """
    ticket = {
        "rut": rut,
        "estado_ticket": status,
        "sla": sla,
        "categoria": category,
        "descripcion_problema": problem_description,
        "asignacion": assignment,
        "fecha_creacion": str(datetime.now())
    }
    return ticket

def modify_ticket(ticket, new_status, new_assignment):
    """
    Modifica el estado y asignación de un ticket.
    """
    ticket["estado_ticket"] = new_status
    ticket["asignacion"] = new_assignment
    return ticket

def qa(input_data):
    """
    Interactúa con el chatbot y devuelve una respuesta para Streamlit.
    """
    question = input_data.get("question", "")
    chat_history = input_data.get("chat_history", [])

    # Estado inicial
    state = {"messages": [{"role": "user", "content": question}], "finished": False}

    # Configurar el grafo
    graph_builder = StateGraph(OrderState)
    graph_builder.add_node("chatbot", chatbot_with_welcome_msg)
    graph_builder.add_node("human", human_node)
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", "human")
    graph_builder.add_conditional_edges("human", maybe_exit_human_node)
    chat_with_human_graph = graph_builder.compile()

    # Invocar el grafo
    response = chat_with_human_graph.invoke(state)

    # Extraer la última respuesta generada por el chatbot
    if response["messages"]:
        last_message = response["messages"][-1]
        return {"answer": last_message.content}  # Acceso directo a .content
    else:
        return {"answer": "Lo siento, no entendí tu solicitud."}


def generate_graph_image():
    """
    Genera la imagen del grafo y la guarda en un archivo temporal.
    Retorna la ruta del archivo de imagen.
    """
    try:
        graph_builder = StateGraph(OrderState)
        graph_builder.add_node("chatbot", chatbot_with_welcome_msg)
        graph_builder.add_node("human", human_node)
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("chatbot", "human")
        graph_builder.add_conditional_edges("human", maybe_exit_human_node)
        chat_with_human_graph = graph_builder.compile()

        # Crear archivo temporal
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        graph_image = chat_with_human_graph.get_graph().draw_mermaid_png()
        with open(temp_file, "wb") as f:
            f.write(graph_image)

        return temp_file
    except Exception as e:
        print("Error al generar la imagen del grafo:", e)
        return None
