
from nodes import *
import dotenv,os
from PIL import Image as PILImage
import tempfile




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


# Start building a new graph.
graph_builder = StateGraph(OrderState)

# Add the chatbot and human nodes to the app graph.
graph_builder.add_node("chatbot", chatbot_with_welcome_msg)
graph_builder.add_node("human", human_node)

graph_builder.add_edge(START, "chatbot") 
graph_builder.add_edge("chatbot", "human");
graph_builder.add_conditional_edges("human", maybe_exit_human_node)

chat_with_human_graph = graph_builder.compile()




# Mostrar el grafo
#save_and_display_graph(chat_with_human_graph)

state = chat_with_human_graph.invoke({"messages": []})
