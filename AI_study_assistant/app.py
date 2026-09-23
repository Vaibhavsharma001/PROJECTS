import streamlit as st 
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader 
import os 
import json

# Page configuration
st.set_page_config(
    page_title = "AI Study Assistant",
    page_icon = "📚",
    layout = "wide"
)

if "quiz_history" not in st.session_state:

    st.session_state.quiz_history = []

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")


if not api_key:
    st.error("API_KEY is missing. Please add it to your .env file.")
    st.stop()
    
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)


st.title("📚 AI Study Assistant")
st.subheader("Learn smarter with AI — explanations, notes, MCQs and quizzes.")

# Sidebar
st.sidebar.header("⚙️ Study Settings")

topic = st.sidebar.text_input(
      "Enter your topic",
      placeholder="e.g. Python OOP"
)

difficulty = st.sidebar.selectbox(
    "Diffficulty",
    ["Beginner", "Intermediate", "Advanced"]
)

st.sidebar.header("📄 Study Material")

uploaded_file = st.sidebar.file_uploader(
    "Upload your study material",
    type=["txt","pdf"]
)

# Main tabs

tab1,tab2,tab3,tab4 = st.tabs(
    ["📖 Explain", "📝 Notes", "❓ MCQs", "🎯 Quiz"]
)

def generate_response(prompt):
    """send prompt to groq and return the resopnse."""
    
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
          messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error:{e}"
    
    
with tab1:
    st.header("📖 Topic Explanation")

    if not topic:
        st.info("Enter a topic from the sidebar.")

    else:
        if st.button("Explain Topic", key="explain"):

            prompt = f"""
You are an expert teacher.

Explain the following topic to a student.

Topic: {topic}
Difficulty: {difficulty}

Follow this structure:

1. Simple definition
2. Why it is important
3. Main concepts
4. Easy examples
5. Real-world example
6. Common mistakes
7. Short summary

Use simple language and make the explanation suitable
for a college student.
"""

            with st.spinner("Preparing explanation..."):
                result = generate_response(prompt)

            st.markdown(result)
            
with tab2:
    st.header("📝 Generate Study Notes")
    
    if not topic:
        st.info("Enter a topic from the sidebar.")
        
    else:
        
        if st.button("Generates Notes" , key= "notes"):
            
            
            prompt = f"""
            
            Create detailed but easy-to-revise study notes.

Topic: {topic}
Difficulty: {difficulty}

Requirements:

- Use clear headings
- Use bullet points
- Explain important definitions
- Include important formulas if applicable
- Include examples
- Mention important exam points
- Keep the notes organized
- Add a final quick revision section
"""
            
            with st.spinner("Creating notes..."):
                result = generate_response(prompt)
                
            st.markdown(result)
            
            
            
# ---------------------------------------------------
# MCQ TAB
# ---------------------------------------------------

with tab3:

    st.header("❓ Multiple Choice Questions")

    if not topic:
        st.info("Enter a topic from the sidebar.")

    else:

        number_of_questions = st.slider(
            "Number of questions",
            min_value=3,
            max_value=10,
            value=5
        )

        if st.button("Generate MCQs", key="mcq"):

            prompt = f"""
Create {number_of_questions} multiple-choice questions.

Topic: {topic}
Difficulty: {difficulty}

For every question provide:

Question:
A)
B)
C)
D)

Correct Answer:
Explanation:

Make sure the correct answer is clearly identified.
Questions should test understanding, not only memorization.
"""

            with st.spinner("Generating questions..."):

                result = generate_response(prompt)

            st.markdown(result)

# ---------------------------------------------------
# QUIZ TAB
# ---------------------------------------------------

with tab4:

    st.header("🎯 Practice Quiz")

    if not topic:

        st.info("Enter a topic from the sidebar.")

    else:

        if st.button("Start Quiz", key="quiz"):
            
             

            prompt = f"""
Create a quiz about the following topic.

Topic: {topic}
Difficulty: {difficulty}

Create exactly 5 multiple-choice questions.

Return ONLY valid JSON in this exact format:

{{
    "questions": [
        {{
            "question": "Question text",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "Option A"
        }}
    ]
}}

Important:
- Create exactly 5 questions.
- Each question must have exactly 4 options.
- The answer must exactly match one of the options.
- Do not add markdown.
- Do not add explanations.
"""
            with st.spinner("Creating quiz..."):
                result = generate_response(prompt)

            try:

                quiz_data = json.loads(result)

                if "questions" not in quiz_data:

                    st.error("AI did not return valid quiz questions.")

                else:

                    st.session_state.quiz_data = quiz_data

            except json.JSONDecodeError:

                st.error(
                    "The AI returned an invalid quiz format. "
                    "Please try starting the quiz again."
                )
                

            
            
if "quiz_data" in st.session_state:

    st.subheader("📝 Quiz")

    for i, question in enumerate(
        st.session_state.quiz_data["questions"]
    ):

        st.write(f"### Question {i + 1}")

        st.write(question["question"])

        st.radio(
            "Choose your answer:",
            question["options"],
            index=None,
            key=f"question_{i}"
        )

    if st.button("🏆 Submit Quiz", key="submit_quiz"):

        score = 0
        unanswered = 0

        for i, question in enumerate(
            st.session_state.quiz_data["questions"]
        ):

            selected_answer = st.session_state.get(
                f"question_{i}"
            )

            correct_answer = question["answer"]

            if selected_answer is None:
                unanswered += 1
                st.warning(
                    f"Question {i + 1}: Not answered ⚠️"
                )

            elif selected_answer == correct_answer:
                score += 1
                st.success(
                    f"Question {i + 1}: Correct! ✅"
                )

            else:
                st.error(
                    f"Question {i + 1}: Wrong ❌"
                )

                st.write(
                    f"Correct answer: **{correct_answer}**"
                )

        total_questions = len(
            st.session_state.quiz_data["questions"]
        )

        percentage = (
            score / total_questions
        ) * 100

        quiz_result = {
            "topic": topic,
            "score": score,
            "total": total_questions,
            "percentage": percentage
        }

        st.session_state.quiz_history.append(quiz_result)

        st.subheader("🏆 Your Result")

        st.write(
            f"### Score: {score}/{total_questions}"
        )

        st.write(
            f"### Percentage: {percentage:.1f}%"
        )

        if unanswered > 0:
            st.info(
                f"You left {unanswered} question(s) unanswered."
            )

    if st.button("🔄 Retry Quiz", key="retry_quiz"):

        del st.session_state.quiz_data

        st.rerun()
        
        # ---------------------------------------------------
# QUIZ HISTORY
# ---------------------------------------------------

st.header("📊 Quiz History")

if not st.session_state.quiz_history:

    st.info("No quiz attempts yet.")

else:

    for i, result in enumerate(
        st.session_state.quiz_history,
        start=1
    ):

        st.write(
            f"**{i}. {result['topic']}** — "
            f"{result['score']}/{result['total']} "
            f"({result['percentage']:.1f}%)"
        )
        
        
        # ---------------------------------------------------
# STUDY DASHBOARD
# ---------------------------------------------------

st.header("📈 Study Dashboard")

if not st.session_state.quiz_history:

    st.info("Complete a quiz to see your study statistics.")

else:

    total_quizzes = len(
        st.session_state.quiz_history
    )

    total_questions = sum(
        result["total"]
        for result in st.session_state.quiz_history
    )

    total_correct = sum(
        result["score"]
        for result in st.session_state.quiz_history
    )

    average_score = (
        total_correct / total_questions
    ) * 100

    best_score = max(
        result["percentage"]
        for result in st.session_state.quiz_history
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "📚 Quizzes Completed",
            total_quizzes
        )

    with col2:

        st.metric(
            "❓ Questions Attempted",
            total_questions
        )

    with col3:

        st.metric(
            "📊 Average Score",
            f"{average_score:.1f}%"
        )

    with col4:

        st.metric(
            "🏆 Best Score",
            f"{best_score:.1f}%"
        )
            
# ---------------------------------------------------
# STUDY MATERIAL
# ---------------------------------------------------

st.header("📄 Uploaded Study Material")

if uploaded_file is not None:

    st.success(f"Uploaded: {uploaded_file.name}")

    if uploaded_file.name.endswith(".txt"):

        file_content = uploaded_file.read().decode("utf-8")

    elif uploaded_file.name.endswith(".pdf"):

        pdf_reader = PdfReader(uploaded_file)

        file_content = ""

        for page in pdf_reader.pages:

            text = page.extract_text()

            if text:
                file_content += text + "\n"

    st.subheader("📖 Your Material")

    st.text_area(
        "Extracted Content",
        file_content,
        height=400
    )

    # ---------------------------------------------------
    # SUMMARIZE MATERIAL
    # ---------------------------------------------------

    if st.button(
        "🤖 Summarize Material",
        key="summarize_material"
    ):

        prompt = f"""
You are an expert study assistant.

Analyze the following study material.

Create a clear and easy-to-revise summary for a college student.

Requirements:

- Identify the main concepts
- Explain important definitions
- Highlight important points
- Use bullet points
- Include important examples
- Keep the language simple
- End with a quick revision section

Study Material:

{file_content}
"""

        with st.spinner("Analyzing your study material..."):

            result = generate_response(prompt)

        st.subheader("🤖 AI Summary")

        st.markdown(result)

    # ---------------------------------------------------
    # ASK QUESTIONS
    # ---------------------------------------------------

    st.subheader("💬 Ask Questions")

    question = st.text_input(
        "Ask a question about your study material",
        placeholder="e.g. What is inheritance?"
    )

    if st.button("💬 Ask AI", key="ask_material"):

        if not question:

            st.warning("Please enter a question.")

        else:

            prompt = f"""
You are an AI study assistant.

Answer the student's question using ONLY the
provided study material.

If the answer cannot be found in the material,
say:

"I couldn't find this information in the uploaded material."

Keep the answer simple and suitable for a college student.

Study Material:

{file_content}

Student Question:

{question}
"""

            with st.spinner("Finding the answer..."):

                result = generate_response(prompt)

            st.subheader("🤖 AI Answer")

            st.markdown(result)

else:

    st.info("Upload a .txt or .pdf study file from the sidebar.")