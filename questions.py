from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Sequence, Tuple

Difficulty = Literal["easy", "medium", "hard"]
InterviewMode = Literal["technical", "hr", "mixed"]
SemesterRange = Tuple[int, int]


@dataclass(frozen=True)
class Question:
    id: str
    mode: InterviewMode
    difficulty: Difficulty
    topic: str
    prompt: str
    keywords_required: Sequence[str]
    keywords_optional: Sequence[str]
    max_points: int = 10
    semester_range: Optional[SemesterRange] = None

    def __post_init__(self) -> None:
        if self.semester_range is None:
            default_range = (1, 8) if self.mode == "hr" else _default_semester_range_for_difficulty(self.difficulty)
            object.__setattr__(self, "semester_range", default_range)

    @property
    def type(self) -> str:
        """User-facing question family used by the evaluator and UI."""
        return "hr" if self.mode == "hr" else "technical"


def _default_semester_range_for_difficulty(difficulty: Difficulty) -> SemesterRange:
    if difficulty == "easy":
        return (1, 4)
    if difficulty == "medium":
        return (1, 8)
    return (5, 8)


TECHNICAL_QUESTIONS: List[Question] = [
    Question(
        id="t101_c_variables_datatypes",
        mode="technical",
        difficulty="easy",
        topic="C Programming",
        prompt="What are variables and data types in C? Give simple examples of int, float, and char.",
        keywords_required=["variables", "data types"],
        keywords_optional=["int", "float", "char", "memory", "declaration"],
        semester_range=(1, 2),
    ),
    Question(
        id="t102_c_loops_conditionals",
        mode="technical",
        difficulty="easy",
        topic="C Programming",
        prompt="Explain how if-else statements and loops like for or while are used in C.",
        keywords_required=["if", "loop"],
        keywords_optional=["for", "while", "condition", "iteration", "decision"],
        semester_range=(1, 2),
    ),
    Question(
        id="t103_arrays_basics",
        mode="technical",
        difficulty="easy",
        topic="Programming Basics",
        prompt="What is an array? How do you access and update elements in an array?",
        keywords_required=["array", "elements"],
        keywords_optional=["index", "contiguous", "update", "loop", "store multiple values"],
        semester_range=(1, 2),
    ),
    Question(
        id="t104_functions_c",
        mode="technical",
        difficulty="medium",
        topic="C Programming",
        prompt="Why do we use functions in C? Explain parameters, return values, and code reuse.",
        keywords_required=["functions", "parameters"],
        keywords_optional=["return", "reuse", "modularity", "arguments", "logic"],
        semester_range=(1, 2),
    ),
    Question(
        id="t105_pointers_basics",
        mode="technical",
        difficulty="medium",
        topic="C Programming",
        prompt="What is a pointer in C, and why is it useful?",
        keywords_required=["pointer", "address"],
        keywords_optional=["memory", "dereference", "variable", "reference", "access"],
        semester_range=(1, 2),
    ),
    Question(
        id="t106_python_datatypes",
        mode="technical",
        difficulty="easy",
        topic="Python Basics",
        prompt="What are common Python data types such as int, float, string, list, and dictionary?",
        keywords_required=["python", "data types"],
        keywords_optional=["list", "dictionary", "string", "int", "float"],
        semester_range=(1, 2),
    ),
    Question(
        id="t107_python_loops_lists",
        mode="technical",
        difficulty="easy",
        topic="Python Basics",
        prompt="How do loops work in Python, and how are they often used with lists?",
        keywords_required=["loops", "lists"],
        keywords_optional=["for", "while", "iterate", "index", "items"],
        semester_range=(1, 2),
    ),
    Question(
        id="t108_python_functions_modules",
        mode="technical",
        difficulty="medium",
        topic="Python Basics",
        prompt="What are functions and modules in Python, and how do they help organize programs?",
        keywords_required=["functions", "modules"],
        keywords_optional=["reuse", "import", "organization", "logic", "parameters"],
        semester_range=(1, 2),
    ),
    Question(
        id="t109_strings_input_output",
        mode="technical",
        difficulty="medium",
        topic="Programming Basics",
        prompt="How do you work with strings and basic input/output in C or Python?",
        keywords_required=["strings", "input"],
        keywords_optional=["output", "print", "scanf", "format", "user input"],
        semester_range=(1, 2),
    ),
    Question(
        id="t110_debugging_basics",
        mode="technical",
        difficulty="medium",
        topic="Programming Basics",
        prompt="When a simple program gives the wrong output, how do you debug it step by step?",
        keywords_required=["debug", "output"],
        keywords_optional=["trace", "print", "logic", "test case", "error"],
        semester_range=(1, 2),
    ),
    Question(
        id="t201_stack_queue",
        mode="technical",
        difficulty="easy",
        topic="Data Structures",
        prompt="What is the difference between a stack and a queue?",
        keywords_required=["stack", "queue"],
        keywords_optional=["lifo", "fifo", "push", "pop", "enqueue", "dequeue"],
        semester_range=(3, 4),
    ),
    Question(
        id="t202_linked_list_vs_array",
        mode="technical",
        difficulty="medium",
        topic="Data Structures",
        prompt="Compare an array and a linked list. When would you choose one over the other?",
        keywords_required=["array", "linked list"],
        keywords_optional=["memory", "access", "insertion", "deletion", "contiguous"],
        semester_range=(3, 4),
    ),
    Question(
        id="t203_tree_basics",
        mode="technical",
        difficulty="medium",
        topic="Data Structures",
        prompt="What is a tree data structure? Explain terms like root, parent, child, and leaf.",
        keywords_required=["tree", "root"],
        keywords_optional=["parent", "child", "leaf", "node", "hierarchy"],
        semester_range=(3, 4),
    ),
    Question(
        id="t204_time_complexity",
        mode="technical",
        difficulty="easy",
        topic="Algorithms",
        prompt="What is time complexity, and what do notations like O(n) and O(log n) mean?",
        keywords_required=["time complexity", "big o"],
        keywords_optional=["o(n)", "o(log n)", "efficiency", "performance", "growth"],
        semester_range=(3, 4),
    ),
    Question(
        id="t205_sorting_searching",
        mode="technical",
        difficulty="medium",
        topic="Algorithms",
        prompt="Explain the idea behind binary search and compare it with linear search.",
        keywords_required=["binary search", "linear search"],
        keywords_optional=["sorted", "mid", "divide", "time complexity", "comparison"],
        semester_range=(3, 4),
    ),
    Question(
        id="t206_oop_classes_objects",
        mode="technical",
        difficulty="easy",
        topic="OOP",
        prompt="What are classes and objects in object-oriented programming?",
        keywords_required=["classes", "objects"],
        keywords_optional=["attributes", "methods", "instance", "blueprint", "oop"],
        semester_range=(3, 4),
    ),
    Question(
        id="t207_inheritance_polymorphism",
        mode="technical",
        difficulty="medium",
        topic="OOP",
        prompt="What are inheritance and polymorphism in OOP? Explain with simple examples.",
        keywords_required=["inheritance", "polymorphism"],
        keywords_optional=["base class", "derived class", "override", "reuse", "behavior"],
        semester_range=(3, 4),
    ),
    Question(
        id="t208_dbms_keys_normalization",
        mode="technical",
        difficulty="easy",
        topic="DBMS",
        prompt="What are primary keys and foreign keys in DBMS, and why are they important?",
        keywords_required=["primary key", "foreign key"],
        keywords_optional=["unique", "relation", "table", "referential integrity", "database"],
        semester_range=(3, 4),
    ),
    Question(
        id="t209_sql_joins",
        mode="technical",
        difficulty="medium",
        topic="DBMS",
        prompt="What is a SQL join, and why do we use joins between tables?",
        keywords_required=["join", "tables"],
        keywords_optional=["inner join", "left join", "combine", "rows", "foreign key"],
        semester_range=(3, 4),
    ),
    Question(
        id="t210_recursion_iteration",
        mode="technical",
        difficulty="medium",
        topic="Algorithms",
        prompt="What is recursion, and how is it different from iteration?",
        keywords_required=["recursion", "iteration"],
        keywords_optional=["function calls", "base case", "loop", "stack", "repeat"],
        semester_range=(3, 4),
    ),
    Question(
        id="t301_process_vs_thread",
        mode="technical",
        difficulty="medium",
        topic="Operating Systems",
        prompt="What is the difference between a process and a thread?",
        keywords_required=["process", "thread"],
        keywords_optional=["execution", "memory", "resource", "parallelism", "scheduler"],
        semester_range=(5, 6),
    ),
    Question(
        id="t302_deadlock",
        mode="technical",
        difficulty="medium",
        topic="Operating Systems",
        prompt="What is deadlock in an operating system, and how can it be avoided or handled?",
        keywords_required=["deadlock", "processes"],
        keywords_optional=["resource", "waiting", "avoidance", "prevention", "circular wait"],
        semester_range=(5, 6),
    ),
    Question(
        id="t303_paging_virtual_memory",
        mode="technical",
        difficulty="hard",
        topic="Operating Systems",
        prompt="Explain paging and virtual memory in simple terms.",
        keywords_required=["paging", "virtual memory"],
        keywords_optional=["pages", "frames", "address space", "memory management", "swap"],
        semester_range=(5, 6),
    ),
    Question(
        id="t304_acid_transactions",
        mode="technical",
        difficulty="medium",
        topic="DBMS",
        prompt="What are ACID properties in DBMS transactions?",
        keywords_required=["acid", "transactions"],
        keywords_optional=["atomicity", "consistency", "isolation", "durability", "database"],
        semester_range=(5, 6),
    ),
    Question(
        id="t305_indexing_queries",
        mode="technical",
        difficulty="medium",
        topic="DBMS",
        prompt="What is indexing in DBMS, and how does it improve query performance?",
        keywords_required=["indexing", "query"],
        keywords_optional=["search", "speed", "table", "performance", "lookup"],
        semester_range=(5, 6),
    ),
    Question(
        id="t306_tcp_udp",
        mode="technical",
        difficulty="medium",
        topic="Computer Networks",
        prompt="What is the difference between TCP and UDP?",
        keywords_required=["tcp", "udp"],
        keywords_optional=["reliable", "connection", "speed", "packets", "transport layer"],
        semester_range=(5, 6),
    ),
    Question(
        id="t307_osi_tcpip",
        mode="technical",
        difficulty="medium",
        topic="Computer Networks",
        prompt="What is the OSI model, and why do we divide network communication into layers?",
        keywords_required=["osi model", "layers"],
        keywords_optional=["network", "transport", "application", "communication", "abstraction"],
        semester_range=(5, 6),
    ),
    Question(
        id="t308_dns_http_flow",
        mode="technical",
        difficulty="hard",
        topic="Computer Networks",
        prompt="What happens at a high level when you type a website URL in a browser?",
        keywords_required=["dns", "browser"],
        keywords_optional=["http", "request", "response", "server", "ip address"],
        semester_range=(5, 6),
    ),
    Question(
        id="t309_supervised_unsupervised",
        mode="technical",
        difficulty="medium",
        topic="Machine Learning",
        prompt="What is the difference between supervised learning and unsupervised learning?",
        keywords_required=["supervised", "unsupervised"],
        keywords_optional=["labels", "clustering", "classification", "training data", "patterns"],
        semester_range=(5, 6),
    ),
    Question(
        id="t310_overfitting_train_test",
        mode="technical",
        difficulty="hard",
        topic="Machine Learning",
        prompt="Why do we use train and test data in machine learning, and what is overfitting?",
        keywords_required=["train", "test"],
        keywords_optional=["overfitting", "generalization", "evaluation", "data split", "model"],
        semester_range=(5, 6),
    ),
    Question(
        id="t401_project_explanation",
        mode="technical",
        difficulty="medium",
        topic="Projects",
        prompt="Explain your final year or mini project clearly. What problem does it solve and how does it work?",
        keywords_required=["project", "problem"],
        keywords_optional=["solution", "workflow", "modules", "users", "result"],
        semester_range=(7, 8),
    ),
    Question(
        id="t402_requirement_analysis",
        mode="technical",
        difficulty="medium",
        topic="Software Engineering",
        prompt="What is requirement analysis in software engineering, and why is it important before development starts?",
        keywords_required=["requirements", "analysis"],
        keywords_optional=["users", "scope", "clarity", "documentation", "planning"],
        semester_range=(7, 8),
    ),
    Question(
        id="t403_sdlc_agile",
        mode="technical",
        difficulty="medium",
        topic="Software Engineering",
        prompt="What is the SDLC, and how is Agile different from a traditional waterfall approach?",
        keywords_required=["sdlc", "agile"],
        keywords_optional=["waterfall", "phases", "iteration", "planning", "delivery"],
        semester_range=(7, 8),
    ),
    Question(
        id="t404_testing_basics",
        mode="technical",
        difficulty="medium",
        topic="Software Engineering",
        prompt="What is the difference between unit testing, integration testing, and system testing?",
        keywords_required=["unit testing", "integration testing"],
        keywords_optional=["system testing", "verification", "modules", "end to end", "quality"],
        semester_range=(7, 8),
    ),
    Question(
        id="t405_version_control_code_review",
        mode="technical",
        difficulty="medium",
        topic="Software Engineering",
        prompt="Why are Git, branching, and code reviews important in team projects?",
        keywords_required=["git", "code review"],
        keywords_optional=["branching", "collaboration", "changes", "quality", "teamwork"],
        semester_range=(7, 8),
    ),
    Question(
        id="t406_api_design_basics",
        mode="technical",
        difficulty="medium",
        topic="System Design",
        prompt="What should you think about when designing a simple API for a student project?",
        keywords_required=["api", "design"],
        keywords_optional=["request", "response", "endpoint", "users", "validation"],
        semester_range=(7, 8),
    ),
    Question(
        id="t407_simple_system_design",
        mode="technical",
        difficulty="hard",
        topic="System Design",
        prompt="How would you design a simple online attendance or library management system at a high level?",
        keywords_required=["design", "system"],
        keywords_optional=["database", "users", "modules", "workflow", "scalability"],
        semester_range=(7, 8),
    ),
    Question(
        id="t408_scalability_basics",
        mode="technical",
        difficulty="hard",
        topic="System Design",
        prompt="If your project suddenly gets many more users, what changes would help it scale better?",
        keywords_required=["scale", "users"],
        keywords_optional=["load", "database", "caching", "performance", "server"],
        semester_range=(7, 8),
    ),
    Question(
        id="t409_deployment_monitoring",
        mode="technical",
        difficulty="hard",
        topic="Projects",
        prompt="After building a project, how would you deploy it and monitor whether it is working properly?",
        keywords_required=["deploy", "monitor"],
        keywords_optional=["server", "logs", "uptime", "errors", "maintenance"],
        semester_range=(7, 8),
    ),
    Question(
        id="t410_database_design_project",
        mode="technical",
        difficulty="hard",
        topic="Projects",
        prompt="How would you design the database for a student project such as placement management or attendance tracking?",
        keywords_required=["database", "design"],
        keywords_optional=["tables", "relations", "keys", "queries", "users"],
        semester_range=(7, 8),
    ),
]


HR_QUESTIONS: List[Question] = [
    Question(
        id="h1_self_intro",
        mode="hr",
        difficulty="easy",
        topic="Communication",
        prompt="Tell me about yourself and highlight experiences most relevant to this role.",
        keywords_required=["role", "experience"],
        keywords_optional=["impact", "skills", "results", "projects", "growth"],
    ),
    Question(
        id="h2_team_conflict",
        mode="hr",
        difficulty="easy",
        topic="Teamwork",
        prompt="Describe a time you had conflict in a team and how you resolved it.",
        keywords_required=["conflict", "resolution"],
        keywords_optional=["listen", "communication", "compromise", "outcome", "stakeholder"],
    ),
    Question(
        id="h3_feedback_response",
        mode="hr",
        difficulty="easy",
        topic="Growth",
        prompt="Share an example of critical feedback you received. What did you do with it?",
        keywords_required=["feedback", "improvement"],
        keywords_optional=["reflection", "action", "learning", "result", "growth"],
    ),
    Question(
        id="h11_customer_focus",
        mode="hr",
        difficulty="easy",
        topic="Customer Focus",
        prompt="Describe a time you changed your approach after learning more about a user or customer need.",
        keywords_required=["customer", "change"],
        keywords_optional=["feedback", "problem", "action", "outcome", "impact"],
    ),
    Question(
        id="h13_learning_speed",
        mode="hr",
        difficulty="easy",
        topic="Learning",
        prompt="Tell me about a time you had to learn something quickly to support a project or team goal.",
        keywords_required=["learn", "project"],
        keywords_optional=["speed", "resources", "application", "outcome", "growth"],
    ),
    Question(
        id="h14_reliability",
        mode="hr",
        difficulty="easy",
        topic="Reliability",
        prompt="How do you make sure teammates can rely on your work when deadlines or expectations are changing?",
        keywords_required=["rely", "deadlines"],
        keywords_optional=["communication", "planning", "quality", "follow-through", "trust"],
    ),
    Question(
        id="h4_prioritization",
        mode="hr",
        difficulty="medium",
        topic="Execution",
        prompt="How do you prioritize when several important tasks compete for your time?",
        keywords_required=["priority", "deadline"],
        keywords_optional=["impact", "urgency", "stakeholder", "tradeoff", "plan"],
    ),
    Question(
        id="h5_ownership",
        mode="hr",
        difficulty="medium",
        topic="Ownership",
        prompt="Describe a project where you took ownership beyond your formal responsibilities.",
        keywords_required=["ownership", "initiative"],
        keywords_optional=["problem", "solution", "collaboration", "impact", "delivery"],
    ),
    Question(
        id="h6_adaptability",
        mode="hr",
        difficulty="medium",
        topic="Adaptability",
        prompt="Tell me about a time requirements changed late. How did you adapt?",
        keywords_required=["change", "adapt"],
        keywords_optional=["communication", "risk", "replan", "stakeholder", "result"],
    ),
    Question(
        id="h7_ethics",
        mode="hr",
        difficulty="medium",
        topic="Ethics",
        prompt="How do you handle situations where speed conflicts with quality or ethics?",
        keywords_required=["quality", "ethics"],
        keywords_optional=["tradeoff", "risk", "decision", "transparency", "responsibility"],
    ),
    Question(
        id="h15_cross_functional_alignment",
        mode="hr",
        difficulty="medium",
        topic="Collaboration",
        prompt="Describe a time you had to align different teams or stakeholders who had conflicting priorities.",
        keywords_required=["align", "priorities"],
        keywords_optional=["stakeholder", "communication", "tradeoff", "decision", "outcome"],
    ),
    Question(
        id="h16_ambiguity",
        mode="hr",
        difficulty="medium",
        topic="Problem Solving",
        prompt="How do you move forward when a problem is important but the path is still unclear?",
        keywords_required=["problem", "unclear"],
        keywords_optional=["clarify", "experiment", "risk", "stakeholder", "next steps"],
    ),
    Question(
        id="h8_leadership",
        mode="hr",
        difficulty="hard",
        topic="Leadership",
        prompt="Give an example of leading without authority. How did you influence others?",
        keywords_required=["leadership", "influence"],
        keywords_optional=["alignment", "communication", "trust", "decision", "outcome"],
    ),
    Question(
        id="h9_failure_learning",
        mode="hr",
        difficulty="hard",
        topic="Resilience",
        prompt="Describe a professional failure and what you learned from it.",
        keywords_required=["failure", "learning"],
        keywords_optional=["accountability", "reflection", "improvement", "process", "result"],
    ),
    Question(
        id="h10_motivation",
        mode="hr",
        difficulty="hard",
        topic="Career Goals",
        prompt="What motivates you, and how does this role align with your long-term goals?",
        keywords_required=["motivation", "goals"],
        keywords_optional=["values", "role fit", "growth", "impact", "career"],
    ),
    Question(
        id="h12_strategic_decision",
        mode="hr",
        difficulty="hard",
        topic="Decision Making",
        prompt="Tell me about a difficult decision you made with incomplete information. How did you approach it?",
        keywords_required=["decision", "information"],
        keywords_optional=["risk", "tradeoff", "stakeholder", "result", "learning"],
    ),
    Question(
        id="h17_missed_deadline",
        mode="hr",
        difficulty="hard",
        topic="Accountability",
        prompt="Describe a time you missed a deadline or target. What did you do next?",
        keywords_required=["deadline", "target"],
        keywords_optional=["accountability", "communication", "recovery", "trust", "learning"],
    ),
    Question(
        id="h18_change_management",
        mode="hr",
        difficulty="hard",
        topic="Leadership",
        prompt="Tell me about a time you helped a team adopt a difficult change in process, tools, or direction.",
        keywords_required=["team", "change"],
        keywords_optional=["influence", "resistance", "communication", "outcome", "leadership"],
    ),
    Question(
        id="h19_strengths",
        mode="hr",
        difficulty="easy",
        topic="Self Awareness",
        prompt="What are your greatest strengths, and how have they helped you in real work situations?",
        keywords_required=["strengths", "work"],
        keywords_optional=["example", "impact", "skills", "team", "results"],
    ),
    Question(
        id="h20_weaknesses",
        mode="hr",
        difficulty="medium",
        topic="Self Awareness",
        prompt="What is one professional weakness you are actively working on, and what are you doing to improve it?",
        keywords_required=["weakness", "improve"],
        keywords_optional=["self awareness", "growth", "plan", "example", "progress"],
    ),
    Question(
        id="h21_why_company",
        mode="hr",
        difficulty="easy",
        topic="Motivation",
        prompt="Why do you want to work with this company or team?",
        keywords_required=["company", "team"],
        keywords_optional=["values", "learning", "role fit", "growth", "impact"],
    ),
    Question(
        id="h22_proud_project",
        mode="hr",
        difficulty="easy",
        topic="Achievement",
        prompt="Tell me about a project or accomplishment you are proud of.",
        keywords_required=["project", "proud"],
        keywords_optional=["challenge", "action", "result", "learning", "impact"],
    ),
    Question(
        id="h23_disagreement_manager",
        mode="hr",
        difficulty="medium",
        topic="Communication",
        prompt="Tell me about a time you disagreed with a manager or teammate. How did you handle it?",
        keywords_required=["disagree", "handle"],
        keywords_optional=["respect", "communication", "alignment", "outcome", "learning"],
    ),
    Question(
        id="h24_pressure_management",
        mode="hr",
        difficulty="medium",
        topic="Resilience",
        prompt="How do you manage pressure when multiple deadlines or problems happen at the same time?",
        keywords_required=["pressure", "deadlines"],
        keywords_optional=["prioritize", "calm", "communication", "plan", "focus"],
    ),
    Question(
        id="h25_why_hire_you",
        mode="hr",
        difficulty="hard",
        topic="Self Awareness",
        prompt="Why should we hire you for this role?",
        keywords_required=["hire", "role"],
        keywords_optional=["skills", "fit", "impact", "strengths", "contribution"],
    ),
    Question(
        id="h26_values_decision",
        mode="hr",
        difficulty="hard",
        topic="Ethics",
        prompt="Tell me about a time your values affected a difficult decision at work or college.",
        keywords_required=["values", "decision"],
        keywords_optional=["ethics", "tradeoff", "action", "result", "reflection"],
    ),
]


MIXED_QUESTIONS: List[Question] = [
    Question(
        id="m1_ai_communication",
        mode="mixed",
        difficulty="easy",
        topic="Communication",
        prompt="Explain a technical AI concept to a non-technical stakeholder with a simple example.",
        keywords_required=["explain", "stakeholder"],
        keywords_optional=["clarity", "example", "simple", "audience", "communication"],
    ),
    Question(
        id="m2_precision_business_tradeoff",
        mode="mixed",
        difficulty="easy",
        topic="AI Product",
        prompt="When would you favor precision over recall in a business setting, and why?",
        keywords_required=["precision", "recall"],
        keywords_optional=["tradeoff", "risk", "false positive", "false negative", "context"],
    ),
    Question(
        id="m3_collaboration_ml_project",
        mode="mixed",
        difficulty="easy",
        topic="Collaboration",
        prompt="Describe how you would collaborate with product and engineering teams on an ML feature.",
        keywords_required=["collaboration", "ml feature"],
        keywords_optional=["requirements", "alignment", "communication", "delivery", "stakeholders"],
    ),
    Question(
        id="m11_python_ai_project",
        mode="mixed",
        difficulty="easy",
        topic="Python",
        prompt="If you were building a small AI prototype in Python, how would you organize the code, evaluation, and iteration loop?",
        keywords_required=["python", "evaluation"],
        keywords_optional=["modules", "testing", "data", "iteration", "logging"],
    ),
    Question(
        id="m13_metric_tradeoff",
        mode="mixed",
        difficulty="easy",
        topic="AI Product",
        prompt="How would you explain the tradeoff between model accuracy and user experience to a product manager?",
        keywords_required=["accuracy", "user experience"],
        keywords_optional=["tradeoff", "latency", "errors", "expectations", "impact"],
    ),
    Question(
        id="m14_dataset_quality",
        mode="mixed",
        difficulty="easy",
        topic="Data Quality",
        prompt="Why does dataset quality matter in an AI project, and how would you explain that to a non-technical teammate?",
        keywords_required=["dataset", "quality"],
        keywords_optional=["labels", "noise", "bias", "outcomes", "communication"],
    ),
    Question(
        id="m4_llm_eval_ownership",
        mode="mixed",
        difficulty="medium",
        topic="AI Operations",
        prompt="If LLM quality drops after release, what steps would you own first?",
        keywords_required=["quality", "monitoring"],
        keywords_optional=["metrics", "logs", "rollback", "root cause", "stakeholder update"],
    ),
    Question(
        id="m5_prompt_iteration",
        mode="mixed",
        difficulty="medium",
        topic="Prompt Engineering",
        prompt="How would you run prompt iterations with tight timelines and limited data?",
        keywords_required=["prompt", "iteration"],
        keywords_optional=["hypothesis", "evaluation", "latency", "cost", "prioritize"],
    ),
    Question(
        id="m6_requirement_change",
        mode="mixed",
        difficulty="medium",
        topic="Project Management",
        prompt="How do you handle a last-minute requirement change in an AI project?",
        keywords_required=["change", "plan"],
        keywords_optional=["risk", "scope", "communication", "tradeoff", "timeline"],
    ),
    Question(
        id="m7_rag_product_impact",
        mode="mixed",
        difficulty="medium",
        topic="Product Strategy",
        prompt="How would you explain the value of RAG to product leadership?",
        keywords_required=["retrieval", "value"],
        keywords_optional=["grounding", "hallucination", "accuracy", "user trust", "impact"],
    ),
    Question(
        id="m15_experiment_design",
        mode="mixed",
        difficulty="medium",
        topic="Experimentation",
        prompt="How would you design a small experiment to test whether an AI feature truly helps users?",
        keywords_required=["experiment", "users"],
        keywords_optional=["baseline", "metric", "hypothesis", "sample", "feedback"],
    ),
    Question(
        id="m16_incident_update",
        mode="mixed",
        difficulty="medium",
        topic="Communication",
        prompt="An AI feature is failing in production. How would you communicate updates to engineers and business stakeholders?",
        keywords_required=["communication", "stakeholders"],
        keywords_optional=["status", "impact", "next steps", "clarity", "technical detail"],
    ),
    Question(
        id="m8_ai_safety_decision",
        mode="mixed",
        difficulty="hard",
        topic="AI Safety",
        prompt="You must ship quickly, but safety risks are unclear. What decision process do you follow?",
        keywords_required=["safety", "decision"],
        keywords_optional=["guardrails", "risk", "approval", "mitigation", "accountability"],
    ),
    Question(
        id="m9_bias_stakeholder",
        mode="mixed",
        difficulty="hard",
        topic="Fairness",
        prompt="A stakeholder challenges model fairness. How do you respond and act?",
        keywords_required=["bias", "stakeholder"],
        keywords_optional=["evaluation", "evidence", "mitigation", "communication", "follow-up"],
    ),
    Question(
        id="m10_growth_plan",
        mode="mixed",
        difficulty="hard",
        topic="Growth",
        prompt="What is your 90-day plan to improve both technical impact and team collaboration?",
        keywords_required=["plan", "impact"],
        keywords_optional=["milestones", "learning", "communication", "execution", "outcomes"],
    ),
    Question(
        id="m12_rollout_strategy",
        mode="mixed",
        difficulty="hard",
        topic="AI Delivery",
        prompt="How would you roll out a new AI feature safely while still moving fast?",
        keywords_required=["rollout", "risk"],
        keywords_optional=["metrics", "guardrails", "rollback", "staged release", "communication"],
    ),
    Question(
        id="m17_cost_quality_balance",
        mode="mixed",
        difficulty="hard",
        topic="AI Strategy",
        prompt="How would you balance model quality against infrastructure cost when recommending an AI solution to leadership?",
        keywords_required=["quality", "cost"],
        keywords_optional=["tradeoff", "latency", "roi", "scale", "recommendation"],
    ),
    Question(
        id="m18_governance_rollout",
        mode="mixed",
        difficulty="hard",
        topic="AI Governance",
        prompt="What governance checks would you add before launching an AI system that affects important user decisions?",
        keywords_required=["governance", "checks"],
        keywords_optional=["risk", "audit", "approval", "fairness", "monitoring"],
    ),
]

QUESTIONS_BY_MODE: Dict[InterviewMode, List[Question]] = {
    "technical": TECHNICAL_QUESTIONS,
    "hr": HR_QUESTIONS,
    "mixed": TECHNICAL_QUESTIONS + HR_QUESTIONS,
}


def semester_band_for(semester: int) -> SemesterRange:
    normalized = max(1, min(8, int(semester)))
    band_start = normalized if normalized % 2 == 1 else normalized - 1
    band_end = min(8, band_start + 1)
    return band_start, band_end


def question_matches_semester(question: Question, semester: int) -> bool:
    band_start, band_end = semester_band_for(semester)
    range_start, range_end = question.semester_range or (1, 8)
    return range_start <= band_start and band_end <= range_end


def difficulty_targets_for_semester(semester: int, total_questions: int = 10) -> Dict[Difficulty, int]:
    normalized = max(1, min(8, int(semester)))
    if normalized <= 2:
        ratios = {"easy": 0.6, "medium": 0.4, "hard": 0.0}
    elif normalized <= 4:
        ratios = {"easy": 0.5, "medium": 0.5, "hard": 0.0}
    elif normalized <= 6:
        ratios = {"easy": 0.0, "medium": 0.6, "hard": 0.4}
    else:
        ratios = {"easy": 0.0, "medium": 0.4, "hard": 0.6}

    counts: Dict[Difficulty, int] = {difficulty: int(total_questions * ratios[difficulty]) for difficulty in ratios}
    assigned = sum(counts.values())
    remainders = sorted(
        [((ratios[difficulty] * total_questions) - counts[difficulty], difficulty) for difficulty in ratios],
        reverse=True,
    )

    for _, difficulty in remainders:
        if assigned >= total_questions:
            break
        if ratios[difficulty] <= 0:
            continue
        counts[difficulty] += 1
        assigned += 1

    return counts


def get_questions_by_id(mode: InterviewMode = "technical") -> Dict[str, Question]:
    """Return a dict for quick lookup by question id for a mode."""
    return {q.id: q for q in QUESTIONS_BY_MODE[mode]}


def get_all_questions(mode: InterviewMode = "technical") -> List[Question]:
    """Return all questions for a mode in the order defined."""
    return list(QUESTIONS_BY_MODE[mode])


def get_questions_by_difficulty(
    mode: InterviewMode = "technical",
    difficulty: Difficulty = "easy",
) -> List[Question]:
    """Return all questions in a mode filtered by difficulty."""
    return [question for question in QUESTIONS_BY_MODE[mode] if question.difficulty == difficulty]


def get_questions_for_semester(
    mode: InterviewMode = "technical",
    semester: int = 4,
    difficulty: Optional[Difficulty] = None,
) -> List[Question]:
    questions = [question for question in QUESTIONS_BY_MODE[mode] if question_matches_semester(question, semester)]
    if difficulty is not None:
        questions = [question for question in questions if question.difficulty == difficulty]
    return questions
