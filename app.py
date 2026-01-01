from flask import Flask, render_template, request, redirect, session, url_for, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import csv
from datetime import datetime, timedelta
import os
import uuid  # For session tokens

app = Flask(__name__)
app.secret_key = "dev-secret-key"  # Secret key for session management

SESSION_TIMEOUT = 30 * 60  # 30 minutes in seconds

# -------------------------------
# Helper function: connect to DB
# -------------------------------
def get_db():
    conn = sqlite3.connect("users.db")  # Connect to SQLite database
    conn.row_factory = sqlite3.Row      # Return rows as dictionaries
    return conn

# -------------------------------
# Middleware: check session timeout
# -------------------------------
@app.before_request
def session_management():
    if "user_id" in session:
        now = datetime.now().timestamp()
        last_active = session.get("last_active", now)

        if now - last_active > SESSION_TIMEOUT:
            # 🔥 CLEAR DB TOKEN (this was missing)
            db = get_db()
            db.execute(
                "UPDATE users SET session_token = NULL WHERE id = ?",
                (session["user_id"],)
            )
            db.commit()
            db.close()

            session.clear()
            flash("Session expired due to inactivity.", "error")
            return redirect(url_for("login"))

        # Update activity timestamp
        session["last_active"] = now

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if user and check_password_hash(user["password"], password):

            # Defensive cleanup of any stale token
            db.execute(
                "UPDATE users SET session_token = NULL WHERE id = ?",
                (user["id"],)
            )
            db.commit()

            # Create new session
            token = str(uuid.uuid4())
            session["user_id"] = user["id"]
            session["last_active"] = datetime.now().timestamp()
            session["session_token"] = token

            # Store new token
            db.execute(
                "UPDATE users SET session_token = ? WHERE id = ?",
                (token, user["id"])
            )
            db.commit()
            db.close()

            flash("Login successful!", "success")
            return redirect("/dashboard")

        db.close()
        flash("Invalid credentials.", "error")

    return render_template("login.html")


# -------------------------------
# Register route
# -------------------------------
@app.route("/register", methods=["GET", "POST"])

def register():
    if request.method == "POST":
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        db = get_db()
        try:
            db.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            db.commit()
            flash("Account created successfully!", "success")
        except sqlite3.IntegrityError:
            flash("Email already registered.", "error")
        finally:
            db.close()
        return redirect("/")

    return render_template("register.html")

# -------------------------------
# Logout route
# -------------------------------
@app.route("/logout")
def logout():
    user_id = session.get("user_id")
    if user_id:
        # Clear session token in database
        db = get_db()
        db.execute("UPDATE users SET session_token=NULL WHERE id=?", (user_id,))
        db.commit()
        db.close()
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect("/")

# -------------------------------
# Dashboard route
# -------------------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    # Get query params for sorting (name, amount, billing_date)
    sort_by = request.args.get("sort", "billing_date")  # Default sort by billing date

    db = get_db()
    subs = db.execute(
        f"SELECT * FROM subscriptions WHERE user_id=? ORDER BY {sort_by} ASC",
        (session["user_id"],)
    ).fetchall()
    db.close()

    # Highlight subscriptions due in next 7 days
    upcoming = []
    for sub in subs:
        billing_date = datetime.strptime(sub["billing_date"], "%Y-%m-%d")
        if 0 <= (billing_date - datetime.now()).days <= 7:
            upcoming.append(sub["id"])

    # Calculate monthly total for current month
    current_month = datetime.now().month
    total = sum(
        sub["amount"] 
        for sub in subs 
        if datetime.strptime(sub["billing_date"], "%Y-%m-%d").month == current_month
    )

    # Prepare data for Chart.js - Subscription amounts
    labels = [sub["name"] for sub in subs]
    amounts = [sub["amount"] for sub in subs]

    # Prepare monthly totals over the year for chart
    monthly_totals = []
    for m in range(1, 13):
        month_total = sum(
            sub["amount"]
            for sub in subs
            if datetime.strptime(sub["billing_date"], "%Y-%m-%d").month == m
        )
        monthly_totals.append(month_total)

    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    return render_template(
        "dashboard.html",
        subs=subs,
        total=total,
        upcoming=upcoming,
        labels=labels,
        amounts=amounts,
        months=months,
        monthly_totals=monthly_totals
    )

# -------------------------------
# Add subscription route
# -------------------------------
@app.route("/add", methods=["GET", "POST"])
def add():
    if "user_id" not in session:
        return redirect("/")

    if request.method == "POST":
        name = request.form["name"]
        amount = float(request.form["amount"])
        date = request.form["date"]
        recurring = request.form.get("recurring", "monthly")

        db = get_db()
        db.execute("INSERT INTO subscriptions (user_id, name, amount, billing_date, recurring) VALUES (?, ?, ?, ?, ?)",
                   (session["user_id"], name, amount, date, recurring))
        db.commit()
        db.close()

        flash("Subscription added successfully!", "success")
        return redirect("/dashboard")

    return render_template("add.html")

# -------------------------------
# Edit subscription route
# -------------------------------
@app.route("/edit/<int:sub_id>", methods=["GET", "POST"])
def edit(sub_id):
    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    sub = db.execute("SELECT * FROM subscriptions WHERE id=? AND user_id=?", (sub_id, session["user_id"])).fetchone()

    if not sub:
        flash("Subscription not found.", "error")
        return redirect("/dashboard")

    if request.method == "POST":
        name = request.form["name"]
        amount = float(request.form["amount"])
        date = request.form["date"]
        recurring = request.form.get("recurring", "monthly")

        db.execute("UPDATE subscriptions SET name=?, amount=?, billing_date=?, recurring=? WHERE id=?",
                   (name, amount, date, recurring, sub_id))
        db.commit()
        db.close()
        flash("Subscription updated successfully!", "success")
        return redirect("/dashboard")

    db.close()
    return render_template("edit.html", sub=sub)

# -------------------------------
# Delete subscription route
# -------------------------------
@app.route("/delete/<int:sub_id>")
def delete(sub_id):
    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    db.execute("DELETE FROM subscriptions WHERE id=? AND user_id=?", (sub_id, session["user_id"]))
    db.commit()
    db.close()
    flash("Subscription deleted.", "success")
    return redirect("/dashboard")

# -------------------------------
# Forgot password route
# -------------------------------
@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        session["reset_email"] = request.form["email"]
        flash("Enter a new password.", "info")
        return redirect("/reset")

    return render_template("forgot.html")

# -------------------------------
# Reset password route
# -------------------------------
@app.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "POST":
        email = session.get("reset_email")
        password = generate_password_hash(request.form["password"])

        db = get_db()
        db.execute("UPDATE users SET password=? WHERE email=?", (password, email))
        db.commit()
        db.close()

        session.pop("reset_email", None)
        flash("Password reset successful.", "success")
        return redirect("/")

    return render_template("reset.html")

# -------------------------------
# Export subscriptions as CSV
# -------------------------------
@app.route("/export")
def export_csv():
    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    subs = db.execute("SELECT * FROM subscriptions WHERE user_id=?", (session["user_id"],)).fetchall()
    db.close()

    filename = f"subscriptions_{session['user_id']}.csv"
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "Name", "Amount", "Billing Date", "Recurring"])
        for sub in subs:
            writer.writerow([sub["id"], sub["name"], sub["amount"], sub["billing_date"], sub["recurring"]])

    return send_file(filename, as_attachment=True)

# -------------------------------
# Import subscriptions from CSV
# -------------------------------
@app.route("/import", methods=["GET", "POST"])
def import_csv():
    if "user_id" not in session:
        return redirect("/")

    if request.method == "POST":
        file = request.files["file"]
        if file:
            db = get_db()
            reader = csv.DictReader(file.stream.read().decode("utf-8").splitlines())
            for row in reader:
                db.execute("INSERT INTO subscriptions (user_id, name, amount, billing_date, recurring) VALUES (?, ?, ?, ?, ?)",
                           (session["user_id"], row["Name"], float(row["Amount"]), row["Billing Date"], row.get("Recurring", "monthly")))
            db.commit()
            db.close()
            flash("CSV imported successfully!", "success")
            return redirect("/dashboard")

    return render_template("import.html")

# -------------------------------
# Run Flask app
# -------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render provides the PORT env variable
    app.run(host="0.0.0.0", port=port, debug=True)

