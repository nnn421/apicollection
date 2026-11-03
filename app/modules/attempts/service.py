import random

from app.core.exceptions import ApiError, not_found
from app.db.memory import AttemptAnswer, MemoryStore, QuizAttempt, QuizQuestion, new_id, utcnow
from app.modules.attempts.schemas import AnswerResult, AnswerSubmit, AttemptOut, AttemptResult
from app.modules.quizzes.schemas import QuestionSourceOut
from app.modules.quizzes.service import QuizService, public


class AttemptService:
    def __init__(self, store: MemoryStore, user_id: str):
        self.store = store
        self.user_id = user_id
        self.quizzes = QuizService(store, user_id)

    def get_owned(self, attempt_id: str) -> QuizAttempt:
        attempt = self.store.attempts.get(attempt_id)
        if attempt is None or attempt.user_id != self.user_id:
            raise not_found("Attempt")
        return attempt

    def start(self, quiz_id: str, shuffle: bool = False) -> AttemptOut:
        """Saves the question order and start time (FR-ATTEMPT-01)."""
        quiz = self.quizzes.get_owned(quiz_id)
        order = [q.id for q in quiz.questions]
        if shuffle:
            random.shuffle(order)
        attempt = QuizAttempt(id=new_id(), user_id=self.user_id, quiz_id=quiz.id, question_order=order, started_at=utcnow())
        self.store.attempts[attempt.id] = attempt
        return self._out(attempt)

    def get(self, attempt_id: str) -> AttemptOut:
        return self._out(self.get_owned(attempt_id))

    def answer(self, attempt_id: str, data: AnswerSubmit) -> AnswerResult:
        """Graded on the server (FR-ATTEMPT-02); each question can be answered once per attempt."""
        attempt = self.get_owned(attempt_id)
        if attempt.completed_at is not None:
            raise ApiError(409, "ATTEMPT_COMPLETED", "This attempt is already completed.")
        question = self._questions(attempt).get(data.question_id)
        if question is None:
            raise not_found("Question")
        if any(a.question_id == question.id for a in attempt.answers):
            raise ApiError(409, "ALREADY_ANSWERED", "This question was already answered in this attempt.")
        is_correct = data.selected_index == question.correct_index
        attempt.answers.append(AttemptAnswer(question.id, data.selected_index, is_correct, utcnow()))
        return _result(question, data.selected_index)

    def complete(self, attempt_id: str) -> AttemptResult:
        attempt = self.get_owned(attempt_id)
        if attempt.completed_at is None:
            attempt.completed_at = utcnow()
        questions = self._questions(attempt)
        answered = {a.question_id: a for a in attempt.answers}
        correct = sum(1 for a in attempt.answers if a.is_correct)
        total = len(attempt.question_order)
        to_review = [
            _result(questions[qid], answered[qid].selected_index if qid in answered else None)
            for qid in attempt.question_order
            if not (qid in answered and answered[qid].is_correct)
        ]
        return AttemptResult(
            attempt_id=attempt.id,
            quiz_id=attempt.quiz_id,
            total_questions=total,
            answered_count=len(attempt.answers),
            correct_count=correct,
            score_percent=round(correct / total * 100, 1) if total else 0.0,
            started_at=attempt.started_at,
            completed_at=attempt.completed_at,
            to_review=to_review,
        )

    def _questions(self, attempt: QuizAttempt) -> dict[str, QuizQuestion]:
        return {q.id: q for q in self.store.quizzes[attempt.quiz_id].questions}

    def _out(self, attempt: QuizAttempt) -> AttemptOut:
        questions = self._questions(attempt)
        return AttemptOut(
            id=attempt.id,
            quiz_id=attempt.quiz_id,
            questions=[public(questions[qid]) for qid in attempt.question_order],
            answered_count=len(attempt.answers),
            started_at=attempt.started_at,
            completed_at=attempt.completed_at,
        )


def _result(q: QuizQuestion, selected_index: int | None) -> AnswerResult:
    is_correct = selected_index == q.correct_index
    source = None
    if not is_correct and q.source is not None:
        source = QuestionSourceOut(document_id=q.source.document_id, page_number=q.source.page_number)
    return AnswerResult(
        question_id=q.id,
        selected_index=selected_index,
        is_correct=is_correct,
        correct_index=q.correct_index,
        explanation=q.explanation,
        source=source,
    )
