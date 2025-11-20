import subprocess
import sys
import shutil
import os
import logging
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler
from rich.prompt import Prompt

console = Console()

def setup_logging(level="INFO"):
    """Setup rich logging."""
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )
    return logging.getLogger("hackeros")

logger = setup_logging()

def require_non_root():
    """Ensure the script is NOT run as root (makepkg safety)."""
    if os.geteuid() == 0:
        logger.critical("Do NOT run this script as root/sudo.")
        logger.critical("Run as a normal user. Sudo will be requested when needed.")
        sys.exit(1)

def ensure_line_in_file(path: Path, line: str):
    """Safely ensure a line exists in a file, handling newlines."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("")

    content = path.read_text()
    lines = content.splitlines()

    if any(l.strip() == line.strip() for l in lines):
        return

    # Safety: Ensure file ends with newline before appending
    prefix = "\n" if content and not content.endswith("\n") else ""
    
    with open(path, "a") as f:
        f.write(f"{prefix}{line}\n")

def notify(title: str, message: str, urgency: str = "normal"):
    """Send a desktop notification."""
    # Only notify if we are in a graphical session
    if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
        subprocess.run(["notify-send", "-u", urgency, title, message], check=False)
    else:
        logger.info(f"Notification [{urgency}]: {title} - {message}")

def run_command(command: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command."""
    return subprocess.run(command, check=check, text=True, capture_output=True)

def command_exists(cmd: str) -> bool:
    """Check if a command exists in PATH."""
    return shutil.which(cmd) is not None

def get_cache_dir() -> Path:
    """Get the cache directory for omarchy."""
    path = Path.home() / ".cache" / "omarchy"
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_documents_dir() -> Path:
    """Get the documents directory."""
    return Path.home() / "Documents"
