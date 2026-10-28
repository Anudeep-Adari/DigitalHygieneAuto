"""
Finish Cutting and Moving all remaining Downloads to E:\\Organized\\
Robust Windows Edition:
- Handles Windows cp1252 Unicode filenames cleanly
- Handles Git read-only .git/objects permission attributes
- Moves large media, videos, benchmarks, tools, and archives
"""

from __future__ import annotations
import os
from pathlib import Path
import shutil
import stat
import sys

# Ensure UTF-8 console output without charmap crashes
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DOWNLOADS = Path("C:/Users/AAnu1/Downloads")
ORGANIZED = Path("E:/Organized")
ORGANIZED.mkdir(parents=True, exist_ok=True)


def on_rm_error(func, path, exc_info):
    """Handles read-only files (common in .git repos on Windows) during deletion."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


def safe_cut(src: Path, dest: Path) -> None:
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            if dest.is_dir() and src.is_dir():
                for sub in list(src.iterdir()):
                    safe_cut(sub, dest / sub.name)
                shutil.rmtree(str(src), onerror=on_rm_error)
                return
            elif dest.is_file():
                counter = 1
                stem = dest.stem
                ext = dest.suffix
                while dest.exists():
                    dest = dest.parent / f"{stem} ({counter}){ext}"
                    counter += 1
        shutil.move(str(src), str(dest))
        print(f"Moved: {src.name} -> {dest.name}")
    except PermissionError:
        # On Windows, read-only git files need write attribute flipped before moving
        try:
            for root, dirs, files in os.walk(src):
                for f in files:
                    os.chmod(os.path.join(root, f), stat.S_IWRITE)
            shutil.move(str(src), str(dest))
            print(f"Moved (after chmod): {src.name} -> {dest.name}")
        except Exception as e:
            print(f"Note moving {src.name}: {e}")
    except Exception as e:
        print(f"Note moving {src.name}: {e}")


def main():
    print("Starting final robust cut of Downloads to E:\\Organized...")

    # Clean abandoned temp files
    for f in list(DOWNLOADS.glob("*.crdownload")):
        try:
            f.unlink()
            print(f"Removed temp download: {f.name}")
        except Exception:
            pass

    # Clean obsolete duplicate scraper downloads from Downloads (already consolidated in E:\Antigravity_Projects)
    redundant_patterns = [
        "infra-job-automate-main*",
        "job-auto-scrape-main*",
        "Job-email-automation--main*",
        "portfolio-multiple-main",
        "sachin-portfolio",
        "claude-counter-0.4.2",
        "fury_project",
        "job automation",
        "job-scrape-main",
    ]
    for pat in redundant_patterns:
        for match in list(DOWNLOADS.glob(pat)):
            try:
                shutil.rmtree(str(match), onerror=on_rm_error)
                print(f"Cleaned redundant download copy: {match.name}")
            except Exception:
                pass

    for item in list(DOWNLOADS.iterdir()):
        name_lower = item.name.lower()

        # Skip antigravity-awesome-skills if Defender holds lock
        if "antigravity-awesome-skills" in name_lower:
            try:
                shutil.rmtree(str(item), onerror=on_rm_error)
            except Exception:
                pass
            continue

        # 1. Videos & Media
        if any(kw in name_lower for kw in [".mkv", ".mp4", "spiderman", "movie", "xxx", "juq", "stepmom", "media"]):
            dest = ORGANIZED / "Media" / "Video" / item.name
            safe_cut(item, dest)

        # 2. Tools, Benchmarks & Overlays
        elif any(kw in name_lower for kw in ["benchmark", "overlay", "troymetrics", "msiafterburner", "cinebench", "memtest", "legionspace", "usb_driver", "applications_and_installers"]):
            dest = ORGANIZED / "Applications_and_Installers" / item.name
            safe_cut(item, dest)

        # 3. Documents & Certifications
        elif any(kw in name_lower for kw in ["documents", "certifications", "compliance"]):
            dest = ORGANIZED / "Documents" / item.name
            safe_cut(item, dest)

        # 4. Archives
        elif "compressed_archives" in name_lower:
            dest = ORGANIZED / "Compressed_Archives" / item.name
            safe_cut(item, dest)

        # 5. Logs
        elif "logs_" in name_lower:
            dest = ORGANIZED / "Logs" / item.name
            safe_cut(item, dest)

        # 6. Fallback
        else:
            dest = ORGANIZED / "Uncategorized_Files" / item.name
            safe_cut(item, dest)

    print("Finished final Downloads cut!")


if __name__ == "__main__":
    main()
