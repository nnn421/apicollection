from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.v1.router import api_router
from app.api.v1.routes import health
from app.core.exceptions import register_exception_handlers

DESCRIPTION = """
REST API for **DuoQuiz**: study subjects and the multiple-choice quizzes made from them.

**Collections**
- **Subjects**: create, list, rename and delete your study subjects.
- **Quizzes**: create quizzes inside a subject, then take them: start an attempt,
  submit answers (graded on the server) and complete it to get your score.

**Auth (demo):** optional. Click **Authorize** and enter any token (e.g. `alice`) to act as that user;
each token only sees its own data. Without a token you are `demo-user`, which has a seeded sample
subject and quiz. (Stand-in for Supabase Auth JWT.)

**Storage:** in-memory, so data resets when the server restarts.

**Errors** use one envelope: `{"error": {"code", "message", "requestId", "details"}}`.

**Quick try:** `GET /api/v1/quizzes` → `POST /api/v1/quizzes/22222222-2222-4222-8222-222222222222/attempts`
→ `POST /api/v1/attempts/{attemptId}/answers` → `POST /api/v1/attempts/{attemptId}/complete`.
"""

app = FastAPI(
    title="DuoQuiz API",
    version="1.0.0",
    description=DESCRIPTION,
    swagger_ui_parameters={"persistAuthorization": True, "displayRequestDuration": True, "tryItOutEnabled": True},
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
register_exception_handlers(app)

app.include_router(health.router)
app.include_router(api_router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/docs")
