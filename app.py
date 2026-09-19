from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "college_erp_secret_key"


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

    # Add password_hash column if it does not already exist
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

        # ================= ADMIN LOGIN =================
        if username == "admin" and password == "admin123":

            session.clear()

            session["logged_in"] = True
            session["user_type"] = "Admin"

            return redirect("/admin-dashboard")

        # ================= FACULTY LOGIN =================
        elif username == "faculty" and password == "faculty123":

            session.clear()

            session["logged_in"] = True
            session["user_type"] = "Faculty"

            return redirect("/faculty-dashboard")

        # ================= STUDENT LOGIN =================
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


# ================= OLD DASHBOARD =================
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

        name = request.form["name"]
        roll_no = request.form["roll_no"]
        course = request.form["course"]
        email = request.form["email"]
        password = request.form["password"]

        password_hash = generate_password_hash(password)

        conn = sqlite3.connect("college.db")
        cursor = conn.cursor()

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

        name = request.form["name"]
        roll_no = request.form["roll_no"]
        course = request.form["course"]
        email = request.form["email"]

        new_password = request.form.get("password", "").strip()

        if new_password:

            password_hash = generate_password_hash(new_password)

            cursor.execute("""
                UPDATE students
                SET name=?, roll_no=?, course=?, email=?, password_hash=?
                WHERE id=?
            """, (
                name,
                roll_no,
                course,
                email,
                password_hash,
                id
            ))

        else:

            cursor.execute("""
                UPDATE students
                SET name=?, roll_no=?, course=?, email=?
                WHERE id=?
            """, (
                name,
                roll_no,
                course,
                email,
                id
            ))

        conn.commit()
        conn.close()

        return redirect("/students")

    cursor.execute("""
        SELECT id, name, roll_no, course, email
        FROM students
        WHERE id=?
    """, (id,))

    student = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_student.html",
        student=student
    )


# ================= DELETE STUDENT =================
@app.route("/delete-student/<int:id>")
def delete_student(id):

    if not session.get("logged_in"):
        return redirect("/login")

    if session.get("user_type") != "Admin":
        return redirect("/login")

    init_db()

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM attendance WHERE student_id=?",
        (id,)
    )

    cursor.execute(
        "DELETE FROM students WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/students")


# ================= FACULTY =================
@app.route("/faculty")
def faculty():

    if not session.get("logged_in"):
        return redirect("/login")

    if session.get("user_type") != "Admin":
        return redirect("/login")

    init_db()

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM faculty")

    faculty = cursor.fetchall()

    conn.close()

    return render_template(
        "faculty.html",
        faculty=faculty
    )


# ================= ADD FACULTY =================
@app.route("/add-faculty", methods=["GET", "POST"])
def add_faculty():

    if not session.get("logged_in"):
        return redirect("/login")

    if session.get("user_type") != "Admin":
        return redirect("/login")

    init_db()

    if request.method == "POST":

        name = request.form["name"]
        department = request.form["department"]
        email = request.form["email"]

        conn = sqlite3.connect("college.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO faculty
            (name, department, email)
            VALUES (?, ?, ?)
        """, (name, department, email))

        conn.commit()
        conn.close()

        return redirect("/faculty")

    return render_template("add_faculty.html")


# ================= COURSES =================
@app.route("/courses")
def courses():

    if not session.get("logged_in"):
        return redirect("/login")

    return render_template("courses.html")


# ================= ATTENDANCE =================
@app.route("/attendance", methods=["GET", "POST"])
def attendance():

    if not session.get("logged_in"):
        return redirect("/login")

    if session.get("user_type") not in ["Admin", "Faculty"]:
        return redirect("/login")

    init_db()

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    selected_branch = request.args.get("branch", "")

    if request.method == "POST":

        attendance_date = str(date.today())
        branch = request.form["branch"]

        cursor.execute(
            "SELECT id FROM students WHERE course=?",
            (branch,)
        )

        students = cursor.fetchall()

        for student in students:

            student_id = student[0]

            status = request.form.get(
                f"attendance_{student_id}"
            )
