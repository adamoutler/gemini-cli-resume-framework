---
name: interview-intelligence
description: Interview Preparation Mode - Generates a strategic "Intelligence Pre-Interview Sheet" by synthesizing the Job Description, Company news, and Candidate history. Use this when preparing for an interview or researching a target role.
---

# Interview Intelligence Workflow

This skill prepares the candidate ([Your Name]) for a high-stakes interview by generating a structured Markdown dossier that maps candidate assets to company pains.

## Prerequisites

- Job Description (JD) saved as a `.txt` file.
- Python virtual environment: `./venv/bin/python3`.

## Execution

Run the interview prep orchestrator using the following command:

```bash
./venv/bin/python3 Codex_Tasks/Orchestrator/generate_interview_prep.py --jd <path_to_jd.txt> --company "<Company Name>" --position "<Position Title>"
```

## Strategy: The "Dating" Metaphor

The orchestrator uses a specific strategy to ensure alignment:
1.  **The Attraction:** Identifies what the company is truly looking for (e.g., Scale, Stability, Disruption).
2.  **The Spark:** Maps [First Name]'s specific stories (from `CV-Data` and past resumes) to the company's problems.
3.  **The Compatibility:** Aligns [First Name]'s core values (Curiosity, Creativity, Forward-Thinking) with the company culture.

## Output Format

The generated dossier (`cv-data/resumes/[Position]-[Company]-Interview-Prep.md`) includes:
- **Intelligence Brief:** Culture vibe, recent news, and "Love Language" (key phrases to echo).
- **Strategic Talking Points:** Problem/Solution/Hook mappings.
- **Strategic Questions:** Deep research, cultural fit, and technical depth questions for the candidate to ask.
- **Red Flags:** Cultural "Icks" to avoid.

**CRITICAL:** After generation, you MUST explicitly restate the absolute `file://` URI to the generated PDF on a single line in your final response to the user so it is easily clickable/copyable.

## Post-Processing

After generation, it is common to:
1.  **Review the Markdown** in `cv-data/resumes/`.
2.  **Convert to PDF** using `pandoc` or `chrome --headless` if a portable version is needed.
