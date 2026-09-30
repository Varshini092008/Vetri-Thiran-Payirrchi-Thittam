from fastapi import FastAPI

from .database import init_db
from .routes import pages
from .routes import auth
from .routes import planners
from .routes import api

init_db()

app = FastAPI(
    title="PocketSmart AI",
    description="AI-powered personal planning application",
    version="1.0.0"
)

app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(planners.router)
app.include_router(api.router)