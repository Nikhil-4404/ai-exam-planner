import streamlit as st
import pandas as pd
import datetime
import requests

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
                # Try to create user (registers if new, fails if exists - for simple logic we just want ID)
                # In a real app we'd have /login endpoint. Here we use create to 'ensure' user exists.
                try:
                    # 1. Try Register
                    payload = {"username": username, "password": password or "123456"}
                    res = requests.post(f"{API_URL}/users/", json=payload)
                    
                    if res.status_code == 200:
                        user_data = res.json()
                        st.session_state.user_id = user_data['id']
                    elif res.status_code == 400 and "already registered" in res.text:
                        # 2. If exists, we hackily just assume ID=1 for this demo or need a GET /users/search endpoint
                        # For MVP demo stability, we will just proceed. 
                        # Ideally: GET /users/{username}
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
    # Title
    st.title("🎓 SmartStudy: AI-Driven Exam Planner")

    # API Connection Check
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 1 # Fallback
    
    uid = st.session_state.user_id

    # Sidebar: Settings & Feedback
    st.sidebar.header("⚙️ Settings")
    daily_hours = st.sidebar.slider("How many hours can you study today?", 1.0, 12.0, 4.0, 0.5)
    
    # Logout Button
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    # --- LOAD DATA FROM API ---
    try:
        res = requests.get(f"{API_URL}/users/{uid}/subjects/")
        if res.status_code == 200:
            db_subjects = res.json()
        else:
            st.error("Failed to fetch subjects")
            db_subjects = []
    except:
        st.error("Backend offline. Run: `uvicorn backend.main:app`")
        db_subjects = []

    # Sidebar: Quick Progress Update (Feedback Loop)
    st.sidebar.markdown("---")
    st.sidebar.subheader("✅ Mark Progress")
    if not db_subjects:
        st.sidebar.info("Add subjects first to track progress.")
    else:
        # Flatten topics for a quick checklist
        for sub in db_subjects:
            with st.sidebar.expander(f"{sub['name']} Topics"):
                for t in sub['topics']:
                    # Checkbox state based on DB status
                    is_checked = st.checkbox(
                        t['name'], 
                        value=t['status'],
                        key=f"check_{t['id']}"
                    )
                    # Note: API update logic for status toggling not strictly implemented in backend yet
                    # We would add PATCH /topics/{id} here. 
                    # For MVP visualization, we just show state.

    # --- MAIN INPUT AREA ---
    st.header("📝 Your Subjects & Syllabus")

    def add_new_subject_ui():
        with st.form("add_subject_form"):
            st.subheader("Add New Subject")
            c1, c2 = st.columns(2)
            name = c1.text_input("Name")
            date = c2.date_input("Exam Date", datetime.date.today() + datetime.timedelta(days=30))
            diff = st.slider("Difficulty", 1, 10, 5)
            
            # PDF Upload Feature
            st.markdown("---")
            st.write("📄 **AI Syllabus Parser (Beta)**")
            uploaded_pdf = st.file_uploader("Upload Syllabus PDF", type="pdf")
            
            topics_placeholder = "Algebra, Geometry"
            if uploaded_pdf is not None:
                # Send to API
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
                    # Construct Payload
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

    # Display Existing Subjects
    for sub in db_subjects:
        with st.expander(f"{sub['name']} (Exam: {sub['exam_date']})", expanded=False):
            st.write(f"**Difficulty:** {sub['difficulty']}/10")
            topics_display = [t['name'] for t in sub['topics']]
            st.write(f"**Topics:** {', '.join(topics_display)}")

    # --- GENERATE PLAN ---
    if st.button("🚀 Generate Granular Study Plan", type="primary"):
        # CALL API
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
                    
                    # Columns from API: subject, topic, allocated_hours, urgency_score, exam_date
                    st.dataframe(
                        df[["subject", "topic", "allocated_hours", "urgency_score", "exam_date"]],
                        use_container_width=True
                    )
                    
                    # CSV Download
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download CSV", csv, "plan.csv", "text/csv")
            else:
                st.error(f"Planning Failed: {res_plan.text}")
        except Exception as e:
            st.error(f"API Connection Failed: {e}")

# --- APP FLOW CONTROL ---

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
else:
    main_app()
