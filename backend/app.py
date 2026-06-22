import os
import json
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from backend.db import (
    init_db, get_profile, save_profile, get_chat_history,
    save_chat_message, clear_chat_history, get_analytics_stats,
    update_study_plan_completion, get_resume_analyses, get_skill_gap_analyses,
    get_interview_preps, get_study_plans, get_career_roadmaps
)
from backend.resume_analyzer import analyze_resume
from backend.skill_gap import analyze_skill_gap
from backend.interview_generator import generate_interview_questions
from backend.study_planner import generate_study_plan
from backend.roadmap_generator import generate_roadmap
from backend.chat_assistant import chat_with_assistant

# Load env variables
load_dotenv()

# Setup Flask paths
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))

app = Flask(__name__, static_folder=frontend_dir, template_folder=frontend_dir)
CORS(app) # Enable CORS for development flexibility

# Configurations
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_student_secret_key_9981')
app.config['UPLOAD_FOLDER'] = uploads_dir
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database on startup
with app.app_context():
    init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------- Serve Frontend Routes -----------------

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # Fallback to index.html for SPA routing routing support
        return send_from_directory(app.static_folder, 'index.html')

# ----------------- User Profile API -----------------

@app.route('/api/profile', methods=['GET'])
def get_user_profile():
    try:
        profile = get_profile(user_id=1)
        return jsonify({"status": "success", "profile": profile})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/profile', methods=['POST'])
def update_user_profile():
    try:
        data = request.json
        name = data.get('name', 'Student')
        email = data.get('email', 'student@example.com')
        career_goal = data.get('career_goal', 'Software Engineer')
        skills = data.get('skills', '')
        
        save_profile(name, email, career_goal, skills, user_id=1)
        return jsonify({"status": "success", "message": "Profile updated successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ----------------- Resume Analyzer API -----------------

@app.route('/api/resume/analyze', methods=['POST'])
def api_resume_analyze():
    try:
        # Check if file uploaded
        if 'resume' not in request.files:
            return jsonify({"status": "error", "message": "No file uploaded"}), 400
            
        file = request.files['resume']
        if file.filename == '':
            return jsonify({"status": "error", "message": "No selected file"}), 400
            
        if not allowed_file(file.filename):
            return jsonify({"status": "error", "message": "Only PDF files are supported."}), 400
            
        # Optional custom target role
        target_role = request.form.get('target_role', '')
        if not target_role:
            # Use profile goal if none specified
            profile = get_profile(user_id=1)
            target_role = profile.get('career_goal', 'Software Engineer')
            
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Analyze using backend module
        analysis = analyze_resume(file_path, target_role=target_role, user_id=1)
        
        # Cleanup uploaded file safely
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return jsonify({"status": "success", "analysis": analysis})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ----------------- Skill Gap Analyzer API -----------------

@app.route('/api/skill-gap/analyze', methods=['POST'])
def api_skill_gap_analyze():
    try:
        data = request.json or {}
        job_role = data.get('job_role')
        current_skills = data.get('current_skills')
        
        if not job_role or not current_skills:
            # Auto populate if empty
            profile = get_profile(user_id=1)
            job_role = job_role or profile.get('career_goal')
            current_skills = current_skills or profile.get('skills')
            
        analysis = analyze_skill_gap(job_role, current_skills, user_id=1)
        return jsonify({"status": "success", "analysis": analysis})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ----------------- Interview Prep API -----------------

@app.route('/api/interview/generate', methods=['POST'])
def api_interview_generate():
    try:
        data = request.json or {}
        job_role = data.get('job_role')
        difficulty = data.get('difficulty', 'Intermediate')
        
        if not job_role:
            profile = get_profile(user_id=1)
            job_role = profile.get('career_goal', 'Software Engineer')
            
        questions = generate_interview_questions(job_role, difficulty, user_id=1)
        return jsonify({"status": "success", "questions": questions})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ----------------- Study Planner API -----------------

@app.route('/api/study-planner/generate', methods=['POST'])
def api_study_planner_generate():
    try:
        data = request.json or {}
        subjects = data.get('subjects')
        exam_date = data.get('exam_date')
        study_hours = data.get('study_hours', 2)
        
        if not subjects or not exam_date:
            return jsonify({"status": "error", "message": "Subjects and exam date are required."}), 400
            
        plan = generate_study_plan(subjects, exam_date, study_hours, user_id=1)
        return jsonify({"status": "success", "plan": plan})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/study-planner/update-completion', methods=['POST'])
def api_study_planner_update():
    try:
        data = request.json or {}
        plan_id = data.get('plan_id')
        completion = data.get('completion_percentage', 0.0)
        
        if not plan_id:
            # Update latest plan if no ID specified
            plans = get_study_plans(user_id=1, limit=1)
            if plans:
                plan_id = plans[0]['id']
            else:
                return jsonify({"status": "error", "message": "No active study plan found to update."}), 400
                
        update_study_plan_completion(plan_id, float(completion), user_id=1)
        return jsonify({"status": "success", "message": "Progress updated."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ----------------- Career Roadmap API -----------------

@app.route('/api/roadmap/generate', methods=['POST'])
def api_roadmap_generate():
    try:
        data = request.json or {}
        career_goal = data.get('career_goal')
        
        if not career_goal:
            profile = get_profile(user_id=1)
            career_goal = profile.get('career_goal', 'Software Engineer')
            
        roadmap = generate_roadmap(career_goal, user_id=1)
        return jsonify({"status": "success", "roadmap": roadmap})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ----------------- Chat Assistant API -----------------

@app.route('/api/chat', methods=['POST'])
def api_chat():
    try:
        data = request.json or {}
        message = data.get('message')
        if not message:
            return jsonify({"status": "error", "message": "Empty message."}), 400
            
        reply = chat_with_assistant(message, user_id=1)
        return jsonify({"status": "success", "reply": reply})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/chat/history', methods=['GET'])
def api_chat_history():
    try:
        history = get_chat_history(user_id=1)
        return jsonify({"status": "success", "history": history})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/chat/clear', methods=['POST'])
def api_chat_clear():
    try:
        clear_chat_history(user_id=1)
        return jsonify({"status": "success", "message": "Chat history cleared."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ----------------- Analytics API -----------------

@app.route('/api/analytics', methods=['GET'])
def api_analytics():
    try:
        stats = get_analytics_stats(user_id=1)
        return jsonify({"status": "success", "analytics": stats})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ----------------- Export API (TXT Export) -----------------

@app.route('/api/export/txt/<module_name>', methods=['GET'])
def api_export_txt(module_name):
    try:
        user_id = 1
        profile = get_profile(user_id)
        report_text = f"===========================================================\n"
        report_text += f"                       SuccessAI                           \n"
        report_text += f"      Transforming Students into Future Professionals       \n"
        report_text += f"===========================================================\n"
        report_text += f"Student Name  : {profile['name']}\n"
        report_text += f"Academic Email: {profile['email']}\n"
        report_text += f"Date Exported : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report_text += f"===========================================================\n\n"
        
        filename_prefix = "success_report"
        
        if module_name == "resume":
            analyses = get_resume_analyses(user_id, limit=1)
            if not analyses:
                return "No resume analysis records found to export.", 404
            data = json.loads(analyses[0]['analysis_json'])
            filename_prefix = "resume_analysis"
            
            report_text += f"RESUME SCORES & AUDIT\n"
            report_text += f"Target Role: {analyses[0].get('filename', 'Resume')}\n"
            report_text += f"Score: {data.get('score', 0)}/100\n\n"
            
            report_text += "SKILLS FOUND:\n"
            for s in data.get('skills', []):
                report_text += f" - {s}\n"
            report_text += "\nMISSING SKILLS (RECOMMENDED):\n"
            for s in data.get('missing_skills', []):
                report_text += f" - {s}\n"
            report_text += "\nSTRENGTHS:\n"
            for s in data.get('strengths', []):
                report_text += f" - {s}\n"
            report_text += "\nWEAKNESSES:\n"
            for s in data.get('weaknesses', []):
                report_text += f" - {s}\n"
            report_text += "\nACTIONABLE IMPROVEMENTS:\n"
            for s in data.get('improvements', []):
                report_text += f" - {s}\n"
            report_text += "\nATS OPTIMIZATION TIPS:\n"
            for s in data.get('ats_tips', []):
                report_text += f" - {s}\n"
                
        elif module_name == "skill-gap":
            analyses = get_skill_gap_analyses(user_id, limit=1)
            if not analyses:
                return "No skill gap records found to export.", 404
            data = json.loads(analyses[0]['analysis_json'])
            filename_prefix = "skill_gap_report"
            
            report_text += f"SKILL GAP ANALYSIS: {analyses[0]['job_role']}\n"
            report_text += f"Match Percentage: {data.get('match_percentage', 0)}%\n\n"
            
            report_text += "MISSING SKILLS:\n"
            for s in data.get('missing_skills', []):
                report_text += f" - {s}\n"
                
            report_text += "\nLEARNING ROADMAP:\n"
            for p in data.get('learning_roadmap', []):
                report_text += f"\n* {p.get('phase', 'Phase')} ({p.get('duration', 'Time')})\n"
                report_text += f"  Focus: {p.get('description', '')}\n"
                report_text += f"  Actions:\n"
                for act in p.get('actions', []):
                    report_text += f"    - {act}\n"
                    
            report_text += "\nRECOMMENDED CERTIFICATIONS:\n"
            for s in data.get('recommended_certifications', []):
                report_text += f" - {s}\n"
                
            report_text += "\nRECOMMENDED PORTFOLIO PROJECTS:\n"
            for p in data.get('recommended_projects', []):
                report_text += f"\n* Project: {p.get('title', 'Project')}\n"
                report_text += f"  Difficulty: {p.get('difficulty', '')}\n"
                report_text += f"  Tech Stack: {', '.join(p.get('tech_stack', []))}\n"
                report_text += f"  Description: {p.get('description', '')}\n"
                
        elif module_name == "interview":
            preps = get_interview_preps(user_id, limit=1)
            if not preps:
                return "No mock interview records found to export.", 404
            data = json.loads(preps[0]['questions_json'])
            filename_prefix = "interview_questions"
            
            report_text += f"INTERVIEW PREPARATION: {preps[0]['job_role']} ({preps[0]['difficulty']})\n\n"
            
            report_text += "--- TECHNICAL QUESTIONS ---\n"
            for idx, q in enumerate(data.get('technical', [])):
                report_text += f"\nQ{idx+1}: {q.get('question')}\n"
                report_text += f"Sample Answer: {q.get('answer')}\n"
                report_text += f"Tips: {q.get('tips')}\n"
                
            report_text += "\n--- BEHAVIORAL QUESTIONS ---\n"
            for idx, q in enumerate(data.get('behavioral', [])):
                report_text += f"\nQ{idx+1}: {q.get('question')}\n"
                report_text += f"STAR Model Sample: {q.get('answer')}\n"
                report_text += f"Tips: {q.get('tips')}\n"
                
            report_text += "\n--- HR QUESTIONS ---\n"
            for idx, q in enumerate(data.get('hr', [])):
                report_text += f"\nQ{idx+1}: {q.get('question')}\n"
                report_text += f"Sample Answer: {q.get('answer')}\n"
                report_text += f"Tips: {q.get('tips')}\n"
                
            report_text += "\n--- SYSTEM PREPARATION TIPS ---\n"
            for s in data.get('general_tips', []):
                report_text += f" - {s}\n"
                
        elif module_name == "study":
            plans = get_study_plans(user_id, limit=1)
            if not plans:
                return "No study planner records found to export.", 404
            data = json.loads(plans[0]['plan_json'])
            filename_prefix = "study_schedule"
            
            report_text += f"STUDY SCHEDULE FOR EXAMS\n"
            report_text += f"Subjects: {plans[0]['subjects']}\n"
            report_text += f"Target Exam Date: {plans[0]['exam_date']}\n"
            report_text += f"Daily Allocated Study Hours: {plans[0]['study_hours']} hrs\n\n"
            
            report_text += "WEEKLY MILESTONES:\n"
            for g in data.get('weekly_goals', []):
                report_text += f" - {g}\n"
                
            report_text += "\nREPRESENTATIVE WEEKLY ROTATION:\n"
            for d in data.get('daily_schedule', []):
                report_text += f"\n* {d.get('day')}:\n"
                report_text += f"  Subjects: {', '.join(d.get('subjects', []))}\n"
                report_text += f"  Topic: {d.get('topic')}\n"
                report_text += f"  Hours: {d.get('hours')} hrs\n"
                report_text += f"  Task: {d.get('task')}\n"
                
            report_text += "\nFINAL REVISION PLAN:\n"
            for r in data.get('revision_plan', []):
                report_text += f" - {r}\n"
                
            report_text += "\nSTUDY TIP LIST:\n"
            for t in data.get('tips', []):
                report_text += f" - {t}\n"
                
        elif module_name == "roadmap":
            roadmaps = get_career_roadmaps(user_id, limit=1)
            if not roadmaps:
                return "No career roadmap records found to export.", 404
            data = json.loads(roadmaps[0]['roadmap_json'])
            filename_prefix = "career_roadmap"
            
            report_text += f"CAREER ROADMAP: {roadmaps[0]['career_goal']}\n\n"
            
            report_text += "LEARNING MILESTONES & TIMELINE:\n"
            for m in data.get('milestones', []):
                report_text += f"\n* {m.get('title')} ({m.get('target_time')})\n"
                report_text += f"  Focus: {m.get('description')}\n"
                report_text += f"  Skills to Acquire:\n"
                for s in m.get('skills_to_acquire', []):
                    report_text += f"    - {s}\n"
                report_text += f"  Suggested Portfolio Projects:\n"
                for p in m.get('projects_to_do', []):
                    report_text += f"    - {p}\n"
                    
            report_text += "\nRECOMMENDED CERTIFICATIONS:\n"
            for c in data.get('certifications', []):
                report_text += f" - {c}\n"
                
            report_text += "\nRESOURCES/COURSES:\n"
            for c in data.get('courses', []):
                report_text += f" - {c}\n"
                
            report_text += "\nINTERNSHIP GUIDANCE:\n"
            for g in data.get('internship_guidance', []):
                report_text += f" - {g}\n"
        else:
            return "Invalid module name specified for export.", 400
            
        response = make_response(report_text)
        response.headers["Content-Disposition"] = f"attachment; filename={filename_prefix}_{datetime.now().strftime('%Y%m%d')}.txt"
        response.headers["Content-Type"] = "text/plain; charset=utf-8"
        return response
        
    except Exception as e:
        return f"Error exporting report: {str(e)}", 500

# ----------------- Start Flask Server -----------------

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # In development, use debug=True, disable for production deploy
    app.run(host='0.0.0.0', port=port, debug=True)
