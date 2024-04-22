import os, sys


import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from streamlit import runtime
from streamlit.web import cli as stcli

import csv_explorer_ui
from csv_explorer_ui.components import (
    StreamlitChatElement,
    append_chat_element,
    include_chat_element,
    initiate_session_state,
    is_csv_missing,
    is_in_dialog_flow,
    page_config,
    prepare_csv,
    render_element,
    was_csv_just_uploaded,
)
from csv_explorer import config
from csv_explorer.csv_explorer import CSVExplorer


def front():

    page_config(layout="centered", sidebar="auto")

    initiate_session_state()

    st.title(config.TITLE)

    rendered = render_element(st.session_state["messages"])

    if is_csv_missing(rendered):
        st.chat_input("Forneça um arquivo CSV.", disabled=True)
        st.session_state["csv_filepath"] = None

    if was_csv_just_uploaded(rendered):
        prepare_csv(rendered)
        

    if is_in_dialog_flow(rendered):
        explorer = CSVExplorer(filepath=st.session_state["csv_filepath"])

        prompt = st.chat_input("Digite aqui...")

        if prompt:
            include_chat_element(role="user", content=prompt, type="markdown")

            with st.spinner("Processando..."):
                response = explorer.invoke(prompt)

                if isinstance(response, matplotlib.figure.Figure):
                    include_chat_element(role="assistant", content=response, type="pyplot")
                else:
                    include_chat_element(role="assistant", content=response, type="markdown")


            st.rerun()



def run():
    path = os.path.join(
        os.sep.join(os.path.abspath(csv_explorer_ui.__file__).split(os.sep)[:-1]),
        "__init__.py",
    )

    if runtime.exists():
        front()

    else:
        sys.argv = ["streamlit", "run", path]
        sys.exit(stcli.main())


if __name__ == "__main__":
    run()
