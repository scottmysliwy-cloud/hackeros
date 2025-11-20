import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List
from dataclasses import dataclass
from hackeros.utils import run_command, notify, command_exists, console, ensure_line_in_file, logger
from hackeros.constants import (
    PACMAN_CONF, REQUIRED_REPOS, OPTIONAL_REPOS,
    BASE_DEVEL, NVIDIA_PACKAGES, INTEL_MEDIA_DRIVER, INTEL_VA_DRIVER, APPLE_T2_PACKAGES,
    NETWORK_SERVICES, PRINTER_SERVICES, NVIDIA_ENV_VARS,
    APPLE_T2_VENDOR, APPLE_T2_DEVICES
)

# --- Plans ---

@dataclass
class RepoPlan:
    pass

@dataclass
class YayPlan:
    pass

@dataclass
class DotfilesPlan:
    source: Path
    target: Path

@dataclass
class HardwarePlan:
    pass

# --- Executors ---

class RepoExecutor:
    @staticmethod
    def apply(plan: RepoPlan):
        logger.info("Checking repositories...")
        if not PACMAN_CONF.exists():
            logger.warning(f"{PACMAN_CONF} not found.")
            return

        with open(PACMAN_CONF, "r") as f:
            content = f.read()

        for repo in REQUIRED_REPOS:
            if f"[{repo}]" not in content:
                 # Logic to check if enabled is complex, assuming standard config for now
                 pass

        for repo in OPTIONAL_REPOS:
            if f"[{repo}]" not in content or f"#[{repo}]" in content:
                logger.warning(f"[{repo}] repository might not be enabled. Some packages may fail.")

class YayExecutor:
    @staticmethod
    def apply(plan: YayPlan):
        if command_exists("yay"):
            logger.debug("yay is already installed.")
            return

        logger.info("yay not found. Bootstrapping...")
        notify("Bootstrap", "Installing yay...")

        with console.status("[bold green]Installing git and base-devel..."):
            subprocess.run(["sudo", "pacman", "-S", "--needed", "--noconfirm"] + BASE_DEVEL, check=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            logger.info(f"Cloning yay into {tmpdir}...")
            subprocess.run(["git", "clone", "https://aur.archlinux.org/yay.git", tmpdir], check=True)
            
            cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                with console.status("[bold green]Building yay..."):
                    subprocess.run(["makepkg", "-si", "--noconfirm"], check=True)
                logger.info("yay installed successfully.")
                notify("Bootstrap", "yay installed successfully.")
            except subprocess.CalledProcessError:
                logger.error("Failed to build yay.")
                notify("Bootstrap Failed", "Could not build yay.", urgency="critical")
                raise Exception("Failed to build yay")
            finally:
                os.chdir(cwd)

class PackageExecutor:
    @staticmethod
    def apply(packages: List[str]):
        if not packages:
            logger.info("No packages to install.")
            return

        logger.info(f"Installing {len(packages)} packages...")
        cmd = ["yay", "-S", "--needed", "--noconfirm"] + packages
        try:
            with console.status(f"[bold green]Installing {len(packages)} packages..."):
                subprocess.run(cmd, check=True)
            notify("Installation Complete", f"Installed {len(packages)} packages.")
        except subprocess.CalledProcessError:
            notify("Installation Failed", "Check terminal for details.", urgency="critical")
            raise Exception("Package installation failed")

class DotfilesExecutor:
    @staticmethod
    def apply(plan: DotfilesPlan):
        src = plan.source
        dst = plan.target

        if not src.exists():
            logger.error(f"Missing dotfiles source: {src}")
            return
        
        dst.mkdir(parents=True, exist_ok=True)
        logger.info(f"Installing dotfiles from {src} to {dst}...")

        for item in src.iterdir():
            if item.name.startswith(".git"):
                continue

            out = dst / item.name

            # CRITICAL: Use lexists() to detect broken symlinks
            if out.lexists():
                # Check if it's already the correct link (Idempotency)
                if out.is_symlink() and out.readlink() == item:
                    continue

                # Backup existing
                ts = subprocess.run(["date", "+%s"], capture_output=True, text=True).stdout.strip()
                backup = out.with_suffix(out.suffix + f".bak.{ts}")
                logger.warning(f"Backup: {out} -> {backup}")
                out.rename(backup)

            logger.info(f"Link: {item} -> {out}")
            out.symlink_to(item)
        
        notify("Dotfiles", "Configuration files installed.")

class HardwareExecutor:
    @staticmethod
    def apply(plan: HardwarePlan):
        logger.info("Applying hardware fixes...")
        
        # 1. Services
        for service, action in NETWORK_SERVICES + PRINTER_SERVICES:
            subprocess.run(["sudo", "systemctl", action, service], check=False)
        
        # 2. GPU Detection
        lspci_out = subprocess.run(["lspci"], capture_output=True, text=True).stdout.lower()
        
        if "vga" in lspci_out and "intel" in lspci_out:
            logger.info("Detected Intel GPU.")
            pkgs = []
            if any(x in lspci_out for x in ["hd graphics", "xe", "iris"]):
                 pkgs = INTEL_MEDIA_DRIVER
            elif "gma" in lspci_out:
                 pkgs = INTEL_VA_DRIVER
            
            if pkgs:
                subprocess.run(["sudo", "pacman", "-S", "--needed", "--noconfirm"] + pkgs, check=False)

        if "nvidia" in lspci_out:
            logger.info("Detected Nvidia GPU.")
            subprocess.run(["sudo", "pacman", "-S", "--needed", "--noconfirm"] + NVIDIA_PACKAGES, check=False)
            
            # Add env vars to hyprland.conf if exists
            hypr_conf = Path.home() / ".config/hypr/hyprland.conf"
            if hypr_conf.exists():
                for env_var in NVIDIA_ENV_VARS:
                    ensure_line_in_file(hypr_conf, env_var)

        # 3. Apple T2
        if f"{APPLE_T2_VENDOR}:{APPLE_T2_DEVICES[0]}" in lspci_out or f"{APPLE_T2_VENDOR}:{APPLE_T2_DEVICES[1]}" in lspci_out:
            logger.info("Detected Apple T2 Chip.")
            subprocess.run(["yay", "-S", "--needed", "--noconfirm"] + APPLE_T2_PACKAGES, check=False)
            
            with open("/tmp/t2.conf", "w") as f: f.write("apple-bce\n")
            subprocess.run(["sudo", "cp", "/tmp/t2.conf", "/etc/modules-load.d/t2.conf"], check=False)
            
            logger.warning("T2 Chip detected. Installed packages. Please verify mkinitcpio.conf manually for apple-bce module.")
