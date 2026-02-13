from typing import List, Optional
from pydantic import BaseModel
from datetime import date

class TopicBase(BaseModel):
    name: str
    weightage: float = 1.0
    status: bool = False

class TopicCreate(TopicBase):
    pass

class Topic(TopicBase):
    id: int
    subject_id: int
    class Config:
        from_attributes = True

class SubjectBase(BaseModel):
    name: str
    difficulty: int
    exam_date: date

class SubjectCreate(SubjectBase):
    topics: List[TopicCreate] = []

class Subject(SubjectBase):
    id: int
    user_id: int
    topics: List[Topic] = []
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    subjects: List[Subject] = []
    class Config:
        from_attributes = True

class ScheduleRequest(BaseModel):
    daily_hours: float

class ScheduleItem(BaseModel):
    subject: str
    topic: str
    topic_id: int  # Used for completing tasks
    allocated_hours: float
    urgency_score: float
    exam_date: date
    reason: str = "" # AI Explanation

class SyllabusResponse(BaseModel):
    success: bool
    extracted_text: str
    message: str = ""
