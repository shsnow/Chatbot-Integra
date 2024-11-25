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
        try:
            if validate_rut(rut_input):  # Si el RUT es válido
                st.session_state["rut"] = rut_input  # Guardamos el RUT
                st.success("¡RUT válido! Puedes continuar al chat.")
                st.rerun()  # Reiniciar la aplicación para mostrar el chat
            else:
                st.error("RUT no válido. Intenta nuevamente.")
        except Exception as e:
            st.error(f"Error al validar el RUT: {e}")
else:
    # Si el RUT está validado, mostrar el chat
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Entrada del usuario para hacer preguntas al chatbot
    if prompt := st.chat_input("¿En qué te puedo ayudar?"):
        # Agregar el mensaje del usuario al historial
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Spinner mientras esperamos la respuesta del chatbot
        with st.chat_message("assistant"):
            with st.spinner("Procesando..."):
                try:
                    # Obtener solo los últimos 5 mensajes para enviar al modelo
                    chat_history = st.session_state["messages"][-5:]

                    # Obtener respuesta del chatbot
                    response = qa({
                        "question": prompt,
                        "chat_history": chat_history,
                        "rut": st.session_state["rut"]  # Pasar el RUT al chatbot
                    })

                    # Mostrar respuesta del chatbot
                    reply = response.get("answer", "Lo siento, no pude procesar tu solicitud.")
                    st.markdown(reply)
                    st.session_state["messages"].append({"role": "assistant", "content": reply})

                except Exception as e:
                    error_msg = f"Error al procesar la solicitud: {e}"
                    st.error(error_msg)
                    st.session_state["messages"].append({"role": "assistant", "content": error_msg})
