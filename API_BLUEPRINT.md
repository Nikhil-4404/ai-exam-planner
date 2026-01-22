# Task 3.1: FastAPI Backend Architecture (API Blueprint)

**Role:** Backend Architect  
**Date:** January 2026  
**Project:** SmartStudy AI Planner (Migration to Microservices/API)

---

## 1. System Overview

We are migrating from a monolithic Streamlit app to a **Headless Architecture**.
*   **Backend:** FastAPI (Python) - chosen for native async support and high performance with AI libraries.
*   **Database:** MongoDB (transitioning from SQLite for flexible JSON document storage of nested topics).
*   **AI Service:** LangChain/LlamaIndex (integrated directly into endpoints).

---

## 2. API Endpoints Design

### 🔐 Authentication Module (Future Auth0/JWT)
*   **POST** `/api/v1/auth/login`
    *   *Input:* `{"username": "...", "password": "..."}`
    *   *Output:* `{"token": "ey...", "user_id": "123"}`

### 📚 Syllabus & Subject Management
This module handles the core data ingestion.

*   **POST** `/api/v1/syllabus/upload` **(The RAG Ingestion)**
    *   *Description:* Accepts a PDF file, runs OCR/Text Extraction, and returns a structured JSON list of topics using an LLM.
    *   *Input:* `multipart/form-data` (file)
    *   *Output:* 
        ```json
        {
          "detected_subjects": ["Physics"],
          "topics": [
              {"name": "Thermodynamics", "confidence": 0.95},
              {"name": "Kinematics", "confidence": 0.88}
          ]
        }
        ```

*   **POST** `/api/v1/subjects`
    *   *Description:* Save a confirmed subject and its verified topics to the DB.
    *   *Input:* `SubjectSchema` (Drafted below)

*   **GET** `/api/v1/subjects`
    *   *Description:* Fetch all subjects for the dashboard.

### 🧠 Scheduling Engine (The "Brain")
This is where `prototype.py` logic moves.

*   **POST** `/api/v1/schedule/generate`
    *   *Description:* Runs the Weighted Priority Algorithm.
    *   *Input:* 
        ```json
        {
          "daily_hours": 4.0,
          "include_completed": false
        }
        ```
    *   *Output:* 
        ```json
        [
          {
            "subject": "Physics", 
            "topic": "Thermodynamics", 
            "duration": 2.0, 
            "priority_score": 1.45,
            "reason": "High Difficulty & Exam in 5 days"
          }
        ]
        ```

*   **POST** `/api/v1/schedule/reschedule`
    *   *Description:* Triggered when a user misses a day. Recalculates remaining urgency.

### ✅ Progress Tracking

*   **PATCH** `/api/v1/topics/{topic_id}/status`
    *   *Input:* `{"status": "Done"}`
    *   *Effect:* Updates DB and triggers a silent re-score of remaining items.

---

## 3. Data Schemas (Pydantic Models)

To ensure type safety between Frontend (React) and Backend (FastAPI).

```python
class TopicBase(BaseModel):
    name: str
    weightage: float = 1.0
    status: Literal['Pending', 'Done'] = 'Pending'

class SubjectCreate(BaseModel):
    name: str
    exam_date: date
    difficulty: int = Field(..., ge=1, le=10)
    topics: List[TopicBase]

class ScheduleItem(BaseModel):
    topic_id: str
    subject_name: str
    allocated_minutes: int
    urgency_label: str # "Critical", "High", "Normal"
```

---

## 4. Technical Risks & Mitigation

1.  **Risk:** PDF Extraction is messy (garbage characters).
    *   *Mitigation:* Implement a "Review Stage" in the API response where the user must approve the parsed topics before saving.
2.  **Risk:** LLM Latency (Parsing takes 10s+).
    *   *Mitigation:* Make the upload endpoint `async` and use WebSockets or Polling for the status.
