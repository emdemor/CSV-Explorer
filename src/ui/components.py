import os
from time import sleep
import tempfile
import uuid
from typing import Any, Literal
from dataclasses import dataclass, field
from collections import OrderedDict

import streamlit as st
import pandas as pd
from bot import config


@dataclass
class StreamlitChatElement:
    role: Literal["user", "assistant"]
    type: str
    content: Any
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)


def initiate_session_state() -> None:
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = uuid.uuid4().hex

    if "csv_filepath" not in st.session_state:
        st.session_state["csv_filepath"] = None

    if "messages" not in st.session_state:
        st.session_state["messages"] = OrderedDict({})

        append_chat_element(
            index="init",
            chat_element=StreamlitChatElement(
                role="assistant",
                content="Olá, tudo bem? Para começarmos, faça upload de seu CSV.",
                type="markdown",
            ),
        )

        append_chat_element(
            index="file_upload",
            chat_element=StreamlitChatElement(
                role="assistant",
                content="Upload CSV",
                type="file_uploader",
                kwargs={"type": "csv"},
            ),
        )


def append_chat_element(chat_element: StreamlitChatElement, index: str | None = None):
    if index is None:
        index = uuid.uuid4().hex
    st.session_state["messages"][index] = chat_element


def include_chat_element(
    role: Literal["user", "assistant"],
    type: str,
    content: Any,
    args: list[Any] = [],
    kwargs: dict[str, Any] = {},
    index: str | None = None,
):

    chat_element = StreamlitChatElement(
        role=role,
        content=content,
        type=type,
        args=args,
        kwargs=kwargs,
    )

    render_element(chat_element)

    if index is None:
        index = uuid.uuid4().hex

    st.session_state["messages"][index] = chat_element


def render_element(
    chat_element: StreamlitChatElement | OrderedDict[str, StreamlitChatElement]
) -> OrderedDict[str, Any]:

    if isinstance(chat_element, StreamlitChatElement):
        chat_element = OrderedDict({uuid.uuid4().hex: chat_element})

    chat_element_list = [v for v in chat_element.values()]
    element_groups = group_elements_by_role(chat_element_list)

    response = OrderedDict({})
    count = 0
    for element_list in element_groups:
        role = element_list[0].role
        with st.chat_message(role):
            for element in element_list:
                response[list(chat_element)[count]] = getattr(st, element.type)(
                    element.content, *element.args, **element.kwargs
                )
                count += 1
    return response


def group_elements_by_role(
    elements: list[StreamlitChatElement],
) -> list[list[StreamlitChatElement]]:
    grouped_elements = []
    if not elements:
        return grouped_elements

    current_group = []
    current_role = elements[0].role

    for element in elements:
        if element.role == current_role:
            current_group.append(element)
        else:
            grouped_elements.append(current_group)
            current_group = [element]
            current_role = element.role

    if current_group:
        grouped_elements.append(current_group)

    return grouped_elements


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
        page_icon=config.LOGO_FILENAME,
        layout=layout,
        initial_sidebar_state=sidebar,
    )

    st.markdown(
        """
        <style>
            .st-emotion-cache-janbn0 {
                flex-direction: row-reverse;
                text-align: right;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
