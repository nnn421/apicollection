"""Demo auth: stand-in for Supabase JWT verification (FR-AUTH-02/03).

The bearer token value is used as the user id. With no token the seeded
`demo-user` is used, so the API can be tried straight from Swagger. Every
resource is still scoped to this id: different tokens never see each other's data.
When Supabase Auth is wired in, only `get_current_user_id` needs to change.
"""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db.memory import DEMO_USER

bearer = HTTPBearer(auto_error=False, description="Any string; it is used as your user id (demo).")


def get_current_user_id(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> str:
    if creds and creds.credentials.strip():
        return creds.credentials.strip()[:100]
    return DEMO_USER
