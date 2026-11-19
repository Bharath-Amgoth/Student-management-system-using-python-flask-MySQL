#import the Flask class
from flask import Flask, render_template,request,redirect,url_for,session,send_from_directory
#import the mysql connector
import mysql.connector as mysql
#create the connection 
con=mysql.connect(host="localhost",user="root",
                   password="Bharath@123",
                   database="student_management")
cur=con.cursor()
#create the object for flask class
app=Flask(__name__)
app.secret_key="student_management_secret_key_2026"
#we always create the view using function
@app.route("/") #default page or landing page
def home():
    return redirect(url_for("signup"))
@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        username=request.form["username"]
        email=request.form["email"]
        password=request.form["password"]
        query="""insert into users(username,email,password)
        values(%s,%s,%s)"""
        values = (username,email,password)
        try:
            cur.execute(query,values)
            con.commit()
            return redirect(url_for("login"))
        except Exception as e:
            con.rollback()
            return f"Regisration Failed:{e}"
    return send_from_directory("templates","signup.html")
    #user login
@app.route("/login",methods=["GET","POST"])
def login():
        if request.method=="POST":
                email=request.form["email"]
                password=request.form["password"]
                query="select * from users where email = %s"
                cur.execute(query,(email,))
                user = cur.fetchone()
                if user and user[3]==password:
                     session["user_id"]=user[0]
                     session["username"]=user[1]
                     return redirect(url_for("dashboard"))
                else:
                     return "invalid email or password"
        return send_from_directory("templates","login.html")
#Dashboard
@app.route("/dashboard")
def dashboard():
     if "user_id" not in session:
          return redirect(url_for("login"))
     return send_from_directory("templates","dashboard.html")
#Add Student
@app.route("/add_students",methods=["GET","POST"])
def add_students():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method=="POST":
        firstname=request.form["firstname"]
        lastname=request.form["lastname"]
        email=request.form["email"]
        age=request.form["age"]
        course=request.form["course"]
        mobileno=request.form["mobileno"]
        query="""insert into students(firstname,lastname,email,age,course,mobileno)
        values(%s,%s,%s,%s,%s,%s)"""
        values = (firstname,lastname,email,age,course,mobileno)
        try:
            cur.execute(query,values)
            con.commit()
            return"""Student added successfully!
            <br><a href="/add_students">Add Another Student</a>
            <br><a href="/dashboard">Go to Dashboard</a>
            """
        except Exception as e:
            con.rollback()
            return f"Failed to add student: {e}"
    return send_from_directory("templates","add_students.html")
#view students
@app.route("/view_students")
def view_students():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return send_from_directory("templates","view_students.html")
#fetch the student data from the database
@app.route("/api/students")
def get_students():
    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401
    query = "SELECT * FROM students"
    cur.execute(query)
    records = cur.fetchall()
    students= []
    for record in records:
        students.append({
            "id": record[0],
            "firstname": record[1],
            "lastname": record[2],
            "email": record[3],
            "age": record[4],
            "course": record[5],
            "mobileno": record[6]
        })
    return students
#update student page
@app.route("/update_student/<int:student_id>", methods=["GET", "POST"])
def update_student(student_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"]
        age = request.form["age"]
        course = request.form["course"]
        mobileno = request.form["mobileno"]
        query = """UPDATE students SET firstname=%s, lastname=%s, email=%s, age=%s, course=%s, mobileno=%s WHERE id=%s"""
        values = (firstname, lastname, email, age, course, mobileno, student_id)
        try:
            cur.execute(query, values)
            con.commit()
            return redirect(url_for("view_students"))
        except Exception as e:
            con.rollback()
            return f"Failed to update student: {e}"
    return send_from_directory("templates","update_student.html")
#Get Individual Student Data
@app.route("/api/student/<int:student_id>")
def get_student(student_id):
    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401
    query = "SELECT * FROM students WHERE id=%s"
    cur.execute(query, (student_id,))
    student = cur.fetchone()
    if student is None:
        return {"error": "Student not found"}, 404
    return {
        "id": student[0],
        "firstname": student[1],
        "lastname": student[2],
        "email": student[3],
        "age": student[4],
        "course": student[5],
        "mobileno": student[6]
    }
#Delete Student
@app.route("/delete_student/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    try:
        query = "DELETE FROM students WHERE id=%s"
        cur.execute(query, (student_id,))
        con.commit()
        return redirect(url_for("view_students"))
    except Exception as e:
        con.rollback()
        return f"Failed to delete student: {e}"
#Logout
@app.route("/logout")
def logout():
     session.clear()
     return redirect(url_for("login"))
if __name__=="__main__":
    app.run(debug=True)
