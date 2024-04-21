import typer

from dotenv import load_dotenv

import csv_explorer_ui


app = typer.Typer()

front_app = typer.Typer()
app.add_typer(front_app, name="frontend")


@front_app.command()
def start():
    csv_explorer_ui.run()


if __name__ == "__main__":
    load_dotenv()
    app()
