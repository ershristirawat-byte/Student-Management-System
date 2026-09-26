from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)


# =========================
# DATABASE INITIALIZATION
# =========================

def init_db():

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    # Student Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_number TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL,
            phone TEXT,
            gender TEXT,
            dob TEXT
        )
    """)

    # Add missing columns to old database
    columns = [
        ("phone", "TEXT"),
        ("gender", "TEXT"),
        ("dob", "TEXT")
    ]

    for column_name, column_type in columns:

        try:
            cursor.execute(
                f"ALTER TABLE students ADD COLUMN {column_name} {column_type}"
            )

        except sqlite3.OperationalError:
            pass


    # Admin Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            username TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    try:
        cursor.execute(
            "ALTER TABLE admin ADD COLUMN password TEXT"
        )
    except sqlite3.OperationalError:
        pass

    cursor.execute("""
    UPDATE admin
    SET username = 'admin',
        password = 'Shristi@2026'
    WHERE id = 1
""")

    # Create default admin if not available
    cursor.execute("SELECT COUNT(*) FROM admin")
    admin_count = cursor.fetchone()[0]

    if admin_count == 0:

        cursor.execute("""
            INSERT INTO admin
            (id, name, username, email)
            VALUES (?, ?, ?, ?)
        """, (
            1,
            "Shristi_admin",
            "admin",
            "admin@studentmanagement.com"
             "Shristi@2026"
        ))

    conn.commit()
    conn.close()


# =========================
# LOGIN
# =========================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT username, password
            FROM admin
            WHERE id = 1
        """)

        admin = cursor.fetchone()

        conn.close()

        if username == "Shristi" and password == "Shristi@2026":
            return redirect(url_for("dashboard"))

        return "Invalid Username or Password"

    return render_template("login.html")


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    # Total students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    # Total courses
    cursor.execute(
        "SELECT COUNT(DISTINCT course) FROM students"
    )
    total_courses = cursor.fetchone()[0]

    # Recent students
    cursor.execute("""
        SELECT *
        FROM students
        ORDER BY id ASC
        LIMIT 5
    """)

    recent_students = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_courses=total_courses,
        recent_students=recent_students
    )


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    return redirect("/")


# =========================
# ADD STUDENT
# =========================

@app.route("/add_student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        course = request.form["course"]
        phone = request.form.get("phone", "")
        gender = request.form.get("gender", "")
        dob = request.form.get("dob", "")

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        # Generate automatic roll number starting from 101
        cursor.execute("SELECT MAX(CAST(roll_number AS INTEGER)) FROM students")
        result = cursor.fetchone()[0]

        if result is None or result < 101:
            roll_number = 101
        else:
            roll_number = result + 1

        cursor.execute("""
            INSERT INTO students
            (name, roll_number, email, course, phone, gender, dob)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            roll_number,
            email,
            course,
            phone,
            gender,
            dob
        ))

        conn.commit()
        conn.close()

        return redirect("/students")

    return render_template("add_student.html")



# =========================
# VIEW STUDENTS
# =========================

@app.route("/students")
def students():

    conn = sqlite3.connect("students.db")

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM students
        ORDER BY id ASC
    """)

    students = cursor.fetchall()

    conn.close()

    return render_template(
        "students.html",
        students=students
    )


# =========================
# DELETE STUDENT
# =========================

@app.route("/delete_student/<int:id>")
def delete_student(id):

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/students")


# =========================
# UPDATE STUDENT
# =========================

@app.route(
    "/update_student/<int:id>",
    methods=["GET", "POST"]
)
def update_student(id):

    conn = sqlite3.connect("students.db")

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()


    if request.method == "POST":

        name = request.form["name"]
        roll_number = request.form["roll_number"]
        email = request.form["email"]
        course = request.form["course"]
        phone = request.form.get("phone", "")
        gender = request.form.get("gender", "")
        dob = request.form.get("dob", "")


        cursor.execute("""
            UPDATE students
            SET
                name = ?,
                roll_number = ?,
                email = ?,
                course = ?,
                phone = ?,
                gender = ?,
                dob = ?
            WHERE id = ?
        """, (
            name,
            roll_number,
            email,
            course,
            phone,
            gender,
            dob,
            id
        ))


        conn.commit()
        conn.close()

        return redirect("/students")


    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    )

    student = cursor.fetchone()

    conn.close()

    return render_template(
        "update_student.html",
        student=student
    )

# =========================
# SEARCH STUDENT
# =========================

@app.route("/search", methods=["GET", "POST"])
def search():

    students = []

    if request.method == "POST":

        keyword = request.form.get("keyword", "").strip()

        conn = sqlite3.connect("students.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM students
            WHERE
                name LIKE ?
                OR roll_number LIKE ?
                OR email LIKE ?
                OR course LIKE ?
                OR phone LIKE ?
                OR gender LIKE ?
                OR dob LIKE ?
        """, (
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%"
        ))

        students = cursor.fetchall()

        conn.close()

    return render_template(
        "search.html",
        students=students
    )
       
# =========================
# STUDENT PROFILE
# =========================

@app.route("/student_profile/<int:id>")
def student_profile(id):

    conn = sqlite3.connect("students.db")

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()


    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    )

    student = cursor.fetchone()

    conn.close()


    if student is None:

        return "Student not found"


    return render_template(
        "student_profile.html",
        student=student
    )


# =========================
# ADMIN PROFILE
# =========================

@app.route("/admin_profile")
def admin_profile():

    conn = sqlite3.connect("students.db")

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()


    cursor.execute(
        "SELECT * FROM admin WHERE id = 1"
    )

    admin = cursor.fetchone()

    conn.close()


    return render_template(
        "admin_profile.html",
        admin=admin
    )


# =========================
# EDIT ADMIN PROFILE
# =========================

@app.route(
    "/edit_admin",
    methods=["GET", "POST"]
)
def edit_admin():

    conn = sqlite3.connect("students.db")

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()


    if request.method == "POST":

        name = request.form["name"]
        username = request.form["username"]
        email = request.form["email"]


        cursor.execute("""
            UPDATE admin
            SET
                name = ?,
                username = ?,
                email = ?
            WHERE id = 1
        """, (
            name,
            username,
            email
        ))


        conn.commit()
        conn.close()


        return redirect("/admin_profile")


    cursor.execute(
        "SELECT * FROM admin WHERE id = 1"
    )

    admin = cursor.fetchone()

    conn.close()


    return render_template(
        "edit_admin.html",
        admin=admin
    )

@app.route("/change_password", methods=["GET", "POST"])
def change_password():

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password FROM admin WHERE id = 1"
        )

        admin = cursor.fetchone()

        if not admin or current_password != admin[0]:
            conn.close()
            return "Current password is incorrect."

        if new_password != confirm_password:
            conn.close()
            return "New passwords do not match."

        cursor.execute("""
            UPDATE admin
            SET password = ?
            WHERE id = 1
        """, (new_password,))

        conn.commit()
        conn.close()

        return redirect("/admin_profile")

    return render_template("change_password.html")

# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True,
        port=8000
    )

    