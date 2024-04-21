import os, sys
import tempfile


import pandas as pd
import streamlit as st
from streamlit import runtime
from streamlit.web import cli as stcli

import ui
from ui.components import StreamlitChatElement, include_chat_element, initiate_session_state, page_config, render_element
from bot import config

import datetime
from time import sleep




def front():

    page_config(layout="centered", sidebar="auto")

    initiate_session_state()

    st.title(config.TITLE)

    rendered = render_element(st.session_state["messages"])

    if rendered["file_upload"] is None:
        st.chat_input("Forneça um arquivo CSV.", disabled=True)
        st.session_state["csv_filepath"] = None
    else:
        
        if st.session_state["csv_filepath"] is None:
            include_chat_element(
                role="user",
                content="Arquivo carregado.",
                type="markdown",
            )
            with st.spinner("Processando..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
                    tmp_file.write(rendered["file_upload"].getvalue())
                    st.session_state["csv_filepath"] = tmp_file.name

                include_chat_element(
                    role="assistant",
                    content="Aqui estão as primeiras linhas do dataframe:",
                    type="markdown",
                )

                include_chat_element(
                    role="assistant",
                    content=pd.read_csv(st.session_state["csv_filepath"]).head(10),
                    type="dataframe",
                )

                include_chat_element(
                    role="assistant",
                    content="O que você gostaria de saber sobre esse dataframe?",
                    type="markdown",
                )

                st.rerun()
        
        else:
            prompt = st.chat_input("Digite aqui...")

            if prompt:
                include_chat_element(role="user", content=prompt, type="markdown")

                with st.spinner("Processando..."):
                    sleep(1)
                    response = "response"
                    include_chat_element(role="assistant", content=response, type="markdown")

                st.rerun()


def run():
    path = os.path.join(
        os.sep.join(os.path.abspath(ui.__file__).split(os.sep)[:-1]),
        "__init__.py",
    )

    if runtime.exists():
        front()

    else:
        sys.argv = ["streamlit", "run", path]
        sys.exit(stcli.main())


if __name__ == "__main__":
    run()
