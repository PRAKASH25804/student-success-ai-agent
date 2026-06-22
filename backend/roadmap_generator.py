from backend.gemini_client import generate_json_response
from backend.db import save_career_roadmap

def generate_roadmap(career_goal, user_id=1):
    """
    Generates a structured career roadmap timeline based on career_goal.
    Saves and returns the output as JSON.
    """
    if not career_goal:
        raise ValueError("Career goal is required to generate a roadmap.")
        
    system_instruction = (
        "You are an AI Career Strategist and Advisor. "
        "Create a detailed, structured, step-by-step career path roadmap for a student targeting a career goal. "
        "Include milestones, timelines, specific project suggestions, certifications, online courses, and internship hunting advice. "
        "Return the roadmap strictly in a JSON format matching the schema requested."
    )
    
    prompt = f"""
    Create a complete career roadmap for:
    Career Goal: {career_goal}
    
    Please return a JSON object with the following fields:
    - milestones: A list of 4-5 sequential progression milestones. Each item must have:
        - title: Title of milestone (e.g. 'Foundations of Programming')
        - target_time: Estimated timeline (e.g. 'Months 1-3')
        - description: Focus of this milestone
        - skills_to_acquire: List of strings of skills to learn
        - projects_to_do: List of strings of portfolio projects to build
        - status: 'Pending'
    - certifications: A list of strings recommending industry certifications to target.
    - courses: A list of strings of popular courses or online paths (e.g. 'Coursera, Udemy, etc.').
    - internship_guidance: A list of strings of tips and guidelines to secure an internship in this field (resume tips, networking, platforms).
    
    Ensure your output is valid JSON and contains all these fields.
    """
    
    roadmap = generate_json_response(prompt, system_instruction)
    
    if not roadmap or not isinstance(roadmap, dict):
        raise ValueError("Received invalid career roadmap structure from Gemini.")
        
    # Standardize fields
    roadmap["milestones"] = list(roadmap.get("milestones", []))
    roadmap["certifications"] = list(roadmap.get("certifications", []))
    roadmap["courses"] = list(roadmap.get("courses", []))
    roadmap["internship_guidance"] = list(roadmap.get("internship_guidance", []))
    
    # Save to SQLite DB
    save_career_roadmap(
        user_id=user_id,
        career_goal=career_goal,
        roadmap_json=roadmap
    )
    
    return roadmap
