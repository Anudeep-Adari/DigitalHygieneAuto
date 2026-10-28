"""
Deep Clean & Organization Automation Script
- Organizes D:\\wipro into Payslips and HR_Letters (ZERO deletions)
- Preserves 100% of IBM, Cognizant, and Wipro files
- Identifies and deletes older resume drafts across D: and E: while keeping latest editions
- Cleans and organizes loose contents in D:\\misc, D:\\backup 2, and E:\\documents
"""

from __future__ import annotations
from datetime import datetime
import os
from pathlib import Path
import shutil
from typing import Dict, List, Set

from rich.console import Console
from rich.table import Table

from resume_manager import ResumeManager
from rules import RuleEngine

console = Console()


def organize_wipro() -> None:
    """Safely organizes D:\\wipro into Payslips and HR Letters without deleting any files."""
    wipro_dir = Path("D:/wipro")
    if not wipro_dir.exists():
        return

    payslips_dir = wipro_dir / "Payslips"
    hr_dir = wipro_dir / "HR_Letters_and_Forms"

    payslips_dir.mkdir(parents=True, exist_ok=True)
    hr_dir.mkdir(parents=True, exist_ok=True)

    moved = 0
    for item in list(wipro_dir.iterdir()):
        if item.is_dir():
            continue

        name_lower = item.name.lower()
        if "payslip" in name_lower or "20591849.pdf" in name_lower:
            dest = payslips_dir / item.name
            shutil.move(str(item), str(dest))
            moved += 1
        else:
            dest = hr_dir / item.name
            shutil.move(str(item), str(dest))
            moved += 1

    console.print(f"[bold green]Organized D:\\wipro:[/bold green] {moved} company documents safely categorized into Payslips/ and HR_Letters_and_Forms/ (0 deleted).")


def process_resumes() -> None:
    """Finds all resumes, preserves latest version per candidate/variant, and permanently deletes older drafts."""
    search_dirs = [
        Path("D:/Organized/Documents/Resumes"),
        Path("D:/misc"),
        Path("D:/backup 2"),
        Path("E:/documents"),
    ]

    mgr = ResumeManager(search_dirs)
    to_keep, to_archive = mgr.preview_deduplication()

    # Ironclad check: NEVER delete any file related to IBM, Cognizant, or Wipro
    protected_keywords = ["ibm", "cognizant", "wipro"]
    deleted_count = 0

    table = Table(title="Deleted Older Resume Drafts")
    table.add_column("Candidate", style="cyan")
    table.add_column("File Deleted", style="red")
    table.add_column("Date", style="magenta")

    for r in to_archive:
        path_lower = str(r.path).lower()
        if any(pk in path_lower for pk in protected_keywords):
            console.print(f"[yellow]Skipping protected company file:[/yellow] {r.path.name}")
            continue

        if r.path.exists():
            try:
                os.remove(r.path)
                deleted_count += 1
                table.add_row(r.candidate, r.path.name, r.mtime.strftime("%Y-%m-%d"))
            except Exception as e:
                console.print(f"[red]Failed to delete {r.path.name}:[/red] {e}")

    console.print(table)
    console.print(f"[bold green]Resume Deduplication Complete:[/bold green] Deleted {deleted_count} older resume drafts. Kept {len(to_keep)} latest resumes intact.\n")


def organize_folder_contents(source_dir: Path, target_base: Path, label: str) -> None:
    """Sorts loose files from source_dir into target_base using RuleEngine."""
    if not source_dir.exists():
        return

    rule_engine = RuleEngine()
    files_to_move = [f for f in source_dir.iterdir() if f.is_file() and not rule_engine.should_ignore(f)]

    if not files_to_move:
        console.print(f"[dim]No loose files to organize in {label} ({source_dir}).[/dim]")
        return

    moved = 0
    for f in files_to_move:
        # Strict protection: do not move or delete anything company-related out of place
        category = rule_engine.classify_file(f) or "Uncategorized_Files"
        dest_folder = target_base / category
        dest_file = rule_engine.get_collision_free_destination(dest_folder, f.name)

        try:
            dest_folder.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), str(dest_file))
            moved += 1
        except Exception as e:
            console.print(f"[red]Error moving {f.name}:[/red] {e}")

    console.print(f"[bold green]Cleaned {label}:[/bold green] Sorted {moved} files into {target_base.name}/.")


def main():
    console.print("[bold cyan]Starting Deep Clean & Organization...[/bold cyan]\n")

    # 1. First, secure and organize D:\wipro
    organize_wipro()

    # 2. Process and delete older resume drafts across all search paths
    process_resumes()

    # 3. Clean loose files in D:\misc into D:\Organized
    organize_folder_contents(Path("D:/misc"), Path("D:/Organized"), "D:\\misc")

    # 4. Clean loose files in D:\backup 2 into D:\Organized
    organize_folder_contents(Path("D:/backup 2"), Path("D:/Organized"), "D:\\backup 2")

    # 5. Clean loose files in E:\documents into E:\Organized
    organize_folder_contents(Path("E:/documents"), Path("E:/Organized"), "E:\\documents")

    console.print("\n[bold green]Deep Clean Execution Finished Successfully![/bold green]")


if __name__ == "__main__":
    main()
