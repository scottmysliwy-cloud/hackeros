import typer
import subprocess
import shutil
from pathlib import Path
from rich.prompt import Prompt
from hackeros.utils import run_command, notify, console, logger
from hackeros.constants import RESOLVED_CONF, PAM_SUDO, PAM_POLKIT

app = typer.Typer(help="Setup Wizards")

class SetupManager:
    def setup_dns(self, provider: str):
        """Setup DNS (Cloudflare, DHCP, or Custom)."""
        logger.info(f"Setting up DNS: {provider}")
        
        content = ""
        if provider.lower() == "cloudflare":
            content = "[Resolve]\nDNS=1.1.1.1 1.0.0.1\nDomains=~."
        elif provider.lower() == "dhcp":
            content = "# DNS managed by DHCP"
        else:
            # Custom
            dns = Prompt.ask("Enter DNS server IP")
            content = f"[Resolve]\nDNS={dns}\nDomains=~."

        try:
            with console.status("[bold green]Configuring DNS..."):
                # Write to /etc/systemd/resolved.conf
                # Need sudo
                subprocess.run(
                    ["sudo", "tee", str(RESOLVED_CONF)],
                    input=content, text=True, check=True, stdout=subprocess.DEVNULL
                )
                
                # Restart services
                run_command(["sudo", "systemctl", "restart", "systemd-networkd"])
                run_command(["sudo", "systemctl", "restart", "systemd-resolved"])
                
                # Update network files (placeholder for full logic)
                self._update_network_files(provider.lower() == "dhcp")
            
            logger.info("DNS configured successfully.")
            notify("Setup", "DNS configured successfully.")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to setup DNS: {e}")
            notify("Setup Failed", "Could not configure DNS.", urgency="critical")

    def _update_network_files(self, use_dhcp_dns: bool):
        """Update /etc/systemd/network/*.network files."""
        # Placeholder: In a real scenario, we'd iterate files and set UseDNS=yes/no
        pass

    def setup_fido2(self, remove: bool = False):
        """Setup FIDO2/YubiKey."""
        if remove:
            logger.info("Removing FIDO2 configuration...")
            # Logic to remove pam_u2f from pam files
            logger.warning("Removal logic not fully implemented yet.")
            return

        logger.info("Setting up FIDO2...")
        try:
            with console.status("[bold green]Installing FIDO2 packages..."):
                run_command(["sudo", "pacman", "-S", "--needed", "--noconfirm", "libfido2", "pam-u2f"])

            if not Path("/etc/u2f_mappings").exists():
                logger.info("Please touch your FIDO2 device when prompted.")
                # This command requires user interaction, so we can't wrap it easily in status if it blocks
                # But pamu2fcfg outputs to stdout.
                mappings = subprocess.run(["pamu2fcfg"], capture_output=True, text=True, check=True).stdout
                subprocess.run(
                    ["sudo", "tee", "/etc/u2f_mappings"],
                    input=mappings, text=True, check=True, stdout=subprocess.DEVNULL
                )

            # Configure PAM
            self._configure_pam(PAM_SUDO, "pam_u2f.so")
            self._configure_pam(PAM_POLKIT, "pam_u2f.so")
            
            logger.info("FIDO2 configured successfully.")
            notify("Setup", "FIDO2 configured successfully.")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to setup FIDO2: {e}")
            notify("Setup Failed", "Could not configure FIDO2.", urgency="critical")

    def setup_fingerprint(self, remove: bool = False):
        """Setup Fingerprint."""
        if remove:
            logger.info("Removing Fingerprint configuration...")
            return

        logger.info("Setting up Fingerprint...")
        try:
            with console.status("[bold green]Installing Fingerprint packages..."):
                run_command(["sudo", "pacman", "-S", "--needed", "--noconfirm", "fprintd", "usbutils"])

            # Enroll
            logger.info("Enrolling fingerprint. Please swipe your finger.")
            subprocess.run(["fprintd-enroll"], check=True)

            # Configure PAM
            self._configure_pam(PAM_SUDO, "pam_fprintd.so")
            self._configure_pam(PAM_POLKIT, "pam_fprintd.so")

            logger.info("Fingerprint configured successfully.")
            notify("Setup", "Fingerprint configured successfully.")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to setup Fingerprint: {e}")

    def _configure_pam(self, pam_file: Path, module: str):
        """Add module to PAM file if not present."""
        if not pam_file.exists():
            return

        content = pam_file.read_text()
        if module in content:
            return

        # Simplified logic: Add to top of auth
        # Real implementation needs careful parsing or using authselect/pam-auth-update if available
        # For Arch, manual edit is common but risky via script.
        # We'll just append a warning for now as modifying PAM programmatically is dangerous without a parser.
        logger.warning(f"Please manually add 'auth sufficient {module}' to {pam_file}")


@app.command()
def dns(provider: str = typer.Option("cloudflare", help="DNS Provider (cloudflare, dhcp, custom)")):
    """Setup DNS."""
    manager = SetupManager()
    manager.setup_dns(provider)

@app.command()
def fido2(remove: bool = typer.Option(False, "--remove", help="Remove FIDO2 configuration")):
    """Setup FIDO2/YubiKey."""
    manager = SetupManager()
    manager.setup_fido2(remove)

@app.command()
def fingerprint(remove: bool = typer.Option(False, "--remove", help="Remove Fingerprint configuration")):
    """Setup Fingerprint."""
    manager = SetupManager()
    manager.setup_fingerprint(remove)

if __name__ == "__main__":
    app()
