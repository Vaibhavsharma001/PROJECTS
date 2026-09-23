import streamlit as st 
import PyPDF2  #allows Python to read PDF files.
import os
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI API key not found.please add it to your .env file")
    st.stop()
    
client = genai.Client(api_key = api_key)    
skills = [
    "python",
    "java",
    "javascript",
    "react",
    "html",
    "css",
    "sql",
    "mongodb",
    "git",
    "github",
    "streamlit",
    "django",
    "flask",
    "fastapi",
    "machine learning",
    "data science",
    "aws",
    "docker",
    "kubernetes",
    "jenkins",
    "redis",
    "postgresql",
    "linux",
    "azure"
]

st.title("AI Resume & Job Analyzer")
st.write("Analyze your resume against a job description")
st.subheader("Upload Your Resume")

resume = st.file_uploader("Upload Your Resume",
                 type = ["pdf"])

if resume:
    pdf_reader = PyPDF2.PdfReader(resume)
    
    st.write("Resume uploaded successfully!")
    st.write("Number of pages:", len(pdf_reader.pages))
    
    resume_text =""
    
    for page in pdf_reader.pages:
     text = page.extract_text()
     
     if text:
         resume_text+=text 
         
    if not resume_text.strip():
        st.warning("Could not extract text from this PDF. Please upload a text-based resume.")
        st.stop()

    st.write("Resume text:")
    st.write(resume_text) 
    
  
st.subheader("Job description")
job_description = st.text_area(
    "Paste job description here"
    ,height = 250)

if st.button("Analyze Resume"): 
    
    if not resume:
        st.warning("Upload your resume")
        
    elif not job_description.strip():
        st.warning("Please enter a job description.")
        
    else:
        resume_lower = resume_text.lower()
        job_lower = job_description.lower()

        st.write("Resume text length:", len(resume_lower))
        st.write("Job description length:", len(job_lower))

        matching_skills = []

        for skill in skills:
            if skill in resume_lower and skill in job_lower:
                matching_skills.append(skill)

        missing_skills = []

        for skill in skills:
            if skill in job_lower and skill not in resume_lower:
                missing_skills.append(skill)

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("✅ Matching Skills")

        if matching_skills:
            for skill in matching_skills:
                st.success(skill)
        else:
            st.write("No matching skills found.")


        with col2:
            st.subheader("❌ Missing Skills")

        if missing_skills:
            for skill in missing_skills:
                st.warning(skill)
        else:
            st.write("No missing skills found.")  

        total_required_skills = len(matching_skills) + len(missing_skills)

        if total_required_skills > 0:
            ats_score = (len(matching_skills) / total_required_skills) * 100
        else:
            ats_score = 0

        st.subheader("ATS SCORE")
        # st.metric() creates a large dashboard-style number.
        st.metric(            
            label = "Resume Match",
            value = f"{ats_score:.0f}%"
        )
        st.progress(ats_score/100)
        
        st.subheader("AI Analysis")

        prompt = f"""
You are an expert resume reviewer and career advisor.

Analyze the candidate's resume against the given job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Provide the following sections:

1. Overall Suitability
Give a short assessment of how suitable the candidate is for this job.

2. Matching Skills
List the important skills from the job description that are present in the resume.

3. Missing Skills
List the important skills from the job description that are missing from the resume.

4. Experience Relevance
Explain how well the candidate's projects and experience match the job requirements.

5. Resume Improvements
Give exactly 3 specific improvements the candidate should make to their resume.

6. Suggested Resume Changes
Give practical examples of what the candidate could add or rewrite in their resume.
Do not invent experience or skills that are not supported by the resume.

7. Final Recommendation
Give a short recommendation about whether the candidate should apply for this job.

Keep the response clear, honest, practical, and easy to understand.
"""

    try:

        response = None

        for attempt in range(3):

            try:
                response = client.models.generate_content(
                    model="gemini-3.7-flash",
                    contents=prompt
                )

                break

            except Exception as e:

                if "503" in str(e):
                    time.sleep(3)
                else:
                    raise e

        if response:
            st.write(response.text)
        else:
            st.error("Gemini is temporarily unavailable. Please try again.")

    except Exception as e:
        st.error(f"AI analysis failed: {e}")