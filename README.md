# 🎓 SmartStudy: AI-Driven Exam Preparation Planner

**SmartStudy** is an intelligent, Python-based study planner designed to help students optimize their exam preparation. By analyzing exam dates, subject difficulty, and specific syllabus topics, it generates a personalized, granular daily study schedule using a weighted priority algorithm.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B)
![Status](https://img.shields.io/badge/Status-Beta-orange)

---

## 🚀 Key Features

*   **Granular Topic Planning**: Instead of generic "Study Math" blocks, get specific tasks like "Math: Calculus" or "Physics: Thermodynamics".
*   **Intelligent Urgency Scoring**: The AI calculates a priority score for every topic based on:
    *   Days remaining until the exam.
    *   Subject difficulty rating (1-10).
    *   Topic weightage.
*   **Interactive Web Interface**: Built with **Streamlit** for a modern, easy-to-use dashboard.
*   **Visual Analytics**: View your study allocation breakdown and urgency metrics instantly.

---

## 🛠️ Installation & Setup

### Prerequisites
*   Python 3.9 or higher
*   pip (Python package manager)

### Quick Start

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Nikhil-4404/ai-exam-planner.git
    cd ai-exam-planner
    ```

3.  **Install Backend Dependencies**:
    ```bash
    pip install fastapi uvicorn sqlalchemy pypdf python-multipart
    ```

4.  **Install Frontend Dependencies**:
    ```bash
    cd frontend
    npm install
    ```

5.  **Run the application (Dual-Terminal Setup)**:

    **Terminal 1: Start the Backend API**
    ```bash
    # (From the root directory)
    python -m uvicorn backend.main:app --reload
    ```
    *(The API will be live at http://127.0.0.1:8000)*

    **Terminal 2: Start the Frontend UI**
    ```bash
    # (From the root directory)
    cd frontend
    npm run dev
    ```
    *(This will open the planner in your browser at http://localhost:5173)*

---

## 📖 Usage Guide

1.  **Login/Register**: Create a username to start your session.
2.  **Configure Settings**: Use the sidebar to set your **Daily Study Hours**.
3.  **Add Subjects**:
    *   Enter Subject Name, Exam Date, and Difficulty.
    *   **PDF Upload**: Upload a syllabus PDF to automatically extract topics!
4.  **Generate Plan**: Click **"🚀 Generate Granular Study Plan"**.
5.  **View Results**: See your AI-generated schedule with urgency scores.

---

## 📁 Project Structure

*   `app.py`: The **Frontend Client** (Streamlit). Communicates with the backend API.
*   `backend/`: The **Backend Server** (FastAPI).
    *   `main.py`: API Endpoints.
    *   `models.py`: Database Models (SQLAlchemy).
    *   `logic.py`: The Core Priority Algorithm.
    *   `parser.py`: The PDF Syllabus Parser.
*   `tests/`: API Test scripts.
*   `PROJECT_BLUEPRINT.md`: Comprehensive academic report and architectural design document.

---

## 🤝 Contributing

This is an academic project, but contributions are welcome!

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request


