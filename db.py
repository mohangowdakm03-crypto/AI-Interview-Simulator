from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

DB_PATH = Path(__file__).with_name("interview.db")


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


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
    attempt_date = date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO scores (usn, score, mode, date) VALUES (?, ?, ?, ?)",
            (normalized_usn, int(score), mode, attempt_date),
        )
        connection.commit()


def load_student_records(usn: str) -> pd.DataFrame:
    normalized_usn = usn.strip().lower()
    with get_connection() as connection:
        return pd.read_sql_query(
            """
            SELECT students.name, students.usn, students.email, scores.score, scores.mode, scores.date
            FROM students
            LEFT JOIN scores ON students.usn = scores.usn
            WHERE students.usn = ?
            ORDER BY scores.date DESC
            """,
            connection,
            params=(normalized_usn,),
        )


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
        return pd.read_sql_query(
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
            ORDER BY scores.date DESC, students.name COLLATE NOCASE ASC
            """,
            connection,
        )


def fetch_leaderboard(limit: int = 10) -> pd.DataFrame:
    with get_connection() as connection:
        return pd.read_sql_query(
            f"""
            SELECT
                students.name,
                students.usn,
                MAX(scores.score) AS best_score,
                ROUND(COALESCE(AVG(scores.score), 0), 2) AS average_score,
                COUNT(scores.id) AS total_attempts
            FROM students
            LEFT JOIN scores ON students.usn = scores.usn
            GROUP BY students.usn, students.name
            ORDER BY best_score DESC, average_score DESC, students.name COLLATE NOCASE ASC
            LIMIT {int(limit)}
            """,
            connection,
        )


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
