---
name: ats-optimization
description: Strict rules for ensuring generated resumes are parsable by Applicant Tracking Systems (ATS).
---

# ATS Optimization Rules

Follow these rules when tailoring resumes to ensure maximum compatibility with older parsers.

## Reference Guides
For deep technical constraints and schema mapping, refer to:
- `references/ATS Resume Field Compatibility Research.md`: Detailed research on parser behaviors.
- `references/JSON Resume ATS Optimization Guide.md`: Advanced optimization strategies for specific profiles.
- `related-requirements/ATS_Resume_Schema.json`: Technical constraints for field names and date formats.

## Parsing Safety
- **No Multi-Column Layouts:** Ensure the template (like 'stackoverflow') renders in a clear vertical flow.
- **No Graphics/Tables:** Avoid complex tables or icons in summary/project fields.
- **Plain Text Only:** (Mandatory) No markdown syntax (`**`, `*`, `[]()`) in JSON fields.
- **Standard Headers:** Use standard terminology (e.g., "Work Experience").

## Keyword Strategy
- **Literal Matching:** Use exact phrasing from the JD for relevant experience.
- **Noun Density:** Prioritize technical nouns (e.g., "CI/CD", "AWS EC2") over soft-skill adjectives.
- **Title Alignment:** Ensure the target job title or a close variant is prominent.

## Sanitization
- Use standard hyphens `-` or asterisks `*` for bullets.
- Write out URLs (e.g., `github.com/[Username]`) instead of using anchors if necessary.
