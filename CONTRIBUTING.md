# Contributing to DataVyn Labs

Thank you for your interest in contributing to **DataVyn** — the automated data intelligence platform by DataVyn Labs. We welcome contributions of all kinds, from bug fixes and documentation improvements to new features and integrations.

Please take a few minutes to read this guide before opening an issue or submitting a pull request.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [How to Contribute](#how-to-contribute)
- [Branch Naming](#branch-naming)
- [Commit Messages](#commit-messages)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Style Guide](#style-guide)
- [Contact](#contact)

---

## Code of Conduct

All contributors are expected to uphold our community standards. Be respectful, constructive, and collaborative. Harassment, discrimination, or disruptive behaviour of any kind will not be tolerated.

---

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip
- Git

### Local Setup

```bash
# 1. Fork the repository on GitHub, then clone your fork
git clone https://github.com/datavynlabs/datavyn.git
cd datavyn

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The app will be available at `http://localhost:8501`.

---

## Project Structure

```
datavyn/
├── app.py                  # Entry point — page config and tab routing
├── style.css               # Global dark theme
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Streamlit server config
└── modules/
    ├── state.py            # Centralised session state
    ├── sidebar.py          # Sidebar — stats, settings, API key
    ├── overview.py         # Landing page
    ├── upload.py           # File upload and parsing
    ├── charts.py           # Plotly chart engine
    ├── kaggle_connect.py   # Kaggle API integration
    ├── db_connect.py       # Database connections (SQLite, PG, MySQL)
    ├── ai_insights.py      # Claude AI analysis modes
    └── export.py           # PDF, CSV, Excel, JSON export
```

Each module is self-contained. When adding a new feature, create a new module file rather than expanding an existing one unless the change is directly related.

---

## How to Contribute

### 1. Check existing issues first

Browse [open issues](https://github.com/datavynlabs/datavyn/issues) before starting work. If something is already being worked on, leave a comment rather than opening a duplicate.

### 2. Open an issue before large changes

For anything beyond a small bug fix — new features, architectural changes, new integrations — open an issue first to discuss the approach. This saves time for both you and the reviewers.

### 3. Fork and create a branch

Never commit directly to `main`. Always work on a dedicated branch off `main`.

```bash
git checkout -b fix/sidebar-toggle-bug
git checkout -b feat/snowflake-connector
git checkout -b docs/update-readme
```

### 4. Make your changes

Keep changes focused. One pull request should address one thing. If you find other bugs while working, open a separate issue or PR for them.

### 5. Test your changes

Before opening a PR, verify that:

- The app runs without errors (`streamlit run app.py`)
- Your change works with at least one real dataset (CSV recommended)
- No existing functionality is broken
- Python files pass syntax check: `python -m py_compile modules/your_file.py`

### 6. Open a pull request

Push your branch and open a PR against `main`. Fill in the PR template completely.

---

## Branch Naming

Use the following prefixes:

| Prefix | Use for |
|---|---|
| `feat/` | New features |
| `fix/` | Bug fixes |
| `docs/` | Documentation only |
| `refactor/` | Code restructuring with no behaviour change |
| `style/` | CSS / UI changes only |
| `chore/` | Dependency updates, config changes |

Examples: `feat/mongodb-connector`, `fix/pdf-export-encoding`, `docs/contributing-guide`

---

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <short summary>

[optional body]
[optional footer]
```

Examples:

```
feat(charts): add time series zoom controls
fix(upload): handle BOM in UTF-8 CSV files
docs(readme): update dependency list
style(sidebar): increase stat label font size
chore(deps): bump reportlab to 4.1.0
```

Rules:
- Use the imperative mood in the summary: "add", "fix", "update" not "added", "fixed", "updated"
- Keep the summary under 72 characters
- Reference issue numbers in the footer: `Closes #42`

---

## Pull Request Guidelines

- PRs should target the `main` branch
- Fill in the PR description — explain **what** changed and **why**
- Link to the related issue with `Closes #<issue-number>`
- Keep PRs small and focused — large PRs are hard to review and slow to merge
- Do not include unrelated formatting or whitespace changes
- Screenshots or screen recordings are appreciated for UI changes
- A reviewer will be assigned within 2 business days

### PR Template

```markdown
## Summary
Brief description of the change.

## Related Issue
Closes #

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactor
- [ ] Style / UI change

## Testing
Describe how you tested the change. Include dataset type if relevant.

## Screenshots (if applicable)
```

---

## Reporting Bugs

Open an issue using the **Bug Report** template and include:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected behaviour vs actual behaviour
- Your environment: OS, Python version, Streamlit version
- The full error traceback (paste into a code block)
- A sample file that reproduces the issue, if applicable (anonymise any sensitive data)

---

## Suggesting Features

Open an issue using the **Feature Request** template and include:

- The problem you are trying to solve
- Your proposed solution
- Any alternatives you considered
- Why this would be valuable to other DataVyn users

Feature requests are evaluated based on alignment with DataVyn's core purpose: automating data ingestion, visualisation, and AI-powered analysis.

---

## Style Guide

### Python

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use `f-strings` for string formatting
- Keep functions focused — one responsibility per function
- Add a short docstring to any new public function
- Use type hints where practical

### CSS

- Use CSS variables defined in `:root` — do not hardcode colour values
- Never use wildcard selectors (`*`) inside Streamlit `data-testid` elements
- Do not add `display: none` or `visibility: hidden` to any `stHeader`, `stSidebar`, or `collapsedControl` selectors — this breaks the sidebar toggle

### Streamlit

- Use `st.session_state` via `get_state()` from `modules/state.py` — do not access `st.session_state` directly in module files
- Pass `key_prefix` to `render_auto_charts()` whenever calling from a new context
- Use `width='stretch'` for `st.plotly_chart` — not `use_container_width=True`
- Avoid `st.rerun()` inside file upload handlers — use filename tracking to prevent reparse loops

---

## Contact

For questions that are not suited to a GitHub issue, reach out to the DataVyn Labs team:

- **GitHub Discussions:** [github.com/datavynlabs/datavyn/discussions](https://github.com/DataVyn-labs/datavyn/discussions)
- **Email:** datavyn247@gmail.com

---

*DataVyn Labs — Automate Your Data. Illuminate Your Insights.*
