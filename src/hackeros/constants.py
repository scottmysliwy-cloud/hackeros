from pathlib import Path

# Paths
PACMAN_CONF = Path("/etc/pacman.conf")
PROJECT_ROOT = Path(__file__).parents[2] # src/hackeros/constants.py -> src/hackeros -> src -> root
PACKAGES_FILE = PROJECT_ROOT / "packages"
DOTFILES_SRC = PROJECT_ROOT / "config"
DOTFILES_DST = Path.home() / ".config"

# Repositories
REQUIRED_REPOS = ["core", "extra"]
OPTIONAL_REPOS = ["multilib"]

# Hardware IDs
APPLE_T2_VENDOR = "106b"
APPLE_T2_DEVICES = ["1801", "1802"]

# Packages
BASE_DEVEL = ["git", "base-devel"]
NVIDIA_PACKAGES = [
    "nvidia-dkms", 
    "nvidia-utils", 
    "lib32-nvidia-utils", 
    "egl-wayland", 
    "qt5-wayland", 
    "qt6-wayland"
]
INTEL_MEDIA_DRIVER = ["intel-media-driver"]
INTEL_VA_DRIVER = ["libva-intel-driver"]
APPLE_T2_PACKAGES = [
    "linux-t2", 
    "linux-t2-headers", 
    "apple-t2-audio-config", 
    "apple-bcm-firmware", 
    "t2fanrd", 
    "tiny-dfr"
]

# Services
NETWORK_SERVICES = [
    ("iwd.service", "enable"),
    ("systemd-networkd-wait-online.service", "disable"),
    ("systemd-networkd-wait-online.service", "mask"),
    ("bluetooth.service", "enable"),
]

PRINTER_SERVICES = [
    ("cups.service", "enable"),
    ("avahi-daemon.service", "enable"),
    ("cups-browsed.service", "enable"),
]

# Environment Variables
NVIDIA_ENV_VARS = [
    "env = NVD_BACKEND,direct",
    "env = LIBVA_DRIVER_NAME,nvidia",
    "env = __GLX_VENDOR_LIBRARY_NAME,nvidia",
]

# Theme
THEME_DIR = PROJECT_ROOT / "themes"
VSCODE_SETTINGS = Path.home() / ".config/Code/User/settings.json"
ALACRITTY_CONFIG = Path.home() / ".config/alacritty/alacritty.toml"
OBSIDIAN_VAULTS_FILE = Path.home() / ".config/obsidian/vaults.json"

# Setup
RESOLVED_CONF = Path("/etc/systemd/resolved.conf")
PAM_SUDO = Path("/etc/pam.d/sudo")
PAM_POLKIT = Path("/etc/pam.d/polkit-1")
