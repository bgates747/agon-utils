# Task records

`../../TODO.md` resolves to `examples/mos-tests/TODO.md` at the subproject
root and is the authoritative unfinished-task index for MOS tests. The
agon-utils repository root does not own this subproject's task index.
Each task has a
`<ID>.md` detail record containing state, intent, categorized subtasks, acceptance criteria,
and evidence. Task records own subtask status; TODO indexes tasks without
copying their subtask checklists.

## Durable subtasks

1. Use literal, immutable identifiers followed by a checkbox, for example
   `- W01 [ ] Description`. `Work` with W01..Wnn is a convenient default,
   not a required or exclusive category. A task may define multiple named
   categories with distinct local prefixes, such as Investigation (I01..Inn),
   Work (W01..Wnn), and Validation (V01..Vnn).
2. Define prefixes within the owning task only. Identifiers must be unique
   within that task; other tasks may reuse the same prefixes and numbers.
   There is no global subtask namespace or registry. Do not use Markdown-generated
   numbering, renumber, reuse, or delete an existing subtask identifier. Allocate
   the next unused number in its category when adding work. References outside
   the task can link to its document and name the local ID without creating a
   globally managed identifier.
3. Use `[ ]` for unfinished work and `[x]` for disposed work. For every checked
   item, explicitly record **Completed**, **Deferred**, or **Canceled**, with
   rationale and evidence or a follow-on task reference as applicable. A checked
   box alone does not mean the work was successfully completed.
4. Subtask wording may be modified in place, but retain the identifier and
   disposition history. Never delete a subtask after creation, including after
   completion, deferral, or cancellation; log material scope changes.
5. Keep acceptance criteria as requirements rather than a second subtask list.
   Closing a task removes its entry from TODO after recording the decision in
   the dated development log; its task record and subtasks remain intact.

## Task silos and promotion

1. Promote work into TODO before starting it.
2. Use `docs/tasks/<ID>/` for experiments, trials, provisional code, scripts,
   documents, and evidence. Separate individual trials into bounded directories
   when useful so their inputs and results remain auditable.
3. When outputs mature, promote maintained code, scripts, or documents into
   subject-named locations in the subproject mainspace. Update consumers and
   links, and retain provenance in the task record. Routine operation should
   not depend on a historical task directory.
4. Record decisions, validation, and dispositions in dated development logs.

The task-silo layout follows `agon-extender/docs/tasks`; permanent task-local subtask IDs
and disposition rules reflect the Author's project-specific instructions.
