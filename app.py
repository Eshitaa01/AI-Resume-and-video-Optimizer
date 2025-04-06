import streamlit as st
import fitz  # PyMuPDF
import docx
import google.generativeai as genai
from dotenv import load_dotenv
import os
from modules.ats_score import get_ats_score
import matplotlib.pyplot as plt
import assemblyai as aai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# 2️⃣ Functions to extract text
def extract_text_from_pdf(file):
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in pdf:
        text += page.get_text()
    return text.strip()

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs]).strip()

# 3️⃣ Streamlit UI
st.title("📄 AI Resume Optimizer")
st.markdown("Upload your **PDF or DOCX resume**, enter your **target job role**, and get AI-powered suggestions.")

uploaded_file = st.file_uploader("Upload Resume (.pdf or .docx)", type=["pdf", "docx"])
job_role = st.text_input("🎯 Target Job Role (e.g., Data Analyst)")

resume_text = ""

if uploaded_file:
    if uploaded_file.name.endswith(".pdf"):
        resume_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".docx"):
        resume_text = extract_text_from_docx(uploaded_file)
    else:
        st.error("Unsupported file format")

    # ✏️ Save extracted text to resume_improve.txt
    os.makedirs("prompts", exist_ok=True)
    with open("prompts/resume_improve.txt", "w", encoding="utf-8") as f:
        f.write(resume_text)

if resume_text:
    st.text_area("✍️ Extracted Resume Text (saved to resume_improve.txt)", resume_text, height=300)

# 4️⃣ Analyze with Gemini
if st.button("Analyze Resume"):
    if os.path.exists("prompts/resume_improve.txt") and job_role:
        with open("prompts/resume_improve.txt", "r", encoding="utf-8") as file:
            resume_text = file.read()

        prompt_template = "Please review the following resume for the role of {{job_role}} and suggest improvements:\n\n{{resume}}"
        final_prompt = prompt_template.replace("{{resume}}", resume_text).replace("{{job_role}}", job_role)
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(final_prompt)

        suggestions = response.text

        st.subheader("Suggestions from AI:")
        st.write(suggestions)

        os.makedirs("output", exist_ok=True)
        with open("output/result_resume1.txt", "w", encoding="utf-8") as out:
            out.write(suggestions)
    else:
        st.warning("Resume and job role required!")

# 5️⃣ ATS Score Checker (Gemini-based)
if st.button("📊 Check ATS Score"):
    if os.path.exists("prompts/resume_improve.txt") and job_role:
        with open("prompts/resume_improve.txt", "r", encoding="utf-8") as file:
            resume_text = file.read()
            ats_result, score, matched_keywords, missing_keywords = get_ats_score(resume_text, job_role)


        st.subheader("📈 ATS Score Report:")
        st.write(ats_result)

        os.makedirs("output", exist_ok=True)
        with open("output/ats_score.txt", "w", encoding="utf-8") as ats_file:
            ats_file.write(ats_result)
    else:
        st.warning("Please upload resume and enter job role.")

    st.progress(score)
    st.write(f"🎯 **ATS Compatibility Score: {score}/100**")
    
    labels = ['Matched Keywords', 'Missing Keywords']
    sizes = [len(matched_keywords), len(missing_keywords)]
    colors = ['#00cc99', '#ff6666']
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    ax.axis('equal')
    st.pyplot(fig)
    # Show keywords
    st.markdown("**Matched Keywords:**")
    if matched_keywords:
        st.write(", ".join(str(k) for k in matched_keywords))
    else:
        st.write("None found")
    st.markdown("** Missing Keywords:**")
    if missing_keywords:
        st.write(", ".join(str(k) for k in missing_keywords))
    else:
        st.write("None found")

from modules.chatbot import basic_chatbot

if 'messages' not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("ATS Assistant Chatbot 🤖")

    user_input = st.text_input("You:", key="user_input")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Get bot response using the chatbot function
        bot_response = basic_chatbot(user_input)

        st.session_state.messages.append({"role": "bot", "content": bot_response})

    # Display chatbot conversation
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"👤 You: {msg['content']}")
        else:
            st.markdown(f"🤖 Bot: {msg['content']}")

# 🎥 Video Resume Analyzer
st.header("🎥 Video Resume Analyzer (Video-to-Text)")
video_file = st.file_uploader("Upload a Video (.mp4, .webm)", type=["mp4", "webm"], key="video")

transcript = ""

if video_file:
    st.video(video_file)

    video_path = os.path.join("temp_video.mp4")
    with open(video_path, "wb") as f:
        f.write(video_file.read())

    st.info("⏳ Transcribing video with AssemblyAI...")

    try:
        transcriber = aai.Transcriber()
        transcript_obj = transcriber.transcribe(video_path)
        transcript = transcript_obj.text

        st.subheader("📝 Transcript from Video:")
        st.write(transcript)

        os.makedirs("output", exist_ok=True)
        with open("output/video_transcript.txt", "w", encoding="utf-8") as f:
            f.write(transcript)

    except Exception as e:
        st.error(f"Error during transcription: {e}")

# 💡 Improve Spoken Resume
if transcript:
    st.subheader("🤖 Improve Your Spoken Resume")

    if st.button("✨ Get AI Suggestions on Your Spoken Resume"):
        try:
            prompt_template = """
You are an expert career advisor. Analyze the following transcribed spoken resume. 
Evaluate it on communication clarity, structure, tone, and content relevance for a job application.
Provide detailed suggestions to improve the spoken delivery and phrasing.

Transcript:
\"\"\"
{transcript}
\"\"\"
            """
            final_prompt = """
You are an expert career advisor. Analyze the following transcribed spoken resume. 
Evaluate it on communication clarity, structure, tone, and content relevance for a job application.

Respond using markdown formatting and include emojis and bullet points under these sections:
- ✅ What is working well
- 🛠️ Areas of improvement
- 💬 Suggested improvements to phrasing and delivery

Transcript:
\"\"\"
{transcript}
\"\"\"
""".format(transcript=transcript)


            model = genai.GenerativeModel("models/gemini-1.5-flash")

            tone_prompt = f"""
You are a professional communication coach AI.

Evaluate the following transcribed spoken resume and provide only a **JSON response** with numeric scores (0–10) for the following tone aspects:

- confidence
- enthusiasm
- clarity
- professionalism

⚠️ Important: **Only return JSON**, without any explanation, markdown, or comments.

Transcript:
\"\"\"{transcript}\"\"\"
"""

            # Generate tone scores
            tone_response = model.generate_content(tone_prompt)
            import json

            try:
                cleaned_text = tone_response.text.strip()

                if cleaned_text.startswith("```json"):
                    cleaned_text = cleaned_text.replace("```json", "").replace("```", "").strip()

                tone_scores = json.loads(cleaned_text)

                st.subheader("📊 Tone Scores")

                def emoji_score(score):
                    if score >= 8: return "🟢"
                    elif score >= 5: return "🟡"
                    else: return "🔴"

                for key, value in tone_scores.items():
                    st.write(f"**{key.capitalize()}**: {value}/10 {emoji_score(value)}")

                import plotly.graph_objects as go

                categories = list(tone_scores.keys())
                values = list(tone_scores.values())

                # Close the radar loop by repeating the first value
                categories += [categories[0]]
                values += [values[0]]

                fig = go.Figure(
                    data=go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill='toself',
                        line=dict(color='royalblue')
                    )
                )
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 10])
                    ),
                    showlegend=False,
                    title="🎯 Tone Radar Chart"
                )

                st.plotly_chart(fig, use_container_width=True)


            except json.JSONDecodeError as e:
                st.error("Couldn't parse tone scores. Gemini response:\n\n" + tone_response.text)
                st.code(tone_response.text, language="json")  # Optional: helpful for debugging


            # Generate suggestions as before
            analysis_response = model.generate_content(final_prompt)
            suggestions = analysis_response.text

            st.subheader("💡 AI Suggestions:")
            st.write(suggestions)

            with open("output/video_analysis.txt", "w", encoding="utf-8") as f:
                f.write(suggestions)

        except Exception as e:
            st.error(f"Error during analysis: {e}")
