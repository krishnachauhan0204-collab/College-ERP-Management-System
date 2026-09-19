from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import date
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "college_erp_secret_key"


# ================= PASSWORD VALIDATION =================
def is_strong_password(password):
    if len(password) < 8:
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"[0-9]", password):
        return False

    if not re.search(r"[^A-Za-z0-9]", password):
        return False

    return True


# ================= DATABASE =================
def init_db():

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            roll_no TEXT,
            course TEXT,
            email TEXT
        )
    """)

    cursor.execute("PRAGMA table_info(students)")
    columns = [column[1] for column in cursor.fetchall()]

    if "password_hash" not in columns:
        cursor.execute("""
            ALTER TABLE students
            ADD COLUMN password_hash TEXT
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            department TEXT,
            email TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            attendance_date TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()


# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        # ADMIN
        if username == "admin" and password == "admin123":

            session.clear()
            session["logged_in"] = True
            session["user_type"] = "Admin"

            return redirect("/admin-dashboard")

        # FACULTY
        elif username == "faculty" and password == "faculty123":

            session.clear()
            session["logged_in"] = True
            session["user_type"] = "Faculty"

            return redirect("/faculty-dashboard")

        # STUDENT
        else:

            init_db()

            conn = sqlite3.connect("college.db")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, roll_no, course, email, password_hash
                FROM students
                WHERE roll_no=?
            """, (username,))

            student = cursor.fetchone()

            conn.close()

            if student and student[5]:

                if check_password_hash(student[5], password):

                    session.clear()
                    session["logged_in"] = True
                    session["user_type"] = "Student"
                    session["student_id"] = student[0]

                    return redirect("/student-dashboard")

            return render_template(
                "login.html",
                error="Invalid Enrollment Number or Password"
            )

    return render_template("login.html")


# ================= LOGOUT =================
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# ================= ADMIN DASHBOARD =================
@app.route("/admin-dashboard")
def admin_dashboard():

    if not session.get("logged_in"):
        return redirect("/login")

    if session.get("user_type") != "Admin":
        return redirect("/login")

    init_db()

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM faculty")
    total_faculty = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_students=total_students,
        total_faculty=total_faculty
    )


# ================= FACULTY DASHBOARD =================
@app.route("/faculty-dashboard")
def faculty_dashboard():

    if not session.get("logged_in"):
        return redirect("/login")

    if session.get("user_type") != "Faculty":
        return redirect("/login")

    init_db()

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "faculty_dashboard.html",
        total_students=total_students
    )


# ================= STUDENT DASHBOARD =================
@app.route("/student-dashboard")
def student_dashboard():

    if not session.get("logged_in"):
        return redirect("/login")

    if session.get("user_type") != "Student":
        return redirect("/login")

    student_id = session.get("student_id")

    init_db()

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, roll_no, course, email
        FROM students
        WHERE id=?
    """, (student_id,))

    student = cursor.fetchone()

    conn.close()

    if not student:
        session.clear()
        return redirect("/login")

    return render_template(
        "student_dashboard.html",
        student=student
    )


# ================= CHANGE PASSWORD =================
@app.route("/change-password", methods=["GET", "POST"])
def change_password():

    if not session.get("logged_in"):
        return redirect("/login")

    if session.get("user_type") != "Student":
        return redirect("/login")

    student_id = session.get("student_id")

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        init_db()

        conn = sqlite3.connect("college.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT password_hash
            FROM students
            WHERE id=?
        """, (student_id,))

        student = cursor.fetchone()

        if not student:
            conn.close()
            return redirect("/login")

        password_hash = student[0]

        if not password_hash or not check_password_hash(
            password_hash,
            current_password
        ):
