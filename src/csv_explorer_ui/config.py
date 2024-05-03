import os
from importlib import resources

import csv_explorer_ui

TITLE = "CSV Explorer"

LOGO_FILEPATH = str(resources.files("csv_explorer_ui.assets").joinpath("logo.png"))

STYLE_FILEPATH = str(resources.files("csv_explorer_ui.assets").joinpath("style.css"))

EXAMPLES_PATH = resources.files("csv_explorer.examples")

PLT_STYLE = str(resources.files("csv_explorer_ui.assets").joinpath("plots.mplstyle"))

INSTRUCTIONS_PATH = str(resources.files("csv_explorer_ui.assets").joinpath("instructions.md"))

if os.environ.get("ENV", "local") == "local":
    LOGS_PATH = "logs"
else:
    LOGS_PATH = os.path.join(
        os.sep.join(os.path.abspath(csv_explorer_ui.__file__).split(os.sep)[:-1]),
        "logs",
    )

if not os.path.exists(LOGS_PATH):
    os.makedirs(LOGS_PATH) 

ICON_ALERT = "🚨"
ICON_HIGH_TEMPERATURE = "🌡️"
ICON_ERROR = "❌"
ICON_SUCCESS = "✅"