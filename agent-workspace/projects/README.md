# projects

Contains configuration pointing to the active projects the agent works on.

## Files

```text
projects/
├── README.md
└── PROJECTS.md
```

`PROJECTS.md` contains the filesystem paths to one or more active projects.

## PROJECTS.md example

````markdown
# Projects

## Paths

```text
/home/user/projects/my-project
/home/user/projects/another-project
````

````

On Windows:

```markdown
# Projects

## Paths

```text
D:/Projects/my-project
D:/Projects/another-project
````

```

Each path represents the canonical root of an active project.

The file may contain one or multiple project paths.

## Rules

- The agent MUST read `PROJECTS.md` before accessing any project source code.
- Every path defined in `PROJECTS.md` is a canonical project root.
- `PROJECTS.md` MAY contain multiple project paths.
- The actual projects may be located anywhere on the local filesystem.
- Each project repository is independent from the `agent-workspace` repository.
- The agent MUST determine which configured project is relevant before accessing or modifying its source code.
- The agent MUST NOT assume that the first path in `PROJECTS.md` is the target project unless the context clearly indicates it.
- `PROJECTS.md` should remain minimal and should contain only information required to locate active projects.
- `PROJECTS.md` should not contain architecture, conventions, notes, plans, decisions, or other project knowledge.
- Project-specific knowledge belongs in `../prompts/`, `../memory/`, `../plans/`, `../decisions/`, and other workspace directories — not in `PROJECTS.md`.
```
