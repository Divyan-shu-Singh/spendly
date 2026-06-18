# Spec: Login and Logout

## Overview
Wire the existing `/login` page to a real backend so existing Spendly users can authenticate, and replace the `/logout` placeholder with a working sign-out flow. The form is already rendered by `templates/login.html` and accepts `email` and `password`; this step turns it into a working flow that validates input, looks the user up in `users`, verifies the password with `werkzeug.security.check_password_hash`, stores `user_id` in the session, and redirects to the placeholder dashboard. `/logout` clears the session and redirects back to `/login`. Step 4 (profile) and the rest of the logged-in app build on top of this.

## Depends on
- Step 1 — Database setup (`users` table exists with `email`, `password_hash`).
- Step 2 — Registration (session is populated on register, dashboard guard already reads `session.get("user_id")` and redirects to `/login` when missing).

## Routes
- `POST /login` — process the login form: validate, verify password, set session, redirect — public.
- `GET  /logout` — clear the session and redirect to `/login` — public (idempotent: signing out when not signed in is a no-op redirect).

The existing `GET /login` placeholder in `app.py` is replaced with a real handler that accepts both methods. The existing `GET /logout` placeholder ("Logout — coming in Step 3") is replaced with a real handler.

## Database changes
No new tables, columns, or constraints. Uses the existing `users` table from Step 1:
- `email` is the lookup key (lower-cased to match the normalized value inserted in Step 2).
- `password_hash` is verified via `werkzeug.security.check_password_hash`.
- A generic "Invalid email or password." error is used for both unknown-email and wrong-password cases, to avoid leaking which one was wrong.

## Templates
- **Modify:** `templates/login.html`
  - Form already submits to `/login` with `method="POST"` — no structural change required.
  - The template already renders `{% if error %}{{ error }}{% endif %}` inside the auth card, so server-side errors will surface automatically once the route passes them in.
  - Preserve the submitted `email` on validation failure (mirroring how `register.html` preserves `name` and `email`) so the user does not retype it.
- **Modify:** `templates/base.html`
  - The nav currently shows "Sign in" + "Get started" for every visitor. Once a user is logged in, the nav must show the user's name and a "Sign out" link to `/logout` instead. Implement this with a conditional `{% if session.user_id %}` block — the dashboard placeholder does not exist yet, so the username is not a link.
  - Use `session.get("user_id")` (not `session.user_id`) so a missing key renders the public nav, matching the `dashboard` guard style in `app.py`.

## Files to change
- `app.py`
  - Import `check_password_hash` from `werkzeug.security` (in addition to the existing `generate_password_hash` import).
  - Rewrite the `/login` route to handle `GET` and `POST`.
  - Add a small helper `_render_login_form(error=None, email="")` that mirrors the `_render_register_form` helper from Step 2.
  - Rewrite the `/logout` route to clear the session and redirect to `/login`.
  - The `/dashboard` placeholder already redirects to `/login` when `session.get("user_id")` is missing — no change required there.

## Files to create
None. No new template, no new JS, no new CSS — `login.html` already exists and `base.html` styles cover the nav.

## New dependencies
No new dependencies. Uses:
- `flask` (already installed) — `request`, `redirect`, `url_for`, `session`.
- `werkzeug.security` (already installed) — `check_password_hash` (in addition to `generate_password_hash` already used in Step 2).
- `sqlite3` via `get_db()` (already wired in Step 1).

## Rules for implementation
- No SQLAlchemy or any ORM. Raw `sqlite3` via `get_db()` only.
- All SQL must use parameterized queries (`?` placeholders). No f-strings or `%` formatting inside SQL.
- Passwords are verified with `werkzeug.security.check_password_hash`. Never compare hashes with `==`.
- Validate server-side:
  - `email`: required, trimmed, must contain `@` and `.`, length ≤ 120. Lowercase before lookup.
  - `password`: required, length ≥ 1 (no minimum length check at login — the user already chose a valid password at registration).
- On validation failure (missing fields, malformed email), re-render `login.html` with an `error` message; preserve the submitted `email` so the user does not retype it.
- On unknown email OR wrong password, re-render `login.html` with the generic error "Invalid email or password." and the preserved `email`. Do NOT distinguish between the two cases.
- On success: store `user_id` in `flask.session`, then `redirect(url_for("dashboard"))`.
- The `logout` route must `session.clear()` (not just pop `user_id`) and `redirect(url_for("login"))`. It must be safe to call when no user is logged in.
- Use `conn.close()` after each request (no connection pooling required at this scale).
- Wrap DB work in `try/finally` so the connection always closes.
- Do NOT introduce blueprints. Keep routes in `app.py`.
- All templates (existing or future) continue to extend `base.html`.
- Use CSS variables (`var(--…)`) for any new styles — never hardcode hex values.
- Keep the implementation aligned with existing code style: 4-space indent, type hints where the file already uses them, section-banner comments for grouped routes.

## Definition of done
- [ ] `GET /login` renders the login form (unchanged visually).
- [ ] `POST /login` with valid credentials (`demo@spendly.com` / `demo123` from the seeded user) sets `session["user_id"]` and redirects to `/dashboard`.
- [ ] `POST /login` with a valid email but the wrong password re-renders the form with the error "Invalid email or password." and does NOT set a session.
- [ ] `POST /login` with an email that does not exist re-renders the form with the error "Invalid email or password." (same string as the wrong-password case) and does NOT set a session.
- [ ] `POST /login` with an empty email or empty password re-renders the form with a validation error and does NOT set a session.
- [ ] After successful login, `GET /dashboard` returns the dashboard placeholder string instead of redirecting to `/login`.
- [ ] `GET /logout` clears the session and redirects to `/login`. After logout, `GET /dashboard` redirects back to `/login`.
- [ ] `GET /logout` is safe to call when no user is logged in (no error, no exception, redirects to `/login`).
- [ ] After login, the nav in `base.html` shows the user's name and a "Sign out" link to `/logout` instead of the public "Sign in" / "Get started" buttons.
- [ ] No new rows are inserted into `users` on any login/logout path.
- [ ] App starts without errors (`python app.py`) and `/login` loads in the browser.
- [ ] No raw SQL string interpolation anywhere in `app.py`.
- [ ] All existing tests still pass (`pytest`).
