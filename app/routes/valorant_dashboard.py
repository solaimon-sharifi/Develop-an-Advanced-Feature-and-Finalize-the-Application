from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/valorant-dashboard", response_class=HTMLResponse, name="valorant_dashboard")
async def valorant_dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "valorant_dashboard.html",
        {"request": request},
    )