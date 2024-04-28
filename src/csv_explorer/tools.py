import os
import json
import uuid
import pandas as pd
from langchain.agents import tool
from tabulate import tabulate
import matplotlib.pyplot as plt
from langchain_experimental.utilities import PythonREPL
from csv_explorer_ui.config import PLT_STYLE
from csv_explorer.tool_response import ToolResponse, ToolDataFrameResponse


@tool
def plot_generator(
    matplotlib_code: str, csv_filepath: str, plot_description: str
) -> str:
    """
    Use this tool whenever you need to generate a plot (like pizza, histogram, line-plot, scatter-plot, heatmap and similars)
    It receives a matplotlib code, a csv_filepath and a plot_description, reads the data in CSV filepath and generates the plot.
    """

    prefix = ""

    imports = [
        "import matplotlib",
        "import matplotlib.pyplot as plt",
        "import seaborn as sns",
        "import pandas as pd",
        "import numpy as np",
        "from cycler import cycler",
    ]

    for _imp in imports:
        if _imp not in matplotlib_code:
            prefix = _imp + "\n" + prefix

    if "import matplotlib.pyplot as plt" in prefix:
        prefix += "\n" + f"plt.style.use('{PLT_STYLE}')"
        prefix += "\n" + "plt.rcParams['figure.facecolor'] = 'none'"
        prefix += "\n" + "plt.rcParams['axes.facecolor'] = 'none'"
        prefix += (
            "\n"
            + "plt.rc('axes', prop_cycle=(cycler('color', ['#14149a', '#ec6810', '#4A8DC4', '#F24405', '#1C2641', '#F7A55A',  '#61408a', '#8C5483',  '#D99F6C', '#32088C',  '#e377c2', '#3314A6'])))"
        )

    if "matplotlib.use('Agg')" not in prefix:
        prefix = "import matplotlib\n" "matplotlib.use('Agg')\n" f"{prefix}"

    if f"pd.read_csv('{csv_filepath}')" not in matplotlib_code:
        matplotlib_code = f"df = pd.read_csv('{csv_filepath}')\n\n" f"{matplotlib_code}"

    if "plt.show()" not in matplotlib_code:
        matplotlib_code = matplotlib_code + "\n" + "plt.show()"

    matplotlib_code = prefix + "\n" + matplotlib_code

    try:
        python_repl = PythonREPL()
        python_repl.run(matplotlib_code)
        return f"\n```\n{matplotlib_code}\n```\n"
    except Exception as err:
        return f"[ERROR] Not possible to run 'plot_generator'. Error: {err}"


@tool
def infer_column_types_of_csv_file(csv_filepath: str) -> str:
    """
    Infers the types of columns in a CSV file and categorizes them as 'Numeric',
    'Categorical', 'Boolean', 'Text', or 'Other'.
    """

    try:
        df = pd.read_csv(csv_filepath, nrows=5)

        basic_types = df.dtypes
        inferred_types = {}
        for column, dtype in basic_types.items():
            if dtype == "object" or dtype.name == "category":
                unique_values = df[column].nunique()
                if unique_values < 10:
                    inferred_types[column] = "Categorical"
                else:
                    inferred_types[column] = "Text"
            elif dtype in ["int64", "float64"]:
                inferred_types[column] = "Numeric"
            elif dtype == "bool":
                inferred_types[column] = "Boolean"
            else:
                inferred_types[column] = "Other"

        return ToolDataFrameResponse(
            pd.DataFrame(
                [t for t in inferred_types.items()],
                columns=["column", "type"],
            )
        )
    except Exception as err:
        return f"[ERROR]. Not possible to run 'infer_column_types_of_csv_file'. Error: {err}"


@tool
def get_column_names(csv_filepath: str) -> str:
    """Get a dataframe from csv filepeth and extracts the column names."""
    try:
        df = pd.read_csv(csv_filepath, nrows=2)
        return ", ".join(df.columns)
    except Exception as err:
        return f"[ERROR]. Not possible to run 'get_column_names'. Error: {err}"


@tool
def generate_descriptive_statistics(csv_filepath: str) -> ToolResponse:
    """
    Generate a formatted table of descriptive statistics for a given DataFrame from csv path.
    This function calculates descriptive statistics that summarize the central
    tendency, dispersion, and shape of a dataset’s distribution, excluding NaN values.
    It includes statistics like mean, median, mode, standard deviation, and more for
    each column. Can be used to describe the database and get some general insights.
    """
    try:
        df = pd.read_csv(csv_filepath).describe(include="all")
        return ToolDataFrameResponse(df)
    except Exception as err:
        return f"[ERROR]. Not possible to run 'generate_descriptive_statistics'. Error: {err}"


@tool
def python_evaluator(python_code: str, csv_filepath: str) -> str:
    """
    Use essa ferramente quando tiver que fazer cálculos complexos, que não podem ser oriundos da estatística descritiva.
    """
    try:
        python_repl = PythonREPL()
        python_repl.run(python_code)
        return f"\n```\n{python_code}\n```\n"
    except Exception as err:
        return f"[ERROR] Not possible to run 'python_evaluator'. Error: {err}"
