# ATS Score Agent

A backend-only Python agent that scores your resume against job postings the
way **Workday / Greenhouse / LinkedIn** ATS rankers do, and recommends what
roles you should apply for. Built on the
[Strands Agents SDK](https://strandsagents.com) with **Amazon Bedrock** (Nova
Pro by default) or **OpenAI** as the model backend.

No UI. Just two scripts:

| Command | What it does |
|---|---|
| `python -m src.recommend` | Analyzes your resume and recommends the best job titles, industries, locations, and search keywords for LinkedIn / Workday / Greenhouse. |
| `python -m src.score`     | Scores your resume against **every** job posting in `jobs/`, returns a percentage + shortlist chance per job, and saves a ranked summary. |

---

## Table of contents

1. [How it works](#how-it-works)
2. [Project layout](#project-layout)
3. [Requirements](#requirements)
4. [Setup](#setup)
5. [Model providers](#model-providers)
6. [Adding your resume](#adding-your-resume)
7. [Adding job postings](#adding-job-postings)
8. [Usage](#usage)
9. [Scoring methodology](#scoring-methodology)
10. [Output reports](#output-reports)
11. [Troubleshooting](#troubleshooting)

---

## How it works

1. Drop your resume (PDF / DOCX / TXT) into [`resumes/`](./resumes).
2. Drop one or more job postings (`.md` / `.txt`) into [`jobs/`](./jobs)
   using the simple `Title:` / `Location:` header format.
3. Run one of the two scripts. Each script:
   - extracts plain text from your resume,
   - computes a deterministic keyword-overlap baseline,
   - sends everything to a Bedrock / OpenAI model via Strands Agents,
   - produces a structured markdown report,
   - saves it to [`reports/`](./reports).

The model invocation is **single-shot** (no agentic tool loop) for maximum
reliability on Bedrock Nova — file IO is done in Python and the data is
inlined into the prompt.

## Project layout

```
ATS-Score/
├── resumes/                  # drop your resume here (PDF / DOCX / TXT)
├── jobs/                     # drop job postings here (.md / .txt)
│   ├── README.md             # job-file format guide
│   ├── sample_job.md
│   ├── ai_engineer_remote.md
│   └── engineering_manager_blr.md
├── reports/                  # generated markdown reports (gitignored)
│   ├── _summary.md           # ranked summary from `score`
│   ├── recommendations.md    # from `recommend`
│   └── score_<job-title>.md  # one per job
├── src/
│   ├── agent.py              # Strands Agent factories + system prompts
│   ├── io_utils.py           # resume / job loaders, save_report
│   ├── keyword_match.py      # deterministic keyword overlap
│   ├── recommend.py          # entrypoint: python -m src.recommend
│   └── score.py              # entrypoint: python -m src.score
├── requirements.txt
├── .env.example
└── README.md
```

## Requirements

- **Python 3.10+** (Strands does not support 3.9).
  On macOS: `brew install python@3.12`
- One of:
  - **AWS account with Bedrock access** to an Amazon Nova or Anthropic Claude
    model (Nova Pro recommended — no Marketplace payment required), **or**
  - **OpenAI API key**.
- macOS / Linux. Windows should work but is untested.

## Setup

```bash
cd ATS-Score

# 1. Create a Python 3.10+ virtualenv
python3.12 -m venv .venv          # or python3.10 / python3.11
source .venv/bin/activate

# 2. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Configure credentials
cp .env.example .env
# Then open .env and fill in either Bedrock or OpenAI credentials.
```

### `.env` reference

```env
# Choose provider: bedrock (default) or openai
MODEL_PROVIDER=bedrock

# --- AWS Bedrock ---
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0

# --- OpenAI (only if MODEL_PROVIDER=openai) ---
OPENAI_API_KEY=
OPENAI_MODEL_ID=gpt-4o-mini
```

## Model providers

### Amazon Bedrock (default)

- Default model: **`us.amazon.nova-pro-v1:0`** — works without an AWS
  Marketplace subscription.
- Other supported model IDs you can set in `BEDROCK_MODEL_ID`:
  - `us.amazon.nova-lite-v1:0` — cheaper, slightly lower quality
  - `us.amazon.nova-micro-v1:0` — cheapest, fastest, lowest quality
  - `us.anthropic.claude-3-5-haiku-20241022-v1:0` — requires Marketplace
    payment method
  - `us.anthropic.claude-opus-4-20250514-v1:0` — most capable, most expensive
- Required AWS IAM permissions: `bedrock:InvokeModel`,
  `bedrock:InvokeModelWithResponseStream`, `bedrock:Converse`,
  `bedrock:ConverseStream`.

### OpenAI

Set in `.env`:
```env
MODEL_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL_ID=gpt-4o-mini
```

## Adding your resume

Drop a single file into [`resumes/`](./resumes). Supported formats:

- `.pdf` (parsed with `pypdf`)
- `.docx` (parsed with `python-docx`)
- `.txt`

If multiple resumes are present the first one alphabetically is used.

## Adding job postings

Each job posting is a single `.md` or `.txt` file inside [`jobs/`](./jobs)
that **must** start with two header lines, then a blank line, then the body:

```
Title: Senior Backend Engineer
Location: Remote - US

We are hiring a Senior Backend Engineer to design and scale our distributed
services. You will own services written in Python (FastAPI), deploy them on
AWS, and work with the data and platform teams.

Requirements:
- 5+ years of backend engineering experience
- Strong Python and AWS
- ...
```

Drop as many job files into `jobs/` as you want — `python -m src.score`
will score your resume against **every** one and rank them.

See the bundled examples:
- [`jobs/sample_job.md`](./jobs/sample_job.md)
- [`jobs/ai_engineer_remote.md`](./jobs/ai_engineer_remote.md)
- [`jobs/engineering_manager_blr.md`](./jobs/engineering_manager_blr.md)

## Usage

```bash
source .venv/bin/activate

# What kind of jobs should I apply for?  (uses only resumes/)
python -m src.recommend

# How well does my resume match each job in jobs/?
python -m src.score
```

### Example `score` output

```
[info] resume: Atique_Resume.pdf
[info] scoring 3 job posting(s)...

  -> ai_engineer_remote.md  (Staff AI Engineer - Agentic Systems - Remote - Global)
     score=82.0%  chance=Very High  ->  reports/score_staff_ai_engineer_-_agentic_systems.md

  -> engineering_manager_blr.md  (Engineering Manager - Platform - Bangalore, India (Hybrid))
     score=80.0%  chance=High  ->  reports/score_engineering_manager_-_platform.md

  -> sample_job.md  (Senior Backend Engineer - Remote - US)
     score=70.0%  chance=Medium  ->  reports/score_senior_backend_engineer.md

================================================================================
# ATS Score Summary - Atique_Resume.pdf

| Rank | Job Title                            | Location                  | Score  | Shortlist Chance |
|------|--------------------------------------|---------------------------|--------|------------------|
|   1  | Staff AI Engineer - Agentic Systems  | Remote - Global           | 82.0%  | Very High        |
|   2  | Engineering Manager - Platform       | Bangalore, India (Hybrid) | 80.0%  | High             |
|   3  | Senior Backend Engineer              | Remote - US               | 70.0%  | Medium           |
```

## Scoring methodology

Each job is scored across six weighted dimensions:

| Dimension                            | Weight |
|--------------------------------------|--------|
| Hard skills / tech stack             | 35%    |
| Years of experience & seniority      | 20%    |
| Domain / industry relevance          | 15%    |
| Education & certifications           | 10%    |
| Keyword / ATS phrasing match         | 10%    |
| Location fit (remote / same city)    | 10%    |

The final selection probability (0–100%) maps to a shortlist chance:

| Score range | Shortlist chance |
|-------------|-------------------|
| < 40%       | Low               |
| 40 – 65%    | Medium            |
| 66 – 80%    | High              |
| > 80%       | Very High         |

A deterministic keyword-overlap baseline (see
[`src/keyword_match.py`](./src/keyword_match.py)) is computed and passed
to the model as a sanity check alongside its semantic judgment.

## Output reports

All reports are written to [`reports/`](./reports) (gitignored):

- `recommendations.md` — output of `python -m src.recommend`.
- `score_<job-title>.md` — one detailed report per job.
- `_summary.md` — ranked summary table across all scored jobs.

Each scoring report contains:
- Final selection score and shortlist chance
- Per-dimension score breakdown table
- Matched strengths
- Gaps / missing keywords
- Concrete recommendations to improve your resume

## Troubleshooting

**`ERROR: Could not find a version that satisfies the requirement strands-agents`**
Your Python is too old. Strands requires Python 3.10+. Recreate the venv with
`python3.12 -m venv .venv`.

**`ResourceNotFoundException ... This model version has reached the end of its life`**
The configured Bedrock model is no longer active. Set
`BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0` in `.env`.

**`AccessDeniedException ... INVALID_PAYMENT_INSTRUMENT`**
Your AWS account does not have a payment method for AWS Marketplace, which is
required for Anthropic Claude models on Bedrock. Either:
- add a payment method in the AWS Billing console and request model access in
  Bedrock → Model access, or
- stay on `us.amazon.nova-pro-v1:0` (no Marketplace subscription needed), or
- switch to OpenAI by setting `MODEL_PROVIDER=openai` in `.env`.

**`modelStreamErrorException: Model produced invalid sequence as part of ToolUse`**
This used to happen on Nova with agentic tool loops. The current code does file
IO in Python and calls the model once, so this should no longer occur. If you
re-introduce tools, prefer Anthropic Claude models for reliable multi-turn tool
use.

**`No resume found in resumes/`**
Drop a `.pdf`, `.docx`, or `.txt` file into [`resumes/`](./resumes).

**`No job file found in jobs/`**
Drop a `.md` or `.txt` file into [`jobs/`](./jobs) using the
`Title:` / `Location:` header format.
