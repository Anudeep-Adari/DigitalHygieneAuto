"""
Real-time Background Watcher for continuous folder hygiene (e.g. Downloads folder).
Listens for filesystem events and sorts incoming files as soon as downloads finish.
"""

from __future__ import annotations
from pathlib import Path
import time
from typing import Optional

from rich.console import Console
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from organizer import Organizer
from rules import RuleEngine

console = Console()


class DownloadStabilizer:
    """Waits for a file to finish downloading/writing before attempting to move it."""

    @staticmethod
    def wait_until_ready(file_path: Path, max_wait_seconds: int = 30) -> bool:
        """
        Polls file size until it remains unchanged for 2 consecutive seconds
        and can be opened in append mode (indicating no active write lock).
        """
        start_time = time.time()
        last_size = -1

        while time.time() - start_time < max_wait_seconds:
            if not file_path.exists():
                return False

            try:
                current_size = file_path.stat().st_size
                # Test opening file exclusively to check for browser locks
                with open(file_path, "a+b"):
                    pass

                if current_size == last_size and current_size > 0:
                    # Size is stable and file is not locked
                    return True

                last_size = current_size
            except (PermissionError, OSError):
                # File is currently locked by browser/downloader
                pass

            time.sleep(1.5)

        return False


class LiveFolderHandler(FileSystemEventHandler):
    def __init__(self, target_dir: Path, organizer: Organizer, stabilizer_seconds: int = 4):
        super().__init__()
        self.target_dir = target_dir.resolve()
        self.organizer = organizer
        self.stabilizer_seconds = stabilizer_seconds

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        self._process(Path(event.src_path))

    def on_moved(self, event: FileSystemEvent) -> None:
        # Many browsers download to .crdownload or .tmp and then rename when done
        if event.is_directory:
            return
        dest_path = getattr(event, "dest_path", None)
        if dest_path:
            self._process(Path(dest_path))

    def _process(self, file_path: Path) -> None:
        # Ignore files inside subdirectories
        if file_path.parent.resolve() != self.target_dir:
            return

        if self.organizer.rules.should_ignore(file_path):
            return

        # Give small breathing room for download renaming
        time.sleep(1)

        # Wait until download write finishes
        if not DownloadStabilizer.wait_until_ready(file_path, max_wait_seconds=30):
            return

        category = self.organizer.rules.classify_file(file_path)
        if not category:
            return

        dest_folder = self.target_dir / category
        dest_file = self.organizer.rules.get_collision_free_destination(dest_folder, file_path.name)

        try:
            dest_folder.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.move(str(file_path), str(dest_file))
            self.organizer.history_mgr.record_batch(
                [{"src": str(file_path), "dest": str(dest_file), "category": category}],
                str(self.target_dir),
            )
            console.print(f"[bold green]Auto-filed:[/bold green] [cyan]{file_path.name}[/cyan] -> [yellow]{category}[/yellow]")
        except Exception as e:
            console.print(f"[bold red]Failed to auto-file {file_path.name}:[/bold red] {e}")


def start_watcher(target_path: Path, rule_engine: Optional[RuleEngine] = None) -> None:
    """Starts the real-time background watcher loop."""
    organizer = Organizer(rule_engine=rule_engine)
    handler = LiveFolderHandler(target_path, organizer)

    observer = Observer()
    observer.schedule(handler, str(target_path), recursive=False)
    observer.start()

    console.print(f"\n[bold green]DigitalHygiene Watcher Active[/bold green]")
    console.print(f"Monitoring: [bold cyan]{target_path}[/bold cyan]")
    console.print("[dim]Press Ctrl+C to stop watching.[/dim]\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping watcher...[/yellow]")
        observer.stop()
    observer.join()
    console.print("[green]Watcher stopped cleanly.[/green]")
