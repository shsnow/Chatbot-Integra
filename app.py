import streamlit as st
from chatbot import qa
from db import validate_rut

# Configuración de la página
st.set_page_config(page_title="ChatBot Integra", page_icon="🤖")
st.title("Chat Integra")
st.caption("¡Hola! Bienvenido al chat de soporte técnico nivel 1.")

# Inicializar estado
if "rut" not in st.session_state:
    st.session_state["rut"] = None
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Solicitar el RUT si no está definido
if not st.session_state["rut"]:
    rut_input = st.text_input("Por favor, ingresa tu RUT:")
    if rut_input:
        if validate_rut(rut_input):
            st.session_state["rut"] = rut_input
            st.success("¡RUT válido! Puedes continuar.")
        else:
            st.error("RUT no válido. Intenta nuevamente.")
    st.stop()  # Detener el flujo hasta que se valide el RUT

# Mostrar mensajes anteriores
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrada del usuario
if prompt := st.chat_input("¿En qué te puedo ayudar?"):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = qa({"question": prompt, "chat_history": st.session_state["messages"]})
        st.markdown(response["answer"])

    st.experimental_rerun()
