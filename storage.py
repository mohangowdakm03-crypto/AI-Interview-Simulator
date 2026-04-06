from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict

import pandas as pd

RESULTS_FILE = Path(__file__).with_name("student_results.csv")
RESULT_COLUMNS = [
    "name",
    "usn",
    "email",
    "degree",
    "semester",
    "mode",
    "score",
    "total_possible",
    "average_score",
    "date",
]


def _ensure_results_file() -> None:
    if RESULTS_FILE.exists():
        return
    pd.DataFrame(columns=RESULT_COLUMNS).to_csv(RESULTS_FILE, index=False)


def load_all_results() -> pd.DataFrame:
    _ensure_results_file()
    dataframe = pd.read_csv(RESULTS_FILE)
    for column in RESULT_COLUMNS:
        if column not in dataframe.columns:
            dataframe[column] = ""
    for numeric_column in ("semester", "score", "total_possible", "average_score"):
        dataframe[numeric_column] = pd.to_numeric(dataframe[numeric_column], errors="coerce")
    return dataframe[RESULT_COLUMNS]


def load_student_records(usn: str) -> pd.DataFrame:
    dataframe = load_all_results()
    if dataframe.empty:
        return dataframe
    return dataframe[dataframe["usn"].astype(str).str.lower() == usn.strip().lower()].copy()


def append_result(record: Dict[str, object]) -> None:
    _ensure_results_file()
    row = {column: record.get(column, "") for column in RESULT_COLUMNS}
    if not row["date"]:
        row["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pd.DataFrame([row], columns=RESULT_COLUMNS).to_csv(
        RESULTS_FILE,
        mode="a",
        header=False,
        index=False,
    )
