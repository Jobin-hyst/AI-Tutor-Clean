from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
from openai import OpenAI
import re
from fastapi.middleware.cors import CORSMiddleware
import requests
import time
import mysql.connector
import json
import os
from dotenv import load_dotenv
# from your_session_store import sessions

# Load environment variables
load_dotenv()

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="AI_tutor"
    )



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)
client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    api_key=os.getenv("OPENAI_API_KEY")
)

# client = OpenAI(
#     base_url=os.getenv("HUGGINGFACE_BASE_URL", "https://router.huggingface.co/nebius/v1"),
#     api_key=os.getenv("HUGGINGFACE_API_KEY")
# )

message_history = ChatMessageHistory()
output_parser = StrOutputParser()

PROGRESS_TRACKER = [
    {"progress": 1, "topic": "Variables & Data Types","needs_coding":False},
        {"progress": 2, "topic": "Basic Data Types (int, float, char, bool, string)","needs_coding":True},
        {"progress": 3, "topic": "Advanced Data Types (Arrays, Structs, Pointers)","needs_coding":True},
        {"progress": 4, "topic": "Revision: Variables, Data Types & Pointers","needs_coding":False},
        {"progress": 5, "topic": "Operators (Arithmetic, Logical, Relational)","needs_coding":True},
        {"progress": 6, "topic": "Bitwise Operators","needs_coding":True},
        {"progress": 7, "topic": "Expressions & Type Conversions","needs_coding":False},
        {"progress": 8, "topic": "Revision: Operators & Expressions","needs_coding":False},
        {"progress": 9, "topic": "Basic Conditional Statements (if, if-else, switch)","needs_coding":True},
        {"progress": 10, "topic": "Intermediate Conditional Statements","needs_coding":True},
        {"progress": 11, "topic": "Advanced Conditional Statements","needs_coding":True},
        {"progress": 12, "topic": "Revision: Conditional Statements","needs_coding":False},
        {"progress": 13, "topic": "Basics of Loops (for, while, do-while)","needs_coding":True},
        {"progress": 14, "topic": "Intermediate Loops (Nested Loops, Pattern Printing)","needs_coding":True},
        {"progress": 15, "topic": "Advanced Loops (Optimization, Break/Continue)","needs_coding":True},
        {"progress": 16, "topic": "Revision: Loops & Iterations","needs_coding":False},
        {"progress": 17, "topic": "Functions (Definition, Parameters, Return Types)","needs_coding":True},
        {"progress": 18, "topic": "Recursive Functions","needs_coding":True},
        {"progress": 19, "topic": "Basic Array Operations (Insertion, Deletion, Traversal)","needs_coding":True},
        {"progress": 20, "topic": "Revision: Functions & Arrays Basics","needs_coding":True},
        {"progress": 21, "topic": "String Operations (Concatenation, Comparison, Substring)","needs_coding":True},
        {"progress": 22, "topic": "String Manipulation (Reversal, Palindrome, Anagram)","needs_coding":True},
        {"progress": 23, "topic": "1D Arrays (Sorting, Searching, Merging)","needs_coding":True},
        {"progress": 24, "topic": "2D Array""s (Matrix Operations, Rotations, Transpose)","needs_coding":True},
        {"progress": 25, "topic": "Revision: Strings & Arrays","needs_coding":False},
        {"progress": 26, "topic": "Modular Arithmetic (GCD, LCM, Prime Numbers)","needs_coding":True},
        {"progress": 27, "topic": "Stacks (LIFO, Applications in Expressions, Undo)","needs_coding":True},
        {"progress": 28, "topic": "Queues (FIFO, Circular, Priority Queue)","needs_coding":True},
        {"progress": 29, "topic": "Revision: Modular Arithmetic & Stack/Queue","needs_coding":False},
        {"progress": 30, "topic": "Bitwise Operations (AND, OR, XOR, Left & Right Shifts)","needs_coding":True},
        {"progress": 31, "topic": "XOR Tricks (Finding Unique Elements, Missing Numbers)","needs_coding":True},
        {"progress": 32, "topic": "Basic Searching Algorithms (Linear, Binary)","needs_coding":True},
        {"progress": 33, "topic": "Advanced Searching (Exponential, Interpolation)","needs_coding":True},
        {"progress": 34, "topic": "Revision: Bitwise Operations & Searching","needs_coding":False},
        {"progress": 35, "topic": "Basic Sorting Algorithms (Bubble, Selection, Insertion)","needs_coding":True},
        {"progress": 36, "topic": "Advanced Sorting (Merge, Quick, Counting Sort)","needs_coding":True},
        {"progress": 37, "topic": "Sliding Window (Fixed & Variable Window Problems)","needs_coding":True},
        {"progress": 38, "topic": "Revision: Sorting & Sliding Window","needs_coding":False},
        {"progress": 39, "topic": "Recursion (Backtracking, Permutations, Combinations)","needs_coding":True},
        {"progress": 40, "topic": "Prefix Sum (Kadane's Algorithm, Subarray Sums)","needs_coding":True},
        {"progress": 41, "topic": "Binary Exponentiation & Fast Modulo Operations","needs_coding":True},
        {"progress": 42, "topic": "Final Revision: Recursion, Prefix Sum & Binary Exponentiation","needs_coding":True}
]

sessions = {}  # In-memory session store

class SessionRequest(BaseModel):
    session_id: str

class LanguageRequest(SessionRequest):
    language: str

class MessageRequest(SessionRequest):
    message: str

class RunCodeRequest(BaseModel):
    code: str
    language: str
    stdin: str = ""

language_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an enthusiastic coding tutor. Greet the user and ask which programming language they want to learn."),
    ("human", "{input}")
])

main_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are a {language} coding tutor. Current topic: {current_topic}
    Conversation History:
    {history}

    Respond following these rules:
    1. Explain concepts clearly with examples
    2. Generate practice problems when needed
    3. Provide constructive feedback
    4. Keep responses under 300 words
    """),
    ("human", "{input}")
])

def get_current_topic(progress):
    for entry in PROGRESS_TRACKER:
        if entry["progress"] == progress:
            return entry
    return None














@app.post("/start")
def start_session():
    import uuid
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "language": None,
        "progress": 1,
        "history": ChatMessageHistory()
    }
    return {"session_id": session_id, "message": "Welcome! Which programming language would you like to learn? (Python, JavaScript, Java, C++)"}













@app.post("/set-language")
def set_language(req: MessageRequest):
    if req.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    # Convert message to lowercase and remove any extra spaces
    message = req.message.lower().strip()
    
    # Map common variations of language names
    language_map = {
        'python': 'Python',
        'py': 'Python',
        'javascript': 'JavaScript',
        'js': 'JavaScript',
        'java': 'Java',
        'cpp': 'C++',
        'c++': 'C++',
        'c plus plus': 'C++'
    }

    # Check if the message contains any of the language keywords
    selected_language = None
    for key, value in language_map.items():
        if key in message:
            selected_language = value
            break

    if selected_language:
        sessions[req.session_id]["language"] = selected_language
        return {"message": f"Excellent choice! Let's begin learning {selected_language}"}
    else:
        return {"message": "Sorry, I couldn't understand the language. Please specify Python, JavaScript, Java, or C++."}

# Helper function to fetch the current topic based on progress
def get_current_topic(progress):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT topic, needs_coding FROM PROGRESS_TRACKER WHERE progress = %s", (progress,))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    if not result:
        raise HTTPException(status_code=404, detail="Invalid progress number.")
    return result






















@app.get("/get-topic")
def get_topic(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    topic_data = get_current_topic(session["progress"])
    language = session["language"]
    topic = topic_data["topic"]

    prompt = (
        f"You are an expert programming tutor helping students prepare for technical placements. "
        f"The student has chosen to learn in {language}. "
        f"Your task is to explain the topic '{topic}' in clear and simple {language} code. "
        f"Follow this structure:\n\n"
        f"1. Brief theoretical introduction to the topic.\n"
        f"2. Why it is important in programming/placements.\n"
        f"3. {language}-specific syntax or use cases.\n"
        f"4. One or two real-world example code snippets in {language}.\n"
        f"5. A short summary or tip.\n\n"
        f"Keep the entire explanation under 300 words. "
        f"Make sure it's beginner-friendly, but technically accurate. "
        f"Remind the student that mastering core topics like this is essential for cracking coding interviews and placements."
    )

    response = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct",
        messages=[
            {"role": "system", "content": "You are a knowledgeable and supportive programming instructor."},
            {"role": "user", "content": prompt}
        ]
    )

    reply = response.choices[0].message.content

    return {
        "topic": topic,
        "explanation": reply,
        "needs_coding": topic_data['needs_coding']
    }












# Endpoint to generate a coding problem
@app.get("/get-problem")
def get_problem(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    topic_data = get_current_topic(session['progress'])

    if not topic_data['needs_coding']:
        return {"message": "This topic does not require a coding problem."}

    language = session['language']
    
    strict_prompt = (
        f"Generate a {language} coding question suitable for placements on the topic '{topic_data['topic']}'.\n\n"
        f"Respond EXACTLY in this strict format (do not omit any part):\n\n"
        f"Problem:\n<problem statement>\n\n"
        f"TestCases:\n"
        f"Input: <test_input_1>\nOutput: <expected_output_1>\n\n"
        f"Input: <test_input_2>\nOutput: <expected_output_2>\n\n"
        f"Input: <test_input_3>\nOutput: <expected_output_3>\n\n"
        f"Input: <test_input_4>\nOutput: <expected_output_4>\n\n"
        f"Input: <test_input_5>\nOutput: <expected_output_5>\n\n"
        f"Company: <Company name like Infosys, TCS, etc>\n\n"
        f"DO NOT write anything else. DO NOT OMIT TEST CASES. DO NOT OMIT THE FORMAT. "
        f"Each test case must be realistic and cover different edge cases. "
        f"Test cases must be for the problem above and must be valid input/output pairs."
    )

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="mistralai/mistral-7b-instruct",
                messages=[
                    {"role": "system", "content": "You are a strict coding question generator. You must always follow the format exactly and never omit any part."},
                    {"role": "user", "content": strict_prompt}
                ]
            ).choices[0].message.content.strip()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")

        print(f"🧠 Raw LLM Response (attempt {attempt+1}):\n", response)  # Debug output

        # === Parsing ===
        problem_match = re.search(r"Problem:\s*(.*?)\n\s*TestCases:", response, re.DOTALL)
        testcase_matches = re.findall(r"Input:\s*(.*?)\nOutput:\s*(.*?)\n", response, re.DOTALL)
        company_match = re.search(r"Company:\s*(.*)", response)

        problem = problem_match.group(1).strip() if problem_match else ""
        testcases = [{"input": inp.strip(), "output": out.strip()} for inp, out in testcase_matches]
        company = company_match.group(1).strip() if company_match else "Unknown"

        print("✅ Parsed test cases count:", len(testcases))  # Debug output

        if len(testcases) == 5:
            session["problem"] = {
                "description": problem,
                "testcases": testcases,
                "company": company
            }
            return {
                "problem": problem,
                "testcases": testcases,
                "company": company,
                "followup": "If you need help to solve this, type 'hint' and I'll guide you!"
            }
        # else, retry
    # If after retries, still not enough test cases:
    raise HTTPException(
        status_code=422,
        detail=f"Expected exactly 5 test cases, but got {len(testcases)} after {max_retries} attempts. Please try again."
    )

# Endpoint to get a hint for the current coding problem

















@app.get("/get-hint")
def get_hint(session_id: str):
    # 1. Validate session
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 2. Check if the topic requires coding
    topic = get_current_topic(session['progress'])
    if not topic["needs_coding"]:
        return {"message": "No coding problem is required for this topic. Hint generation is skipped."}

    # 3. Check if a problem has been generated
    problem_data = session.get("problem")
    if not problem_data or not problem_data.get("description"):
        raise HTTPException(status_code=400, detail="No problem generated yet. Please call /get-problem first.")

    # 4. Use the existing problem description to generate a hint
    problem_description = problem_data["description"]

    # 5. Construct the LLM prompt to generate a precise hint for this specific problem
    prompt = f"""
    You're an assistant helping students solve coding challenges. Based on the following problem description:

    \"\"\"{problem_description}\"\"\"  

    Write a helpful hint for beginners that:
    - Does NOT give away the answer.
    - Suggests how to approach THIS specific problem.
    - Mentions relevant concepts or functions that could be used.
    - Can include a tiny example or pseudocode to illustrate the approach.
    - Should be clear even for users new to programming.
    - Breaks down complex concepts into simple steps.
    - Uses analogies or simple language to explain technical terms.
    - Is no more than 150 words.
    """

    # 6. Call the LLM to generate the hint
    response = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct",
        messages=[
            {"role": "system", "content": "You are a coding tutor for absolute beginners."},
            {"role": "user", "content": prompt}
        ]
    ).choices[0].message.content.strip()

    # 7. Save the hint to session for optional reuse
    session["problem"]["hint"] = response

    # 8. Return the hint
    return {"hint": response}










@app.post("/next-topic")
def next_topic(req: SessionRequest):
    session = sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session['progress'] += 1
    if session['progress'] > len(PROGRESS_TRACKER):
        return {"message": "Congratulations! You've completed the course."}

    return {"message": "Moving to next topic."}



API_SUBMISSION_URL = "http://13.60.204.233:2358/submissions"
API_GET_URL = "http://13.60.204.233:2358/submissions/{}"



language_mapping = {
    "Python": {"id": 71},
    "javascript": {"id": 63},
    "cpp": {"id": 54},
    "java": {"id": 62}
}





@app.post("/submit-solution")
def submit_solution(req: MessageRequest):
    currentSessionId = req.session_id
    sourceCode = req.message
    session = sessions.get(currentSessionId)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    language_id = language_mapping.get(session["language"], {}).get("id")
    if not language_id:
        raise HTTPException(status_code=400, detail="Unsupported language")

    topic = get_current_topic(session["progress"])
    problem = session['problem']

    if not problem or not problem.get("testcases"):
        raise HTTPException(status_code=400, detail="No test cases found")

    testcases = problem["testcases"]
    results = []
    all_passed = True

    for idx, case in enumerate(testcases):
        payload = {
            "source_code": sourceCode,
            "language_id": language_id,
            "stdin": case["input"]
        }

        submission = requests.post(API_SUBMISSION_URL, json=payload)
        if submission.status_code != 201:
            results.append({
                "testcase": idx + 1,
                "status": "Submission Failed",
                "input": case["input"],
                "expected": case["output"],
                "actual": None,
                "pass": False
            })
            all_passed = False
            continue

        token = submission.json().get("token")

        for _ in range(10):
            time.sleep(1)
            result = requests.get(API_GET_URL.format(token))
            result_json = result.json()
            status = result_json.get("status", {}).get("description")

            if status == "Accepted":
                actual_output = result_json.get("stdout", "").strip()
                expected_output = case["output"].strip()
                passed = actual_output == expected_output
                results.append({
                    "testcase": idx + 1,
                    "status": status,
                    "input": case["input"],
                    "expected": expected_output,
                    "actual": actual_output,
                    "pass": passed
                })
                if not passed:
                    all_passed = False
                break
            elif status in ["Compilation Error", "Runtime Error (NZEC)", "Time Limit Exceeded"]:
                results.append({
                    "testcase": idx + 1,
                    "status": status,
                    "input": case["input"],
                    "expected": case["output"],
                    "actual": result_json.get("stderr"),
                    "pass": False
                })
                all_passed = False
                break
        else:
            results.append({
                "testcase": idx + 1,
                "status": "Timeout",
                "input": case["input"],
                "expected": case["output"],
                "actual": None,
                "pass": False
            })
            all_passed = False

    # ---------- LLM Feedback Section ----------

    problem_description = problem.get("description", "No description provided.")

    if all_passed:
        feedback_prompt = (
            f"The student was given the following problem:\n\n"
            f"{problem_description}\n\n"
            f"They submitted the following Python code which passed all the test cases:\n\n"
            f"```\n{sourceCode}\n```\n\n"
            f"Please review the code and say if it's correct. If yes, explain why it's correct, "
            f"and suggest any improvements in style, performance, or edge-case handling. "
            f"Keep it clear and under 100 words."
        )
    else:
        failed_cases = [r for r in results if not r["pass"]]
        feedback_prompt = (
            f"The student was given the following problem:\n\n"
            f"{problem_description}\n\n"
            f"They submitted this Python code:\n\n"
            f"```\n{sourceCode}\n```\n\n"
            f"The following test cases failed:\n" +
            "\n".join(
                f"- Input: {fc['input']} | Expected: {fc['expected']} | Actual: {fc['actual'] or 'None'}"
                for fc in failed_cases
            ) +
            "\n\nPlease explain why this code is not fully correct, what is wrong, and how the student can fix or improve it. "
            f"Keep it educational, specific, and helpful."
        )

    # Get feedback from LLM
    feedback_response = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct",
        messages=[
            {"role": "system", "content": "You are an expert Python coding tutor. Respond clearly and helpfully."},
            {"role": "user", "content": feedback_prompt}
        ]
    )
    feedback = feedback_response.choices[0].message.content.strip()

    return {
        "results": results,
        "all_passed": all_passed,
        "verdict": "Correct" if all_passed else "Incorrect",
        "feedback": feedback
    }


# Add this route to your FastAPI app
@app.post("/process-prompt")
async def process_prompt(request: Request):
    data = await request.json()
    session_id = data.get("session_id")
    message = data.get("message")
    
    if not session_id or session_id not in sessions:
        return {"error": "Session not found", "message": "Please start a new session first."}
    
    session = sessions[session_id]
    
    if session["language"] is None:
        language_match = re.search(r"(python|javascript|java|c\+\+)", message.lower())
        if language_match:
            language = language_match.group(1).capitalize()
            session["language"] = language
            # Get the first topic
            topic_data = get_current_topic(session["progress"])
            intro = f"Excellent choice! Let's begin learning {language}."
            topic_intro = f"Let's start with the first topic: {topic_data['topic']}."
            # Compose the explanation prompt
            explanation_prompt = (
                f"You are an expert programming tutor helping students prepare for technical placements. "
                f"The student has chosen to learn in {language}. "
                f"Your task is to explain the topic '{topic_data['topic']}' in clear and simple {language} code. "
                f"Follow this structure:\n\n"
                f"1. Brief theoretical introduction to the topic.\n"
                f"2. Why it is important in programming/placements.\n"
                f"3. {language}-specific syntax or use cases.\n"
                f"4. One or two real-world example code snippets in {language}.\n"
                f"5. A short summary or tip.\n\n"
                f"Keep the entire explanation under 300 words. "
                f"Make sure it's beginner-friendly, but technically accurate. "
                f"Remind the student that mastering core topics like this is essential for cracking coding interviews and placements."
            )
            response = client.chat.completions.create(
                model="mistralai/mistral-7b-instruct",
                messages=[
                    {"role": "system", "content": "You are a knowledgeable and supportive programming instructor."},
                    {"role": "user", "content": explanation_prompt}
                ]
            )
            reply = response.choices[0].message.content
            # Add follow-up message
            if topic_data['needs_coding']:
                followup = "\n\nThere are coding questions for this topic."
            else:
                followup = "\n\nThere are no coding questions for this topic. You can type 'next topic' to move forward."
            return {
                "message": f"{intro}\n{topic_intro}\n\n{reply}{followup}",
                "topic": topic_data['topic']
            }
        else:
            return {"message": "Sorry, I couldn't understand the language. Please specify Python, JavaScript, Java, or C++."}
    
    if "next topic" in message.lower() or "move forward" in message.lower():
        session["progress"] += 1
        if session["progress"] > len(PROGRESS_TRACKER):
            return {"message": "Congratulations! You've completed the course."}
        # Teach the new topic
        topic_data = get_current_topic(session["progress"])
        language = session["language"]
        topic = topic_data["topic"]
        explanation_prompt = (
            f"You are an expert programming tutor helping students prepare for technical placements. "
            f"The student has chosen to learn in {language}. "
            f"Your task is to explain the topic '{topic}' in clear and simple {language} code. "
            f"Follow this structure:\n\n"
            f"1. Brief theoretical introduction to the topic.\n"
            f"2. Why it is important in programming/placements.\n"
            f"3. {language}-specific syntax or use cases.\n"
            f"4. One or two real-world example code snippets in {language}.\n"
            f"5. A short summary or tip.\n\n"
            f"Keep the entire explanation under 300 words. "
            f"Make sure it's beginner-friendlclsy, but technically accurate. "
            f"Remind the student that mastering core topics like this is essential for cracking coding interviews and placements."
        )
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=[
                {"role": "system", "content": "You are a knowledgeable and supportive programming instructor."},
                {"role": "user", "content": explanation_prompt}
            ]
        )
        reply = response.choices[0].message.content
        # Add follow-up message
        if topic_data['needs_coding']:
            followup = "\n\nThere are coding questions for this topic."
        else:
            followup = "\n\nThere are no coding questions for this topic. You can type 'next topic' to move forward."
        return {
            "message": f"Moving to next topic.\n\n{reply}{followup}",
            "topic": topic
        }
    
    if "get topic" in message.lower() or "current topic" in message.lower():
        topic_data = get_current_topic(session["progress"])
        return {
            "message": f"Current Topic: {topic_data['topic']}",
            "needs_coding": topic_data['needs_coding']
        }
    
    # Accept more variations for coding question requests
    coding_question_phrases = [
        "coding question", "get problem", "coding problem", "give coding question", "give coding problem", "problem please", "give me coding question", "give me coding problem"
    ]
    if any(phrase in message.lower() for phrase in coding_question_phrases):
        topic_data = get_current_topic(session["progress"])
        if not topic_data['needs_coding']:
            return {"message": "This topic does not require a coding problem."}
        # Generate problem using the existing get_problem endpoint logic
        problem_data = get_problem(session_id)
        # Return the problem and followup as two chat bubbles if followup exists
        if "followup" in problem_data:
            return {
                "message": f"Problem: {problem_data['problem']}\n\nTest Cases:",
                "testcases": problem_data['testcases'],
                "company": problem_data['company'],
                "followup": problem_data['followup']
            }
        else:
            return {
                "message": f"Problem: {problem_data['problem']}",
                "testcases": problem_data['testcases'],
                "company": problem_data['company']
            }
    
    if "hint" in message.lower() or "need help" in message.lower():
        # Generate hint using the existing get_hint endpoint logic
        hint_data = get_hint(session_id)
        return {"message": f"Hint: {hint_data['hint']}"}
    
    if "submit solution" in message.lower():
        # Extract code from the message
        code = message.split("submit solution")[1].strip()
        # Process solution submission using the existing submit_solution endpoint logic
        submission_data = submit_solution(MessageRequest(session_id=session_id, message=code))
        return {
            "message": f"Submission Results: {submission_data['verdict']}",
            "feedback": submission_data['feedback']
        }
    
    return {"message": "I didn't understand your request. Please try again!"}

@app.post("/run-code")
def run_code(req: RunCodeRequest):
    # JDoodle language mapping
    lang_map = {
        'python': ('python3', '3'),
        'python3': ('python3', '3'),
        'c': ('c', '5'),
        'cpp': ('cpp17', '0'),
        'c++': ('cpp17', '0'),
        'java': ('java', '4'),
        'javascript': ('nodejs', '4'),
        'js': ('nodejs', '4'),
    }
    lang = req.language.lower()
    if lang not in lang_map:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {req.language}")
    jdoodle_lang, jdoodle_ver = lang_map[lang]

    client_id = os.environ.get("JDOODLE_CLIENT_ID", "your_client_id")
    client_secret = os.environ.get("JDOODLE_CLIENT_SECRET", "your_client_secret")
    if client_id == "your_client_id" or client_secret == "your_client_secret":
        raise HTTPException(status_code=500, detail="JDoodle credentials not set in environment variables.")

    payload = {
        "clientId": client_id,
        "clientSecret": client_secret,
        "script": req.code,
        "language": jdoodle_lang,
        "versionIndex": jdoodle_ver,
        "stdin": req.stdin or ""
    }
    try:
        resp = requests.post("https://api.jdoodle.com/v1/execute", json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JDoodle error: {str(e)}")

