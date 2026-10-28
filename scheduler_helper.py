"""
Windows Task Scheduler Helper
Configures automated daily or hourly background execution using Windows native schtasks.
"""

from __future__ import annotations
import os
from pathlib import Path
import subprocess
import sys
from rich.console import Console

console = Console()


def generate_task_command(interval_hours: int = 4) -> str:
    """Generates the PowerShell command to create a Scheduled Task in Windows."""
    python_exe = sys.executable
    main_script = (Path(__file__).parent / "main.py").resolve()

    task_name = "DigitalHygieneAutoSweep"
    # Action runs main.py organize --silent
    cmd = (
        f'schtasks /create /tn "{task_name}" '
        f'/tr "\"{python_exe}\" \"{main_script}\" organize --silent" '
        f'/sc HOURLY /mo {interval_hours} /f'
    )
    return cmd


def install_scheduled_task(interval_hours: int = 4) -> bool:
    """Installs the Windows Scheduled Task directly."""
    cmd = generate_task_command(interval_hours)
    console.print(f"[cyan]Registering Windows Scheduled Task:[/cyan] [dim]{cmd}[/dim]")

    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            console.print(f"[bold green]Scheduled task registered successfully![/bold green]")
            console.print(f"DigitalHygiene will automatically sweep your target folders every {interval_hours} hours.")
            return True
        else:
            console.print(f"[yellow]Task registration output:[/yellow] {res.stderr.strip() or res.stdout.strip()}")
            console.print("[dim]Note: If permissions were denied, run terminal as Administrator or execute the generated command manually.[/dim]")
            return False
    except Exception as e:
        console.print(f"[bold red]Error running schtasks:[/bold red] {e}")
        return False


def remove_scheduled_task() -> bool:
    """Removes the Windows Scheduled Task."""
    task_name = "DigitalHygieneAutoSweep"
    cmd = f'schtasks /delete /tn "{task_name}" /f'
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            console.print(f"[bold green]Task '{task_name}' removed from Windows Task Scheduler.[/bold green]")
            return True
        else:
            console.print(f"[yellow]Task removal output:[/yellow] {res.stderr.strip() or res.stdout.strip()}")
            return False
    except Exception as e:
        console.print(f"[bold red]Error removing task:[/bold red] {e}")
        return False
