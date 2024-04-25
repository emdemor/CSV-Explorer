import os, sys


import matplotlib
import openai
import pydantic
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from streamlit import runtime
from streamlit.web import cli as stcli
from streamlit_chat_handler import StreamlitChatHandler

import csv_explorer_ui
from csv_explorer_ui.components import (
    initiate_session_state,
    is_csv_missing,
    is_in_dialog_flow,
    page_config,
    prepare_csv,
    set_explorer,
    sidebar,
    was_csv_just_uploaded,
)
from csv_explorer import config


def front():

    page_config(layout="centered", sidebar="auto")

    initiate_session_state()

    sidebar()

    st.title(config.TITLE)

    st.session_state["chat_handler"].render()

    if is_csv_missing():
        st.chat_input("Forneça um arquivo CSV.", disabled=True)
        st.session_state["csv_filepath"] = None

    if was_csv_just_uploaded():
        prepare_csv()

    if is_in_dialog_flow():

        set_explorer()
        
        prompt = st.chat_input("Digite aqui...")

        if (prompt and ("explorer" in st.session_state)):
            
            st.session_state["chat_handler"].append(
                role="user", content=prompt, type="markdown", render=True
            )

            with st.spinner("Processando..."):

                try:

                    response, additional = st.session_state["explorer"].invoke(prompt)

                    if isinstance(additional, matplotlib.figure.Figure):
                        st.session_state["chat_handler"].append(
                            role="assistant", content=response, type="markdown", render=True
                        )
                        st.session_state["chat_handler"].append(
                            role="assistant", content=additional, type="pyplot", render=True
                        )

                    else:
                        st.session_state["chat_handler"].append(
                            role="assistant", content=response, type="markdown", render=True
                        )
                    
                    st.rerun()

                except KeyError:
                    pass

                except openai.AuthenticationError:
                    st.error("Chave da API inválida.", icon="🚨")
                
                except openai.InternalServerError as err:
                    if "reducing the temperature" in str(err):
                        st.error("A temperatura está muito alta. Tente reduzir.", icon="🚨")
                    st.error("Houve um erro interno. Tente novamente.", icon="🚨")


            


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
