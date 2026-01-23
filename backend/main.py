from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, logic, parser
from .database import SessionLocal, engine

# Create Tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SmartStudy API")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to SmartStudy API"} # updated for test

# --- SYLLABUS PARSING ---
@app.post("/syllabus/parse", response_model=schemas.SyllabusResponse)
async def parse_syllabus(file: UploadFile = File(...)):
    """
    Uploads a PDF and returns extracted topics string.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    result_text = await parser.extract_topics_from_pdf(file)
    
    if "Error" in result_text:
        return {"success": False, "extracted_text": "", "message": result_text}
    
    return {"success": True, "extracted_text": result_text, "message": "Successfully parsed"}

# --- USERS ---
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    # In real app, hash password here
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(username=user.username, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- SUBJECTS ---
@app.post("/users/{user_id}/subjects/", response_model=schemas.Subject)
def create_subject_for_user(
    user_id: int, subject: schemas.SubjectCreate, db: Session = Depends(get_db)
):
    # 1. Create Subject
    db_subject = models.Subject(**subject.dict(exclude={'topics'}), user_id=user_id)
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    
    # 2. Create nested Topics
    for topic_data in subject.topics:
        db_topic = models.Topic(**topic_data.dict(), subject_id=db_subject.id)
        db.add(db_topic)
    
    db.commit()
    db.refresh(db_subject)
    return db_subject

@app.get("/users/{user_id}/subjects/", response_model=List[schemas.Subject])
def read_subjects(user_id: int, db: Session = Depends(get_db)):
    subjects = db.query(models.Subject).filter(models.Subject.user_id == user_id).all()
    return subjects

# --- SCHEDULING ---
@app.post("/schedule/{user_id}", response_model=List[schemas.ScheduleItem])
def generate_schedule(user_id: int, request: schemas.ScheduleRequest, db: Session = Depends(get_db)):
    subjects = db.query(models.Subject).filter(models.Subject.user_id == user_id).all()
    if not subjects:
        return []
    
    plan = logic.get_study_plan(subjects, request.daily_hours)
    return plan
