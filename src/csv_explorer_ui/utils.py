import json

import pandas as pd
import streamlit as st
from loguru import logger

from csv_explorer_ui import config
import os


def persist_logs() -> None:
    """
    Persists the logs for the CSV Explorer application.

    This function performs the following tasks:
    1. Extracts the messages from the chat memory of the Explorer object and writes them to a JSON file at the location specified by `config.MEMORY_LOGS_PATH`.
    2. Iterates through the interactions stored in `st.session_state.interactions`, and for each interaction, writes detailed information about the interaction (including the prompt, response, output, elements, intermediate outputs and actions, rating, and comment) to a file at the location specified by `config.RATING_LOGS_PATH`.

    The function uses the `logger` object to log an informational message about the log persistence process.
    """

    logger.info(f"Persistindo os logs")

    extracted_messages = [
        x.__repr__() for x in st.session_state["explorer"].memory.chat_memory.messages
    ]

    if not os.path.exists(config.LOGS_PATH):
        os.makedirs(config.LOGS_PATH) 
    memory_logs_path = os.path.join(config.LOGS_PATH, f"memory_{st.session_state['session_id']}.txt")
    metadata_logs_path = os.path.join(config.LOGS_PATH, f"metadata_{st.session_state['session_id']}.yaml")

    with open(memory_logs_path, "w") as file:
        file.write(json.dumps(extracted_messages, indent=4, ensure_ascii=False))

    with open(metadata_logs_path, "w") as file:
        for index, int in st.session_state.interactions.items():
            tab = 2 * " "
            msg = (
                f"{index}:\n"
                + f"{tab}{int.__class__.__name__}:\n"
                + f'{2*tab}prompt:\n{3*tab}"{int.prompt}"\n'
                + f"{2*tab}response:\n{3*tab}{int.response.__class__.__name__}:\n"
                + f"{4*tab}output: " + '"' + f"\n{5*tab}"
                + str(int.response.output).replace("\n", f"\n{5*tab}").replace('"', "'") + '"'
                + "\n"
                + f"{4*tab}elements:"
            )
            for element in int.response.elements:
                msg += f"\n{5*tab}- {element.__class__.__name__}:"
                for k, v in element.__dict__.items():
                    if isinstance(v, pd.DataFrame):
                        value = "\n\n" + str(v.to_markdown()).replace(
                            "-:|", "--|"
                        ).replace("|:-", "|--") + "\n"
                        value = value.replace("\n", f"\n{6*tab + '  ' + tab}")
                    else:
                        value = str(v).replace("\n", f"\n{6*tab + '  ' + tab}").replace('"', "'")
                    msg += f"\n{6*tab}  {k}: \"{str(value).strip().replace('None', 'null')}\""
            msg += "\n"
            msg += f"{4*tab}intermediate_outputs:\n"
            for output in int.response.intermediate_outputs:
                msg += f"{5*tab}- \"" + str(output).replace('\n', '\n  ' + 6*tab).replace("None", "null").replace('"', "'") + "\"\n"

            msg += f"{4*tab}intermediate_actions:\n"
            for action in int.response.intermediate_outputs:
                msg += f"{5*tab}- \"" + str(action).replace('\n', '\n  ' + 6*tab).replace("None", "null").replace('"', "'") + "\"\n"

            msg += f"{2*tab}rating: {int.rating}\n"
            msg += f'{2*tab}comment: "{int.comment}"\n'
            msg += "\n"
            file.write(msg)
