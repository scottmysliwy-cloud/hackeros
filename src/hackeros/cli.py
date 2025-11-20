import typer
from rich.console import Console

app = typer.Typer(
    name="hackeros",
    help="Hackeros CLI tools",
    add_completion=False,
)
console = Console()

from hackeros.modules import packages, theme, setup, webapp
from hackeros.modules import focus, capture, context, pomodoro, install, network, bluetooth, keybindings, settings

app.add_typer(focus.app, name="focus")
app.add_typer(capture.app, name="capture")
app.add_typer(context.app, name="context")
app.add_typer(pomodoro.app, name="pomodoro")
app.add_typer(install.app, name="install")
app.add_typer(network.app, name="wifi")
app.add_typer(bluetooth.app, name="bluetooth")
app.add_typer(keybindings.app, name="keys")
app.add_typer(settings.app, name="settings")

app.add_typer(packages.app, name="pkg")
app.add_typer(theme.app, name="theme")
app.add_typer(setup.app, name="setup")
app.add_typer(webapp.app, name="webapp")

@app.callback()
def main():
    """
    HackerOS CLI tools for managing your system.
    """
    pass

if __name__ == "__main__":
    app()
