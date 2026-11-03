import pytest
from fastapi.testclient import TestClient

from app.db.memory import MemoryStore, get_store
from app.main import app

SEED_SUBJECT = "11111111-1111-4111-8111-111111111111"
SEED_QUIZ = "22222222-2222-4222-8222-222222222222"
Q1, Q2, Q3 = (f"33333333-3333-4333-8333-33333333333{i}" for i in (1, 2, 3))


@pytest.fixture
def client():
    store = MemoryStore()
    app.dependency_overrides[get_store] = lambda: store
    yield TestClient(app)
    app.dependency_overrides.clear()


def quiz_body(subject_id: str, **question_overrides):
    question = {
        "question": "O(n log n)?",
        "options": ["Bubble", "Merge", "Selection", "Insertion"],
        "correctIndex": 1,
        "explanation": "Merge sort",
        "source": {"pageNumber": 4},
        **question_overrides,
    }
    return {"subjectId": subject_id, "title": "Sorting", "questions": [question]}


def test_health_and_docs(client):
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/docs").status_code == 200
    paths = client.get("/openapi.json").json()["paths"]
    assert "/api/v1/subjects" in paths and "/api/v1/quizzes" in paths


def test_subject_crud(client):
    created = client.post("/api/v1/subjects", json={"name": "  CTDL  ", "description": "HK1"})
    assert created.status_code == 201
    sid = created.json()["id"]
    assert created.json()["name"] == "CTDL"
    assert created.json()["quizCount"] == 0

    assert client.patch(f"/api/v1/subjects/{sid}", json={"name": "CTDL và GT"}).json()["name"] == "CTDL và GT"
    assert [s["id"] for s in client.get("/api/v1/subjects", params={"search": "ctdl"}).json()] == [sid]

    assert client.delete(f"/api/v1/subjects/{sid}").status_code == 204
    assert client.get(f"/api/v1/subjects/{sid}").json()["error"]["code"] == "SUBJECT_NOT_FOUND"


def test_subject_validation_uses_error_envelope(client):
    res = client.post("/api/v1/subjects", json={"name": ""})
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"
    assert res.json()["error"]["requestId"].startswith("req_")
    assert client.get("/api/v1/subjects/not-a-uuid").status_code == 422


def test_users_are_isolated(client):
    alice = {"Authorization": "Bearer alice"}
    assert client.get("/api/v1/subjects", headers=alice).json() == []
    assert client.get(f"/api/v1/quizzes/{SEED_QUIZ}", headers=alice).status_code == 404
    assert client.post("/api/v1/quizzes", json=quiz_body(SEED_SUBJECT), headers=alice).status_code == 404


@pytest.mark.parametrize(
    "override, field",
    [
        ({"options": ["a", "A ", "b", "c"]}, "options"),  # duplicate (case-insensitive)
        ({"options": ["a", "b", "c"]}, "options"),  # not exactly 4
        ({"correctIndex": 4}, "correctIndex"),
        ({"correctIndex": -1}, "correctIndex"),
        ({"explanation": ""}, "explanation"),
    ],
)
def test_quiz_question_rules(client, override, field):
    res = client.post("/api/v1/quizzes", json=quiz_body(SEED_SUBJECT, **override))
    assert res.status_code == 422
    assert any(field in f["field"] for f in res.json()["error"]["details"]["fields"])


def test_quiz_hides_answers_and_cascades(client):
    created = client.post("/api/v1/quizzes", json=quiz_body(SEED_SUBJECT))
    assert created.status_code == 201
    question = created.json()["questions"][0]
    assert "correctIndex" not in question and "explanation" not in question
    assert client.get(f"/api/v1/subjects/{SEED_SUBJECT}").json()["quizCount"] == 2
    assert len(client.get("/api/v1/quizzes", params={"subjectId": SEED_SUBJECT}).json()) == 2

    client.delete(f"/api/v1/subjects/{SEED_SUBJECT}")
    assert client.get("/api/v1/quizzes").json() == []


def test_attempt_flow(client):
    attempt = client.post(f"/api/v1/quizzes/{SEED_QUIZ}/attempts", params={"shuffle": True}).json()
    aid = attempt["id"]
    assert sorted(q["id"] for q in attempt["questions"]) == [Q1, Q2, Q3]

    wrong = client.post(f"/api/v1/attempts/{aid}/answers", json={"questionId": Q1, "selectedIndex": 2}).json()
    assert wrong["isCorrect"] is False and wrong["correctIndex"] == 0
    assert wrong["source"] == {"documentId": None, "pageNumber": 12}

    right = client.post(f"/api/v1/attempts/{aid}/answers", json={"questionId": Q2, "selectedIndex": 1}).json()
    assert right["isCorrect"] is True and right["source"] is None

    dup = client.post(f"/api/v1/attempts/{aid}/answers", json={"questionId": Q1, "selectedIndex": 0})
    assert dup.status_code == 409 and dup.json()["error"]["code"] == "ALREADY_ANSWERED"

    result = client.post(f"/api/v1/attempts/{aid}/complete").json()
    assert (result["totalQuestions"], result["answeredCount"], result["correctCount"]) == (3, 2, 1)
    assert result["scorePercent"] == 33.3
    assert [r["questionId"] for r in result["toReview"]] == [
        q["id"] for q in attempt["questions"] if q["id"] != Q2
    ]
    unanswered = next(r for r in result["toReview"] if r["questionId"] == Q3)
    assert unanswered["selectedIndex"] is None

    late = client.post(f"/api/v1/attempts/{aid}/answers", json={"questionId": Q3, "selectedIndex": 2})
    assert late.status_code == 409 and late.json()["error"]["code"] == "ATTEMPT_COMPLETED"
    assert client.get(f"/api/v1/attempts/{aid}").json()["completedAt"] is not None


def test_attempt_unknown_question_and_other_user(client):
    aid = client.post(f"/api/v1/quizzes/{SEED_QUIZ}/attempts").json()["id"]
    res = client.post(
        f"/api/v1/attempts/{aid}/answers",
        json={"questionId": "00000000-0000-4000-8000-000000000000", "selectedIndex": 0},
    )
    assert res.json()["error"]["code"] == "QUESTION_NOT_FOUND"
    assert client.get(f"/api/v1/attempts/{aid}", headers={"Authorization": "Bearer bob"}).status_code == 404
