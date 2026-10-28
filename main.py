"""
DigitalHygieneAuto - Autonomous Daily File & Multi-Drive Organizer
Main CLI Entry Point
"""

from __future__ import annotations
import argparse
from pathlib import Path
import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from organizer import HistoryManager, Organizer
from rules import RuleEngine
from scheduler_helper import install_scheduled_task, remove_scheduled_task
from watcher import start_watcher

console = Console()


def print_banner() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]DigitalHygieneAuto[/bold cyan] [dim]v1.1.0[/dim]\n"
            "[green]Multi-Drive Autonomous File & Download Hygiene for Windows[/green]",
            border_style="cyan",
        )
    )


def cmd_organize(args: argparse.Namespace) -> None:
    rule_engine = RuleEngine()
    organizer = Organizer(rule_engine=rule_engine)

    # Determine targets
    raw_targets = rule_engine.config.get("targets", [])
    if args.target:
        targets_to_run = [{"path": args.target, "scope": "shallow", "label": f"Custom: {args.target}"}]
    else:
        targets_to_run = []
        for t in raw_targets:
            if isinstance(t, dict):
                targets_to_run.append(t)
            elif isinstance(t, str):
                targets_to_run.append({"path": t, "scope": "shallow", "label": t})

    # Dry run safety: default to dry-run unless --run flag is passed
    is_dry_run = args.dry_run
    if not args.dry_run and not args.run:
        is_dry_run = True

    total_planned = 0
    for target_spec in targets_to_run:
        target_path = Path(target_spec["path"])
        label = target_spec.get("label", str(target_path))

        if not target_path.exists():
            console.print(f"[yellow]Target path not accessible: {target_path}[/yellow]")
            continue

        moves = organizer.organize_directory(
            target_dir=target_path,
            dry_run=is_dry_run,
            interactive=args.interactive,
            label=label,
        )
        total_planned += len(moves)

    if is_dry_run and total_planned > 0:
        console.print(
            "\n[bold yellow]Multi-Drive Dry-Run Complete.[/bold yellow] "
            "To execute file moves across these drives, run:\n"
            "  [bold green]python main.py organize --run[/bold green]\n"
        )


def cmd_undo(args: argparse.Namespace) -> None:
    organizer = Organizer()
    organizer.undo_last_batch()


def cmd_watch(args: argparse.Namespace) -> None:
    rule_engine = RuleEngine()
    target = Path(args.target) if args.target else Path(rule_engine.config.get("targets", [])[0]["path"])
    if not target.exists():
        console.print(f"[bold red]Target folder does not exist: {target}[/bold red]")
        sys.exit(1)
    start_watcher(target, rule_engine=rule_engine)


def cmd_status(args: argparse.Namespace) -> None:
    rule_engine = RuleEngine()
    history = HistoryManager().history

    table = Table(title="DigitalHygiene Configuration & Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    targets = rule_engine.config.get("targets", [])
    target_strs = []
    for t in targets:
        if isinstance(t, dict):
            target_strs.append(f"{t.get('label', t['path'])} ({t['path']})")
        else:
            target_strs.append(str(t))

    table.add_row("Monitored Locations", "\n".join(target_strs))
    table.add_row("Active Categories", f"{len(rule_engine.config.get('categories', []))} rules defined")
    table.add_row("Protected Locations", "\n".join(rule_engine.config.get("protected_paths", [])[:5]) + "\n...")
    table.add_row("Undo Batches Stored", str(len(history)))

    if history:
        latest = history[-1]
        table.add_row(
            "Latest Batch",
            f"ID: {latest.get('batch_id')} | {latest.get('timestamp')} ({len(latest.get('moves', []))} files moved)",
        )

    console.print(table)


def cmd_setup_task(args: argparse.Namespace) -> None:
    install_scheduled_task(interval_hours=args.interval)


def cmd_remove_task(args: argparse.Namespace) -> None:
    remove_scheduled_task()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="DigitalHygieneAuto - Autonomous File & Multi-Drive Organizer",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # organize command
    p_org = subparsers.add_parser("organize", help="Scan and organize target folders/drives")
    p_org.add_argument("--target", type=str, help="Specific target path (e.g., D:\\ or Downloads)")
    p_org.add_argument("--dry-run", action="store_true", help="Preview planned moves without moving files (default)")
    p_org.add_argument("--run", action="store_true", help="Execute file moves immediately")
    p_org.add_argument("-i", "--interactive", action="store_true", help="Ask confirmation before each drive")
    p_org.add_argument("--silent", action="store_true", help="Minimal console output for automated background jobs")

    # undo command
    subparsers.add_parser("undo", help="Roll back the most recent file organization batch")

    # watch command
    p_watch = subparsers.add_parser("watch", help="Start real-time background watcher on Downloads")
    p_watch.add_argument("--target", type=str, help="Folder to watch (default: Downloads)")

    # status command
    subparsers.add_parser("status", help="View current configuration and organization history")

    # task scheduler setup
    p_setup = subparsers.add_parser("setup-task", help="Register Windows Scheduled Task for hands-free maintenance")
    p_setup.add_argument("--interval", type=int, default=4, help="Interval in hours (default: 4)")

    # remove task
    subparsers.add_parser("remove-task", help="Remove Windows Scheduled Task")

    args = parser.parse_args()

    if not getattr(args, "silent", False):
        print_banner()

    if args.command == "organize":
        cmd_organize(args)
    elif args.command == "undo":
        cmd_undo(args)
    elif args.command == "watch":
        cmd_watch(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "setup-task":
        cmd_setup_task(args)
    elif args.command == "remove-task":
        cmd_remove_task(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
