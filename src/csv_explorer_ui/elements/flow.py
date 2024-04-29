import tempfile

import pydantic
import streamlit as st
import pandas as pd
from csv_explorer.csv_explorer import CSVExplorer
from csv_explorer_ui import config



def is_csv_missing():
    return st.session_state["chat_handler"].rendered_elements.get("file_upload") is None


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
    _add_instructions()
    
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

        if "no-apt-key" in st.session_state["elements"]:
            st.session_state["chat_handler"].append(
                role="user",
                content="Por favor, forneça sua chave da API.",
                type="error",
                icon="🚨",
                index="no-apt-key",
            )

def _add_instructions():

    with open(config.INSTRUCTIONS_PATH) as f:
        instructions = f.read()

    st.session_state["chat_handler"].append(
        role="assistant",
        content=instructions,
        type="markdown",
        render=True,
        parent="popover",
        parent_kwargs={
            "label": f"Leia as instruções",
            # "expanded": False,
        },
    )