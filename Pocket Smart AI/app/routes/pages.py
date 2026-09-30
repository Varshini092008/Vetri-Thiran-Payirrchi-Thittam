from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..auth import current_user, optional_user
from ..services.catalog import one, history


router = APIRouter()


templates = Jinja2Templates(
    directory="app/templates"
)


def render(request: Request, template: str, **context):
    return templates.TemplateResponse(
        request=request,
        name=template,
        context=context
    )


@router.get("/")
def home(request: Request):
    user = optional_user(request)

    return render(
        request,
        "index.html",
        user=user
    )


@router.get("/dashboard")
def dashboard(request: Request):
    user = current_user(request)

    return render(
        request,
        "dashboard.html",
        user=user
    )


@router.get("/history")
def history_page(request: Request):
    user = current_user(request)

    records = history(user["id"])

    return render(
        request,
        "history.html",
        user=user,
        records=records
    )


@router.get("/recommendation/{recommendation_id}")
def recommendation_page(
    request: Request,
    recommendation_id: int
):
    user = current_user(request)

    record = one(
        user["id"],
        recommendation_id
    )

    if not record:
        return RedirectResponse(
            "/history",
            status_code=303
        )

    return render(
        request,
        "recommendation.html",
        user=user,
        recommendation=record
    )