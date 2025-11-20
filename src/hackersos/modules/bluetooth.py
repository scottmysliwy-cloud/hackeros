import typer
import subprocess
from hackersos.utils import command_exists, notify

app = typer.Typer(help="Bluetooth Management")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Launch bluetooth manager TUI."""
    if ctx.invoked_subcommand is not None:
        return

    if command_exists("bluetuith"):
        subprocess.run(["bluetuith"])
    elif command_exists("bluetoothctl"):
        # bluetoothctl is interactive but not a full TUI in the same sense, but better than nothing
        subprocess.run(["bluetoothctl"])
    else:
        from hackersos.utils import logger
        logger.error("bluetuith or bluetoothctl not found.")
        notify("Bluetooth Error", "No bluetooth tool found.", urgency="critical")
