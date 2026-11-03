from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator

from app.core.schemas import CamelModel

Difficulty = Literal["EASY", "MEDIUM", "HARD"]


class QuestionSourceIn(CamelModel):
    document_id: str | None = Field(default=None, description="Source document id, if any")
    page_number: int = Field(ge=1, examples=[4], description="Page in the source document")


class QuestionCreate(CamelModel):
    question: str = Field(min_length=1, max_length=500, examples=["Thuật toán nào có độ phức tạp trung bình O(n log n)?"])
    options: list[str] = Field(
        min_length=4,
        max_length=4,
        description="Exactly 4 distinct options (FR-QUIZ-02)",
        examples=[["Bubble sort", "Merge sort", "Selection sort", "Insertion sort"]],
    )
    correct_index: int = Field(ge=0, le=3, examples=[1])
    explanation: str = Field(min_length=1, max_length=1000, examples=["Merge sort chia đôi mảng và trộn lại, luôn O(n log n)."])
    difficulty: Difficulty = "MEDIUM"
    source: QuestionSourceIn | None = None

    @field_validator("options")
    @classmethod
    def _distinct_options(cls, options: list[str]) -> list[str]:
        cleaned = [o.strip() for o in options]
        if any(not o or len(o) > 200 for o in cleaned):
            raise ValueError("each option must be 1-200 characters")
        if len({o.lower() for o in cleaned}) != len(cleaned):
            raise ValueError("options must be distinct")
        return cleaned


class QuizCreate(CamelModel):
    subject_id: str = Field(examples=["11111111-1111-4111-8111-111111111111"], description="Subject that owns the quiz")
    title: str = Field(min_length=1, max_length=150, examples=["Sorting - Quiz 1"])
    questions: list[QuestionCreate] = Field(min_length=1, max_length=50)


class QuestionSourceOut(CamelModel):
    document_id: str | None
    page_number: int


class PublicQuestion(CamelModel):
    """Question as shown to a student: correct answer and explanation are hidden."""

    id: str
    question: str
    options: list[str]
    difficulty: Difficulty


class QuizSummary(CamelModel):
    id: str = Field(examples=["22222222-2222-4222-8222-222222222222"])
    subject_id: str
    title: str
    status: str = Field(examples=["READY"])
    question_count: int
    created_at: datetime


class QuizDetail(QuizSummary):
    questions: list[PublicQuestion]
