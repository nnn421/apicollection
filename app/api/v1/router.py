from fastapi import APIRouter

from app.api.v1.routes import attempts, quizzes, subjects

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(subjects.router)
api_router.include_router(quizzes.router)
api_router.include_router(attempts.router)
