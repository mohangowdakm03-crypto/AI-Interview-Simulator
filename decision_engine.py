from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Set

from evaluator import EvaluationResult
from questions import (
    Difficulty,
    InterviewMode,
    Question,
    difficulty_targets_for_semester,
    get_all_questions,
    get_questions_by_id,
    question_matches_semester,
)

DIFFICULTY_ORDER: Sequence[Difficulty] = ("easy", "medium", "hard")


@dataclass
class InterviewState:
    step: int = 0
    current_difficulty: Difficulty = "easy"
    asked_question_ids: Set[str] = field(default_factory=set)
    difficulty_history: List[Difficulty] = field(default_factory=list)
    score_history: List[float] = field(default_factory=list)
    total_points_awarded: int = 0
    total_max_points: int = 0
    last_question_id: Optional[str] = None
    last_evaluated_question_id: Optional[str] = None
    last_evaluation: Optional[EvaluationResult] = None


class DecisionEngine:
    """
    Adaptive question selector with smooth difficulty transitions.

    Rules:
    - Start at easy.
    - Promote one level when the latest score meets the threshold for the
      current difficulty.
    - Demote one level when the latest score is clearly low.
    - Otherwise stay on the same difficulty.
    - Never repeat a question.
    - Prefer topic variety when several questions are available.
    - Timeout cases can feed in as low-score evaluations from main.py.
    - Skipped questions stay separate and do not push difficulty downward.
    """

    def __init__(
        self,
        mode: InterviewMode = "technical",
        questions_by_id: Optional[Dict[str, Question]] = None,
        pass_thresholds: Optional[Dict[Difficulty, float]] = None,
        low_score_thresholds: Optional[Dict[Difficulty, float]] = None,
        steps_total: int = 10,
        random_seed: Optional[int] = None,
        current_semester: int = 4,
        degree: str = "BE",
    ) -> None:
        self.mode = mode
        self.current_semester = max(1, min(8, int(current_semester)))
        self.degree = degree
        self.questions_by_id = questions_by_id or get_questions_by_id(mode=mode)
        self._rng = random.Random(random_seed)
        all_questions: List[Question] = [
            question
            for question in get_all_questions(mode=mode)
            if question.id in self.questions_by_id and question_matches_semester(question, self.current_semester)
        ]
        self.pass_thresholds: Dict[Difficulty, float] = pass_thresholds or {
            "easy": 0.6,
            "medium": 0.7,
            "hard": 0.8,
        }
        self.low_score_thresholds: Dict[Difficulty, float] = low_score_thresholds or {
            "easy": 0.35,
            "medium": 0.4,
            "hard": 0.5,
        }
        self.state = InterviewState()
        self._steps_total = min(steps_total, len(all_questions))
        self.questions = self._select_interview_pool(all_questions=all_questions, steps_total=self._steps_total)
        self._question_order = {question.id: index for index, question in enumerate(self.questions)}
        self._questions_by_difficulty: Dict[Difficulty, List[Question]] = {
            difficulty: [question for question in self.questions if question.difficulty == difficulty]
            for difficulty in DIFFICULTY_ORDER
        }

    @property
    def steps_total(self) -> int:
        return self._steps_total

    def _difficulty_index(self, difficulty: Difficulty) -> int:
        return DIFFICULTY_ORDER.index(difficulty)

    def _shift_difficulty(self, difficulty: Difficulty, shift: int) -> Difficulty:
        next_index = min(
            len(DIFFICULTY_ORDER) - 1,
            max(0, self._difficulty_index(difficulty) + shift),
        )
        return DIFFICULTY_ORDER[next_index]

    def _next_target_difficulty(self, question_difficulty: Difficulty, score: float) -> Difficulty:
        promote_threshold = self.pass_thresholds[question_difficulty]
        demote_threshold = self.low_score_thresholds[question_difficulty]

        if score >= promote_threshold:
            return self._shift_difficulty(question_difficulty, 1)
        if score <= demote_threshold:
            return self._shift_difficulty(question_difficulty, -1)
        return question_difficulty

    def _difficulty_search_order(self, target: Difficulty) -> List[Difficulty]:
        if target == "easy":
            return ["easy", "medium", "hard"]
        if target == "medium":
            return ["medium", "easy", "hard"]
        return ["hard", "medium", "easy"]

    def _balanced_target_counts(self, all_questions: Sequence[Question], steps_total: int) -> Dict[Difficulty, int]:
        availability = {
            difficulty: sum(1 for question in all_questions if question.difficulty == difficulty)
            for difficulty in DIFFICULTY_ORDER
        }
        counts: Dict[Difficulty, int] = {difficulty: 0 for difficulty in DIFFICULTY_ORDER}

        base = steps_total // len(DIFFICULTY_ORDER)
        remainder = steps_total % len(DIFFICULTY_ORDER)

        for difficulty in DIFFICULTY_ORDER:
            counts[difficulty] = min(base, availability[difficulty])

        for difficulty in DIFFICULTY_ORDER[:remainder]:
            if counts[difficulty] < availability[difficulty]:
                counts[difficulty] += 1

        remaining = steps_total - sum(counts.values())
        while remaining > 0:
            progressed = False
            for difficulty in DIFFICULTY_ORDER:
                if counts[difficulty] < availability[difficulty]:
                    counts[difficulty] += 1
                    remaining -= 1
                    progressed = True
                    if remaining == 0:
                        break
            if not progressed:
                break

        return counts

    def _difficulty_fill_order(self) -> List[Difficulty]:
        if self.current_semester <= 2:
            return ["easy", "medium", "hard"]
        if self.current_semester <= 4:
            return ["easy", "medium", "hard"]
        return ["medium", "hard", "easy"]

    def _rebalance_target_counts(
        self,
        questions: Sequence[Question],
        target_counts: Dict[Difficulty, int],
        steps_total: int,
    ) -> Dict[Difficulty, int]:
        availability = {
            difficulty: sum(1 for question in questions if question.difficulty == difficulty)
            for difficulty in DIFFICULTY_ORDER
        }
        counts: Dict[Difficulty, int] = {
            difficulty: min(target_counts.get(difficulty, 0), availability[difficulty])
            for difficulty in DIFFICULTY_ORDER
        }

        remaining = steps_total - sum(counts.values())
        fill_order = self._difficulty_fill_order()
        while remaining > 0:
            progressed = False
            for difficulty in fill_order:
                if counts[difficulty] < availability[difficulty]:
                    counts[difficulty] += 1
                    remaining -= 1
                    progressed = True
                    if remaining == 0:
                        break
            if not progressed:
                break

        return counts

    def _select_interview_pool(self, all_questions: Sequence[Question], steps_total: int) -> List[Question]:
        """
        Choose a fresh interview pool for the session.

        The pool is random, balanced across easy/medium/hard as evenly as
        possible, and then shuffled so different interviews feel distinct.
        """
        if self.mode == "mixed":
            return self._select_mixed_interview_pool(all_questions=all_questions, steps_total=steps_total)

        target_counts = self._rebalance_target_counts(
            questions=all_questions,
            target_counts=difficulty_targets_for_semester(self.current_semester, steps_total),
            steps_total=steps_total,
        )
        selected_questions: List[Question] = []

        for difficulty in DIFFICULTY_ORDER:
            difficulty_questions = [
                question for question in all_questions if question.difficulty == difficulty
            ]
            sample_size = target_counts[difficulty]
            if sample_size <= 0:
                continue
            selected_questions.extend(self._rng.sample(difficulty_questions, sample_size))

        self._rng.shuffle(selected_questions)
        return selected_questions

    def _select_mixed_interview_pool(self, all_questions: Sequence[Question], steps_total: int) -> List[Question]:
        technical_questions = [question for question in all_questions if question.type == "technical"]
        hr_questions = [question for question in all_questions if question.type == "hr"]

        technical_count = steps_total // 2
        hr_count = steps_total // 2
        if steps_total % 2 == 1:
            technical_count += 1

        technical_targets = self._rebalance_target_counts(
            questions=technical_questions,
            target_counts=difficulty_targets_for_semester(self.current_semester, technical_count),
            steps_total=technical_count,
        )
        hr_targets = self._rebalance_target_counts(
            questions=hr_questions,
            target_counts=difficulty_targets_for_semester(self.current_semester, hr_count),
            steps_total=hr_count,
        )

        selected_questions: List[Question] = []
        for difficulty in DIFFICULTY_ORDER:
            if technical_targets[difficulty] > 0:
                candidates = [question for question in technical_questions if question.difficulty == difficulty]
                selected_questions.extend(self._rng.sample(candidates, technical_targets[difficulty]))
            if hr_targets[difficulty] > 0:
                candidates = [question for question in hr_questions if question.difficulty == difficulty]
                selected_questions.extend(self._rng.sample(candidates, hr_targets[difficulty]))

        return selected_questions

    def _expected_question_type(self) -> Optional[str]:
        if self.mode != "mixed":
            return None
        return "technical" if self.state.step % 2 == 0 else "hr"

    def _apply_last_evaluation(self, last_evaluation: Optional[EvaluationResult]) -> None:
        last_question_id = self.state.last_question_id
        if last_evaluation is None or last_question_id is None:
            return
        if self.state.last_evaluated_question_id == last_question_id:
            return

        last_question = self.questions_by_id[last_question_id]
        self.state.last_evaluation = last_evaluation
        self.state.last_evaluated_question_id = last_question_id
        self.state.total_points_awarded += last_evaluation.points_awarded
        self.state.total_max_points += last_evaluation.max_points

        if last_evaluation.response_status == "skipped":
            return

        self.state.score_history.append(last_evaluation.normalized_score)
        self.state.current_difficulty = self._next_target_difficulty(
            question_difficulty=last_question.difficulty,
            score=last_evaluation.normalized_score,
        )

    def _topic_counts(self) -> Counter[str]:
        asked_topics = [
            self.questions_by_id[question_id].topic
            for question_id in self.state.asked_question_ids
            if question_id in self.questions_by_id
        ]
        return Counter(asked_topics)

    def _select_best_question(self, candidates: Sequence[Question]) -> Question:
        if not candidates:
            raise ValueError("No candidate questions available to select from.")

        topic_counts = self._topic_counts()
        last_topic = None
        if self.state.last_question_id and self.state.last_question_id in self.questions_by_id:
            last_topic = self.questions_by_id[self.state.last_question_id].topic

        return min(
            candidates,
            key=lambda question: (
                question.topic == last_topic,
                topic_counts[question.topic],
                self._question_order[question.id],
            ),
        )

    def _pick_question_for_difficulty(self, target_difficulty: Difficulty) -> Question:
        expected_type = self._expected_question_type()
        for difficulty in self._difficulty_search_order(target_difficulty):
            available = [
                question
                for question in self._questions_by_difficulty[difficulty]
                if question.id not in self.state.asked_question_ids
            ]
            if expected_type is not None:
                preferred_type_questions = [
                    question for question in available if question.type == expected_type
                ]
                if preferred_type_questions:
                    return self._select_best_question(preferred_type_questions)
            if available:
                return self._select_best_question(available)
        raise ValueError("No unasked questions remain in the question bank.")

    def get_next_question_id(self, last_evaluation: Optional[EvaluationResult] = None) -> str:
        """
        Return the next question id using the latest evaluation as the signal.

        Difficulty moves at most one level per step, which keeps transitions
        smooth while still adapting to performance.
        """
        if self.state.step >= self.steps_total:
            raise ValueError("All interview steps have already been consumed.")

        self._apply_last_evaluation(last_evaluation)

        next_question = self._pick_question_for_difficulty(self.state.current_difficulty)
        self.state.step += 1
        self.state.current_difficulty = next_question.difficulty
        self.state.last_question_id = next_question.id
        self.state.asked_question_ids.add(next_question.id)
        self.state.difficulty_history.append(next_question.difficulty)
        return next_question.id
