import typer
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

app = typer.Typer(help="Settings Menu")
console = Console()

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Interactive Settings Menu."""
    if ctx.invoked_subcommand is not None:
        return

    while True:
        console.clear()
        console.print(Panel.fit("Omarchy Settings", style="bold blue"))
        
        print("1. Network (WiFi)")
        print("2. Bluetooth")
        print("3. Focus Mode")
        print("4. Keybindings")
        print("5. Install Packages")
        print("6. Pomodoro Timer")
        print("q. Quit")
        
        choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6", "q"])
        
        if choice == "q":
            break
        elif choice == "1":
            subprocess.run(["hackeros", "wifi"])
        elif choice == "2":
            subprocess.run(["hackeros", "bluetooth"])
        elif choice == "3":
            subprocess.run(["hackeros", "focus", "toggle"])
            input("Press Enter to continue...")
        elif choice == "4":
            subprocess.run(["hackeros", "keys"])
            input("Press Enter to continue...")
        elif choice == "5":
            subprocess.run(["hackeros", "install", "--dry-run"]) # Default to dry run for safety in menu
            input("Press Enter to continue...")
        elif choice == "6":
            subprocess.run(["hackeros", "pomodoro", "status"])
            input("Press Enter to continue...")
