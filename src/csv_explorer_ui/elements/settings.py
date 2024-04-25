from collections import OrderedDict
import uuid
import streamlit as st
from streamlit_chat_handler import StreamlitChatHandler

from csv_explorer_ui import config


def initiate_session_state() -> None:
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = uuid.uuid4().hex

    if "csv_filepath" not in st.session_state:
        st.session_state["csv_filepath"] = None

    if "messages" not in st.session_state:
        st.session_state["messages"] = OrderedDict({})

    if "chat_handler" not in st.session_state:
        st.session_state["chat_handler"] = StreamlitChatHandler(
            st.session_state,
            session_id=st.session_state["session_id"],
        )

        st.session_state["chat_handler"].append(
            index="init",
            role="assistant",
            type="markdown",
            content="Olá, tudo bem? Para começar, faça upload de seu CSV.",
        )

        st.session_state["chat_handler"].append(
            index="file_upload",
            role="assistant",
            type="file_uploader",
            content="Upload CSV",
            kwargs={"type": "csv"},
        )


def page_config(layout: str = "centered", sidebar: str = "auto") -> None:
    """
    Set the page configuration for each page of the app.
    Must be the first command in each page, and it must be called
    only once.

    Parameters
    ----------
    layout : str
        Type of the layout of the page, by default 'centered'.
    sidebar : str
        Initial state of the sidebar, by default 'auto'.
    """

    st.set_page_config(
        page_title=config.TITLE,
        page_icon=config.LOGO_FILEPATH,
        layout=layout,
        initial_sidebar_state=sidebar,
    )

    with open(config.STYLE_FILEPATH) as css:
        st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)
