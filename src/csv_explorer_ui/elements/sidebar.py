import os

import streamlit as st

from csv_explorer_ui import config


def update_model():
    if ("model" in st.session_state) and ("explorer" in st.session_state):
        st.session_state["explorer"].set(model=str(st.session_state["model"]))
        st.session_state["chat_handler"].append(
            role="user",
            content=f"Modelo foi alterado para {st.session_state['model']}",
            type="success",
        )


def update_temperature():
    if ("model" in st.session_state) and ("explorer" in st.session_state):
        st.session_state["explorer"].set(
            temperature=str(st.session_state["temperature"])
        )
        st.session_state["chat_handler"].append(
            role="user",
            content=f"Temperature foi alterada para {st.session_state['temperature']}",
            type="success",
        )


def update_memory_k():
    if ("model" in st.session_state) and ("explorer" in st.session_state):
        st.session_state["explorer"].set(memory_k=str(st.session_state["memory_k"]))
        st.session_state["chat_handler"].append(
            role="user",
            content=f"Janela de memória foi alterada para {st.session_state['memory_k']} passos",
            type="success",
        )


def add_api_key():
    if "api_key" in st.session_state:
        os.environ["OPENAI_API_KEY"] = st.session_state["api_key"]
        masked_key = _mask_key(os.environ["OPENAI_API_KEY"])
        st.session_state["api_key"] = masked_key

        if st.session_state["csv_filepath"]:
            st.session_state["chat_handler"].append(
                role="user",
                content=f"Chave '{masked_key}' adicionada.",
                type="success",
            )


def sidebar():
    left_co, cent_co, last_co = st.columns(3)
    with cent_co:
        st.sidebar.image(config.LOGO_FILEPATH, width=150)

    st.sidebar.header("Configurações")

    st.sidebar.selectbox(
        "Modelo",
        ["gpt-3.5-turbo", "gpt-4"],
        placeholder="Selecione o modelo",
        key="model",
        on_change=update_model,
    )

    api_key_value = (
        _mask_key(os.environ.get("OPENAI_API_KEY"))
        if os.environ.get("OPENAI_API_KEY")
        else None
    )

    st.sidebar.text_input(
        "Chave de API",
        type="password",
        placeholder="Insira sua chave de API",
        value=api_key_value,
        on_change=add_api_key,
        key="api_key",
    )

    st.sidebar.slider(
        "Temperatura",
        min_value=0.0,
        max_value=2.0,
        step=0.1,
        key="temperature",
        on_change=update_temperature,
    )
    st.sidebar.slider(
        "Janela de memória",
        min_value=0,
        max_value=20,
        value=5,
        step=1,
        key="memory_k",
        on_change=update_memory_k,
    )


def _mask_key(key):
    if not key:
        return ""
    if len(key) == 0:
        return ""
    return key[:3] + "..." + key[-4:]
