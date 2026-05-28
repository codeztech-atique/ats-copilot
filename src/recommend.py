"""Recommend jobs to apply based on the resume in resumes/.

Run: python -m src.recommend
"""
from __future__ import annotations

from dotenv import load_dotenv

from .agent import build_recommend_agent
from .io_utils import load_resume, save_report

load_dotenv()


def main() -> None:
    resume_name, resume_text = load_resume()
    print(f"[info] loaded resume: {resume_name} ({len(resume_text)} chars)")

    agent = build_recommend_agent()
    prompt = (
        f"Resume filename: {resume_name}\n\n"
        f"Resume text:\n\"\"\"\n{resume_text}\n\"\"\"\n\n"
        "Produce the job recommendations report now."
    )
    result = agent(prompt)
    report = str(result)

    out = save_report("recommendations.md", report)
    print("\n" + "=" * 80)
    print(report)
    print("=" * 80)
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
