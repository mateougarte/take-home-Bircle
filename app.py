import streamlit as st
import requests

FASTAPI_URL = "http://localhost:8000/chat"
USER_ID = "streamlit-user"

st.title("Bircle Outdoors - Asistente")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Escribí tu consulta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(""):
            try:
                response = requests.post(
                    FASTAPI_URL,
                    json={"user_id": USER_ID, "message": prompt},
                    timeout=30,
                )
                response.raise_for_status()
                answer = response.json()["response"]
            except requests.exceptions.ConnectionError:
                answer = "No se pudo conectar al servidor. ¿Está corriendo FastAPI?"
            except requests.exceptions.HTTPError as e:
                answer = f"Error del servidor: {e.response.status_code}"
            except Exception as e:
                answer = f"Error inesperado: {e}"

        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
