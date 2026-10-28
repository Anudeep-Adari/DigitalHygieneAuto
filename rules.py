"""
Rule Engine and Classifier for DigitalHygieneAuto
Handles config loading, ignore filtering, keyword/extension classification,
safety blacklists, and conflict-free destination resolution.
"""

from __future__ import annotations
import fnmatch
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml


DEFAULT_CONFIG: Dict[str, Any] = {
    "settings": {
        "dry_run": False,
        "download_stabilization_seconds": 4,
        "max_undo_batches": 50,
        "auto_rename_collisions": True,
    },
    "targets": [
        {"path": str(Path.home() / "Downloads"), "scope": "shallow", "label": "User Downloads"},
        {"path": str(Path.home() / "Desktop"), "scope": "shallow", "label": "User Desktop"},
        {"path": "D:\\", "scope": "root_only", "label": "Drive D: Root"},
        {"path": "E:\\", "scope": "root_only", "label": "Drive E: Root"},
    ],
    "protected_paths": [
        "C:\\Windows",
        "C:\\Program Files",
        "C:\\Program Files (x86)",
        "C:\\ProgramData",
        "E:\\Games",
        "E:\\Riot Games",
        "E:\\XboxGames",
        "E:\\WindowsApps",
        "E:\\WpSystem",
    ],
    "ignore": {
        "extensions": [".tmp", ".crdownload", ".part", ".download", ".ini", ".sys", ".lnk"],
        "patterns": ["desktop.ini", "thumbs.db", "~$*", ".git*", "node_modules", "$RECYCLE.BIN", "System Volume Information"],
    },
    "categories": [
        {
            "name": "Documents/Resumes",
            "keywords": ["resume", "cv", "ats", "cover letter", "overleaf"],
            "extensions": [".pdf", ".docx", ".doc"],
        },
        {
            "name": "Documents/Certifications",
            "keywords": ["certificate", "credential", "certified", "exam", "score report", "offerletter", "experience letter"],
            "extensions": [".pdf", ".png", ".jpg", ".jpeg"],
        },
        {
            "name": "Documents/Technical_Docs_and_SOPs",
            "keywords": ["sop", "guide", "blueprint", "roadmap", "handover", "troubleshooting", "runbook", "specification", "provisioning", "rca_sop"],
            "extensions": [".pdf", ".docx", ".html", ".md", ".txt"],
        },
        {
            "name": "Media/Work_Shifts_and_Rosters",
            "keywords": ["shift", "noon shift", "night shift", "week", "roster", "schedule"],
            "extensions": [".png", ".jpg", ".jpeg"],
        },
        {
            "name": "Financial_and_Expenses",
            "keywords": ["expense", "expenses", "invoice", "receipt", "fmg approval", "hdfc", "fact_pc"],
            "extensions": [".xlsx", ".xls", ".csv", ".pdf"],
        },
        {
            "name": "Applications_and_Installers",
            "extensions": [".exe", ".msi", ".bat", ".cmd"],
        },
        {
            "name": "Compressed_Archives",
            "extensions": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"],
        },
        {
            "name": "Documents/PDFs",
            "extensions": [".pdf"],
        },
        {
            "name": "Documents/Word_and_Office",
            "extensions": [".docx", ".doc", ".odt", ".rtf"],
        },
        {
            "name": "Documents/Spreadsheets",
            "extensions": [".xlsx", ".xls", ".csv", ".tsv"],
        },
        {
            "name": "Documents/Presentations",
            "extensions": [".pptx", ".ppt", ".key"],
        },
        {
            "name": "Media/Images",
            "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff"],
        },
        {
            "name": "Media/Video",
            "extensions": [".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".wmv"],
        },
        {
            "name": "Media/Audio",
            "extensions": [".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"],
        },
        {
            "name": "Code_and_Scripts",
            "extensions": [".py", ".ps1", ".sh", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".json", ".xml", ".yaml", ".yml", ".sql"],
        },
        {
            "name": "Text_and_Notes",
            "extensions": [".txt", ".log", ".md"],
        },
    ],
}


class RuleEngine:
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or (Path(__file__).parent / "config.yaml")
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = yaml.safe_load(f)
                    if isinstance(loaded, dict):
                        return loaded
            except Exception as e:
                print(f"[Warning] Failed to parse {self.config_path}: {e}. Using built-in defaults.")
        return DEFAULT_CONFIG

    def is_protected_path(self, path: Path) -> bool:
        """Never allow touching system directories or protected game/app paths."""
        path_str = str(path).lower()
        protected = self.config.get("protected_paths", [])
        for p in protected:
            if path_str.startswith(str(p).lower()):
                return True
        return False

    def should_ignore(self, path: Path) -> bool:
        """Check if file should be ignored based on name, extension, or system patterns."""
        if self.is_protected_path(path):
            return True

        name = path.name
        name_lower = name.lower()
        suffix = path.suffix.lower()

        # Check ignored extensions
        ignored_exts = [ext.lower() for ext in self.config.get("ignore", {}).get("extensions", [])]
        if suffix in ignored_exts:
            return True

        # Check ignored wildcard patterns
        ignored_patterns = self.config.get("ignore", {}).get("patterns", [])
        for pattern in ignored_patterns:
            if fnmatch.fnmatch(name_lower, pattern.lower()):
                return True

        # Ignore hidden files or directories
        if name.startswith("."):
            return True

        # Ignore git repo internals if found
        path_parts_lower = [part.lower() for part in path.parts]
        if ".git" in path_parts_lower or "node_modules" in path_parts_lower:
            return True

        return False

    def classify_file(self, file_path: Path) -> Optional[str]:
        """
        Classifies a file into a category string (e.g. 'Documents/Resumes').
        Returns None if file is ignored or doesn't match any rule.
        """
        if not file_path.is_file() or self.should_ignore(file_path):
            return None

        stem_lower = file_path.stem.lower()
        suffix_lower = file_path.suffix.lower()

        categories: List[Dict[str, Any]] = self.config.get("categories", [])

        for cat in categories:
            cat_name = cat.get("name")
            cat_exts = [e.lower() for e in cat.get("extensions", [])]
            cat_keywords = [k.lower() for k in cat.get("keywords", [])]

            # 1. If rule has both keywords and extensions:
            if cat_keywords and cat_exts:
                if suffix_lower in cat_exts:
                    for kw in cat_keywords:
                        if kw in stem_lower:
                            return cat_name

            # 2. If rule has only keywords:
            elif cat_keywords and not cat_exts:
                for kw in cat_keywords:
                    if kw in stem_lower:
                        return cat_name

            # 3. If rule has only extensions:
            elif cat_exts and not cat_keywords:
                if suffix_lower in cat_exts:
                    return cat_name

        # Fallback for unrecognized file types
        return "Uncategorized_Files"

    @staticmethod
    def get_collision_free_destination(target_dir: Path, original_filename: str) -> Path:
        """
        If a file already exists in target_dir, appends (1), (2), etc.
        Example: report.pdf -> report (1).pdf
        """
        dest = target_dir / original_filename
        if not dest.exists():
            return dest

        stem = Path(original_filename).stem
        suffix = Path(original_filename).suffix
        counter = 1

        while True:
            candidate = target_dir / f"{stem} ({counter}){suffix}"
            if not candidate.exists():
                return candidate
            counter += 1
