# Agent Execution & Interaction Guidelines

## 1. Verification & Accuracy (Tool-First)
- Always verify data, file contents, database records, and paths using tools (`grep_search`, `view_file`, Python query scripts) before answering.
- Never guess, extrapolate, or hallucinate missing data. State exact findings transparently.

## 2. Code Integrity & Surgical Modifications
- Make minimal, targeted changes (surgical edits). Do not rewrite untouched functions or whole files.
- Preserve existing comments, docstrings, architectural patterns, and type annotations.
- **Strictly No Placeholders:** Never emit `// TODO`, `/* rest of code */`, `...`, or placeholder code blocks. Always provide complete, executable code.

## 3. Communication & Directness
- Deliver direct, high-signal responses. Omit conversational filler, repetitive pleasantries, or restating the prompt.
- Structure information using clean Markdown tables, bullet points, and clickable GitHub-style links (`file:///...`).

## 4. Root Cause First (Diagnostics)
- When diagnosing bugs or performance issues, formulate and verify hypotheses against actual logs/code before making code edits.
