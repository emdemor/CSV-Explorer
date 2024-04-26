from abc import ABC, abstractmethod
from streamlit_chat_handler.types import StreamlitChatElement

class ToolResponse(ABC):
    pass
    
    def __str__(self):
        return self.response
    
    def __repr__(self):
        return f"{self.__class__.__name__}(response={self.response})"
    
    @abstractmethod
    def to_element(self) -> StreamlitChatElement:
        pass


class ToolDataFrameResponse(ToolResponse):
    def __init__(self, df):
        self.df = df
    
    def to_element(self) -> StreamlitChatElement:
        return StreamlitChatElement(
            role="assistant",
            type="dataframe",
            content=self.df,
        )


class ToolFigureResponse(ToolResponse):
    def __init__(self, df):
        self.df = df
    
    def to_element(self) -> StreamlitChatElement:
        return StreamlitChatElement(
            role="assistant",
            type="dataframe",
            content=self.df,
        )