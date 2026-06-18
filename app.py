import sqlite3

from flask import Flask, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import get_db, init_db, seed_db

app = Flask(__name__)
# Placeholder secret key for development. Real key wiring is out of scope
# for this step; replace with a secure, environment-sourced value later.
app.secret_key = "dev-only-change-me"


# ------------------------------------------------------------------ #
# Request hooks                                                       #
# ------------------------------------------------------------------ #

@app.before_request
def _load_current_user():
    """Look up the logged-in user (by id) once per request for templates.

    Populates flask.g.current_user (a sqlite3.Row or None) so base.html
    can show the user's name in the nav without each route re-querying.
    Safe when no user is logged in — leaves g.current_user as None.
    """
    user_id = session.get("user_id")
    g.current_user = None
    if user_id is None:
        return
    conn = get_db()
    try:
        g.current_user = conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Render the registration form (GET) or create a new user (POST)."""
    if request.method == "POST":
        # Read and trim submitted fields.
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""

        # Validate in order; return the first failure with the form re-rendered.
        if not (1 <= len(name) <= 80):
            return _render_register_form(
                error="Please enter your name (1-80 characters).",
                name=name,
                email=email,
            )
        if "@" not in email or "." not in email or len(email) > 120:
            return _render_register_form(
                error="Please enter a valid email address.",
                name=name,
                email=email,
            )
        if len(password) < 8:
            return _render_register_form(
                error="Password must be at least 8 characters.",
                name=name,
                email=email,
            )

        email_normalized = email.lower()
        password_hash = generate_password_hash(password)

        conn = get_db()
        try:
            try:
                cursor = conn.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    (name, email_normalized, password_hash),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                return _render_register_form(
                    error="An account with that email already exists.",
                    name=name,
                    email=email,
                )

            session["user_id"] = cursor.lastrowid
        finally:
            conn.close()

        return redirect(url_for("dashboard"))

    # GET: render an empty form.
    return _render_register_form()


def _render_register_form(error: str | None = None, name: str = "", email: str = ""):
    """Helper that renders register.html with optional error and preserved input."""
    return render_template(
        "register.html",
        error=error,
        name=name,
        email=email,
    )


def _render_login_form(error: str | None = None, email: str = ""):
    """Helper that renders login.html with optional error and preserved email."""
    return render_template(
        "login.html",
        error=error,
        email=email,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """Render the login form (GET) or authenticate (POST)."""
    if request.method == "POST":
        # Read and trim submitted fields.
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""

        # Validate in order; return the first failure with the form re-rendered.
        if "@" not in email or "." not in email or len(email) > 120:
            return _render_login_form(
                error="Please enter a valid email address.",
                email=email,
            )
        if not password:
            return _render_login_form(
                error="Please enter your password.",
                email=email,
            )

        email_normalized = email.lower()

        conn = get_db()
        try:
            row = conn.execute(
                "SELECT id, password_hash FROM users WHERE email = ?",
                (email_normalized,),
            ).fetchone()

            # Generic error: do NOT leak whether the email exists.
            if row is None or not check_password_hash(row["password_hash"], password):
                return _render_login_form(
                    error="Invalid email or password.",
                    email=email,
                )

            session["user_id"] = row["id"]
        finally:
            conn.close()

        return redirect(url_for("dashboard"))

    # GET: render an empty form.
    return _render_login_form()


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    """Clear the session and redirect to /login. Idempotent."""
    session.clear()
    return redirect(url_for("login"))


# TODO: replace inline guard with a @login_required decorator in a later step.
@app.route("/dashboard")
def dashboard():
    """Placeholder dashboard — requires a logged-in session."""
    if not session.get("user_id"):
        return redirect(url_for("login"))
    return "Dashboard — coming in Step 5"


@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    # Ensure the schema exists and demo data is present before serving requests.
    init_db()
    seed_db()
    app.run(debug=True, port=5001)
