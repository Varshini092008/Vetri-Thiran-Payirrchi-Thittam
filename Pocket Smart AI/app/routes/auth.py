from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from ..auth import (
    authenticate_user,
    create_access_token,
    hash_password
)
from ..database import get_db


router = APIRouter()


@router.get("/login")
def login_page(request: Request):
    from .pages import render

    return render(
        request,
        "login.html"
    )


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    user = authenticate_user(
        email,
        password
    )

    if not user:
        from .pages import render

        return render(
            request,
            "login.html",
            error="Invalid email or password."
        )

    token = create_access_token(
        user["id"]
    )

    response = RedirectResponse(
        "/dashboard",
        status_code=303
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax"
    )

    return response


@router.get("/register")
def register_page(request: Request):
    from .pages import render

    return render(
        request,
        "register.html"
    )


@router.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    name = name.strip()
    email = email.lower().strip()

    if not name or not email or not password:
        from .pages import render

        return render(
            request,
            "register.html",
            error="All fields are required."
        )

    with get_db() as db:
        existing = db.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing:
            from .pages import render

            return render(
                request,
                "register.html",
                error="Email already registered."
            )

        password_hash = hash_password(password)

        cursor = db.execute(
            """
            INSERT INTO users
            (name, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (
                name,
                email,
                password_hash
            )
        )

        user_id = cursor.lastrowid

    token = create_access_token(
        user_id
    )

    response = RedirectResponse(
        "/dashboard",
        status_code=303
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax"
    )

    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(
        "/",
        status_code=303
    )

    response.delete_cookie(
        key="access_token"
    )

    return response