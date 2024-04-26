import os, sys

import csv_explorer_ui
from streamlit import runtime
from streamlit.web import cli as stcli

from csv_explorer_ui.elements.front import front


def run():

    path = os.path.join(
        os.sep.join(os.path.abspath(csv_explorer_ui.__file__).split(os.sep)[:-1]),
        "__init__.py",
    )

    if runtime.exists():
        front()

    else:
        sys.argv = ["streamlit", "run", path]
        sys.exit(stcli.main())


if __name__ == "__main__":
    run()
