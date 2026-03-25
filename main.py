from __future__ import annotations

import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from decision_engine import DecisionEngine
from evaluator import (
    EvaluationResult,
    build_special_evaluation,
    evaluate_answer,
    format_question_feedback,
)
from questions import InterviewMode, Question, get_questions_by_id
from timer import timed_text_input
from voice import capture_voice_input, voice_input_available

QUESTION_TIME_LIMIT = 60


@dataclass
class AnswerRecord:
    question: Question
    answer: str
    evaluation: EvaluationResult
    passed: bool
    time_taken: float
    skipped: bool = False
    timed_out: bool = False
    input_mode: str = "text"


@dataclass
class FinalReport:
    total_score: int
    total_possible: int
    average_score: float
    average_response_time: float
    fastest_answer: str
    slowest_answer: str
    skipped_questions_count: int
    timed_out_count: int
    skipped_question_labels: Sequence[str]
    rating: str
    strengths: Sequence[str]
    weaknesses: Sequence[str]
    improvement_suggestions: Sequence[str]
    speed_accuracy_suggestion: str


@dataclass
class CollectedAnswer:
    answer: str
    time_taken: float
    timed_out: bool
    input_mode: str


def _rating_from_average(average_score: float) -> str:
    if average_score >= 8.5:
        return "Excellent"
    if average_score >= 7.0:
        return "Strong"
    if average_score >= 5.5:
        return "Good"
    return "Developing"


def _select_strengths_and_weaknesses(
    topic_averages: Dict[str, float],
) -> tuple[List[str], List[str]]:
    ordered_topics = sorted(topic_averages.items(), key=lambda item: (-item[1], item[0]))
    strengths = [topic for topic, score in ordered_topics if score >= 7.5]
    weaknesses = [topic for topic, score in ordered_topics if score < 6.0]

    if not strengths and ordered_topics:
        strengths = [ordered_topics[0][0]]
    if not weaknesses and len(ordered_topics) > 1:
        weaknesses = [ordered_topics[-1][0]]

    strengths = [topic for topic in strengths if topic not in weaknesses]
    return strengths[:3], weaknesses[:3]


def _question_label(question: Question) -> str:
    short_prompt = question.prompt
    if len(short_prompt) > 55:
        short_prompt = short_prompt[:52] + "..."
    return f"{question.topic} - {short_prompt}"


def _speed_accuracy_suggestion(average_response_time: float, average_score: float) -> str:
    if average_response_time > 45:
        return "Practice giving a first structured answer faster so you stay safe inside the 60-second limit."
    if average_response_time < 20 and average_score < 6:
        return "Slow down slightly and add one clear example or tradeoff to improve answer accuracy."
    return "Keep balancing speed and accuracy with short, structured answers."


def _build_final_report(records: List[AnswerRecord]) -> FinalReport:
    total_score = sum(record.evaluation.points_awarded for record in records)
    total_possible = sum(record.evaluation.max_points for record in records)
    average_score = total_score / len(records) if records else 0.0
    average_response_time = sum(record.time_taken for record in records) / len(records) if records else 0.0
    rating = _rating_from_average(average_score)

    topic_scores: Dict[str, List[int]] = defaultdict(list)
    topic_gaps: Dict[str, List[str]] = defaultdict(list)

    for record in records:
        if record.skipped:
            continue
        topic_scores[record.question.topic].append(record.evaluation.points_awarded)
        topic_gaps[record.question.topic].extend(record.evaluation.missing_points)

    topic_averages = {
        topic: sum(scores) / len(scores)
        for topic, scores in topic_scores.items()
    }
    strengths, weaknesses = _select_strengths_and_weaknesses(topic_averages)

    improvement_suggestions: List[str] = []
    for topic in weaknesses:
        common_gap = Counter(topic_gaps[topic]).most_common(1)
        if common_gap:
            improvement_suggestions.append(f"{topic}: {common_gap[0][0]}")
        else:
            improvement_suggestions.append(
                f"{topic}: Add clearer structure, more topic-specific terms, and a concrete example."
            )

    if not improvement_suggestions:
        improvement_suggestions.append(
            "Keep practicing complete answers with clear reasoning, examples, and tradeoffs."
        )

    skipped_records = [record for record in records if record.skipped]
    timed_out_count = sum(1 for record in records if record.timed_out)
    fastest_record = min(records, key=lambda record: record.time_taken)
    slowest_record = max(records, key=lambda record: record.time_taken)

    return FinalReport(
        total_score=total_score,
        total_possible=total_possible,
        average_score=average_score,
        average_response_time=average_response_time,
        fastest_answer=f"{_question_label(fastest_record.question)} ({fastest_record.time_taken:.1f}s)",
        slowest_answer=f"{_question_label(slowest_record.question)} ({slowest_record.time_taken:.1f}s)",
        skipped_questions_count=len(skipped_records),
        timed_out_count=timed_out_count,
        skipped_question_labels=[_question_label(record.question) for record in skipped_records],
        rating=rating,
        strengths=strengths,
        weaknesses=weaknesses,
        improvement_suggestions=improvement_suggestions,
        speed_accuracy_suggestion=_speed_accuracy_suggestion(average_response_time, average_score),
    )


def _print_final_report(report: FinalReport, engine: DecisionEngine) -> None:
    print("\nFinal Report")
    print("=" * 80)
    print(f"Total score: {report.total_score}/{report.total_possible}")
    print(f"Average score: {report.average_score:.1f}/10")
    print(f"Average response time: {report.average_response_time:.1f}s")
    print(f"Fastest answer: {report.fastest_answer}")
    print(f"Slowest answer: {report.slowest_answer}")
    print(f"Skipped questions: {report.skipped_questions_count}")
    print(f"You skipped {report.skipped_questions_count} questions.")
    print(f"Timed out questions: {report.timed_out_count}")
    print(f"Overall rating: {report.rating}")

    strengths = ", ".join(report.strengths) if report.strengths else "No clear strengths identified yet"
    weaknesses = ", ".join(report.weaknesses) if report.weaknesses else "No major weak areas identified"
    print(f"Strengths: {strengths}")
    print(f"Weaknesses: {weaknesses}")

    if report.skipped_question_labels:
        print("Skipped question details:")
        for label in report.skipped_question_labels:
            print(f"- {label}")

    if engine.state.difficulty_history:
        print(f"Difficulty path: {' -> '.join(engine.state.difficulty_history)}")

    print("Improvement suggestions:")
    for suggestion in report.improvement_suggestions:
        print(f"- {suggestion}")
    print(f"Speed/accuracy suggestion: {report.speed_accuracy_suggestion}")


def _ask_voice_mode() -> bool:
    voice_choice = input("Enable voice input mode? [y/N]: ").strip().lower()
    if voice_choice not in {"y", "yes"}:
        return False

    if not voice_input_available():
        print("Voice mode requested, but speech_recognition is not installed. Using text input instead.")
        return False

    return True


def _collect_answer(use_voice: bool) -> CollectedAnswer:
    prompt = "Your answer (type `skip` to skip, `quit` to stop):"
    overall_start = time.monotonic()

    if use_voice:
        voice_result = capture_voice_input(time_limit=QUESTION_TIME_LIMIT)
        total_elapsed = min(time.monotonic() - overall_start, float(QUESTION_TIME_LIMIT))

        if voice_result.used_voice and voice_result.answer:
            return CollectedAnswer(
                answer=voice_result.answer,
                time_taken=total_elapsed,
                timed_out=voice_result.timed_out,
                input_mode="voice",
            )

        if voice_result.timed_out or total_elapsed >= QUESTION_TIME_LIMIT:
            return CollectedAnswer(
                answer="",
                time_taken=float(QUESTION_TIME_LIMIT),
                timed_out=True,
                input_mode="voice",
            )

        if voice_result.error:
            print(f"Voice fallback: {voice_result.error}")

        remaining = int(QUESTION_TIME_LIMIT - total_elapsed)
        if remaining <= 0:
            return CollectedAnswer(
                answer="",
                time_taken=float(QUESTION_TIME_LIMIT),
                timed_out=True,
                input_mode="voice",
            )

        text_result = timed_text_input(prompt=prompt, time_limit=remaining)
        total_time = min(time.monotonic() - overall_start, float(QUESTION_TIME_LIMIT))
        return CollectedAnswer(
            answer=text_result.answer,
            time_taken=total_time,
            timed_out=text_result.timed_out,
            input_mode="text-fallback",
        )

    text_result = timed_text_input(prompt=prompt, time_limit=QUESTION_TIME_LIMIT)
    return CollectedAnswer(
        answer=text_result.answer,
        time_taken=text_result.time_taken,
        timed_out=text_result.timed_out,
        input_mode="text",
    )


def _status_text(record: AnswerRecord, threshold: float) -> str:
    if record.skipped:
        return "Skipped"
    if record.timed_out:
        return "Timed out"
    if record.passed:
        return f"Pass for {record.question.difficulty} threshold ({threshold * 100:.0f}%)"
    return f"Below target for {record.question.difficulty} threshold ({threshold * 100:.0f}%)"


def run_interview() -> None:
    print("Select interview mode: technical | hr | mixed")
    mode_input = input("Mode [technical]: ").strip().lower()
    if mode_input not in {"", "technical", "hr", "mixed"}:
        print("Unknown mode. Defaulting to technical.")
        mode_input = "technical"

    if mode_input == "hr":
        mode: InterviewMode = "hr"
    elif mode_input == "mixed":
        mode = "mixed"
    else:
        mode = "technical"

    use_voice = _ask_voice_mode()

    questions_by_id = get_questions_by_id(mode=mode)
    engine = DecisionEngine(mode=mode, questions_by_id=questions_by_id)

    print(f"AI Interview Simulator ({mode} mode, adaptive difficulty)")
    print(f"Each question has a {QUESTION_TIME_LIMIT}-second time limit.")
    print("Type `skip` to skip a question or `quit` to stop the interview.\n")

    records: List[AnswerRecord] = []
    last_eval: Optional[EvaluationResult] = None

    for step in range(1, engine.steps_total + 1):
        question_id = engine.get_next_question_id(last_eval)
        question = questions_by_id[question_id]
        question_type_label = "HR Question" if question.type == "hr" else "Technical Question"

        print(
            f"Question {step}/{engine.steps_total} "
            f"({question_type_label} | {question.difficulty} | {question.topic}): {question.prompt}"
        )

        collected = _collect_answer(use_voice=use_voice)
        answer = collected.answer.strip()
        normalized_answer = answer.lower()

        if normalized_answer in {"quit", "exit"}:
            break

        skipped = normalized_answer == "skip"
        timed_out = collected.timed_out

        if timed_out:
            evaluation = build_special_evaluation(question, status="timeout")
        elif skipped:
            evaluation = build_special_evaluation(question, status="skip")
        else:
            evaluation = evaluate_answer(question, answer)

        threshold = engine.pass_thresholds[question.difficulty]
        passed = evaluation.passed(threshold)

        record = AnswerRecord(
            question=question,
            answer=answer,
            evaluation=evaluation,
            passed=passed,
            time_taken=collected.time_taken,
            skipped=skipped,
            timed_out=timed_out,
            input_mode=collected.input_mode,
        )
        records.append(record)

        print(
            f"\nResult: {evaluation.points_awarded}/{evaluation.max_points} "
            f"({evaluation.normalized_score * 100:.1f}%) | "
            f"{_status_text(record, threshold)}"
        )
        print(f"Input mode: {record.input_mode}")
        print(f"Time taken: {record.time_taken:.1f}s")
        print(format_question_feedback(question, evaluation))
        print("\n" + "-" * 80 + "\n")

        last_eval = evaluation

    if not records:
        print("No answers provided. Exiting.")
        return

    report = _build_final_report(records)
    _print_final_report(report, engine)


if __name__ == "__main__":
    run_interview()
