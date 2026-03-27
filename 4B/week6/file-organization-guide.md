# File Organization Guide — Team 4B

This document defines conventions for the 4B folder structure and where to place files.

---

## Week Folder Structure

| Week   | Purpose                                              | Notes                    |
| ------ | ---------------------------------------------------- | ------------------------ |
| week1  | Marketing intelligence, UX strategy, perplexity logs | Renamed from "Week 1"    |
| week2  | —                                                    | No folder (no git tasks) |
| week3  | Engineering baseline (bot modules)                    | Keep as-is               |
| week4  | Integration sprint archive                           | ASSIGNMENT.md + README   |
| week5  | Production bot (Twilio, auth, wrappers, etc.)        | Current deployment       |
| week6  | Escalations, docs, file-organization guide           | Week 6 deliverables      |

---

## Student Folder Structure

Each Team 4B member folder should follow:

```
[student-name]/
├── README.md
├── logs/
│   ├── week-1/
│   ├── week-2/
│   ├── week-3/
│   ├── week-4/
│   ├── week-5/
│   └── week-6/
├── weekly-summaries/         # Optional; per STANDARDS
└── research/                 # Optional; per STANDARDS
```

### logs/week-N/ Convention

- Store all logs (Perplexity exports, transcripts, session notes) in `logs/week-N/` for the relevant week.
- Use consistent naming: `week-1`, `week-2`, etc.

### Rule: No Production Code in Name Folders

- Production code belongs in team week folders (`4B/week3/`, `4B/week5/`, etc.).
- Use `4B/[your-name]/` only for: README, logs, weekly-summaries, research.
- Do not duplicate bot modules, integrations, or database code in name folders.

---

## Branch Naming

- `feature/week6-<name>-<task>` for individual work
- Merge flow: individual branch → `team-4B-week6` (or `group-4b/week6`) → PR to main

---

## Naming Conventions

- File names: `kebab-case`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
