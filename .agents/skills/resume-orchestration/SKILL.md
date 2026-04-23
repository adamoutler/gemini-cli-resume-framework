---
name: resume-orchestration
description: Execution mode - Workflow for generating tailored resumes and cover letters based on a Job Description (JD). Use this when the user asks to create a resume for a specific job or provides a position description.
---

# Resume Orchestration Workflow

This workflow automates the process of creating a tailored JSON Resume, HTML/PDF exports, and a Cover Letter.

**WARNING: RESOURCE INTENSIVE OPERATION**
- This is a time and token expensive operation.
- **It can take between 15 to 45 minutes for the thorough process to be completed.**
- It involves multiple operations with 8 separate Gemini-based AI Agents.
- **INSTRUCTION FOR AI:** You MUST explicitly warn the user about this 15-45 minute execution time *before* you start the orchestrator or immediately upon starting it, so they know what to expect.

## Prerequisites

- Job Description (JD) saved as a `.txt` file (e.g., in `cv-data/resumes/`).
- Python virtual environment: `./venv/bin/python3`.

## Execution

Run the orchestrator using the following command. Do not background this process, use `timeout`, or attempt to `tail` logs. Simply execute the script and wait for it to complete. 

```bash
./venv/bin/python3 Agentic_Tasks/Orchestrator/resume_orchestrator.py --jd <path_to_job_description.txt>
```

**Optional Arguments:**
- `--notes "Strategic guidance"`: Provide extra context to the builder (e.g., "Emphasize AI and Security"). These are notes provided by user to the resume builder. You are never to make decisions on what should be added. The Resume Builder has instructions which should be modified by the user and not by the AI.
- `--sentinel-only`: Only run the initial security/trap detection check.

## Post-Execution

Once the orchestrator completes successfully:
1. Stage all changes in the `cv-data/` repository directory.
2. Stage all changes in the main `Cv` repository.
3. Commit and push the changes for both repositories. Use a descriptive commit message indicating the generation of the resume for the specific JD.

## Workflow Phases

1. **Phase 0 Setup:** Initializes master session, calculates word frequency, and loads CV data and JD. Includes **ASCII Sanitization** (via `unidecode`) of all inputs to ensure strict ASCII compatibility.
2. **Phase 1 Sentinel:** Performs a security threat check on the JD.
3. **Phase 2 Builder:** Generates an initial JSON draft tailored to the JD.
4. **Phase 3 Validate Audit Review:** Performs schema validation, forensic audit, persona review, and **ASCII Validation**. Any detected Unicode triggers a fixer loop or manual audit requirement.
5. **Phase 4 Cover Letter:** Generates a matching cover letter.
6. **Phase 5 Export Artifacts:** Renders the resume to HTML and PDF (using 'stackoverflow' theme) and generates an appendix PDF.

## Output Handling

- The orchestrator handles all file generation and reporting.
- **DO NOT** list the generated files in your response.
- **DO NOT** provide a summary of the resume creation process.
- **Expected Termination:** A successful run ends with:
  ```
  [REPORT] Email: <generated_email>
  [DONE] Workflow complete for <job_name>
  ---
  This generation took X/5 retries.
  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  >>>>> END OF ORCHESTRATION <<<<<
  ```
- Simply acknowledge completion based on the tool's output (e.g., "Resume orchestration complete.").
