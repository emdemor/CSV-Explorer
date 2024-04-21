import os
from importlib import resources

import csv_explorer

TITLE = "CSV Explorer"

TOOLS_FILEPATH = os.path.join("/".join(os.path.abspath(csv_explorer.__file__).split("/")[:-1]), "tools.py")

TEMP_FILEPATH = "/tmp"

LOGO_FILENAME = str(resources.files("csv_explorer_ui.assets").joinpath("logo.png"))

EXAMPLES_PATH = resources.files("csv_explorer.examples")