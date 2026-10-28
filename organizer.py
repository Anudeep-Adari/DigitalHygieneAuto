"""
Core File Organizer Engine with Safe Transactions and Rollback/Undo support.
Supports Drive-Root sweeps and folder-level organization.
"""

from __future__ import annotations
from datetime import datetime
import json
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional, Tuple
import uuid

from rich.console import Console
from rich.table import Table

from rules import RuleEngine

console = Console()


class HistoryManager:
    """Manages transactional history for 100% reliable rollbacks/undo."""

    def __init__(self, history_file: Optional[Path] = None):
        self.history_file = history_file or (Path(__file__).parent / ".history.json")
        self.history: List[Dict[str, Any]] = self._load()

    def _load(self) -> List[Dict[str, Any]]:
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save(self) -> None:
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            console.print(f"[bold red]Failed to save history:[/bold red] {e}")

    def record_batch(self, moves: List[Dict[str, str]], base_dir: str) -> str:
        batch_id = str(uuid.uuid4())[:8]
        record = {
            "batch_id": batch_id,
            "timestamp": datetime.now().isoformat(),
            "base_dir": base_dir,
            "moves": moves,
        }
        self.history.append(record)
        self.save()
        return batch_id

    def pop_latest_batch(self) -> Optional[Dict[str, Any]]:
        if not self.history:
            return None
        batch = self.history.pop()
        self.save()
        return batch


class Organizer:
    """Executes file categorization, moving, conflict avoidance, and undo."""

    def __init__(self, rule_engine: Optional[RuleEngine] = None):
        self.rules = rule_engine or RuleEngine()
        self.history_mgr = HistoryManager()

    def organize_directory(
        self,
        target_dir: Path,
        dry_run: bool = False,
        interactive: bool = False,
        label: Optional[str] = None,
        use_organized_subfolder: bool = True,
    ) -> List[Tuple[Path, Path, str]]:
        """
        Organizes loose files inside target_dir into structured category subfolders.
        For drive roots (e.g. D:\, E:\), places them in <drive>:\Organized\<category>
        so the drive root stays completely clean.
        """
        target_dir = Path(target_dir).resolve()
        if not target_dir.exists() or not target_dir.is_dir():
            console.print(f"[bold red]Error:[/bold red] Target path {target_dir} is not a valid directory.")
            return []

        # Determine destination base folder
        is_drive_root = (len(target_dir.parts) == 1) or (target_dir.parent == target_dir)
        if is_drive_root and use_organized_subfolder:
            dest_base = target_dir / "Organized"
        else:
            dest_base = target_dir

        candidates: List[Path] = []
        try:
            for item in target_dir.iterdir():
                # SAFETY: Strictly ignore directories! Never move project or system folders
                if item.is_dir():
                    continue
                if self.rules.should_ignore(item):
                    continue
                candidates.append(item)
        except PermissionError as e:
            console.print(f"[yellow]Skipping {target_dir}: Permission denied ({e})[/yellow]")
            return []

        display_name = label or target_dir.name or str(target_dir)

        if not candidates:
            console.print(f"[dim]No loose files found in {display_name} ({target_dir}).[/dim]")
            return []

        planned_moves: List[Tuple[Path, Path, str]] = []

        for file_path in candidates:
            category = self.rules.classify_file(file_path)
            if not category:
                continue

            dest_folder = dest_base / category
            dest_file = self.rules.get_collision_free_destination(dest_folder, file_path.name)
            planned_moves.append((file_path, dest_file, category))

        if not planned_moves:
            console.print(f"[yellow]No files matched organization rules in {display_name}.[/yellow]")
            return []

        # Display preview table
        table = Table(title=f"{display_name} ({'DRY RUN - No Files Moved' if dry_run else 'LIVE RUN'})")
        table.add_column("File Name", style="cyan", max_width=45, no_wrap=True)
        table.add_column("Destination", style="green", max_width=50)
        table.add_column("Size", style="magenta", justify="right")

        total_bytes = 0
        for src, dest, cat in planned_moves:
            try:
                st_size = src.stat().st_size
            except Exception:
                st_size = 0
            size_kb = st_size / 1024
            total_bytes += st_size
            size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
            table.add_row(src.name, f"{dest.relative_to(target_dir)}", size_str)

        console.print(table)
        console.print(f"[dim]Total: {len(planned_moves)} files ({total_bytes / (1024*1024):.2f} MB)[/dim]\n")

        if dry_run:
            return planned_moves

        if interactive:
            confirm = input(f"Proceed with moving {len(planned_moves)} files in {display_name}? [y/N]: ").strip().lower()
            if confirm != "y":
                console.print(f"[yellow]Skipped {display_name}.[/yellow]")
                return []

        # Execute live moves
        recorded_moves = []
        success_count = 0

        for src, dest, cat in planned_moves:
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dest))
                recorded_moves.append({"src": str(src), "dest": str(dest), "category": cat})
                success_count += 1
            except Exception as e:
                console.print(f"[bold red]Failed to move {src.name}:[/bold red] {e}")

        if recorded_moves:
            batch_id = self.history_mgr.record_batch(recorded_moves, str(target_dir))
            console.print(f"[bold green]Organized {success_count} files in {display_name}![/bold green] (Batch: [cyan]{batch_id}[/cyan])")

        return planned_moves

    def undo_last_batch(self) -> bool:
        """Rolls back the most recent move batch, returning files to original locations."""
        batch = self.history_mgr.pop_latest_batch()
        if not batch:
            console.print("[yellow]No undo history found.[/yellow]")
            return False

        moves = batch.get("moves", [])
        batch_id = batch.get("batch_id", "unknown")
        timestamp = batch.get("timestamp", "unknown")

        console.print(f"[bold cyan]Rolling back Batch {batch_id}[/bold cyan] ({timestamp})...")

        restored = 0
        for item in moves:
            src_original = Path(item["src"])
            current_dest = Path(item["dest"])

            if current_dest.exists():
                try:
                    src_original.parent.mkdir(parents=True, exist_ok=True)
                    final_src = self.rules.get_collision_free_destination(src_original.parent, src_original.name)
                    shutil.move(str(current_dest), str(final_src))
                    restored += 1
                except Exception as e:
                    console.print(f"[bold red]Failed to restore {current_dest.name}:[/bold red] {e}")

        console.print(f"[bold green]Undo complete.[/bold green] Restored {restored}/{len(moves)} files.")
        return True
