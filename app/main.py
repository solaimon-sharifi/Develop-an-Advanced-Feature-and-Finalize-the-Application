from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .core.config import get_settings
from .database import Base, engine
from .routes.matches import router as matches_router
from .routes.sessions import router as sessions_router
from .routes.strategies import router as strategies_router
from .routes.users import router as users_router
from .routes.valorant_dashboard import router as valorant_dashboard_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


settings = get_settings()
app = FastAPI(title="Valorant Coach", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(users_router)
app.include_router(matches_router)
app.include_router(strategies_router)
app.include_router(valorant_dashboard_router)
app.include_router(sessions_router)


@app.get("/", response_class=HTMLResponse, name="home")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse, name="login_page")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse, name="register_page")
def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/dashboard/app", response_class=HTMLResponse, name="dashboard_view")
def dashboard_view(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}
