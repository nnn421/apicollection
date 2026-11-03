# DuoQuiz API

FastAPI REST API for DuoQuiz with two API collections, documented and testable via Swagger UI.
Follows the DuoQuiz specification v1.1 (sections 6, 12 and 13).

## Collections

| Collection | Method | Endpoint | Purpose |
|---|---|---|---|
| **Subjects** | GET | `/api/v1/subjects?search=` | List my subjects |
| | POST | `/api/v1/subjects` | Create a subject |
| | GET | `/api/v1/subjects/{subjectId}` | Get a subject |
| | PATCH | `/api/v1/subjects/{subjectId}` | Rename / update |
| | DELETE | `/api/v1/subjects/{subjectId}` | Delete (with its quizzes) |
| **Quizzes** | GET | `/api/v1/quizzes?subjectId=` | List my quizzes |
| | POST | `/api/v1/quizzes` | Create a quiz in a subject |
| | GET | `/api/v1/quizzes/{quizId}` | Get a quiz (answers hidden) |
| | DELETE | `/api/v1/quizzes/{quizId}` | Delete a quiz |
| | POST | `/api/v1/quizzes/{quizId}/attempts` | Start an attempt |
| | GET | `/api/v1/attempts/{attemptId}` | Get an attempt |
| | POST | `/api/v1/attempts/{attemptId}/answers` | Submit an answer (graded on server) |
| | POST | `/api/v1/attempts/{attemptId}/complete` | Finish and get the score |

- Swagger UI: `/docs` · OpenAPI JSON: `/openapi.json` · health: `/health`
- **Auth (demo):** optional `Authorization: Bearer <any-string>`; the token is used as the user id, and each user only sees their own data. Without a token you are `demo-user`, which has a seeded subject and quiz. This stands in for Supabase Auth JWT verification.
- **Storage:** in-memory, resets on restart.
- **Errors:** `{ "error": { "code", "message", "requestId", "details" } }`
- **Rules:** each question has exactly 4 distinct options, `correctIndex` 0..3 and an explanation; wrong answers return the source page.

## Project layout

```
app/
  main.py                 FastAPI app, Swagger config
  api/v1/routes/          subjects.py, quizzes.py, attempts.py, health.py
  core/                   error envelope, demo auth, base schema
  db/memory.py            in-memory store + seed data
  modules/{subjects,quizzes,attempts}/   schemas.py, service.py
tests/test_api.py         pytest
```

## Run locally

```bash
python -m venv .venv
.venv/Scripts/activate          # Windows (macOS/Linux: source .venv/bin/activate)
pip install -r requirements-dev.txt
uvicorn app.main:app --reload   # http://localhost:8000/docs
pytest
```

## Deploy (Render)

`render.yaml` is included: on Render choose **New → Blueprint**, select this repo, and apply.
