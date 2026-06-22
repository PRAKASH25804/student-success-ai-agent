# SuccessAI — Student Success AI Agent

> Transforming Students into Future Professionals

[![Google Gemini 2.0 Flash](https://img.shields.io/badge/AI-Gemini%202.0%20Flash-blueviolet?style=flat-square&logo=google)](https://deepmind.google/technologies/gemini/)
[![Framework](https://img.shields.io/badge/Backend-Python%20Flask-lightgrey?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-SQLite-blue?style=flat-square&logo=sqlite)](https://sqlite.org/)
[![UI Theme](https://img.shields.io/badge/UI-Glassmorphism%20Dark-purple?style=flat-square)](https://github.com)

A production-ready academic counselor and career readiness platform designed for the **Google Kaggle Vibecoding Agents Capstone Project**. Built using a Python Flask REST API backend, SQLite persistence database, and a vanilla HTML5/CSS3/ES6 Single Page Application (SPA) frontend, the platform integrates Google Gemini 2.0 Flash to empower students in optimizing resumes, analyzing skill gaps, preparing for technical interviews, and generating structured study plans.

---

## 🎨 Brand Identity & Styling

SuccessAI focuses on establishing a professional, trustworthy, and student-focused identity through key branding elements:
- **Logo Icon**: A minimal, vector-based SVG design representing a graduation cap, combined with AI brain hemispheres and an upward career growth arrow.
- **Tagline**: *"Transforming Students into Future Professionals"*
- **Color Palette**:
  - **Electric Purple** (`#8b5cf6`): Innovation, Trust, Cognitive Agency
  - **Bright Blue** (`#3b82f6`): Stable Career Growth, Academic Integrity
  - **Pink Glow** (`#ec4899`): High Energy, Success Milestones
  - **Midnight Violet** (`#090514`): Professional Dark Mode base background

---

## 🌟 Core Features

1. **ATS Resume Analyzer**:
   - Compiles resume scores (0–100) and extracts current skills.
   - Highlights strengths, weaknesses, and ATS-friendly design adjustments.
   - Direct downloads of evaluation reports as formatted `.txt` files.

2. **Skill Gap Analyzer**:
   - Select desired roles (AI Engineer, DevOps, Full-stack) and compare them with your current skills.
   - Outputs match percentages, missing credentials, suggested certifications, and online courses.
   - Recommends tailored portfolio projects to bridge skill gaps.

3. **Interview Preparation Simulator**:
   - Generates Technical, Behavioral (STAR Method), and HR questions mapped to role difficulties.
   - Interactive flashcard sandbox practice mode with slide flips and model answers.

4. **Academic Study Planner**:
   - Allocates study hours for upcoming exams based on subjects and exam date.
   - Generates week-by-week goals, spaced revision tactics, and daily study checklists.
   - Checklist markers sync completion progress directly back to the database.

5. **Milestone Career Roadmap**:
   - Charts milestone timelines, target certifications, online course resources, and internship application strategies.

6. **SuccessAI Student Counsel Chat**:
   - A context-aware chat assistant equipped with student profile details (current skills and career goals).
   - Injected with professional guidance personas to answer complex technical queries and homework questions.

7. **Visual Analytics Dashboard**:
   - Connects Chart.js graphics to SQLite records, tracking resume scores, match progress, and practice frequency.

---

## ⚙️ Architecture Diagram

```
                 ┌────────────────────────────────┐
                 │       SPA FRONTEND (HTML/JS)   │
                 └──────────────┬───▲─────────────┘
                                │   │  JSON REST APIs
                 ┌──────────────▼───┴─────────────┐
                 │     FLASK WEB SERVER (app.py)  │
                 └──────────────┬───▲─────────────┘
                                │   │
      ┌─────────────────────────┼───┼─────────────────────────┐
      ▼                         ▼   ▼                         ▼
┌───────────┐             ┌───────────┐                 ┌───────────┐
│  db.py    │             │ pypdf parser│               │gemini_client│
└─────┬─────┘             └───────────┘                 └─────┬─────┘
      │                           ▲                           │
      ▼                           │ uploads/                  ▼
┌───────────┐                     │                     ┌───────────┐
│ database.db│ (SQLite)          [Resume.pdf]           │Gemini API │ (2.0 Flash)
└───────────┘                                           └───────────┘
```

---

## 🚀 Installation & Local Launch

### Prerequisites
- Python 3.9 or higher
- Google Gemini API Key

### Step-by-Step Setup

1. **Clone or Navigate to the Workspace Directory**:
   ```bash
   cd student-success-ai-agent
   ```

2. **Establish a Python Virtual Environment**:
   ```bash
   python -m venv venv
   # Activate on Windows:
   venv\Scripts\activate
   # Activate on MacOS/Linux:
   source venv/bin/activate
   ```

3. **Install Package Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Environment Credentials**:
   Copy the example environment template and enter your Google Gemini API Key:
   ```bash
   cp .env.example .env
   ```
   Edit `.env`:
   ```env
   GEMINI_API_KEY=AIzaSy...your_gemini_api_key...
   ```

5. **Start Flask Server**:
   ```bash
   python backend/app.py
   ```
   The application will automatically initialize the SQLite tables inside `backend/database.db` and start serving on: **`http://localhost:5000`**

---

## 🧪 Running Unit Tests
Validate database connections, REST API endpoints, profile updates, and routing structures:
```bash
python -m unittest backend/test_api.py
```

---

## 📦 Deployment Instructions

### Deploying to Render (Backend & Frontend Unified)
Render is ideal for hosting Python Flask applications.
1. Create a new **Web Service** on Render and link your Git repository.
2. Configure environment settings:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn backend.app:app`
3. Add Environment Variables under settings:
   - `GEMINI_API_KEY`: *Your Google API Key*
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: *Random secure string*

### Deploying to Vercel (API & Client decoupling)
To run on Vercel:
1. Ensure `vercel.json` is configured in the project root to forward requests to the Flask server.
2. Vercel utilizes Serverless Functions. Install the Vercel CLI: `npm install -g vercel`.
3. Run `vercel` in the project root folder to deploy directly. Add your `GEMINI_API_KEY` to Vercel's project dashboard env settings.

---

## 📄 License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
