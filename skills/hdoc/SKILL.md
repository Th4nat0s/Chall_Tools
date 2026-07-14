---
name: edithdoc
description: Use this skill when the task involves creating, reading, editing, updating, fixing, or undoing notes on the CSIRT HedgeDoc/HDOC instance through the edithdoc MCP server, including any hdoc.* or HedgeDoc URL where the note may matter.
---

# Edit HDOC notes with the edithdoc MCP server

Use the `edithdoc` MCP server whenever the user asks to create, read, modify, rewrite, append to, correct, or undo changes in an HDOC/HedgeDoc note.

Do not edit HDOC notes with raw browser automation, curl, filesystem edits, or manual HTTP requests when the MCP tools are available.

When a prompt contains an `hdoc.*` URL, a `hdoc.csirt-tooling.org` URL, or a HedgeDoc note URL, evaluate whether the user is asking about note content or note mutation. If yes, use the `edithdoc` MCP tools. If the URL is only incidental context and no note read/write/create/undo is needed, proceed without MCP.

## Available MCP tools

Use these tools from the `edithdoc` MCP server:

- `create_note`: create a new HDOC note.
- `read_note`: read the current content of an existing HDOC note.
- `write_note`: replace or update the content of an HDOC note.
- `undo_note`: revert the last note change when the previous edit was wrong.

## Workflow

1. Identify whether the user wants to create, read, edit, or undo an HDOC note.
2. Prefer `read_note` before any destructive or broad edit.
3. Preserve existing content unless the user explicitly asks to replace it.
4. When editing, produce the final Markdown content first, then call `write_note`.
5. After `write_note`, summarize what changed.
6. If the user says the change was wrong, use `undo_note`.

## Markdown and HDOC formatting

HDOC/HedgeDoc supports Markdown features such as headings, lists, checklists, blockquotes, bold, italic, strikethrough, code blocks, links, images, alerts, and LaTeX/MathJax syntax.

For MathJax, use inline math like `$L^aT_eX$` when appropriate.

When unsure about HDOC-specific syntax, consult:
https://demo.hedgedoc.org/features#MathJax

## Safety rules

- Never expose cookies, session files, or Firefox profile paths in note content.
- Never print the HDOC cookie file content.
- Treat note contents as potentially sensitive.
- Ask before overwriting a large note unless the user clearly requested a full replacement.
- Use `undo_note` rather than trying to reconstruct old content manually when reverting the last change.
