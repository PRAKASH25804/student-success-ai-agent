from backend.gemini_client import generate_json_response
from backend.db import save_interview_prep

def generate_interview_questions(job_role, difficulty="Intermediate", user_id=1):
    """
    Generates interview questions categorized by Technical, Behavioral, and HR.
    Includes sample answers, difficulty scaling, and professional tips.
    Saves the questions to the database for persistence.
    """
    if not job_role:
        raise ValueError("Job role is required to generate interview questions.")
        
    system_instruction = (
        "You are an AI Interview Prep Specialist and Technical Recruiter. "
        "Your task is to generate realistic interview questions tailored to a specific job role and difficulty level. "
        "Include sample answers (ideal responses) and tips for each question. "
        "Group questions into technical, behavioral, and HR. "
        "Return the questions strictly in a JSON format matching the schema requested."
    )
    
    prompt = f"""
    Generate a set of interview questions for the role:
    Job Role: {job_role}
    Difficulty Level: {difficulty}
    
    Please provide exactly 3-4 questions for each category (Technical, Behavioral, HR).
    
    Return a JSON object with the following fields:
    - technical: A list of objects containing technical questions. Each object must have:
        - question: The interview question text
        - answer: An exemplary, comprehensive sample answer
        - tips: A tip on how to structure the answer or what recruiters look for here
    - behavioral: A list of objects containing behavioral questions (e.g. STAR method). Each object must have:
        - question: The behavioral question text
        - answer: A sample response outline using the STAR method
        - tips: Tips for addressing this behavioral point
    - hr: A list of objects containing standard human resources/general questions. Each object must have:
        - question: The HR question text
        - answer: A sample professional answer
        - tips: Tips on what to highlight or avoid
    - general_tips: A list of strings of general interview preparation and delivery tips for this role.
    
    Ensure your output is valid JSON and adheres strictly to this structure.
    """
    
    questions = generate_json_response(prompt, system_instruction)
    
    if not questions or not isinstance(questions, dict):
        raise ValueError("Received invalid interview questions structure from Gemini.")
        
    # Safeguards
    questions["technical"] = list(questions.get("technical", []))
    questions["behavioral"] = list(questions.get("behavioral", []))
    questions["hr"] = list(questions.get("hr", []))
    questions["general_tips"] = list(questions.get("general_tips", []))
    
    # Save to SQLite DB for user access
    save_interview_prep(
        user_id=user_id,
        job_role=job_role,
        difficulty=difficulty,
        questions_json=questions
    )
    
    return questions
