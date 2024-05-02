import os
import ast
from importlib import import_module
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
from loguru import logger
from langchain.memory.buffer_window import ConversationBufferWindowMemory
from langchain_openai import ChatOpenAI
from langchain_core.tools import StructuredTool
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from pydantic import BaseModel
import csv_explorer
from csv_explorer.parsers.markdown_table import parse_markdown_text
import traceback

from csv_explorer.types import ChatDataFrameResponse, ChatMarkdownResponse, ChatResponse

TOOLS_FILEPATH = os.path.join(
    "/".join(os.path.abspath(csv_explorer.__file__).split("/")[:-1]), "tools.py"
)

TEMP_FILEPATH = "/tmp"

AGENTS = [
    "chat-conversational-react-description",
    "chat-zero-shot-react-description",
    "conversational-react-description",
    "openai-functions",
    "openai-tools",
    "openai-multi-functions",
    "react-docstore",
    "self-ask-with-search",
    "structured-chat-zero-shot-react-description",
    "zero-shot-react-description",
]


LLM_MODELS = {
    "gpt-3.5-turbo": ChatOpenAI,
    "gpt-4": ChatOpenAI,
}


class ChatResponse(BaseModel):
    output: str
    elements: List[Any]
    intermediate_outputs: List[Any]
    intermediate_actions: List[Any]


class CSVExplorer:
    """
    A class for exploring CSV files using AI-powered tools.

    Args:
        filepath (str): The path to the CSV file.
        extra_tools (list[StructuredTool], optional): Additional tools to use for exploration. Defaults to an empty list.
        agent_type (str, optional): The type of AI agent to use. Defaults to "openai-tools".
        model (str, optional): The AI model to use. Defaults to "gpt-3.5-turbo".
        temperature (float, optional): The temperature parameter for generating AI responses. Defaults to 0.
        memory_k (int, optional): The number of previous conversation turns to consider for context. Defaults to 3.
    """

    tools_filepath: str = TOOLS_FILEPATH
    temp_filepath: str = TEMP_FILEPATH
    _instance = None

    def __init__(
        self,
        filepath: str,
        extra_tools: list[StructuredTool] = [],
        agent_type: str = "openai-functions",
        model: str = "gpt-3.5-turbo",
        temperature: float = 0,
        memory_k: int = 3,
    ):
        self._set_temp_folder()
        self.filepath = filepath
        self.tools = self._set_tools(extra_tools)
        self.agent_type = self._set_agent_type(agent_type)
        self.model = self._set_model(model)
        self.temperature = temperature
        self.memory_k = memory_k
        self.reset()

    def reset(self) -> "CSVExplorer":
        """
        Reset the CSVExplorer instance to its initial state.

        Returns:
            CSVExplorer: The updated CSVExplorer instance.
        """
        self.llm = self._set_llm()
        self.memory = self._set_memory()
        self.agent = create_csv_agent(
            self.llm,
            self.filepath,
            verbose=True,
            agent_type=self.agent_type,
            extra_tools=self.tools,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
        )
        return self

    def invoke(self, query: str, callbacks=None) -> ChatResponse:
        """
        Invokes the AI agent with a query and returns the response.

        Args:
            query (str): The query to send to the AI agent.

        Returns:
            str: The response from the AI agent.
        """

        prompt = self._set_prompt(query)
        answer = self.agent.invoke({"input": prompt}, {"callbacks": callbacks})
        response = self._parse_answer(query, answer)
        return self._format_chat_response(answer, response)

    def _format_chat_response(
        self, answer: Dict[str, Any], response
    ) -> list[ChatResponse]:
        """
        Formats and constructs a list of ChatResponse objects based on the provided answer dictionary
        and response elements.

        This method takes the output and intermediate steps from the answer dictionary, and transforms
        response elements into their corresponding object format. The `ChatResponse` objects encapsulate
        the final output, interactive elements, and the sequences of intermediate outputs and actions.

        Args:
        answer (Dict[str, Any]): A dictionary containing the final output text and intermediate steps
                                where each step includes an action and its output.
        response (iterable): An iterable of objects that need to be transformed into interactive elements
                            as part of the chat response.

        Returns:
        list[ChatResponse]: A list containing a single ChatResponse object, which includes the main output,
                            interactive elements, and lists of intermediate outputs and actions.
        """
        return ChatResponse(
            output=answer["output"],
            elements=[x.to_element() for x in response],
            intermediate_outputs=[x[1] for x in answer["intermediate_steps"]],
            intermediate_actions=[x[0] for x in answer["intermediate_steps"]],
        )

    def _set_prompt(self, query: str) -> str:
        """
        Formats and returns a prompt string for executing in a different context based on the given query.

        This method constructs a multi-line prompt that includes instructions and guidelines for processing data,
        formatting output, and interaction rules within a specified tool environment. The prompt includes reading
        a CSV file, output formatting preferences, language specifications, and additional guidelines about plot
        generation and markdown syntax.

        Args:
        query (str): The user's input query that will be appended to the conversation history in the prompt.

        Returns:
        str: A formatted string that serves as a prompt for further processing in another context.
        """
        return (
            "# Siga TODAS as seguintes instruções\n"
            f"- Leia os dados do csv '{self.filepath}'.\n"
            f"- Formate os outputs para markdown.\n"
            f"- Os outputs devem estar em português.\n"
            f"- NÃO exiba figuras em código markdown com a sintaxe `![<alt>](<path>)`.\n"
            "- NÃO use `python_repl_ast` para gerar plots. Se precisar gerar plots, use a tool `plot_generator`. "
            "Quando for pasar o código do matplotlib para a tool, não esqueça de passar a instrucao `plt.show()`\n\n"
            "# Histórico de conversa\n"
            f"{self.memory.buffer_as_str}\n{self.memory.human_prefix}: {query}\n\n"
        )

    def _parse_answer(self, query: str, answer: dict) -> list:
        """
        Parse the answer to a query.

        This method checks if the provided `answer` dictionary contains a figure. If it does, it calls the `_parse_figures()` method to parse the figures.
        If the `answer` does not contain a figure, it calls the `_parse_markdown()` method to parse the answer as Markdown.

        Args:    def _parse_answer(self, query, answer):
            if _has_figure_in_answer(answer):
                return self._parse_figures(query, answer)
            return self._parse_markdown(query, answer)
            query (str): The original query.
            answer (dict): The answer dictionary, which may contain figures or Markdown.

        Returns:
            list: A list of `memory_text` elements, which can be either Markdown-formatted strings or Pandas DataFrames.
        """
        try:
            if _has_figure_in_answer(answer):
                return self._parse_figures(query, answer)
            return self._parse_markdown(query, answer)
        except Exception as err:
            logger.warning(f"Error on _parse_markdown:\n{traceback.print_exc()}")
            return self._parse_raw(query, answer)

    def _parse_raw(self, query: str, answer: dict) -> list[ChatResponse]:
        """
        Parses the raw response from the language model and saves the context.

        Args:
            query (str): The original user query.
            answer (dict): The response dictionary from the language model, containing the output.

        Returns:
            list[ChatResponse]: A list of ChatResponse objects representing the parsed response.
        """
        self.memory.save_context(
            {"input": query},
            {"output": [answer["output"]]},
        )
        return [ChatMarkdownResponse(answer["output"])]

    def _parse_figures(self, query: str, answer: Dict[str, Any]) -> List[ChatResponse]:
        """
        Parses plotting information from a given answer and updates the context memory.
        Sets the background color of the current figure to transparent.

        Parameters:
        - query (str): The query string that resulted in the answer.
        - answer (Dict[str, Any]): A dictionary containing the output and intermediate
        steps of some computation that may include plots.

        Returns:
        - List[Any]: A list containing the final output string and the figure object.
        """

        fig = plt.gcf()
        fig.set_facecolor("none")

        action, response = answer["intermediate_steps"][-1]

        self.memory.save_context(
            {"input": query},
            {
                "output": (
                    f'{answer["output"]} | '
                    f'Title: {str(action.tool_input["plot_description"])} | '
                    f"Code: {str(response)}."
                )
            },
        )
        return [ChatMarkdownResponse(answer["output"]), response]

    def _parse_markdown(self, query: str, answer: Dict[str, Any]) -> List[ChatResponse]:
        """
        Processes the markdown output from an answer dictionary, handles tables represented
        by pandas DataFrames, and updates the memory context.

        Parameters:
        - query (str): The input query that resulted in the answer.
        - answer (Dict[str, Any]): A dictionary containing the output of some computation,
        potentially including markdown and DataFrames.

        Returns:
        - List[Any]: A list of elements formatted as markdown or strings, including DataFrames
        if present.
        """

        elements: list[ChatResponse] = [
            x for x in parse_markdown_text(answer["output"])
        ]
        memory_text: list[str] = [
            e.df.to_markdown() if isinstance(e, ChatDataFrameResponse) else str(e)
            for e in elements
        ]
        self.memory.save_context(
            {"input": query},
            {"output": " ".join(memory_text)},
        )

        return elements

    @classmethod
    def get_tools(cls) -> list[StructuredTool]:
        """
        Retrieves a list of structured tools from the CSVExplorer tools file.

        Returns:
            A list of StructuredTool objects representing the available tools.
        """
        module = "csv_explorer.tools"
        decorator_name = "tool"

        with open(CSVExplorer.tools_filepath, "r") as file:
            tree = ast.parse(file.read(), filename=CSVExplorer.tools_filepath)

        functions_with_decorator = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            for decorator in node.decorator_list
            if isinstance(decorator, ast.Name) and decorator.id == decorator_name
        ]

        return [_import_function(module, f) for f in functions_with_decorator]

    @classmethod
    def list_agents():
        """
        Returns a list of available AI agents.

        Returns:
            list: A list of available AI agents.
        """
        return AGENTS

    @classmethod
    def list_llm_models():
        """
        Returns a list of available language models for the AI agent.

        Returns:
            list: A list of available language models.
        """
        return list(LLM_MODELS.keys())

    def set(self, **kwargs: dict) -> "CSVExplorer":
        """
        Set one or more attributes of the CSVExplorer instance.

        Args:
            **kwargs: A dictionary of keyword arguments, where the keys are the names of the attributes to be set,
                and the values are the new values for those attributes.

        Returns:
            The CSVExplorer instance, after the attributes have been set.
        """
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
        return self.reset()

    def _set_model(self, model: str) -> str:
        """
        Set the model to be used by the CSVExplorer instance.

        This method checks if the provided `model` is a valid LLM (Large Language Model) model, as defined in the `LLM_MODELS` constant.
        If the model is not recognized, it raises a `LLMModelNotRecognized` exception.
        If the model is valid, it returns the model string.

        Args:
            model (str): The name of the LLM model to be set.

        Raises:
            LLMModelNotRecognized: If the provided `model` is not a valid LLM model.

        Returns:
            str: The provided `model` string, if it is a valid LLM model.
        """
        if model not in LLM_MODELS:
            raise LLMModelNotRecognized()
        return model

    def _set_llm(self) -> Any:
        """
        Set the Large Language Model (LLM) to be used by the CSVExplorer instance.

        This method retrieves the LLM model specified by the `self.model` attribute from the `LLM_MODELS` dictionary.
        It then initializes the LLM model with the `self.model`, `self.temperature`, and `verbose=True` parameters.

        Returns:
            Any: The initialized LLM model instance.
        """
        return LLM_MODELS[self.model](
            model=self.model, temperature=self.temperature, verbose=True
        )

    def _set_tools(self, extra_tools: str) -> str:
        """
        Set the additional tools to be used by the CSVExplorer instance.

        This method takes an `extra_tools` string and appends it to the result of the `CSVExplorer.get_tools()` method.
        The resulting string is then returned.

        Args:
            extra_tools (str): The additional tools to be added to the CSVExplorer instance.

        Returns:
            str: The combined set of tools, including the additional `extra_tools`.
        """
        return CSVExplorer.get_tools() + extra_tools

    def _set_agent_type(self, agent_type: str) -> str:
        """
        Set the agent type for the CSVExplorer instance.

        This method checks if the provided `agent_type` is a valid agent type, as defined in the `AGENTS` constant.
        If the agent type is not recognized, it raises an `AgentTypeNotRecognized` exception.
        If the agent type is valid, it returns the agent type string.

        Args:
            agent_type (str): The name of the agent type to be set.

        Raises:
            AgentTypeNotRecognized: If the provided `agent_type` is not a valid agent type.

        Returns:
            str: The provided `agent_type` string, if it is a valid agent type.
        """
        if agent_type not in AGENTS:
            raise AgentTypeNotRecognized()
        return agent_type

    def _set_memory(self):
        """
        Set the memory for the CSVExplorer instance.

        This method creates a new `ConversationBufferWindowMemory` instance with a window size of `self.memory_k`.
        It then saves an initial context with an "input" of "Olá!" and an "output" of "Olá!. Como posso ajudar?".
        Finally, it returns the created memory instance.

        Returns:
            ConversationBufferWindowMemory: The initialized memory instance for the CSVExplorer.
        """
        memory = ConversationBufferWindowMemory(k=self.memory_k)
        memory.save_context({"input": "Olá!"}, {"output": "Olá!. Como posso ajudar?"})
        return memory

    @classmethod
    def _set_temp_folder(cls):
        _create_directory_if_not_exists(cls.temp_filepath)


def _create_directory_if_not_exists(folderpath: str) -> None:
    """
    Ensures that the specified directory exists. If the directory does not exist,
    it creates the directory along with any necessary parent directories.

    Args:
        folderpath (str): The path to the directory that needs to be checked and
                          potentially created.

    Returns:
        None: This function does not return anything. It ensures the directory is created.
    """
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)


def _import_function(module_name: str, function_name: str) -> Optional[Any]:
    """
    Importa uma função de um módulo e retorna a função.

    Args:
        module_name (str): O nome do módulo a ser importado.
        function_name (str): O nome da função a ser obtida do módulo.

    Returns:
        Optional[Any]: A função importada, se encontrada. Caso contrário, retorna None.
    """
    try:
        module = import_module(module_name)
        function = getattr(module, function_name)
        return function
    except ImportError:
        print(f"Módulo {module_name} não encontrado.")
    except AttributeError:
        print(f"Função {function_name} não encontrada no módulo {module_name}.")


def _has_figure_in_answer(answer: dict) -> bool:
    """
    Checks if the given answer contains any plots generated by a "plot_generator" tool.

    This function looks into the 'intermediate_steps' of the provided answer dictionary.
    It logs the presence or absence of intermediate steps and plots, helping in debugging
    and verification of processing steps.

    Args:
        answer (dict): The answer dictionary potentially containing various processing steps.

    Returns:
        bool: True if a plot is found in the answer, False otherwise.
    """

    if "intermediate_steps" not in answer:
        logger.info("No intermediate steps found in answer")
        return False

    action = answer["intermediate_steps"][-1][0]

    if action.tool == "plot_generator":
        logger.info("Plot found in answer")
        return True
    logger.info("No plot found in answer")
    return False


class AgentTypeNotRecognized(Exception):
    pass


class LLMModelNotRecognized(Exception):
    pass
