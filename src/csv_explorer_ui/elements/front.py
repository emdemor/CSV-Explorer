import matplotlib
import openai

import pandas as pd
import streamlit as st
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler

from csv_explorer.tool_response import ToolResponse
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

            try:
                parsed_elements = st.session_state["explorer"].invoke(
                    prompt,
                    callbacks=[
                        StreamlitCallbackHandler(
                            st.container(), expand_new_thoughts=True
                        )
                    ],
                )

                for element in parsed_elements:

                    if isinstance(element, matplotlib.figure.Figure):
                        st.session_state["chat_handler"].append(
                            role="assistant",
                            content=element,
                            type="pyplot",
                            render=True,
                        )

                    elif isinstance(element, pd.DataFrame):
                        
                        from tabulate import tabulate
                        print(f"\n\n\n```\n{tabulate(element, tablefmt='github', headers='keys')}\n``` \n\n\n")

                        st.session_state["chat_handler"].append(
                            role="assistant",
                            content=element,
                            type="dataframe",
                            render=True,
                        )

                    else:
                        st.session_state["chat_handler"].append(
                            role="assistant",
                            content=element,
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
                    st.error("A temperatura está muito alta. Tente reduzir.", icon="🚨")
                st.error("Houve um erro interno. Tente novamente.", icon="🚨")
