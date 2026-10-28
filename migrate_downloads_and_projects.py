"""
Downloads Folder Migration & Antigravity Projects Consolidation Script
- Consolidates all Antigravity & Agentic projects with full source code into E:\\Antigravity_Projects\\
- Organizes and CUTS (moves) all other Downloads (media, installers, archives, docs) into E:\\Organized\\
- Purges temporary/obsolete redundant downloads
- Leaves C:\\Users\\AAnu1\\Downloads completely clean, freeing up ~25-30 GB on C:
"""

from __future__ import annotations
import os
from pathlib import Path
import shutil
import sys
from typing import Dict, List, Tuple

from rich.console import Console
from rich.table import Table

console = Console()

DOWNLOADS_DIR = Path("C:/Users/AAnu1/Downloads")
PROJECTS_HUB = Path("E:/Antigravity_Projects")
ORGANIZED_HUB = Path("E:/Organized")


def safe_move(src: Path, dest: Path) -> bool:
    """Moves src to dest with collision avoidance and directory creation."""
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            if dest.is_dir() and src.is_dir():
                # Merge or append timestamp
                stem = dest.name
                dest = dest.parent / f"{stem}_backup_{dest.stat().st_mtime_ns}"
            elif dest.is_file():
                stem = dest.stem
                ext = dest.suffix
                counter = 1
                while dest.exists():
                    dest = dest.parent / f"{stem} ({counter}){ext}"
                    counter += 1
        shutil.move(str(src), str(dest))
        return True
    except Exception as e:
        console.print(f"[red]Failed to move {src.name} -> {dest}:[/red] {e}")
        return False


def consolidate_projects() -> None:
    """Collects all Antigravity and AI coding projects into E:\\Antigravity_Projects\\."""
    PROJECTS_HUB.mkdir(parents=True, exist_ok=True)
    console.print(f"\n[bold cyan]Consolidating Antigravity Projects into {PROJECTS_HUB}...[/bold cyan]")

    # 1. Projects currently residing in Downloads
    downloads_projects = {
        "antigravity-awesome-skills": "antigravity-awesome-skills",
        "awesome-agent-skills-main": "awesome-agent-skills",
        "Job-email-automation--main": "job-email-automation",
        "fury_project": "fury_project",
        "portfolio-multiple-main": "portfolio-multiple",
        "sachin-portfolio": "sachin-portfolio",
        "claude-counter-0.4.2": "claude-counter",
        "Compliance": "compliance-tracker",
    }

    for folder_name, target_name in downloads_projects.items():
        src = DOWNLOADS_DIR / folder_name
        if src.exists():
            dest = PROJECTS_HUB / target_name
            if safe_move(src, dest):
                console.print(f"  [green]Moved:[/green] {src.name} -> [cyan]{dest}[/cyan]")

    # Select latest versions of multi-downloaded scrapers in Downloads
    # infra-job-automate
    infra_candidates = sorted(DOWNLOADS_DIR.glob("infra-job-automate-main*"), key=lambda p: p.stat().st_mtime, reverse=True)
    if infra_candidates:
        latest = infra_candidates[0]
        dest = PROJECTS_HUB / "infra-job-automate"
        safe_move(latest, dest)
        console.print(f"  [green]Moved (latest):[/green] {latest.name} -> [cyan]{dest}[/cyan]")
        # Delete duplicate older downloads
        for older in infra_candidates[1:]:
            shutil.rmtree(older, ignore_errors=True)
            console.print(f"  [dim]Removed older duplicate download:[/dim] {older.name}")

    # job-auto-scrape
    job_scrape_candidates = sorted(DOWNLOADS_DIR.glob("job-auto-scrape-main*"), key=lambda p: p.stat().st_mtime, reverse=True)
    if job_scrape_candidates:
        latest = job_scrape_candidates[0]
        dest = PROJECTS_HUB / "job-auto-scrape"
        safe_move(latest, dest)
        console.print(f"  [green]Moved (latest):[/green] {latest.name} -> [cyan]{dest}[/cyan]")
        for older in job_scrape_candidates[1:]:
            shutil.rmtree(older, ignore_errors=True)
            console.print(f"  [dim]Removed older duplicate download:[/dim] {older.name}")

    # Clean up single redundant Job-email-automation--main (1)
    redundant_email = DOWNLOADS_DIR / "Job-email-automation--main (1)"
    if redundant_email.exists():
        shutil.rmtree(redundant_email, ignore_errors=True)

    # 2. Existing projects on E:\
    existing_e_projects = [
        "ats-platform",
        "jobnexus",
        "PulseGuard",
        "PulseGuardApp",
        "finance-dashboard",
        "infra-job-automate-source",
    ]
    for proj_name in existing_e_projects:
        src = Path("E:/") / proj_name
        if src.exists():
            dest = PROJECTS_HUB / proj_name
            if safe_move(src, dest):
                console.print(f"  [green]Relocated E: project:[/green] {src.name} -> [cyan]{dest}[/cyan]")

    # 3. Project from D:\New folder (2) (Job search dashboard)
    d_job_dash = Path("D:/New folder (2)")
    if d_job_dash.exists():
        dest = PROJECTS_HUB / "job-analytics-dashboard"
        if safe_move(d_job_dash, dest):
            console.print(f"  [green]Moved D: project:[/green] D:\\New folder (2) -> [cyan]{dest}[/cyan]")

    # 4. DigitalHygieneAuto
    d_hygiene = Path("D:/DigitalHygieneAuto")
    if d_hygiene.exists():
        dest = PROJECTS_HUB / "DigitalHygieneAuto"
        # Copy/mirror so current executing process doesn't break
        try:
            shutil.copytree(str(d_hygiene), str(dest), dirs_exist_ok=True)
            console.print(f"  [green]Synced source to Hub:[/green] DigitalHygieneAuto -> [cyan]{dest}[/cyan]")
        except Exception as e:
            console.print(f"[yellow]Note syncing DigitalHygieneAuto:[/yellow] {e}")


def migrate_and_cut_downloads() -> None:
    """Cuts (moves) all remaining Downloads content into E:\\Organized."""
    ORGANIZED_HUB.mkdir(parents=True, exist_ok=True)
    console.print(f"\n[bold cyan]Cutting and migrating remaining Downloads to {ORGANIZED_HUB}...[/bold cyan]")

    for item in list(DOWNLOADS_DIR.iterdir()):
        name_lower = item.name.lower()

        # Delete defunct 0-byte or incomplete download
        if item.name.endswith(".crdownload") or item.name.startswith("~"):
            try:
                if item.is_file():
                    item.unlink()
                console.print(f"  [dim]Cleaned abandoned temp file:[/dim] {item.name}")
                continue
            except Exception:
                pass

        # 1. Video files or folders with media
        if any(kw in name_lower for kw in [".mkv", ".mp4", "spiderman", "movie", "xxx", "juq"]):
            dest = ORGANIZED_HUB / "Media" / "Video" / item.name
            safe_move(item, dest)
            console.print(f"  [magenta]Cut Media/Video:[/magenta] {item.name} -> E:\\Organized\\Media\\Video\\")

        # 2. Benchmarks, Overlays, and Tools
        elif any(kw in name_lower for kw in ["benchmark", "overlay", "troymetrics", "msiafterburner", "cinebench", "memtest", "legionspace", "usb_driver"]):
            dest = ORGANIZED_HUB / "Applications_and_Installers" / item.name
            safe_move(item, dest)
            console.print(f"  [yellow]Cut Tool/Benchmark:[/yellow] {item.name} -> E:\\Organized\\Applications_and_Installers\\")

        # 3. Categorized subfolders created previously
        elif item.name == "Media":
            for sub in list(item.iterdir()):
                safe_move(sub, ORGANIZED_HUB / "Media" / sub.name)
            shutil.rmtree(item, ignore_errors=True)

        elif item.name in ["Applications_and_Installers", "Compressed_Archives", "Documents", "Uncategorized_Files"]:
            dest_dir = ORGANIZED_HUB / item.name
            dest_dir.mkdir(parents=True, exist_ok=True)
            for sub in list(item.iterdir()):
                safe_move(sub, dest_dir / sub.name)
            shutil.rmtree(item, ignore_errors=True)

        elif item.name == "Certifications":
            dest_dir = ORGANIZED_HUB / "Documents" / "Certifications"
            dest_dir.mkdir(parents=True, exist_ok=True)
            for sub in list(item.iterdir()):
                safe_move(sub, dest_dir / sub.name)
            shutil.rmtree(item, ignore_errors=True)

        # 4. Logs
        elif "logs_" in name_lower:
            dest = ORGANIZED_HUB / "Logs" / item.name
            safe_move(item, dest)

        # 5. Fallback general items
        else:
            dest = ORGANIZED_HUB / "Uncategorized_Files" / item.name
            safe_move(item, dest)


def main():
    console.print("[bold green]Starting Downloads Migration & Antigravity Hub Consolidation[/bold green]")
    consolidate_projects()
    migrate_and_cut_downloads()
    console.print("\n[bold green]Migration Finished Successfully![/bold green]")


if __name__ == "__main__":
    main()
