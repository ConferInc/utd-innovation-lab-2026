# Team 4B Git Workflow (Week 8/9)

This document outlines commit conventions and expectations for Team 4B to maintain clean and reviewable pull requests.

## Commit Prefix Format

All commits must follow this structure:

- feat(scope): new feature
- fix(scope): bug fix
- docs(scope): documentation changes
- test(scope): test-related updates

### Examples

- fix(stripe): resolve webhook import crash
- docs(demo): add demo script
- test(stripe): verify webhook behavior

## Commit Rules

- No duplicate commit messages in the same PR
- One commit per logical change (not per file save)
- Avoid vague messages like "update" or "fix stuff"
- Always test locally before committing

## PR Expectations

Before raising a PR:
- Clean up commit history (squash duplicates)
- Ensure commits are meaningful and readable
- Confirm app runs locally if relevant

Git history should clearly reflect what was changed and why.