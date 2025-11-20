import typer
from pathlib import Path
from hackersos.utils import run_command, notify, require_non_root, logger
from hackersos.constants import PACKAGES_FILE, DOTFILES_SRC, DOTFILES_DST
from hackersos.modules.install_executors import (
    RepoPlan, RepoExecutor,
    YayPlan, YayExecutor,
    PackageExecutor,
    DotfilesPlan, DotfilesExecutor,
    HardwarePlan, HardwareExecutor
)

app = typer.Typer(help="Package Installer")

@app.callback(invoke_without_command=True)
def install(
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be installed without installing"),
    file: Path = typer.Option(PACKAGES_FILE, "--file", "-f", help="Path to packages file"),
    skip_dotfiles: bool = typer.Option(False, "--skip-dotfiles", help="Skip dotfiles installation"),
    skip_hardware: bool = typer.Option(False, "--skip-hardware", help="Skip hardware fixes")
):
    """Install packages, dotfiles, and apply hardware fixes."""
    
    # 1. Safety Check
    require_non_root()

    if not file.exists():
        logger.error(f"Packages file not found at {file.absolute()}")
        raise typer.Exit(1)

    logger.info(f"Reading packages from {file}...")
    packages = []
    with open(file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                packages.append(line)

    # 2. Correct Execution Order
    # Repo -> Yay -> PACKAGES -> Dotfiles -> Hardware
    
    if dry_run:
        logger.info("Dry run enabled.")
        logger.info("Would check repositories.")
        logger.info("Would bootstrap yay.")
        if packages:
            logger.info(f"Would install {len(packages)} packages: {', '.join(packages[:5])}...")
        if not skip_dotfiles:
            logger.info("Would install dotfiles.")
        if not skip_hardware:
            logger.info("Would apply hardware fixes.")
        return

    # Execute Plans
    RepoExecutor.apply(RepoPlan())
    YayExecutor.apply(YayPlan())
    
    if packages:
        PackageExecutor.apply(packages)

    if not skip_dotfiles:
        # Use constant for default, but allow override if we were to add a flag
        # For now, just use the constant logic which is robust
        source = DOTFILES_SRC
        if not source.exists():
             # Fallback to local config if running from source
             source = Path("config")
        
        DotfilesExecutor.apply(DotfilesPlan(source, DOTFILES_DST))

    if not skip_hardware:
        HardwareExecutor.apply(HardwarePlan())
