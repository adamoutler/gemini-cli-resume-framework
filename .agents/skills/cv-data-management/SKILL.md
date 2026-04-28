---
name: cv-data-management
description: CV Building Mode. Guidelines for adding new professional experience, projects, or skills to the cv-data repository.
---

>>>
CRITICAL INSTRUCTION: There are model and runtime-specific variances for agents running in this environment.  If you are a Gemini Agent in Gemini CLI, you will use Gemini_Tasks.  If you are an OpenAI Agent running under Codex, you will use Codex_Tasks.
>>>

# CV Data Management (CV Building Mode)

This workflow ensures new artifacts in the `cv-data/` directory are high-quality, fact-based, and indexable.

## File Standards
- **Format:** Markdown (`.md`).
- **Voice:** 3rd Person, Objective/Journalistic (e.g., "The Candidate architected...").
- **Location:** Place new files in the appropriate subdirectory of `cv-data/`.

### Media Mentions & Articles
- **Body Content:** MUST contain the **FULL TEXT** of the article. Do not summarize the content in the body.
- **Summary:** The summary must be placed **strictly** in the JSON FrontMatter `summary` field.

## Mandatory JSON FrontMatter
Every file must start with a JSON FrontMatter block for indexing:

```markdown
---
{
  "title": "Project Review: <Project Name>",
  "summary": "A concise (2-3 sentence) overview.",
  "keywords": ["Skill 1", "Skill 2"],
  "date": "YYYY-MM-DD", 
  "document_type": "Project Review", 
  "domain": "Software Engineering"
}
---
```

## Validation
Run the linter after any modification:
```bash
python3 AGENT_Tasks/Maintenance/lint_cv_data.py
```
