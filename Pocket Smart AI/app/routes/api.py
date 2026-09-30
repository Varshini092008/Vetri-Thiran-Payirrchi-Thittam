from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ..auth import current_user
from ..services.recommendations import run
from ..services.catalog import history, one


router = APIRouter()


@router.get("/api/session")
def session(request: Request):
    user = current_user(request)

    return {
        "user": user
    }


@router.get("/api/history")
def get_history(request: Request):
    user = current_user(request)

    return {
        "history": history(user["id"])
    }


@router.get("/api/recommendation/{recommendation_id}")
def get_recommendation(
    recommendation_id: int,
    request: Request
):
    user = current_user(request)

    recommendation = one(
        user["id"],
        recommendation_id
    )

    if not recommendation:
        return JSONResponse(
            {
                "error": "Recommendation not found."
            },
            status_code=404
        )

    return recommendation


@router.post("/api/generate-home")
def api_generate_home(
    request: Request,
    data: dict
):
    user = current_user(request)

    result = run(
        user["id"],
        "home",
        data
    )

    return result


@router.post("/api/generate-party")
def api_generate_party(
    request: Request,
    data: dict
):
    user = current_user(request)

    result = run(
        user["id"],
        "party",
        data
    )

    return result


@router.post("/api/generate-jewelry")
def api_generate_jewelry(
    request: Request,
    data: dict
):
    user = current_user(request)

    result = run(
        user["id"],
        "jewelry",
        data
    )

    return result