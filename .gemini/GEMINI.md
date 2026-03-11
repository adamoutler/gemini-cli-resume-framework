# CV-as-Code Agent Manual

This repository is a structured database of professional experience. It uses automated workflows to generate tailored resumes and cover letters.

## Repository Overview
- **`cv-data/`**: The central markdown database (private).
- **`Agentic_Tasks/`**: Automated workflows and tools.
- **`cv-data/resumes/`**: Output directory for generated artifacts.

## Prerequisites
- **Node.js**: Required for `resume-cli`.
- **Python 3**: Use `./venv/bin/python3` for all scripts.
- **Setup**: `npm install && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`.
- **ASCII Mandate**: All generated artifacts MUST be strictly plain ASCII.
    - Sanitize all non-ASCII (smart quotes, accents, Cyrillic, etc.) to visual or transliterated ASCII equivalents (e.g., using `unidecode`).
    - If no clear equivalent exists, contextually rephrase or omit the character/word to maintain professional flow and correctness.

## Core Mandate
Always utilize the automated orchestrator for resume generation tasks. Do not build JSON files manually or manually execute steps of the pipeline (e.g., manual PDF rendering or cover letter generation) if the pipeline fails or times out. The pipeline is designed to generate all required outputs autonomously. 

If the pipeline fails or the end of the workflow is not detected:
1.  **Analyze the failure:** Examine logs and tool outputs to identify the root cause.
2.  **Provide suggestions:** Report the failure to the user and offer specific suggestions on how to resolve it.
3.  **No autonomous alterations:** Do not attempt to fix the agentic pipeline code or bypass it with manual actions without explicit user instruction.

Refer to the available skills for specific execution details and standards.

## Project Sub-Agents
This project utilizes specialized sub-agents for discrete, high-level tasks. Delegate to them when appropriate:
- **`interview-intelligence`**: Generates strategic interview preparation dossiers.

## Reporting Standard
- **Automated Workflows:** When running long-running processes (like resume orchestration), **DO NOT** summarize the tool output or list files.
- Simply confirm completion.

## Artifact Management
- **MANDATORY**: ALL content, temporary or otherwise, MUST go in the `cv-data/` directory. `cv-data` should be the only place to output content.
- Specifically, all generated artifacts, including Job Descriptions (.jd.txt), Resumes (JSON, HTML, PDF), Cover Letters, Audit Reports, and Interview Intelligence dossiers MUST be saved exclusively in the `cv-data/resumes/` directory. 
- The repository root must be kept entirely clean of these files. Never generate or leave artifact files in the root folder.

## User Information
- For general information about the current user, view the markdown files in `cv-data/general/**`.
