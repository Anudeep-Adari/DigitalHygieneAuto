"""
Resume Deduplication and Candidate Consolidation Engine
Identifies candidates, detects exact duplicates and older drafts,
and safely archives or stages older versions without destructive loss.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import hashlib
import os
from pathlib import Path
import re
import shutil
from typing import Dict, List, Optional, Set, Tuple

from rich.console import Console
from rich.table import Table

console = Console()


@dataclass
class ResumeFile:
    path: Path
    candidate: str
    variant: str
    mtime: datetime
    size_bytes: int
    file_hash: str
    is_latest: bool = False


def compute_file_hash(path: Path) -> str:
    """Computes SHA-256 hash of a file for exact duplicate detection."""
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()[:12]
    except Exception:
        return "error"


def extract_candidate_and_variant(filename: str) -> Tuple[str, str]:
    """
    Extracts candidate name and format variant from filename.
    Example: 'Anudeep_Adari_ATS_Optimized_Resume.docx' -> ('Anudeep Adari', 'ATS Optimized')
    """
    stem = Path(filename).stem
    stem_lower = stem.lower()

    # Known candidates in user files
    if "anudeep" in stem_lower or "anu bro" in stem_lower:
        candidate = "Anudeep Adari"
    elif "sudheer" in stem_lower:
        candidate = "Sudheer (Oracle DBA)"
    elif "rohith" in stem_lower:
        candidate = "Rohith Annam"
    elif "lohit" in stem_lower:
        candidate = "Lohit"
    elif "pravin" in stem_lower:
        candidate = "Pravin"
    elif "dinesh" in stem_lower:
        candidate = "Dinesh"
    elif "deepthi" in stem_lower:
        candidate = "Allu Deepthi"
    elif "vishnu" in stem_lower:
        candidate = "Vishnu"
    else:
        candidate = "Unknown / General"

    # Identify variant
    variant = "General"
    if "ats" in stem_lower:
        variant = "ATS"
    elif "enhancv" in stem_lower:
        variant = "Enhancv Style"
    elif "infrastructurespecialist" in stem_lower:
        variant = "Infrastructure Specialist"
    elif "twocolumn" in stem_lower:
        variant = "Two Column"
    elif "visual_timeline" in stem_lower:
        variant = "Visual Timeline"
    elif "master_overleaf" in stem_lower:
        variant = "Master Overleaf"
    elif "vmware" in stem_lower:
        variant = "VMware / Windows Admin"
    elif "enhanced" in stem_lower:
        variant = "Enhanced"
    elif "flowcv" in stem_lower:
        variant = "FlowCV"

    return candidate, variant


class ResumeManager:
    def __init__(self, search_roots: List[Path]):
        self.search_roots = search_roots

    def find_all_resumes(self) -> List[ResumeFile]:
        """Finds all resume files across search directories."""
        resumes: List[ResumeFile] = []
        resume_keywords = ["resume", "cv", "ats", "adar1", "flowcv"]

        for root in self.search_roots:
            if not root.exists():
                continue

            for dirpath, _, filenames in os.walk(root):
                for fname in filenames:
                    ext = Path(fname).suffix.lower()
                    if ext not in [".pdf", ".docx", ".doc"]:
                        continue

                    stem_lower = Path(fname).stem.lower()
                    if any(k in stem_lower for k in resume_keywords) or "anudeep" in stem_lower:
                        full_path = Path(dirpath) / fname
                        try:
                            st = full_path.stat()
                            mtime = datetime.fromtimestamp(st.st_mtime)
                            candidate, variant = extract_candidate_and_variant(fname)
                            fhash = compute_file_hash(full_path)
                            resumes.append(
                                ResumeFile(
                                    path=full_path,
                                    candidate=candidate,
                                    variant=variant,
                                    mtime=mtime,
                                    size_bytes=st.st_size,
                                    file_hash=fhash,
                                )
                            )
                        except Exception:
                            continue
        return resumes

    def analyze_resumes(
        self,
    ) -> Dict[str, Dict[str, List[ResumeFile]]]:
        """
        Groups resumes by Candidate -> Variant -> list of files sorted by modified date (newest first).
        """
        all_resumes = self.find_all_resumes()
        grouped: Dict[str, Dict[str, List[ResumeFile]]] = {}

        for r in all_resumes:
            if r.candidate not in grouped:
                grouped[r.candidate] = {}
            if r.variant not in grouped[r.candidate]:
                grouped[r.candidate][r.variant] = []
            grouped[r.candidate][r.variant].append(r)

        # Sort each list by modification date descending
        for cand in grouped:
            for var in grouped[cand]:
                grouped[cand][var].sort(key=lambda x: x.mtime, reverse=True)
                # Mark the first one as latest
                if grouped[cand][var]:
                    grouped[cand][var][0].is_latest = True

        return grouped

    def preview_deduplication(self) -> Tuple[List[ResumeFile], List[ResumeFile]]:
        """
        Returns (to_keep, to_archive)
        """
        grouped = self.analyze_resumes()
        to_keep: List[ResumeFile] = []
        to_archive: List[ResumeFile] = []

        seen_hashes: Set[str] = set()

        table = Table(title="Resume Consolidation & Deduplication Plan")
        table.add_column("Candidate", style="cyan", no_wrap=True)
        table.add_column("Variant", style="yellow")
        table.add_column("File Name", style="white", max_width=40)
        table.add_column("Modified Date", style="magenta")
        table.add_column("Status / Action", style="green")

        for candidate, variants in sorted(grouped.items()):
            for variant, files in variants.items():
                for idx, r in enumerate(files):
                    # Check exact duplicate hash
                    is_hash_duplicate = r.file_hash in seen_hashes

                    if idx == 0 and not is_hash_duplicate:
                        # Keep the latest version of this format
                        to_keep.append(r)
                        status = "[bold green]KEEP (Latest)[/bold green]"
                        seen_hashes.add(r.file_hash)
                    else:
                        to_archive.append(r)
                        if is_hash_duplicate:
                            status = "[bold red]ARCHIVE (Identical duplicate)[/bold red]"
                        else:
                            status = "[yellow]ARCHIVE (Older draft)[/yellow]"

                    table.add_row(
                        candidate,
                        variant,
                        r.path.name,
                        r.mtime.strftime("%Y-%m-%d %H:%M"),
                        status,
                    )

        console.print(table)
        console.print(f"\n[bold]Summary:[/bold] Keeping [green]{len(to_keep)}[/green] latest resumes across candidates. "
                      f"Staging [yellow]{len(to_archive)}[/yellow] older/duplicate files.\n")

        return to_keep, to_archive

    def execute_archive(self, archive_dest: Path, to_archive: List[ResumeFile]) -> int:
        """Safely moves older drafts to archive_dest."""
        archive_dest.mkdir(parents=True, exist_ok=True)
        archived_count = 0

        for r in to_archive:
            if not r.path.exists():
                continue
            dest = archive_dest / r.path.name
            if dest.exists():
                stem = r.path.stem
                ext = r.path.suffix
                dest = archive_dest / f"{stem}_{r.file_hash}{ext}"

            try:
                shutil.move(str(r.path), str(dest))
                archived_count += 1
            except Exception as e:
                console.print(f"[red]Failed to move {r.path.name}:[/red] {e}")

        return archived_count
