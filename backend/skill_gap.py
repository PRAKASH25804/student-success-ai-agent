from backend.gemini_client import generate_json_response
from backend.db import save_skill_gap_analysis

def analyze_skill_gap(job_role, current_skills, user_id=1):
    """
    Compares student's current skills against requirements for job_role.
    Generates missing skills list, custom learning plan, project recommendations, and resources.
    Saves and returns the output as JSON.
    """
    if not job_role or not current_skills:
        raise ValueError("Job role and current skills are required fields.")
        
    system_instruction = (
        "You are an AI Career Coach and Skill Gap Analyst. "
        "Analyze the gap between a student's current skills and their desired job role. "
        "Produce detailed learning goals, cert recommendations, resources, and custom projects. "
        "Return your results strictly in a JSON format matching the schema requested."
    )
    
    prompt = f"""
    Analyze the skill gap for:
    Desired Job Role: {job_role}
    Current Skills: {current_skills}
    
    Please return a JSON object with the following fields:
    - match_percentage: An integer (0 to 100) indicating how well the current skills align with the target job role.
    - missing_skills: A list of strings of critical skills required for the role that the student does not have or needs to build.
    - learning_roadmap: A list of phases/milestones to bridge the gap. Each item in the list must be an object containing:
        - phase: Title of the phase (e.g. 'Phase 1: Foundation')
        - description: What to focus on
        - duration: Estimated time (e.g. '4 weeks')
        - actions: A list of strings of specific study tasks
    - recommended_certifications: A list of strings recommending industry-recognized certifications for the role.
    - recommended_projects: A list of objects for hands-on projects the student should build to demonstrate competence. Each project object must contain:
        - title: Name of project
        - description: Details of what the project does
        - tech_stack: List of technologies to use
        - difficulty: 'Beginner', 'Intermediate', or 'Advanced'
    - resources: A list of objects with learning resources. Each object must contain:
        - name: Resource name (e.g. course or book title)
        - type: 'Course', 'Documentation', 'Tutorial', or 'Book'
        - description: Brief details of how this helps
        
    Make sure the response is valid JSON and contains all these fields.
    """
    
    analysis = generate_json_response(prompt, system_instruction)
    
    if not analysis or not isinstance(analysis, dict):
        raise ValueError("Received invalid skill gap analysis structure from Gemini.")
        
    # Default assignments for robustness
    analysis["match_percentage"] = int(analysis.get("match_percentage", 50))
    analysis["missing_skills"] = list(analysis.get("missing_skills", []))
    analysis["learning_roadmap"] = list(analysis.get("learning_roadmap", []))
    analysis["recommended_certifications"] = list(analysis.get("recommended_certifications", []))
    analysis["recommended_projects"] = list(analysis.get("recommended_projects", []))
    analysis["resources"] = list(analysis.get("resources", []))
    
    # Save to SQLite DB
    save_skill_gap_analysis(
        user_id=user_id,
        job_role=job_role,
        current_skills=current_skills,
        analysis_json=analysis
    )
    
    return analysis
