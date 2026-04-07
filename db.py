from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

import pandas as pd

DB_PATH = Path(__file__).with_name("interview.db")
IST = ZoneInfo("Asia/Kolkata")
DISPLAY_TIME_FORMAT = "%d %b %Y, %I:%M %p"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def current_ist_time() -> datetime:
    return datetime.now(IST)


def format_timestamp(value: object) -> str:
    if value in (None, ""):
        return ""

    if isinstance(value, datetime):
        timestamp = value
    else:
        text = str(value).strip()
        if not text:
            return ""
        for pattern in (DISPLAY_TIME_FORMAT, "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S%z"):
            try:
                timestamp = datetime.strptime(text, pattern)
                break
            except ValueError:
                timestamp = None
        else:
            try:
                timestamp = datetime.fromisoformat(text.replace("Z", "+00:00"))
            except ValueError:
                return text

    if timestamp is None:
        return ""

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=ZoneInfo("UTC"))

    return timestamp.astimezone(IST).strftime(DISPLAY_TIME_FORMAT)


def format_timestamp_column(dataframe: pd.DataFrame, column: str = "date") -> pd.DataFrame:
    if column not in dataframe.columns:
        return dataframe
    formatted = dataframe.copy()
    formatted[column] = formatted[column].apply(format_timestamp)
    return formatted


def init_db() -> None:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                usn TEXT UNIQUE,
                email TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usn TEXT,
                score INTEGER,
                mode TEXT,
                date TEXT
            )
            """
        )
        connection.commit()


def ensure_student(name: str, usn: str, email: str) -> None:
    normalized_usn = usn.strip().lower()
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT usn FROM students WHERE usn = ?", (normalized_usn,))
        existing = cursor.fetchone()
        if existing is None:
            cursor.execute(
                "INSERT INTO students (name, usn, email) VALUES (?, ?, ?)",
                (name.strip(), normalized_usn, email.strip().lower()),
            )
        else:
            cursor.execute(
                "UPDATE students SET name = ?, email = ? WHERE usn = ?",
                (name.strip(), email.strip().lower(), normalized_usn),
            )
        connection.commit()


def insert_score(usn: str, score: int, mode: str, date: Optional[str] = None) -> None:
    normalized_usn = usn.strip().lower()
    attempt_date = date or current_ist_time().strftime(DISPLAY_TIME_FORMAT)
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO scores (usn, score, mode, date) VALUES (?, ?, ?, ?)",
            (normalized_usn, int(score), mode, attempt_date),
        )
        connection.commit()


def load_student_records(usn: str) -> pd.DataFrame:
    normalized_usn = usn.strip().lower()
    with get_connection() as connection:
        dataframe = pd.read_sql_query(
            """
            SELECT students.name, students.usn, students.email, scores.score, scores.mode, scores.date
            FROM students
            LEFT JOIN scores ON students.usn = scores.usn
            WHERE students.usn = ?
            ORDER BY scores.id DESC
            """,
            connection,
            params=(normalized_usn,),
        )
    return format_timestamp_column(dataframe)


def fetch_student_summary() -> pd.DataFrame:
    with get_connection() as connection:
        return pd.read_sql_query(
            """
            SELECT
                students.name,
                students.usn,
                students.email,
                COUNT(scores.id) AS total_attempts,
                ROUND(COALESCE(AVG(scores.score), 0), 2) AS average_score
            FROM students
            LEFT JOIN scores ON students.usn = scores.usn
            GROUP BY students.usn, students.name, students.email
            ORDER BY students.name COLLATE NOCASE ASC
            """,
            connection,
        )


def fetch_joined_records() -> pd.DataFrame:
    with get_connection() as connection:
        dataframe = pd.read_sql_query(
            """
            SELECT
                students.name,
                students.usn,
                students.email,
                scores.score,
                scores.mode,
                scores.date
            FROM students
            LEFT JOIN scores ON students.usn = scores.usn
            ORDER BY scores.id DESC, students.name COLLATE NOCASE ASC
            """,
            connection,
        )
    return format_timestamp_column(dataframe)


def fetch_leaderboard(limit: int = 10) -> pd.DataFrame:
    with get_connection() as connection:
        dataframe = pd.read_sql_query(
            f"""
            SELECT
                students.name,
                students.usn,
                MAX(scores.score) AS best_score,
                ROUND(COALESCE(AVG(scores.score), 0), 2) AS average_score,
                COUNT(scores.id) AS total_attempts,
                COALESCE(
                    (
                        SELECT latest_scores.date
                        FROM scores AS latest_scores
                        WHERE latest_scores.usn = students.usn
                        ORDER BY latest_scores.id DESC
                        LIMIT 1
                    ),
                    ''
                ) AS last_attempt
            FROM students
            LEFT JOIN scores ON students.usn = scores.usn
            GROUP BY students.usn, students.name
            ORDER BY best_score DESC, average_score DESC, students.name COLLATE NOCASE ASC
            LIMIT {int(limit)}
            """,
            connection,
        )
    return format_timestamp_column(dataframe, column="last_attempt")


def delete_student_by_usn(usn: str) -> bool:
    normalized_usn = usn.strip().lower()
    if not normalized_usn:
        return False

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT usn FROM students WHERE usn = ?", (normalized_usn,))
        existing = cursor.fetchone()
        if existing is None:
            return False
        cursor.execute("DELETE FROM scores WHERE usn = ?", (normalized_usn,))
        cursor.execute("DELETE FROM students WHERE usn = ?", (normalized_usn,))
        connection.commit()
        return True


def reset_database() -> None:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM scores")
        cursor.execute("DELETE FROM students")
        connection.commit()
