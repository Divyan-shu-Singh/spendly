# Spec: Registration

## Overview
Wire the existing `/register` page to a real backend so visitors can create a Spendly account. The form is already rendered by `templates/register.html` and accepts `name`, `email`, and `password`; this step turns it into a working flow that validates input, creates a row in `users`, hashes the password, logs the user in immediately, and redirects to a placeholder home view. Step 3 (login) and Step 4 (profile) build on top of this.

## Depends on
- Step 1 — Database setup (`users` table exists with `name`, `email`, `password_hash`, `created_at`).

## Routes
- `GET  /register` — render the registration form — public.
- `POST /register` — process the form: validate, create user, log in, redirect — public.

The existing `GET /register` placeholder in `app.py` is replaced with a real handler that accepts both methods.

## Database changes
No new tables, columns, or constraints. Uses the existing `users` table from Step 1:
- `email` UNIQUE — duplicate registrations must surface as a user-facing error.
- `password_hash` is set via `werkzeug.security.generate_password_hash`.
- `name`, `password_hash` are NOT NULL.

## Templates
- **Modify:** `templates/register.html`
  - Form already submits to `/register` with `method="POST"` — no structural change required.
  - The template already renders `{% if error %}{{ error }}{% endif %}` inside the auth card, so server-side errors will surface automatically once the route passes them in.

## Files to change
- `app.py`
  - Import `request`, `redirect`, `url_for`, `session` from `flask`.
  - Import `flash` from `flask` (or pass errors directly via `render_template`).
  - Import `generate_password_hash` from `werkzeug.security`.
  - Import `get_db` from `database.db` (already imported).
  - Add `app.secret_key` configuration (use a stable dev key for now; real key wiring is out of scope for this step).
  - Rewrite the `/register` route to handle `GET` and `POST`.
  - Add a placeholder `GET /dashboard` route that requires login and returns a short string ("Dashboard — coming in Step 5"). Required so we have somewhere to redirect after successful registration. Mark it with a `@login_required`-style comment but keep the guard logic simple for this step (session-based).

## Files to create
None. No new template, no new JS, no new CSS — the form already exists and uses existing styles.

## New dependencies
No new dependencies. Uses:
- `flask` (already installed) — `request`, `redirect`, `url_for`, `session`, `flash`.
- `werkzeug.security` (already installed) — `generate_password_hash`.
- `sqlite3` via `get_db()` (already wired in Step 1).

## Rules for implementation
- No SQLAlchemy or any ORM. Raw `sqlite3` via `get_db()` only.
- All SQL must use parameterized queries (`?` placeholders). No f-strings or `%` formatting inside SQL.
- Passwords are hashed with `werkzeug.security.generate_password_hash`. Never store plaintext passwords.
- Validate server-side:
  - `name`: required, trimmed, length 1–80.
  - `email`: required, must contain `@` and `.`, length ≤ 120, lowercased before insert.
  - `password`: required, length ≥ 8.
- On validation failure, re-render `register.html` with an `error` message; preserve the submitted `name` and `email` so the user does not retype.
- On duplicate email (UNIQUE constraint violation), surface a friendly error like "An account with that email already exists." and re-render the form.
- On success: insert the user, store `user_id` in `flask.session`, then `redirect(url_for("dashboard"))`.
- The `dashboard` placeholder route must read `session.get("user_id")`; if missing, redirect to `/login`.
- Use `conn.close()` after each request (no connection pooling required at this scale).
- Wrap DB work in `try/finally` so the connection always closes.
- Do NOT introduce blueprints. Keep routes in `app.py`.
- All templates (existing or future) continue to extend `base.html`.
- Use CSS variables (`var(--…)`) for any new styles — never hardcode hex values.
- Keep the implementation aligned with existing code style: 4-space indent, type hints where the file already uses them, section-banner comments for grouped routes.

## Definition of done
- [ ] `GET /register` renders the registration form (unchanged visually).
- [ ] `POST /register` with valid input creates a new row in `users`, stores `user_id` in the session, and redirects to `/dashboard`.
- [ ] `POST /register` with a duplicate email re-renders the form with the error "An account with that email already exists." and does NOT create a row.
- [ ] `POST /register` with an invalid email (missing `@` or `.`) re-renders the form with a validation error and does NOT create a row.
- [ ] `POST /register` with a password shorter than 8 characters re-renders the form with a validation error and does NOT create a row.
- [ ] `POST /register` with an empty `name` re-renders the form with a validation error and does NOT create a row.
- [ ] After successful registration, `GET /dashboard` returns the dashboard placeholder string instead of redirecting to `/login`.
- [ ] After a fresh app start (without `spendly.db`), the demo user from Step 1 still exists and can be re-registered-against by hitting `/register` with `demo@spendly.com` — error appears as expected.
- [ ] Passwords in the database are stored as hashed strings (verify via `sqlite3 spendly.db "SELECT password_hash FROM users WHERE email = 'demo@spendly.com';"` — must NOT match `"demo123"`).
- [ ] No new rows are inserted into `users` when registration fails for any reason.
- [ ] App starts without errors (`python app.py`) and `/register` loads in the browser.
- [ ] No raw SQL string interpolation anywhere in `app.py`.