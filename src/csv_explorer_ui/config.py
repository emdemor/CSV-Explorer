import os
from importlib import resources

import csv_explorer

TITLE = "CSV Explorer"

LOGO_FILEPATH = str(resources.files("csv_explorer_ui.assets").joinpath("logo.png"))

STYLE_FILEPATH = str(resources.files("csv_explorer_ui.assets").joinpath("style.css"))

EXAMPLES_PATH = resources.files("csv_explorer.examples")

PLT_STYLE = str(resources.files("csv_explorer_ui.assets").joinpath("plots.mplstyle"))