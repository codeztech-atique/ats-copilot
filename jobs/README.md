# How to add a job posting

Drop one `.md` or `.txt` file per job into this folder. The file MUST start
with two or three header lines, then a blank line, then the job description
body:

```
Title: <job title>
Location: <city, country / Remote / Hybrid>
Region: <US | EMEA | UAE | INDIA | GLOBAL>   # optional - inferred from Location if omitted

<full job description text - responsibilities, requirements, nice-to-have, etc.>
```

## Region-specific ATS filtering

Different regions filter resumes differently. The scorer applies region-aware
rules when judging your resume against each job:

| Region | Highlights of the filtering rules applied |
|---|---|
| **US**     | 1-page CV, no photo / DOB, action verbs, quantified impact, ATS keywords, work-auth as a hard filter. |
| **EMEA**   | Up to 2 pages, photo OK in DE/FR/IT (not UK/IE), GDPR, language proficiency (CEFR), EU work authorization. |
| **UAE**    | 2-3 pages, photo expected, nationality + visa status + notice period commonly listed, Arabic a plus, local Gulf experience. |
| **INDIA**  | 2-4 pages, current/expected CTC + notice period, 10th/12th percentages, certifications (AWS/Azure/PMP), location flexibility. |
| **GLOBAL** | Generic best practices - no region weighting. |

You can set `Region:` explicitly, or omit it and let the scorer infer from
`Location:` (e.g. "Dubai" → UAE, "Bangalore" → INDIA, "Berlin" → EMEA,
"Remote - US" → US).

## Examples in this folder

- [`sample_job.md`](./sample_job.md) - US backend role
- [`ai_engineer_remote.md`](./ai_engineer_remote.md) - GLOBAL remote AI role
- [`engineering_manager_blr.md`](./engineering_manager_blr.md) - INDIA EM role
- [`backend_dubai_uae.md`](./backend_dubai_uae.md) - UAE fintech role
- [`cloud_engineer_berlin_emea.md`](./cloud_engineer_berlin_emea.md) - EMEA SaaS role

## Run

From the project root:

```bash
python -m src.score
```

The agent will:
1. Load your resume from `resumes/`.
2. Score it against **every** job file in this folder, applying the
   region-specific rules.
3. Save one detailed report per job in `reports/`.
4. Print a ranked summary table to the terminal and save it as
   `reports/_summary.md`.
