from __future__ import annotations

import json
import os
from datetime import date
from typing import Any

from app.models import PlannerRequest, StrategyResponse

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore[assignment]


SYSTEM_PROMPT = """You are an expert academic strategy coach.
Generate concise, practical study guidance in JSON.
Be specific, time-aware, and realistic.
Output JSON with keys:
summary, next_steps, weekly_plan, risk_alerts, focus_subjects.
Each list should contain 3 to 5 short string items.
"""


def _subject_priority(subject: Any) -> float:
    gap = max(subject.target_level - subject.current_level, 0)
    return (
        gap * 0.42
        + subject.priority * 10
        + (100 - subject.syllabus_coverage) * 0.26
        + (100 - subject.mock_score) * 0.22
    )


def _safe_target_date(target_date: str) -> date | None:
    try:
        return date.fromisoformat(target_date)
    except ValueError:
        return None


def _exam_window(payload: PlannerRequest) -> tuple[int | None, str]:
    target = _safe_target_date(payload.target_date)
    if target is None:
        return None, "Preparation"

    days_left = (target - date.today()).days
    if days_left <= 30:
        return days_left, "Final revision"
    if days_left <= 75:
        return days_left, "Acceleration"
    if days_left <= 150:
        return days_left, "Build-up"
    return days_left, "Foundation"


def _subject_readiness(subject: Any) -> int:
    readiness = (
        subject.current_level * 0.42
        + subject.mock_score * 0.34
        + subject.syllabus_coverage * 0.24
    )
    return round(min(100, max(0, readiness)))


def _focus_mode(payload: PlannerRequest, subject: Any) -> str:
    if payload.study_style == "Concept-first" or subject.syllabus_coverage < 45:
        return "concept rebuild"
    if payload.study_style == "Practice-heavy" or subject.mock_score < 55:
        return "timed drilling"
    return "mixed revision"


def _allocate_hours(total_hours: int, ranked_subjects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not ranked_subjects:
        return []

    total_weight = sum(subject["pressure"] for subject in ranked_subjects) or 1
    remaining = total_hours
    allocated: list[dict[str, Any]] = []

    for index, subject in enumerate(ranked_subjects):
        if index == len(ranked_subjects) - 1:
            hours = max(1, remaining)
        else:
            proportional = round((subject["pressure"] / total_weight) * total_hours)
            hours = max(1, proportional)
            remaining -= hours

        allocated.append({**subject, "hours": hours})

    return allocated


def _build_ranked_subjects(payload: PlannerRequest) -> list[dict[str, Any]]:
    ranked = []
    for subject in payload.subjects:
        gap = max(subject.target_level - subject.current_level, 0)
        pressure = _subject_priority(subject)
        readiness = _subject_readiness(subject)
        ranked.append(
            {
                "name": subject.name,
                "priority": subject.priority,
                "coverage": subject.syllabus_coverage,
                "mock_score": subject.mock_score,
                "current_level": subject.current_level,
                "target_level": subject.target_level,
                "gap": gap,
                "pressure": pressure,
                "readiness": readiness,
                "mode": _focus_mode(payload, subject),
            }
        )
    ranked.sort(key=lambda entry: entry["pressure"], reverse=True)
    return _allocate_hours(payload.weekly_hours, ranked)


def _weekly_micro_plan(
    payload: PlannerRequest,
    ranked_subjects: list[dict[str, Any]],
    phase: str,
    days_left: int | None,
) -> list[str]:
    if not ranked_subjects:
        return [
            "Week 1: add your subjects with coverage, mock score, and target level so the planner can build a real execution roadmap.",
            "Week 2: split available study time into concept work, timed practice, and revision loops.",
            "Week 3: introduce one mock plus one full review session to measure whether the plan is working.",
        ]

    weeks_visible = 2 if days_left is not None and days_left <= 21 else 3 if days_left is not None and days_left <= 60 else 4
    primary = ranked_subjects[0]
    secondary = ranked_subjects[1] if len(ranked_subjects) > 1 else None
    tertiary = ranked_subjects[2] if len(ranked_subjects) > 2 else None

    plan: list[str] = []
    for week in range(1, weeks_visible + 1):
        if phase == "Final revision":
            line = (
                f"Week {week}: run {primary['name']} recall + mock correction for {max(2, primary['hours'] - 1)}h, "
                f"use {secondary['name'] if secondary else 'a secondary subject'} for short timed sets, "
                "and keep the final block for error-log revision and formula/fact compression."
            )
        elif phase == "Acceleration":
            line = (
                f"Week {week}: push {primary['name']} for {primary['hours']}h with {primary['mode']}, "
                f"give {secondary['name'] if secondary else 'your next subject'} "
                f"{secondary['hours'] if secondary else max(2, payload.weekly_hours // 4)}h for timed practice, "
                f"and use {tertiary['name'] if tertiary else 'remaining time'} for revision recovery and backlog cleanup."
            )
        elif phase == "Build-up":
            line = (
                f"Week {week}: finish one major block in {primary['name']} ({primary['hours']}h), "
                f"stabilize {secondary['name'] if secondary else 'your second subject'} with "
                f"{secondary['hours'] if secondary else max(2, payload.weekly_hours // 4)}h, "
                "and close the week with one mock plus a full review session."
            )
        else:
            line = (
                f"Week {week}: build core understanding in {primary['name']} for {primary['hours']}h, "
                f"support it with {secondary['name'] if secondary else 'one complementary subject'}, "
                "and reserve one shorter session for revision notes and recall drills."
            )
        plan.append(line)

    return plan


def build_fallback_strategy(payload: PlannerRequest) -> StrategyResponse:
    ranked_subjects = _build_ranked_subjects(payload)
    top_subjects = [subject["name"] for subject in ranked_subjects[:3]]
    avg_readiness = (
        round(sum(subject["readiness"] for subject in ranked_subjects) / len(ranked_subjects))
        if ranked_subjects
        else max(35, payload.confidence_level)
    )
    days_left, phase = _exam_window(payload)
    revision_hours = max(1, round(payload.weekly_hours * (0.22 if phase == "Foundation" else 0.3 if phase == "Acceleration" else 0.38)))
    mock_hours = max(2, round(payload.weekly_hours * (0.2 if phase == "Foundation" else 0.28 if phase == "Acceleration" else 0.34)))
    deep_work_hours = max(2, payload.weekly_hours - revision_hours - mock_hours)
    micro_plan = _weekly_micro_plan(payload, ranked_subjects, phase, days_left)

    summary = (
        f"{payload.exam_name} is currently in the {phase.lower()} phase with "
        f"{f'{days_left} days left' if days_left is not None else 'an unspecified exam timeline'}. "
        f"The fallback strategy estimates readiness at {avg_readiness}% against a target of "
        f"{payload.target_score}%. Use {payload.weekly_hours} weekly hours to push "
        f"{top_subjects[0] if top_subjects else 'your weakest subject'} first while keeping "
        f"stress at {payload.stress_level}% under control."
    )

    if ranked_subjects:
        primary = ranked_subjects[0]
        secondary = ranked_subjects[1] if len(ranked_subjects) > 1 else None
        next_steps = [
            f"Start the next study cycle with {primary['name']} for {primary['hours']}h/week, focused on {primary['mode']} and closing a {primary['gap']} point gap.",
            (
                f"Use your second block on {secondary['name']} for {secondary['hours']}h/week and convert every mock mistake into a short revision note."
                if secondary
                else "Add one supporting subject and pair it with daily recall sessions so the planner can build a stronger sequence."
            ),
            f"Run at least {1 if payload.weekly_hours < 14 else 2} timed test blocks this week and review errors within 24 hours.",
            "End each day with a 15-minute active recall pass from formulas, facts, or error logs instead of passive rereading.",
        ]
    else:
        next_steps = [
            "Add your core subjects with current level, target level, coverage, and mock score so the fallback engine can rank them properly.",
            "Block your weekly hours into deep work, mock review, and revision instead of keeping study time unstructured.",
            "Use one daily recall block and one weekly timed test to make progress measurable.",
        ]

    weekly_plan = [
        f"Deep work block: spend {deep_work_hours}h/week on concept completion and targeted chapter repair, led by {top_subjects[0] if top_subjects else 'your top subject'}.",
        f"Mock and analysis block: spend {mock_hours}h/week on timed solving, post-test diagnosis, and pattern tracking.",
        f"Revision block: spend {revision_hours}h/week on flash review, spaced repetition, and previously missed questions.",
    ] + micro_plan

    risk_alerts = []
    if days_left is not None and days_left < 21 and avg_readiness < payload.target_score - 10:
        risk_alerts.append("The exam is close and readiness is still trailing the target. Shift from broad learning to high-yield revision and test correction.")
    if payload.stress_level >= 70:
        risk_alerts.append("Stress is high. Keep one lighter evening and one no-mock recovery block each week.")
    if payload.weekly_hours < 12:
        risk_alerts.append("Available study time is tight. Protect at least one uninterrupted long session on weekends.")
    if avg_readiness < payload.target_score - 15:
        risk_alerts.append("Your current performance indicators are significantly below the target score. Favor practice and analysis over collecting more content.")
    if ranked_subjects and ranked_subjects[0]["coverage"] < 40:
        risk_alerts.append(f"{ranked_subjects[0]['name']} has low coverage. Finish the core syllabus before increasing mock frequency.")
    if payload.confidence_level - avg_readiness > 18:
        risk_alerts.append("Confidence is ahead of measured readiness. Use mocks and error logs to calibrate the plan more honestly.")
    if not risk_alerts:
        risk_alerts.append("Current workload is manageable. Consistency, mock review, and short revision loops should stay non-negotiable.")

    if payload.constraints.strip():
        risk_alerts.append(f"Plan around this constraint: {payload.constraints.strip()}")

    if not top_subjects:
        top_subjects = ["Add subjects to unlock sharper AI prioritization."]

    return StrategyResponse(
        mode="fallback",
        model="heuristic-engine-v2",
        summary=summary,
        next_steps=next_steps[:5],
        weekly_plan=weekly_plan[:5],
        risk_alerts=risk_alerts[:5],
        focus_subjects=top_subjects,
    )


def _build_user_prompt(payload: PlannerRequest) -> str:
    subject_lines = [
        (
            f"- {subject.name}: priority {subject.priority}/5, current {subject.current_level}%, "
            f"target {subject.target_level}%, coverage {subject.syllabus_coverage}%, "
            f"mock score {subject.mock_score}%"
        )
        for subject in payload.subjects
    ]
    return "\n".join(
        [
            f"Exam: {payload.exam_name}",
            f"Target date: {payload.target_date}",
            f"Weekly hours: {payload.weekly_hours}",
            f"Target score: {payload.target_score}%",
            f"Confidence level: {payload.confidence_level}%",
            f"Stress level: {payload.stress_level}%",
            f"Study style: {payload.study_style}",
            f"Constraints: {payload.constraints or 'None'}",
            "Subjects:",
            *subject_lines,
        ]
    )


def generate_ai_strategy(payload: PlannerRequest) -> StrategyResponse:
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini") # ensure a valid model like 4o is used as default

    if not api_key or OpenAI is None:
        return build_fallback_strategy(payload)

    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(payload)}
            ],
            temperature=0.7,
        )
        raw_output = response.choices[0].message.content.strip()
    except Exception as e:
        # Fallback if OpenAI call fully fails
        print(f"OpenAI API failed: {e}")
        raw_output = ""

    if not raw_output:
        return build_fallback_strategy(payload)

    try:
        # Remove any Markdown JSON wrappings that might get attached
        clean_json_str = raw_output
        if clean_json_str.startswith("```json"):
            clean_json_str = clean_json_str[7:]
            if clean_json_str.endswith("```"):
                clean_json_str = clean_json_str[:-3]
        clean_json_str = clean_json_str.strip()

        parsed = json.loads(clean_json_str)
    except json.JSONDecodeError:
        return StrategyResponse(
            mode="ai",
            model=model,
            summary=raw_output,
            next_steps=["Review the generated summary and refine the inputs for more structure."],
            weekly_plan=["Run the request again after adding fuller subject data."],
            risk_alerts=["The model returned unstructured text, so the planner used a minimal fallback wrapper."],
            focus_subjects=[subject.name for subject in payload.subjects[:3]] or ["Add subjects for prioritization."],
        )

    return StrategyResponse(
        mode="ai",
        model=model,
        summary=str(parsed.get("summary", "")).strip() or build_fallback_strategy(payload).summary,
        next_steps=[str(item) for item in parsed.get("next_steps", [])][:5] or build_fallback_strategy(payload).next_steps,
        weekly_plan=[str(item) for item in parsed.get("weekly_plan", [])][:5] or build_fallback_strategy(payload).weekly_plan,
        risk_alerts=[str(item) for item in parsed.get("risk_alerts", [])][:5] or build_fallback_strategy(payload).risk_alerts,
        focus_subjects=[str(item) for item in parsed.get("focus_subjects", [])][:5] or build_fallback_strategy(payload).focus_subjects,
    )
