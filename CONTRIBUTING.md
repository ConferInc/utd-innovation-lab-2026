# Contributing Guidelines

How to contribute your work to the UTD Innovation Lab 2026 repository.

---

## 🔄 Git Workflow

### 1. Clone the Repository

```bash
git clone https://github.com/confersolutions/utd-innovation-lab-2026.git
cd utd-innovation-lab-2026
```

### 2. Create a Branch (Optional but Recommended)

For significant changes, create a branch:

```bash
git checkout -b yourname-weekly-update
```

For small updates, working on `main` is acceptable.

### 3. Make Your Changes

Work in your assigned folder only:
- `4A/[your-folder]/` for Group 4A
- `4B/[your-folder]/` for Group 4B

### 4. Commit Your Changes

```bash
git add .
git commit -m "type: description"
```

### 5. Push to GitHub

```bash
git push origin main
# or if using a branch:
git push origin yourname-weekly-update
```

---

## ✍️ Commit Message Format

Format: `type: brief description`

### Types

| Type | Use for |
|------|---------|
| `feat:` | New features or significant additions |
| `fix:` | Bug fixes or corrections |
| `docs:` | Documentation updates |
| `research:` | Research findings, notes, analysis |
| `design:` | Diagrams, mockups, wireframes |
| `update:` | General updates to existing content |

### Examples

```bash
docs: add week 3 weekly summary
research: API comparison for WhatsApp Business
feat: add mortgage calculator prototype
design: update system architecture diagram
fix: correct spelling in week 2 summary
```

### Best Practices

- Keep first line under 50 characters
- Use imperative mood: "add" not "added"
- Be specific: `docs: add week 3 summary` not `docs: update`

---

## 📤 Weekly Summary Submission Process

### Step-by-Step

1. **Create your weekly summary** using [`WEEKLY_TEMPLATE.md`](WEEKLY_TEMPLATE.md)
2. **Save as:** `weekly-summaries/YYYY-MM-DD-week-N.md`
3. **Commit:**
   ```bash
   git add weekly-summaries/2026-02-20-week-1.md
   git commit -m "docs: add week 1 summary"
   git push origin main
   ```
4. **Notify your team lead** that you've pushed your summary

### Team Lead Responsibilities

Team leads (Rujul for 4A, Sysha for 4B) should:
1. Review team members' weekly summaries
2. Compile into a team-level summary
3. Submit to `students@mail.confersolutions.ai` by **Thursday EOD**

---

## ⚠️ What NOT to Commit

### Never Commit

- API keys or secrets
- Passwords or credentials
- Personal information of real customers
- Large binary files (>10MB) without discussion
- Node_modules, `__pycache__`, or other dependency folders

### Use .gitignore

The repository includes a `.gitignore` file. If you need to ignore additional files:

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.log" >> .gitignore
```

---

## 🔍 Code Review

### Self-Review Checklist

Before pushing:
- [ ] I've read the changes I'm committing
- [ ] No sensitive data is included
- [ ] File names follow `kebab-case`
- [ ] Documents are properly formatted
- [ ] Commit message follows the format

### Team Lead Review

Team leads should:
- Check that weekly summaries are complete
- Verify students are following standards
- Provide feedback if needed

---

## 🆘 Getting Help

### Git Issues

If you encounter merge conflicts or other Git issues:

1. **Don't panic** — conflicts are normal
2. **Ask your team lead** for help first
3. **Document the issue** if you need to escalate

### Common Commands

```bash
# Check status
git status

# See what changed
git diff

# Undo uncommitted changes
git checkout -- filename

# See commit history
git log --oneline -10

# Pull latest changes
git pull origin main
```

---

## 📧 Communication

### For Questions About:

| Topic | Contact |
|-------|---------|
| Repository access | Shrikanth (shrikanth@mail.confersolutions.ai) |
| Project requirements | Sivram (sivram@mail.confersolutions.ai) |
| Weekly assignments | Team lead → students@mail.confersolutions.ai |
| Course-related | Professor Garapaty or TA Yidi Li |

---

## 🎯 Goals

This workflow ensures:
1. **Transparency** — All work is visible to the team
2. **Accountability** — Clear tracking of contributions
3. **Learning** — Practice industry-standard Git workflows
4. **Documentation** — Project history is preserved

---

*Last updated: February 2026*
