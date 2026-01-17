import streamlit as st
import pandas as pd
import datetime
from prototype import Subject, get_study_plan_data

# Page Configuration
st.set_page_config(
    page_title="SmartStudy Planner",
    page_icon="📚",
    layout="wide"
)

# Title and Intro
st.title("🎓 SmartStudy: AI-Driven Exam Planner")
st.markdown("""
Welcome to your personalized exam strategy tool. 
Enter your subjects and constraints below, and we'll generate the optimal study plan for today.
""")

# Sidebar: Global Constraints
st.sidebar.header("⚙️ Settings")
daily_hours = st.sidebar.slider("How many hours can you study today?", 1.0, 12.0, 4.0, 0.5)

# Session State for Subjects
if 'subjects' not in st.session_state:
    st.session_state.subjects = [
        # Default entry
        {"name": "Math", "difficulty": 5, "chapters_total": 10, "chapters_done": 2, "exam_date": datetime.date.today() + datetime.timedelta(days=30)}
    ]

def add_subject():
    st.session_state.subjects.append({
        "name": "New Subject", 
        "difficulty": 5, 
        "chapters_total": 10, 
        "chapters_done": 0, 
        "exam_date": datetime.date.today() + datetime.timedelta(days=30)
    })

def remove_subject(index):
    st.session_state.subjects.pop(index)

# Main Area: Subject Inputs
st.header("📝 Your Subjects")

# We use a container to render the list
for i, sub in enumerate(st.session_state.subjects):
    with st.expander(f"Subject {i+1}: {sub['name']}", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.session_state.subjects[i]['name'] = st.text_input(f"Name #{i}", sub['name'])
            st.session_state.subjects[i]['exam_date'] = st.date_input(f"Exam Date #{i}", sub['exam_date'])
        
        with col2:
            st.session_state.subjects[i]['difficulty'] = st.slider(f"Difficulty (1-10) #{i}", 0, 10, sub['difficulty'])
        
        with col3:
            st.session_state.subjects[i]['chapters_total'] = st.number_input(f"Total Chapters #{i}", 1, 100, sub['chapters_total'])
            st.session_state.subjects[i]['chapters_done'] = st.number_input(f"Chapters Done #{i}", 0, 100, sub['chapters_done'])
        
        with col4:
            st.write("Actions")
            if st.button(f"🗑️ Remove #{i}", key=f"del_{i}"):
                remove_subject(i)
                st.rerun()

if st.button("➕ Add Another Subject"):
    add_subject()
    st.rerun()

# Logic Execution
if st.button("🚀 Generate Study Plan", type="primary"):
    # Convert session state dicts to Subject objects
    subject_objects = []
    
    for s in st.session_state.subjects:
        # Pass date object directly now that prototype supports it
        obj = Subject(s['name'], s['difficulty'], s['chapters_total'], s['chapters_done'], s['exam_date'])
        subject_objects.append(obj)

    # Get Data
    plan_data = get_study_plan_data(subject_objects, daily_hours)
    
    if not plan_data:
        st.warning("No plan generated. Add subjects or check inputs.")
    else:
        # Metrics Dashboard
        st.divider()
        m1, m2, m3 = st.columns(3)
        
        # Calculate next deadline
        upcoming_exams = sorted([s for s in subject_objects if s.days_remaining < 30], key=lambda x: x.days_remaining)
        next_exam = upcoming_exams[0].name if upcoming_exams else "None"
        days_to_next = upcoming_exams[0].days_remaining if upcoming_exams else "-"

        m1.metric("📚 Subjects Tracked", len(subject_objects))
        m2.metric("⏳ Next Exam", next_exam, delta=f"{days_to_next} Days")
        m3.metric("🧠 Study Efficiency", f"{daily_hours} Hrs", "Target")

        st.success("Analysis Complete! Here is your strategy.")
        
        # Display as DataFrame
        df = pd.DataFrame(plan_data)
        
        # Formatting
        st.subheader("Your Schedule for Today")
        
        # Colour highlighting
        def highlight_urgency(val):
            color = 'green'
            if val > 1.5: color = '#ff4b4b' # Red
            elif val > 0.8: color = '#ffa421' # Orange
            return f'color: {color}; font-weight: bold'

        st.dataframe(
            df.style.applymap(highlight_urgency, subset=['Urgency Score'])
                    .format({"Urgency Score": "{:.2f}", "Allocated Hours": "{:.2f} hrs"}),
            use_container_width=True
        )

        # Visualization
        st.subheader("Time Allocation")
        if any(d['Allocated Hours'] > 0 for d in plan_data):
            st.bar_chart(df.set_index("Subject")['Allocated Hours'])
        else:
            st.info("No study hours needed today (Revision only or holiday).")
