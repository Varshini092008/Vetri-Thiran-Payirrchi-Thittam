from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings
from .database import get_db


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM
    )


def user_by_email(email: str):
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM users WHERE email = ?",
            (email.lower().strip(),)
        ).fetchone()

        return row


def user_by_id(user_id: int):
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        return row


def authenticate_user(email: str, password: str):
    user = user_by_email(email)

    if not user:
        return None

    if not verify_password(
        password,
        user["password_hash"]
    ):
        return None

    return user


def current_user(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM]
        )

        user_id = int(payload.get("sub"))

    except (JWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


def optional_user(request: Request):
    try:
        return current_user(request)
    except HTTPException:
        return None