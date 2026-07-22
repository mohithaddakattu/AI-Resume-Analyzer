import google.generativeai as genai
import json
import time
import os

# Your Gemini API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Models to try (newest first)
MODELS = [
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.0-flash"
]


def get_resume_feedback(resume_text, jd=""):

    prompt = f"""
You are an ATS Resume Analyzer.

Analyze the resume against the given job description.

Resume:
{resume_text}

Job Description:
{jd}

Return ONLY valid JSON.

{{
    "ats_score": 0,
    "missing_skills": [],
    "strengths": [],
    "weaknesses": [],
    "suggestions": []
}}
"""

    for model_name in MODELS:

        try:

            model = genai.GenerativeModel(model_name)

            response = model.generate_content(prompt)

            text = response.text.strip()

            if text.startswith("```json"):
                text = text.replace("```json", "").replace("```", "").strip()

            return json.loads(text)

        except Exception as e:

            print(f"{model_name} failed:", e)

            time.sleep(2)

            continue

    return {
        "ats_score": 0,
        "missing_skills": [],
        "strengths": [],
        "weaknesses": [],
        "suggestions": [
            "Unable to generate AI feedback. All Gemini models are currently unavailable."
        ]
    }