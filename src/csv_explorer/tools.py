
import json
import pandas as pd
from langchain.agents import tool
from tabulate import tabulate
import matplotlib.pyplot as plt
from langchain_experimental.utilities import PythonREPL



@tool
def infer_column_types_of_csv_file(filepath: str) -> str:
    """
    Infers the types of columns in a CSV file and categorizes them as 'Numeric', 
    'Categorical', 'Boolean', 'Text', or 'Other'.
    """

    try:
        df = pd.read_csv(filepath, nrows=5)
        
        basic_types = df.dtypes
        inferred_types = {}
        for column, dtype in basic_types.items():
            if dtype == 'object' or dtype.name == 'category':
                unique_values = df[column].nunique()
                if unique_values < 10:
                    inferred_types[column] = 'Categorical'
                else:
                    inferred_types[column] = 'Text'
            elif dtype in ['int64', 'float64']:
                inferred_types[column] = 'Numeric'
            elif dtype == 'bool':
                inferred_types[column] = 'Boolean'
            else:
                inferred_types[column] = 'Other'
        
        return json.dumps(inferred_types, indent=2, ensure_ascii=False)
    except Exception as err:
        return f"[ERROR]. Not possible to run 'infer_column_types_of_csv_file'. Error: {err}"

@tool
def get_column_names(filepath: str) -> str:
    """Get a dataframe from csv filepeth and extracts the column names."""
    try:
        df = pd.read_csv(filepath, nrows=2)
        return ", ".join(df.columns)
    except Exception as err:
        return f"[ERROR]. Not possible to run 'get_column_names'. Error: {err}"

@tool
def generate_descriptive_statistics(filepath: str) -> str:
    """
    Generate a formatted table of descriptive statistics for a given DataFrame from csv path.
    This function calculates descriptive statistics that summarize the central
    tendency, dispersion, and shape of a dataset’s distribution, excluding NaN values.
    It includes statistics like mean, median, mode, standard deviation, and more for
    each column. Can be used to describe the database and get some general insights.
    """
    try:
        df = pd.read_csv(filepath)
        return tabulate(df.describe(include="all"), headers="keys")
    except Exception as err:
        return f"[ERROR]. Not possible to run 'generate_descriptive_statistics'. Error: {err}"