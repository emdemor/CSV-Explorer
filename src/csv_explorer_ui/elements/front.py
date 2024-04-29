import traceback


import matplotlib
import openai
import pandas as pd
import streamlit as st
from loguru import logger
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from streamlit_chat_handler.types import StreamlitChatElement

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
                _render_assistant_response(response)

            except KeyError:
                pass

            except openai.AuthenticationError:
                st.error("Chave da API inválida.", icon=config.ICON_ALERT)

            except openai.InternalServerError as err:
                if "reducing the temperature" in str(err):
                    st.error(
                        "A temperatura está muito alta. Tente reduzir.",
                        icon=config.ICON_HIGH_TEMPERATURE,
                    )
                st.error(
                    "Houve um erro interno. Tente novamente.", icon=config.ICON_ALERT
                )
            except Exception as err:
                logger.error(traceback.print_exc())
                st.error(
                    "Houve um erro interno. Tente novamente.", icon=config.ICON_ERROR
                )


def _render_user_prompt(prompt):
    st.session_state["chat_handler"].append(
        role="user", content=prompt, type="markdown", render=True
    )


def _generate_response(prompt):
    callbacks = [StreamlitCallbackHandler(st.container(), expand_new_thoughts=True)]
    return st.session_state["explorer"].invoke(prompt, callbacks=callbacks)





def _parse_assistant_response(response) -> list[StreamlitChatElement]:
    result = []
    for element in response.elements:
        if isinstance(element, matplotlib.figure.Figure):
            result.append(
                StreamlitChatElement(
                    role="assistant",
                    type="pyplot",
                    content=element,
                    parent=None,
                    parent_args=[],
                    parent_kwargs={},
                    args=[],
                    kwargs={},
                )
            )

        elif isinstance(element, pd.DataFrame):
            result.append(
                StreamlitChatElement(
                    role="assistant",
                    type="dataframe",
                    content=element,
                    parent=None,
                    parent_args=[],
                    parent_kwargs={},
                    args=[],
                    kwargs={},
                )
            )
        else:
            result.append(
                StreamlitChatElement(
                    role="assistant",
                    type="markdown",
                    content=element,
                    parent=None,
                    parent_args=[],
                    parent_kwargs={},
                    args=[],
                    kwargs={},
                )
            )

    return result


def _render_assistant_response(response):
    parsed_response = _parse_assistant_response(response)
    st.session_state["chat_handler"].append_multiple(parsed_response, response)
