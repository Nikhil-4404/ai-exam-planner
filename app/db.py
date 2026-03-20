from __future__ import annotations

import hashlib
import json
import os
import secrets
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from app.models import PlannerRequest, SavePlanRequest, SavedPlanDetail, SavedPlanSummary, StrategyResponse, UserResponse


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "planner.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS saved_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                exam_name TEXT NOT NULL,
                target_date TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                strategy_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            """
        )


def _timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120_000,
    ).hex()


def create_user(name: str, email: str, password: str) -> UserResponse:
    salt = secrets.token_hex(16)
    password_hash = _hash_password(password, salt)

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO users (name, email, password_salt, password_hash, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, email.lower(), salt, password_hash, _timestamp()),
            )
            user_id = cursor.lastrowid
    except sqlite3.IntegrityError as exc:
        raise ValueError("An account with this email already exists.") from exc

    return UserResponse(id=user_id, name=name, email=email.lower())


def authenticate_user(email: str, password: str) -> UserResponse | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, name, email, password_salt, password_hash FROM users WHERE email = ?",
            (email.lower(),),
        ).fetchone()

    if row is None:
        return None

    attempted_hash = _hash_password(password, row["password_salt"])
    if attempted_hash != row["password_hash"]:
        return None

    return UserResponse(id=row["id"], name=row["name"], email=row["email"])


def get_user_by_id(user_id: int) -> UserResponse | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

    if row is None:
        return None

    return UserResponse(id=row["id"], name=row["name"], email=row["email"])


def save_plan(user_id: int, request: SavePlanRequest) -> SavedPlanSummary:
    payload_json = request.payload.model_dump_json()
    strategy_json = request.strategy.model_dump_json()
    created_at = _timestamp()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO saved_plans (
                user_id, title, exam_name, target_date, payload_json, strategy_json, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                request.title,
                request.payload.exam_name,
                request.payload.target_date,
                payload_json,
                strategy_json,
                created_at,
            ),
        )
        plan_id = cursor.lastrowid

    return SavedPlanSummary(
        id=plan_id,
        title=request.title,
        exam_name=request.payload.exam_name,
        target_date=request.payload.target_date,
        created_at=created_at,
        summary=request.strategy.summary,
    )


def list_saved_plans(user_id: int) -> list[SavedPlanSummary]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, title, exam_name, target_date, strategy_json, created_at
            FROM saved_plans
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,),
        ).fetchall()

    plans: list[SavedPlanSummary] = []
    for row in rows:
        strategy = json.loads(row["strategy_json"])
        plans.append(
            SavedPlanSummary(
                id=row["id"],
                title=row["title"],
                exam_name=row["exam_name"],
                target_date=row["target_date"],
                created_at=row["created_at"],
                summary=str(strategy.get("summary", "")),
            )
        )
    return plans


def get_saved_plan(user_id: int, plan_id: int) -> SavedPlanDetail | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, title, payload_json, strategy_json, created_at
            FROM saved_plans
            WHERE user_id = ? AND id = ?
            """,
            (user_id, plan_id),
        ).fetchone()

    if row is None:
        return None

    payload = PlannerRequest.model_validate_json(row["payload_json"])
    strategy = StrategyResponse.model_validate_json(row["strategy_json"])
    return SavedPlanDetail(
        id=row["id"],
        title=row["title"],
        created_at=row["created_at"],
        payload=payload,
        strategy=strategy,
    )
