from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change-this-secret-key-for-your-project"

DATA_FILE = Path(__file__).with_name("smartqueue_data.json")
SERVICES = ["Banking", "Aadhaar Services", "Document Verification", "General Enquiry"]

def load_data():
    if not DATA_FILE.exists():
        return {"users": [], "tokens": []}
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"users": [], "tokens": []}

def save_data(data):
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

@app.route("/")
def home():
    return render_template("index.html", user=session.get("user"))

@app.route("/services")
def services():
    return render_template("services.html", services=SERVICES, user=session.get("user"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 6:
            flash("Please enter all details. Password must be at least 6 characters.", "error")
            return render_template("auth.html", mode="register", user=None)
        data = load_data()
        if any(u["email"] == email for u in data["users"]):
            flash("This email is already registered. Please login.", "error")
            return render_template("auth.html", mode="register", user=None)
        data["users"].append({
            "name": name,
            "email": email,
            "password": generate_password_hash(password)
        })
        save_data(data)
        session["user"] = {"name": name, "email": email}
        flash("Account created successfully. Welcome to SmartQueue!", "success")
        return redirect(url_for("dashboard"))
    return render_template("auth.html", mode="register", user=session.get("user"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        data = load_data()
        for user in data["users"]:
            if user["email"] == email and check_password_hash(user["password"], password):
                session["user"] = {"name": user["name"], "email": user["email"]}
                flash("Login successful. Welcome back!", "success")
                return redirect(url_for("dashboard"))
        flash("Incorrect email or password.", "error")
    return render_template("auth.html", mode="login", user=session.get("user"))

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        flash("Please login to view your dashboard.", "error")
        return redirect(url_for("login"))
    data = load_data()
    my_tokens = [t for t in reversed(data["tokens"]) if t["email"] == session["user"]["email"]]
    total_tokens = len(data["tokens"])
    waiting_tokens = sum(1 for t in data["tokens"] if t["status"] == "Waiting")
    return render_template(
        "dashboard.html",
        user=session["user"],
        my_tokens=my_tokens,
        total_tokens=total_tokens,
        waiting_tokens=waiting_tokens
    )

@app.route("/get-token", methods=["POST"])
def get_token():
    if "user" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("login"))
    service = request.form.get("service", "")
    priority = request.form.get("priority", "Normal")
    if service not in SERVICES:
        flash("Please select a valid service.", "error")
        return redirect(url_for("dashboard"))
    if priority not in ["Normal", "Senior Citizen"]:
        priority = "Normal"
    data = load_data()
    next_number = max([t.get("number", 0) for t in data["tokens"]] or [0]) + 1
    token = {
        "number": next_number,
        "token": f"Q{next_number:03d}",
        "name": session["user"]["name"],
        "email": session["user"]["email"],
        "service": service,
        "priority": priority,
        "status": "Waiting",
        "date": datetime.now().strftime("%d %b %Y, %I:%M %p")
    }
    data["tokens"].append(token)
    save_data(data)
    flash(f"Your token {token['token']} has been generated successfully!", "success")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)
