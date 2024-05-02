from abc import ABC, abstractmethod
import matplotlib
from matplotlib import pyplot as plt
from streamlit_chat_handler.types import StreamlitChatElement
from tabulate import tabulate


class ChatResponse(ABC):
    """
    Abstract base class for chat responses.

    Subclasses must implement the `to_element` method to convert the response to a `StreamlitChatElement`.
    """

    @abstractmethod
    def to_element(self) -> StreamlitChatElement:
        """
        Convert the chat response to a `StreamlitChatElement`.

        Returns:
            StreamlitChatElement: The chat response as a `StreamlitChatElement`.
        """
        pass


class ChatMarkdownResponse(ChatResponse):
    """
    A chat response that is formatted as Markdown.

    Args:
        response (str): The Markdown-formatted response.
    """
    def __init__(self, response: str):
        self.response = response

    def __str__(self):
        return self.response

    def __repr__(self):
        return self.response

    def to_element(self) -> StreamlitChatElement:
        """
        Convert the Markdown response to a `StreamlitChatElement`.

        Returns:
            StreamlitChatElement: The Markdown response as a `StreamlitChatElement`.
        """
        return StreamlitChatElement(
            role="assistant",
            type="markdown",
            content=self.__repr__(),
        )



class ChatDataFrameResponse(ChatResponse):
    """
    A chat response that displays a Pandas DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame to be displayed.
    """

    def __init__(self, df):
        self.df = df

    def __str__(self):
        return f"```\n{tabulate(self.df, headers='keys')}\n```"

    def __repr__(self):
        return f"{self.__class__.__name__}(response=DataFrame(n_rows={self.df.shape[0]}, n_columns={self.df.shape[1]}))"

    def to_element(self) -> StreamlitChatElement:
        """
        Convert the DataFrame response to a `StreamlitChatElement`.

        Returns:
            StreamlitChatElement: The DataFrame response as a `StreamlitChatElement`.
        """
        return StreamlitChatElement(
            role="assistant",
            type="dataframe",
            content=self.df,
        )


class ChatFigureResponse(ChatResponse):
    """
    A chat response that displays a Matplotlib figure.

    Args:
        code (str): The code used to generate the Matplotlib figure.
    """
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return f"\n```\n{self.code}\n```\n"

    def __repr__(self):
        return f"\n```\n{self.code}\n```\n"

    @property
    def figure(self) -> matplotlib.figure.Figure:
        """
        Get the Matplotlib figure.

        Returns:
            matplotlib.figure.Figure: The Matplotlib figure.
        """
        fig = plt.gcf()
        fig.set_facecolor("none")
        return fig

    def to_element(self) -> StreamlitChatElement:
        """
        Convert the Matplotlib figure response to a `StreamlitChatElement`.

        Returns:
            StreamlitChatElement: The Matplotlib figure response as a `StreamlitChatElement`.
        """
        return StreamlitChatElement(
            role="assistant",
            type="pyplot",
            content=self.figure,
        )


class ChatPythonREPLResponse(ChatResponse):
    """
    A chat response that displays the output of a Python REPL session.

    Args:
        code (str): The Python code executed in the REPL.
        response (str): The output of the Python REPL.
    """
    def __init__(self, code: str, response: str):
        self.code = code
        self.response = response

    def __str__(self):
        return f"Code:\n```\n{self.code}\n```\n\nOutput:\n```\n{self.response}\n```"

    def __repr__(self):
        return f"Code:\n```\n{self.code}\n```\n\nOutput:\n```\n{self.response}\n```"

    def to_element(self) -> StreamlitChatElement:
        """
        Convert the Python REPL response to a `StreamlitChatElement`.

        Returns:
            StreamlitChatElement: The Python REPL response as a `StreamlitChatElement`.
        """
        return StreamlitChatElement(
            role="assistant",
            type="markdown",
            content=self.__repr__(),
        )
