from app.core.exceptions import ApiError, not_found
from app.db.memory import MemoryStore, Subject, new_id, utcnow
from app.modules.subjects.schemas import SubjectCreate, SubjectOut, SubjectUpdate


class SubjectService:
    def __init__(self, store: MemoryStore, user_id: str):
        self.store = store
        self.user_id = user_id

    def get_owned(self, subject_id: str) -> Subject:
        """Ownership check (FR-AUTH-05): other users' subjects look like they don't exist."""
        subject = self.store.subjects.get(subject_id)
        if subject is None or subject.user_id != self.user_id:
            raise not_found("Subject")
        return subject

    def list(self, search: str | None = None) -> list[SubjectOut]:
        q = (search or "").strip().lower()
        items = [
            s for s in self.store.subjects.values()
            if s.user_id == self.user_id and (not q or q in s.name.lower())
        ]
        items.sort(key=lambda s: s.created_at, reverse=True)
        return [self._out(s) for s in items]

    def get(self, subject_id: str) -> SubjectOut:
        return self._out(self.get_owned(subject_id))

    def create(self, data: SubjectCreate) -> SubjectOut:
        now = utcnow()
        subject = Subject(
            id=new_id(),
            user_id=self.user_id,
            name=_clean_name(data.name),
            description=(data.description or "").strip() or None,
            created_at=now,
            updated_at=now,
        )
        self.store.subjects[subject.id] = subject
        return self._out(subject)

    def update(self, subject_id: str, data: SubjectUpdate) -> SubjectOut:
        subject = self.get_owned(subject_id)
        fields = data.model_fields_set
        if "name" in fields:
            if data.name is None:
                raise ApiError(422, "VALIDATION_ERROR", "name cannot be null.")
            subject.name = _clean_name(data.name)
        if "description" in fields:
            subject.description = (data.description or "").strip() or None
        subject.updated_at = utcnow()
        return self._out(subject)

    def delete(self, subject_id: str) -> None:
        """Deletes the subject together with its quizzes and their attempts."""
        self.get_owned(subject_id)
        quiz_ids = {q.id for q in self.store.quizzes.values() if q.subject_id == subject_id}
        for attempt_id in [a.id for a in self.store.attempts.values() if a.quiz_id in quiz_ids]:
            del self.store.attempts[attempt_id]
        for quiz_id in quiz_ids:
            del self.store.quizzes[quiz_id]
        del self.store.subjects[subject_id]

    def _out(self, s: Subject) -> SubjectOut:
        quiz_count = sum(1 for q in self.store.quizzes.values() if q.subject_id == s.id)
        return SubjectOut(
            id=s.id,
            name=s.name,
            description=s.description,
            quiz_count=quiz_count,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )


def _clean_name(name: str) -> str:
    name = name.strip()
    if not name:
        raise ApiError(422, "VALIDATION_ERROR", "name cannot be blank.")
    return name
