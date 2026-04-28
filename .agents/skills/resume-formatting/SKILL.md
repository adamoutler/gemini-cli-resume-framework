---
name: resume-formatting
description: Guidelines and constraints for JSON Resume generation and rendering. Use this when editing or validating resume data.
---

>>>
CRITICAL INSTRUCTION: There are model and runtime-specific variances for agents running in this environment.  If you are a Gemini Agent in Gemini CLI, you will use Gemini_Tasks.  If you are an OpenAI Agent running under Codex, you will use Codex_Tasks.
>>>

# Resume Formatting Guidelines

## JSON Resume Standards

- **Plain Text Only:** Absolutely no markdown formatting (bold, italics, links, etc.) is allowed in any fields within the JSON file.
- **Schema Compliance:** Must adhere to the JSON Resume schema (as validated in Phase 3 of the orchestrator).

## Reference Materials

Consult these files for deep validation and formatting rules:

- **ATS Optimization:**
  - `references/ATS Resume Field Compatibility Research.md`: Core research on parsing rules and field compatibility.
  - `references/JSON Resume ATS Optimization Guide.md`: Advanced guide for optimizing content for ATS systems.
  - `related-requirements/ATS_Resume_Schema.json`: Strict schema optimized for parsing fidelity.

- **Schema Definitions:**
  - `related-requirements/Official_JSON_Resume_Schema_v1.0.0.json`: The base standard schema.
  - `related-requirements/Standard_JSON_Resume_Schema.json`: "Kitchen Sink" example showing all possible fields.
  - `references/Comprehensive JSON Resume Schema Example.md`: Detailed analysis and implementation guide.

## Rendering & Export

- **Theme:** The only authorized theme is **'stackoverflow'**. Other themes (paper, flat, etc.) are deprecated.
- **Format:** The final deliverable is always a **PDF**. HTML is used as an intermediate step for rendering.
- **Page Limits:** Resumes should be optimized for length (enforced via `AGENT_Tasks/Maintenance/enforce_page_limit.py` during orchestration).

## Maintenance Tools

- `AGENT_Tasks/Maintenance/lint_cv_data.py`: Check for errors in the source CV data.
- `AGENT_Tasks/Resume_Audit/fix_resume_structure.py`: Repair structural issues in JSON files.
