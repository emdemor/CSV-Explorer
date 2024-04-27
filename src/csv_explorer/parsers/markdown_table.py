import re
import pandas as pd
from typing import List, Generator, Tuple, Dict, Union

MARKDOWN_TABLE_REPLACEMENTS: Dict[str, str] = {
    "-:-": "---",
    "|:-": "|--",
    "| :-": "|---",
    "-:|": "--|",
    "-: |": "---|",
    "- |": "--|",
    "| -": "|--",
    "| :": "|--",
    ":  |": "--|",
}

MARKDOWN_TABLE_REGEX = r"(?:\|.*\|\r?\n)+\|(?:-+\|)+\r?\n(?:\|.*\|\r?\n)+"


def parse_markdown_text(text: str) -> Generator[Union[str, pd.DataFrame], None, None]:
    """
    Parses the given text, extracting and converting any markdown tables to Pandas DataFrames.

    Args:
        text (str): The input text to be parsed.

    Yields:
        Union[str, pd.DataFrame]: Either a string or a Pandas DataFrame, depending on the content of the input text.
    """

    formatted_text = _format_markdown_tables(text)
    tables = _extract_markdown_tables(formatted_text)
    pieces = _split_text_by_substrings(formatted_text, tables)

    for i, piece in enumerate(pieces):
        if i % 2 == 0:
            yield piece
        else:
            yield md_to_pandas(piece)


def _format_markdown_tables(text: str) -> str:
    """
    Formats the given text by replacing specific markdown table syntax with the appropriate formatting.

    Args:
        text (str): The input text to be formatted.

    Returns:
        str: The formatted text.
    """
    for old, new in MARKDOWN_TABLE_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text + "\n\n"


def _extract_markdown_tables(text: str) -> List[str]:
    """
    Extracts all markdown tables from the given text.

    Args:
        text (str): The input text to search for markdown tables.

    Returns:
        List[str]: A list of extracted markdown tables.
    """
    return re.findall(MARKDOWN_TABLE_REGEX, text, re.MULTILINE)


def _split_text_by_substrings(text: str, substrings: List[str]) -> List[str]:
    """
    Splits the given text into a list of substrings based on the provided substrings.

    Args:
        text (str): The input text to be split.
        substrings (List[str]): The list of substrings to use for splitting the text.

    Returns:
        List[str]: A list of substrings.
    """
    regex_pattern = "|".join(map(re.escape, substrings))
    return [piece for piece in re.split(f"({regex_pattern})", text) if piece]


def md_to_pandas(md_table_string: str) -> pd.DataFrame:
    """
    Converts a markdown table string to a Pandas DataFrame.

    Args:
        md_table_string (str): The markdown table string to be converted.

    Returns:
        pd.DataFrame: A Pandas DataFrame representing the markdown table.
    """
    lines = md_table_string.split("\n")
    content_lines = [
        line[1:-1].strip().split("|")
        for line in lines
        if any(x not in ["|", "-", ":", " "] for x in line)
    ]
    return pd.DataFrame(content_lines[1:], columns=content_lines[0])
