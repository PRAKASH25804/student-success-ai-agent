import os
import pypdf
from backend.gemini_client import generate_json_response
from backend.db import save_resume_analysis

def extract_text_from_pdf(file_path):
    """
    Extracts text content from a PDF file using pypdf.
    """
    text = ""
    try:
        reader = pypdf.PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        raise ValueError(f"Failed to read PDF file: {str(e)}")
    return text.strip()

def analyze_resume(file_path, target_role="Software Developer", user_id=1):
    """
    Extracts text from PDF, requests Gemini 2.0 Flash to analyze it,
    saves the results to SQLite db, and returns the response.
    """
    filename = os.path.basename(file_path)
    resume_text = extract_text_from_pdf(file_path)
    
    if not resume_text:
        raise ValueError("The uploaded PDF appears to be empty or contains non-extractable text.")
        
    system_instruction = (
        "You are an expert AI Resume Analyzer and ATS (Applicant Tracking System) optimizer. "
        "Your task is to review a student's resume against a target role, provide a score from 0 to 100, "
        "extract skills, identify gaps, list strengths and weaknesses, and recommend improvements and ATS tips. "
        "Return your analysis strictly as a JSON object matching the requested schema."
    )
    
    prompt = f"""
    Analyze the following student resume text.
    Target Role: {target_role}
    
    Resume Text:
    ---
    {resume_text}
    ---
    
    Please output a JSON object with the following fields:
    - score: An integer (0 to 100) representing how strong this resume is for the target role.
    - skills: A list of strings containing skills found in the resume.
    - missing_skills: A list of strings containing skills relevant to the target role '{target_role}' that are missing or weak in this resume.
    - strengths: A list of strings containing positive aspects and strengths of the resume.
    - weaknesses: A list of strings containing aspects that need improvement or are weak.
    - improvements: A list of actionable suggestions to improve the content, formatting, or impact of the resume.
    - ats_tips: A list of tips to optimize this resume for Applicant Tracking Systems (e.g. keywords, layout).
    
    Ensure your output is valid JSON and matches this schema exactly.
    """
    
    # Request Gemini JSON response
    analysis = generate_json_response(prompt, system_instruction)
    
    # Secure API values and handle errors
    if not analysis or not isinstance(analysis, dict):
        raise ValueError("Received invalid analysis structure from Gemini.")
        
    # Standardize field presence
    analysis["score"] = int(analysis.get("score", 50))
    analysis["skills"] = list(analysis.get("skills", []))
    analysis["missing_skills"] = list(analysis.get("missing_skills", []))
    analysis["strengths"] = list(analysis.get("strengths", []))
    analysis["weaknesses"] = list(analysis.get("weaknesses", []))
    analysis["improvements"] = list(analysis.get("improvements", []))
    analysis["ats_tips"] = list(analysis.get("ats_tips", []))
    
    # Save in DB for progress tracking
    save_resume_analysis(
        user_id=user_id,
        filename=filename,
        score=analysis["score"],
        analysis_json=analysis
    )
    
    return analysis
