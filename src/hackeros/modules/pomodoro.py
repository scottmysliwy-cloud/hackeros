import typer
import time
import os
import signal
from datetime import datetime, timedelta
from hackeros.utils import notify, get_cache_dir

app = typer.Typer(help="Pomodoro Timer")

TIMER_FILE = get_cache_dir() / "pomodoro_timer"
PID_FILE = get_cache_dir() / "pomodoro_pid"

@app.command()
def start(minutes: int = typer.Argument(25, help="Duration in minutes")):
    """Start a Pomodoro timer."""
    seconds = minutes * 60
    end_time = int(time.time()) + seconds
    
    TIMER_FILE.write_text(str(end_time))
    
    # Kill existing timer
    stop(notify_user=False)
    
    # Fork a background process to handle the notification
    pid = os.fork()
    if pid == 0:
        # Child process
        try:
            time.sleep(seconds)
            notify("Pomodoro Complete", "Time to take a break!", urgency="critical")
        finally:
            if TIMER_FILE.exists():
                TIMER_FILE.unlink()
            if PID_FILE.exists():
                PID_FILE.unlink()
            os._exit(0)
    else:
        # Parent process
        PID_FILE.write_text(str(pid))
        notify("Pomodoro Started", f"{minutes} minutes on the clock.")

@app.command()
def stop(notify_user: bool = True):
    """Stop the current timer."""
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text())
            os.kill(pid, signal.SIGTERM)
        except (ValueError, ProcessLookupError):
            pass
        finally:
            PID_FILE.unlink()
    
    if TIMER_FILE.exists():
        TIMER_FILE.unlink()
    
    if notify_user:
        notify("Pomodoro Stopped", "Timer cancelled.")

@app.command()
def status():
    """Show timer status."""
    if not TIMER_FILE.exists():
        print("No active timer.")
        return

    try:
        end_time = int(TIMER_FILE.read_text())
        remaining = end_time - int(time.time())
        
        if remaining > 0:
            mins = remaining // 60
            secs = remaining % 60
            print(f"Time remaining: {mins}m {secs}s")
        else:
            print("Timer finished.")
    except ValueError:
        print("Error reading timer state.")
