import typer
import subprocess
from hackeros.utils import command_exists, notify

app = typer.Typer(help="Network Management")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Launch network manager TUI."""
    if ctx.invoked_subcommand is not None:
        return

    if command_exists("nmtui"):
        subprocess.run(["nmtui"])
    else:
        from hackeros.utils import logger
        logger.error("nmtui not found. Please install NetworkManager-tui.")
        notify("Network Error", "nmtui not found.", urgency="critical")
