from backend.gemini_client import generate_json_response
from backend.db import save_study_plan

def generate_study_plan(subjects, exam_date, study_hours, user_id=1):
    """
    Generates a personalized study calendar schedule leading up to exam_date.
    Organizes daily focus areas, weekly milestones, revision plans, and productivity tips.
    Saves and returns study plan as JSON.
    """
    if not subjects or not exam_date or not study_hours:
        raise ValueError("Subjects, Exam Date, and daily study hours are all required to create a schedule.")
        
    system_instruction = (
        "You are an AI Academic Advisor and Student Study Planner. "
        "Create a realistic, structured, and balanced study schedule leading up to the given exam date. "
        "Allocate subjects and study hours appropriately. Prioritize revision phases closer to the exam. "
        "Return the schedule strictly in a JSON format matching the schema requested."
    )
    
    prompt = f"""
    Create a study plan for:
    Subjects: {subjects}
    Exam Date: {exam_date}
    Available Daily Study Hours: {study_hours} hours
    
    Return a JSON object with the following fields:
    - weekly_goals: A list of strings of major goals/milestones for each week leading to the exam.
    - daily_schedule: A list of study tasks for a 7-day representative weekly schedule template. Each item in the list must have:
        - day: 'Monday', 'Tuesday', etc.
        - subjects: List of strings of subjects to study on this day
        - topic: Specific topic/chapter to cover
        - hours: Number of hours allocated (float/int)
        - task: Description of the study task (e.g. 'Read Chapter 3 and solve practice problems')
    - revision_plan: A list of strings detailing a dedicated revision strategy for the final days before the exam.
    - tips: A list of strings containing advice on how to study efficiently, avoid burnout, and retain information.
    
    Ensure your output is valid JSON and contains all these fields.
    """
    
    plan = generate_json_response(prompt, system_instruction)
    
    if not plan or not isinstance(plan, dict):
        raise ValueError("Received invalid study plan structure from Gemini.")
        
    # Standardize output
    plan["weekly_goals"] = list(plan.get("weekly_goals", []))
    plan["daily_schedule"] = list(plan.get("daily_schedule", []))
    plan["revision_plan"] = list(plan.get("revision_plan", []))
    plan["tips"] = list(plan.get("tips", []))
    
    # Save to SQLite DB
    save_study_plan(
        user_id=user_id,
        subjects=subjects,
        exam_date=exam_date,
        study_hours=float(study_hours),
        plan_json=plan
    )
    
    return plan
