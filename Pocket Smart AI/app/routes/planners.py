from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse

from ..auth import current_user
from ..config import settings
from ..services.recommendations import run


router = APIRouter()


@router.get("/home-planner")
def home_planner(request: Request):
    from .pages import render

    user = current_user(request)

    return render(
        request,
        "home_planner.html",
        user=user
    )


@router.post("/generate-home")
def generate_home(
    request: Request,
    budget: float = Form(...),
    rooms: list[str] = Form(...),
    style: str = Form("Modern"),
    priorities: str = Form("")
):
    user = current_user(request)

    data = {
        "budget": budget,
        "rooms": rooms,
        "style": style,
        "priorities": priorities
    }

    result = run(
        user["id"],
        "home",
        data
    )

    return RedirectResponse(
        f"/recommendation/{result['id']}",
        status_code=303
    )


@router.get("/party-planner")
def party_planner(request: Request):
    from .pages import render

    user = current_user(request)

    return render(
        request,
        "party_planner.html",
        user=user
    )


@router.post("/generate-party")
def generate_party(
    request: Request,
    budget: float = Form(...),
    guests: int = Form(...),
    event_type: str = Form("Birthday"),
    venue: str = Form("Home"),
    preferences: str = Form("")
):
    user = current_user(request)

    data = {
        "budget": budget,
        "guests": guests,
        "event_type": event_type,
        "venue": venue,
        "preferences": preferences
    }

    result = run(
        user["id"],
        "party",
        data
    )

    return RedirectResponse(
        f"/recommendation/{result['id']}",
        status_code=303
    )


@router.get("/jewelry-planner")
def jewelry_planner(request: Request):
    from .pages import render

    user = current_user(request)

    return render(
        request,
        "jewelry_planner.html",
        user=user
    )


@router.post("/generate-jewelry")
async def generate_jewelry(
    request: Request,
    budget: float = Form(...),
    occasion: str = Form("Wedding"),
    style: str = Form("Traditional"),
    outfit_image: UploadFile | None = File(None)
):
    user = current_user(request)

    image_bytes = None
    mime = None

    if outfit_image:
        if outfit_image.content_type not in [
            "image/jpeg",
            "image/png",
            "image/webp"
        ]:
            from .pages import render

            return render(
                request,
                "jewelry_planner.html",
                user=user,
                error="Only JPG, PNG and WEBP images are allowed."
            )

        image_bytes = await outfit_image.read()

        max_bytes = (
            settings.max_upload_mb * 1024 * 1024
        )

        if len(image_bytes) > max_bytes:
            from .pages import render

            return render(
                request,
                "jewelry_planner.html",
                user=user,
                error="Image size is too large."
            )

        mime = outfit_image.content_type

    data = {
        "budget": budget,
        "occasion": occasion,
        "style": style
    }

    result = run(
        user["id"],
        "jewelry",
        data,
        image_bytes,
        mime
    )

    return RedirectResponse(
        f"/recommendation/{result['id']}",
        status_code=303
    )