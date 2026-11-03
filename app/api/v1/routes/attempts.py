from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies import attempt_service
from app.core.exceptions import error_responses
from app.modules.attempts.schemas import AnswerResult, AnswerSubmit, AttemptOut, AttemptResult
from app.modules.attempts.service import AttemptService

# Attempts belong to the Quizzes collection, so they share its Swagger tag.
router = APIRouter(prefix="/attempts", tags=["Quizzes"])


@router.get("/{attemptId}", response_model=AttemptOut, summary="Get an attempt", responses=error_responses(404, 422))
def get_attempt(attemptId: UUID, svc: AttemptService = Depends(attempt_service)):
    return svc.get(str(attemptId))


@router.post("/{attemptId}/answers", response_model=AnswerResult, status_code=status.HTTP_201_CREATED,
             summary="Submit an answer", responses=error_responses(404, 409, 422))
def submit_answer(attemptId: UUID, body: AnswerSubmit, svc: AttemptService = Depends(attempt_service)):
    """Graded on the server. A wrong answer returns the source page to open (FR-ATTEMPT-02/03).

    409 if the question was already answered or the attempt is completed.
    """
    return svc.answer(str(attemptId), body)


@router.post("/{attemptId}/complete", response_model=AttemptResult, summary="Complete an attempt",
             responses=error_responses(404, 422))
def complete_attempt(attemptId: UUID, svc: AttemptService = Depends(attempt_service)):
    """Returns the score and the wrong/unanswered questions to review. Safe to call again."""
    return svc.complete(str(attemptId))
