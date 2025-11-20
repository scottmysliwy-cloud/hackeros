import typer
import re
from pathlib import Path
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Keybindings Viewer")
console = Console()

CONFIG_DIR = Path.home() / ".config" / "hypr"

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """View Hyprland keybindings."""
    if ctx.invoked_subcommand is not None:
        return

    bindings = []
    
    # Files to search
    files = [
        CONFIG_DIR / "hyprland.conf",
        CONFIG_DIR / "bindings.conf",
        CONFIG_DIR / "input.conf"
    ]
    
    # Also check default omarchy bindings if they exist
    default_bindings = Path.home() / ".local/share/omarchy/default/hypr/bindings.conf"
    if default_bindings.exists():
        files.append(default_bindings)

    for file in files:
        if file.exists():
            with open(file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("bind ="):
                        # Parse bind = MOD, KEY, dispatcher, arg
                        # Example: bind = $mainMod, Q, exec, kitty
                        parts = line.split(",")
                        if len(parts) >= 4:
                            mod = parts[0].replace("bind =", "").strip()
                            key = parts[1].strip()
                            action = parts[2].strip()
                            arg = ",".join(parts[3:]).strip()
                            bindings.append((mod, key, action, arg))

    if not bindings:
        print("No keybindings found.")
        return

    table = Table(title="Hyprland Keybindings")
    table.add_column("Modifier", style="cyan")
    table.add_column("Key", style="green")
    table.add_column("Action", style="magenta")
    table.add_column("Command", style="yellow")

    for mod, key, action, arg in bindings:
        table.add_row(mod, key, action, arg)

    console.print(table)
