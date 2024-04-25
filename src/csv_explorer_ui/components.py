from importlib import resources
import os

import tempfile
import uuid
from collections import OrderedDict

import openai
import pydantic
import streamlit as st
import pandas as pd
from streamlit_chat_handler import StreamlitChatHandler
from csv_explorer import config
from csv_explorer.config import STYLE_FILEPATH
from csv_explorer.csv_explorer import CSVExplorer


def initiate_session_state() -> None:
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = uuid.uuid4().hex

    if "csv_filepath" not in st.session_state:
        st.session_state["csv_filepath"] = None

    if "messages" not in st.session_state:
        st.session_state["messages"] = OrderedDict({})

    if "chat_handler" not in st.session_state:
        st.session_state["chat_handler"] = StreamlitChatHandler(
            st.session_state,
            session_id=st.session_state["session_id"],
        )

        st.session_state["chat_handler"].append(
            index="init",
            role="assistant",
            type="markdown",
            content="Olá, tudo bem? Para começar, faça upload de seu CSV.",
        )

        st.session_state["chat_handler"].append(
            index="file_upload",
            role="assistant",
            type="file_uploader",
            content="Upload CSV",
            kwargs={"type": "csv"},
        )


def page_config(layout: str = "centered", sidebar: str = "auto") -> None:
    """
    Set the page configuration for each page of the app.
    Must be the first command in each page, and it must be called
    only once.

    Parameters
    ----------
    layout : str
        Type of the layout of the page, by default 'centered'.
    sidebar : str
        Initial state of the sidebar, by default 'auto'.
    """

    st.set_page_config(
        page_title=config.TITLE,
        page_icon=config.LOGO_FILEPATH,
        layout=layout,
        initial_sidebar_state=sidebar,
    )

    with open(STYLE_FILEPATH) as css:
        st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)


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
        masked_key = _mask_key(os.environ['OPENAI_API_KEY'])
        st.session_state["api_key"] = masked_key

        if st.session_state["csv_filepath"]:    
            st.session_state["chat_handler"].append(
                role="user",
                content=f"Chave '{masked_key}' adicionada.",
                type="success",
            )


def sidebar():
    left_co, cent_co,last_co = st.columns(3)
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

    st.sidebar.slider('Temperatura', min_value=0.0, max_value=2.0, step=0.1, key='temperature', on_change=update_temperature)
    st.sidebar.slider('Janela de memória', min_value=0, max_value=20, value=5, step=1, key='memory_k', on_change=update_memory_k)


def is_csv_missing():
    return st.session_state["chat_handler"].rendered_elements["file_upload"] is None


def was_csv_just_uploaded():
    csv_uploaded = not is_csv_missing()
    csv_path_empty = st.session_state["csv_filepath"] is None
    return csv_uploaded and csv_path_empty


def is_in_dialog_flow():
    csv_uploaded = not is_csv_missing()
    csv_prepared = st.session_state["csv_filepath"] is not None
    return csv_uploaded and csv_prepared


def prepare_csv():
    rendered = st.session_state["chat_handler"].rendered_elements
    st.session_state["chat_handler"].append(
        role="user",
        content="Arquivo carregado.",
        type="markdown",
        render=True,
    )
    with st.spinner("Processando..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
            tmp_file.write(rendered["file_upload"].getvalue())
            st.session_state["csv_filepath"] = tmp_file.name

        st.session_state["chat_handler"].append(
            role="assistant",
            content="Aqui estão as primeiras linhas do dataframe:",
            type="markdown",
            render=True,
        )

        st.session_state["chat_handler"].append(
            role="assistant",
            content=pd.read_csv(st.session_state["csv_filepath"]).head(10),
            type="dataframe",
            render=True,
        )

        st.session_state["chat_handler"].append(
            role="assistant",
            content="O que você gostaria de saber sobre esse dataframe?",
            type="markdown",
            render=True,
        )

        st.rerun()


def set_explorer():

    try:
        if "explorer" not in st.session_state:
            st.session_state["explorer"] = CSVExplorer(
                filepath=st.session_state["csv_filepath"],
                model=st.session_state.get("model", "gpt-3.5-turbo"),
                temperature=st.session_state.get("temperature", 0.0),
                memory_k=st.session_state.get("memory_k", 10),
            )

    except pydantic.v1.error_wrappers.ValidationError:
        st.session_state["chat_handler"].append(
            role="user",
            content="Por favor, forneça sua chave da API.",
            type="error",
            icon="🚨",
        )

def _mask_key(key):
    return key[:3] + "..." + key[-4:]
