from datetime import datetime

from pydantic import Field

from app.core.schemas import CamelModel
from app.modules.quizzes.schemas import PublicQuestion, QuestionSourceOut


class AttemptOut(CamelModel):
    id: str
    quiz_id: str
    questions: list[PublicQuestion] = Field(description="Questions in the order they must be shown")
    answered_count: int
    started_at: datetime
    completed_at: datetime | None


class AnswerSubmit(CamelModel):
    question_id: str = Field(examples=["33333333-3333-4333-8333-333333333331"])
    selected_index: int = Field(ge=0, le=3, examples=[1])


class AnswerResult(CamelModel):
    question_id: str
    selected_index: int | None = Field(description="null if the question was not answered")
    is_correct: bool
    correct_index: int
    explanation: str
    source: QuestionSourceOut | None = Field(
        description="Only set for wrong answers, so the app can open the source page (FR-ATTEMPT-03)"
    )


class AttemptResult(CamelModel):
    attempt_id: str
    quiz_id: str
    total_questions: int
    answered_count: int
    correct_count: int
    score_percent: float = Field(examples=[66.7])
    started_at: datetime
    completed_at: datetime
    to_review: list[AnswerResult] = Field(description="Wrong or unanswered questions to review")
