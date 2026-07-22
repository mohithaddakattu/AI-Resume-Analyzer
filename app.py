from flask import Flask, render_template, request
import pdfplumber
import sqlite3
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from resume_analyzer import extract_skills
from gemini_ai import get_resume_feedback

app = Flask(__name__)


# -----------------------------
# Extract text from PDF
# -----------------------------
def extract_text(pdf):
    text = ""

    with pdfplumber.open(pdf) as pdf_file:
        for page in pdf_file.pages:
            text += page.extract_text() or ""

    return text


# -----------------------------
# Home
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# Resume Analysis
# -----------------------------
@app.route("/analyze", methods=["POST"])
def analyze():

    resume = request.files["resume"]
    jd = request.form.get("jd", "")

    resume_text = extract_text(resume)

    # Detect skills
    skills = extract_skills(resume_text)

    # -----------------------------
    # Cosine Similarity Score
    # -----------------------------
    similarity = 0

    if jd.strip() != "":
        cv = CountVectorizer()
        matrix = cv.fit_transform([resume_text, jd])
        similarity = cosine_similarity(matrix)[0][1]
        similarity = round(similarity * 100, 2)

    # -----------------------------
    # Gemini AI Feedback
    # -----------------------------
    feedback = get_resume_feedback(resume_text, jd)

    # Use Gemini ATS score if available
    ats_score = feedback.get("ats_score")

    if ats_score is None:
        ats_score = similarity

    # -----------------------------
    # Save to Database
    # -----------------------------
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            ats_score REAL,
            feedback TEXT
        )
    """)

    cursor.execute("""
        INSERT INTO reports(name, ats_score, feedback)
        VALUES (?, ?, ?)
    """, (
        resume.filename,
        ats_score,
        str(feedback)
    ))

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        score=ats_score,
        feedback=feedback,
        skills=skills,
        similarity=similarity
    )


# -----------------------------
# Dashboard
# -----------------------------
@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM reports")
    data = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        data=data
    )


# -----------------------------
# Interview Page
# -----------------------------
@app.route("/interview")
def interview():
    return render_template("interview.html")


# -----------------------------
# Interview Evaluation
# -----------------------------
@app.route("/interview", methods=["POST"])
def interview_feedback():

    answer = request.form["answer"]

    words = len(answer.split())

    if words >= 100:
        score = 90
        feedback = "Excellent answer with detailed explanation."

    elif words >= 60:
        score = 75
        feedback = "Good answer, but could include more details."

    else:
        score = 50
        feedback = "Answer is too short. Add more explanation."

    return render_template(
        "interview_result.html",
        score=score,
        feedback=feedback
    )


if __name__ == "__main__":
    app.run(debug=True)