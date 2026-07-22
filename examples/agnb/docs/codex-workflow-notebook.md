# Codex Workflow Notebook

This is a concise, living handoff document for starting new Codex
conversations. Review it at the beginning of a session and update it when a
durable workflow convention becomes clear. Do not turn it into a detailed
session log or duplicate project specifications here.

## Working relationship

- Work collaboratively and conversationally. Make reasonable, reversible
  assumptions when they keep the task moving, and call out assumptions that
  could materially affect the result.
- Prefer completing a requested implementation and checking it over merely
  describing the steps.
- Preserve the user's existing and uncommitted work. Inspect repository status
  before edits, commits, or cleanup, and do not fold unrelated changes into a
  commit without agreement.
- Give concise progress updates during longer work. Lead the final report with
  the outcome, important decisions, verification performed, and any remaining
  issue.
- The user may manually move, rename, edit, build, or test files between
  prompts. Reinspect current state rather than assuming it is unchanged.
- Present design work in small, sequential, implementation-sized decisions.
  Do not assume the user has absorbed a complete design document before coding;
  introduce the next relevant constraint when it becomes actionable and work
  through it collaboratively.
- The user may intentionally discover or decide behavior while coding and let
  the code serve as the working specification. Treat that behavior as
  provisional until it is tested and agreed, then distill the durable contract
  into the authoritative specification instead of requiring an up-front,
  exhaustive design pass.

## Documentation roles

The local checkout of the official Agon platform documentation is rooted at:

```text
/home/smith/Agon/agon-docs/docs
```

Use this as the first source for MOS, VDP, API, and platform behavior when
working on Agon projects. Project-specific technical precis documents should
record the exact files consulted and the conclusions relevant to that project.

- **Specification:** the authoritative, normative description of a format or
  interface. Keep it compact and current.
- **Technical precis:** verified platform facts, API behavior, constraints, and
  mappings to relevant source code that will inform implementation.
- **Development log:** chronological session work, experiments, decisions, and
  brief rationale. It may be more detailed while work is exploratory.
- **Environment setup log:** durable machine, editor, toolchain, repository,
  symlink, and deployment setup—not application design work.
- **This notebook:** reusable workflow conventions only.

Avoid repeating the same explanation in several documents. A log should note
that a durable decision was made and point to the authoritative specification
instead of copying the entire decision.

## Keeping context economical

- As requirements stabilize, distill exploratory prose into short,
  authoritative statements.
- Periodically prune obsolete discussion, resolved questions, duplicated
  explanations, and implementation speculation that is no longer useful.
- Use Git history as the normal archive for deleted or superseded prose. Do not
  maintain an `old`, `archive`, or `ignore this` directory merely to retain
  earlier wording; it creates search noise and can be mistaken for current
  guidance.
- Retain a short rejected-alternative note only when its rationale is likely to
  prevent repeating an expensive investigation.
- Preserve substantial experiments, benchmarks, or postmortems when they
  remain useful evidence, clearly labeling their status.
- Mark unfinished material `DRAFT`. Make authoritative documents and unresolved
  questions easy to identify.

## Starting a new conversation

At the start of a fresh session:

1. Read this notebook.
2. Read the current project specification or task document relevant to the
   requested work.
3. Read only the pertinent technical precis and latest development-log entry.
4. Inspect repository status and the relevant source files before changing
   anything.
5. Treat current documents and code as authoritative; consult Git history only
   when the reason for a current decision matters.

Do not reconstruct the entire project from old chat transcripts when the
current documents answer the question.

## Maintaining this notebook

- Add a convention only when it is likely to help across multiple sessions or
  projects.
- Phrase conventions as current guidance, not as a narrative of how they were
  discovered.
- Prune or revise this file as the workflow improves; Git retains its earlier
  versions.
- Other Codex sessions may propose additions after working with the user, but
  they should avoid adding project-specific technical details.
