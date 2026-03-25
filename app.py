from __future__ import annotations

import random
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional

import streamlit as st
import streamlit.components.v1 as components

from evaluator import EvaluationResult, build_special_evaluation, evaluate_answer
from questions import (
    InterviewMode,
    Question,
    difficulty_targets_for_semester,
    get_questions_for_semester,
)

QUESTION_TIME_LIMIT = 60
MODE_OPTIONS: List[InterviewMode] = ["technical", "hr", "mixed"]
DEGREE_OPTIONS: List[str] = ["BE", "BTECH"]
SEMESTER_OPTIONS: List[int] = list(range(1, 9))


@dataclass(frozen=True)
class InterviewItem:
    question: Question
    round_label: str
    is_follow_up: bool = False


def inject_css() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg-start: #040712;
                --bg-end: #0a1530;
                --glass: rgba(13, 19, 39, 0.68);
                --glass-strong: rgba(10, 15, 30, 0.84);
                --stroke: rgba(255, 255, 255, 0.11);
                --text: #f4f7ff;
                --muted: #9caccc;
                --accent-a: #4cc9f0;
                --accent-b: #8b5cf6;
                --accent-c: #38bdf8;
                --shadow: 0 24px 60px rgba(0, 0, 0, 0.28);
            }

            .stApp {
                background: transparent !important;
                color: var(--text);
                position: relative;
                z-index: 2;
                isolation: isolate;
            }

            [data-testid="stAppViewContainer"] {
                background: transparent !important;
                position: relative;
                z-index: 2;
            }

            [data-testid="stAppViewContainer"] > .main {
                background: transparent;
                position: relative;
                z-index: 2;
            }

            [data-testid="stAppViewContainer"],
            .stApp,
            .block-container {
                position: relative;
                z-index: 2;
            }

            header[data-testid="stHeader"],
            #MainMenu,
            footer,
            div[data-testid="stElementToolbar"],
            div[data-testid="stElementToolbarButton"],
            button[title="Copy link to element"],
            button[title="Copy link"],
            button[aria-label="Copy link to element"] {
                visibility: hidden;
                display: none !important;
            }

            a[href^="#"],
            a[href^="/#"],
            a[href*="#ai-interview-simulator"],
            [data-testid="stHeadingWithActionElements"] a,
            .stMarkdown a[href^="#"] {
                visibility: hidden !important;
                opacity: 0 !important;
                pointer-events: none !important;
                display: none !important;
            }

            .block-container {
                padding-top: 1.2rem;
                padding-bottom: 1.8rem;
                max-width: 1180px;
            }

            .hero {
                text-align: center;
                margin-bottom: 0.95rem;
                position: relative;
                z-index: 2;
            }

            .hero h1 {
                margin: 0;
                font-size: clamp(2.1rem, 4vw, 3.8rem);
                font-weight: 800;
                letter-spacing: 0.04em;
                color: #f3f8ff;
                text-shadow: 0 0 28px rgba(97, 218, 251, 0.14);
            }

            .hero p {
                color: var(--muted);
                margin: 0.45rem 0 0;
                font-size: 0.98rem;
            }

            .hero-accent {
                width: 120px;
                height: 4px;
                margin: 0.9rem auto 0;
                border-radius: 999px;
                background: linear-gradient(90deg, rgba(76, 201, 240, 0.95), rgba(139, 92, 246, 0.95));
                box-shadow: 0 0 18px rgba(97, 218, 251, 0.25);
            }

            .glass-card {
                background: var(--glass);
                border: 1px solid var(--stroke);
                box-shadow: var(--shadow);
                border-radius: 24px;
                backdrop-filter: blur(18px);
                -webkit-backdrop-filter: blur(18px);
                padding: 1.15rem 1.2rem;
            }

            .landing-card {
                max-width: 760px;
                margin: 0 auto;
                padding: 1.3rem 1.3rem 1.2rem;
                position: relative;
                overflow: hidden;
                z-index: 2;
            }

            .landing-card::before,
            .landing-card::after {
                content: "";
                position: absolute;
                border-radius: 999px;
                filter: blur(18px);
                opacity: 0.22;
                pointer-events: none;
            }

            .landing-card::before {
                width: 160px;
                height: 160px;
                top: -48px;
                right: -36px;
                background: radial-gradient(circle, rgba(76, 201, 240, 0.95), transparent 68%);
                animation: driftGlow 8s ease-in-out infinite;
            }

            .landing-card::after {
                width: 180px;
                height: 180px;
                bottom: -72px;
                left: -54px;
                background: radial-gradient(circle, rgba(139, 92, 246, 0.95), transparent 68%);
                animation: driftGlow 10s ease-in-out infinite reverse;
            }

            .fade-in {
                animation: landingFade 0.52s ease-out both;
            }

            .fade-delay-1 {
                animation-delay: 0.06s;
            }

            .fade-delay-2 {
                animation-delay: 0.12s;
            }

            .fade-delay-3 {
                animation-delay: 0.18s;
            }

            .landing-hero-card {
                max-width: 920px;
                margin: 0 auto 1rem;
                padding: 1.4rem 1.45rem 1.3rem;
            }

            .landing-kicker {
                color: #edf5ff;
                font-size: 1.22rem;
                font-weight: 700;
                margin: 0 0 0.55rem;
            }

            .landing-hero-copy {
                color: var(--muted);
                font-size: 0.98rem;
                line-height: 1.7;
                margin: 0;
            }

            .landing-bullet-list {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
                gap: 0.7rem;
                margin-top: 1rem;
            }

            .landing-bullet {
                display: flex;
                gap: 0.65rem;
                align-items: flex-start;
                padding: 0.85rem 0.9rem;
                border-radius: 18px;
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.08);
            }

            .landing-bullet-dot {
                width: 10px;
                height: 10px;
                border-radius: 999px;
                margin-top: 0.3rem;
                background: linear-gradient(135deg, rgba(76, 201, 240, 1), rgba(139, 92, 246, 1));
                box-shadow: 0 0 14px rgba(97, 218, 251, 0.3);
                flex: 0 0 auto;
            }

            .landing-bullet-text {
                color: #e9f1ff;
                font-size: 0.9rem;
                line-height: 1.55;
            }

            .landing-detail-card {
                height: 100%;
                padding: 1.15rem 1.2rem;
            }

            .landing-detail-title {
                font-size: 1.02rem;
                font-weight: 700;
                color: #eef6ff;
                margin: 0 0 0.8rem;
            }

            .landing-number-list,
            .landing-tip-list {
                margin: 0;
                padding-left: 1.15rem;
                color: #d8e6ff;
            }

            .landing-number-list li,
            .landing-tip-list li {
                margin-bottom: 0.55rem;
                line-height: 1.6;
            }

            .landing-mini-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
                gap: 0.7rem;
            }

            .landing-mini-card {
                padding: 0.9rem;
                border-radius: 18px;
                background: linear-gradient(180deg, rgba(17, 26, 52, 0.68), rgba(10, 17, 35, 0.58));
                border: 1px solid rgba(255, 255, 255, 0.08);
            }

            .landing-mini-card strong {
                display: block;
                color: #eef6ff;
                font-size: 0.9rem;
                margin-bottom: 0.4rem;
            }

            .landing-mini-card span {
                color: var(--muted);
                font-size: 0.85rem;
                line-height: 1.5;
            }

            .landing-start-card {
                max-width: 920px;
                margin: 1rem auto 0;
                padding: 1.15rem 1.2rem 1.2rem;
            }

            .section-title {
                color: var(--muted);
                text-transform: uppercase;
                letter-spacing: 0.14em;
                font-size: 0.74rem;
                margin-bottom: 0.8rem;
            }

            .question-card {
                padding: 1.2rem 1.25rem 1.3rem;
                margin-bottom: 0.9rem;
            }

            .question-card .meta-row {
                display: flex;
                gap: 0.6rem;
                flex-wrap: wrap;
                margin-bottom: 0.95rem;
            }

            .chip {
                display: inline-flex;
                align-items: center;
                border-radius: 999px;
                padding: 0.42rem 0.82rem;
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: #d9e7ff;
                font-size: 0.8rem;
            }

            .chip-strong {
                background: linear-gradient(90deg, rgba(76, 201, 240, 0.18), rgba(139, 92, 246, 0.22));
                border-color: rgba(125, 171, 255, 0.28);
                color: #eef6ff;
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04), 0 0 0 1px rgba(76, 201, 240, 0.08);
            }

            .question-text {
                font-size: 1.18rem;
                line-height: 1.72;
                font-weight: 600;
                color: var(--text);
                margin: 0;
            }

            .answer-card {
                padding: 1rem 1.1rem 1.05rem;
            }

            .button-note {
                margin-top: 0.65rem;
            }

            .feature-row {
                display: flex;
                gap: 0.6rem;
                flex-wrap: wrap;
                margin: 0.9rem 0 1rem;
            }

            .feature-chip {
                display: inline-flex;
                align-items: center;
                padding: 0.48rem 0.82rem;
                border-radius: 999px;
                color: #e1ecff;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.08);
                font-size: 0.82rem;
            }

            .metric-stack {
                display: grid;
                gap: 0.8rem;
            }

            .metric-card {
                padding: 0.95rem 1rem;
                border-radius: 20px;
                background: linear-gradient(180deg, rgba(17, 26, 52, 0.84), rgba(10, 17, 35, 0.76));
                border: 1px solid rgba(255, 255, 255, 0.08);
            }

            .metric-label {
                color: var(--muted);
                font-size: 0.76rem;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                margin-bottom: 0.3rem;
            }

            .metric-value {
                font-size: 1.45rem;
                font-weight: 800;
                color: var(--text);
            }

            .feedback-card {
                margin-top: 0.95rem;
            }

            .interviewer-card {
                margin-bottom: 0.9rem;
                border: 1px solid rgba(120, 173, 255, 0.18);
                background:
                    linear-gradient(135deg, rgba(76, 201, 240, 0.08), transparent 38%),
                    linear-gradient(180deg, rgba(15, 22, 44, 0.86), rgba(10, 15, 31, 0.78));
                position: relative;
                overflow: hidden;
            }

            .interviewer-card::before {
                content: "";
                position: absolute;
                inset: 0 auto 0 0;
                width: 4px;
                border-radius: 24px;
                background: linear-gradient(180deg, rgba(76, 201, 240, 0.98), rgba(139, 92, 246, 0.98));
                box-shadow: 0 0 18px rgba(97, 218, 251, 0.25);
            }

            .interviewer-copy {
                color: #e4efff;
                font-size: 1rem;
                line-height: 1.6;
                margin: 0;
                padding-left: 0.35rem;
            }

            .interviewer-label {
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                margin-bottom: 0.7rem;
                color: #dbe8ff;
                font-size: 0.82rem;
                letter-spacing: 0.16em;
                text-transform: uppercase;
            }

            .interviewer-dot {
                width: 10px;
                height: 10px;
                border-radius: 999px;
                background: linear-gradient(135deg, rgba(76, 201, 240, 1), rgba(139, 92, 246, 1));
                box-shadow: 0 0 14px rgba(97, 218, 251, 0.4);
            }

            .feedback-title {
                font-size: 1rem;
                font-weight: 700;
                margin-bottom: 0.7rem;
            }

            .feedback-list {
                margin: 0;
                padding-left: 1.05rem;
                color: #dce8ff;
            }

            .feedback-list li {
                margin-bottom: 0.3rem;
                line-height: 1.55;
            }

            .muted-note {
                color: var(--muted);
                font-size: 0.9rem;
                line-height: 1.55;
                margin: 0;
            }

            .stTextArea textarea {
                border-radius: 18px !important;
                background: rgba(9, 16, 34, 0.9) !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
                color: #eff6ff !important;
                min-height: 220px !important;
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
            }

            .stTextArea textarea:focus {
                border-color: rgba(97, 218, 251, 0.72) !important;
                box-shadow: 0 0 0 1px rgba(97, 218, 251, 0.32) !important;
            }

            .stTextArea label,
            .stSelectbox label {
                color: #dbe6ff !important;
                font-weight: 600 !important;
            }

            [data-testid="stSelectbox"] [data-baseweb="select"] span,
            [data-testid="stSelectbox"] [data-baseweb="select"] div,
            div[role="listbox"] div,
            ul[role="listbox"] li,
            [role="option"] {
                text-transform: uppercase !important;
            }

            .stProgress > div > div > div > div {
                background: linear-gradient(90deg, var(--accent-a), var(--accent-b)) !important;
            }

            div[data-testid="stButton"] button,
            div[data-testid="stFormSubmitButton"] button {
                border-radius: 16px !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
                color: white !important;
                font-weight: 700 !important;
                padding: 0.72rem 1rem !important;
                background: linear-gradient(90deg, rgba(76, 201, 240, 0.96), rgba(139, 92, 246, 0.96)) !important;
                box-shadow: 0 16px 32px rgba(11, 18, 40, 0.28);
                transition: transform 0.18s ease, filter 0.18s ease, box-shadow 0.18s ease;
            }

            div[data-testid="stButton"] button:hover,
            div[data-testid="stFormSubmitButton"] button:hover {
                filter: brightness(1.08);
                transform: translateY(-1px);
                box-shadow: 0 0 0 1px rgba(102, 219, 255, 0.25), 0 16px 34px rgba(21, 32, 65, 0.42);
            }

            .summary-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(165px, 1fr));
                gap: 0.8rem;
                margin: 0.85rem 0 1rem;
            }

            .summary-card {
                padding: 0.95rem;
                border-radius: 18px;
                background: rgba(12, 21, 40, 0.74);
                border: 1px solid rgba(255, 255, 255, 0.08);
            }

            body[data-ai-viewport="mobile"] .block-container {
                padding-top: 0.8rem !important;
                padding-bottom: 1.2rem !important;
                overflow-x: hidden !important;
            }

            body[data-ai-viewport="mobile"] .hero {
                margin-bottom: 0.7rem !important;
            }

            body[data-ai-viewport="mobile"] .hero h1 {
                font-size: clamp(1.9rem, 8vw, 2.8rem) !important;
            }

            body[data-ai-viewport="mobile"] .hero p,
            body[data-ai-viewport="mobile"] .landing-hero-copy,
            body[data-ai-viewport="mobile"] .muted-note {
                font-size: 0.92rem !important;
            }

            body[data-ai-viewport="mobile"] .landing-hero-card,
            body[data-ai-viewport="mobile"] .landing-start-card,
            body[data-ai-viewport="mobile"] .glass-card {
                margin-left: 0 !important;
                margin-right: 0 !important;
                max-width: 100% !important;
            }

            body[data-ai-viewport="mobile"] .landing-bullet-list,
            body[data-ai-viewport="mobile"] .landing-mini-grid,
            body[data-ai-viewport="mobile"] .summary-grid {
                grid-template-columns: 1fr !important;
            }

            body[data-ai-viewport="mobile"] .question-text {
                font-size: 1.03rem !important;
                line-height: 1.6 !important;
                word-break: break-word;
            }

            body[data-ai-viewport="mobile"] [data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
                gap: 0.85rem !important;
            }

            body[data-ai-viewport="mobile"] [data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 0 !important;
            }

            body[data-ai-viewport="mobile"] .metric-value {
                font-size: 1.3rem !important;
            }

            body[data-ai-viewport="mobile"] .stTextArea textarea {
                min-height: 170px !important;
            }

            body[data-ai-viewport="mobile"] div[data-testid="stButton"] button,
            body[data-ai-viewport="mobile"] div[data-testid="stFormSubmitButton"] button {
                width: 100% !important;
                min-height: 48px !important;
            }

            @keyframes driftGlow {
                0% { transform: translate3d(0, 0, 0) scale(1); }
                50% { transform: translate3d(10px, -8px, 0) scale(1.08); }
                100% { transform: translate3d(0, 0, 0) scale(1); }
            }

            @keyframes landingFade {
                from {
                    opacity: 0;
                    transform: translateY(12px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

        </style>
        """,
        unsafe_allow_html=True,
    )


def init_session_state() -> None:
    defaults = {
        "mode": "technical",
        "degree": "BE",
        "current_semester": 4,
        "interview_started": False,
        "completed": False,
        "question_queue": [],
        "current_queue_index": 0,
        "current_question_index": 0,
        "total_questions_expected": 0,
        "score": 0,
        "difficulty": "easy",
        "answers": [],
        "last_feedback": None,
        "deadline_at": None,
        "question_started_at": None,
        "answer_input": "",
        "clear_input": False,
        "controls_disabled": False,
        "notification": None,
        "interviewer_message": "Let's begin.",
        "follow_up_count": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_answer_input_if_needed() -> None:
    """
    Clear the textarea safely before the widget is rendered.

    Streamlit raises an error when we mutate a widget-backed session key after
    that widget has already been created in the same run. We avoid that by
    using a flag plus rerun, then clearing the value at the top of the next run.
    """
    if st.session_state.clear_input:
        st.session_state.pop("answer_input", None)
        st.session_state.answer_input = ""
        st.session_state.clear_input = False


def set_notification(kind: str, message: str) -> None:
    st.session_state.notification = {"kind": kind, "message": message}


def render_notification() -> None:
    notification = st.session_state.notification
    if not notification:
        return

    kind = notification["kind"]
    message = notification["message"]
    if kind == "success":
        st.success(message)
    elif kind == "warning":
        st.warning(message)
    else:
        st.info(message)

    st.session_state.notification = None


def current_item() -> Optional[InterviewItem]:
    queue: List[InterviewItem] = st.session_state.question_queue
    index = st.session_state.current_queue_index
    if not queue or index >= len(queue):
        return None
    return queue[index]


def current_question() -> Question | None:
    item = current_item()
    if item is None:
        return None
    return item.question


def steps_total() -> int:
    return int(st.session_state.total_questions_expected or 0)


def progress_ratio() -> float:
    total = steps_total()
    if total == 0:
        return 0.0
    return min(len(st.session_state.answers) / total, 1.0)


def _sample_questions(
    *,
    mode: InterviewMode,
    counts: Dict[str, int],
    semester: int,
    exclude_ids: Optional[set[str]] = None,
) -> List[Question]:
    rng = random.Random()
    exclude_ids = exclude_ids or set()
    sampled: List[Question] = []
    fill_order: List[str] = ["easy", "medium", "hard"] if semester <= 4 else ["medium", "hard", "easy"]

    available_by_difficulty: Dict[str, List[Question]] = {
        difficulty: [
            question
            for question in get_questions_for_semester(mode=mode, semester=semester, difficulty=difficulty)  # type: ignore[arg-type]
            if question.id not in exclude_ids
        ]
        for difficulty in ("easy", "medium", "hard")
    }

    adjusted_counts = {difficulty: min(counts.get(difficulty, 0), len(available_by_difficulty[difficulty])) for difficulty in counts}
    remaining = 10 if sum(counts.values()) == 10 else sum(counts.values())
    remaining -= sum(adjusted_counts.values())

    while remaining > 0:
        progressed = False
        for difficulty in fill_order:
            if adjusted_counts.get(difficulty, 0) < len(available_by_difficulty[difficulty]):
                adjusted_counts[difficulty] = adjusted_counts.get(difficulty, 0) + 1
                remaining -= 1
                progressed = True
                if remaining == 0:
                    break
        if not progressed:
            break

    for difficulty, count in counts.items():
        count = adjusted_counts.get(difficulty, 0)
        if count <= 0:
            continue
        candidates = [question for question in available_by_difficulty[difficulty] if question.id not in exclude_ids]
        sampled.extend(rng.sample(candidates, count))
        exclude_ids.update(question.id for question in sampled)
    rng.shuffle(sampled)
    return sampled


def _build_closing_question() -> Question:
    return Question(
        id="hr_closing_questions",
        mode="hr",
        difficulty="easy",
        topic="Closing",
        prompt="Do you have any questions for me?",
        keywords_required=["questions"],
        keywords_optional=["company", "team", "role", "learning", "next steps"],
    )


def _build_interview_queue(mode: InterviewMode, semester: int) -> List[InterviewItem]:
    difficulty_order = {"easy": 0, "medium": 1, "hard": 2}
    semester_targets = difficulty_targets_for_semester(semester, 10)
    if mode == "technical":
        technical_questions = _sample_questions(
            mode="technical",
            counts=semester_targets,
            semester=semester,
        )
        technical_questions.sort(key=lambda question: (difficulty_order[question.difficulty], question.id))
        return [
            InterviewItem(question=question, round_label="Technical Round")
            for question in technical_questions
        ]
    elif mode == "hr":
        hr_questions = _sample_questions(
            mode="hr",
            counts=semester_targets,
            semester=semester,
        )
        hr_questions.sort(key=lambda question: (difficulty_order[question.difficulty], question.id))
        return [InterviewItem(question=question, round_label="HR Round") for question in hr_questions]
    else:
        mixed_targets = difficulty_targets_for_semester(semester, 5)
        technical_questions = _sample_questions(
            mode="technical",
            counts=mixed_targets,
            semester=semester,
        )
        hr_questions = _sample_questions(
            mode="hr",
            counts=mixed_targets,
            semester=semester,
        )
        technical_questions.sort(key=lambda question: (difficulty_order[question.difficulty], question.id))
        hr_questions.sort(key=lambda question: (difficulty_order[question.difficulty], question.id))
        queue: List[InterviewItem] = []
        for technical_question, hr_question in zip(technical_questions, hr_questions):
            queue.append(InterviewItem(question=technical_question, round_label="Technical Round"))
            queue.append(InterviewItem(question=hr_question, round_label="HR Round"))
        return queue


def update_state() -> None:
    st.session_state.controls_disabled = False
    st.session_state.clear_input = True
    item = current_item()
    if item is None:
        st.session_state.completed = True
        st.session_state.deadline_at = None
        st.session_state.question_started_at = None
        st.session_state.current_question_index = len(st.session_state.answers)
        return

    st.session_state.current_question_index = st.session_state.current_queue_index + 1
    st.session_state.difficulty = item.question.difficulty
    st.session_state.question_started_at = time.time()
    st.session_state.deadline_at = st.session_state.question_started_at + QUESTION_TIME_LIMIT


def start_interview(mode: InterviewMode, degree: str, current_semester: int) -> None:
    question_queue = _build_interview_queue(mode, current_semester)
    st.session_state.mode = mode
    st.session_state.degree = degree
    st.session_state.current_semester = current_semester
    st.session_state.interview_started = True
    st.session_state.completed = False
    st.session_state.question_queue = question_queue
    st.session_state.current_queue_index = 0
    st.session_state.answers = []
    st.session_state.last_feedback = None
    st.session_state.score = 0
    st.session_state.difficulty = "easy"
    st.session_state.notification = None
    st.session_state.total_questions_expected = len(question_queue)
    st.session_state.follow_up_count = 0
    if mode == "technical":
        st.session_state.interviewer_message = "Let's begin with technical questions."
    elif mode == "hr":
        st.session_state.interviewer_message = "Let's begin with HR questions."
    else:
        st.session_state.interviewer_message = "Let's begin. We'll alternate technical and HR questions."
    update_state()


def _build_follow_up_question(question: Question, evaluation: EvaluationResult) -> Optional[Question]:
    if st.session_state.total_questions_expected >= 10:
        return None
    if st.session_state.follow_up_count >= 2:
        return None
    item = current_item()
    if item is None or item.is_follow_up:
        return None

    if evaluation.points_awarded >= 8:
        if question.type == "technical":
            prompt = f"Good answer, let's go deeper. Can you explain {question.topic.lower()} with a simple example?"
        else:
            prompt = "Good answer, let's go a bit deeper. Can you share one concrete example from your experience?"
    elif evaluation.points_awarded <= 4:
        if question.type == "technical":
            prompt = "Can you explain that in simpler terms with one clear example?"
        else:
            prompt = "Can you answer that more directly in 2 or 3 clear sentences?"
    else:
        return None

    return Question(
        id=question.id,
        mode=question.mode,
        difficulty=question.difficulty,
        topic=question.topic,
        prompt=prompt,
        keywords_required=question.keywords_required,
        keywords_optional=question.keywords_optional,
        max_points=question.max_points,
    )


def _set_next_interviewer_message(
    next_item: Optional[InterviewItem],
    *,
    previous_round: str,
    follow_up_inserted: bool,
) -> None:
    if follow_up_inserted:
        return
    if next_item is None:
        st.session_state.interviewer_message = "That concludes the interview. Thanks for your time."
        return
    if next_item.round_label != previous_round and next_item.round_label == "Technical Round":
        st.session_state.interviewer_message = "Thanks. Now let's move into the technical round."
        return
    if next_item.round_label != previous_round and next_item.round_label == "HR Round":
        st.session_state.interviewer_message = "Alright, now let's move into the HR round."
        return
    if next_item.round_label != previous_round and next_item.round_label == "Closing":
        st.session_state.interviewer_message = "We are almost done. I have one final question for you."
        return
    st.session_state.interviewer_message = "Alright, next question."


def process_answer(status: str, answer_text: str = "") -> None:
    if st.session_state.controls_disabled:
        return

    question = current_question()
    item = current_item()
    if question is None or item is None:
        return

    st.session_state.controls_disabled = True
    time_taken = min(
        max(0.0, time.time() - float(st.session_state.question_started_at or time.time())),
        float(QUESTION_TIME_LIMIT),
    )
    cleaned_answer = answer_text.strip()

    if status == "timeout":
        evaluation = build_special_evaluation(question, status="timeout")
        cleaned_answer = ""
        set_notification("warning", "Time is up! The question was auto-submitted with a low score.")
    elif status == "skip":
        evaluation = build_special_evaluation(question, status="skip")
        cleaned_answer = "skip"
        set_notification("info", "Question skipped. Moving to the next one.")
    else:
        evaluation = evaluate_answer(question, cleaned_answer)
        set_notification("success", "Answer submitted.")

    record = {
        "question": question,
        "answer": cleaned_answer,
        "evaluation": evaluation,
        "time_taken": time_taken,
        "skipped": status == "skip",
        "timed_out": status == "timeout",
        "passed": evaluation.normalized_score >= 0.6,
        "round_label": item.round_label,
        "is_follow_up": item.is_follow_up,
    }

    st.session_state.answers.append(record)
    st.session_state.last_feedback = record
    st.session_state.score = sum(
        answer_record["evaluation"].points_awarded for answer_record in st.session_state.answers
    )
    follow_up_inserted = False

    follow_up_question = None
    if status == "submit":
        follow_up_question = _build_follow_up_question(question, evaluation)

    current_index = st.session_state.current_queue_index
    if follow_up_question is not None:
        st.session_state.question_queue.insert(
            current_index + 1,
            InterviewItem(question=follow_up_question, round_label=item.round_label, is_follow_up=True),
        )
        st.session_state.total_questions_expected += 1
        st.session_state.follow_up_count += 1
        follow_up_inserted = True
        if evaluation.points_awarded >= 8:
            st.session_state.interviewer_message = "Good answer, let's go a bit deeper."
        else:
            st.session_state.interviewer_message = "Let's simplify that with one quick follow-up."

    st.session_state.current_queue_index += 1
    if st.session_state.current_queue_index >= len(st.session_state.question_queue):
        st.session_state.question_queue = []
        update_state()
        _set_next_interviewer_message(None, previous_round=item.round_label, follow_up_inserted=False)
        return

    update_state()
    _set_next_interviewer_message(
        current_item(),
        previous_round=item.round_label,
        follow_up_inserted=follow_up_inserted,
    )


def build_report(records: List[dict]) -> dict:
    total_score = sum(record["evaluation"].points_awarded for record in records)
    total_possible = sum(record["evaluation"].max_points for record in records)
    average_score = total_score / len(records) if records else 0.0
    average_time = sum(record["time_taken"] for record in records) / len(records) if records else 0.0

    topic_scores: Dict[str, List[int]] = defaultdict(list)
    topic_gaps: Dict[str, List[str]] = defaultdict(list)
    for record in records:
        question = record["question"]
        evaluation = record["evaluation"]
        if record["skipped"]:
            continue
        topic_scores[question.topic].append(evaluation.points_awarded)
        topic_gaps[question.topic].extend(evaluation.missing_points)

    topic_averages = {
        topic: sum(scores) / len(scores)
        for topic, scores in topic_scores.items()
    }
    ordered_topics = sorted(topic_averages.items(), key=lambda item: (-item[1], item[0]))
    strengths = [topic for topic, score in ordered_topics if score >= 7.5][:3]
    weaknesses = [topic for topic, score in ordered_topics if score < 6.0][:3]

    if not strengths and ordered_topics:
        strengths = [ordered_topics[0][0]]
    if not weaknesses and len(ordered_topics) > 1:
        weaknesses = [ordered_topics[-1][0]]

    suggestions: List[str] = []
    for topic in weaknesses:
        common_gap = Counter(topic_gaps[topic]).most_common(1)
        if common_gap:
            suggestions.append(f"{topic}: {common_gap[0][0]}")

    if not suggestions:
        suggestions.append("Keep practicing concise answers with one clear example and one key concept.")

    fastest = min(records, key=lambda record: record["time_taken"])
    slowest = max(records, key=lambda record: record["time_taken"])

    return {
        "total_score": total_score,
        "total_possible": total_possible,
        "average_score": average_score,
        "average_time": average_time,
        "skipped_count": sum(1 for record in records if record["skipped"]),
        "timed_out_count": sum(1 for record in records if record["timed_out"]),
        "fastest": f"{fastest['question'].topic} ({fastest['time_taken']:.1f}s)",
        "slowest": f"{slowest['question'].topic} ({slowest['time_taken']:.1f}s)",
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "skip_summary": f"You skipped {sum(1 for record in records if record['skipped'])} questions.",
    }


def render_title() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>AI Interview Simulator</h1>
            <p>VTU-friendly interview practice for students across semesters with technical, HR, and mixed rounds.</p>
            <div class="hero-accent"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_landing_background(active: bool) -> None:
    mode = "landing" if active else "interview"
    components.html(
        f"""
        <html>
        <body style="margin:0;background:transparent;overflow:hidden;">
        <script>
            const parentDoc = window.parent.document;
            const mode = "{mode}";
            const LANDING_ID = "ai-landing-particles-bg";
            const INTERVIEW_ID = "ai-interview-gradient-bg";
            const STYLE_ID = "ai-dynamic-background-style";

            function ensureStyle() {{
                let styleEl = parentDoc.getElementById(STYLE_ID);
                if (styleEl) return;
                styleEl = parentDoc.createElement("style");
                styleEl.id = STYLE_ID;
                styleEl.textContent = `
                    #${{LANDING_ID}}, #${{INTERVIEW_ID}} {{
                        position: fixed;
                        inset: 0;
                        pointer-events: none;
                        z-index: -1;
                    }}
                    #${{INTERVIEW_ID}} {{
                        overflow: hidden;
                        background:
                            radial-gradient(circle at 18% 24%, rgba(76, 201, 240, 0.14), transparent 30%),
                            radial-gradient(circle at 82% 18%, rgba(139, 92, 246, 0.16), transparent 28%),
                            linear-gradient(140deg, #040712, #0a1530);
                    }}
                    #${{INTERVIEW_ID}} .ai-gradient-orb {{
                        position: absolute;
                        border-radius: 999px;
                        filter: blur(80px);
                        opacity: 0.22;
                        mix-blend-mode: screen;
                        animation: aiGradientFloat 18s ease-in-out infinite alternate;
                    }}
                    #${{INTERVIEW_ID}} .ai-gradient-orb.orb-a {{
                        width: 34vw;
                        height: 34vw;
                        min-width: 280px;
                        min-height: 280px;
                        top: -8vh;
                        left: -6vw;
                        background: rgba(76, 201, 240, 0.30);
                    }}
                    #${{INTERVIEW_ID}} .ai-gradient-orb.orb-b {{
                        width: 36vw;
                        height: 36vw;
                        min-width: 300px;
                        min-height: 300px;
                        right: -8vw;
                        top: 8vh;
                        background: rgba(139, 92, 246, 0.26);
                        animation-delay: 3s;
                    }}
                    #${{INTERVIEW_ID}} .ai-gradient-orb.orb-c {{
                        width: 30vw;
                        height: 30vw;
                        min-width: 240px;
                        min-height: 240px;
                        left: 28vw;
                        bottom: -10vh;
                        background: rgba(56, 189, 248, 0.18);
                        animation-delay: 6s;
                    }}
                    @keyframes aiGradientFloat {{
                        0% {{ transform: translate3d(0, 0, 0) scale(1); }}
                        50% {{ transform: translate3d(2vw, -2vh, 0) scale(1.08); }}
                        100% {{ transform: translate3d(-1vw, 3vh, 0) scale(0.96); }}
                    }}
                `;
                parentDoc.head.appendChild(styleEl);
            }}

            function removeElement(id) {{
                const node = parentDoc.getElementById(id);
                if (node) node.remove();
            }}

            function stopLandingLoop() {{
                if (window.parent.__aiLandingAnimationFrame) {{
                    window.parent.cancelAnimationFrame(window.parent.__aiLandingAnimationFrame);
                    window.parent.__aiLandingAnimationFrame = null;
                }}
                window.parent.__aiLandingLoopActive = false;
            }}

            function removeLandingParticles() {{
                stopLandingLoop();
                removeElement(LANDING_ID);
            }}

            function removeInterviewGradient() {{
                removeElement(INTERVIEW_ID);
            }}

            function ensureLandingParticles() {{
                removeInterviewGradient();
                let wrapper = parentDoc.getElementById(LANDING_ID);
                if (!wrapper) {{
                    wrapper = parentDoc.createElement("div");
                    wrapper.id = LANDING_ID;
                    const canvas = parentDoc.createElement("canvas");
                    canvas.id = "ai-landing-particles-canvas";
                    canvas.style.width = "100%";
                    canvas.style.height = "100%";
                    canvas.style.display = "block";
                    canvas.style.opacity = "0.88";
                    wrapper.appendChild(canvas);
                    parentDoc.body.prepend(wrapper);
                }}

                if (window.parent.__aiLandingLoopActive) {{
                    return;
                }}

                const canvas = parentDoc.getElementById("ai-landing-particles-canvas");
                const ctx = canvas.getContext("2d");
                const particles = [];
                const total = 42;

                function resizeCanvas() {{
                    canvas.width = window.parent.innerWidth;
                    canvas.height = window.parent.innerHeight;
                }}

                function seedParticles() {{
                    particles.length = 0;
                    for (let i = 0; i < total; i += 1) {{
                        particles.push({{
                            x: Math.random() * canvas.width,
                            y: Math.random() * canvas.height,
                            radius: Math.random() * 2.2 + 0.9,
                            vx: (Math.random() - 0.5) * 0.16,
                            vy: (Math.random() - 0.5) * 0.16,
                            color: i % 2 === 0 ? "76, 201, 240" : "139, 92, 246",
                        }});
                    }}
                }}

                function draw() {{
                    if (!parentDoc.getElementById(LANDING_ID)) {{
                        stopLandingLoop();
                        return;
                    }}

                    ctx.clearRect(0, 0, canvas.width, canvas.height);

                    for (const particle of particles) {{
                        particle.x += particle.vx;
                        particle.y += particle.vy;

                        if (particle.x < -20) particle.x = canvas.width + 20;
                        if (particle.x > canvas.width + 20) particle.x = -20;
                        if (particle.y < -20) particle.y = canvas.height + 20;
                        if (particle.y > canvas.height + 20) particle.y = -20;

                        ctx.beginPath();
                        ctx.fillStyle = `rgba(${{particle.color}}, 0.34)`;
                        ctx.shadowBlur = 14;
                        ctx.shadowColor = `rgba(${{particle.color}}, 0.18)`;
                        ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
                        ctx.fill();
                    }}

                    ctx.shadowBlur = 0;
                    for (let i = 0; i < particles.length; i += 1) {{
                        for (let j = i + 1; j < particles.length; j += 1) {{
                            const a = particles[i];
                            const b = particles[j];
                            const dx = a.x - b.x;
                            const dy = a.y - b.y;
                            const dist = Math.sqrt(dx * dx + dy * dy);
                            if (dist < 150) {{
                                ctx.beginPath();
                                ctx.strokeStyle = `rgba(122, 164, 255, ${{0.08 - dist / 2200}})`;
                                ctx.lineWidth = 1;
                                ctx.moveTo(a.x, a.y);
                                ctx.lineTo(b.x, b.y);
                                ctx.stroke();
                            }}
                        }}
                    }}

                    window.parent.__aiLandingAnimationFrame = window.parent.requestAnimationFrame(draw);
                }}

                resizeCanvas();
                seedParticles();
                window.parent.addEventListener("resize", resizeCanvas);
                window.parent.__aiLandingLoopActive = true;
                draw();
            }}

            function ensureInterviewGradient() {{
                removeLandingParticles();
                let wrapper = parentDoc.getElementById(INTERVIEW_ID);
                if (!wrapper) {{
                    wrapper = parentDoc.createElement("div");
                    wrapper.id = INTERVIEW_ID;
                    wrapper.innerHTML = `
                        <div class="ai-gradient-orb orb-a"></div>
                        <div class="ai-gradient-orb orb-b"></div>
                        <div class="ai-gradient-orb orb-c"></div>
                    `;
                    parentDoc.body.prepend(wrapper);
                }}
            }}

            ensureStyle();
            if (mode === "landing") {{
                ensureLandingParticles();
            }} else {{
                ensureInterviewGradient();
            }}
        </script>
        </body>
        </html>
        """,
        height=0,
    )


def inject_responsive_controller() -> None:
    components.html(
        """
        <html>
        <body style="margin:0;background:transparent;overflow:hidden;">
        <script>
            const parentDoc = window.parent.document;
            function applyViewportTag() {
                const isMobile = window.parent.innerWidth <= 900;
                parentDoc.body.setAttribute("data-ai-viewport", isMobile ? "mobile" : "desktop");
            }
            applyViewportTag();
            window.parent.addEventListener("resize", applyViewportTag);
        </script>
        </body>
        </html>
        """,
        height=0,
    )


def render_landing() -> None:
    st.markdown(
        """
        <div class="glass-card landing-start-card fade-in fade-delay-3">
            <div class="section-title">Start Interview</div>
            <p class="muted-note">
                Select your practice mode and begin. These guidance sections disappear as soon as the interview starts.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    profile_col_1, profile_col_2 = st.columns(2, gap="large")
    with profile_col_1:
        selected_degree = st.selectbox(
            "Degree",
            DEGREE_OPTIONS,
            index=DEGREE_OPTIONS.index(st.session_state.degree),
        )
    with profile_col_2:
        selected_semester = st.selectbox(
            "Current semester",
            SEMESTER_OPTIONS,
            index=SEMESTER_OPTIONS.index(int(st.session_state.current_semester)),
        )

    st.markdown(
        f"<p class='muted-note'>Semester: {selected_semester} (VTU). Questions are adapted to your level.</p>",
        unsafe_allow_html=True,
    )

    selected_mode = st.selectbox(
        "Interview mode",
        MODE_OPTIONS,
        index=MODE_OPTIONS.index(st.session_state.mode),
        format_func=lambda mode: mode.upper(),
    )
    if st.button("Start Interview", type="primary", use_container_width=True):
        start_interview(selected_mode, selected_degree, int(selected_semester))
        st.rerun()

    st.markdown(
        """
        <div class="glass-card landing-hero-card fade-in">
            <div class="section-title">Practice Smarter</div>
            <p class="landing-kicker">Build interview confidence before campus placements and internship rounds.</p>
            <p class="landing-hero-copy">
                This simulator is designed for VTU-level students who want focused interview practice with realistic
                technical and HR questions, quick feedback, and a smooth guided experience.
            </p>
            <div class="landing-bullet-list">
                <div class="landing-bullet">
                    <span class="landing-bullet-dot"></span>
                    <div class="landing-bullet-text">Practice <strong>TECHNICAL, HR, or MIXED</strong> interview modes in one place.</div>
                </div>
                <div class="landing-bullet">
                    <span class="landing-bullet-dot"></span>
                    <div class="landing-bullet-text">Get <strong>instant feedback</strong> on strengths, missing ideas, and next improvements.</div>
                </div>
                <div class="landing-bullet">
                    <span class="landing-bullet-dot"></span>
                    <div class="landing-bullet-text">Use <strong>voice input</strong> or typed answers during each timed question.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([1.1, 0.9], gap="large")

    with left_col:
        st.markdown(
            """
            <div class="glass-card landing-detail-card fade-in fade-delay-1" style="margin-top: 0.95rem;">
                <div class="section-title">How It Works</div>
                <p class="landing-detail-title">A simple interview flow from start to finish.</p>
                <ol class="landing-number-list">
                    <li>Choose a mode: TECHNICAL, HR, or MIXED.</li>
                    <li>Answer 10 timed questions from the VTU-level practice bank.</li>
                    <li>Review score, strengths, and missing points after each response.</li>
                    <li>Finish with a summary of performance, skipped questions, and speed.</li>
                </ol>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="glass-card landing-detail-card fade-in fade-delay-2" style="margin-top: 0.95rem;">
                <div class="section-title">Tips</div>
                <p class="landing-detail-title">Small habits that improve interview performance.</p>
                <ul class="landing-tip-list">
                    <li>Start with a direct answer first, then add one supporting detail or example.</li>
                    <li>Keep technical explanations simple enough to speak clearly within one minute.</li>
                    <li>If you are unsure, explain your approach instead of staying silent.</li>
                    <li>In HR answers, show clarity, teamwork, confidence, and self-awareness.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        st.markdown(
            """
            <div class="glass-card landing-detail-card fade-in fade-delay-2" style="margin-top: 0.95rem;">
                <div class="section-title">Features</div>
                <p class="landing-detail-title">Built for realistic VTU-level practice.</p>
                <div class="landing-mini-grid">
                    <div class="landing-mini-card">
                        <strong>Adaptive Questions</strong>
                        <span>Difficulty moves from easy to harder questions in a student-friendly way.</span>
                    </div>
                    <div class="landing-mini-card">
                        <strong>Feedback</strong>
                        <span>See strengths, weaknesses, and suggestions after every response.</span>
                    </div>
                    <div class="landing-mini-card">
                        <strong>Voice Input</strong>
                        <span>Speak your answer in the browser and edit the transcript before submitting.</span>
                    </div>
                    <div class="landing-mini-card">
                        <strong>VTU-Level Questions</strong>
                        <span>Questions stay practical and suitable for BE 4th semester preparation.</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_question_card(question: Question) -> None:
    current_index = st.session_state.current_question_index
    total = steps_total()
    item = current_item()
    question_type_label = "HR Question" if question.type == "hr" else "Technical Question"
    round_label = item.round_label if item is not None else "Interview"
    prompt_label = "Follow-up Question" if item is not None and item.is_follow_up else "Current Question"
    st.markdown(
        f"""
        <div class="glass-card question-card">
            <div class="section-title">{prompt_label}</div>
            <div class="meta-row">
                <span class="chip">Question {current_index} of {total}</span>
                <span class="chip chip-strong">{round_label}</span>
                <span class="chip chip-strong">{question_type_label}</span>
                <span class="chip">{question.topic}</span>
                <span class="chip">{question.difficulty.title()}</span>
            </div>
            <p class="question-text">{question.prompt}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_voice_button(question_id: str) -> None:
    """
    Browser-side voice input using the Web Speech API.

    The component lives in an iframe, finds the parent Streamlit textarea,
    and writes recognized text into it. The user can still edit the text
    before submitting the answer.
    """
    components.html(
        f"""
        <html>
        <body style="margin:0;background:transparent;overflow:hidden;">
        <div style="height:72px; display:flex; align-items:center; justify-content:center; background:transparent;">
            <button id="voice-trigger" type="button" style="
                width:100%;
                border:none;
                border-radius:16px;
                padding:0.72rem 1rem;
                color:white;
                cursor:pointer;
                font-weight:700;
                background:linear-gradient(90deg, rgba(76, 201, 240, 0.96), rgba(139, 92, 246, 0.96));
                box-shadow:0 16px 30px rgba(13, 18, 38, 0.28);
                font-family:system-ui, sans-serif;
            ">
                🎤 Start Speaking
            </button>
            <div id="voice-status" style="
                display:none;
                width:100%;
                border-radius:16px;
                padding:0.78rem 0.95rem;
                color:#eef6ff;
                text-align:center;
                background:rgba(12, 22, 44, 0.88);
                border:1px solid rgba(255,255,255,0.08);
                font-family:system-ui, sans-serif;
                font-weight:600;
            "></div>
        </div>

        <script>
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const questionId = "{question_id}";
            const trigger = document.getElementById("voice-trigger");
            const statusEl = document.getElementById("voice-status");
            let recognition = null;
            let transcriptFinal = "";
            let isListening = false;

            function resetButton(message) {{
                statusEl.textContent = message;
                statusEl.style.display = message ? "block" : "none";
                trigger.style.display = "block";
                trigger.disabled = false;
                trigger.textContent = "🎤 Start Speaking";
                isListening = false;
            }}

            function findAnswerTextarea() {{
                const parentDoc = window.parent.document;
                return parentDoc.querySelector('textarea[aria-label="Your answer"]') || parentDoc.querySelector("textarea");
            }}

            function writeTranscript(text) {{
                const textarea = findAnswerTextarea();
                if (!textarea) {{
                    resetButton("Answer box not available yet.");
                    return;
                }}

                const nativeSetter = Object.getOwnPropertyDescriptor(
                    window.parent.HTMLTextAreaElement.prototype,
                    "value"
                ).set;
                nativeSetter.call(textarea, text);
                textarea.dispatchEvent(new Event("input", {{ bubbles: true }}));
                textarea.dispatchEvent(new Event("change", {{ bubbles: true }}));
                textarea.focus();
            }}

            if (!SpeechRecognition) {{
                trigger.disabled = true;
                trigger.textContent = "Voice input not supported in this browser";
                statusEl.style.display = "none";
            }} else {{
                recognition = new SpeechRecognition();
                recognition.lang = "en-US";
                recognition.continuous = false;
                recognition.interimResults = true;
                recognition.maxAlternatives = 1;

                recognition.onstart = () => {{
                    transcriptFinal = "";
                    isListening = true;
                    trigger.disabled = true;
                    trigger.style.display = "none";
                    statusEl.style.display = "block";
                    statusEl.textContent = "Listening...";
                }};

                recognition.onresult = (event) => {{
                    let interim = "";
                    for (let i = event.resultIndex; i < event.results.length; i += 1) {{
                        const piece = event.results[i][0].transcript;
                        if (event.results[i].isFinal) {{
                            transcriptFinal += piece + " ";
                        }} else {{
                            interim += piece;
                        }}
                    }}
                    statusEl.textContent = (transcriptFinal + interim).trim() || "Listening...";
                }};

                recognition.onspeechend = () => {{
                    recognition.stop();
                }};

                recognition.onerror = (event) => {{
                    if (event.error === "not-allowed") {{
                        resetButton("Microphone permission denied.");
                        return;
                    }}
                    if (event.error === "no-speech") {{
                        resetButton("No speech detected. Try again.");
                        return;
                    }}
                    resetButton(`Voice recognition error: ${{event.error}}`);
                }};

                recognition.onend = () => {{
                    const finalText = transcriptFinal.trim();
                    if (finalText) {{
                        writeTranscript(finalText);
                        resetButton("Voice captured. You can edit the text before submitting.");
                    }} else if (isListening) {{
                        resetButton("No speech captured. Try again.");
                    }}
                }};

                trigger.addEventListener("click", () => {{
                    transcriptFinal = "";
                    statusEl.style.display = "none";
                    try {{
                        recognition.start();
                    }} catch (error) {{
                        resetButton("Voice input is already active.");
                    }}
                }});
            }}
        </script>
        </body>
        </html>
        """,
        height=82,
    )


def render_timer_widget(question_id: str, deadline_at: float) -> None:
    remaining = max(0, int(deadline_at - time.time()))
    remaining_ms = max(0, int((deadline_at - time.time()) * 1000))
    components.html(
        f"""
        <html>
        <body style="margin:0;background:transparent;overflow:hidden;">
        <div style="
            padding:1rem 1rem 0.95rem;
            border-radius:20px;
            background:linear-gradient(180deg, rgba(17, 26, 52, 0.84), rgba(10, 17, 35, 0.76));
            border:1px solid rgba(255,255,255,0.08);
            font-family:system-ui, sans-serif;
            color:#f1f6ff;
        ">
            <div style="font-size:0.76rem; letter-spacing:0.12em; text-transform:uppercase; color:#9caccc;">
                Timer
            </div>
            <div id="timer-value" style="font-size:2rem; font-weight:800; margin-top:0.35rem;">
                {remaining}s
            </div>
            <div id="timer-note" style="color:#b8c8e5; font-size:0.88rem; margin-top:0.25rem;">
                60-second response window
            </div>
            <div style="margin-top:0.9rem; height:10px; width:100%; background:rgba(255,255,255,0.08); border-radius:999px; overflow:hidden;">
                <div id="timer-fill" style="
                    height:100%;
                    width:{(remaining / QUESTION_TIME_LIMIT) * 100:.2f}%;
                    border-radius:999px;
                    background:linear-gradient(90deg, #4cc9f0, #8b5cf6);
                    box-shadow:0 0 18px rgba(76, 201, 240, 0.42);
                "></div>
            </div>
        </div>
        <script>
            const questionId = "{question_id}";
            const deadline = Date.now() + {remaining_ms};
            const timerValue = document.getElementById("timer-value");
            const timerFill = document.getElementById("timer-fill");
            const timerNote = document.getElementById("timer-note");
            const submitLockKey = "__ai_timeout_submit_" + questionId;

            function findSubmitButton() {{
                const buttons = Array.from(window.parent.document.querySelectorAll("button"));
                return buttons.find((button) => button.innerText && button.innerText.trim() === "Submit");
            }}

            function tick() {{
                const now = Date.now();
                const remainingMs = Math.max(0, deadline - now);
                const seconds = Math.ceil(remainingMs / 1000);
                const width = Math.max(0, Math.min(100, (remainingMs / ({QUESTION_TIME_LIMIT} * 1000)) * 100));

                timerValue.innerText = `${{seconds}}s`;
                timerFill.style.width = `${{width}}%`;

                if (remainingMs <= 0) {{
                    timerValue.innerText = "0s";
                    timerNote.innerText = "Time is up! Auto-submitting...";
                    if (!window.parent[submitLockKey]) {{
                        window.parent[submitLockKey] = true;
                        const submitButton = findSubmitButton();
                        if (submitButton) {{
                            submitButton.click();
                        }}
                    }}
                    return true;
                }}
                return false;
            }}

            tick();
            const intervalId = setInterval(() => {{
                const finished = tick();
                if (finished) {{
                    clearInterval(intervalId);
                }}
            }}, 1000);
        </script>
        </body>
        </html>
        """,
        height=170,
    )


def render_stats_panel(question: Question) -> None:
    total = steps_total()
    answered = len(st.session_state.answers)
    metric_cards: List[str] = []
    for label, value in [
        ("Current Score", str(st.session_state.score)),
        ("Difficulty", question.difficulty.title()),
        ("Progress", f"{st.session_state.current_question_index}/{total}"),
    ]:
        metric_cards.append(
            (
                f'<div class="metric-card">'
                f'<div class="metric-label">{label}</div>'
                f'<div class="metric-value">{value}</div>'
                f"</div>"
            )
        )

    stats_panel_html = (
        '<div class="glass-card">'
        '<div class="section-title">Live Stats</div>'
        f"<p class='muted-note' style='margin-bottom:0.8rem;'>Semester: {st.session_state.current_semester} (VTU)<br>Questions are adapted to your level.</p>"
        '<div class="metric-stack">'
        + "".join(metric_cards)
        + "</div></div>"
    )
    st.markdown(stats_panel_html, unsafe_allow_html=True)

    if st.session_state.deadline_at:
        render_timer_widget(question.id, st.session_state.deadline_at)

    st.progress(
        min(st.session_state.current_question_index / max(1, total), 1.0),
        text=f"Question {st.session_state.current_question_index} of {total}",
    )
    st.markdown(
        f"<p class='muted-note'>Answered: {answered} | Remaining: {max(total - answered, 0)}</p>",
        unsafe_allow_html=True,
    )


def render_feedback_card() -> None:
    record = st.session_state.last_feedback
    if not record:
        return

    evaluation: EvaluationResult = record["evaluation"]
    status_label = "Timed Out" if record["timed_out"] else "Skipped" if record["skipped"] else "Submitted"

    st.markdown('<div class="glass-card feedback-card">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="feedback-title">Latest Feedback</div>
        <div class="chip" style="margin-bottom:0.85rem;">{status_label} | Score {evaluation.points_awarded}/{evaluation.max_points}</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("**Strengths**")
    if evaluation.reason:
        st.markdown(
            "<ul class='feedback-list'>"
            + "".join(f"<li>{item}</li>" for item in evaluation.reason)
            + "</ul>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("<p class='muted-note'>No positive signals recorded for this answer.</p>", unsafe_allow_html=True)

    st.markdown("**Weaknesses**")
    if evaluation.missing_points:
        st.markdown(
            "<ul class='feedback-list'>"
            + "".join(f"<li>{item}</li>" for item in evaluation.missing_points)
            + "</ul>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("<p class='muted-note'>No major gaps detected.</p>", unsafe_allow_html=True)

    suggestion = evaluation.missing_points[0] if evaluation.missing_points else "Keep the same structure and confidence."
    st.markdown("**Suggestion**")
    st.markdown(f"<p class='muted-note'>{suggestion}</p>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_interviewer_message() -> None:
    message = st.session_state.interviewer_message
    if not message:
        return
    st.markdown(
        f"""
        <div class="glass-card interviewer-card">
            <div class="interviewer-label">
                <span class="interviewer-dot"></span>
                <span>Interviewer</span>
            </div>
            <p class="interviewer-copy">{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_answer_panel(question: Question) -> None:
    disabled = st.session_state.controls_disabled

    st.markdown('<div class="section-title">Your Answer</div>', unsafe_allow_html=True)

    st.text_area(
        "Your answer",
        key="answer_input",
        placeholder="Write a clear and structured answer here, or use the voice button to dictate it...",
        height=220,
        label_visibility="collapsed",
        disabled=disabled,
    )

    submit_col, skip_col, voice_col = st.columns([1, 1, 1.15], gap="small")
    with submit_col:
        submit_clicked = st.button("Submit", use_container_width=True, disabled=disabled)
    with skip_col:
        skip_clicked = st.button("Skip", use_container_width=True, disabled=disabled)
    with voice_col:
        render_voice_button(question.id)

    st.markdown(
        "<p class='muted-note button-note'>Voice input uses your browser microphone, fills the answer box automatically, "
        "and still lets you edit the text before submitting.</p>",
        unsafe_allow_html=True,
    )

    if submit_clicked:
        if st.session_state.deadline_at and time.time() >= st.session_state.deadline_at:
            process_answer("timeout")
        else:
            answer = st.session_state.answer_input.strip()
            if answer:
                process_answer("submit", answer)
            else:
                set_notification("warning", "Please enter an answer or use Skip.")
        st.rerun()

    if skip_clicked:
        process_answer("skip")
        st.rerun()


def render_interview_panel() -> None:
    question = current_question()
    if question is None:
        return

    total = steps_total()
    st.progress(progress_ratio(), text=f"Interview progress: {len(st.session_state.answers)} / {total}")

    left_col, right_col = st.columns([2.25, 1.0], gap="large")
    with left_col:
        render_interviewer_message()
        render_question_card(question)
        render_answer_panel(question)
        render_feedback_card()

    with right_col:
        render_stats_panel(question)


def render_final_screen() -> None:
    report = build_report(st.session_state.answers)

    st.markdown(
        """
        <div class="glass-card">
            <div class="section-title">Interview Complete</div>
            <div class="summary-grid">
        """,
        unsafe_allow_html=True,
    )
    for label, value in [
        ("Total Score", f"{report['total_score']}/{report['total_possible']}"),
        ("Average Score", f"{report['average_score']:.1f}/10"),
        ("Average Time", f"{report['average_time']:.1f}s"),
        ("Skipped", str(report["skipped_count"])),
        ("Timed Out", str(report["timed_out_count"])),
    ]:
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.markdown("**Strengths**")
        for item in report["strengths"]:
            st.markdown(f"- {item}")
        st.markdown("**Speed Summary**")
        st.markdown(f"- Fastest: {report['fastest']}")
        st.markdown(f"- Slowest: {report['slowest']}")

    with col_b:
        st.markdown("**Weaknesses**")
        for item in report["weaknesses"]:
            st.markdown(f"- {item}")
        st.markdown("**Suggestions**")
        for item in report["suggestions"]:
            st.markdown(f"- {item}")

    st.markdown(report["skip_summary"])

    if st.button("Start New Interview", type="primary", use_container_width=True):
        start_interview(st.session_state.mode, st.session_state.degree, int(st.session_state.current_semester))
        st.rerun()


def handle_timeout_if_needed() -> None:
    if not st.session_state.interview_started or st.session_state.completed:
        return

    if st.session_state.controls_disabled:
        return

    deadline_at = st.session_state.deadline_at
    if deadline_at and time.time() >= deadline_at:
        process_answer("timeout")
        st.rerun()


def main() -> None:
    st.set_page_config(
        page_title="AI Interview Simulator",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    inject_css()
    inject_responsive_controller()
    init_session_state()
    reset_answer_input_if_needed()
    handle_timeout_if_needed()

    render_landing_background(not st.session_state.interview_started)
    render_title()
    render_notification()

    if not st.session_state.interview_started:
        render_landing()
        return

    if st.session_state.completed or current_question() is None:
        render_feedback_card()
        render_final_screen()
        return

    render_interview_panel()


if __name__ == "__main__":
    main()
