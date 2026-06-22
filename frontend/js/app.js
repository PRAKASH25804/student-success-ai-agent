// ========================================== //
//              GLOBAL APPLICATION STATE      //
// ========================================== //
const STATE = {
    user: {
        name: "Alex Student",
        email: "alex@university.edu",
        careerGoal: "AI Engineer",
        skills: "Python, Basic Math, Java"
    },
    activeTab: "home",
    charts: {},
    activeMockDeck: null,
    mockCurrentIndex: 0,
    activeStudyTasks: [],
    checkedStudyTasks: 0
};

const API_BASE = window.location.origin;

// Initialize on DOM Load
document.addEventListener("DOMContentLoaded", () => {
    // 1. Run Particle Background Animation on Landing Page
    initParticles();
    
    // 2. Load User Profile and Analytics from database
    syncUserProfile();
    
    // 3. Setup Events Listeners for Forms & Dropzones
    setupEventListeners();
    
    // 4. Initialize Lucide SVGs
    lucide.createIcons();
    
    // 5. Dismiss Loading Splash Screen
    setTimeout(() => {
        const loader = document.getElementById("loading-screen");
        if (loader) {
            loader.classList.add("fade-out");
            setTimeout(() => loader.remove(), 600);
        }
    }, 1500);
});

// ========================================== //
//            TOAST NOTIFICATION ENGINE       //
// ========================================== //
function showToast(message, type = "success") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    
    let icon = "info";
    if (type === "success") icon = "check-circle";
    if (type === "error") icon = "alert-circle";
    if (type === "warning") icon = "alert-triangle";
    
    toast.innerHTML = `
        <i data-lucide="${icon}"></i>
        <span>${message}</span>
    `;
    container.appendChild(toast);
    lucide.createIcons();
    
    setTimeout(() => {
        toast.style.animation = "toastIn 0.3s reverse forwards";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ========================================== //
//            SPA TAB NAVIGATION ENGINE       //
// ========================================== //
function scrollToElement(id) {
    const el = document.getElementById(id);
    if (el) {
        el.scrollIntoView({ behavior: "smooth" });
    }
}

function launchDashboard(preSelectTab = "home") {
    document.getElementById("landing-header").classList.add("hide");
    document.getElementById("landing-section").classList.remove("active");
    document.getElementById("dashboard-container").classList.add("active");
    showTab(preSelectTab);
}

function exitDashboard() {
    document.getElementById("landing-header").classList.remove("hide");
    document.getElementById("landing-section").classList.add("active");
    document.getElementById("dashboard-container").classList.remove("active");
}

function showTab(tabId) {
    // Deactivate previous
    document.querySelectorAll(".nav-item").forEach(item => item.classList.remove("active"));
    document.querySelectorAll(".view-panel").forEach(panel => panel.classList.remove("active"));
    
    // Activate current
    const navItem = document.getElementById(`tab-${tabId}`);
    const panel = document.getElementById(`view-${tabId}`);
    
    if (navItem && panel) {
        navItem.classList.add("active");
        panel.classList.add("active");
        STATE.activeTab = tabId;
        
        // Tab specific loading
        if (tabId === "home") {
            loadDashboardSummary();
        } else if (tabId === "analytics") {
            loadAnalyticsDashboard();
        } else if (tabId === "chat") {
            restoreChatHistory();
        }
        
        // Update header subtitles
        const titles = {
            home: ["Dashboard Hub", "Your academic & career readiness summary"],
            resume: ["Resume Evaluator", "Upload PDF resume and evaluate against target ATS criteria"],
            "skill-gap": ["Skill Gap Analyzer", "Cross-reference current skills with job expectations"],
            interview: ["Interview Prep Simulator", "Rehearsal recruiter questions tailored by difficulty"],
            study: ["Exam Study Routine", "Prepare study schedules and daily checklist timelines"],
            roadmap: ["Career Roadmap", "Milestones, certificates, and guides for landing internships"],
            chat: ["SuccessAI Counselor", "Dynamic academic advising and homework/project resolver"],
            analytics: ["Analytics Panel", "Visual trends of scores, gap match rates, and milestones"],
            profile: ["User Settings", "Manage academic targets and skillset profile records"],
            settings: ["Application Config", "Fine-tune UI features and reset databases"]
        };
        
        document.getElementById("page-title").innerText = titles[tabId][0];
        document.getElementById("page-subtitle").innerText = titles[tabId][1];
    }
}

function switchSubTab(button, tabId) {
    const parent = button.parentElement;
    parent.querySelectorAll(".sub-tab").forEach(tab => tab.classList.remove("active"));
    button.classList.add("active");
    
    const contentContainer = parent.parentElement;
    contentContainer.querySelectorAll(".sub-tab-content").forEach(content => {
        content.classList.remove("active");
    });
    document.getElementById(tabId).classList.add("active");
}

// ========================================== //
//            PARTICLE ANIMATION ENGINE       //
// ========================================== //
function initParticles() {
    const canvas = document.getElementById("particle-canvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = 650);
    
    window.addEventListener("resize", () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = 650;
    });
    
    const particles = [];
    for (let i = 0; i < 45; i++) {
        particles.push({
            x: Math.random() * width,
            y: Math.random() * height,
            vx: (Math.random() - 0.5) * 0.4,
            vy: (Math.random() - 0.5) * 0.4,
            radius: Math.random() * 3 + 1
        });
    }
    
    function animate() {
        ctx.clearRect(0, 0, width, height);
        ctx.fillStyle = "rgba(139, 92, 246, 0.4)";
        ctx.strokeStyle = "rgba(59, 130, 246, 0.08)";
        
        particles.forEach((p, idx) => {
            p.x += p.vx;
            p.y += p.vy;
            
            if (p.x < 0 || p.x > width) p.vx *= -1;
            if (p.y < 0 || p.y > height) p.vy *= -1;
            
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fill();
            
            // Draw connector lines
            for (let j = idx + 1; j < particles.length; j++) {
                const p2 = particles[j];
                const dist = Math.hypot(p.x - p2.x, p.y - p2.y);
                if (dist < 120) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            }
        });
        
        requestAnimationFrame(animate);
    }
    animate();
}

// ========================================== //
//            USER PROFILE & DATABASE SYNC    //
// ========================================== //
function syncUserProfile() {
    fetch(`${API_BASE}/api/profile`)
        .then(res => res.json())
        .then(data => {
            if (data.status === "success" && data.profile) {
                const p = data.profile;
                STATE.user = {
                    name: p.name,
                    email: p.email,
                    careerGoal: p.career_goal,
                    skills: p.skills
                };
                
                // Update Sidebar values
                document.getElementById("sidebar-user-name").innerText = p.name;
                document.getElementById("sidebar-user-role").innerText = p.career_goal;
                
                // Set User initials
                const parts = p.name.split(" ");
                const initials = parts.map(n => n[0]).join("").toUpperCase().substring(0, 2);
                document.getElementById("sidebar-user-initials").innerText = initials;
                
                // Update profile forms defaults
                document.getElementById("profile-name").value = p.name;
                document.getElementById("profile-email").value = p.email;
                document.getElementById("profile-goal").value = p.career_goal;
                document.getElementById("profile-skills").value = p.skills;
                
                // Populate forms across app
                document.getElementById("resume-target-role").value = p.career_goal;
                document.getElementById("skill-job-role").value = p.career_goal;
                document.getElementById("skill-current-list").value = p.skills;
                document.getElementById("interview-job-role").value = p.career_goal;
                document.getElementById("roadmap-career-goal").value = p.career_goal;
                
                // Sync Header
                document.getElementById("header-user-name").innerText = p.name;
            }
        })
        .catch(err => console.error("Database connection check failed: ", err));
}

function saveUserProfile(event) {
    event.preventDefault();
    const btn = document.getElementById("profile-save-btn");
    btn.disabled = true;
    
    const payload = {
        name: document.getElementById("profile-name").value,
        email: document.getElementById("profile-email").value,
        career_goal: document.getElementById("profile-goal").value,
        skills: document.getElementById("profile-skills").value
    };
    
    fetch(`${API_BASE}/api/profile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        btn.disabled = false;
        if (data.status === "success") {
            showToast("Profile changes synced to DB successfully!", "success");
            syncUserProfile();
            showTab("home");
        } else {
            showToast(data.message, "error");
        }
    })
    .catch(err => {
        btn.disabled = false;
        showToast("Server Sync Failed.", "error");
    });
}

// ========================================== //
//            DASHBOARD SUMMARY PANEL         //
// ========================================== //
function loadDashboardSummary() {
    fetch(`${API_BASE}/api/analytics`)
        .then(res => res.json())
        .then(data => {
            if (data.status === "success" && data.analytics) {
                const a = data.analytics;
                
                // Resume Stat
                const latestResume = a.resume_history[a.resume_history.length - 1];
                document.getElementById("home-stat-resume-score").innerText = latestResume ? `${latestResume.score}/100` : "0/100";
                
                // Skill Match
                const latestSkill = a.skill_history[a.skill_history.length - 1];
                document.getElementById("home-stat-skill-match").innerText = latestSkill ? `${latestSkill.match_percentage}%` : "0%";
                
                // Study progress
                const completion = Math.round(a.study_completion);
                document.getElementById("home-stat-study-progress").innerText = `${completion}%`;
                document.getElementById("home-stat-study-bar").style.width = `${completion}%`;
                
                // Interview Count
                document.getElementById("home-stat-interview-count").innerText = a.interview_count;
                
                // Target role sync
                document.getElementById("home-target-role").innerText = STATE.user.careerGoal;
                
                // Skills list tags
                const tagBox = document.getElementById("home-skills-tags");
                tagBox.innerHTML = "";
                STATE.user.skills.split(",").forEach(s => {
                    if (s.trim()) {
                        const span = document.createElement("span");
                        span.className = "tag";
                        span.innerText = s.trim();
                        tagBox.appendChild(span);
                    }
                });
                
                // Render mini dashboard overview chart
                renderMiniOverviewChart(a.resume_history, a.skill_history);
            }
        });
}

function renderMiniOverviewChart(resumeHistory, skillHistory) {
    const ctx = document.getElementById("home-mini-chart");
    if (!ctx) return;
    
    // Destroy previous instance
    if (STATE.charts.miniOverview) {
        STATE.charts.miniOverview.destroy();
    }
    
    const labels = resumeHistory.map(r => r.date);
    const resumeScores = resumeHistory.map(r => r.score);
    const skillMatches = skillHistory.map(s => s.match_percentage);
    
    STATE.charts.miniOverview = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Resume Score',
                    data: resumeScores,
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'Job Match Rate',
                    data: skillMatches,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.3,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: true, labels: { color: '#9f96b3', font: { family: 'Outfit' } } }
            },
            scales: {
                y: { min: 0, max: 100, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9f96b3' } },
                x: { grid: { display: false }, ticks: { color: '#9f96b3' } }
            }
        }
    });
}

// ========================================== //
//            RESUME ANALYZER MODULE          //
// ========================================== //
function handleResumeSubmit(event) {
    event.preventDefault();
    const fileInput = document.getElementById("resume-file-input");
    const targetInput = document.getElementById("resume-target-role");
    const skeleton = document.getElementById("resume-skeleton");
    const content = document.getElementById("resume-results-content");
    const emptyState = document.getElementById("resume-empty");
    const submitBtn = document.getElementById("resume-submit-btn");
    
    if (!fileInput.files.length) {
        showToast("Please upload a PDF file first.", "warning");
        return;
    }
    
    // Toggle loading states
    submitBtn.disabled = true;
    emptyState.classList.add("hide");
    skeleton.classList.remove("hide");
    content.classList.add("hide");
    
    const formData = new FormData();
    formData.append("resume", fileInput.files[0]);
    formData.append("target_role", targetInput.value);
    
    fetch(`${API_BASE}/api/resume/analyze`, {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        submitBtn.disabled = false;
        skeleton.classList.add("hide");
        
        if (data.status === "success" && data.analysis) {
            content.classList.remove("hide");
            showToast("Resume parsed and audited successfully!", "success");
            renderResumeAnalysis(data.analysis);
        } else {
            emptyState.classList.remove("hide");
            showToast(data.message || "Failed to analyze resume.", "error");
        }
    })
    .catch(err => {
        submitBtn.disabled = false;
        skeleton.classList.add("hide");
        emptyState.classList.remove("hide");
        showToast("API timeout or network failure.", "error");
    });
}

function renderResumeAnalysis(analysis) {
    // Score gauge animation
    const circle = document.getElementById("resume-score-circle");
    const scoreText = document.getElementById("resume-score-text");
    const score = analysis.score;
    
    // SVG circle path stroke circumference is 100 max
    circle.setAttribute("stroke-dasharray", `${score}, 100`);
    scoreText.innerText = `${score}%`;
    
    // Skills found tags
    const foundBox = document.getElementById("resume-skills-found");
    foundBox.innerHTML = "";
    analysis.skills.forEach(s => {
        const span = document.createElement("span");
        span.className = "tag";
        span.innerText = s;
        foundBox.appendChild(span);
    });
    
    // Missing skills
    const missingBox = document.getElementById("resume-skills-missing");
    missingBox.innerHTML = "";
    analysis.missing_skills.forEach(s => {
        const span = document.createElement("span");
        span.className = "tag";
        span.style.borderColor = "var(--danger)";
        span.innerText = s;
        missingBox.appendChild(span);
    });
    
    // Strengths
    const strengthUl = document.getElementById("resume-strengths-list");
    strengthUl.innerHTML = "";
    analysis.strengths.forEach(s => {
        const li = document.createElement("li");
        li.innerText = s;
        strengthUl.appendChild(li);
    });
    
    // Weaknesses
    const weakUl = document.getElementById("resume-weaknesses-list");
    weakUl.innerHTML = "";
    analysis.weaknesses.forEach(w => {
        const li = document.createElement("li");
        li.innerText = w;
        weakUl.appendChild(li);
    });
    
    // Improvements
    const impUl = document.getElementById("resume-improvements-list");
    impUl.innerHTML = "";
    analysis.improvements.forEach(i => {
        const li = document.createElement("li");
        li.innerText = i;
        impUl.appendChild(li);
    });
    
    // ATS Guidelines
    const atsUl = document.getElementById("resume-ats-list");
    atsUl.innerHTML = "";
    analysis.ats_tips.forEach(t => {
        const li = document.createElement("li");
        li.innerText = t;
        atsUl.appendChild(li);
    });
}

// ========================================== //
//            SKILL GAP ANALYZER MODULE       //
// ========================================== //
function handleSkillGapSubmit(event) {
    event.preventDefault();
    const role = document.getElementById("skill-job-role").value;
    const skills = document.getElementById("skill-current-list").value;
    const skeleton = document.getElementById("skill-skeleton");
    const content = document.getElementById("skill-results-content");
    const emptyState = document.getElementById("skill-empty");
    const submitBtn = document.getElementById("skill-submit-btn");
    
    submitBtn.disabled = true;
    emptyState.classList.add("hide");
    skeleton.classList.remove("hide");
    content.classList.add("hide");
    
    fetch(`${API_BASE}/api/skill-gap/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_role: role, current_skills: skills })
    })
    .then(res => res.json())
    .then(data => {
        submitBtn.disabled = false;
        skeleton.classList.add("hide");
        if (data.status === "success" && data.analysis) {
            content.classList.remove("hide");
            showToast("Skills compared against market index.", "success");
            renderSkillGapAnalysis(data.analysis);
        } else {
            emptyState.classList.remove("hide");
            showToast(data.message || "Failed to compare skills.", "error");
        }
    })
    .catch(err => {
        submitBtn.disabled = false;
        skeleton.classList.add("hide");
        emptyState.classList.remove("hide");
        showToast("API timeout or server error.", "error");
    });
}

function renderSkillGapAnalysis(analysis) {
    // Match bar
    const bar = document.getElementById("skill-match-bar");
    const text = document.getElementById("skill-match-percent");
    bar.style.width = `${analysis.match_percentage}%`;
    text.innerText = `Match Rate: ${analysis.match_percentage}%`;
    
    // Missing tags
    const missingBox = document.getElementById("skill-missing-tags");
    missingBox.innerHTML = "";
    analysis.missing_skills.forEach(s => {
        const span = document.createElement("span");
        span.className = "tag";
        span.style.borderColor = "var(--danger)";
        span.innerText = s;
        missingBox.appendChild(span);
    });
    
    // Certs
    const certUl = document.getElementById("skill-certs-list");
    certUl.innerHTML = "";
    analysis.recommended_certifications.forEach(c => {
        const li = document.createElement("li");
        li.innerText = c;
        certUl.appendChild(li);
    });
    
    // Resources Grid
    const resourceGrid = document.getElementById("skill-resources-grid");
    resourceGrid.innerHTML = "";
    analysis.resources.forEach(r => {
        const div = document.createElement("div");
        div.className = "resource-box";
        div.innerHTML = `
            <span class="res-type">${r.type}</span>
            <h5>${r.name}</h5>
            <p>${r.description}</p>
        `;
        resourceGrid.appendChild(div);
    });
    
    // Learning Roadmap Phases
    const timeline = document.getElementById("skill-roadmap-timeline");
    timeline.innerHTML = "";
    analysis.learning_roadmap.forEach((p, idx) => {
        const dev = document.createElement("div");
        dev.className = "timeline-phase";
        
        let actionLi = "";
        p.actions.forEach(act => actionLi += `<li>${act}</li>`);
        
        dev.innerHTML = `
            <div class="phase-number">${idx+1}</div>
            <div class="phase-detail">
                <span class="phase-time">${p.duration}</span>
                <h5>${p.phase}</h5>
                <p>${p.description}</p>
                <ul class="bullet-list-small">${actionLi}</ul>
            </div>
        `;
        timeline.appendChild(dev);
    });
    
    // Recommended Portfolio projects
    const projs = document.getElementById("skill-projects-list");
    projs.innerHTML = "";
    analysis.recommended_projects.forEach(p => {
        const card = document.createElement("div");
        card.className = "project-card";
        card.innerHTML = `
            <div class="project-card-header">
                <h5>${p.title}</h5>
                <span class="proj-diff ${p.difficulty.toLowerCase()}">${p.difficulty}</span>
            </div>
            <p>${p.description}</p>
            <div class="tag-container">
                ${p.tech_stack.map(t => `<span class="tag">${t}</span>`).join("")}
            </div>
        `;
        projs.appendChild(card);
    });
}

// ========================================== //
//            INTERVIEW PREPARATION MODULE    //
// ========================================== //
function handleInterviewSubmit(event) {
    event.preventDefault();
    const role = document.getElementById("interview-job-role").value;
    const diff = document.getElementById("interview-difficulty").value;
    const skeleton = document.getElementById("interview-skeleton");
    const content = document.getElementById("interview-results-content");
    const emptyState = document.getElementById("interview-empty");
    const submitBtn = document.getElementById("interview-submit-btn");
    const startPracticeBtn = document.getElementById("start-mock-btn");
    
    // Clear flashcard view if open
    document.getElementById("mock-sandbox-viewport").classList.add("hide");
    
    submitBtn.disabled = true;
    emptyState.classList.add("hide");
    skeleton.classList.remove("hide");
    content.classList.add("hide");
    
    fetch(`${API_BASE}/api/interview/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_role: role, difficulty: diff })
    })
    .then(res => res.json())
    .then(data => {
        submitBtn.disabled = false;
        skeleton.classList.add("hide");
        if (data.status === "success" && data.questions) {
            content.classList.remove("hide");
            startPracticeBtn.disabled = false;
            STATE.activeMockDeck = data.questions;
            showToast("Mock Interview deck generated.", "success");
            renderInterviewQuestions(data.questions);
        } else {
            emptyState.classList.remove("hide");
            showToast(data.message || "Failed to generate questions.", "error");
        }
    })
    .catch(err => {
        submitBtn.disabled = false;
        skeleton.classList.add("hide");
        emptyState.classList.remove("hide");
        showToast("API connection error.", "error");
    });
}

function renderInterviewQuestions(q) {
    const renderAccordionList = (questions, containerId) => {
        const box = document.getElementById(containerId);
        box.innerHTML = "";
        
        questions.forEach((item, idx) => {
            const div = document.createElement("div");
            div.className = "accordion-item";
            div.innerHTML = `
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <span>Q${idx+1}: ${item.question}</span>
                    <i data-lucide="chevron-down" class="accordion-icon"></i>
                </div>
                <div class="accordion-body">
                    <div class="accordion-content">
                        <h5>Sample Response Outline:</h5>
                        <p>${item.answer}</p>
                        <div class="tips-box">
                            <strong>Coach Tip:</strong> ${item.tips}
                        </div>
                    </div>
                </div>
            `;
            box.appendChild(div);
        });
    };
    
    renderAccordionList(q.technical, "interview-tech-accordion");
    renderAccordionList(q.behavioral, "interview-behavioral-accordion");
    renderAccordionList(q.hr, "interview-hr-accordion");
    
    // Tips
    const tipsBox = document.getElementById("interview-tips-list");
    tipsBox.innerHTML = "";
    q.general_tips.forEach(t => {
        const li = document.createElement("li");
        li.innerText = t;
        tipsBox.appendChild(li);
    });
    
    lucide.createIcons();
}

function toggleAccordion(header) {
    const item = header.parentElement;
    const isActive = item.classList.contains("active");
    
    // Close other siblings
    item.parentElement.querySelectorAll(".accordion-item").forEach(sib => {
        sib.classList.remove("active");
        sib.querySelector(".accordion-body").style.maxHeight = null;
    });
    
    if (!isActive) {
        item.classList.add("active");
        const body = item.querySelector(".accordion-body");
        body.style.maxHeight = body.scrollHeight + "px";
    }
}

// Interactive Mock Sandbox Operations
function startMockInterview() {
    if (!STATE.activeMockDeck) return;
    
    // Hide standard lists, show card panel
    document.getElementById("interview-results-content").classList.add("hide");
    document.getElementById("mock-sandbox-viewport").classList.remove("hide");
    
    // Consolidate questions
    const q = STATE.activeMockDeck;
    STATE.consolidatedMockQuestions = [
        ...q.technical.map(x => ({...x, category: "Technical"})),
        ...q.behavioral.map(x => ({...x, category: "Behavioral (STAR Method)"})),
        ...q.hr.map(x => ({...x, category: "HR / Fit"}))
    ];
    
    STATE.mockCurrentIndex = 0;
    renderFlashcardQuestion();
}

function exitMockInterview() {
    document.getElementById("mock-sandbox-viewport").classList.add("hide");
    document.getElementById("interview-results-content").classList.remove("hide");
}

function renderFlashcardQuestion() {
    const items = STATE.consolidatedMockQuestions;
    if (!items || !items.length) return;
    
    const current = items[STATE.mockCurrentIndex];
    document.getElementById("mock-current-idx").innerText = STATE.mockCurrentIndex + 1;
    document.getElementById("mock-total-count").innerText = items.length;
    
    // Set card face values
    document.getElementById("mock-card-category").innerText = current.category;
    document.getElementById("mock-card-question").innerText = current.question;
    document.getElementById("mock-card-answer").innerText = current.answer;
    document.getElementById("mock-card-tips").innerText = current.tips;
    
    // Reset flip status
    document.getElementById("interview-flashcard").classList.remove("flipped");
}

function flipFlashcard() {
    document.getElementById("interview-flashcard").classList.toggle("flipped");
}

function prevMockQuestion() {
    if (STATE.mockCurrentIndex > 0) {
        STATE.mockCurrentIndex--;
        renderFlashcardQuestion();
    } else {
        showToast("First question in deck.", "info");
    }
}

function nextMockQuestion() {
    if (STATE.mockCurrentIndex < STATE.consolidatedMockQuestions.length - 1) {
        STATE.mockCurrentIndex++;
        renderFlashcardQuestion();
    } else {
        showToast("Mock deck finished. Excellent practice!", "success");
        exitMockInterview();
    }
}

// ========================================== //
//            STUDY PLANNER MODULE            //
// ========================================== //
function handleStudyPlannerSubmit(event) {
    event.preventDefault();
    const subjects = document.getElementById("study-subjects").value;
    const examDate = document.getElementById("study-exam-date").value;
    const hours = document.getElementById("study-hours").value;
    
    const skeleton = document.getElementById("study-skeleton");
    const content = document.getElementById("study-results-content");
    const emptyState = document.getElementById("study-empty");
    const submitBtn = document.getElementById("study-submit-btn");
    
    submitBtn.disabled = true;
    emptyState.classList.add("hide");
    skeleton.classList.remove("hide");
    content.classList.add("hide");
    
    fetch(`${API_BASE}/api/study-planner/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subjects, exam_date: examDate, study_hours: hours })
    })
    .then(res => res.json())
    .then(data => {
        submitBtn.disabled = false;
        skeleton.classList.add("hide");
        if (data.status === "success" && data.plan) {
            content.classList.remove("hide");
            showToast("Academic study schedule calculated.", "success");
            renderStudyPlan(data.plan);
        } else {
            emptyState.classList.remove("hide");
            showToast(data.message || "Failed to create planner.", "error");
        }
    })
    .catch(err => {
        submitBtn.disabled = false;
        skeleton.classList.add("hide");
        emptyState.classList.remove("hide");
        showToast("Failed to connect to study coordinator.", "error");
    });
}

function renderStudyPlan(plan) {
    // Weekly goals
    const goalsUl = document.getElementById("study-weekly-goals");
    goalsUl.innerHTML = "";
    plan.weekly_goals.forEach(g => {
        const li = document.createElement("li");
        li.innerText = g;
        goalsUl.appendChild(li);
    });
    
    // Calendar view (Representing representative 7 days checklist)
    const cards = document.getElementById("study-calendar-cards");
    cards.innerHTML = "";
    
    STATE.activeStudyTasks = plan.daily_schedule;
    STATE.checkedStudyTasks = 0;
    updateStudyCompletionDisplay(0);
    
    plan.daily_schedule.forEach((d, idx) => {
        const dev = document.createElement("div");
        dev.className = "calendar-card";
        dev.id = `cal-card-${idx}`;
        dev.innerHTML = `
            <div class="calendar-card-header">
                <h5>${d.day}</h5>
                <span class="cal-hours">${d.hours} hrs</span>
            </div>
            <div class="cal-subj">${d.subjects.join(", ")}</div>
            <div class="cal-topic">${d.topic}</div>
            <div class="cal-task-desc">${d.task}</div>
            
            <label class="checkbox-control">
                <input type="checkbox" onchange="toggleStudyTask(${idx}, this)">
                <span>Mark Completed</span>
            </label>
        `;
        cards.appendChild(dev);
    });
    
    // Revision roadmap
    const revUl = document.getElementById("study-revision-list");
    revUl.innerHTML = "";
    plan.revision_plan.forEach(r => {
        const li = document.createElement("li");
        li.innerText = r;
        revUl.appendChild(li);
    });
}

function toggleStudyTask(idx, checkbox) {
    const card = document.getElementById(`cal-card-${idx}`);
    if (checkbox.checked) {
        card.classList.add("completed");
        STATE.checkedStudyTasks++;
    } else {
        card.classList.remove("completed");
        STATE.checkedStudyTasks--;
    }
    
    const percentage = Math.round((STATE.checkedStudyTasks / STATE.activeStudyTasks.length) * 100);
    updateStudyCompletionDisplay(percentage);
    
    // Sync completion status to server database (SQLite progress tracking)
    fetch(`${API_BASE}/api/study-planner/update-completion`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ completion_percentage: percentage })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status !== "success") {
            console.error("Progress save failed: ", data.message);
        }
    });
}

function updateStudyCompletionDisplay(percentage) {
    document.getElementById("study-percent-text").innerText = `${percentage}%`;
    document.getElementById("study-percent-bar").style.width = `${percentage}%`;
}

// ========================================== //
//            CAREER ROADMAP MODULE            //
// ========================================== //
function handleRoadmapSubmit(event) {
    event.preventDefault();
    const goal = document.getElementById("roadmap-career-goal").value;
    const skeleton = document.getElementById("roadmap-skeleton");
    const content = document.getElementById("roadmap-results-content");
    const emptyState = document.getElementById("roadmap-empty");
    const submitBtn = document.getElementById("roadmap-submit-btn");
    
    submitBtn.disabled = true;
    emptyState.classList.add("hide");
    skeleton.classList.remove("hide");
    content.classList.add("hide");
    
    fetch(`${API_BASE}/api/roadmap/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ career_goal: goal })
    })
    .then(res => res.json())
    .then(data => {
        submitBtn.disabled = false;
        skeleton.classList.add("hide");
        if (data.status === "success" && data.roadmap) {
            content.classList.remove("hide");
            showToast("Career milestone timeline mapped.", "success");
            renderRoadmap(data.roadmap);
        } else {
            emptyState.classList.remove("hide");
            showToast(data.message || "Failed to map roadmap.", "error");
        }
    })
    .catch(err => {
        submitBtn.disabled = false;
        skeleton.classList.add("hide");
        emptyState.classList.remove("hide");
        showToast("Roadmap planner network connection error.", "error");
    });
}

function renderRoadmap(r) {
    const tree = document.getElementById("roadmap-timeline-tree");
    tree.innerHTML = "";
    
    r.milestones.forEach((m, idx) => {
        const node = document.createElement("div");
        node.className = "timeline-node";
        
        let skillsLi = m.skills_to_acquire.map(s => `<li>${s}</li>`).join("");
        let projsLi = m.projects_to_do.map(p => `<li>${p}</li>`).join("");
        
        node.innerHTML = `
            <div class="node-bullet"><i data-lucide="check-circle"></i></div>
            <div class="node-box">
                <div class="node-header">
                    <h4>Milestone ${idx+1}: ${m.title}</h4>
                    <span class="node-time">${m.target_time}</span>
                </div>
                <p>${m.description}</p>
                <div class="node-lists">
                    <div class="node-lists-col">
                        <h5>Skills to Master:</h5>
                        <ul class="bullet-list-small">${skillsLi}</ul>
                    </div>
                    <div class="node-lists-col">
                        <h5>Portfolio Deliverables:</h5>
                        <ul class="bullet-list-small">${projsLi}</ul>
                    </div>
                </div>
            </div>
        `;
        tree.appendChild(node);
    });
    
    // Courses list
    const courseUl = document.getElementById("roadmap-courses-list");
    courseUl.innerHTML = "";
    r.courses.forEach(c => {
        const li = document.createElement("li");
        li.innerText = c;
        courseUl.appendChild(li);
    });
    
    // Credentials
    const certUl = document.getElementById("roadmap-certs-list");
    certUl.innerHTML = "";
    r.certifications.forEach(c => {
        const li = document.createElement("li");
        li.innerText = c;
        certUl.appendChild(li);
    });
    
    // Internship Guidelines
    const guideUl = document.getElementById("roadmap-internship-list");
    guideUl.innerHTML = "";
    r.internship_guidance.forEach(g => {
        const li = document.createElement("li");
        li.innerText = g;
        guideUl.appendChild(li);
    });
    
    lucide.createIcons();
}

// ========================================== //
//            AI ASSISTANT CHAT ENGINE        //
// ========================================== //
function handleChatSubmit(event) {
    event.preventDefault();
    const input = document.getElementById("chat-user-message");
    const msg = input.value.trim();
    if (!msg) return;
    
    input.value = "";
    
    // Render user message immediately
    appendChatMessage(msg, "user");
    
    // Add typing spinner
    const spinner = appendChatSpinner();
    
    fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg })
    })
    .then(res => res.json())
    .then(data => {
        spinner.remove();
        if (data.status === "success") {
            appendChatMessage(data.reply, "assistant");
        } else {
            appendChatMessage("I encountered an error analyzing that question. Please try again.", "assistant");
        }
    })
    .catch(err => {
        spinner.remove();
        appendChatMessage("Network connection interrupted.", "assistant");
    });
}

function sendPresetChat(message) {
    document.getElementById("chat-user-message").value = message;
    const form = document.getElementById("chat-input-form");
    form.dispatchEvent(new Event("submit"));
}

function appendChatMessage(text, sender) {
    const body = document.getElementById("chat-messages-body");
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${sender}-msg`;
    
    // Basic Markdown bullet lists parser to match counselor tone formatting
    let formattedText = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n\* (.*?)/g, '<br>• $1')
        .replace(/\n\s*-\s*(.*?)/g, '<br>• $1')
        .replace(/\n/g, '<br>');
        
    msgDiv.innerHTML = `
        <div class="msg-bubble">${formattedText}</div>
    `;
    body.appendChild(msgDiv);
    
    // Scroll chat window down
    body.scrollTop = body.scrollHeight;
}

function appendChatSpinner() {
    const body = document.getElementById("chat-messages-body");
    const spinner = document.createElement("div");
    spinner.className = "message assistant-msg";
    spinner.innerHTML = `
        <div class="msg-bubble">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    body.appendChild(spinner);
    body.scrollTop = body.scrollHeight;
    return spinner;
}

function restoreChatHistory() {
    fetch(`${API_BASE}/api/chat/history`)
        .then(res => res.json())
        .then(data => {
            if (data.status === "success" && data.history.length) {
                const body = document.getElementById("chat-messages-body");
                body.innerHTML = "";
                data.history.forEach(chat => {
                    appendChatMessage(chat.message, chat.sender === "user" ? "user" : "assistant");
                });
            }
        });
}

function clearChat() {
    fetch(`${API_BASE}/api/chat/clear`, { method: "POST" })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                document.getElementById("chat-messages-body").innerHTML = `
                    <div class="message assistant-msg">
                        <div class="msg-bubble">Chat memory purged. Ask me anything to begin again!</div>
                    </div>
                `;
                showToast("Chat advisor history reset.", "success");
            }
        });
}

// ========================================== //
//            ANALYTICS CHART SYSTEM          //
// ========================================== //
function loadAnalyticsDashboard() {
    fetch(`${API_BASE}/api/analytics`)
        .then(res => res.json())
        .then(data => {
            if (data.status === "success" && data.analytics) {
                const a = data.analytics;
                
                // Set text logs
                document.getElementById("analytics-ring-percentage").innerText = `${Math.round(a.study_completion)}%`;
                document.getElementById("analytics-count-interviews").innerText = a.interview_count;
                document.getElementById("analytics-count-roadmaps").innerText = a.milestone_count;
                
                // Draw Full Charts
                renderDetailedAnalyticsCharts(a.resume_history, a.skill_history);
            }
        });
}

function renderDetailedAnalyticsCharts(resumeHistory, skillHistory) {
    // 1. Resume Trend Chart
    const ctxResume = document.getElementById("chart-resume-history");
    if (ctxResume) {
        if (STATE.charts.resumeHistory) STATE.charts.resumeHistory.destroy();
        
        STATE.charts.resumeHistory = new Chart(ctxResume, {
            type: 'line',
            data: {
                labels: resumeHistory.map(r => r.date),
                datasets: [{
                    label: 'ATS Audit Grade',
                    data: resumeHistory.map(r => r.score),
                    borderColor: '#a78bfa',
                    backgroundColor: 'rgba(167, 139, 250, 0.15)',
                    tension: 0.2,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { min: 0, max: 100, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9f96b3' } },
                    x: { grid: { display: false }, ticks: { color: '#9f96b3' } }
                }
            }
        });
    }
    
    // 2. Skill Gap Radar Compare Chart
    const ctxSkill = document.getElementById("chart-skill-alignment");
    if (ctxSkill) {
        if (STATE.charts.skillAlignment) STATE.charts.skillAlignment.destroy();
        
        STATE.charts.skillAlignment = new Chart(ctxSkill, {
            type: 'bar',
            data: {
                labels: skillHistory.map(s => s.date),
                datasets: [{
                    label: 'Target Job Suitability %',
                    data: skillHistory.map(s => s.match_percentage),
                    backgroundColor: 'rgba(59, 130, 246, 0.5)',
                    borderColor: '#3b82f6',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { min: 0, max: 100, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9f96b3' } },
                    x: { grid: { display: false }, ticks: { color: '#9f96b3' } }
                }
            }
        });
    }
}

// ========================================== //
//            EXPORT SYSTEMS CONTROL          //
// ========================================== //
function exportModule(moduleName, format) {
    if (format === 'txt') {
        window.location.href = `${API_BASE}/api/export/txt/${moduleName}`;
        showToast("Downloading report file...", "info");
    } else {
        showToast("Unsupported format selected.", "warning");
    }
}

// ========================================== //
//            EVENT LISTENERS REGISTRATION    //
// ========================================== //
function setupEventListeners() {
    // Resume Dropzone configuration
    const zone = document.getElementById("resume-dropzone");
    const fileInput = document.getElementById("resume-file-input");
    const nameInd = document.getElementById("resume-file-name");
    
    zone.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", () => {
        if (fileInput.files.length) {
            nameInd.innerText = fileInput.files[0].name;
            showToast("PDF Resume Staged.", "info");
        }
    });
    
    zone.addEventListener("dragover", (e) => {
        e.preventDefault();
        zone.style.borderColor = "var(--primary)";
    });
    zone.addEventListener("dragleave", () => {
        zone.style.borderColor = "rgba(255,255,255,0.15)";
    });
    zone.addEventListener("drop", (e) => {
        e.preventDefault();
        zone.style.borderColor = "rgba(255,255,255,0.15)";
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            nameInd.innerText = fileInput.files[0].name;
            showToast("PDF Dragged & Staged.", "info");
        }
    });
    
    // Form submissions binding
    document.getElementById("resume-upload-form").addEventListener("submit", handleResumeSubmit);
    document.getElementById("skill-gap-form").addEventListener("submit", handleSkillGapSubmit);
    document.getElementById("interview-form").addEventListener("submit", handleInterviewSubmit);
    document.getElementById("study-form").addEventListener("submit", handleStudyPlannerSubmit);
    document.getElementById("roadmap-form").addEventListener("submit", handleRoadmapSubmit);
    document.getElementById("chat-input-form").addEventListener("submit", handleChatSubmit);
    document.getElementById("profile-edit-form").addEventListener("submit", saveUserProfile);
}

// Docs modals
function showDocsModal() {
    document.getElementById("docs-modal").classList.remove("hide");
}

function hideDocsModal() {
    document.getElementById("docs-modal").classList.add("hide");
}

function refreshAllData() {
    syncUserProfile();
    loadDashboardSummary();
    showToast("Application metrics synchronized from SQLite db.", "success");
}

function clearAllAppMetrics() {
    if (confirm("Are you sure you want to clear all analysis files, study schedules, and reset profiles? This resets SQLite database values.")) {
        fetch(`${API_BASE}/api/chat/clear`, { method: "POST" })
            .then(() => {
                showToast("Application data tables purged.", "success");
                window.location.reload();
            });
    }
}
