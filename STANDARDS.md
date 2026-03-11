# Standards & Conventions

This document defines the coding standards, naming conventions, and documentation requirements for the UTD Innovation Lab 2026 project.

---

## 📝 General Principles

1. **Clarity over cleverness** — Write code that others can understand
2. **Consistency** — Follow these standards across all work
3. **Documentation** — Document your decisions and reasoning
4. **Version control** — Every significant change should be committed

---

## 📁 File & Folder Naming

### Naming Convention: `kebab-case`

✅ **Good:**
```
weekly-summary.md
user-authentication.js
database-schema.sql
```

❌ **Avoid:**
```
Weekly Summary.md      # Spaces
userAuthentication.js  # camelCase for files
Database_Schema.sql    # Mixed case
```

### Folder Structure

Each student folder should follow this structure:

```
[student-name]/
├── README.md                    # Personal overview
├── weekly-summaries/            # Weekly progress reports
│   ├── 2026-02-20-week-1.md
│   ├── 2026-02-27-week-2.md
│   └── ...
├── research/                    # Research notes and findings
│   └── [topic-name].md
├── designs/                     # Diagrams, mockups, wireframes
│   └── [feature-name].png
└── code/                        # Code samples, prototypes
    └── [experiment-name]/
```

---

## 💻 Code Standards

### Markdown Documentation

- Use proper heading hierarchy (`#` → `##` → `###`)
- Include a brief description at the top of each document
- Use code blocks with language tags: ```python, ```javascript, ```bash
- Keep lines under 100 characters when possible

### Python (if used)

- Follow [PEP 8](https://pep8.org/)
- Use 4 spaces for indentation
- Maximum line length: 88 characters (Black formatter default)
- Docstrings for functions and classes

```python
def calculate_mortgage_payment(principal, rate, term):
    """
    Calculate monthly mortgage payment.
    
    Args:
        principal: Loan amount in dollars
        rate: Annual interest rate (decimal)
        term: Loan term in years
    
    Returns:
        Monthly payment amount
    """
    # Implementation
```

### JavaScript/TypeScript (if used)

- Use 2 spaces for indentation
- Prefer `const` and `let` over `var`
- Use meaningful variable names

```javascript
// Good
const calculateMonthlyPayment = (principal, annualRate, years) => {
  const monthlyRate = annualRate / 12;
  const numPayments = years * 12;
  // ...
};

// Avoid
function calc(p, r, t) {
  var mr = r / 12;
  // ...
}
```

### SQL

- Use uppercase for keywords
- Indent subqueries
- Use meaningful table and column names

```sql
SELECT 
    customer_id,
    first_name,
    last_name
FROM customers
WHERE created_at >= '2026-01-01'
ORDER BY created_at DESC;
```

---

## 📊 Diagrams & Visuals

### Tools Recommended

- **Architecture diagrams:** Draw.io, Lucidchart, Mermaid
- **Wireframes:** Figma, Balsamiq
- **Flowcharts:** Mermaid, Draw.io

### Export Format

- Save diagrams as **PNG** or **SVG**
- Include source files (`.drawio`, `.fig`) when possible
- Place in `designs/` folder with descriptive names

---

## 🗂️ Documentation Standards

### README.md (Personal)

Each student should maintain a `README.md` in their folder with:

```markdown
# [Your Name]

**Group:** 4A or 4B  
**Email:** your.email@UTDallas.edu  
**GitHub:** @yourusername

## Weekly Summaries
- [Week 1 — Feb 20, 2026](weekly-summaries/2026-02-20-week-1.md)
- [Week 2 — Feb 27, 2026](weekly-summaries/2026-02-27-week-2.md)

## Current Focus
Brief description of what you're working on.

## Research Areas
- Area 1
- Area 2
```

### Weekly Summaries

Use the template in [`WEEKLY_TEMPLATE.md`](WEEKLY_TEMPLATE.md) and save as:
```
weekly-summaries/YYYY-MM-DD-week-N.md
```

---

## ✅ Checklist for All Submissions

Before committing any work:

- [ ] File names use `kebab-case`
- [ ] Document has a clear title and description
- [ ] Code examples are properly formatted
- [ ] No sensitive data (API keys, passwords) is included
- [ ] Spelling and grammar checked
- [ ] Links are functional

---

## 🔄 Version Control

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for detailed Git workflow.

Quick reference:
- Commit messages: `type: brief description`
- Types: `feat:`, `fix:`, `docs:`, `research:`, `design:`
- Example: `docs: add week 3 summary and API research`

---

*Last updated: February 2026*
