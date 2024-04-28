from loguru import logger
import matplotlib
import openai
import traceback

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
            _render_user_prompt(prompt)
            try:
                response = _generate_response(prompt)
                _render_assistant_steps(response)
                _render_assistant_response(response)
                st.rerun()

            except KeyError:
                pass

            except openai.AuthenticationError:
                st.error("Chave da API inválida.", icon=config.ICON_ALERT)

            except openai.InternalServerError as err:
                if "reducing the temperature" in str(err):
                    st.error("A temperatura está muito alta. Tente reduzir.", icon=config.ICON_HIGH_TEMPERATURE)
                st.error("Houve um erro interno. Tente novamente.", icon=config.ICON_ALERT)
            except Exception as err:
                logger.error(traceback.print_exc())
                st.error("Houve um erro interno. Tente novamente.", icon=config.ICON_ERROR)


def _render_user_prompt(prompt):
    st.session_state["chat_handler"].append(
        role="user", content=prompt, type="markdown", render=True
    )


def _generate_response(prompt):
    callbacks = [StreamlitCallbackHandler(st.container(), expand_new_thoughts=True)]
    return st.session_state["explorer"].invoke(prompt, callbacks=callbacks)


def _render_assistant_steps(response):
    for action, output in zip(
        response.intermediate_actions, response.intermediate_outputs
    ):

        if "[ERROR]" in str(output):
            icon = config.ICON_ERROR
            element_type = "error"
        else:
            icon = config.ICON_SUCCESS
            element_type = "write"

        st.session_state["chat_handler"].append(
            role="assistant",
            content=output,
            type=element_type,
            render=True,
            parent="expander",
            parent_kwargs={
                "label": f"{icon}\t\t  **{action.tool}**: {str(action.tool_input)[:100]}",
                "expanded": False,
            },
        )


def _render_assistant_response(response):
    for element in response.elements:

        if isinstance(element, matplotlib.figure.Figure):
            st.session_state["chat_handler"].append(
                role="assistant",
                content=element,
                type="pyplot",
                render=True,
            )

        elif isinstance(element, pd.DataFrame):
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
