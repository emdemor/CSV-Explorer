from importlib import resources

TITLE = "CSV Explorer"

LOGO_FILENAME = str(resources.files("ui.assets").joinpath("logo.png"))

EXAMPLES_PATH = resources.files("bot.examples")