from __future__ import annotations

from http import HTTPStatus
from typing import Any

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from sanic import HTTPResponse, Request, json


def response(model: BaseModel, status: int = HTTPStatus.OK) -> HTTPResponse:
    return json(model.model_dump(mode="json"), status=status)


def response_collection(
    models: list[Any], schema_cls: type[BaseModel], status: int = HTTPStatus.OK
) -> HTTPResponse:
    return json(
        [schema_cls.model_validate(model).model_dump(mode="json") for model in models],
        status=status,
    )


def error_response(
    *,
    status: int,
    code: str,
    message: str,
    details: Any | None = None,
    request: Request | None = None,
) -> HTTPResponse:
    payload: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        payload["details"] = details
    if request is not None:
        request_id = getattr(request, "id", None)
        if request_id is not None:
            payload["request_id"] = str(request_id)
    return json(payload, status=status)


def parse_payload[T: BaseModel](model_cls: type[T], data: dict[str, Any]) -> T | HTTPResponse:
    """Validate incoming JSON payload into the given pydantic model.

    Returns either the parsed model instance or an HTTPResponse representing a
    validation error (400). Callers should check for HTTPResponse with
    isinstance(payload, HTTPResponse) and return it early on error.
    """
    try:
        return model_cls.model_validate(data)
    except PydanticValidationError as exc:
        return error_response(
            status=HTTPStatus.BAD_REQUEST,
            code="validation_error",
            message="Validation error",
            details=exc.errors(),
        )
