from fastapi import Depends

from app.core.security import get_current_user_id
from app.db.memory import MemoryStore, get_store
from app.modules.attempts.service import AttemptService
from app.modules.quizzes.service import QuizService
from app.modules.subjects.service import SubjectService


def subject_service(store: MemoryStore = Depends(get_store), user_id: str = Depends(get_current_user_id)) -> SubjectService:
    return SubjectService(store, user_id)


def quiz_service(store: MemoryStore = Depends(get_store), user_id: str = Depends(get_current_user_id)) -> QuizService:
    return QuizService(store, user_id)


def attempt_service(store: MemoryStore = Depends(get_store), user_id: str = Depends(get_current_user_id)) -> AttemptService:
    return AttemptService(store, user_id)
