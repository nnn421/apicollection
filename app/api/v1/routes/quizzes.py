from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.dependencies import attempt_service, quiz_service
from app.core.exceptions import error_responses
from app.modules.attempts.schemas import AttemptOut
from app.modules.attempts.service import AttemptService
from app.modules.quizzes.schemas import QuizCreate, QuizDetail, QuizSummary
from app.modules.quizzes.service import QuizService

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.get("", response_model=list[QuizSummary], summary="List my quizzes", responses=error_responses(404, 422))
def list_quizzes(
    subjectId: UUID | None = Query(default=None, description="Only quizzes of this subject"),
    svc: QuizService = Depends(quiz_service),
):
    return svc.list(str(subjectId) if subjectId else None)


@router.post("", response_model=QuizDetail, status_code=status.HTTP_201_CREATED, summary="Create a quiz in a subject",
             responses=error_responses(404, 422))
def create_quiz(body: QuizCreate, svc: QuizService = Depends(quiz_service)):
    """Each question needs exactly 4 distinct options, `correctIndex` 0..3 and an explanation (FR-QUIZ-02/03)."""
    return svc.create(body)


@router.get("/{quizId}", response_model=QuizDetail, summary="Get a quiz", responses=error_responses(404, 422))
def get_quiz(quizId: UUID, svc: QuizService = Depends(quiz_service)):
    """Correct answers and explanations stay hidden until the question is answered in an attempt."""
    return svc.get(str(quizId))


@router.delete("/{quizId}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a quiz",
               responses=error_responses(404, 422))
def delete_quiz(quizId: UUID, svc: QuizService = Depends(quiz_service)):
    """Also deletes the quiz's attempts."""
    svc.delete(str(quizId))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{quizId}/attempts", response_model=AttemptOut, status_code=status.HTTP_201_CREATED,
             summary="Start an attempt", responses=error_responses(404, 422))
def start_attempt(
    quizId: UUID,
    shuffle: bool = Query(default=False, description="Shuffle the question order"),
    svc: AttemptService = Depends(attempt_service),
):
    """Saves the question order and start time (FR-ATTEMPT-01)."""
    return svc.start(str(quizId), shuffle)
