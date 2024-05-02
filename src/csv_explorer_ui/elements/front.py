from dataclasses import dataclass
import json
import traceback
from typing import NamedTuple
import matplotlib
import openai
import pandas as pd
from pydantic import BaseModel
import streamlit as st
from loguru import logger
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from streamlit_chat_handler.types import StreamlitChatElement

from csv_explorer.csv_explorer import ChatResponse
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


@dataclass
class InteractionStep:
    prompt: str
    response: ChatResponse
    rating: int | None = None
    comment: str | None = None


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
        st.session_state.counter += 1
        prepare_csv()

    if is_in_dialog_flow():
        logger.info(f"Iniciando a interação {st.session_state.counter}")
        set_explorer()
        prompt = st.chat_input("Digite aqui...")
        if prompt and ("explorer" in st.session_state):
            st.session_state.counter += 1
            _render_user_prompt(prompt)
            try:
                response = _generate_response(prompt)
                _set_interaction_metadata(prompt, response)
                _persist_logs()
                _render_assistant_response(response)

            except KeyError as err:
                msg = str(traceback.print_exc())
                logger.error(msg)
                st.error(msg, icon=config.ICON_ALERT)

            except openai.AuthenticationError:
                msg = "Chave da API inválida."
                logger.error(msg)
                st.error(msg, icon=config.ICON_ALERT)

            except openai.InternalServerError as err:
                if "reducing the temperature" in str(err):
                    msg = "A temperatura está muito alta. Tente reduzir."
                    st.error(msg, icon=config.ICON_HIGH_TEMPERATURE)
                else:
                    msg = "Houve um erro interno. Tente novamente."
                    st.error(msg, icon=config.ICON_ALERT)
                logger.error(msg)

            except Exception as err:
                msg = f"Houve um erro interno. {traceback.print_exc()}"
                st.error(msg, icon=config.ICON_ALERT)


def _render_user_prompt(prompt):
    """
    Renders the user's prompt in the Streamlit chat interface.

    Args:
        prompt (str): The user's input prompt to be displayed.
    """
    logger.info(f"Usuário digitou a mensagem '{prompt}'")
    st.session_state["chat_handler"].append(
        role="user", content=prompt, type="markdown", render=True
    )


def _generate_response(prompt: str) -> ChatResponse:
    """
    Generates a response for the given user prompt using the CSV Explorer's API.

    Args:
        prompt (str): The user's input prompt.

    Returns:
        ChatResponse: The response object containing elements to be rendered.
    """
    callbacks = [StreamlitCallbackHandler(st.container(), expand_new_thoughts=True)]
    response = st.session_state["explorer"].invoke(prompt, callbacks=callbacks)
    logger.info(f"Recebendo a resposta {response}")
    return response


def _render_assistant_response(response: ChatResponse) -> None:
    """
    Renders the assistant's response in the Streamlit chat interface.

    Args:
        response (ChatResponse): The response object containing elements to be rendered.
    """
    logger.info(f"Renderizando a resposta {response}")
    st.session_state["chat_handler"].append_multiple(response.elements, render=True)


def _set_interaction_metadata(prompt: str, response: ChatResponse) -> None:
    """
    Set the interaction metadata in the session state.

    This function takes a prompt and a ChatResponse object, and stores them in the session state
    along with the rating for the current interaction step.

    Args:
        prompt (str): The prompt for the current interaction step.
        response (ChatResponse): The response object for the current interaction step.
    """
    logger.info(f"Formatando os metadadaos da interação")


    indexes = [index for index, counter in st.session_state.rating_indexes.items() if counter == st.session_state.counter]

    if len(indexes) > 0:
        index = indexes[-1]
        rating = st.session_state.ratings[index]
        comment = st.session_state.comments[index]
    else:
        rating = None
        comment = None

    metadata = InteractionStep(
        prompt=prompt,
        response=response,
        rating=rating,
        comment=comment
    )
    st.session_state.interactions[st.session_state.counter] = metadata

    logger.info(
        f"Interation metadata: {st.session_state.interactions[st.session_state.counter]}"
    )


def _persist_logs():
    logger.info(f"Persistindo os logs")

    extracted_messages = [x.__repr__() for x in st.session_state["explorer"].memory.chat_memory.messages]
    with open(config.MEMORY_LOGS_PATH, "w") as file:
        file.write(json.dumps(extracted_messages, indent=4, ensure_ascii=False))

    with open(config.RATING_LOGS_PATH, "w") as file:
        for index, int in st.session_state.interactions.items():
            file.write( f"{index}: {int}\n" ) 