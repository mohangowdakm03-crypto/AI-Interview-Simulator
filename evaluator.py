from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Dict, List, Literal, Sequence, Tuple

from questions import Question

# Canonical concept aliases to reduce strict keyword dependency.
SYNONYM_MAP: Dict[str, Sequence[str]] = {
    "lifo": (
        "last in first out",
        "last-in first-out",
        "last item comes out first",
    ),
    "fifo": (
        "first in first out",
        "first-in first-out",
        "first item comes out first",
    ),
    "vector": (
        "numerical representation",
        "dense representation",
        "embedding vector",
        "feature vector",
        "coordinate representation",
    ),
    "embeddings": (
        "vector representation",
        "numeric representation",
        "semantic representation",
    ),
    "retrieval": (
        "search",
        "document lookup",
        "fetch relevant documents",
    ),
    "generation": (
        "response creation",
        "text generation",
        "answer synthesis",
    ),
    "overfitting": (
        "memorization",
        "poor generalization",
        "fits training noise",
    ),
    "generalization": (
        "performance on unseen data",
        "out of sample performance",
        "transfer to new data",
    ),
    "leakage": (
        "data contamination",
        "information leak",
        "train test contamination",
    ),
    "guardrails": (
        "safety controls",
        "constraints",
        "policy checks",
    ),
    "metrics": (
        "measurement",
        "evaluation criteria",
        "quality indicators",
    ),
    "monitor": (
        "observability",
        "tracking",
        "monitoring",
    ),
    "encapsulation": (
        "data hiding",
        "controlled access",
    ),
    "inheritance": (
        "reuse behavior",
        "base class",
        "derived class",
    ),
    "asyncio": (
        "event loop",
        "async programming",
    ),
    "multiprocessing": (
        "multiple processes",
        "parallel workers",
    ),
    "ownership": (
        "taking responsibility",
        "own the outcome",
    ),
    "prioritize": (
        "rank tasks",
        "decide order",
    ),
    "pointer": (
        "stores an address",
        "memory address reference",
        "points to a memory location",
    ),
    "recursion": (
        "function calling itself",
        "self call",
        "recursive call",
    ),
    "iteration": (
        "repeating with a loop",
        "loop based repetition",
        "repeated steps",
    ),
    "big o": (
        "big oh",
        "order of growth",
        "growth rate",
    ),
    "process": (
        "program in execution",
        "running program",
    ),
    "thread": (
        "lightweight execution unit",
        "smaller execution flow",
    ),
    "join": (
        "combine tables",
        "merge rows from tables",
        "bring related table data together",
    ),
    "primary key": (
        "unique identifier",
        "uniquely identifies a row",
    ),
    "foreign key": (
        "reference to another table",
        "links one table to another",
        "referential link",
    ),
}


def _build_alias_to_canonical() -> Dict[str, str]:
    alias_to_canonical: Dict[str, str] = {}
    for canonical, aliases in SYNONYM_MAP.items():
        for alias in aliases:
            alias_to_canonical[alias] = canonical
    return alias_to_canonical


ALIAS_TO_CANONICAL: Dict[str, str] = _build_alias_to_canonical()

WEIGHTED_RUBRICS: Dict[str, Sequence[str]] = {
    "q2_overfitting": (
        "defines overfitting as memorizing noise or training specific patterns",
        "explains weaker performance on unseen data or poor generalization",
        "mentions at least one prevention technique such as regularization dropout or early stopping",
        "mentions data strategy such as more data augmentation or cross validation",
        "provides clear structured explanation connecting cause and mitigation",
    ),
    "q3_embeddings": (
        "defines embeddings as numerical vector representations",
        "explains semantic closeness or distance in vector space",
        "mentions retrieval search nearest neighbors or ranking use",
        "explains what embeddings represent such as meaning context or features",
        "provides clear structured explanation with an end to end idea",
    ),
    "q11_python_oop": (
        "defines classes and objects clearly",
        "explains how attributes or methods belong to an object design",
        "mentions encapsulation inheritance or another core oop principle",
        "connects oop to code reuse organization or maintainability",
        "provides a practical Python example or real project use",
    ),
    "q4_llm_evaluation": (
        "proposes task specific metrics",
        "describes evaluation dataset split such as test or validation set",
        "mentions human evaluation rubric or error analysis",
        "mentions reliability risks such as hallucination or calibration",
        "provides clear evaluation workflow from data to measurement",
    ),
    "q5_prompt_vs_finetune": (
        "states when to use prompt engineering",
        "states when to use fine tuning",
        "compares data requirements",
        "compares cost or latency tradeoffs",
        "provides clear decision framework with contrast",
    ),
    "q6_data_leakage": (
        "defines data leakage or contamination",
        "explains why leakage inflates offline results or harms true generalization",
        "mentions split hygiene such as no overlap deduplication or strict train test isolation",
        "mentions time aware split strategy when relevant",
        "provides clear prevention workflow",
    ),
    "q7_rag": (
        "defines retrieval augmented generation",
        "mentions retrieval components such as indexing embedding chunking or reranking",
        "mentions generation step using retrieved context",
        "explains why rag helps with grounding freshness or factuality",
        "provides clear pipeline style explanation",
    ),
    "q8_agent_tool_use": (
        "describes tool calling architecture such as planner executor or function schema",
        "mentions loop control safeguards such as step limits timeout or budget",
        "mentions safety controls such as allowlists permission checks or policy filters",
        "mentions verification human approval or fallback behavior",
        "provides clear guardrail strategy balancing utility and safety",
    ),
    "q9_bias_hallucination_mitigation": (
        "explains bias risk in model outputs",
        "explains hallucination risk in model outputs",
        "mentions bias mitigation methods such as debiasing filters or data balancing",
        "mentions hallucination mitigation methods such as grounding retrieval citations or abstention",
        "mentions evaluation strategy to measure improvements",
    ),
    "q10_debug_regression": (
        "describes monitoring and metrics to detect regression",
        "mentions logging and traceability such as prompt model version and context",
        "mentions root cause isolation strategy",
        "mentions safe rollout mitigation such as rollback canary or feature flag",
        "provides clear end to end debugging workflow",
    ),
    "q12_python_concurrency": (
        "distinguishes threading asyncio and multiprocessing",
        "connects each option to io bound or cpu bound workloads",
        "mentions the gil or process level parallelism tradeoff",
        "recommends a suitable choice for an ai workflow example",
        "provides a clear tradeoff based explanation",
    ),
    "h1_self_intro": (
        "introduces background relevant to the role",
        "highlights concrete experience and skills",
        "mentions measurable impact or outcomes",
        "shows clear role fit motivation",
        "communicates in a structured concise narrative",
    ),
    "h2_team_conflict": (
        "describes a real conflict scenario",
        "explains actions taken to resolve conflict",
        "shows communication listening or empathy",
        "mentions outcome and what improved",
        "shares learning applied later",
    ),
    "h3_feedback_response": (
        "describes specific feedback received",
        "shows reflection and accountability",
        "explains concrete improvement actions",
        "mentions measurable or observable result",
        "demonstrates growth mindset",
    ),
    "h11_customer_focus": (
        "describes a real user or customer need",
        "explains how the candidate changed approach based on that signal",
        "mentions feedback evidence or direct observation",
        "reports an outcome for the user business or team",
        "shows empathy and structured communication",
    ),
    "h4_prioritization": (
        "describes prioritization framework",
        "balances urgency and impact",
        "mentions stakeholder communication",
        "explains tradeoff decisions under constraints",
        "shows clear execution plan",
    ),
    "h5_ownership": (
        "identifies problem owned proactively",
        "describes initiative beyond assigned scope",
        "shows collaboration and alignment",
        "explains execution and delivery",
        "mentions impact and lessons learned",
    ),
    "h6_adaptability": (
        "describes late requirement change",
        "explains replanning and adaptation strategy",
        "shows risk management and communication",
        "mentions stakeholder alignment",
        "summarizes outcome quality and timing",
    ),
    "h7_ethics": (
        "identifies quality and ethics tension clearly",
        "explains principled decision framework",
        "mentions risk assessment and mitigation",
        "includes transparency or escalation behavior",
        "balances delivery speed with responsibility",
    ),
    "h8_leadership": (
        "describes leading without formal authority",
        "shows influence strategy and persuasion",
        "mentions alignment and trust building",
        "explains execution through others",
        "reports concrete outcomes",
    ),
    "h9_failure_learning": (
        "describes a meaningful failure",
        "takes responsibility without deflection",
        "explains root cause analysis",
        "details corrective actions",
        "shows durable learning and improved future behavior",
    ),
    "h10_motivation": (
        "explains personal motivation drivers",
        "connects motivation to this role",
        "aligns with long term goals",
        "shows values and impact orientation",
        "communicates realistic growth plan",
    ),
    "h12_strategic_decision": (
        "describes the difficult decision context clearly",
        "explains how incomplete information was handled",
        "mentions tradeoffs risks or decision criteria",
        "includes stakeholder communication or alignment",
        "reports the outcome and lesson learned",
    ),
    "m1_ai_communication": (
        "explains technical concept in plain language",
        "adapts explanation to non technical audience",
        "uses a concrete example",
        "preserves technical correctness",
        "communicates clearly and logically",
    ),
    "m2_precision_business_tradeoff": (
        "defines precision and recall tradeoff",
        "maps tradeoff to business context",
        "explains false positive versus false negative risk",
        "justifies selected metric priority",
        "uses clear comparative reasoning",
    ),
    "m3_collaboration_ml_project": (
        "describes cross functional collaboration model",
        "clarifies requirements and success criteria",
        "explains communication cadence with teams",
        "mentions delivery ownership and handoffs",
        "shows alignment to product outcomes",
    ),
    "m11_python_ai_project": (
        "describes how a small python ai project would be organized",
        "mentions evaluation or testing in the iteration loop",
        "references code structure data flow or logging",
        "shows practical iteration from experiment to improvement",
        "communicates an end to end workflow clearly",
    ),
    "m4_llm_eval_ownership": (
        "identifies immediate triage steps",
        "mentions monitoring metrics and logs",
        "explains root cause isolation approach",
        "includes mitigation such as rollback or guardrails",
        "communicates status to stakeholders clearly",
    ),
    "m5_prompt_iteration": (
        "proposes iterative prompt experimentation",
        "defines lightweight evaluation strategy",
        "considers time cost and latency constraints",
        "prioritizes highest impact experiments",
        "shows clear decision loop from signal to action",
    ),
    "m6_requirement_change": (
        "acknowledges requirement change impact",
        "replans scope timeline and priorities",
        "communicates tradeoffs to stakeholders",
        "manages risk while preserving quality",
        "drives execution with clear next steps",
    ),
    "m7_rag_product_impact": (
        "explains rag concept simply",
        "connects rag to user value",
        "mentions grounding and hallucination reduction",
        "identifies metrics for impact tracking",
        "communicates business and technical tradeoffs",
    ),
    "m8_ai_safety_decision": (
        "frames safety risk and uncertainty explicitly",
        "defines decision process and go no go criteria",
        "includes guardrails and approvals",
        "balances speed with risk mitigation",
        "provides accountable rollout plan",
    ),
    "m9_bias_stakeholder": (
        "responds to fairness concern constructively",
        "uses evidence and evaluation to diagnose bias",
        "proposes mitigation actions",
        "communicates transparently with stakeholders",
        "defines follow up validation plan",
    ),
    "m10_growth_plan": (
        "defines clear ninety day milestones",
        "covers both technical impact and collaboration goals",
        "includes learning and execution strategy",
        "mentions measurable outcomes",
        "shows realistic prioritization and ownership",
    ),
    "m12_rollout_strategy": (
        "defines a staged rollout plan",
        "mentions metrics monitoring and guardrails",
        "includes rollback or fallback behavior",
        "balances release speed with risk control",
        "communicates the plan to stakeholders clearly",
    ),
}

LOGICAL_CONNECTORS: Sequence[str] = ("while", "whereas", "in contrast", "however", "because")
HR_STRUCTURE_MARKERS: Sequence[str] = (
    "first",
    "then",
    "finally",
    "for example",
    "for instance",
    "in my last role",
    "one example",
    "because",
    "as a result",
    "so that",
)
HR_OUTCOME_MARKERS: Sequence[str] = (
    "result",
    "outcome",
    "learned",
    "improved",
    "impact",
    "grew",
    "delivered",
    "achieved",
    "resolved",
)
INVALID_ANSWER_PATTERNS: Sequence[str] = (
    "i don't know",
    "i dont know",
    "no idea",
    "skip",
)
HR_INVALID_PATTERNS: Sequence[str] = (
    "i don't have any weakness",
    "i dont have any weakness",
    "i have no weaknesses",
    "nothing to improve",
)


@dataclass(frozen=True)
class EvaluationResult:
    question_id: str
    max_points: int
    points_awarded: int
    normalized_score: float
    required_hits: Sequence[str]
    missing_required: Sequence[str]
    optional_hits: Sequence[str]
    reason: Sequence[str]
    missing_points: Sequence[str]
    matched_criteria: Sequence[str] = ()
    response_status: Literal["answered", "skipped", "timeout"] = "answered"

    @property
    def score_out_of_10(self) -> float:
        if self.max_points == 10:
            return float(self.points_awarded)
        if self.max_points == 0:
            return 0.0
        return round((self.points_awarded / self.max_points) * 10, 1)

    def passed(self, threshold: float) -> bool:
        return self.normalized_score >= threshold


def stem_token(token: str) -> str:
    """Very small rule-based stemmer to keep matching dependency-free."""
    if len(token) <= 3:
        return token
    if token.endswith("ization") and len(token) > 8:
        return token[:-7] + "ize"
    if token.endswith("isation") and len(token) > 8:
        return token[:-7] + "ize"
    if token.endswith("tion") and len(token) > 6:
        return token[:-4]
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "i"
    for suffix, cut in (("ingly", 5), ("ing", 3), ("edly", 4), ("ed", 2), ("ly", 2)):
        if token.endswith(suffix) and len(token) > cut + 2:
            return token[:-cut]
    if token.endswith("es") and len(token) > 4:
        return token[:-2]
    if token.endswith("s") and len(token) > 3:
        return token[:-1]
    return token


def normalize_text(text: str) -> str:
    text = text.lower()
    tokens = re.findall(r"[a-z0-9]+", text)
    stems = [stem_token(token) for token in tokens]
    return " ".join(stems)


def _tokenize_for_tfidf(text: str) -> List[str]:
    words = normalize_text(text).split()
    features: List[str] = list(words)
    for token in words:
        if len(token) < 5:
            continue
        for index in range(0, len(token) - 3):
            features.append(f"cg:{token[index:index+4]}")
    return features


def _expand_concept_text(text: str) -> str:
    words = normalize_text(text).split()
    expanded_parts: List[str] = [text]
    for word in words:
        aliases = SYNONYM_MAP.get(word, ())
        if aliases:
            expanded_parts.extend(aliases)
    return " ".join(expanded_parts)


def _inject_canonical_terms(text: str) -> str:
    normalized_words = normalize_text(text).split()
    normalized_text = " ".join(normalized_words)
    injected: List[str] = [text]

    for alias, canonical in ALIAS_TO_CANONICAL.items():
        alias_norm_words = normalize_text(alias).split()
        if not alias_norm_words:
            continue
        alias_norm = " ".join(alias_norm_words)
        if alias_norm in normalized_text:
            injected.append(canonical)

    return " ".join(injected)


def _tfidf_vectors(texts: Sequence[str]) -> List[Dict[str, float]]:
    docs = [_tokenize_for_tfidf(text) for text in texts]
    doc_count = len(docs)
    if doc_count == 0:
        return []

    df: Dict[str, int] = {}
    for tokens in docs:
        for token in set(tokens):
            df[token] = df.get(token, 0) + 1

    idf: Dict[str, float] = {
        token: math.log((1 + doc_count) / (1 + freq)) + 1.0
        for token, freq in df.items()
    }

    vectors: List[Dict[str, float]] = []
    for tokens in docs:
        if not tokens:
            vectors.append({})
            continue

        tf_counts: Dict[str, int] = {}
        for token in tokens:
            tf_counts[token] = tf_counts.get(token, 0) + 1

        token_total = float(len(tokens))
        vector: Dict[str, float] = {}
        for token, count in tf_counts.items():
            vector[token] = (count / token_total) * idf[token]
        vectors.append(vector)

    return vectors


def _cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    if not vec_a or not vec_b:
        return 0.0

    if len(vec_a) > len(vec_b):
        vec_a, vec_b = vec_b, vec_a

    dot = sum(value * vec_b.get(token, 0.0) for token, value in vec_a.items())
    if dot <= 0.0:
        return 0.0

    norm_a = math.sqrt(sum(value * value for value in vec_a.values()))
    norm_b = math.sqrt(sum(value * value for value in vec_b.values()))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def _similarities_to_keywords(*, answer: str, keywords: Sequence[str]) -> List[float]:
    expanded_answer = _inject_canonical_terms(_expand_concept_text(answer))
    answer_words = set(normalize_text(expanded_answer).split())
    similarities: List[float] = []

    for keyword in keywords:
        expanded_keyword = _inject_canonical_terms(_expand_concept_text(keyword))
        vectors = _tfidf_vectors([expanded_answer, expanded_keyword])
        if len(vectors) != 2:
            similarities.append(0.0)
            continue
        cosine = float(_cosine_similarity(vectors[0], vectors[1]))
        keyword_words = set(normalize_text(expanded_keyword).split())
        coverage = 0.0
        if keyword_words:
            coverage = len(answer_words.intersection(keyword_words)) / len(keyword_words)
        similarities.append((0.85 * cosine) + (0.15 * coverage))

    return similarities


def _keyword_only_penalty(answer: str, question: Question) -> float:
    answer_tokens = _tokenize_for_tfidf(answer)
    if not answer_tokens:
        return 0.15

    rubric_text = _expand_concept_text(
        " ".join(list(question.keywords_required) + list(question.keywords_optional))
    )
    rubric_tokens = set(_tokenize_for_tfidf(rubric_text))
    if not rubric_tokens:
        return 1.0

    unique_answer_tokens = set(answer_tokens)
    overlap = len(unique_answer_tokens.intersection(rubric_tokens))
    overlap_ratio = overlap / max(1, len(unique_answer_tokens))
    answer_length = len(answer_tokens)

    if answer_length <= 4:
        return 0.2
    if answer_length <= 8 and overlap_ratio >= 0.75:
        return 0.35
    if overlap_ratio >= 0.85:
        return 0.5
    if overlap_ratio >= 0.7:
        return 0.7
    return 1.0


def _reference_similarity(question: Question, answer: str) -> float:
    reference = _inject_canonical_terms(
        _expand_concept_text(
            " ".join(
                [
                    question.prompt,
                    "required concepts:",
                    ", ".join(question.keywords_required),
                    "optional concepts:",
                    ", ".join(question.keywords_optional),
                ]
            )
        )
    )
    expanded_answer = _inject_canonical_terms(_expand_concept_text(answer))
    vectors = _tfidf_vectors([expanded_answer, reference])
    if len(vectors) != 2:
        return 0.0
    return _cosine_similarity(vectors[0], vectors[1])


def _criterion_similarity(answer: str, criterion: str) -> float:
    expanded_answer = _inject_canonical_terms(_expand_concept_text(answer))
    expanded_criterion = _inject_canonical_terms(_expand_concept_text(criterion))
    vectors = _tfidf_vectors([expanded_answer, expanded_criterion])
    if len(vectors) != 2:
        return 0.0
    return _cosine_similarity(vectors[0], vectors[1])


def _word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", text))


def _sentence_count(text: str) -> int:
    segments = [segment.strip() for segment in re.split(r"[.!?]+", text) if segment.strip()]
    return len(segments)


def _contains_any_phrase(text: str, phrases: Sequence[str]) -> bool:
    normalized = normalize_text(text)
    for phrase in phrases:
        if normalize_text(phrase) in normalized:
            return True
    return False


def _contains_all_terms(text: str, terms: Sequence[str]) -> bool:
    normalized_words = set(normalize_text(text).split())
    required_words = set()
    for term in terms:
        required_words.update(normalize_text(term).split())
    return bool(required_words) and required_words.issubset(normalized_words)


def _matches_concept(
    text: str,
    *,
    phrases: Sequence[str] = (),
    term_sets: Sequence[Sequence[str]] = (),
) -> bool:
    if phrases and _contains_any_phrase(text, phrases):
        return True
    for term_set in term_sets:
        if _contains_all_terms(text, term_set):
            return True
    return False


def _unique_in_order(items: Sequence[str]) -> Tuple[str, ...]:
    seen = set()
    ordered: List[str] = []
    for item in items:
        cleaned = item.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        ordered.append(cleaned)
    return tuple(ordered)


def _as_feedback_item(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        return ""
    sentence = cleaned[0].upper() + cleaned[1:]
    if sentence.endswith("."):
        return sentence
    return sentence + "."


def _humanize_positive_feedback(text: str) -> str:
    normalized = text.strip().lower()
    replacements = (
        ("defines the main idea instead of only naming terms", "You clearly defined the core idea instead of just naming it"),
        ("explains how the concept works or why it matters", "You explained the idea in a way that shows real understanding"),
        ("uses an example or analogy to make the answer easier to understand", "The example made your explanation easier to follow"),
        ("the response is clear and organized instead of feeling like a keyword list", "Your answer felt clear and well organized"),
        ("the response had enough detail and structure to show understanding", "Your answer had enough detail to feel thoughtful and complete"),
        ("correctly explained what precision and recall measure", "You explained both precision and recall correctly"),
        ("clearly contrasted the two metrics instead of listing them separately", "You compared the two metrics clearly"),
        ("included the true positive, false positive, and false negative framing", "You brought in the right supporting concepts to strengthen the answer"),
        ("used an example to make the tradeoff easier to understand", "The example helped connect the concept to a practical situation"),
        ("defines leakage as information from outside the training split contaminating evaluation", "You explained data leakage in a clear and accurate way"),
        ("identifies realistic leakage sources such as full-dataset preprocessing, overlap, or label leakage", "You pointed out realistic causes instead of keeping the answer too theoretical"),
        ("explains prevention steps such as split-first workflows, train-only fitting, or strict isolation", "You gave practical prevention steps, which made the answer stronger"),
        ("covers time-aware validation by keeping past and future data strictly separated", "You included the time-based split point, which is an important detail"),
        ("the response stayed relevant to the question being asked", "Your answer stayed focused on what was asked"),
        ("the response was partially relevant to the prompt", "Your answer was relevant, though it could be a bit more focused"),
        ("the answer was clear enough to follow without feeling fragmented", "Your answer was easy to follow"),
        ("the response had a clear introduction, supporting body, and closing takeaway", "Your answer had a strong structure from start to finish"),
        ("the response had some structure and directional flow", "Your answer had a sensible flow"),
        ("the answer included concrete actions or examples instead of only abstract claims", "You supported your answer with concrete actions and examples"),
        ("the answer included at least one useful concrete detail", "You included a useful concrete detail"),
        ("the answer closed with an outcome or learning point", "Ending with the outcome or lesson made the answer feel complete"),
    )

    for source, target in replacements:
        if normalized.startswith(source):
            return _as_feedback_item(target)
    return _as_feedback_item(text)


def _humanize_improvement_feedback(text: str) -> str:
    normalized = text.strip().lower()
    replacements = (
        ("start with a simple definition of the main concept", "Start with a simple definition so the answer has a clear opening"),
        ("add a short explanation of how it works, when it is used, or why it matters", "Add one or two lines explaining how it works or why it matters"),
        ("add a small example or analogy to make the answer more concrete", "A quick example would make this answer feel stronger and more practical"),
        ("include the core concepts more clearly", "Bring in the key concepts a bit more directly"),
        ("make the answer clearer with 2-3 connected sentences", "Use 2-3 connected sentences so the answer feels smoother"),
        ("use a fuller explanation with an example, comparison, or short workflow", "A little more detail would help this answer feel complete"),
        ("make the answer more relevant to the specific question instead of giving a generic response", "Make the answer more specific to the exact question"),
        ("use a simple structure: main point, supporting example, then a closing takeaway", "A simple structure would help: main point, example, then takeaway"),
        ("strengthen the answer with a concrete example, action, or result", "Add a real example, action, or result to make the answer more convincing"),
        ("finish with a short outcome, lesson, or reflection", "End with a short lesson or outcome so the answer feels complete"),
        ("state that precision focuses on correct predicted positives and recall focuses on finding actual positives", "State clearly what precision measures and what recall measures"),
        ("include how true positives, false positives, and false negatives relate to the metrics", "Add the TP/FP/FN connection to make the explanation more complete"),
        ("add a comparison that explains when precision differs from recall", "Briefly compare the two so the difference is obvious"),
        ("add a small example to show why one metric may matter more in a real use case", "A short real-world example would make this much stronger"),
        ("define leakage as train/test or future information contaminating the training process", "Define leakage more clearly before moving into causes or fixes"),
        ("mention concrete leakage causes like preprocessing before splitting, overlap, or target leakage", "Mention one or two concrete leakage causes"),
        ("explain how to prevent leakage with split-first pipelines and train-only fitting", "Add the prevention steps more directly"),
        ("add time-based splitting guidance such as chronological validation or keeping future data out of training", "Include the time-based split detail if the data has an order"),
    )

    for source, target in replacements:
        if normalized.startswith(source):
            return _as_feedback_item(target)
    return _as_feedback_item(text)


def _build_keyword_feedback(
    question: Question,
    required_hits: Sequence[str],
    missing_required: Sequence[str],
    optional_hits: Sequence[str],
    answer: str,
) -> Tuple[Sequence[str], Sequence[str]]:
    reasons: List[str] = []
    missing_points: List[str] = []

    if required_hits:
        reasons.append(f"You covered the main idea well: {', '.join(required_hits[:3])}.")
    if optional_hits:
        reasons.append(f"You strengthened the answer with supporting detail around: {', '.join(optional_hits[:4])}.")
    if _word_count(answer) >= 18:
        reasons.append("You gave enough detail for the answer to feel properly explained.")
    if not reasons:
        reasons.append("You made an attempt, but the answer needs a clearer connection to the question.")

    if missing_required:
        missing_points.append(f"Add the core point(s) more clearly: {', '.join(missing_required[:3])}.")

    remaining_optional = [
        keyword for keyword in question.keywords_optional if keyword not in set(optional_hits)
    ][:3]
    if remaining_optional:
        missing_points.append(
            f"Strengthen the answer with supporting details such as: {', '.join(remaining_optional)}."
        )
    if _word_count(answer) < 12:
        missing_points.append("Use a fuller explanation with an example, comparison, or short workflow.")

    return _unique_in_order(reasons), _unique_in_order(missing_points)


def _build_criteria_feedback(
    matched_criteria: Sequence[str],
    missing_criteria: Sequence[str],
    answer: str,
) -> Tuple[Sequence[str], Sequence[str]]:
    reasons = [_humanize_positive_feedback(text) for text in matched_criteria[:3]]
    missing_points = [_humanize_improvement_feedback(text) for text in missing_criteria[:3]]

    if matched_criteria and _word_count(answer) >= 18:
        reasons.append("This felt like a complete answer rather than a rushed one.")
    if not reasons:
        reasons.append("You attempted the question, but the answer still needs more substance.")
    if _word_count(answer) < 12:
        missing_points.append("Try adding a little more detail so the answer does not feel too brief.")

    return _unique_in_order(reasons), _unique_in_order(missing_points)


def _build_immediate_evaluation(
    question: Question,
    *,
    score: int,
    reason: str,
    missing_points: Sequence[str],
    response_status: Literal["answered", "skipped", "timeout"] = "answered",
) -> EvaluationResult:
    normalized_score = score / question.max_points if question.max_points else 0.0
    return EvaluationResult(
        question_id=question.id,
        max_points=question.max_points,
        points_awarded=score,
        normalized_score=normalized_score,
        required_hits=(),
        missing_required=tuple(question.keywords_required),
        optional_hits=(),
        reason=(reason,),
        missing_points=tuple(missing_points),
        response_status=response_status,
    )


def _maybe_invalid_answer_evaluation(question: Question, answer: str) -> EvaluationResult | None:
    answer_lower = answer.strip().lower()
    words = _word_count(answer_lower)

    if not answer_lower or words < 3:
        return _build_immediate_evaluation(
            question,
            score=0,
            reason="Answer not provided. Try attempting the question.",
            missing_points=("Try answering in at least 2-3 complete words or a short sentence.",),
        )

    if _contains_any_phrase(answer_lower, INVALID_ANSWER_PATTERNS):
        return _build_immediate_evaluation(
            question,
            score=0,
            reason="Answer not provided. Try attempting the question.",
            missing_points=("Give a short attempt even if you are unsure.",),
        )

    if question.type == "hr" and _contains_any_phrase(answer_lower, HR_INVALID_PATTERNS):
        return _build_immediate_evaluation(
            question,
            score=0,
            reason="Answer lacks honesty. Mention real areas of improvement.",
            missing_points=("Choose one genuine weakness or improvement area and explain how you are working on it.",),
        )

    reference_similarity = _reference_similarity(question, answer)
    required_hits, _, optional_hits, _ = _extract_concept_hits(question, answer)

    if question.type == "technical":
        if words >= 3 and reference_similarity < 0.04 and not required_hits and not optional_hits:
            return _build_immediate_evaluation(
                question,
                score=1,
                reason="The answer does not match the question topic closely enough.",
                missing_points=("Focus on the exact topic asked and mention the main concept directly.",),
            )
    else:
        personal_voice = _contains_any_phrase(answer, (" i ", " my ", " me ", " myself "))
        if words >= 3 and reference_similarity < 0.04 and not personal_voice:
            return _build_immediate_evaluation(
                question,
                score=1,
                reason="The answer does not match the question topic closely enough.",
                missing_points=("Answer the HR question directly with a personal and relevant example.",),
            )

    return None


def _calibrate_structured_score(
    *,
    question: Question,
    answer: str,
    raw_score: float,
    relevance_similarity: float,
    substantive_attempt: bool,
    concept_hit_count: int,
) -> int:
    """
    Calibrate structured rubric scores into fair interview bands.

    Goals:
    - strong answers: 8-10
    - medium substantive answers: 5-7
    - weak attempts: 2-4
    - extremely empty/irrelevant answers: 0-2
    """
    words = _word_count(answer)
    points_awarded = int(round(raw_score))

    if substantive_attempt and raw_score >= 4:
        points_awarded = max(5, points_awarded)

    if words < 5:
        points_awarded = min(points_awarded, 2)
    elif words < 10:
        points_awarded = min(points_awarded, 4)

    if relevance_similarity < 0.02 and concept_hit_count == 0:
        points_awarded = min(points_awarded, 3)

    if words >= 3 and points_awarded < 2:
        points_awarded = 2

    return max(0, min(question.max_points, points_awarded))


def _extract_concept_hits(
    question: Question,
    answer: str,
) -> Tuple[Sequence[str], Sequence[str], Sequence[str], float]:
    required_similarity_threshold = 0.15
    optional_similarity_threshold = 0.12

    required_sims = _similarities_to_keywords(answer=answer, keywords=question.keywords_required)
    optional_sims = _similarities_to_keywords(answer=answer, keywords=question.keywords_optional)

    required_hits = [
        keyword
        for keyword, similarity in zip(question.keywords_required, required_sims)
        if similarity >= required_similarity_threshold
    ]
    missing_required = [
        keyword
        for keyword, similarity in zip(question.keywords_required, required_sims)
        if similarity < required_similarity_threshold
    ]
    optional_hits = [
        keyword
        for keyword, similarity in zip(question.keywords_optional, optional_sims)
        if similarity >= optional_similarity_threshold
    ]

    concept_signal = 0.0
    if required_sims:
        concept_signal += sum(required_sims) / len(required_sims)
    if optional_sims:
        concept_signal += 0.5 * (sum(optional_sims) / len(optional_sims))

    return required_hits, missing_required, optional_hits, concept_signal


def _evaluate_generic_concept_answer(question: Question, answer: str) -> EvaluationResult:
    """
    Fairer technical scoring based on concepts and answer structure.

    The rubric rewards:
    - definition
    - explanation
    - example/analogy
    - key concepts
    - clarity

    Medium substantive answers get a floor near 5, while vague or irrelevant
    answers can still land in the 2-4 range.
    """
    words = _word_count(answer)
    sentences = _sentence_count(answer)
    reference_similarity = _reference_similarity(question, answer)
    required_hits, missing_required, optional_hits, concept_signal = _extract_concept_hits(question, answer)

    definition_present = bool(required_hits) and (
        _contains_any_phrase(
            answer,
            (
                "is",
                "are",
                "means",
                "refers to",
                "can be defined as",
                "is used to",
                "is useful because",
                "is a",
            ),
        )
        or sentences >= 1
    )

    explanation_present = (
        words >= 12
        and (
            sentences >= 2
            or _contains_any_phrase(
                answer,
                (
                    "because",
                    "so that",
                    "used to",
                    "helps",
                    "allows",
                    "works by",
                    "difference",
                    "compared with",
                    "when",
                    "while",
                    "how",
                ),
            )
        )
    )

    example_present = _contains_any_phrase(
        answer,
        (
            "for example",
            "for instance",
            "such as",
            "like",
            "imagine",
            "consider",
            "one example",
            "suppose",
        ),
    )

    required_target = max(1, len(question.keywords_required))
    key_concepts_present = (
        len(required_hits) >= required_target
        or (len(required_hits) >= 1 and len(optional_hits) >= 1)
        or concept_signal >= 0.34
    )

    clarity_present = (
        words >= 18
        and sentences >= 2
        and (
            _contains_any_phrase(answer, LOGICAL_CONNECTORS)
            or _contains_any_phrase(answer, ("first", "then", "finally", "overall", "in short"))
            or sentences >= 3
        )
    )

    raw_score = 0
    matched_criteria: List[str] = []
    missing_criteria: List[str] = []

    if definition_present:
        raw_score += 2
        matched_criteria.append("Defines the main idea instead of only naming terms.")
    else:
        missing_criteria.append("Start with a simple definition of the main concept.")

    if explanation_present:
        raw_score += 2
        matched_criteria.append("Explains how the concept works or why it matters.")
    else:
        missing_criteria.append("Add a short explanation of how it works, when it is used, or why it matters.")

    if example_present:
        raw_score += 2
        matched_criteria.append("Uses an example or analogy to make the answer easier to understand.")
    else:
        missing_criteria.append("Add a small example or analogy to make the answer more concrete.")

    if key_concepts_present:
        raw_score += 2
        matched_criteria.append(
            f"Covers the key concepts for this question: {', '.join((list(required_hits) + list(optional_hits))[:3])}."
        )
    else:
        missing_criteria.append(
            f"Include the core concepts more clearly, such as: {', '.join(list(question.keywords_required)[:3])}."
        )

    if clarity_present:
        raw_score += 2
        matched_criteria.append("The response is clear and organized instead of feeling like a keyword list.")
    else:
        missing_criteria.append("Make the answer clearer with 2-3 connected sentences.")

    substantive_attempt = words >= 10 and reference_similarity >= 0.03
    points_awarded = _calibrate_structured_score(
        question=question,
        answer=answer,
        raw_score=raw_score,
        relevance_similarity=reference_similarity,
        substantive_attempt=substantive_attempt,
        concept_hit_count=len(required_hits) + len(optional_hits),
    )
    normalized_score = points_awarded / question.max_points if question.max_points else 0.0
    reason, missing_points = _build_criteria_feedback(matched_criteria, missing_criteria, answer)

    return EvaluationResult(
        question_id=question.id,
        max_points=question.max_points,
        points_awarded=points_awarded,
        normalized_score=normalized_score,
        required_hits=tuple(required_hits),
        missing_required=tuple(missing_required),
        optional_hits=tuple(optional_hits),
        reason=reason,
        missing_points=missing_points,
        matched_criteria=tuple(matched_criteria),
    )


def _evaluate_weighted_rubric(question: Question, answer: str, criteria: Sequence[str]) -> EvaluationResult:
    generic_result = _evaluate_generic_concept_answer(question, answer)
    words = _word_count(answer)
    connectors_present = _contains_any_phrase(answer, LOGICAL_CONNECTORS)
    criterion_weight = question.max_points / max(1, len(criteria))
    criterion_hit_threshold = 0.1

    raw_points = 0.0
    hit_criteria: List[str] = []
    missing_criteria: List[str] = []
    for criterion in criteria:
        similarity = _criterion_similarity(answer, criterion)
        if similarity >= criterion_hit_threshold:
            raw_points += criterion_weight
            hit_criteria.append(criterion)
        else:
            missing_criteria.append(criterion)

    if connectors_present and words >= 12:
        raw_points += 1.0
    raw_points *= _keyword_only_penalty(answer, question)

    required_sim_threshold = 0.17
    optional_sim_threshold = 0.14
    required_sims = _similarities_to_keywords(answer=answer, keywords=question.keywords_required)
    optional_sims = _similarities_to_keywords(answer=answer, keywords=question.keywords_optional)

    required_hits = [
        keyword
        for keyword, similarity in zip(question.keywords_required, required_sims)
        if similarity >= required_sim_threshold
    ]
    missing_required = [
        keyword
        for keyword, similarity in zip(question.keywords_required, required_sims)
        if similarity < required_sim_threshold
    ]
    optional_hits = [
        keyword
        for keyword, similarity in zip(question.keywords_optional, optional_sims)
        if similarity >= optional_sim_threshold
    ]
    if connectors_present:
        optional_hits.append("contrastive explanation")

    points_awarded = generic_result.points_awarded
    normalized_score = generic_result.normalized_score
    criteria_reason, criteria_missing_points = _build_criteria_feedback(hit_criteria, missing_criteria, answer)
    reason = _unique_in_order(tuple(generic_result.reason) + tuple(criteria_reason))
    missing_points = _unique_in_order(tuple(generic_result.missing_points) + tuple(criteria_missing_points))

    return EvaluationResult(
        question_id=question.id,
        max_points=question.max_points,
        points_awarded=points_awarded,
        normalized_score=normalized_score,
        required_hits=generic_result.required_hits,
        missing_required=generic_result.missing_required,
        optional_hits=generic_result.optional_hits,
        reason=reason,
        missing_points=missing_points,
        matched_criteria=tuple(hit_criteria),
    )


def _evaluate_precision_recall_weighted(question: Question, answer: str) -> EvaluationResult:
    answer_norm = normalize_text(answer)
    words = _word_count(answer)
    sentences = _sentence_count(answer)

    precision_definition = _contains_any_phrase(
        answer,
        (
            "precision is",
            "precision measures",
            "precision tells us",
            "precision means",
            "of predicted positives",
            "how many predicted positives are correct",
            "fraction of predicted positives",
            "correct predicted positives",
        ),
    )
    recall_definition = _contains_any_phrase(
        answer,
        (
            "recall is",
            "recall measures",
            "recall tells us",
            "recall means",
            "of actual positives",
            "how many actual positives are found",
            "fraction of actual positives",
            "sensitivity",
            "find actual positives",
        ),
    )

    has_tp = "tp" in answer_norm or "true positive" in answer_norm
    has_fp = "fp" in answer_norm or "false positive" in answer_norm
    has_fn = "fn" in answer_norm or "false negative" in answer_norm
    formula_present = has_tp and has_fp and has_fn

    has_connector = _contains_any_phrase(answer, LOGICAL_CONNECTORS)
    difference_explained = has_connector and precision_definition and recall_definition
    example_present = _contains_any_phrase(
        answer,
        ("for example", "for instance", "such as", "like", "imagine"),
    )

    definition_present = precision_definition and recall_definition
    explanation_present = difference_explained or (definition_present and words >= 14)
    key_concepts_present = formula_present or (
        definition_present and (has_fp or has_fn or has_tp)
    )
    clarity_present = words >= 18 and sentences >= 2 and (
        has_connector or difference_explained or formula_present
    )

    points = 0
    if definition_present:
        points += 2
    if explanation_present:
        points += 2
    if example_present:
        points += 2
    if key_concepts_present:
        points += 2
    if clarity_present:
        points += 2

    if words < 10:
        points = min(points, 2)
    if words <= 8 and _contains_any_phrase(
        answer,
        ("precision recall tp fp fn", "precision recall", "tp fp fn"),
    ):
        points = min(points, 1)

    required_hits = []
    if precision_definition:
        required_hits.append("precision")
    if recall_definition:
        required_hits.append("recall")

    missing_required = []
    if not precision_definition:
        missing_required.append("precision")
    if not recall_definition:
        missing_required.append("recall")

    optional_hits = []
    if formula_present:
        optional_hits.extend(["true positive", "false positive", "false negative"])
    if has_connector:
        optional_hits.append("contrastive explanation")
    if example_present:
        optional_hits.append("example")

    substantive_attempt = words >= 10 and (
        precision_definition or recall_definition or formula_present or difference_explained
    )
    points = _calibrate_structured_score(
        question=question,
        answer=answer,
        raw_score=points,
        relevance_similarity=_reference_similarity(question, answer),
        substantive_attempt=substantive_attempt,
        concept_hit_count=len(required_hits) + len(optional_hits),
    )
    normalized_score = points / question.max_points if question.max_points else 0.0

    reason: List[str] = []
    missing_points: List[str] = []

    if definition_present:
        reason.append("Correctly explained what precision and recall measure.")
    if explanation_present:
        reason.append("Clearly contrasted the two metrics instead of listing them separately.")
    if key_concepts_present:
        reason.append("Included the true positive, false positive, and false negative framing.")
    if example_present:
        reason.append("Used an example to make the tradeoff easier to understand.")
    if not reason:
        reason.append("The answer referenced the topic but did not clearly define both metrics.")

    if not definition_present:
        missing_points.append("State that precision focuses on correct predicted positives and recall focuses on finding actual positives.")
    if not explanation_present:
        missing_points.append("Add a comparison that explains when precision differs from recall.")
    if not key_concepts_present:
        missing_points.append("Include how true positives, false positives, and false negatives relate to the metrics.")
    if not example_present:
        missing_points.append("Add a small example to show why one metric may matter more in a real use case.")
    if words < 12:
        missing_points.append("Use a fuller explanation instead of a short keyword list.")

    return EvaluationResult(
        question_id=question.id,
        max_points=question.max_points,
        points_awarded=points,
        normalized_score=normalized_score,
        required_hits=tuple(required_hits),
        missing_required=tuple(missing_required),
        optional_hits=tuple(optional_hits),
        reason=_unique_in_order(reason),
        missing_points=_unique_in_order(missing_points),
    )


def _evaluate_data_leakage_concepts(question: Question, answer: str) -> EvaluationResult:
    """
    Concept-based evaluator for data leakage.

    This avoids strict keyword dependence by accepting several paraphrases
    for the same idea, such as train-only fitting, split-first preprocessing,
    future-information leakage, and overlap contamination.
    """
    words = _word_count(answer)

    definition_present = _matches_concept(
        answer,
        phrases=(
            "data leakage",
            "data contamination",
            "train test contamination",
            "information leak",
            "using information from the test set during training",
            "using validation information during training",
            "using future information",
            "information from outside the training split gets into training",
        ),
        term_sets=(
            ("test", "information", "training"),
            ("validation", "information", "training"),
            ("future", "information"),
            ("train", "test", "contamination"),
            ("leakage", "information"),
        ),
    )

    causes_present = _matches_concept(
        answer,
        phrases=(
            "preprocessing before the split",
            "scaling before the split",
            "normalizing the full dataset first",
            "fitting the scaler on all data",
            "using target information in features",
            "label leakage",
            "duplicate records across splits",
            "same user in train and test",
            "future data leaking into the past",
        ),
        term_sets=(
            ("fit", "scaler", "all", "data"),
            ("preprocess", "before", "split"),
            ("transform", "before", "split"),
            ("target", "feature"),
            ("label", "leakage"),
            ("duplicate", "split"),
            ("overlap", "split"),
            ("future", "past"),
        ),
    )

    prevention_present = _matches_concept(
        answer,
        phrases=(
            "split before preprocessing",
            "split the data first",
            "fit preprocessing only on the training set",
            "fit the scaler only on train",
            "train only preprocessing",
            "train-only preprocessing",
            "use a pipeline fit on training data only",
            "keep train validation test fully separate",
            "strict train test isolation",
            "deduplicate across splits",
            "no overlap between splits",
        ),
        term_sets=(
            ("split", "first"),
            ("fit", "train", "only"),
            ("pipeline", "train"),
            ("preprocess", "train", "only"),
            ("isolation", "train", "test"),
            ("no", "overlap", "split"),
            ("deduplicate", "split"),
        ),
    )

    time_split_present = _matches_concept(
        answer,
        phrases=(
            "time based split",
            "time-based split",
            "chronological split",
            "split by time",
            "train on past data and test on future data",
            "never let future data into training",
            "rolling window validation",
            "forward chaining",
        ),
        term_sets=(
            ("time", "split"),
            ("chronological", "split"),
            ("past", "future"),
            ("future", "training"),
            ("rolling", "window"),
            ("forward", "chain"),
        ),
    )

    points = 0
    matched_criteria: List[str] = []
    missing_criteria: List[str] = []

    if definition_present:
        points += 2
        matched_criteria.append("Defines leakage as information from outside the training split contaminating evaluation.")
    else:
        missing_criteria.append("Define leakage as train/test or future information contaminating the training process.")

    if causes_present:
        points += 2
        matched_criteria.append("Identifies realistic leakage sources such as full-dataset preprocessing, overlap, or label leakage.")
    else:
        missing_criteria.append("Mention concrete leakage causes like preprocessing before splitting, overlap, or target leakage.")

    if prevention_present:
        points += 3
        matched_criteria.append("Explains prevention steps such as split-first workflows, train-only fitting, or strict isolation.")
    else:
        missing_criteria.append("Explain how to prevent leakage with split-first pipelines and train-only fitting.")

    if time_split_present:
        points += 3
        matched_criteria.append("Covers time-aware validation by keeping past and future data strictly separated.")
    else:
        missing_criteria.append("Add time-based splitting guidance such as chronological validation or keeping future data out of training.")

    if words >= 24 and sum(
        int(flag) for flag in (definition_present, causes_present, prevention_present, time_split_present)
    ) >= 3:
        points = min(question.max_points, points + 1)

    substantive_attempt = words >= 10 and (
        definition_present or causes_present or prevention_present or time_split_present
    )
    points = _calibrate_structured_score(
        question=question,
        answer=answer,
        raw_score=points,
        relevance_similarity=_reference_similarity(question, answer),
        substantive_attempt=substantive_attempt,
        concept_hit_count=sum(
            int(flag) for flag in (definition_present, causes_present, prevention_present, time_split_present)
        ),
    )
    normalized_score = points / question.max_points if question.max_points else 0.0

    required_hits = []
    if definition_present:
        required_hits.append("definition")
    if prevention_present:
        required_hits.append("prevention")

    missing_required = []
    if not definition_present:
        missing_required.append("definition")
    if not prevention_present:
        missing_required.append("prevention")

    optional_hits = []
    if causes_present:
        optional_hits.append("causes")
    if time_split_present:
        optional_hits.append("time-based split")

    reason, missing_points = _build_criteria_feedback(matched_criteria, missing_criteria, answer)

    return EvaluationResult(
        question_id=question.id,
        max_points=question.max_points,
        points_awarded=points,
        normalized_score=normalized_score,
        required_hits=tuple(required_hits),
        missing_required=tuple(missing_required),
        optional_hits=tuple(optional_hits),
        reason=reason,
        missing_points=missing_points,
        matched_criteria=tuple(matched_criteria),
    )


def _evaluate_hr_answer(question: Question, answer: str) -> EvaluationResult:
    """
    Evaluate HR answers using communication quality rather than strict keywords.

    The score focuses on:
    - clarity of response
    - structure
    - relevance to the prompt
    - completeness with concrete detail
    """
    words = _word_count(answer)
    sentences = _sentence_count(answer)
    normalized_answer = normalize_text(answer)
    prompt_reference = f"{question.topic} {question.prompt}"
    relevance_similarity = _reference_similarity(
        Question(
            id=question.id,
            mode=question.mode,
            difficulty=question.difficulty,
            topic=question.topic,
            prompt=prompt_reference,
            keywords_required=(),
            keywords_optional=(),
            max_points=question.max_points,
        ),
        answer,
    )

    example_present = _contains_any_phrase(
        answer,
        ("for example", "for instance", "one time", "in my last role", "on a project", "when i"),
    )
    personal_voice = _contains_any_phrase(answer, (" i ", " my ", " me ", " myself "))
    action_present = _contains_any_phrase(
        answer,
        ("i did", "i worked", "i handled", "i decided", "i changed", "i improved", "i led", "i took"),
    )
    outcome_present = _contains_any_phrase(answer, HR_OUTCOME_MARKERS)
    structure_marker_present = _contains_any_phrase(answer, HR_STRUCTURE_MARKERS)
    conclusion_present = _contains_any_phrase(
        answer,
        ("that taught me", "i learned", "since then", "because of that", "in summary", "overall", "fits this role"),
    )

    relevance_score = 0
    if personal_voice and relevance_similarity >= 0.08:
        relevance_score = 3
    elif personal_voice and relevance_similarity >= 0.04:
        relevance_score = 2
    elif personal_voice and (relevance_similarity >= 0.02 or example_present or action_present):
        relevance_score = 1

    clarity_score = 0
    if words >= 45 and sentences >= 3:
        clarity_score = 2
    elif words >= 22 and sentences >= 2:
        clarity_score = 1

    structure_score = 0
    if sentences >= 3 and structure_marker_present and (example_present or action_present) and conclusion_present:
        structure_score = 2
    elif sentences >= 2 and (structure_marker_present or example_present or action_present):
        structure_score = 1

    completeness_score = 0
    if example_present and action_present and outcome_present:
        completeness_score = 3
    elif (example_present and action_present) or (action_present and outcome_present):
        completeness_score = 2
    elif example_present or action_present or outcome_present:
        completeness_score = 1

    points = relevance_score + clarity_score + structure_score + completeness_score

    if words < 12:
        points = min(points, 2)
    elif words < 20:
        points = min(points, 4)

    if relevance_score == 0:
        points = min(points, 2)
    elif relevance_score == 1:
        points = min(points, 5)

    points = max(0, min(question.max_points, points))
    normalized_score = points / question.max_points if question.max_points else 0.0

    matched_criteria: List[str] = []
    missing_criteria: List[str] = []

    if relevance_score >= 2:
        matched_criteria.append("The response stayed relevant to the question being asked.")
    elif relevance_score == 1:
        matched_criteria.append("The response was partially relevant to the prompt.")
    else:
        missing_criteria.append("Make the answer more relevant to the specific question instead of giving a generic response.")

    if clarity_score >= 1:
        matched_criteria.append("The answer was clear enough to follow without feeling fragmented.")
    else:
        missing_criteria.append("Add more detail so the answer feels clear instead of brief or vague.")

    if structure_score == 2:
        matched_criteria.append("The response had a clear introduction, supporting body, and closing takeaway.")
    elif structure_score == 1:
        matched_criteria.append("The response had some structure and directional flow.")
    else:
        missing_criteria.append("Use a simple structure: main point, supporting example, then a closing takeaway.")

    if completeness_score >= 2:
        matched_criteria.append("The answer included concrete actions or examples instead of only abstract claims.")
    elif completeness_score == 1:
        matched_criteria.append("The answer included at least one useful concrete detail.")
    else:
        missing_criteria.append("Strengthen the answer with a concrete example, action, or result.")

    if conclusion_present and outcome_present:
        matched_criteria.append("The answer closed with an outcome or learning point.")
    elif words >= 20 and not conclusion_present:
        missing_criteria.append("Finish with a short outcome, lesson, or reflection.")

    required_hits = []
    if relevance_score >= 2:
        required_hits.append("relevance")
    if clarity_score >= 1:
        required_hits.append("clarity")

    missing_required = []
    if relevance_score < 2:
        missing_required.append("relevance")
    if clarity_score < 1:
        missing_required.append("clarity")

    optional_hits = []
    if structure_score >= 1:
        optional_hits.append("structure")
    if completeness_score >= 1:
        optional_hits.append("completeness")
    if example_present:
        optional_hits.append("example")

    reason, missing_points = _build_criteria_feedback(matched_criteria, missing_criteria, answer)

    return EvaluationResult(
        question_id=question.id,
        max_points=question.max_points,
        points_awarded=points,
        normalized_score=normalized_score,
        required_hits=tuple(required_hits),
        missing_required=tuple(missing_required),
        optional_hits=tuple(optional_hits),
        reason=reason,
        missing_points=missing_points,
        matched_criteria=tuple(matched_criteria),
    )


def evaluate_answer(question: Question, answer: str) -> EvaluationResult:
    """
    Evaluate an answer and return structured feedback.

    The project keeps lightweight NLP scoring, but each result now includes:
    - score (via points_awarded / max_points)
    - reason
    - missing_points
    """
    invalid_result = _maybe_invalid_answer_evaluation(question, answer)
    if invalid_result is not None:
        return invalid_result

    if question.id == "q1_precision_recall":
        return _evaluate_precision_recall_weighted(question, answer)

    if question.id == "q6_data_leakage":
        return _evaluate_data_leakage_concepts(question, answer)

    if question.type == "hr":
        return _evaluate_hr_answer(question, answer)

    if question.id in WEIGHTED_RUBRICS:
        return _evaluate_weighted_rubric(
            question=question,
            answer=answer,
            criteria=WEIGHTED_RUBRICS[question.id],
        )
    return _evaluate_generic_concept_answer(question, answer)


def format_question_feedback(question: Question, evaluation: EvaluationResult) -> str:
    """Return structured, readable feedback for a single answer."""
    lines = [
        f"Topic: {question.topic}",
        f"Score: {evaluation.points_awarded}/{evaluation.max_points}",
        "What was correct:",
    ]

    if evaluation.reason:
        for item in evaluation.reason:
            lines.append(f"- {item}")
    else:
        lines.append("- The answer partially matched the prompt.")

    lines.append("Missing points:")
    if evaluation.missing_points:
        for item in evaluation.missing_points:
            lines.append(f"- {item}")
    else:
        lines.append("- No major gaps detected.")

    return "\n".join(lines)


def build_special_evaluation(
    question: Question,
    status: Literal["skip", "timeout"],
) -> EvaluationResult:
    """
    Build a minimal-score evaluation for skipped or timed-out questions so the
    adaptive engine can continue using the same evaluation object.
    """
    if status == "skip":
        score = 0
        reason = ("The question was skipped, so no score was assigned.",)
        missing_points = (
            "Answer the question instead of skipping it to improve topic coverage.",
            "Use a short structured response even if you are unsure.",
        )
    else:
        score = 0
        reason = ("No complete answer was submitted within the 60-second limit.",)
        missing_points = (
            "Respond within 60 seconds to avoid an automatic low score.",
            "Practice giving a brief first answer quickly, then add detail.",
        )

    normalized_score = score / question.max_points if question.max_points else 0.0
    return EvaluationResult(
        question_id=question.id,
        max_points=question.max_points,
        points_awarded=score,
        normalized_score=normalized_score,
        required_hits=(),
        missing_required=tuple(question.keywords_required),
        optional_hits=(),
        reason=reason,
        missing_points=missing_points,
        response_status="skipped" if status == "skip" else "timeout",
    )
