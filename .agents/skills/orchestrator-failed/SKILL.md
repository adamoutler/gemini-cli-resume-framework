---
name: orchestrator-failed
description: Protocol for handling resume orchestrator failures. STRICTLY prohibits completion of failed jobs and mandates user-driven corrective actions.
---

# Orchestrator Failure Protocol

This skill is activated when the resume orchestrator script fails to complete successfully.

## Context

A failure indicates that the system has attempted to generate and validate the resume **5 times in a row** and has failed to reach a passing state. This suggests one of the following:
*   **Conflicting Information:** The generated content contradicts the source of truth.
*   **Incomplete Information:** The source data lacks the necessary evidence to support the claims.
*   **Flawed System:** The Personas (Builder, Auditor, Reviewer) or the Orchestrator script are malfunctioning or misaligned.

## Core Mandate

**You must NEVER complete the job if the orchestrator fails.**

## Procedure

1.  **Analyze Logs:** Read the execution logs to determine the specific cause of failure (e.g., persistent factual inconsistencies, missing keywords, schema violations).
2.  **Trace Root Cause:** Identify the source of the problem.
    *   **Hallucination:** Did the LLM invent facts?
    *   **Input Data:** Is the CV data missing required skills or experience?
    *   **Persona:** Is a persona instruction too strict, ambiguous, or incorrect?
    *   **Script/Orchestration:** Is there a bug in the automation logic?
3.  **Determine Least Impactful Solution:** Evaluate potential fixes and their side effects (e.g., weakening validation rules vs. fixing data).
4.  **Present Options to User:** You must **not** take proactive corrective action. Instead, present the findings and example options to the user.
    *   **Option 1:** Update CV Data (e.g., Add missing skills or evidence to the source files).
    *   **Option 2:** Update Persona/Reviewer Instructions (e.g., Relax constraints or clarify prompts).
    *   **Option 3:** Update Orchestration Logic (e.g., Fix bugs in the script or workflow).
5.  **Await Decision:** Take no action until the user selects a path.

**It is better to produce no resume and make no changes than to give the user a flawed resume, or potentially cause flaws in all future resumes.**
