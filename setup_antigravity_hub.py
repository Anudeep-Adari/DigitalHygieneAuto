"""
Consolidates all genuine Antigravity projects into E:\\Antigravity_Projects\\:
- Job Automation (infra-job-automate-source, job automation)
- Job Intelligence (job-intelligence-dashboard from D:\\New folder (2))
- Job Nexus (from E:\\jobnexus)
- Current Project (DigitalHygieneAuto)
- ATS Platform (from E:\\ats-platform)
- PulseGuard (from E:\\PulseGuard)
- Finance Dashboard (from E:\\finance-dashboard)
"""

from __future__ import annotations
from pathlib import Path
import shutil
import sys

from rich.console import Console

console = Console()

HUB = Path("E:/Antigravity_Projects")
HUB.mkdir(parents=True, exist_ok=True)


def move_or_sync(src: Path, dest_name: str) -> None:
    if not src.exists():
        console.print(f"[dim]Source does not exist: {src}[/dim]")
        return

    dest = HUB / dest_name
    console.print(f"[cyan]Consolidating:[/cyan] {src} -> [green]{dest}[/green]")

    try:
        if dest.exists():
            console.print(f"[yellow]Destination already exists: {dest}. Merging/syncing...[/yellow]")
            shutil.copytree(str(src), str(dest), dirs_exist_ok=True)
            if src != dest:
                # remove source if it is not in HUB
                if src.parent != HUB:
                    shutil.rmtree(str(src), ignore_errors=True)
        else:
            shutil.move(str(src), str(dest))
        console.print(f"[bold green]Successfully consolidated:[/bold green] {dest_name}")
    except Exception as e:
        console.print(f"[red]Error moving {src.name}:[/red] {e}")


def main():
    console.print("[bold cyan]Building Antigravity Master Projects Hub in E:\\Antigravity_Projects...[/bold cyan]\n")

    # 1. Job Nexus
    move_or_sync(Path("E:/jobnexus"), "JobNexus")

    # 2. Job Intelligence (D:\New folder (2))
    move_or_sync(Path("D:/New folder (2)"), "Job-Intelligence-Analytics")

    # 3. Job Automation
    move_or_sync(Path("E:/infra-job-automate-source"), "Job-Automation-Infra")
    if Path("E:/job-auto-scrape-main").exists():
        move_or_sync(Path("E:/job-auto-scrape-main"), "Job-Auto-Scrape")
    if Path("C:/Users/AAnu1/Downloads/job automation").exists():
        move_or_sync(Path("C:/Users/AAnu1/Downloads/job automation"), "Job-Automation-Scripts")

    # 4. ATS Platform
    move_or_sync(Path("E:/ats-platform"), "ATS-Platform")

    # 5. PulseGuard
    move_or_sync(Path("E:/PulseGuard"), "PulseGuard")
    if Path("E:/PulseGuardApp").exists():
        move_or_sync(Path("E:/PulseGuardApp"), "PulseGuardApp")

    # 6. Finance Dashboard
    move_or_sync(Path("E:/finance-dashboard"), "Finance-Dashboard")

    # 7. Current Project: DigitalHygieneAuto
    cur_proj = Path("D:/DigitalHygieneAuto")
    dest_cur = HUB / "DigitalHygieneAuto"
    try:
        shutil.copytree(str(cur_proj), str(dest_cur), dirs_exist_ok=True)
        console.print(f"[bold green]Mirrored Current Project:[/bold green] {dest_cur}")
    except Exception as e:
        console.print(f"[yellow]Note mirroring current project:[/yellow] {e}")

    console.print("\n[bold green]Antigravity Projects Hub setup complete![/bold green]")


if __name__ == "__main__":
    main()
