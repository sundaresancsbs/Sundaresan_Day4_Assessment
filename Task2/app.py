
from flask import Flask, render_template, request, redirect, session, jsonify, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "my_secret_key_123"


# Connect to the database and create the table
def init_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
        )
    """)

    conn.commit()
    conn.close()


# Home page: Login
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "1234":
            session["logged_in"] = True
            return redirect(url_for("tasks"))

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


# Display tasks (login required)
@app.route("/tasks", methods=["GET"])
def tasks():
    if not session.get("logged_in"):
        return redirect(url_for("home"))

    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
    all_tasks = cursor.fetchall()

    conn.close()

    return render_template("tasks.html", tasks=all_tasks)


# Add a task using AJAX
@app.route("/add_task", methods=["POST"])
def add_task():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "Please log in first"}), 401

    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()

    if not title:
        return jsonify({
            "success": False,
            "message": "Task title cannot be empty"
        }), 400

    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (title) VALUES (?)",
        (title,)
    )

    task_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "task": {
            "id": task_id,
            "title": title,
            "status": "Pending"
        }
    })


# Logout
@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
