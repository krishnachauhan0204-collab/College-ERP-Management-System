from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date

app = Flask(__name__)


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


# ================= DASHBOARD =================
@app.route("/")
def home():
    init_db()

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM faculty")
    total_faculty = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        total_students=total_students,
        total_faculty=total_faculty
    )


# ================= STUDENTS =================
@app.route("/students")
def students():
    init_db()

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()

    return render_template("students.html", students=students)


# ================= ADD STUDENT =================
@app.route("/add-student", methods=["GET", "POST"])
def add_student():

    init_db()

    if request.method == "POST":

        name = request.form["name"]
        course = request.form["course"]
        email = request.form["email"]

        conn = sqlite3.connect("college.db")
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM students")
        count = cursor.fetchone()[0] + 1

        roll_no = f"ENR{count:03d}"

        cursor.execute("""
            INSERT INTO students
            (name, roll_no, course, email)
            VALUES (?, ?, ?, ?)
        """, (name, roll_no, course, email))

        conn.commit()
        conn.close()

        return redirect("/students")

    return render_template("add_student.html")


# ================= EDIT STUDENT =================
@app.route("/edit-student/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    init_db()

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        course = request.form["course"]
        email = request.form["email"]

        cursor.execute("""
            UPDATE students
            SET name=?, course=?, email=?
            WHERE id=?
        """, (name, course, email, id))

        conn.commit()
        conn.close()

        return redirect("/students")

    cursor.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    )

    student = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_student.html",
        student=student
    )


# ================= DELETE STUDENT =================
@app.route("/delete-student/<int:id>")
def delete_student(id):

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
    return render_template("courses.html")


# ================= ATTENDANCE =================
@app.route("/attendance", methods=["GET", "POST"])
def attendance():

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

            if status:

                cursor.execute("""
                    INSERT INTO attendance
                    (student_id, attendance_date, status)
                    VALUES (?, ?, ?)
                """, (
                    student_id,
                    attendance_date,
                    status
                ))

        conn.commit()
        conn.close()

        return redirect(
            f"/attendance?branch={branch}"
        )

    if selected_branch:

        cursor.execute("""
            SELECT * FROM students
            WHERE course=?
            ORDER BY id
        """, (selected_branch,))

    else:

        cursor.execute("""
            SELECT * FROM students
            ORDER BY id
        """)

    students = cursor.fetchall()

    conn.close()

    return render_template(
        "attendance.html",
        students=students,
        selected_branch=selected_branch
    )


# ================= ATTENDANCE REPORT =================
@app.route("/attendance-report")
def attendance_report():

    init_db()

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            students.id,
            students.name,
            students.roll_no,
            students.course,
            COUNT(attendance.id),
            SUM(
                CASE
                    WHEN attendance.status='Present'
                    THEN 1
                    ELSE 0
                END
            )
        FROM students
        LEFT JOIN attendance
        ON students.id = attendance.student_id
        GROUP BY students.id
    """)

    records = cursor.fetchall()

    conn.close()

    return render_template(
        "attendance_report.html",
        records=records
    )


# ================= FEES =================
@app.route("/fees")
def fees():
    return render_template("fees.html")


# ================= REPORTS =================
@app.route("/reports")
def reports():

    init_db()

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()

    return render_template(
        "reports.html",
        students=students
    )


# ================= RUN =================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
