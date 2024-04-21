import typer

from dotenv import load_dotenv

import ui


app = typer.Typer()

front_app = typer.Typer()
app.add_typer(front_app, name="frontend")


@front_app.command()
def start():
    ui.run()


if __name__ == "__main__":
    load_dotenv()
    app()
