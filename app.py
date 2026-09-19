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

        if username == "admin" and password == "admin123":

            session.clear()

            session["logged_in"] = True
            session["user_type"] = "Admin"

            return redirect("/admin-dashboard")

        elif username == "faculty" and password == "faculty123":

            session.clear()

            session["logged_in"] = True
            session["user_type"] = "Faculty"

            return redirect("/faculty-dashboard")

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

        # Current password check
        if not password_hash or not check_password_hash(
            password_hash,
            current_password
        ):

            conn.close()

            return render_template(
                "change_password.html",
                error="Current password is incorrect."
            )

        # Strong password check
        if not is_strong_password(new_password):

            conn.close()

            return render_template(
                "change_password.html",
                error="Password must have at least 8 characters, 1 uppercase letter, 1 lowercase letter, 1 number and 1 special character."
            )

        # Confirm password check
        if new_password != confirm_password:

            conn.close()

            return render_template(
                "change_password.html",
                error="New password and Confirm Password do not match."
            )

        # New password should be different
        if check_password_hash(password_hash, new_password):

            conn.close()

            return render_template(
                "change_password.html",
                error="New password must be different from the current password."
            )

        new_password_hash = generate_password_hash(new_password)

        cursor.execute("""
            UPDATE students
            SET password_hash=?
            WHERE id=?
        """, (
            new_password_hash,
            student_id
        ))

        conn.commit()
        conn.close()

        return render_template(
            "change_password.html",
            success="Password changed successfully."
        )

    return render_template("change_password.html")


# ================= STUDENT PROFILE =================
@app.route("/student-profile")
def student_profile():

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
        return redirect("/login")

    return render_template(
        "student_profile.html",
        student=student
    )


# ================= HOME =================
@app.route("/")
def home():

    if not session.get("logged_in"):
        return redirect("/login")

    user_type = session.get("user_type")

    if user_type == "Admin":
        return redirect("/admin-dashboard")

    elif user_type == "Faculty":
        return redirect("/faculty-dashboard")

    elif user_type == "Student":
        return redirect("/student-dashboard")

    return redirect("/login")


# ================= STUDENTS =================
@app.route("/students")
def students():

    if not session.get("logged_in"):
        return redirect("/login")

    if session.get("user_type") != "Admin":
        return redirect("/login")

    init_db()

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, roll_no, course, email
        FROM students
        ORDER BY roll_no ASC
    """)

    students = cursor.fetchall()

    conn.close()

    return render_template(
        "students.html",
        students=students
    )


# ================= ADD STUDENT =================
@app.route("/add-student", methods=["GET", "POST"])
def add_student():

    if not session.get("logged_in"):
        return redirect("/login")

    if session.get("user_type") != "Admin":
        return redirect("/login")

    init_db()

    if request.method == "POST":

        name = request.form["name"].strip()
        roll_no = request.form["roll_no"].strip()
        course = request.form["course"]
        email = request.form["email"].strip()

        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if not is_strong_password(password):

            return render_template(
                "add_student.html",
                error="Password must have at least 8 characters, 1 uppercase letter, 1 lowercase letter, 1 number and 1 special character."
            )

        if password != confirm_password:

            return render_template(
                "add_student.html",
                error="Password and Confirm Password do not match."
            )

        password_hash = generate_password_hash(password)

        conn = sqlite3.connect("college.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM students WHERE roll_no=?",
            (roll_no,)
        )

        existing_student = cursor.fetchone()

        if existing_student:

            conn.close()

            return render_template(
                "add_student.html",
                error="This Enrollment Number already exists."
            )

        cursor.execute("""
            INSERT INTO students
            (name, roll_no, course, email, password_hash)
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            roll_no,
            course,
            email,
            password_hash
        ))

        conn.commit()
        conn.close()

        return redirect("/students")

    return render_template("add_student.html")


# ================= EDIT STUDENT =================
@app.route("/edit-student/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    if not session.get("logged_in"):
        return redirect("/login")

    if session.get("user_type") != "Admin":
        return redirect("/login")

    init_db()

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"].strip()
        roll_no = request.form["roll_no"].strip()
        course = request.form["course"]
        email = request.form["email"].strip()

        new_password = request.form.get(
            "password",
            ""
        ).strip()

        confirm_password = request.form.get(
            "confirm_password",
            ""
        ).strip()

        if new_password:

            if not is_strong_password(new_password):

                conn.close()

                return render_template(
                    "edit_student.html",
                    student=(
                        id,
                        name,
                        roll_no,
                        course,
                        email
                    ),
                    error="Password must have at least 8 characters, 1 uppercase letter, 1 lowercase letter, 1 number and 1 special character."
                )

            if new_password != confirm_password:

                conn.close()

              return render_template(
    "edit_student.html",
    student=(
        id,
        name,
        roll_no,
        course,
        email
    ),
    error="Password must have at least 8 characters, 1 uppercase letter, 1 lowercase letter, 1 number and 1 special character."
)
