"""In-memory store. Data resets on restart; a demo dataset is seeded for `demo-user`.

Field names follow the spec's tables (spec 12.3) so this can later be swapped for
SQLAlchemy repositories on Supabase PostgreSQL.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

Difficulty = Literal["EASY", "MEDIUM", "HARD"]
DEMO_USER = "demo-user"


def new_id() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Subject:
    id: str
    user_id: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


@dataclass
class QuestionSource:
    document_id: str | None
    page_number: int


@dataclass
class QuizQuestion:
    id: str
    question: str
    options: list[str]
    correct_index: int
    explanation: str
    difficulty: Difficulty
    source: QuestionSource | None


@dataclass
class QuizSet:
    id: str
    user_id: str
    subject_id: str
    title: str
    status: str
    questions: list[QuizQuestion]
    created_at: datetime


@dataclass
class AttemptAnswer:
    question_id: str
    selected_index: int
    is_correct: bool
    answered_at: datetime


@dataclass
class QuizAttempt:
    id: str
    user_id: str
    quiz_id: str
    question_order: list[str]
    started_at: datetime
    answers: list[AttemptAnswer] = field(default_factory=list)
    completed_at: datetime | None = None


class MemoryStore:
    def __init__(self, seed: bool = True) -> None:
        self.subjects: dict[str, Subject] = {}
        self.quizzes: dict[str, QuizSet] = {}
        self.attempts: dict[str, QuizAttempt] = {}
        if seed:
            self._seed()

    def _seed(self) -> None:
        now = utcnow()
        subject = Subject(
            id="11111111-1111-4111-8111-111111111111",
            user_id=DEMO_USER,
            name="Công nghệ phần mềm",
            description="Chương 2 - Software Processes",
            created_at=now,
            updated_at=now,
        )
        self.subjects[subject.id] = subject
        quiz = QuizSet(
            id="22222222-2222-4222-8222-222222222222",
            user_id=DEMO_USER,
            subject_id=subject.id,
            title="Software Processes - Quiz 1",
            status="READY",
            created_at=now,
            questions=[
                QuizQuestion(
                    id="33333333-3333-4333-8333-333333333331",
                    question="Which process model completes each phase fully before starting the next?",
                    options=["Waterfall", "Incremental", "Scrum", "Spiral"],
                    correct_index=0,
                    explanation="The waterfall model is plan-driven: each phase must finish before the next one begins.",
                    difficulty="EASY",
                    source=QuestionSource(None, 12),
                ),
                QuizQuestion(
                    id="33333333-3333-4333-8333-333333333332",
                    question="What is the main benefit of incremental development?",
                    options=[
                        "No documentation is needed",
                        "Customer feedback is obtained earlier",
                        "The system structure never degrades",
                        "It requires no planning",
                    ],
                    correct_index=1,
                    explanation="Delivering increments lets customers comment on working software early.",
                    difficulty="MEDIUM",
                    source=QuestionSource(None, 15),
                ),
                QuizQuestion(
                    id="33333333-3333-4333-8333-333333333333",
                    question="Which activity checks that the software conforms to its specification?",
                    options=["Software specification", "Software evolution", "Software validation", "Software design"],
                    correct_index=2,
                    explanation="Validation (V&V) shows that a system conforms to its specification and meets customer needs.",
                    difficulty="MEDIUM",
                    source=QuestionSource(None, 31),
                ),
            ],
        )
        self.quizzes[quiz.id] = quiz


store = MemoryStore()


def get_store() -> MemoryStore:
    return store
