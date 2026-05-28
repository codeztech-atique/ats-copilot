"""Deterministic keyword overlap helper (no Strands @tool decoration)."""
from __future__ import annotations

import re

_STOP = {
    "the", "and", "for", "with", "you", "your", "are", "our", "will",
    "have", "has", "this", "that", "from", "into", "any", "all", "but",
    "not", "can", "may", "use", "used", "using", "able", "work", "role",
    "team", "teams", "etc", "job", "company", "experience", "experiences",
    "years", "year", "skills", "skill", "knowledge", "ability", "strong",
    "good", "plus", "preferred", "required", "requirements", "responsibilities",
}


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9+.#-]{1,}", text.lower())
    return {w for w in words if len(w) > 2 and w not in _STOP}


def compute_keyword_overlap(resume_text: str, jd_text: str) -> dict:
    jd_words = _tokens(jd_text)
    resume_words = _tokens(resume_text)
    if not jd_words:
        return {"overlap_percent": 0.0, "matched_keywords": [], "missing_keywords": []}
    matched = sorted(jd_words & resume_words)
    missing = sorted(jd_words - resume_words)
    pct = round(len(matched) / len(jd_words) * 100, 2)
    return {
        "overlap_percent": pct,
        "matched_keywords": matched[:50],
        "missing_keywords": missing[:50],
    }
