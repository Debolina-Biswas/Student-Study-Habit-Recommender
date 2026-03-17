from flask import Flask, render_template, request, redirect, session
import pandas as pd
import random
import os

app = Flask(__name__)
app.secret_key = "study_ai_project"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- LOAD DATA ----------------

attention_df = pd.read_csv("attention_span.csv")
learning_df = pd.read_csv("learning_methods.csv")
quiz_df = pd.read_csv("quiz_results.csv")
study_df = pd.read_csv("study_hours.csv")

users_df = pd.read_excel("users.xlsx")
users_df.columns = users_df.columns.str.strip()

students_df = study_df.merge(quiz_df, on="student_id") \
                      .merge(attention_df, on="student_id") \
                      .merge(learning_df, on="student_id")




# ---------------- HOME ----------------

@app.route("/")
def home():
    return """
    <h2>Study Behavior Analysis System</h2>
    <a href='/student_login'>Student Login</a><br><br>
    <a href='/admin_login'>Admin Login</a>
    """

# ---------------- STUDENT LOGIN ----------------

@app.route("/student_login", methods=["GET","POST"])
def student_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = users_df[
            (users_df["student_id"] == username) &
            (users_df["password"].astype(str) == password)
        ]

        if len(user) == 0:
            return "Invalid Student Login"

        session["username"] = username
        session["role"] = "Student"

        return redirect("/student_dashboard")

    return render_template("student_login.html")

# ---------------- ADMIN LOGIN ----------------
@app.route("/admin_login", methods=["GET","POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = users_df[
            (users_df["student_id"] == username) &
            (users_df["password"].astype(str) == password) &
            (users_df["role"] == "Admin")
        ]

        if len(user) == 0:
            return "Invalid Admin Login"

        session["username"] = username
        session["role"] = "Admin"

        return redirect("/admin_dashboard")

    return render_template("admin_login.html")


# ---------------- STUDENT DASHBOARD ----------------
# Milestone 3 + Milestone 4

@app.route("/student_dashboard")
def student_dashboard():

    if session.get("role") != "Student":
        return redirect("/")

    student_id = session["username"]

    student = students_df[students_df["student_id"] == student_id].iloc[0]

    study_hours = student["study_hours"]
    quiz_score = student["quiz_score"]

    # Weekly Study Plan
    optimal_times = ["8:00-10:00 AM","2:00-3:30 PM","7:00-8:30 PM"]
    study_duration = "90 minutes with 15 minute breaks"
    break_schedule = "5 minute break every 25 minutes"

    # Weekly Study Schedule Chart
    weekly_hours = [
        round(study_hours + random.uniform(-1,1),2)
        for _ in range(7)
    ]

    # Expected Performance
    performance = [
        quiz_score,
        min(quiz_score + random.randint(3,6),100),
        min(quiz_score + random.randint(7,12),100),
        min(quiz_score + random.randint(12,18),100)
    ]

    # Recommended Tools
    learning_method = student["learning_method"]

    if learning_method == "Visual":
        tools = ["Mind Maps","Flashcards","Digital Notes"]

    elif learning_method == "Auditory":
        tools = ["Focus Music","Recorded Lectures","Podcasts"]

    else:
        tools = ["Pomodoro Timer","Practice Tests","Site Blocker"]

    # Weekly Study Routine
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

    routine = [
        f"{day} : Study {round(study_hours + random.uniform(-1,1),1)} hours"
        for day in days
    ]

    return render_template(
        "student_dashboard.html",
        optimal_times=optimal_times,
        study_duration=study_duration,
        break_schedule=break_schedule,
        weekly_hours=weekly_hours,
        performance=performance,
        tools=tools,
        routine=routine
    )
# ---------------- STUDY SESSION LOG ----------------

@app.route("/log_session", methods=["POST"])
def log_session():

    if session.get("role") != "Student":
        return redirect("/")

    date = request.form["date"]
    duration = request.form["duration"]
    subject = request.form["subject"]
    distraction = request.form["distraction"]
    score = request.form["score"]

    print("Study Session Logged:", date, duration, subject, distraction, score)

    return redirect("/student_dashboard")

# ---------------- STUDENT STUDY TRACKER ----------------

@app.route("/study_tracker")
def study_tracker():

    if session.get("role") != "Student":
        return redirect("/")

    return render_template("study_tracker.html")

# ---------------- ADMIN DASHBOARD ----------------
# Milestone 1 + Milestone 2

@app.route("/admin_dashboard")
def admin_dashboard():

    if session.get("role") != "Admin":
        return redirect("/")
    return render_template("admin_dashboard.html")

    total_students = len(students_df)

    avg_performance = round(students_df["quiz_score"].mean(),2)

    avg_study = round(students_df["study_hours"].mean(),2)

    avg_stress = round(students_df["attention_span"].mean(),2)

    correlation = round(
        students_df["study_hours"].corr(students_df["quiz_score"]),2
    )

    students = students_df.to_dict(orient="records")

    return render_template(
        "admin_dashboard.html",
        total_students=total_students,
        avg_performance=avg_performance,
        avg_stress=avg_stress,
        students=students
    )

@app.route("/milestone1")
def milestone1():

    if session.get("role") != "Admin":
        return redirect("/")

    study = students_df["study_hours"].tolist()
    scores = students_df["quiz_score"].tolist()

    distractions = ["Low","Medium","High"]
    performance = [85,75,65]

    return render_template(
        "milestone1.html",
        study=study,
        scores=scores,
        distractions=distractions,
        performance=performance
    )


# ---------------- CLUSTERING (Milestone 2) ----------------

@app.route("/milestone2")
def milestone2():

    if session.get("role") != "Admin":
        return redirect("/")

    focused = 0
    short = 0
    night = 0
    distracted = 0

    for i, row in students_df.iterrows():

        if row["study_hours"] > 4 and row["attention_span"] > 60:
            focused += 1

        elif row["study_hours"] < 2:
            short += 1

        elif row["attention_span"] < 40:
            distracted += 1

        else:
            night += 1

    cluster_data = [focused, short, night, distracted]

    return render_template(
        "milestone2.html",
        cluster_data=cluster_data   
    )

# ---------------- ADMIN PANEL (Milestone 4) ----------------


# ---------------- ADMIN PANEL ----------------

@app.route("/admin_panel", methods=["GET","POST"])
def admin_panel():

    if session.get("role") != "Admin":
        return redirect("/admin_login")



    # -------- FILE UPLOAD --------
    if request.method == "POST":

        if "file" in request.files:
            file = request.files["file"]

            if file.filename != "":
                path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(path)

# -------- SYSTEM METRICS --------

    total_students = len(students_df)

    total_sessions = random.randint(7000,9000)

    accuracy = round(random.uniform(92,96),2)

    retrain_days = random.randint(5,15)

# -------- ACADEMIC OVERVIEW --------

    avg_score = round(students_df["quiz_score"].mean(),2)

    avg_study = round(students_df["study_hours"].mean(),2)
    
    avg_stress = round(students_df["attention_span"].mean(),2)

    correlation = round(students_df["study_hours"].corr(students_df["quiz_score"]),2)

    students = students_df.to_dict(orient="records")

    return render_template(
        "admin_panel.html",
        total_students=total_students,
        total_sessions=total_sessions,
        accuracy=accuracy,
        retrain_days=retrain_days,
        avg_score=avg_score,
        avg_study=avg_study,
        avg_stress=avg_stress,
        correlation=correlation,
        students=students
    )

@app.route("/quick_retrain", methods=["POST"])
def quick_retrain():

    if session.get("role") != "Admin":
        return redirect("/")

    print("Quick Retrain Started")

    # Example: simulate retraining
    accuracy = round(random.uniform(93,97),2)

    return f"""
    <h2>Quick Retraining Completed</h2>
    <p>New Model Accuracy: {accuracy}%</p>
    <a href='/admin_panel'>Back to Admin Panel</a>
    """

@app.route("/full_retrain", methods=["POST"])
def full_retrain():

    if session.get("role") != "Admin":
        return redirect("/")

    print("Full Retrain Started")

    # Simulate full retraining
    accuracy = round(random.uniform(95,99),2)

    return f"""
    <h2>Full Model Retraining Completed</h2>
    <p>New Model Accuracy: {accuracy}%</p>
    <a href='/admin_panel'>Back to Admin Panel</a>
    """

    

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)
