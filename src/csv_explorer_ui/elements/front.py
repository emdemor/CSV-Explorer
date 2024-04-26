import matplotlib
import openai

import streamlit as st
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler

from csv_explorer_ui import config
from csv_explorer_ui.elements.settings import initiate_session_state, page_config
from csv_explorer_ui.elements.sidebar import sidebar
from csv_explorer_ui.elements.flow import (
    is_csv_missing,
    is_in_dialog_flow,
    prepare_csv,
    set_explorer,
    was_csv_just_uploaded,
)


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

        if prompt and ("explorer" in st.session_state):

            st.session_state["chat_handler"].append(
                role="user", content=prompt, type="markdown", render=True
            )

            with st.spinner("Processando..."):

                try:
                    st_callback = response, additional = st.session_state[
                        "explorer"
                    ].invoke(
                        prompt,
                        [
                            StreamlitCallbackHandler(
                                st.container(), expand_new_thoughts=True
                            )
                        ],
                    )

                    if isinstance(additional, matplotlib.figure.Figure):
                        st.session_state["chat_handler"].append(
                            role="assistant",
                            content=response,
                            type="markdown",
                            render=True,
                        )
                        st.session_state["chat_handler"].append(
                            role="assistant",
                            content=additional,
                            type="pyplot",
                            render=True,
                        )

                    else:
                        st.session_state["chat_handler"].append(
                            role="assistant",
                            content=response,
                            type="markdown",
                            render=True,
                        )

                    st.rerun()

                except KeyError:
                    pass

                except openai.AuthenticationError:
                    st.error("Chave da API inválida.", icon="🚨")

                except openai.InternalServerError as err:
                    if "reducing the temperature" in str(err):
                        st.error(
                            "A temperatura está muito alta. Tente reduzir.", icon="🚨"
                        )
                    st.error("Houve um erro interno. Tente novamente.", icon="🚨")
