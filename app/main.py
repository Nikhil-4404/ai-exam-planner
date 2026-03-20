import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.ai import generate_ai_strategy
from app.db import create_user, get_saved_plan, get_user_by_id, initialize_database, list_saved_plans, save_plan, authenticate_user
from app.models import (
    AuthLoginRequest,
    AuthRegisterRequest,
    AuthStateResponse,
    PlannerRequest,
    SavePlanRequest,
    SavedPlanDetail,
    SavedPlanSummary,
    StrategyResponse,
    UserResponse,
)
from app.pdf import build_plan_pdf


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="AI Exam Preparation Strategy Planner",
    version="2.0.0",
    description="A Python-based AI planner for exam strategy, saved plans, and PDF exports.",
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "change-this-in-production"),
    same_site="lax",
    https_only=os.getenv("APP_ENV") == "production",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
initialize_database()


def require_user(request: Request) -> UserResponse:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in first.")

    user = get_user_by_id(int(user_id))
    if user is None:
        request.session.clear()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired. Please log in again.")

    return user


@app.get("/", include_in_schema=False)
async def root(request: Request) -> RedirectResponse:
    user_id = request.session.get("user_id")
    destination = "/planner" if user_id and get_user_by_id(int(user_id)) else "/login"
    return RedirectResponse(url=destination, status_code=status.HTTP_303_SEE_OTHER)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    user_id = request.session.get("user_id")
    if user_id and get_user_by_id(int(user_id)):
        return RedirectResponse(url="/planner", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "app_name": "AI Exam Preparation Strategy Planner",
        },
    )


@app.get("/planner", response_class=HTMLResponse)
async def planner_page(request: Request) -> HTMLResponse:
    user_id = request.session.get("user_id")
    user = get_user_by_id(int(user_id)) if user_id else None
    if user is None:
        request.session.clear()
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "planner.html",
        {
            "request": request,
            "app_name": "AI Exam Preparation Strategy Planner",
            "user_name": user.name,
            "user_email": user.email,
        },
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/auth/me", response_model=AuthStateResponse)
async def auth_me(request: Request) -> AuthStateResponse:
    user_id = request.session.get("user_id")
    if not user_id:
        return AuthStateResponse(authenticated=False)

    user = get_user_by_id(int(user_id))
    if user is None:
        request.session.clear()
        return AuthStateResponse(authenticated=False)

    return AuthStateResponse(authenticated=True, user=user)


@app.post("/api/auth/register", response_model=AuthStateResponse)
async def register(request: Request, payload: AuthRegisterRequest) -> AuthStateResponse:
    try:
        user = create_user(payload.name, payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    request.session["user_id"] = user.id
    return AuthStateResponse(authenticated=True, user=user)


@app.post("/api/auth/login", response_model=AuthStateResponse)
async def login(request: Request, payload: AuthLoginRequest) -> AuthStateResponse:
    user = authenticate_user(payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    request.session["user_id"] = user.id
    return AuthStateResponse(authenticated=True, user=user)


@app.post("/api/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request) -> Response:
    request.session.clear()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/api/generate-strategy", response_model=StrategyResponse)
async def generate_strategy(payload: PlannerRequest) -> StrategyResponse:
    if payload.subjects and len(payload.subjects) > 12:
        raise HTTPException(status_code=400, detail="Please keep the subject list to 12 items or fewer.")

    return generate_ai_strategy(payload)


@app.get("/api/plans", response_model=list[SavedPlanSummary])
async def plans(request: Request) -> list[SavedPlanSummary]:
    user = require_user(request)
    return list_saved_plans(user.id)


@app.post("/api/plans", response_model=SavedPlanSummary, status_code=status.HTTP_201_CREATED)
async def create_saved_plan(request: Request, payload: SavePlanRequest) -> SavedPlanSummary:
    user = require_user(request)
    return save_plan(user.id, payload)


@app.get("/api/plans/{plan_id}", response_model=SavedPlanDetail)
async def plan_detail(request: Request, plan_id: int) -> SavedPlanDetail:
    user = require_user(request)
    plan = get_saved_plan(user.id, plan_id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found.")
    return plan


@app.get("/api/plans/{plan_id}/pdf")
async def plan_pdf(request: Request, plan_id: int) -> StreamingResponse:
    user = require_user(request)
    plan = get_saved_plan(user.id, plan_id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found.")

    pdf_bytes = build_plan_pdf(plan.title, plan.payload, plan.strategy)
    filename = f"{plan.title.lower().replace(' ', '-')}.pdf"
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/export-pdf")
async def export_pdf(payload: SavePlanRequest) -> StreamingResponse:
    pdf_bytes = build_plan_pdf(payload.title, payload.payload, payload.strategy)
    filename = f"{payload.title.lower().replace(' ', '-')}.pdf"
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
