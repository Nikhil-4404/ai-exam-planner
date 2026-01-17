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
    *   Input: Exams config (Name, Date).
    *   Input: **Detailed Syllabus Parsing** (List of Topics/Chapters per subject).
    *   Input: Topic Metadata (Weightage, Difficulty, Status: Pending/Done).
    *   Input: Constraints (Daily study hours, focused time slots).
2.  **Strategy Engine (The "Brain"):**
    *   Calculates "Study Urgency Score" for **each specific topic**.
    *   Prioritizes high-weightage topics that are incomplete.
    *   Allocates hours based on weighted priorities.
    *   Interleaves subjects to prevent burnout (spaced repetition logic).
3.  **Plan Generator:**
    *   Output: **Granular Daily Schedule** (e.g., "Study Physics: Thermodynamics - 2 hours").
    *   Output: Revision slots vs. New learning slots.
4.  **Dashboard & Tracker:**
    *   Mark specific topics as "Done".
    *   Visual progress bars per subject and per module.
    *   Analytics: "Projected Syllabus Completion Date".

---

## 3. System Design and Architecture

### Architecture Pattern
**Modular Monolith with Data-Science-Centric UI**
We will use a **Streamlit** (Python) web application architecture. This allows us to build a modern, interactive web UI using *only* Python, making it perfect for an AI/Data-focused academic project.

### Diagram Descriptions
*   **Data Layer:** SQLite Database (stores User Profiles, Exam Data, Logs, **Topic Registry**).
*   **Logic Layer (Python):** `PlannerEngine` class, `UserSession` manager.
*   **Presentation Layer:** Streamlit Frontend (Sidebar for inputs, Main area for dashboards and tables).

### Data Flow
1.  User inputs syllabus topics -> `Topic Registry`
2.  Data validated -> `JSON/Topic Objects`
3.  `PlannerEngine` runs heuristics on **Topic Level** -> Generates `Pandas DataFrame` (Schedule)
4.  `Streamlit` renders DataFrame -> Interactive Table/Calendar

---

## 4. Rule-Based / AI Logic Design

The core "Intelligence" comes from a **Weighted Priority Algorithm**.

### Key Heuristics
1.  **Days Remaining ($D_r$)**: $ExamDate - CurrentDate$
2.  **Topic Weight ($T_w$)**: Importance of the specific topic (High/Med/Low).
3.  **Difficulty Factor ($W_d$)**: User-rated difficulty (1.0 to 2.0 multiplier).
4.  **Urgency Score ($S_u$)**:
    $$ S_u = \frac{T_w \times W_d}{D_r} $$
    *(Higher score = Higher priority)*

### Algorithm Pseudocode
```python
def generate_study_plan(topics_list, total_hours_per_day):
    plan = {}
    # Filter only incomplete topics
    pending_topics = [t for t in topics_list if t.status != 'Done']
    
    total_urgency = sum(t.calculate_urgency() for t in pending_topics)
    
    for topic in pending_topics:
        # Allocate time proportional to topic urgency
        allocation_ratio = topic.urgency_score / total_urgency
        study_hours = total_hours_per_day * allocation_ratio
        
        # Rule: Minimum 30 mins, Max 2 hours per specific topic
        study_hours = clamp(study_hours, 0.5, 2.0)
        
        plan[topic.name] = study_hours
        
    return optimize_schedule(plan)
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
*   Define `Subject`, `Exam`, and **`Topic`** classes.
*   Implement the `calculate_priority()` and `allocate_time()` functions.
*   Test with mock data in a Jupyter Notebook.

**Phase 2: The Interface (Week 3-4)**
*   Set up Streamlit.
*   Create forms for inputting subjects, topics, and exam dates.
*   Display the raw schedule (DataFrame) on screen.

**Phase 3: Persistence & Polish (Week 5-6)**
*   **Database Integration**: Save nested topic data to SQLite.
*   **Add Topic**: UI to add list of topics to a subject.
*   **Mark as Done**: Checkbox for specific topics finishes them.

---

## 6. Sample Data Models & I/O

**Input (Student Profile - Nested):**
```json
{
  "student_name": "Alex",
  "daily_hours": 6,
  "subjects": [
    {
      "name": "Physics", 
      "exam_date": "2023-11-10",
      "topics": [
          {"name": "Thermodynamics", "difficulty": 8, "status": "Pending"},
          {"name": "Kinematics", "difficulty": 4, "status": "Done"}
      ]
    }
  ]
}
```

**Output (Generated Plan - Visualized as Table):**

| Date       | Subject | Topic          | Duration | Priority Reason |
|------------|---------|----------------|----------|-----------------|
| 2023-10-01 | Physics | Thermodynamics | 2.0 Hrs  | High Difficulty |
| 2023-10-01 | English | Poetry Rev 1   | 1.0 Hrs  | Easy / Cleanup  |

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

---
