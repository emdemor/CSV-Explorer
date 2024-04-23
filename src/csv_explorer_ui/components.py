import os

import tempfile
import uuid
from collections import OrderedDict

import streamlit as st
import pandas as pd
from streamlit_chat_handler import StreamlitChatHandler
from csv_explorer import config


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
            content="Olá, tudo bem? Para começarmos, faça upload de seu CSV.",
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
        page_icon=config.LOGO_FILENAME,
        layout=layout,
        initial_sidebar_state=sidebar,
    )

    st.markdown(
        """
        <style>
            .st-emotion-cache-janbn0 {
                flex-direction: row-reverse;
                text-align: right;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


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
