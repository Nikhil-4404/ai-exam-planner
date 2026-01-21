import streamlit as st
import pandas as pd
import datetime
import pypdf
from prototype import Subject, Topic, get_study_plan_data
import database as db

# Initialize DB
db.init_db()

# Page Configuration
st.set_page_config(
    page_title="SmartStudy Planner",
    page_icon="📚",
    layout="wide"
)

def extract_text_from_pdf(uploaded_file):
    """
    Simulate RAG/NLP Parsing: 
    Extracts text and splits it into potential topics using heuristics.
    In Phase 4, this will be replaced by an LLM call.
    """
    try:
        reader = pypdf.PdfReader(uploaded_file)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
        
        # Simple heuristic: Split by newlines, filter short lines
        # This mimics finding "Topic 1: ..." lines
        lines = [line.strip() for line in full_text.split('\n') if len(line.strip()) > 5]
        
        # Return top 20 lines as "detected topics" for now
        # Ideally, an LLM would summarize this.
        return ", ".join(lines[:20]) 
    except Exception as e:
        return f"Error parsing PDF: {e}"

def login_page():
    """Simple Login Page logic"""
    st.title("🔐 Login to SmartStudy")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if username: 
                st.session_state.logged_in = True
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Please enter a username.")

def main_app():
    """The Main Application Logic"""
    # Title
    st.title("🎓 SmartStudy: AI-Driven Exam Planner")

    # Sidebar: Settings & Feedback
    st.sidebar.header("⚙️ Settings")
    daily_hours = st.sidebar.slider("How many hours can you study today?", 1.0, 12.0, 4.0, 0.5)
    
    # Logout Button
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    # --- LOAD DATA FROM DB ---
    db_subjects = db.get_all_data()

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
                        value=(t['status'] == 1),
                        key=f"check_{t['id']}"
                    )
                    # If changed, update DB immediately
                    if is_checked != (t['status'] == 1):
                        new_status = 1 if is_checked else 0
                        db.toggle_topic_status(t['id'], new_status)
                        st.rerun()

    # --- MAIN INPUT AREA ---
    st.header("📝 Your Subjects & Syllabus")

    def add_new_subject_ui():
        with st.form("add_subject_form"):
            st.subheader("Add New Subject")
            c1, c2 = st.columns(2)
            name = c1.text_input("Name")
            date = c2.date_input("Exam Date", datetime.date.today() + datetime.timedelta(days=30))
            diff = st.slider("Difficulty", 1, 10, 5)
            
            # PDF Upload Feature (Phase 4 Prototype)
            st.markdown("---")
            st.write("📄 **AI Syllabus Parser (Beta)**")
            uploaded_pdf = st.file_uploader("Upload Syllabus PDF", type="pdf")
            
            topics_placeholder = "Algebra, Geometry"
            if uploaded_pdf is not None:
                extracted_topics = extract_text_from_pdf(uploaded_pdf)
                topics_placeholder = extracted_topics
                st.info("✅ PDF Parsed! Review the extracted topics below.")
            
            # If PDF uploaded, we want to auto-fill this area
            # Streamlit workaround: we can't programmatically change the 'value' of a text_area inside a form easily 
            # without session state tricks, but for now we display the extracted text as a suggestion to copy-paste 
            # OR we just rely on the user to see it.
            # BETTER UX: Show the extracted text in a code block if `uploaded_pdf` exists, and ask user to paste it.
            
            if uploaded_pdf:
                st.text_area("Extracted Text (Copy & Paste below if correct)", value=topics_placeholder, height=100)
                topics_str = st.text_area("Final Topics List (comma separated)", value="", placeholder="Paste topics here...")
            else:
                topics_str = st.text_area("Topics (comma separated)", placeholder="Algebra, Geometry")
            
            if st.form_submit_button("Save Subject"):
                if name:
                    s_id = db.add_subject(name, diff, date.strftime("%Y-%m-%d"))
                    # Add topics
                    raw_topics = [t.strip() for t in topics_str.split(',') if t.strip()]
                    if not raw_topics and uploaded_pdf:
                         # Fallback if user submitted without pasting, maybe use the placeholder?
                         # For now, let's just warn them
                         st.warning("Please verify and paste the topics into the text area!")
                         return

                    for t in raw_topics:
                        db.add_topic(s_id, t)
                    st.success(f"Added {name}!")
                    st.rerun()
                else:
                    st.error("Name is required")

    with st.expander("➕ Add New Subject", expanded=False):
        add_new_subject_ui()

    # Display Existing Subjects (ReadOnly View in Expander)
    for sub in db_subjects:
        with st.expander(f"{sub['name']} (Exam: {sub['exam_date']})", expanded=False):
            st.write(f"**Difficulty:** {sub['difficulty']}/10")
            st.write(f"**Topics:** {', '.join([t['name'] for t in sub['topics']])}")
            if st.button(f"Delete {sub['name']}", key=f"del_{sub['id']}"):
                db.delete_subject(sub['id'])
                st.rerun()

    # --- GENERATE PLAN ---
    if st.button("🚀 Generate Granular Study Plan", type="primary"):
        # Convert DB dictionaries to Object Model
        subject_objects = []
        
        for s in db_subjects:
            # Create Topic Objects
            topic_objs = []
            for t in s['topics']:
                topic_objs.append(Topic(
                    name=t['name'], 
                    id=t['id'], 
                    is_completed=(t['status'] == 1)
                ))
                
            # Create Subject Object
            obj = Subject(s['name'], s['difficulty'], s['exam_date'], topics=topic_objs, id=s['id'])
            subject_objects.append(obj)

        # Get Data
        plan_data = get_study_plan_data(subject_objects, daily_hours)
        
        if not plan_data:
            st.warning("No pending topics found! Either add subjects or mark tasks as Pending.")
        else:
            # Metrics Dashboard
            st.divider()
            st.success("Strategy Generated!")
            
            # Display as DataFrame
            df = pd.DataFrame(plan_data)
            
            # Focus Mode
            st.markdown("### 🔥 Focus Mode")
            top_task = plan_data[0]
            st.info(f"**Top Task:** {top_task['Subject']} - {top_task['Topic']} ({top_task['Allocated Hours']} hrs)")

            # Main Table
            st.dataframe(
                df[["Subject", "Topic", "Allocated Hours", "Urgency Score", "Exam Date"]],
                use_container_width=True
            )

            # CSV Download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "plan.csv", "text/csv")

    # --- FEATURE 3: Sidebar Countdown ---
    if db_subjects:
        st.sidebar.markdown("---")
        st.sidebar.subheader("⏳ Upcoming Exams")
        # Sort subjects by date
        # db_subjects stores dates as date objects already from get_all_data
        sorted_subs = sorted(db_subjects, key=lambda x: x['exam_date'])
        for sub in sorted_subs:
            d_left = (sub['exam_date'] - datetime.date.today()).days
            if d_left < 0:
                st.sidebar.error(f"{sub['name']}: Finished!")
            elif d_left < 7:
                st.sidebar.error(f"{sub['name']}: {d_left} days left! 🚨")
            elif d_left < 30:
                st.sidebar.warning(f"{sub['name']}: {d_left} days left")
            else:
                st.sidebar.success(f"{sub['name']}: {d_left} days left")

# --- APP FLOW CONTROL ---

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
else:
    main_app()
