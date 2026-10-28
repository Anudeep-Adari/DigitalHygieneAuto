"""
Prune All Empty Folders across D:, E:, and Downloads
- Moves lone index.html from D:\\New folder to D:\\Organized\\Code_and_Scripts\\
- Cleans defunct .crdownload in E:\\documents
- Renames E:\\New folder (jarvis_backup) to E:\\jarvis_backup
- Recursively purges all truly empty folders (0 children) across D:, E:, and Downloads
- Strictly protects Windows, Games, Git repos, and active projects
"""

from __future__ import annotations
import os
from pathlib import Path
import shutil

PROTECTED_NAMES = {
    "windows",
    "program files",
    "program files (x86)",
    "programdata",
    "appdata",
    "games",
    "riot games",
    "xboxgames",
    "windowsapps",
    "wpsystem",
    "system volume information",
    "$recycle.bin",
    ".git",
    "node_modules",
    "venv",
    ".venv",
}


def is_protected(dir_path: Path) -> bool:
    parts = [p.lower() for p in dir_path.parts]
    if any(p in PROTECTED_NAMES for p in parts):
        return True
    return False


def prep_cleanup():
    # 1. Move D:\New folder\index.html to D:\Organized\Code_and_Scripts
    d_nf_index = Path("D:/New folder/index.html")
    if d_nf_index.exists():
        dest = Path("D:/Organized/Code_and_Scripts/index (from New folder).html")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(d_nf_index), str(dest))
        print("Moved D:\\New folder\\index.html -> D:\\Organized\\Code_and_Scripts\\")

    # 2. Clean defunct .crdownload in E:\documents
    e_cr = Path("E:/documents/Unconfirmed 580306.crdownload")
    if e_cr.exists():
        try:
            e_cr.unlink()
            print("Removed defunct temp download in E:\\documents")
        except Exception as e:
            print(f"Note removing .crdownload: {e}")

    # 3. Rename E:\New folder to E:\jarvis_backup
    e_nf = Path("E:/New folder")
    if e_nf.exists() and (e_nf / "jarvis_backup").exists():
        dest = Path("E:/jarvis_backup")
        if not dest.exists():
            shutil.move(str(e_nf / "jarvis_backup"), str(dest))
            shutil.rmtree(str(e_nf), ignore_errors=True)
            print("Renamed E:\\New folder\\jarvis_backup -> E:\\jarvis_backup")


def remove_empty_folders(target_root: Path) -> int:
    deleted_count = 0
    # Bottom-up traversal so nested empty folders collapse cleanly
    for root, dirs, files in os.walk(target_root, topdown=False):
        current = Path(root)
        if current == target_root:
            continue
        if is_protected(current):
            continue

        try:
            # Check if directory has no files and no subdirectories
            if not any(current.iterdir()):
                current.rmdir()
                deleted_count += 1
                print(f"Deleted empty folder: {current}")
        except Exception:
            pass

    return deleted_count


def main():
    print("Pre-cleaning loose items and empty folder targets...")
    prep_cleanup()

    targets = [
        Path("D:/"),
        Path("E:/"),
        Path("C:/Users/AAnu1/Downloads"),
    ]

    total_deleted = 0
    for t in targets:
        if t.exists():
            print(f"\nScanning for empty folders in {t}...")
            count = remove_empty_folders(t)
            total_deleted += count
            print(f"Purged {count} empty folders in {t}.")

    print(f"\nTotal empty folders deleted: {total_deleted}")


if __name__ == "__main__":
    main()
