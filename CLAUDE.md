# CLAUDE.md

Guidance for Claude Code (claude.ai/code) when working in this repository.

## Project Summary

**Spendly** is a lightweight Flask expense tracker. Server-Side Rendering with Jinja2, SQLite for storage, no ORM, no frontend framework — vanilla JS + CSS only.

The repo is built spec-by-spec. Before touching a feature, read the matching spec in `.claude/specs/` — each spec defines the schema, routes, and acceptance criteria for one step.

## Development Commands

- **Install dependencies**: `pip install -r requirements.txt`
- **Run application**: `python app.py` (serves on `http://127.0.0.1:5001`)
- **Run tests**: `pytest`
- **Virtual env** (optional but recommended): `python -m venv .venv`

## Repository Layout

```
expense-tracker/
├── app.py                  # Flask app: routes + startup wiring (init_db, seed_db)
├── database/
│   ├── __init__.py
│   └── db.py               # SQLite layer: get_db(), init_db(), seed_db()
├── templates/
│   ├── base.html           # Master layout (nav, footer, global assets)
│   ├── landing.html        # Marketing landing page
│   ├── login.html          # Login form (UI only — auth wired in later spec)
│   ├── register.html       # Registration form (UI only)
│   ├── terms.html          # Terms & Conditions
│   └── privacy.html        # Privacy Policy
├── static/
│   ├── css/
│   │   ├── style.css       # Global styles + design tokens (CSS variables in :root)
│   │   └── landing.css     # Landing-page-specific styles
│   └── js/
│       └── main.js         # Client-side logic (e.g. landing-page modal)
├── tests/                  # pytest test suite (see requirements.txt)
├── requirements.txt        # flask, werkzeug, pytest, pytest-flask
├── .claude/specs/          # Per-feature implementation specs
└── spendly.db              # SQLite file — created on first run, gitignored
```

## Architecture

### Backend (`app.py`)
- Plain Flask, no blueprints yet. All routes live in `app.py`.
- Active routes: `/`, `/register`, `/login`, `/terms`, `/privacy`.
- Placeholder routes return short strings ("coming in Step N") — these correspond to upcoming specs and should NOT be silently wired up until the spec for that step is followed.
- Startup order in `if __name__ == "__main__":`: `init_db()` → `seed_db()` → `app.run(...)`. Both DB calls are idempotent and safe on every run.

### Database (`database/db.py`)
Three entry points:
- **`get_db()`** — opens `spendly.db` in the project root, sets `row_factory = sqlite3.Row`, enables `PRAGMA foreign_keys = ON`. Always use this for queries — never call `sqlite3.connect` directly.
- **`init_db()`** — `CREATE TABLE IF NOT EXISTS` for `users` and `expenses`. Safe to call repeatedly.
- **`seed_db()`** — inserts one demo user + 8 sample expenses; early-returns if any user already exists.

**Rules (enforced across the project):**
- All SQL is parameterized (`?` placeholders). Never use f-strings or `%` formatting inside SQL.
- Passwords are hashed via `werkzeug.security.generate_password_hash` / `check_password_hash`.
- `amount` is `REAL`. Dates are stored as `YYYY-MM-DD` strings.
- FK enforcement is per-connection — every `get_db()` call sets the pragma.

**Schema (current — users, expenses):**
| Table | Key columns |
|---|---|
| `users` | `id`, `name`, `email` (UNIQUE), `password_hash`, `created_at` |
| `expenses` | `id`, `user_id` (FK → users.id, ON DELETE CASCADE), `amount`, `category`, `date`, `description`, `created_at` |

**Fixed category list** (from spec): `Food`, `Transport`, `Bills`, `Health`, `Entertainment`, `Shopping`, `Other`. Use exactly these strings — no variations.

**Demo credentials** (seeded on first run): `demo@spendly.com` / `demo123`.

### Templates
- All page templates `{% extends "base.html" %}`.
- Three blocks to fill: `title`, `content`, `scripts`. Optional `head` block for page-specific `<link>`/`<script>`.
- Global nav lives in `base.html` — do not duplicate it in page templates.

### Design System
CSS custom properties are defined in `:root` in `static/css/style.css` (colors, spacing, radii, shadows, typography). Always reference design tokens (`var(--…)`) instead of hard-coding values. Fonts: **DM Serif Display** for headings, **DM Sans** for body — loaded from Google Fonts in `base.html`.

## Conventions

- **Match existing code style**: 4-space indent, type hints where the file already uses them, docstrings on public functions, section-banner comments (`# ---... #`) for grouped routes.
- **Don't add dependencies** unless the spec asks for them. `requirements.txt` is the source of truth.
- **Don't introduce an ORM.** The spec for step 1 explicitly forbids SQLAlchemy. Use raw `sqlite3` via `get_db()`.
- **Don't widen scope.** Each spec is one step. Touch only the files listed in the spec's "Files to Change". If you think adjacent work is needed, flag it — don't bundle it.
- **Idempotency matters.** `init_db()` and `seed_db()` must stay safe to call on every app start.

## Workflow When Implementing a Spec

1. Read `.claude/specs/<NN>-<name>.md` end-to-end before writing anything.
2. Skim the listed "Files to Change" and any files those reference.
3. Implement strictly within the spec's Definition of Done. Don't invent extra behavior.
4. Verify using the spec's verification checklist (startup, schema checks, count queries, constraint tests, smoke test).
5. Update this CLAUDE.md only if the change introduces a new pattern, file, or convention future work should know about.

## Known Gotchas

- `.gitignore` ignores `spendly.db`, `*.db`, `expense_tracker.db`, `.venv/`, `venv/`, and `.claude/plans/` — but **not** `.claude/specs/`, which must stay tracked. Earlier in the repo's history, `spendly.db` was accidentally committed (`6541e2a adding db`); it should be removed with `git rm --cached spendly.db` when convenient.
- `spendly.db` is created in the project root at runtime. Delete it to force a clean re-seed.
- `seed_db()` is idempotent on empty `users` table only — dropping `spendly.db` is the supported way to reset; manually deleting user rows won't trigger a re-seed.