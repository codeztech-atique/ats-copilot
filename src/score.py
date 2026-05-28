"""Score the resume against every job posting file in jobs/.

Run: python -m src.score
"""
from __future__ import annotations

import json
import re

from dotenv import load_dotenv

from .agent import build_score_agent
from .io_utils import list_jobs, load_job, load_resume, save_report
from .keyword_match import compute_keyword_overlap
from .regions import rules_for

load_dotenv()


def _safe_slug(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", text).strip("_").lower() or "job"


_SCORE_RE = re.compile(r"Final Selection Score:\*?\*?\s*([0-9]+(?:\.[0-9]+)?)\s*%")
_CHANCE_RE = re.compile(r"Shortlist Chance:\*?\*?\s*([A-Za-z ]+)")


def _parse_summary(report: str) -> tuple[float, str]:
    score_m = _SCORE_RE.search(report)
    chance_m = _CHANCE_RE.search(report)
    score = float(score_m.group(1)) if score_m else 0.0
    chance = chance_m.group(1).strip() if chance_m else "Unknown"
    return score, chance


def _score_one(agent, resume_name: str, resume_text: str, job: dict) -> str:
    overlap = compute_keyword_overlap(resume_text, job["description"])
    region = job.get("region", "GLOBAL")
    prompt = (
        f"Resume filename: {resume_name}\n"
        f"Job file: {job['filename']}\n"
        f"Job Title: {job['title']}\n"
        f"Location: {job['location']}\n"
        f"Region: {region}\n\n"
        f"Region-specific ATS filtering rules to apply:\n{rules_for(region)}\n"
        f"Job Description:\n\"\"\"\n{job['description']}\n\"\"\"\n\n"
        f"Resume text:\n\"\"\"\n{resume_text}\n\"\"\"\n\n"
        f"Deterministic keyword overlap baseline:\n"
        f"{json.dumps(overlap, indent=2)}\n\n"
        "Produce the ATS Match Report now. Apply the region-specific rules "
        "above when judging location fit, work-authorization, and ATS phrasing."
    )
    return str(agent(prompt))


def main() -> None:
    resume_name, resume_text = load_resume()
    job_paths = list_jobs()
    if not job_paths:
        print("[error] No job postings found in jobs/. Add a .md or .txt file.")
        return

    print(f"[info] resume: {resume_name}")
    print(f"[info] scoring {len(job_paths)} job posting(s)...\n")

    agent = build_score_agent()
    rows = []  # (title, location, region, file, score, chance, report_filename)

    for path in job_paths:
        job = load_job(path.name)
        print(f"  -> {job['filename']}  ({job['title']} - {job['location']}) [region={job['region']}]")
        report = _score_one(agent, resume_name, resume_text, job)
        score, chance = _parse_summary(report)
        slug = f"score_{_safe_slug(job['title'])}.md"
        out = save_report(slug, report)
        rows.append((job["title"], job["location"], job["region"], job["filename"], score, chance, out.name))
        print(f"     score={score:.1f}%  chance={chance}  ->  reports/{out.name}\n")

    rows.sort(key=lambda r: r[4], reverse=True)

    summary_lines = [
        f"# ATS Score Summary - {resume_name}",
        "",
        "| Rank | Job Title | Location | Region | Score | Shortlist Chance | Report |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, (title, loc, region, _file, score, chance, report_file) in enumerate(rows, 1):
        summary_lines.append(
            f"| {i} | {title} | {loc} | {region} | **{score:.1f}%** | {chance} | "
            f"[{report_file}]({report_file}) |"
        )
    summary_md = "\n".join(summary_lines) + "\n"
    summary_path = save_report("_summary.md", summary_md)

    print("=" * 80)
    print(summary_md)
    print("=" * 80)
    print(f"[saved] {summary_path}")


if __name__ == "__main__":
    main()
