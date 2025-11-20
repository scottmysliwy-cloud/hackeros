import typer
import json
import subprocess
from hackersos.utils import notify, run_command, get_cache_dir

app = typer.Typer(help="Context Management")

CONTEXT_FILE = get_cache_dir() / "context_state.json"

@app.command()
def save():
    """Save current context (open apps)."""
    print("Saving context...")
    try:
        result = run_command(["hyprctl", "clients", "-j"])
        CONTEXT_FILE.write_text(result.stdout)
        notify("Context", "Current state saved.")
    except subprocess.CalledProcessError:
        notify("Context", "Failed to save context (Hyprland not running?)", urgency="critical")
        raise typer.Exit(1)

@app.command()
def restore():
    """Restore context (show summary)."""
    if not CONTEXT_FILE.exists():
        notify("Context", "No saved context found.")
        raise typer.Exit(1)

    print("Restoring context...")
    try:
        data = json.loads(CONTEXT_FILE.read_text())
        app_count = len(data)
        apps = sorted(list(set(client["class"] for client in data)))
        app_list = ", ".join(apps)
        
        notify("Context Restore", f"You had {app_count} apps open: {app_list}")
    except json.JSONDecodeError:
        notify("Context", "Saved context is corrupt.", urgency="critical")
        raise typer.Exit(1)
