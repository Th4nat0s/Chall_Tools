---
name: github-issue-writer
description: Analyze a problem description against the current repository, draft a repository-aware GitHub issue in English, and create it using the GH tool. Use when the user enters `ghissue` or `ghadd` followed by a problem description; quotation marks are optional when the remaining input is one description.
---

# GitHub Issue Writer

## Commands

Trigger only for:

```text
ghissue "<problem description>"
ghadd "<problem description>"
```

`ghissue` and `ghadd` are strict aliases and must execute the same workflow. Treat everything after the command as the raw problem description. Reject requests with no meaningful problem description.
Depending of the repo where this skill is requested it could be GitHub or Forjeo. Determine it at the begining and use the right tool "GH" or "FJ".

## Language

Write the generated issue title and body in clear technical English, regardless of user language. Do not translate or rewrite repository identifiers such as file paths, function names, class names, variable names, config directives, API fields, command names, or project names.

## Required Tooling

Use the GH tool for all GitHub and repository operations:

- Identify the current repository, owner, name, default branch, and current branch or revision when available.
- Inspect repository files and directories.
- Search relevant code, symbols, config, tests, docs, scripts, automation, dependency manifests, and CI workflows.
- Read relevant implementation files.
- Search open and closed GitHub issues and pull requests.
- Identify duplicates, related work, dependencies, sibling issues, and existing implementations.
- Create the final GitHub issue.

Do not create or modify repository files. Do not use generic web search as a replacement for GH-backed repository inspection.

## Workflow

1. Parse the command alias and complete problem description. Extract explicit constraints, expected behavior, affected components, and acceptance requirements.
2. Identify the repository with GH. Stop if owner, repo, or default branch cannot be confirmed.
3. Search related issues and PRs with important terms from the description, relevant file names, symbols, error messages, and config directives.
4. Do not create a duplicate when an equivalent active issue exists. If likely duplicate equivalence is uncertain, report it instead of creating a new issue.
5. Inspect current repository implementation through GH. Confirm current behavior, abstractions, conventions, validation, error handling, tests, docs, operational constraints, and compatibility requirements.
6. Classify required change: new code, modified code, removal, refactor, config, deployment, infrastructure, DB/schema, API, docs, tests, monitoring, migration, or rollback.
7. Analyze relevant risks only: compatibility, security, authn/authz, data integrity, resource use, concurrency, performance, failure handling, deployment safety, rollback, platform support, and test coverage.
8. Draft concise English title and structured Markdown body using the required template.
9. Create the issue with GH only when repository identification, repo inspection, duplicate checks, and authorization all succeed.

Use concrete repository evidence. Do not invent paths, symbols, runtime behavior, deps, tests, infrastructure, issue numbers, or PR numbers.

## Issue Template

```markdown
## Problem

Describe the current implementation and the observed or expected problem.

Reference confirmed repository paths, modules, functions, configuration directives or code paths.

Explain why the current behavior is problematic, including relevant operational, security, performance, reliability, compatibility or maintenance impact.

Distinguish confirmed behavior from assumptions that still require validation.

## Proposed approach

Describe the recommended implementation approach based on the current repository.

State whether the work requires:

- New code.
- Modification of existing code.
- Configuration changes.
- Refactoring.
- Documentation.
- Tests.
- Deployment or migration work.

Explain the important technical decisions and constraints.

Do not prescribe arbitrary limits, timeouts, budgets, concurrency values or thresholds without repository evidence, measurements or explicit user requirements.

Values requiring production measurements must be described as provisional.

## Scope

- List the concrete implementation work.
- Identify affected files or components when confirmed.
- Reuse existing repository abstractions and conventions where applicable.
- Add or update automated tests.
- Add or update documentation.
- Include deployment, migration, monitoring and rollback work when relevant.
- Identify behavior that must remain unchanged.
- Explicitly state important work that is outside the scope.

## Acceptance criteria

- Use observable and verifiable conditions.
- Describe the expected runtime or user-visible behavior.
- Verify successful behavior.
- Verify relevant failure cases.
- Verify edge cases.
- Include automated test expectations.
- Include security, compatibility, performance or resource measurements when relevant.
- Confirm that unrelated application behavior remains unchanged.
- Confirm that rollback or recovery steps are documented when relevant.

## Dependencies

List confirmed blocking or related:

- Issues.
- Pull requests.
- Infrastructure changes.
- Database migrations.
- External services.
- Design decisions.
- Deployment requirements.

Write `None identified` when no dependency can be confirmed.
```

## Title Rules

The title must be English, concise, outcome-oriented, and mention the affected component when known. Use imperative or action-oriented form when appropriate. Avoid vague titles such as `Fix issue`, `Improve code`, or `Update configuration`. Avoid issue numbers unless referencing a confirmed dependency.

## Quality Rules

The issue must:

- Be grounded in repository evidence.
- Use precise technical terminology.
- Be implementation-oriented.
- Contain measurable acceptance criteria.
- Preserve relevant existing behavior.
- Mention tests and documentation.
- Include rollback requirements when operational changes are involved.
- Include confirmed file paths and symbols only.
- Separate confirmed facts, proposed decisions, values requiring measurement, and open technical questions.

The issue must not:

- Merely translate the input.
- Copy raw input without analysis.
- Invent repository details.
- Include conversational introductions.
- Mention AI generation.
- Include internal reasoning or tool execution details.
- Use vague acceptance criteria such as `Works correctly`, `Handles errors`, `Is optimized`, or `Is production ready`.

## Result Format

After successful creation, return only:

```text
Created issue #<number>: <url>
```

When no issue is created, return a concise blocking reason and include any relevant existing issue or PR reference found through GH.
