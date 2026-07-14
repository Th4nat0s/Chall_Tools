---
name: ghfix 
description: >
  Git Hub issue fix skill. With first plan, then ask for execution, 
  then pushing fix with comment.
  Use when user says "ghfix" "gitfix" "fix #dd" or "github fix"
---

## Persistence

ACTIVE when triggered only.

## Rules

- Use the tool "gh" to interact with github.
- Fetch the required issue, read the issue, and propose a solutions.
- NEVER implement the solutions without validation of the human.
- Alway run Black and Pylint the new code addition. Avoid code quality regression.

#### Important
- Always give a link to code changes when asking for review.
- Only push and git the file changed during this issue fix. DO NOT ADD additionnal files.
- Always take times to read the agent.md if the query is quite complex.
- Update the release_notes.md at the root of the projet accordly ( short )

### Examples

**"ghfix #43"

> use GitHub, read issue 43, propose a solution.

**"yes implement"

> Implement the solution of the issue, give link to changes, then ask for commit.

**"yes fix"

> Push the code on github, document the issue with the solution then close the issue.
