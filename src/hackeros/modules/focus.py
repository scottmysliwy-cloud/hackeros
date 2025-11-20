import typer
import subprocess
from hackeros.utils import notify, run_command, get_cache_dir, command_exists

app = typer.Typer(help="Manage Focus Mode")

STATE_FILE = get_cache_dir() / "focus_mode"

def get_state() -> str:
    if STATE_FILE.exists():
        return STATE_FILE.read_text().strip()
    return "off"

def set_state(state: str):
    STATE_FILE.write_text(state)

@app.command()
def on():
    """Enable Focus Mode (DND, hide Waybar)."""
    print("Enabling Focus Mode...")
    run_command(["makoctl", "mode", "-a", "dnd"], check=False)
    
    run_command(["pkill", "waybar"], check=False)
    
    notify("Focus Mode", "Enabled. Distractions minimized.")
    set_state("on")

@app.command()
def off():
    """Disable Focus Mode."""
    print("Disabling Focus Mode...")
    run_command(["makoctl", "mode", "-r", "dnd"], check=False)
    
    # Restore Waybar if not running
    try:
        run_command(["pgrep", "-x", "waybar"])
    except subprocess.CalledProcessError:
        # Waybar not running
        if command_exists("uwsm-app"):
            subprocess.Popen(["uwsm-app", "--", "waybar"])
        else:
            subprocess.Popen(["waybar"])

    notify("Focus Mode", "Disabled. Welcome back.")
    set_state("off")

@app.command()
def toggle():
    """Toggle Focus Mode."""
    if get_state() == "on":
        off()
    else:
        on()

@app.command()
def status():
    """Show Focus Mode status."""
    print(get_state())
