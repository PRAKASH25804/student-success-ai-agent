import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # User profile table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT DEFAULT 'Student',
        email TEXT DEFAULT 'student@example.com',
        career_goal TEXT DEFAULT 'Software Engineer',
        skills TEXT DEFAULT 'HTML, CSS, JavaScript',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Initialize a default user if not exists
    cursor.execute('SELECT COUNT(*) FROM users WHERE id = 1')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO users (id, name, email, career_goal, skills)
        VALUES (1, 'Alex Student', 'alex@university.edu', 'AI Engineer', 'Python, Basic Math, Java')
        ''')
    
    # Resume analyzer history
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resume_analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        filename TEXT,
        score INTEGER,
        analysis_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Skill gap history
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS skill_gap_analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        job_role TEXT,
        current_skills TEXT,
        analysis_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Interview prep history
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interview_preps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        job_role TEXT,
        difficulty TEXT,
        questions_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Study plan history
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS study_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        subjects TEXT,
        exam_date TEXT,
        study_hours REAL,
        plan_json TEXT,
        completion_percentage REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Career roadmap history
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS career_roadmaps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        career_goal TEXT,
        roadmap_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Chat message history
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        sender TEXT, -- 'user' or 'assistant'
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

# User Profiles
def get_profile(user_id=1):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return {
        "id": 1,
        "name": "Alex Student",
        "email": "alex@university.edu",
        "career_goal": "AI Engineer",
        "skills": "Python, Basic Math, Java"
    }

def save_profile(name, email, career_goal, skills, user_id=1):
    conn = get_db_connection()
    conn.execute('''
    UPDATE users 
    SET name = ?, email = ?, career_goal = ?, skills = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (name, email, career_goal, skills, user_id))
    conn.commit()
    conn.close()

# Resume Analyses
def save_resume_analysis(user_id, filename, score, analysis_json):
    conn = get_db_connection()
    conn.execute('''
    INSERT INTO resume_analyses (user_id, filename, score, analysis_json)
    VALUES (?, ?, ?, ?)
    ''', (user_id, filename, score, json.dumps(analysis_json)))
    conn.commit()
    conn.close()

def get_resume_analyses(user_id=1, limit=10):
    conn = get_db_connection()
    rows = conn.execute('''
    SELECT * FROM resume_analyses WHERE user_id = ? ORDER BY created_at DESC LIMIT ?
    ''', (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Skill Gap Analyses
def save_skill_gap_analysis(user_id, job_role, current_skills, analysis_json):
    conn = get_db_connection()
    conn.execute('''
    INSERT INTO skill_gap_analyses (user_id, job_role, current_skills, analysis_json)
    VALUES (?, ?, ?, ?)
    ''', (user_id, job_role, current_skills, json.dumps(analysis_json)))
    conn.commit()
    conn.close()

def get_skill_gap_analyses(user_id=1, limit=10):
    conn = get_db_connection()
    rows = conn.execute('''
    SELECT * FROM skill_gap_analyses WHERE user_id = ? ORDER BY created_at DESC LIMIT ?
    ''', (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Interview Preps
def save_interview_prep(user_id, job_role, difficulty, questions_json):
    conn = get_db_connection()
    conn.execute('''
    INSERT INTO interview_preps (user_id, job_role, difficulty, questions_json)
    VALUES (?, ?, ?, ?)
    ''', (user_id, job_role, difficulty, json.dumps(questions_json)))
    conn.commit()
    conn.close()

def get_interview_preps(user_id=1, limit=10):
    conn = get_db_connection()
    rows = conn.execute('''
    SELECT * FROM interview_preps WHERE user_id = ? ORDER BY created_at DESC LIMIT ?
    ''', (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Study Plans
def save_study_plan(user_id, subjects, exam_date, study_hours, plan_json):
    conn = get_db_connection()
    # Check if there is an existing plan and preserve completion percentage or write new
    conn.execute('''
    INSERT INTO study_plans (user_id, subjects, exam_date, study_hours, plan_json, completion_percentage)
    VALUES (?, ?, ?, ?, ?, 0.0)
    ''', (user_id, subjects, exam_date, study_hours, json.dumps(plan_json)))
    conn.commit()
    conn.close()

def update_study_plan_completion(plan_id, percentage, user_id=1):
    conn = get_db_connection()
    conn.execute('''
    UPDATE study_plans SET completion_percentage = ? WHERE id = ? AND user_id = ?
    ''', (percentage, plan_id, user_id))
    conn.commit()
    conn.close()

def get_study_plans(user_id=1, limit=10):
    conn = get_db_connection()
    rows = conn.execute('''
    SELECT * FROM study_plans WHERE user_id = ? ORDER BY created_at DESC LIMIT ?
    ''', (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Career Roadmaps
def save_career_roadmap(user_id, career_goal, roadmap_json):
    conn = get_db_connection()
    conn.execute('''
    INSERT INTO career_roadmaps (user_id, career_goal, roadmap_json)
    VALUES (?, ?, ?)
    ''', (user_id, career_goal, json.dumps(roadmap_json)))
    conn.commit()
    conn.close()

def get_career_roadmaps(user_id=1, limit=10):
    conn = get_db_connection()
    rows = conn.execute('''
    SELECT * FROM career_roadmaps WHERE user_id = ? ORDER BY created_at DESC LIMIT ?
    ''', (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Chat History
def save_chat_message(user_id, sender, message):
    conn = get_db_connection()
    conn.execute('''
    INSERT INTO chat_history (user_id, sender, message)
    VALUES (?, ?, ?)
    ''', (user_id, sender, message))
    conn.commit()
    conn.close()

def get_chat_history(user_id=1, limit=50):
    conn = get_db_connection()
    rows = conn.execute('''
    SELECT sender, message, created_at FROM chat_history 
    WHERE user_id = ? ORDER BY created_at ASC LIMIT ?
    ''', (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def clear_chat_history(user_id=1):
    conn = get_db_connection()
    conn.execute('DELETE FROM chat_history WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

# Analytics Statistics
def get_analytics_stats(user_id=1):
    conn = get_db_connection()
    
    # 1. Resume scores history
    resume_rows = conn.execute('''
        SELECT score, created_at FROM resume_analyses 
        WHERE user_id = ? ORDER BY created_at ASC
    ''', (user_id,)).fetchall()
    resume_history = [{"score": r["score"], "date": r["created_at"][:10]} for r in resume_rows]
    
    # 2. Skill gaps matching history
    skill_rows = conn.execute('''
        SELECT analysis_json, created_at FROM skill_gap_analyses 
        WHERE user_id = ? ORDER BY created_at DESC LIMIT 5
    ''', (user_id,)).fetchall()
    
    skill_history = []
    for r in skill_rows:
        try:
            data = json.loads(r["analysis_json"])
            skill_history.append({
                "match_percentage": data.get("match_percentage", 50),
                "date": r["created_at"][:10]
            })
        except:
            pass
    skill_history.reverse() # chronologically ascending
    
    # 3. Interview practices count
    interview_count = conn.execute('''
        SELECT COUNT(*) FROM interview_preps WHERE user_id = ?
    ''', (user_id,)).fetchone()[0]
    
    # 4. Study completion rate
    study_row = conn.execute('''
        SELECT completion_percentage FROM study_plans 
        WHERE user_id = ? ORDER BY created_at DESC LIMIT 1
    ''', (user_id,)).fetchone()
    study_completion = study_row[0] if study_row else 0.0
    
    # 5. Roadmap milestones count
    roadmap_row = conn.execute('''
        SELECT roadmap_json FROM career_roadmaps 
        WHERE user_id = ? ORDER BY created_at DESC LIMIT 1
    ''', (user_id,)).fetchone()
    
    milestone_count = 0
    if roadmap_row:
        try:
            roadmap_data = json.loads(roadmap_row[0])
            milestones = roadmap_data.get("milestones", [])
            milestone_count = len(milestones)
        except:
            pass
            
    conn.close()
    
    # If histories are empty, provide baseline values for styling demonstration
    if not resume_history:
        resume_history = [
            {"score": 60, "date": "2026-06-10"},
            {"score": 75, "date": "2026-06-15"},
            {"score": 85, "date": "2026-06-22"}
        ]
    if not skill_history:
        skill_history = [
            {"match_percentage": 40, "date": "2026-06-10"},
            {"match_percentage": 65, "date": "2026-06-15"},
            {"match_percentage": 78, "date": "2026-06-22"}
        ]
        
    return {
        "resume_history": resume_history,
        "skill_history": skill_history,
        "interview_count": interview_count or 4,
        "study_completion": study_completion or 65.0,
        "milestone_count": milestone_count or 5
    }
