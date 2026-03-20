from pydantic import BaseModel, EmailStr, Field


class SubjectInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    priority: int = Field(..., ge=1, le=5)
    current_level: int = Field(..., ge=0, le=100)
    target_level: int = Field(..., ge=0, le=100)
    syllabus_coverage: int = Field(..., ge=0, le=100)
    mock_score: int = Field(..., ge=0, le=100)


class PlannerRequest(BaseModel):
    exam_name: str = Field(..., min_length=2, max_length=120)
    target_date: str
    weekly_hours: int = Field(..., ge=1, le=100)
    target_score: int = Field(..., ge=1, le=100)
    confidence_level: int = Field(..., ge=0, le=100)
    stress_level: int = Field(..., ge=0, le=100)
    study_style: str = Field(..., min_length=2, max_length=40)
    constraints: str = Field(default="", max_length=600)
    subjects: list[SubjectInput] = Field(default_factory=list)


class StrategyResponse(BaseModel):
    mode: str
    model: str
    summary: str
    next_steps: list[str]
    weekly_plan: list[str]
    risk_alerts: list[str]
    focus_subjects: list[str]


class AuthRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class AuthLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr


class AuthStateResponse(BaseModel):
    authenticated: bool
    user: UserResponse | None = None


class SavePlanRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=120)
    payload: PlannerRequest
    strategy: StrategyResponse


class SavedPlanSummary(BaseModel):
    id: int
    title: str
    exam_name: str
    target_date: str
    created_at: str
    summary: str


class SavedPlanDetail(BaseModel):
    id: int
    title: str
    created_at: str
    payload: PlannerRequest
    strategy: StrategyResponse
