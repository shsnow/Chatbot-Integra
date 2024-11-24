import time
import streamlit as st
from streamlit_chat import message
from chatbot import qa

# Configuración de la página
st.set_page_config(page_title="ChatBot Integra", page_icon="🤖")
st.title("Chat Integra")
st.caption("¡Hola! Bienvenido al chat de soporte técnico nivel 1.")

# Inicializar el historial del chat
if "history" not in st.session_state:
    st.session_state["history"] = []

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Mostrar mensajes anteriores
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrada del usuario
if prompt := st.chat_input("¿En qué te puedo ayudar?"):
    # Agregar mensaje del usuario
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar la respuesta del chatbot
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        with st.spinner("🧠 Pensando..."):
            result = qa({"question": prompt, "chat_history": st.session_state["history"]})
            assistant_response = result["answer"]

            # Manejo del estado final
            if assistant_response.lower() == "end":
                st.markdown("Gracias por usar el soporte técnico. ¡Adiós!")
                st.stop()  # Detener Streamlit

        # Mostrar la respuesta progresivamente
        for word in assistant_response.split(" "):
            full_response += word + " "
            response_placeholder.markdown(full_response)
            time.sleep(0.05)

        # Actualizar el historial de mensajes
        st.session_state["messages"].append({"role": "assistant", "content": full_response})

    # Actualizar el historial de interacción
    st.session_state["history"].append((prompt, full_response))
    st.experimental_rerun()