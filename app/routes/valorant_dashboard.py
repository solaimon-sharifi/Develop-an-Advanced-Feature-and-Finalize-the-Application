from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..auth import get_current_user_for_templates

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/valorant-dashboard", response_class=HTMLResponse, name="valorant_dashboard")
async def valorant_dashboard(
    request: Request,
    current_user=Depends(get_current_user_for_templates),
) -> HTMLResponse:
    return templates.TemplateResponse(
        "valorant_dashboard.html",
        {"request": request},
    )