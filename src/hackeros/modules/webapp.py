import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.prompt import Prompt

console = Console()

class WebAppManager:
    def __init__(self):
        self.apps_dir = Path.home() / ".local/share/applications"
        self.icons_dir = self.apps_dir / "icons"
        self.apps_dir.mkdir(parents=True, exist_ok=True)
        self.icons_dir.mkdir(parents=True, exist_ok=True)

    def install(self, name: str, url: str, icon_url: str):
        """Create a web app shortcut."""
        console.print(f"Creating web app: {name}")
        
        # Download icon
        icon_path = self.icons_dir / f"{name}.png"
        if icon_url.startswith("http"):
            try:
                subprocess.run(["curl", "-sL", "-o", str(icon_path), icon_url], check=True)
            except subprocess.CalledProcessError:
                console.print("[red]Failed to download icon.[/red]")
                return
        else:
            # Local file or existing icon
            src = Path(icon_url)
            if src.exists():
                shutil.copy(src, icon_path)
            else:
                console.print(f"[yellow]Icon not found at {icon_url}, using placeholder.[/yellow]")
                # Could touch file or use default

        # Create .desktop file
        desktop_file = self.apps_dir / f"{name}.desktop"
        content = f"""[Desktop Entry]
Version=1.0
Name={name}
Comment={name}
Exec=omarchy-launch-webapp {url}
Terminal=false
Type=Application
Icon={icon_path}
StartupNotify=true
"""
        with open(desktop_file, "w") as f:
            f.write(content)
        
        desktop_file.chmod(0o755)
        console.print(f"[green]Web app created at {desktop_file}[/green]")

    def remove(self, names: List[str]):
        """Remove web app shortcuts."""
        for name in names:
            desktop_file = self.apps_dir / f"{name}.desktop"
            icon_file = self.icons_dir / f"{name}.png"
            
            if desktop_file.exists():
                desktop_file.unlink()
                console.print(f"Removed {desktop_file}")
            
            if icon_file.exists():
                icon_file.unlink()
                console.print(f"Removed {icon_file}")

    def list_apps(self) -> List[str]:
        """List installed web apps."""
        apps = []
        if self.apps_dir.exists():
            for f in self.apps_dir.glob("*.desktop"):
                # Check if it's a web app (heuristic: Exec contains omarchy-launch-webapp)
                with open(f, "r") as file:
                    if "omarchy-launch-webapp" in file.read():
                        apps.append(f.stem)
        return sorted(apps)

app = typer.Typer()
webapp_manager = WebAppManager()

@app.command()
def install(
    name: str = typer.Option(..., prompt=True),
    url: str = typer.Option(..., prompt=True),
    icon: str = typer.Option(..., prompt="Icon URL/Path")
):
    """Install a new web application."""
    webapp_manager.install(name, url, icon)

@app.command()
def remove(names: List[str] = typer.Argument(None)):
    """Remove web applications."""
    if not names:
        # Interactive selection
        apps = webapp_manager.list_apps()
        if not apps:
            console.print("No web apps found.")
            return
        
        # Simple list for now, could use gum/fzf if available or rich prompt
        console.print("Installed web apps:")
        for app in apps:
            console.print(f"- {app}")
        names = Prompt.ask("Enter names to remove (space separated)").split()

    webapp_manager.remove(names)

@app.command("list")
def list_webapps():
    """List installed web applications."""
    apps = webapp_manager.list_apps()
    for app in apps:
        console.print(app)
