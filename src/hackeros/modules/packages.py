import subprocess
import shutil
from pathlib import Path
from typing import List, Set

class PackageManager:
    def __init__(self, packages_file: Path):
        self.packages_file = packages_file

    def _run_yay(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Helper to run yay commands."""
        cmd = ["yay", "--noconfirm"] + args
        return subprocess.run(cmd, check=check, text=True, capture_output=False)

    def get_installed_packages(self) -> Set[str]:
        """Returns a set of installed packages using pacman -Qq."""
        try:
            result = subprocess.run(
                ["pacman", "-Qq"], 
                check=True, 
                text=True, 
                capture_output=True
            )
            return set(result.stdout.strip().splitlines())
        except subprocess.CalledProcessError:
            return set()

    def get_desired_packages(self) -> Set[str]:
        """Reads the packages file and returns a set of desired packages."""
        if not self.packages_file.exists():
            return set()
        
        packages = set()
        with open(self.packages_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    packages.add(line)
        return packages

    def install(self, packages: List[str]):
        """Installs a list of packages."""
        if not packages:
            return
        print(f"Installing packages: {', '.join(packages)}")
        self._run_yay(["-S"] + packages)

    def remove(self, packages: List[str]):
        """Removes a list of packages."""
        if not packages:
            return
        print(f"Removing packages: {', '.join(packages)}")
        # -Rns removes package, its configuration, and unneeded dependencies
        self._run_yay(["-Rns"] + packages)

    def sync(self):
        """Syncs installed packages with the desired packages list."""
        installed = self.get_installed_packages()
        desired = self.get_desired_packages()

        to_install = list(desired - installed)
        # We generally don't auto-remove packages not in the list to avoid 
        # accidental system breakage, but we could add a flag for strict sync later.
        
        if to_install:
            print(f"Found {len(to_install)} missing packages.")
            self.install(to_install)
        else:
            print("System is up to date with packages list.")

import typer
app = typer.Typer()
package_manager = PackageManager(Path("packages"))

@app.command()
def install(packages: List[str]):
    """Install specified packages."""
    package_manager.install(packages)

@app.command()
def remove(packages: List[str]):
    """Remove specified packages."""
    package_manager.remove(packages)

@app.command()
def sync():
    """Sync installed packages with the packages list."""
    package_manager.sync()

@app.command("list")
def list_packages():
    """List installed packages."""
    for pkg in sorted(package_manager.get_installed_packages()):
        print(pkg)
