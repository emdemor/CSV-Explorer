import traceback
import matplotlib
import openai
import pandas as pd
import streamlit as st
from loguru import logger
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from streamlit_chat_handler.types import StreamlitChatElement

from csv_explorer.csv_explorer import CSVExplorerResponse
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
    """
    The main entry point for the CSV Explorer UI.

    This function sets up the Streamlit page configuration, initiates the session state,
    renders the sidebar, and handles the main flow of the application.

    It checks if a CSV file is missing, if a new CSV file has been uploaded, and if the
    application is in the dialog flow. Based on these conditions, it renders the appropriate
    UI elements and handles user input and responses.
    """
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
    """
    Renders the user's prompt in the Streamlit chat interface.

    Args:
        prompt (str): The user's input prompt to be displayed.
    """
    st.session_state["chat_handler"].append(
        role="user", content=prompt, type="markdown", render=True
    )

def _generate_response(prompt: str) -> CSVExplorerResponse:
    """
    Generates a response for the given user prompt using the CSV Explorer's API.

    Args:
        prompt (str): The user's input prompt.

    Returns:
        CSVExplorerResponse: The response object containing elements to be rendered.
    """
    callbacks = [StreamlitCallbackHandler(st.container(), expand_new_thoughts=True)]
    return st.session_state["explorer"].invoke(prompt, callbacks=callbacks)

def _render_assistant_response(response: CSVExplorerResponse) -> None:
    """
    Renders the assistant's response in the Streamlit chat interface.

    Args:
        response (CSVExplorerResponse): The response object containing elements to be rendered.
    """
    st.session_state["chat_handler"].append_multiple(response.elements, render=True)
