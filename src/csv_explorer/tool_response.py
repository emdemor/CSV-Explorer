from abc import ABC, abstractmethod
from streamlit_chat_handler.types import StreamlitChatElement
from tabulate import tabulate

class ToolResponse(ABC):
    
    @abstractmethod
    def to_element(self) -> StreamlitChatElement:
        pass


class ToolDataFrameResponse(ToolResponse):
        
    def __init__(self, df):
        self.df = df
    
    def __str__(self):
        return f"{tabulate(self.df, headers='keys')}"

    def __repr__(self):
        return f"{self.__class__.__name__}(response=DataFrame(n_rows={self.df.shape[0]}, n_columns={self.df.shape[1]}))"
    
    def to_element(self) -> StreamlitChatElement:
        return StreamlitChatElement(
            role="assistant",
            type="dataframe",
            content=self.df,
        )


class ToolFigureResponse(ToolResponse):
    def __init__(self, df):
        self.df = df
    
    
    def __repr__(self):
        return tabulate(self.df, headers="keys")
    
    def to_element(self) -> StreamlitChatElement:
        return StreamlitChatElement(
            role="assistant",
            type="dataframe",
            content=self.df,
        )