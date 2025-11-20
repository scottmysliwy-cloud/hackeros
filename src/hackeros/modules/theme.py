import typer
import json
import re
import shutil
import subprocess
import os
from pathlib import Path
from typing import List, Optional
from hackeros.utils import run_command, notify, console, logger
from hackeros.constants import THEME_DIR, VSCODE_SETTINGS, ALACRITTY_CONFIG, OBSIDIAN_VAULTS_FILE

app = typer.Typer(help="Theme Manager")

class ThemeManager:
    def __init__(self):
        self.theme_dir = THEME_DIR

    def list_themes(self) -> List[str]:
        """List available themes."""
        if not self.theme_dir.exists():
            logger.warning(f"Theme directory {self.theme_dir} does not exist.")
            return []
        
        themes = [d.name for d in self.theme_dir.iterdir() if d.is_dir()]
        return sorted(themes)

    def set_theme(self, theme_name: str):
        """Apply a theme."""
        theme_path = self.theme_dir / theme_name
        if not theme_path.exists():
            logger.error(f"Theme '{theme_name}' not found.")
            raise typer.Exit(1)

        logger.info(f"Applying theme: {theme_name}")
        notify("Theme Manager", f"Applying theme: {theme_name}")

        try:
            with console.status(f"[bold green]Applying theme {theme_name}..."):
                # 1. Link theme directory
                current_theme_link = self.theme_dir / "current"
                if current_theme_link.exists() or current_theme_link.is_symlink():
                    current_theme_link.unlink()
                current_theme_link.symlink_to(theme_path)

                # 2. Reload system components
                self._reload_components()

                # 3. Update specific apps
                self._update_app_themes(theme_path)
            
            logger.info(f"Theme '{theme_name}' applied successfully.")
            notify("Theme Manager", f"Theme '{theme_name}' applied successfully.")

        except Exception as e:
            logger.error(f"Failed to apply theme: {e}")
            notify("Theme Manager", "Failed to apply theme.", urgency="critical")
            raise typer.Exit(1)

    def _reload_components(self):
        """Reload system components (Waybar, SwayOSD, Hyprland, etc.)."""
        logger.debug("Reloading system components...")
        
        # Waybar
        if subprocess.run(["pgrep", "-x", "waybar"], capture_output=True).returncode == 0:
            run_command(["pkill", "-SIGUSR2", "waybar"], check=False)
        
        # SwayOSD
        if subprocess.run(["pgrep", "-x", "swayosd-server"], capture_output=True).returncode == 0:
            run_command(["swayosd-client", "--style", str(self.theme_dir / "current/swayosd.css")], check=False)

        # Hyprland
        run_command(["hyprctl", "reload"], check=False)

        # Mako (Notifications)
        run_command(["makoctl", "reload"], check=False)

    def _update_app_themes(self, theme_path: Path):
        """Update themes for specific applications."""
        logger.debug("Updating application themes...")
        self._set_terminal_theme(theme_path)
        self._set_vscode_theme(theme_path)
        self._set_browser_theme(theme_path)
        self._set_gnome_theme(theme_path)
        self._set_obsidian_theme(theme_path)

    def _set_terminal_theme(self, theme_path: Path):
        """Set terminal theme (Alacritty, Kitty, Ghostty)."""
        # Alacritty: Touch config to reload
        if ALACRITTY_CONFIG.exists():
            ALACRITTY_CONFIG.touch()
        
        # Kitty: Send signal
        if subprocess.run(["pgrep", "-x", "kitty"], capture_output=True).returncode == 0:
            run_command(["pkill", "-SIGUSR1", "kitty"], check=False)

    def _set_vscode_theme(self, theme_path: Path):
        """Set VSCode/Cursor theme."""
        vscode_theme_file = theme_path / "vscode.json"
        if not vscode_theme_file.exists():
            return

        try:
            with open(vscode_theme_file) as f:
                data = json.load(f)
                theme_name = data.get("name")
            
            if not theme_name:
                return

            settings_path = VSCODE_SETTINGS
            if settings_path.exists():
                content = settings_path.read_text()
                # Simple regex replacement for workbench.colorTheme
                new_content = re.sub(
                    r'("workbench.colorTheme":\s*")[^"]+(")', 
                    f'\\1{theme_name}\\2', 
                    content
                )
                settings_path.write_text(new_content)
                logger.debug(f"Updated VSCode theme to {theme_name}")

        except Exception as e:
            logger.warning(f"Failed to set VSCode theme: {e}")

    def _set_browser_theme(self, theme_path: Path):
        """Set Chromium/Brave theme color."""
        chromium_theme_file = theme_path / "chromium.theme"
        if not chromium_theme_file.exists():
            return

        color = chromium_theme_file.read_text().strip()
        logger.debug(f"Browser theme color: {color} (Implementation pending permission handling)")

    def _set_gnome_theme(self, theme_path: Path):
        """Set GNOME/GTK theme."""
        light_mode_file = theme_path / "light.mode"
        is_light = light_mode_file.exists()
        
        color_scheme = "default" if is_light else "prefer-dark"
        run_command(["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", color_scheme], check=False)
        
        # GTK Theme
        gtk_theme = "Adwaita" # Placeholder
        run_command(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", gtk_theme], check=False)

    def _set_obsidian_theme(self, theme_path: Path):
        """Set Obsidian theme."""
        # Copy obsidian.css to vaults
        obsidian_css = theme_path / "obsidian.css"
        if not obsidian_css.exists():
            return

        # Logic to find vaults would go here. For now, just a placeholder.
        logger.debug("Obsidian theme update not fully implemented (requires vault discovery).")


@app.command()
def list():
    """List installed themes."""
    manager = ThemeManager()
    themes = manager.list_themes()
    if not themes:
        logger.info("No themes found.")
        return
    
    console.print("[bold]Available Themes:[/bold]")
    for theme in themes:
        console.print(f" - {theme}")

@app.command()
def set(name: str):
    """Set the active theme."""
    manager = ThemeManager()
    manager.set_theme(name)

if __name__ == "__main__":
    app()
