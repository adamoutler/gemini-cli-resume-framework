# Codex Workspace Rules

This repository is split into two agent-owned areas:

- `Codex_Tasks/` is the Codex-owned workspace.
- `Agentic_Tasks/` is the Gemini-owned workspace and is out of scope for Codex edits unless the user explicitly overrides that boundary.

Codex must not modify files under `Agentic_Tasks/` by default.

Preferred operating rules:

- Make Codex-side changes in `Codex_Tasks/` or repo-root configuration files only.
- Treat `Agentic_Tasks/` as read-only unless the user explicitly asks for a change there.
- If a task seems to require `Agentic_Tasks/`, stop and confirm with the user before editing.
- Keep Codex workflow docs and helper scripts aligned with Codex-side behavior.

This boundary exists to prevent cross-agent collisions when Gemini and Codex are working in the same repository.
