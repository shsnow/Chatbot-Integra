
from nodes import *
import dotenv,os
from PIL import Image as PILImage
import tempfile
from datetime import datetime


#---- Funciones varias

# Función para guardar y mostrar el grafo
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


# Construccion del grafo
graph_builder = StateGraph(OrderState)

# Añadir nodos y aristas
graph_builder.add_node("chatbot", chatbot_with_welcome_msg)
graph_builder.add_node("human", human_node)

graph_builder.add_edge(START, "chatbot") 
graph_builder.add_edge("chatbot", "human");
graph_builder.add_conditional_edges("human", maybe_exit_human_node)

# Compilar el grafo
chat_with_human_graph = graph_builder.compile()




# Mostrar el grafo
#save_and_display_graph(chat_with_human_graph)

# Inicializar el grafo, aqui va infinite loop
state = chat_with_human_graph.invoke({"messages": []})
