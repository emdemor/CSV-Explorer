import os
from importlib import resources

import csv_explorer

TITLE = "CSV Explorer"

LOGO_FILENAME = str(resources.files("csv_explorer_ui.assets").joinpath("logo.png"))

EXAMPLES_PATH = resources.files("csv_explorer.examples")