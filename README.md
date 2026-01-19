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

2.  **Install dependencies**:
    ```bash
    pip install streamlit pandas plotly
    ```

3.  **Run the application**:
    ```bash
    streamlit run app.py
    ```
    *This will automatically open the planner in your default web browser (http://localhost:8501).*

---

## 📖 Usage Guide

1.  **Configure Settings**: Use the sidebar to set your **Daily Study Hours** (e.g., 4 hours).
2.  **Add Subjects**:
    *   Enter the Subject Name (e.g., "History").
    *   Set the **Exam Date**.
    *   Adjust the **Difficulty Slider** (1 = Easy, 10 = Very Hard).
3.  **Input Syllabus**:
    *   In the text area, paste your topics separated by commas.
    *   *Example*: `World War 1, French Revolution, Cold War`
4.  **Generate Plan**: Click **"🚀 Generate Granular Study Plan"**.
5.  **View Results**:
    *   See a color-coded table of what strictly needs to be studied today.
    *   Check the "Urgency Score" to understand why a topic was chosen.

---

## 📁 Project Structure

*   `app.py`: The main entry point. Contains the Streamlit frontend code.
*   `prototype.py`: The logical core. Contains the `Subject`, `Topic` classes and the   `get_study_plan_data` algorithm.
*   `PROJECT_BLUEPRINT.md`: Comprehensive academic report and architectural design document.

---

## 🤝 Contributing

This is an academic project, but contributions are welcome!

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request


