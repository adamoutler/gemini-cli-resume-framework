# Agentic Tasks & Automation

This directory contains the operational scripts and workflows used by AI agents (and human operators) to maintain, validate, and publish the CV-as-Code artifacts.

## Folder Structure

*   **`Resume_Audit/`**: Tools for verifying the factual integrity of generated resumes against the `cv-data` source of truth.
    *   `audit_resume.py`: The core auditing engine. Uses batch processing and a persistent temporary workspace to validate claims.
*   **`Maintenance/`**: Scripts for repository health and metadata management.
    *   `lint_cv_data.py`: Validates structure and frontmatter of Markdown files.
    *   `fix_metadata.py`: Utilities for batch-correcting frontmatter issues.
*   **`Format_Conversion/`**: Tools for transforming resume data between formats.
    *   `html_to_pdf.py`: Converts the JSON Resume HTML export to PDF.
    *   `json_to_md.py`: Converts JSON resume structures to Markdown summaries.
*   **`LinkedIn/`**: Workflows for LinkedIn profile automation (e.g., project uploads).

## Temporary Workspace Policy

To keep the repository clean and git-history pristine, all transient files, logs, and intermediate processing artifacts **MUST** be stored in the system temporary directory.

**Standard Location:** `/tmp/gemini_cv_audit/`

*   **Logs:** Debug logs (e.g., `audit_debug.log`) should be written here.
*   **Checkpoints:** Long-running tasks (like resume audits) should save their state (e.g., `checkpoint_findings.json`) here to allow resumption after interruptions.
*   **Intermediate Files:** Any JSON fragments or raw model outputs used during processing should be stored here and cleaned up if necessary.

**Do NOT** create log files or temporary artifacts in the project root or subdirectories unless they are intended to be committed as permanent records (e.g., a final `audit_report.md` requested by the user).
