from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.dependencies import subject_service
from app.core.exceptions import error_responses
from app.modules.subjects.schemas import SubjectCreate, SubjectOut, SubjectUpdate
from app.modules.subjects.service import SubjectService

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("", response_model=list[SubjectOut], summary="List my subjects")
def list_subjects(
    search: str | None = Query(default=None, max_length=120, description="Case-insensitive name search"),
    svc: SubjectService = Depends(subject_service),
):
    """Newest first."""
    return svc.list(search)


@router.post("", response_model=SubjectOut, status_code=status.HTTP_201_CREATED, summary="Create a subject",
             responses=error_responses(422))
def create_subject(body: SubjectCreate, svc: SubjectService = Depends(subject_service)):
    return svc.create(body)


@router.get("/{subjectId}", response_model=SubjectOut, summary="Get a subject", responses=error_responses(404, 422))
def get_subject(subjectId: UUID, svc: SubjectService = Depends(subject_service)):
    return svc.get(str(subjectId))


@router.patch("/{subjectId}", response_model=SubjectOut, summary="Rename / update a subject",
              responses=error_responses(404, 422))
def update_subject(subjectId: UUID, body: SubjectUpdate, svc: SubjectService = Depends(subject_service)):
    return svc.update(str(subjectId), body)


@router.delete("/{subjectId}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a subject",
               responses=error_responses(404, 422))
def delete_subject(subjectId: UUID, svc: SubjectService = Depends(subject_service)):
    """Also deletes the subject's quizzes and their attempts."""
    svc.delete(str(subjectId))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
