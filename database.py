import sqlite3
import datetime

DB_NAME = "study_planner.db"

def init_db():
    """Initialize the database with tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Table: Subjects
    c.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            difficulty INTEGER,
            exam_date TEXT
        )
    ''')
    
    # Table: Topics
    # Status: 0 = Pending, 1 = Done
    c.execute('''
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            name TEXT NOT NULL,
            status INTEGER DEFAULT 0,
            FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

def add_subject(name, difficulty, exam_date):
    """Add a subject and return its ID."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO subjects (name, difficulty, exam_date) VALUES (?, ?, ?)", 
              (name, difficulty, exam_date))
    subject_id = c.lastrowid
    conn.commit()
    conn.close()
    return subject_id

def add_topic(subject_id, name):
    """Add a topic to a specific subject."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO topics (subject_id, name, status) VALUES (?, ?, 0)", 
              (subject_id, name))
    conn.commit()
    conn.close()

def get_all_data():
    """
    Fetch all subjects and their topics.
    Returns a list of dictionaries structured like the session state.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Get Subjects
    c.execute("SELECT id, name, difficulty, exam_date FROM subjects")
    subjects_rows = c.fetchall()
    
    data = []
    for s_row in subjects_rows:
        s_id, s_name, s_diff, s_date = s_row
        
        # Get Topics for this subject
        c.execute("SELECT id, name, status FROM topics WHERE subject_id = ?", (s_id,))
        topic_rows = c.fetchall()
        
        topics = []
        for t_row in topic_rows:
            topics.append({
                "id": t_row[0],
                "name": t_row[1],
                "status": t_row[2] # 0 or 1
            })
            
        data.append({
            "id": s_id,
            "name": s_name,
            "difficulty": s_diff,
            "exam_date": datetime.datetime.strptime(s_date, "%Y-%m-%d").date(),
            "topics": topics
        })
        
    conn.close()
    return data

def delete_subject(subject_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
    c.execute("DELETE FROM topics WHERE subject_id = ?", (subject_id,)) # Manually cascade if needed
    conn.commit()
    conn.close()

def toggle_topic_status(topic_id, new_status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE topics SET status = ? WHERE id = ?", (new_status, topic_id))
    conn.commit()
    conn.close()
