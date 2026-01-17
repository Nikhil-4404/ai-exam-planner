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
        {
            "name": "Math", 
            "difficulty": 5, 
            "exam_date": datetime.date.today() + datetime.timedelta(days=30),
            "topics_str": "Algebra, Geometry, Calculus"
        }
    ]

def add_subject():
    st.session_state.subjects.append({
        "name": "New Subject", 
        "difficulty": 5, 
        "exam_date": datetime.date.today() + datetime.timedelta(days=30),
        "topics_str": ""
    })

def remove_subject(index):
    st.session_state.subjects.pop(index)

# Main Area: Subject Inputs
st.header("📝 Your Subjects & Syllabus")
st.info("Enter your syllabus topics comma-separated (e.g., 'Newton Laws, Optics, Waves').")

# We use a container to render the list
for i, sub in enumerate(st.session_state.subjects):
    with st.expander(f"Subject {i+1}: {sub['name']}", expanded=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.session_state.subjects[i]['name'] = st.text_input(f"Subject Name", sub['name'], key=f"name_{i}")
            st.session_state.subjects[i]['exam_date'] = st.date_input(f"Exam Date", sub['exam_date'], key=f"date_{i}")
            st.session_state.subjects[i]['difficulty'] = st.slider(f"Difficulty (1-10)", 0, 10, sub['difficulty'], key=f"diff_{i}")
        
        with col2:
            st.session_state.subjects[i]['topics_str'] = st.text_area(
                f"Topics (Comma Separated)", 
                sub['topics_str'], 
                height=150,
                key=f"topics_{i}",
                placeholder="Chapter 1, Chapter 2, Chapter 3..."
            )
            
        if st.button(f"🗑️ Remove Subject", key=f"del_{i}"):
            remove_subject(i)
            st.rerun()

if st.button("➕ Add Another Subject"):
    add_subject()
    st.rerun()

# Logic Execution
if st.button("🚀 Generate Granular Study Plan", type="primary"):
    from prototype import Topic # Import locally to avoid stale cache issues
    
    # Convert session state dicts to Subject objects
    subject_objects = []
    all_topics_count = 0
    
    for s in st.session_state.subjects:
        # Parse Topics
        raw_topics = [t.strip() for t in s['topics_str'].split(',') if t.strip()]
        topic_objects = [Topic(name=t_name) for t_name in raw_topics]
        all_topics_count += len(topic_objects)
        
        # Create Subject with Topics
        obj = Subject(s['name'], s['difficulty'], s['exam_date'], topics=topic_objects)
        subject_objects.append(obj)

    # Get Data
    plan_data = get_study_plan_data(subject_objects, daily_hours)
    
    if not plan_data:
        st.warning("No plan generated. Please add subjects and topics.")
    else:
        # Metrics Dashboard
        st.divider()
        m1, m2, m3 = st.columns(3)
        
        m1.metric("📚 Topics Identified", all_topics_count)
        m2.metric("🎯 Tasks Scheduled", len(plan_data))
        m3.metric("🧠 Total Study Time", f"{daily_hours} Hrs")

        st.success("Strategy Generated! Focus on these specific topics today:")
        
        # Display as DataFrame
        df = pd.DataFrame(plan_data)
        
        # Formatting
        st.subheader("Today's Granular Schedule")
        
        # Grid config
        st.dataframe(
            df[["Subject", "Topic", "Allocated Hours", "Urgency Score", "Exam Date"]],
            use_container_width=True
        )

        # Visualization: Time per Subject
        st.subheader("Allocation Analysis")
        chart_data = df.groupby("Subject")["Allocated Hours"].sum()
        st.bar_chart(chart_data)
