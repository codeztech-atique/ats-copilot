"""Region-specific ATS filtering rules.

Resume screening practices differ significantly by region. These hints are
passed to the scoring model so it judges the resume by the conventions of the
target market.
"""
from __future__ import annotations

import re

REGIONS = ("US", "EMEA", "UAE", "INDIA", "GLOBAL")

REGION_RULES: dict[str, str] = {
    "US": """\
US (Workday / Greenhouse / Lever ATS conventions):
- Strong preference for 1-page resumes (2 pages OK for senior/staff+).
- No photo, no date of birth, no marital status, no nationality.
- Education at the bottom; GPA optional, only if strong.
- Action-verb bullet points with quantified impact (metrics, $, %, scale).
- Heavy keyword match against JD; ATS phrasing matters a lot.
- Work authorization / visa status is a hard filter — penalize if unclear and
  the role does not offer sponsorship.
- Remote-friendliness and US time-zone overlap matter for remote roles.
""",
    "EMEA": """\
EMEA (Europe, Middle East, Africa — excluding Gulf):
- CV up to 2 pages is standard; structured "Europass-like" layouts are common.
- Photo is acceptable in DE / FR / IT / ES; avoided in UK / IE / NL.
- Date of birth and nationality are common in DE / FR / IT, not in UK / IE.
- GDPR consent line is a plus.
- Language proficiency (CEFR A1-C2) is highly valued; multilingual candidates
  score higher.
- EU work authorization is a hard filter — penalize candidates needing
  sponsorship unless the JD explicitly offers it.
- Local language fluency strongly boosts fit when the JD is in a local
  language or the role is client-facing.
""",
    "UAE": """\
UAE / Gulf (Workday / Bayt / Naukri Gulf conventions):
- 2-3 page CV is standard.
- Photo is expected; nationality, marital status, and visa status are commonly
  listed and used as filters.
- Arabic language proficiency is a strong plus.
- Current visa status (employment / dependent / visit) materially affects
  shortlisting — penalize if not stated.
- Notice period and availability to join are weighted heavily.
- Local Gulf experience is a meaningful differentiator.
- References are often expected on the CV itself.
""",
    "INDIA": """\
India (Naukri / LinkedIn / Workday conventions):
- 2-4 page CV is standard; education details including 10th / 12th
  percentages are often expected for early/mid-career.
- Current CTC, expected CTC, and notice period are major filters — penalize
  if not stated and the JD does not say "negotiable".
- Strong emphasis on certifications (AWS, Azure, GCP, PMP, Scrum, etc.).
- Multiple tech stacks listed is normal and expected.
- Location flexibility (Bangalore / Hyderabad / Pune / NCR / Chennai) and
  willingness to relocate strongly affect shortlisting for on-site roles.
- Photo is optional; not penalized either way.
""",
    "GLOBAL": """\
Global / unspecified region: apply generic best practices — quantified impact,
clear tech stack match, seniority alignment, location fit. Do not over-weight
any single regional convention.
""",
}


_LOCATION_HINTS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(uae|dubai|abu dhabi|sharjah|doha|qatar|riyadh|jeddah|kuwait|bahrain|oman|muscat|gulf)\b", re.I), "UAE"),
    (re.compile(r"\b(india|bangalore|bengaluru|hyderabad|pune|chennai|mumbai|delhi|noida|gurgaon|gurugram|kolkata|ahmedabad)\b", re.I), "INDIA"),
    (re.compile(r"\b(us|usa|united states|remote\s*-\s*us|new york|nyc|san francisco|sf|seattle|austin|boston|chicago|los angeles|la|washington|atlanta|denver|miami)\b", re.I), "US"),
    (re.compile(r"\b(emea|europe|uk|united kingdom|london|manchester|dublin|ireland|germany|berlin|munich|hamburg|france|paris|netherlands|amsterdam|spain|madrid|barcelona|italy|rome|milan|sweden|stockholm|switzerland|zurich|poland|warsaw|portugal|lisbon)\b", re.I), "EMEA"),
]


def infer_region(location: str) -> str:
    """Infer region from a freeform location string."""
    if not location:
        return "GLOBAL"
    for pattern, region in _LOCATION_HINTS:
        if pattern.search(location):
            return region
    if re.search(r"\bremote\b", location, re.I):
        return "GLOBAL"
    return "GLOBAL"


def normalize_region(value: str | None) -> str:
    """Map a freeform region string onto one of the supported regions."""
    if not value:
        return "GLOBAL"
    v = value.strip().upper()
    if v in REGIONS:
        return v
    if v in {"EUROPE", "EU", "UK", "GB", "GERMANY", "FRANCE", "NETHERLANDS"}:
        return "EMEA"
    if v in {"USA", "U.S.", "U.S.A", "AMERICA", "NORTH AMERICA"}:
        return "US"
    if v in {"GULF", "MIDDLE EAST", "DUBAI", "ABU DHABI"}:
        return "UAE"
    if v in {"IN", "BHARAT"}:
        return "INDIA"
    return "GLOBAL"


def rules_for(region: str) -> str:
    return REGION_RULES.get(region, REGION_RULES["GLOBAL"])
