# CV-as-Code Agent Manual

This repository is a structured database of professional experience. It uses automated workflows to generate tailored resumes and cover letters.

## Repository Overview
- **`cv-data/`**: The central markdown database (private).
- **`Agentic_Tasks/`**: Automated workflows and tools.
- **`cv-data/resumes/`**: Output directory for generated artifacts.

## Agent Context & Joplin RAG Integration
This repository utilizes an optional Retrieval-Augmented Generation (RAG) hook that automatically queries a local Joplin memory server to inject semantic context into your prompt stream before processing.
- **RAG Kill Switch (`.settings/norag`)**: The automatic injection of Joplin context is controlled by the presence of the `.settings/norag` file.
  - If `.settings/norag` **exists**, the RAG hook is disabled and context is kept clean.
  - If `.settings/norag` is **deleted**, the RAG hook is active and Joplin notes will be appended to user prompts.
- As an agent, you must respect this switch and you are authorized to create or delete `.settings/norag` if the user complains about context bloat or requests access to their Joplin memory.

## Prerequisites
- **Node.js**: Required for `resume-cli`.
- **Python 3**: Use `./venv/bin/python3` for all scripts.
- **Setup**: `npm install && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`.
- **ASCII Mandate**: All generated artifacts MUST be strictly plain ASCII.
    - If a script fails with a Non-ASCII encoding error (Exit Code 1), you CAN and SHOULD autonomously fix the input file. 
    - Sanitize all non-ASCII (smart quotes, accents, Cyrillic, em-dashes, etc.) to visual or transliterated ASCII equivalents (e.g., replace bullets with `*`, em-dashes with `-`, or use `unidecode`). Do this proactively if needed.
    - If no clear equivalent exists, contextually rephrase or omit the character/word to maintain professional flow and correctness.

## Core Mandate
Always utilize the automated orchestrator for resume generation tasks. Do not build JSON files manually or manually execute steps of the pipeline (e.g., manual PDF rendering or cover letter generation) if the pipeline fails or times out. The pipeline is designed to generate all required outputs autonomously. 
- When a user provides a Job Description without mentioning a scheduled interview, interviewer, or date, ALWAYS automatically run the resume-orchestration pipeline. DO NOT ask if they want to run the interview-intelligence tool unless there is clear context of an upcoming interview.

If the pipeline fails, throws an error, exits with a non-zero exit code, produces hallucinated content, OR outputs ANY `[WARN]`, `[ERROR]`, or `[FATAL]` log regarding missing context/files (such as "No target job description was found"):
1.  **HALT IMMEDIATELY**: Stop your execution. The session is invalidated. Do not attempt to force the workflow to continue.
2.  **ABSOLUTELY NO AUTONOMOUS ALTERATIONS TO CODE/PIPELINE**: Never attempt to write custom python scripts, fix agentic pipeline code, or bypass the pipeline with manual actions to get around a core logic error. (You MAY sanitize text files as noted in the ASCII mandate).
3.  **ZERO TOLERANCE FOR HALLUCINATIONS/MISSING CONTEXT**: You must actively read the logs as the orchestrator runs. If the internal Forensic Audit flags ANY exceptions, or if a step reports that it cannot find the Job Description or Master Session, you must consider the run compromised.
4.  **DO NOT TRUST 'DONE'**: Never blindly trust the final `[DONE]` message if the preceding logs show failures, warnings, or missing context. A resume built on missing data is garbage.
5.  **EXPLICITLY WARN THE USER**: Stop and report exactly what was fabricated or what errored out. Quote the exact logs showing the hallucinated claims or the specific error message.
6.  **DELETE COMPROMISED ARTIFACTS**: If the pipeline outputs a PDF or JSON file that you know contains fabricated data, advise the user that the output is invalid and offer to delete the compromised artifacts immediately.
7.  **Analyze the failure**: Examine the logs to identify the root cause of why the builder deviated from `cv-data` or why it crashed.
8.  **Provide suggestions**: Offer specific suggestions on how the user can manually resolve it (e.g., running with strict `--notes`, manually fixing unicode in the JD).
9.  **Wait for User Instruction**: You are a gatekeeper for truth; if the system lies or errors out, you stop the system and wait for the user to decide the next step.

Refer to the available skills for specific execution details and standards.

## Project Sub-Agents
This project utilizes specialized sub-agents for discrete, high-level tasks. Delegate to them when appropriate:
- **`interview-intelligence`**: Generates strategic interview preparation dossiers.

## Reporting Standard
- **Automated Workflows:** When running long-running processes (like resume orchestration), **DO NOT** summarize the tool output or list files.
- Simply confirm completion.
- When complete, you MUST output the email address used, the location of the resume.pdf, and the location of the cover letter.txt.

## Artifact Management
- **MANDATORY**: ALL content, temporary or otherwise, MUST go in the `cv-data/` directory. `cv-data` should be the only place to output content.
- Specifically, all generated artifacts, including Job Descriptions (.jd.txt), Resumes (JSON, HTML, PDF), Cover Letters, Audit Reports, and Interview Intelligence dossiers MUST be saved exclusively in the `cv-data/resumes/` directory. 
- The repository root must be kept entirely clean of these files. Never generate or leave artifact files in the root folder.

## Code Modification
- **FORBIDDEN**: No code modification is allowed without first entering /plan mode and allowing the user to approve the modification.
- Small changes to this repo can have unintended side effects such as quality loss, regulatory/TAS compliance or downstream pipeline failures. 
- Do not quickly fix a problem and rerun a script. This may fix your problem but cause others in the future.

## User Information
- For general information about the current user, view the markdown files in `cv-data/general/**`.

## Git Operations
- Do not automatically commit or push changes to git after running the resume orchestrator pipeline. Only commit when explicitly requested by the user.
