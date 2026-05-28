"""Shared helpers for reading resumes and job postings from disk.

These are plain Python functions (not Strands tools) so the entrypoint scripts
can call them directly and feed the data inline to the agent.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
RESUME_DIR = ROOT / "resumes"
JOBS_DIR = ROOT / "jobs"
REPORTS_DIR = ROOT / "reports"


def _read_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def _read_docx(path: Path) -> str:
    import docx

    document = docx.Document(str(path))
    return "\n".join(p.text for p in document.paragraphs)


def load_resume(filename: Optional[str] = None) -> tuple[str, str]:
    """Return (filename, text) of a resume in resumes/."""
    if not RESUME_DIR.exists():
        raise FileNotFoundError("resumes/ folder does not exist.")

    if filename:
        path = RESUME_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"{filename} not found in resumes/.")
    else:
        candidates = sorted(
            p for p in RESUME_DIR.iterdir()
            if p.suffix.lower() in {".pdf", ".docx", ".txt"}
        )
        if not candidates:
            raise FileNotFoundError(
                "No resume found in resumes/. Drop a PDF/DOCX/TXT file there."
            )
        path = candidates[0]

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        text = _read_pdf(path)
    elif suffix == ".docx":
        text = _read_docx(path)
    else:
        text = path.read_text(encoding="utf-8", errors="ignore")

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        raise ValueError(f"Resume {path.name} is empty after extraction.")
    return path.name, text


def list_jobs() -> list[Path]:
    """Return all job posting files in jobs/ (sorted)."""
    if not JOBS_DIR.exists():
        return []
    return sorted(
        p for p in JOBS_DIR.iterdir()
        if p.suffix.lower() in {".md", ".txt"} and not p.name.lower().startswith("readme")
    )


def load_job(filename: Optional[str] = None) -> dict:
    """Return dict {filename, title, location, description} for a job posting."""
    if not JOBS_DIR.exists():
        raise FileNotFoundError("jobs/ folder does not exist.")

    if filename:
        path = JOBS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"{filename} not found in jobs/.")
    else:
        candidates = list_jobs()
        if not candidates:
            raise FileNotFoundError(
                "No job file found in jobs/. Drop a .md or .txt file there."
            )
        path = candidates[0]

    raw = path.read_text(encoding="utf-8", errors="ignore")
    title_m = re.search(r"^\s*Title\s*:\s*(.+)$", raw, re.IGNORECASE | re.MULTILINE)
    loc_m = re.search(r"^\s*Location\s*:\s*(.+)$", raw, re.IGNORECASE | re.MULTILINE)
    region_m = re.search(r"^\s*Region\s*:\s*(.+)$", raw, re.IGNORECASE | re.MULTILINE)
    body = raw
    parts = re.split(r"\n\s*\n", raw, maxsplit=1)
    if len(parts) == 2:
        body = parts[1].strip()

    from .regions import infer_region, normalize_region

    location = loc_m.group(1).strip() if loc_m else "(unknown)"
    if region_m:
        region = normalize_region(region_m.group(1))
    else:
        region = infer_region(location)

    return {
        "filename": path.name,
        "title": title_m.group(1).strip() if title_m else "(unknown)",
        "location": location,
        "region": region,
        "description": body.strip(),
    }


def save_report(filename: str, content: str) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    out = REPORTS_DIR / filename
    out.write_text(content, encoding="utf-8")
    return out
