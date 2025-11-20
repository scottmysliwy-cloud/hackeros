import typer
from datetime import datetime
from hackersos.utils import notify, run_command, get_documents_dir

app = typer.Typer(help="Quick Capture")

INBOX_FILE = get_documents_dir() / "Inbox.md"

@app.callback(invoke_without_command=True)
def capture(ctx: typer.Context):
    """Quickly capture thoughts/todos."""
    if ctx.invoked_subcommand is not None:
        return

    # Use walker dmenu to get input
    result = run_command(
        ["walker", "--dmenu", "--placeholder", "Capture thought...", "--p", "Capture"],
        check=False
    )
    
    note = result.stdout.strip()
    
    if note:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(INBOX_FILE, "a") as f:
            f.write(f"- [ ] {timestamp}: {note}\n")
        notify("Captured", "Saved to Inbox.md")
