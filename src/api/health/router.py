from sanic import Blueprint, HTTPResponse, Request, json

router = Blueprint("health")


@router.get("/health")
async def healthcheck(_request: Request) -> HTTPResponse:
    return json({"status": "ok"})
