from datetime import datetime

from pydantic import Field

from app.core.schemas import CamelModel


class SubjectCreate(CamelModel):
    name: str = Field(min_length=1, max_length=120, examples=["Cấu trúc dữ liệu và giải thuật"])
    description: str | None = Field(default=None, max_length=500, examples=["Học kỳ 1 - 2026"])


class SubjectUpdate(CamelModel):
    name: str | None = Field(default=None, min_length=1, max_length=120, examples=["CTDL & GT"])
    description: str | None = Field(default=None, max_length=500)


class SubjectOut(CamelModel):
    id: str = Field(examples=["11111111-1111-4111-8111-111111111111"])
    name: str
    description: str | None
    quiz_count: int = Field(description="Number of quizzes in this subject")
    created_at: datetime
    updated_at: datetime
