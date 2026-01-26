import streamlit as st
import pandas as pd
import datetime
import requests
import plotly.express as px

# API CONFIG
API_URL = "http://127.0.0.1:8000"

# Page Configuration
st.set_page_config(
    page_title="SmartStudy Planner",
    page_icon="📚",
    layout="wide"
)

def login_page():
    """Simple Login Page logic communicating with API"""
    st.title("🔐 Login to SmartStudy")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if username:
                try:
                    # 1. Try Register/Login
                    payload = {"username": username, "password": password or "123456"}
                    res = requests.post(f"{API_URL}/users/", json=payload)
                    
                    if res.status_code == 200:
                        user_data = res.json()
                        st.session_state.user_id = user_data['id']
                    elif res.status_code == 400 and "already registered" in res.text:
                        st.warning("User exists! Logging in (Simulation ID: 1)") 
                        st.session_state.user_id = 1 
                    else:
                        st.error(f"Login Error: {res.text}")
                        return

                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Logged in successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not connect to Backend API: {e}")
            else:
                st.error("Please enter a username.")

def main_app():
    """The Main Application Logic"""
    st.title("🎓 SmartStudy: AI-Driven Exam Planner")

    # API Connection Check
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 1 
    
    uid = st.session_state.user_id

    # Sidebar
    st.sidebar.header("⚙️ Settings")
    daily_hours = st.sidebar.slider("How many hours can you study today?", 1.0, 12.0, 4.0, 0.5)
    
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    # Load Data
    try:
        res = requests.get(f"{API_URL}/users/{uid}/subjects/")
        if res.status_code == 200:
            db_subjects = res.json()
        else:
            st.error("Failed to fetch subjects")
            db_subjects = []
    except:
        st.error("Backend offline. Run: `python -m uvicorn backend.main:app --reload`")
        db_subjects = []

    # Sidebar Progress
    st.sidebar.markdown("---")
    st.sidebar.subheader("✅ Mark Progress")
    if not db_subjects:
        st.sidebar.info("Add subjects first to track progress.")
    else:
        for sub in db_subjects:
            with st.sidebar.expander(f"{sub['name']} Topics"):
                for t in sub['topics']:
                    st.checkbox(t['name'], value=t['status'], key=f"check_{t['id']}")

    # --- TABS ---
    tab1, tab2 = st.tabs(["📅 Study Planner", "📊 Analytics"])

    with tab1:
        st.header("📝 Your Subjects & Syllabus")

        def add_new_subject_ui():
            with st.form("add_subject_form"):
                st.subheader("Add New Subject")
                c1, c2 = st.columns(2)
                name = c1.text_input("Name")
                date = c2.date_input("Exam Date", datetime.date.today() + datetime.timedelta(days=30))
                diff = st.slider("Difficulty", 1, 10, 5)
                
                st.markdown("---")
                st.write("📄 **AI Syllabus Parser (Beta)**")
                uploaded_pdf = st.file_uploader("Upload Syllabus PDF", type="pdf")
                
                topics_placeholder = "Algebra, Geometry"
                if uploaded_pdf is not None:
                    files = {"file": (uploaded_pdf.name, uploaded_pdf.getvalue(), "application/pdf")}
                    try:
                        res_pdf = requests.post(f"{API_URL}/syllabus/parse", files=files)
                        if res_pdf.status_code == 200:
                            data = res_pdf.json()
                            if data['success']:
                                topics_placeholder = data['extracted_text']
                                st.info("✅ PDF Parsed via API!")
                            else:
                                st.error(data['message'])
                    except Exception as e:
                        st.error(f"API Error: {e}")
                
                if uploaded_pdf:
                    st.text_area("Extracted Text", value=topics_placeholder, height=100)
                    topics_str = st.text_area("Final Topics List", value="", placeholder="Paste topics here...")
                else:
                    topics_str = st.text_area("Topics (comma separated)", placeholder="Algebra, Geometry")
                
                if st.form_submit_button("Save Subject"):
                    if name:
                        raw_topics = [t.strip() for t in topics_str.split(',') if t.strip()]
                        topic_list = [{"name": t, "weightage": 1.0, "status": False} for t in raw_topics]
                        
                        payload = {
                            "name": name,
                            "difficulty": diff,
                            "exam_date": date.strftime("%Y-%m-%d"),
                            "topics": topic_list
                        }
                        try:
                            res_create = requests.post(f"{API_URL}/users/{uid}/subjects/", json=payload)
                            if res_create.status_code == 200:
                                st.success(f"Added {name}!")
                                st.rerun()
                            else:
                                st.error(f"Failed: {res_create.text}")
                        except Exception as e:
                            st.error(f"API Error: {e}")
                    else:
                        st.error("Name is required")

        with st.expander("➕ Add New Subject", expanded=False):
            add_new_subject_ui()

        # Display Subjects
        for sub in db_subjects:
            with st.expander(f"{sub['name']} (Exam: {sub['exam_date']})", expanded=False):
                st.write(f"**Difficulty:** {sub['difficulty']}/10")
                topics_display = [t['name'] for t in sub['topics']]
                st.write(f"**Topics:** {', '.join(topics_display)}")

        # Generate Plan Logic
        if st.button("🚀 Generate Granular Study Plan", type="primary"):
            payload = {"daily_hours": daily_hours}
            try:
                res_plan = requests.post(f"{API_URL}/schedule/{uid}", json=payload)
                if res_plan.status_code == 200:
                    plan_data = res_plan.json()
                    
                    if not plan_data:
                        st.warning("No pending topics found!")
                    else:
                        st.divider()
                        st.success("Strategy Generated via Backend AI!")
                        
                        df = pd.DataFrame(plan_data)
                        st.dataframe(
                            df[["subject", "topic", "allocated_hours", "urgency_score", "exam_date"]],
                            use_container_width=True
                        )
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button("📥 Download CSV", csv, "plan.csv", "text/csv")
                else:
                    st.error(f"Planning Failed: {res_plan.text}")
            except Exception as e:
                st.error(f"API Connection Failed: {e}")

    with tab2:
        st.header("📊 Progress Analytics")
        if not db_subjects:
            st.info("Add subjects to see analytics.")
        else:
            all_topics = []
            for s in db_subjects:
                for t in s['topics']:
                    all_topics.append({
                        "Subject": s['name'],
                        "Topic": t['name'],
                        "Status": "Done" if t['status'] else "Pending",
                        "Weightage": t['weightage']
                    })
            
            df_analytics = pd.DataFrame(all_topics)
            
            if not df_analytics.empty:
                c1, c2 = st.columns(2)
                
                with c1:
                    st.subheader("Completion Status")
                    status_counts = df_analytics['Status'].value_counts().reset_index()
                    status_counts.columns = ['Status', 'Count']
                    fig_pie = px.pie(status_counts, values='Count', names='Status', color='Status',
                                     color_discrete_map={'Done':'#00CC96', 'Pending':'#EF553B'})
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with c2:
                    st.subheader("Subject Load")
                    subj_counts = df_analytics['Subject'].value_counts().reset_index()
                    subj_counts.columns = ['Subject', 'Topic Count']
                    fig_bar = px.bar(subj_counts, x='Subject', y='Topic Count', color='Subject')
                    st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.warning("No topics found.")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
else:
    main_app()
