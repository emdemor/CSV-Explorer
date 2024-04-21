import importlib.metadata
from csv_explorer._csv_explorer import CSVExplorer

__version__ = importlib.metadata.version("csv_explorer")
__all__ = [
    "CSVExplorer",
]
