from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/students")
def students():
    import sqlite3

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

        import sqlite3
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

        cursor.execute(
            "INSERT INTO students (name, roll_no, course, email) VALUES (?, ?, ?, ?)",
            (name, roll_no, course, email)
        )

        conn.commit()
        conn.close()

        return redirect("/students")

    return render_template("add_student.html")

if __name__ == "__main__":
    app.run(debug=True)
