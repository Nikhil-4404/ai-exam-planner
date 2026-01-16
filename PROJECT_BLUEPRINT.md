# AI-Based Exam Preparation Strategy Planner - Project Blueprint

## 1. Refined Project Definition

### Project Title
**SmartStudy: AI-Driven Personalized Exam Preparation & Strategy Planner**

### Problem Statement
Academic students face significant challenges in managing their study schedules due to a lack of personalized planning tools. Generic timetables fail to account for individual learning speeds, varying subject grasp, and specific syllabus requirements, resulting in suboptimal exam performance and increased anxiety.

### Objectives
1.  To develop a system that captures a student's academic profile, including strong/weak areas and available study time.
2.  To implement a rule-based AI engine that prioritizes subjects based on exam proximity, difficulty, and weightage.
3.  To generate a dynamic, day-by-day study and revision schedule.
4.  To provide a visual dashboard tracking progress and adherence to the plan.

### Scope and Limitations
*   **Scope:** Capturing user constraints, generating schedules, tracking completion, and simple progress analytics.
*   **Limitations:** The "AI" is primarily heuristic/rule-based, not a deep learning model. It relies on honest self-assessment data from the user.

---

## 2. System Features and Functional Requirements

### Core Modules
1.  **Student Profiler:**
    *   Input: Exams config (Name, Date, Syllabus count).
    *   Input: Subject metadata (Name, Difficulty rating 1-10, Competency level).
    *   Input: Constraints (Daily study hours, focused time slots).
2.  **Strategy Engine (The "Brain"):**
    *   Calculates "Study Urgency Score" for each unit.
    *   Allocates hours based on weighted priorities.
    *   Interleaves subjects to prevent burnout (spaced repetition logic).
3.  **Plan Generator:**
    *   Output: Daily schedule (What to study, when, and for how long).
    *   Output: Revision slots vs. New learning slots.
4.  **Dashboard & Tracker:**
    *   Mark topics as "Done".
    *   Visual progress bars per subject.
    *   Analytics: "Projected Syllabus Completion Date".

---

## 3. System Design and Architecture

### Architecture Pattern
**Modular Monolith with Data-Science-Centric UI**
We will use a **Streamlit** (Python) web application architecture. This allows us to build a modern, interactive web UI using *only* Python, making it perfect for an AI/Data-focused academic project.

### Diagram Descriptions
*   **Data Layer:** SQLite Database (stores User Profiles, Exam Data, Logs).
*   **Logic Layer (Python):** `PlannerEngine` class, `UserSession` manager.
*   **Presentation Layer:** Streamlit Frontend (Sidebar for inputs, Main area for dashboards and tables).

### Data Flow
1.  User enters data -> `Input Form`
2.  Data validated -> `JSON/Dict Structure`
3.  `PlannerEngine` runs heuristics -> Generates `Pandas DataFrame` (Schedule)
4.  `Streamlit` renders DataFrame -> Interactive Table/Calendar

---

## 4. Rule-Based / AI Logic Design

The core "Intelligence" comes from a **Weighted Priority Algorithm**.

### Key Heuristics
1.  **Days Remaining ($D_r$)**: $ExamDate - CurrentDate$
2.  **Content Remaining ($C_r$)**: $TotalChapters - CompletedChapters$
3.  **Difficulty Factor ($W_d$)**: User-rated difficulty (1.0 to 2.0 multiplier).
4.  **Urgency Score ($S_u$)**:
    $$ S_u = \frac{C_r \times W_d}{D_r} $$
    *(Higher score = Higher priority)*

### Algorithm Pseudocode
```python
def generate_study_plan(subjects, total_hours_per_day):
    plan = {}
    total_urgency = sum(s.urgency_score for s in subjects)
    
    for subject in subjects:
        # Allocate time proportional to urgency
        allocation_ratio = subject.urgency_score / total_urgency
        study_hours = total_hours_per_day * allocation_ratio
        
        # Rule: Minimum 30 mins, Max 3 hours per block
        study_hours = clamp(study_hours, 0.5, 3.0)
        
        plan[subject.name] = study_hours
        
    return optimize_schedule(plan) # Interleave subjects using simple logic
```

---

## 5. Python Tech Stack and Implementation Plan

### Tech Stack
*   **Language:** Python 3.9+
*   **Frontend/App Framework:** **Streamlit** (Highly recommended for "wow" factor with low code).
*   **Data Manipulation:** **Pandas** (For handling time-series data and tables).
*   **Math/Logic:** **NumPy** (For weighted calculations).
*   **Database:** **SQLite** (Built-in, zero config) or simple **JSON files** for MVP.
*   **Visualization:** **Plotly** or **Altair** (Built into Streamlit).

### Implementation Phases

**Phase 1: The Core Logic (Week 1-2)**
*   Define `Subject` and `Exam` classes.
*   Implement the `calculate_priority()` and `allocate_time()` functions.
*   Test with mock data in a Jupyter Notebook.

**Phase 2: The Interface (Week 3-4)**
*   Set up Streamlit.
*   Create forms for inputting subjects and exam dates.
*   Display the raw schedule (DataFrame) on screen.

**Phase 3: Persistence & Polish (Week 5-6)**
*   Save user data to SQLite so it persists after restart.
*   Add the "Mark as Done" feature updates the `ContentRemaining`.
*   Add progress charts (Pie chart of syllabus coverage).

---

## 6. Sample Data Models & I/O

**Input (Student Profile):**
```json
{
  "student_name": "Alex",
  "daily_hours": 6,
  "subjects": [
    {"name": "Physics", "difficulty": 8, "chapters_left": 12, "exam_date": "2023-11-10"},
    {"name": "English", "difficulty": 3, "chapters_left": 5, "exam_date": "2023-11-15"}
  ]
}
```

**Output (Generated Plan - Visualized as Table):**

| Date       | Subject | Activity       | Duration | Priority Reason |
|------------|---------|----------------|----------|-----------------|
| 2023-10-01 | Physics | Learn New Ch 1 | 2.5 Hrs  | High Weightage  |
| 2023-10-01 | English | Revision A     | 1.0 Hrs  | Easy / Cleanup  |
| 2023-10-01 | Physics | Practice Qs    | 1.0 Hrs  | Reinforcement   |

---

## 7. Evaluation, Testing, and Enhancements

### Evaluation Strategy
*   **User Acceptance Testing (UAT):** Have 3 friends use it for a week for midterms.
*   **Comparison:** Compare the "AI Plan" vs. a manually written plan. Does the AI plan cover all topics?
*   **Survey:** Usage ease, stress reduction perception.

### Enhancements (The "Extra Mile")
1.  **Prediction:** Use Scikit-Learn `LinearRegression` to predict "Expected Score" based on hours studied (requires mock training data).
2.  **Notification:** Simple toast notifications or desktop alerts for study sessions.

---

## 8. Draft Documentation Structure

**1. Abstract**
> "This project presents SmartStudy, an automated, heuristic-driven study planner designed to optimize academic revision strategies..."

**2. Introduction**
> "Traditional study planning is manual and error-prone. This system applies algorithmic resource allocation to the domain of personal time management."

**3. System Analysis**
> Includes Flowcharts and Data Flow Diagrams (DFD) Level 0/1.

**4. Implementation**
> Screenshots of the Streamlit Interface, snippets of the Priority Algorithm.

**5. Conclusion**
> "The system successfully reduces planning overhead, allowing students to focus on execution."

