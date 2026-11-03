"""Error envelope (spec 13.3): {"error": {"code", "message", "requestId", "details"}}."""

import logging
import uuid
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("duoquiz")


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str, details: dict[str, Any] | None = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


def not_found(what: str) -> ApiError:
    return ApiError(status.HTTP_404_NOT_FOUND, f"{what.upper()}_NOT_FOUND", f"{what} not found.")


class ErrorBody(BaseModel):
    code: str = Field(examples=["SUBJECT_NOT_FOUND"])
    message: str = Field(examples=["Subject not found."])
    requestId: str = Field(examples=["req_5f1c2a9e"])
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorEnvelope(BaseModel):
    error: ErrorBody


def error_responses(*codes: int) -> dict[int | str, dict[str, Any]]:
    """OpenAPI `responses=` helper so Swagger documents the error envelope."""
    return {c: {"model": ErrorEnvelope} for c in codes}


_CODE_BY_STATUS = {400: "BAD_REQUEST", 401: "UNAUTHORIZED", 403: "FORBIDDEN", 404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}


def _envelope(status_code: int, code: str, message: str, details: dict[str, Any] | None = None) -> JSONResponse:
    request_id = f"req_{uuid.uuid4().hex[:8]}"
    body = {"error": {"code": code, "message": message, "requestId": request_id, "details": details or {}}}
    return JSONResponse(status_code=status_code, content=body)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def _api_error(_: Request, exc: ApiError):
        return _envelope(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError):
        fields = [
            {"field": ".".join(str(p) for p in e["loc"]), "message": e["msg"]} for e in exc.errors()
        ]
        return _envelope(422, "VALIDATION_ERROR", "Request validation failed.", {"fields": fields})

    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException):
        return _envelope(exc.status_code, _CODE_BY_STATUS.get(exc.status_code, "HTTP_ERROR"), str(exc.detail))

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return _envelope(500, "INTERNAL_ERROR", "An unexpected error occurred.")
