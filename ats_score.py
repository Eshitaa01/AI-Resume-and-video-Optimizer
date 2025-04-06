# ats_score.py

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def get_ats_score(resume_text, job_role):
    prompt = f"""
You are an expert ATS system.

Given this resume and the target job role: **{job_role}**, evaluate how well this resume matches common keywords and skills required for the role.

1. Give an **ATS compatibility score** out of 100.
2. List **matched keywords** and **missing keywords** (in comma-separated format).
3. Provide a **short suggestion** on how to improve the score.

Resume:
\"\"\"
{resume_text}
\"\"\"
"""

    model = genai.GenerativeModel("models/gemini-1.5-flash")
    response = model.generate_content(prompt)
    result_text = response.text

    import re
    score_match = re.search(r'(\d{1,3})/100', result_text)
    score = int(score_match.group(1)) if score_match else 0

    matched_section = re.search(r"(?i)matched keywords:\s*(.*?)\n", result_text)
    missing_section = re.search(r"(?i)missing keywords:\s*(.*?)\n", result_text)

    matched_keywords = [kw.strip("•* \n") for kw in matched_section.group(1).split(",")] if matched_section else []
    missing_keywords = [kw.strip("•* \n") for kw in missing_section.group(1).split(",")] if missing_section else []

    return result_text, score, matched_keywords, missing_keywords
