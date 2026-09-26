from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


# =========================
# DATABASE
# =========================

def init_db():
    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    # Students Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT NOT NULL,
            course TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)

    # Faculty Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            faculty_id TEXT NOT NULL,
            department TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)

    # Courses Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            course_code TEXT NOT NULL,
            department TEXT NOT NULL,
            semester TEXT NOT NULL
        )
    """)

    # Attendance Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            enrollment_no TEXT NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    # Fees Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            enrollment_no TEXT NOT NULL,
            course TEXT NOT NULL,
            total_fees REAL NOT NULL,
            paid_fees REAL NOT NULL,
            pending_fees REAL NOT NULL,
            status TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================
# DASHBOARD
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# STUDENT MANAGEMENT
# =========================

@app.route("/students")
def students():
    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()

    return render_template("students.html", students=students)


@app.route("/add-student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":
        name = request.form["name"]
        roll_no = request.form["roll_no"]
        course = request.form["course"]
        email = request.form["email"]

        conn = sqlite3.connect("college.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO students (name, roll_no, course, email)
            VALUES (?, ?, ?, ?)
        """, (name, roll_no, course, email))

        conn.commit()
        conn.close()

        return redirect("/students")

    return render_template("add_student.html")


@app.route("/edit-student/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        roll_no = request.form["roll_no"]
        course = request.form["course"]
        email = request.form["email"]

        cursor.execute("""
            UPDATE students
            SET name = ?, roll_no = ?, course = ?, email = ?
            WHERE id = ?
        """, (name, roll_no, course, email, id))

        conn.commit()
        conn.close()

        return redirect("/students")

    cursor.execute("SELECT * FROM students WHERE id = ?", (id,))
    student = cursor.fetchone()

    conn.close()

    return render_template("edit_student.html", student=student)


@app.route("/delete-student/<int:id>")
def delete_student(id):

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect("/students")


# =========================
# FACULTY MANAGEMENT
# =========================

@app.route("/faculty")
def faculty():
    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM faculty")
    faculties = cursor.fetchall()

    conn.close()

    return render_template("faculty.html", faculties=faculties)


@app.route("/add-faculty", methods=["GET", "POST"])
def add_faculty():

    if request.method == "POST":
        name = request.form["name"]
        faculty_id = request.form["faculty_id"]
        department = request.form["department"]
        email = request.form["email"]

        conn = sqlite3.connect("college.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO faculty (name, faculty_id, department, email)
            VALUES (?, ?, ?, ?)
        """, (name, faculty_id, department, email))

        conn.commit()
        conn.close()

        return redirect("/faculty")

    return render_template("add_faculty.html")


@app.route("/edit-faculty/<int:id>", methods=["GET", "POST"])
def edit_faculty(id):

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        faculty_id = request.form["faculty_id"]
        department = request.form["department"]
        email = request.form["email"]

        cursor.execute("""
            UPDATE faculty
            SET name = ?, faculty_id = ?, department = ?, email = ?
            WHERE id = ?
        """, (name, faculty_id, department, email, id))

        conn.commit()
        conn.close()

        return redirect("/faculty")

    cursor.execute(
        "SELECT * FROM faculty WHERE id = ?",
        (id,)
    )

    faculty_data = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_faculty.html",
        faculty=faculty_data
    )


@app.route("/delete-faculty/<int:id>")
def delete_faculty(id):

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM faculty WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

  
    # =========================
# COURSES & SUBJECTS
# =========================

@app.route("/courses")
def courses():
    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM courses")
    courses_data = cursor.fetchall()

    conn.close()

    return render_template("courses.html", courses=courses_data)


@app.route("/add-course", methods=["GET", "POST"])
def add_course():

    if request.method == "POST":
        course_name = request.form["course_name"]
        course_code = request.form["course_code"]
        department = request.form["department"]
        semester = request.form["semester"]

        conn = sqlite3.connect("college.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO courses
            (course_name, course_code, department, semester)
            VALUES (?, ?, ?, ?)
        """, (
            course_name,
            course_code,
            department,
            semester
        ))

        conn.commit()
        conn.close()

        return redirect("/courses")

    return render_template("add_course.html")


@app.route("/edit-course/<int:id>", methods=["GET", "POST"])
def edit_course(id):

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    if request.method == "POST":

        course_name = request.form["course_name"]
        course_code = request.form["course_code"]
        department = request.form["department"]
        semester = request.form["semester"]

        cursor.execute("""
            UPDATE courses
            SET course_name = ?,
                course_code = ?,
                department = ?,
                semester = ?
            WHERE id = ?
        """, (
            course_name,
            course_code,
            department,
            semester,
            id
        ))

        conn.commit()
        conn.close()

        return redirect("/courses")

    cursor.execute(
        "SELECT * FROM courses WHERE id = ?",
        (id,)
    )

    course = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_course.html",
        course=course
    )


@app.route("/delete-course/<int:id>")
def delete_course(id):

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM courses WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/courses")
     # =========================
# ATTENDANCE MANAGEMENT
# =========================

@app.route("/attendance")
def attendance():
    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM attendance")
    attendance_data = cursor.fetchall()

    conn.close()

    return render_template(
        "attendance.html",
        attendances=attendance_data
    )


@app.route("/add-attendance", methods=["GET", "POST"])
def add_attendance():

    if request.method == "POST":

        student_name = request.form["student_name"]
        enrollment_no = request.form["enrollment_no"]
        date = request.form["date"]
        status = request.form["status"]

        conn = sqlite3.connect("college.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO attendance
            (student_name, enrollment_no, date, status)
            VALUES (?, ?, ?, ?)
        """, (
            student_name,
            enrollment_no,
            date,
            status
        ))

        conn.commit()
        conn.close()

        return redirect("/attendance")

    return render_template("add_attendance.html")


@app.route("/edit-attendance/<int:id>", methods=["GET", "POST"])
def edit_attendance(id):

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    if request.method == "POST":

        student_name = request.form["student_name"]
        enrollment_no = request.form["enrollment_no"]
        date = request.form["date"]
        status = request.form["status"]

        cursor.execute("""
            UPDATE attendance
            SET student_name = ?,
                enrollment_no = ?,
                date = ?,
                status = ?
            WHERE id = ?
        """, (
            student_name,
            enrollment_no,
            date,
            status,
            id
        ))

        conn.commit()
        conn.close()

        return redirect("/attendance")

    cursor.execute(
        "SELECT * FROM attendance WHERE id = ?",
        (id,)
    )

    attendance_data = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_attendance.html",
        attendance=attendance_data
    )


@app.route("/delete-attendance/<int:id>")
def delete_attendance(id):

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM attendance WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/attendance")
    # =========================
# FEES MANAGEMENT
# =========================

@app.route("/fees")
def fees():
    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM fees")
    fees_data = cursor.fetchall()

    conn.close()

    return render_template(
        "fees.html",
        fees=fees_data
    )


@app.route("/add-fee", methods=["GET", "POST"])
def add_fee():

    if request.method == "POST":

        student_name = request.form["student_name"]
        enrollment_no = request.form["enrollment_no"]
        course = request.form["course"]

        total_fees = float(request.form["total_fees"])
        paid_fees = float(request.form["paid_fees"])

        pending_fees = total_fees - paid_fees

        if pending_fees <= 0:
            pending_fees = 0
            status = "Paid"
        else:
            status = "Pending"

        conn = sqlite3.connect("college.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO fees
            (student_name, enrollment_no, course,
             total_fees, paid_fees, pending_fees, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            student_name,
            enrollment_no,
            course,
            total_fees,
            paid_fees,
            pending_fees,
            status
        ))

        conn.commit()
        conn.close()

        return redirect("/fees")

    return render_template("add_fee.html")


@app.route("/edit-fee/<int:id>", methods=["GET", "POST"])
def edit_fee(id):

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    if request.method == "POST":

        student_name = request.form["student_name"]
        enrollment_no = request.form["enrollment_no"]
        course = request.form["course"]

        total_fees = float(request.form["total_fees"])
        paid_fees = float(request.form["paid_fees"])

        pending_fees = total_fees - paid_fees

        if pending_fees <= 0:
            pending_fees = 0
            status = "Paid"
        else:
            status = "Pending"

        cursor.execute("""
            UPDATE fees
            SET student_name = ?,
                enrollment_no = ?,
                course = ?,
                total_fees = ?,
                paid_fees = ?,
                pending_fees = ?,
                status = ?
            WHERE id = ?
        """, (
            student_name,
            enrollment_no,
            course,
            total_fees,
            paid_fees,
            pending_fees,
            status,
            id
        ))

        conn.commit()
        conn.close()

        return redirect("/fees")

    cursor.execute(
        "SELECT * FROM fees WHERE id = ?",
        (id,)
    )

    fee = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_fee.html",
        fee=fee
    )


@app.route("/delete-fee/<int:id>")
def delete_fee(id):

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM fees WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/fees")
    # =========================
# REPORTS
# =========================

@app.route("/reports")
def reports():

    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM faculty")
    total_faculty = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM courses")
    total_courses = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attendance")
    total_attendance = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM fees")
    total_fee_records = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total_fees) FROM fees")
    total_fees = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(paid_fees) FROM fees")
    paid_fees = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(pending_fees) FROM fees")
    pending_fees = cursor.fetchone()[0] or 0

    conn.close()

    return render_template(
        "reports.html",
        total_students=total_students,
        total_faculty=total_faculty,
        total_courses=total_courses,
        total_attendance=total_attendance,
        total_fee_records=total_fee_records,
        total_fees=total_fees,
        paid_fees=paid_fees,
        pending_fees=pending_fees
    )
if __name__ == "__main__":
    init_db()
    app.run(debug=True)