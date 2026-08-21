# AGENTS.md - Agent Instructions & Workspace Guidelines

## Core Interaction & Coding Guidelines

See `.agents/rules/agent-instructions.md` for full guidelines.
- **Verification First:** Query DB/files with tools before answering. No guessing.
- **Surgical Edits:** Minimal, targeted changes without placeholders (`// TODO`). Preserve comments & docstrings.
- **High Signal:** Concise, direct output with clear markdown tables and file links.
- **Root Cause Analysis:** Diagnose before patching.

## Agent skills

### Issue tracker
GitHub Issues is used as the issue tracker for this repository. See `docs/agents/issue-tracker.md`.

### Triage labels
The canonical triage label vocabulary is used (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs
Single-context layout: `CONTEXT.md` and `docs/adr/`. See `docs/agents/domain.md`.
