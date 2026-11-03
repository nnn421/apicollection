from app.core.exceptions import not_found
from app.db.memory import MemoryStore, QuestionSource, QuizQuestion, QuizSet, new_id, utcnow
from app.modules.quizzes.schemas import PublicQuestion, QuizCreate, QuizDetail, QuizSummary
from app.modules.subjects.service import SubjectService


class QuizService:
    def __init__(self, store: MemoryStore, user_id: str):
        self.store = store
        self.user_id = user_id
        self.subjects = SubjectService(store, user_id)

    def get_owned(self, quiz_id: str) -> QuizSet:
        quiz = self.store.quizzes.get(quiz_id)
        if quiz is None or quiz.user_id != self.user_id:
            raise not_found("Quiz")
        return quiz

    def list(self, subject_id: str | None = None) -> list[QuizSummary]:
        if subject_id:
            self.subjects.get_owned(subject_id)
        items = [
            q for q in self.store.quizzes.values()
            if q.user_id == self.user_id and (not subject_id or q.subject_id == subject_id)
        ]
        items.sort(key=lambda q: q.created_at, reverse=True)
        return [summary(q) for q in items]

    def get(self, quiz_id: str) -> QuizDetail:
        quiz = self.get_owned(quiz_id)
        return QuizDetail(**summary(quiz).model_dump(), questions=[public(q) for q in quiz.questions])

    def create(self, data: QuizCreate) -> QuizDetail:
        self.subjects.get_owned(data.subject_id)
        quiz = QuizSet(
            id=new_id(),
            user_id=self.user_id,
            subject_id=data.subject_id,
            title=data.title.strip(),
            status="READY",
            created_at=utcnow(),
            questions=[
                QuizQuestion(
                    id=new_id(),
                    question=q.question.strip(),
                    options=q.options,
                    correct_index=q.correct_index,
                    explanation=q.explanation.strip(),
                    difficulty=q.difficulty,
                    source=QuestionSource(q.source.document_id, q.source.page_number) if q.source else None,
                )
                for q in data.questions
            ],
        )
        self.store.quizzes[quiz.id] = quiz
        return self.get(quiz.id)

    def delete(self, quiz_id: str) -> None:
        self.get_owned(quiz_id)
        for attempt_id in [a.id for a in self.store.attempts.values() if a.quiz_id == quiz_id]:
            del self.store.attempts[attempt_id]
        del self.store.quizzes[quiz_id]


def summary(q: QuizSet) -> QuizSummary:
    return QuizSummary(
        id=q.id,
        subject_id=q.subject_id,
        title=q.title,
        status=q.status,
        question_count=len(q.questions),
        created_at=q.created_at,
    )


def public(q: QuizQuestion) -> PublicQuestion:
    return PublicQuestion(id=q.id, question=q.question, options=q.options, difficulty=q.difficulty)
