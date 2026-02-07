# AI-Based Exam Preparation Strategy Planner - Project Blueprint

## 1. Refined Project Definition

### Project Title
**SmartStudy: AI-Driven Personalized Exam Preparation & Strategy Planner**
*(Evolving into a Full-Stack Adaptive Learning System)*

### Problem Statement
Academic students face significant challenges in managing their study schedules due to a lack of personalized planning tools. Generic timetables fail to account for individual learning speeds, varying subject grasp, and specific syllabus requirements, resulting in suboptimal exam performance and increased anxiety.

### Objectives
1.  **To develop an intelligent system** that parses syllabi (PDFs) and assesses student difficulty levels using Natural Language Processing (NLP/RAG).
2.  **To implement an adaptive scheduling algorithm** that prioritizes subjects based on exam proximity, difficulty, and weightage, moving beyond static dates.
3.  **To integrate Spaced Repetition (SRS)** principles into the study plan to ensure long-term retention.
4.  To provide a mobile-responsive dashboard for tracking progress and adherence to the plan.

### Scope and Limitations
*   **Scope:** Syllabus parsing from PDFs, adaptive re-scheduling, tracking completions, and multi-platform access.
*   **Limitations:** The initial "AI" is heuristic/rule-based, evolving into a Retrieval-Augmented Generation (RAG) model for syllabus parsing.

---

## 2. System Features and Functional Requirements

### Core Modules
1.  **Student Profiler:**
    *   Input: Exams config (Name, Date).
    *   Input: **Detailed Syllabus Parsing** (Uploaded PDF -> List of Topics via LLM).
    *   Input: Topic Metadata (Weightage, Difficulty, SRS Status).
    *   Input: Constraints (Daily study hours, focused time slots).
2.  **Strategy Engine (The "Brain"):**
    *   Calculates "Study Urgency Score" using **Adaptive Logic**.
    *   Prioritizes high-weightage topics that are incomplete.
    *   Implements **Spaced Repetition** (Review intervals: 1d, 3d, 7d).
    *   Allocates hours based on weighted priorities.
3.  **Plan Generator:**
    *   Output: **Granular Daily Schedule** (e.g., "Study Physics: Thermodynamics - 2 hours").
    *   Output: Dynamic adjustment based on yesterday's completion.
4.  **Dashboard & Tracker:**
    *   Mark specific topics as "Done".
    *   Visual progress bars per subject and per module.
    *   Analytics: "Projected Syllabus Completion Date".

---

## 3. System Design and Architecture

### Architecture Pattern
**Current Phase: Python Monolith (Streamlit)**
**Future Phase: Full-Stack MERN + Python Service**

We are currently building the **Python Core** (Logic & AI) which will serve as the backend intelligence for the future Full-Stack application.

### Diagram Descriptions
*   **Data Layer:** SQLite (Current) -> MongoDB (Future).
*   **Logic Layer (Python):** `PlannerEngine` (Heuristics) -> `RAG_Agent` (Syllabus Parser).
*   **Presentation Layer:** Streamlit (Prototype) -> React.js (Production).

### Data Flow
1.  User uploads PDF Syllabus -> `Python RAG Service` extracts Topics.
2.  Topics stored in `Database`.
3.  `PlannerEngine` runs adaptive heuristics -> Generates `Schedule`.
4.  Frontend renders interactive Schedule.

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
*   **Backend/AI Logic:** Python 3.9+ (LangChain/LlamaIndex for RAG).
*   **Prototype UI:** **Streamlit** (Current).
*   **Production UI:** **React.js** (Future Roadmap).
*   **Database:** **SQLite** (Current) -> **MongoDB** (Future).
*   **Data Manipulation:** **Pandas** (For handling time-series data and tables).
*   **Math/Logic:** **NumPy** (For weighted calculations).

### Implementation Phases

**Phase 1: The Core Logic (Completed)**
*   Define `Subject`, `Exam`, and `Topic` classes.
*   Implement urgency calculation.

**Phase 2: The Interface (Completed)**
*   Streamlit UI with Login.
*   Granular Topic Input (Manual).

**Phase 3: Persistence (Completed)**
*   SQLite Database Integration.
*   Progress Tracking (Checkboxes).

**Phase 4: Advanced AI Features (New Target)**
*   **Syllabus Parsing:** Upload PDF -> Auto-populate topics.
*   **Adaptive Scheduling:** Adjust plan based on "Missed Tasks".
*   **Migration:** Prepare backend API for React frontend.

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
