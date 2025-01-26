# src/genai_ecommerce_web/app.py
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routers import api

app = FastAPI(title="GenAI E-commerce")

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
app.mount(
    "/static",
    StaticFiles(directory=str(Path(__file__).parent / "static")),
    name="static",
)

app.include_router(api.router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """
    Render the index page.

    Args:
        request: The HTTP request object.

    Returns:
        An HTMLResponse containing the rendered index page.
    """
    try:
        return templates.TemplateResponse("catalog.html", {"request": request})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/product/{product_id}", response_class=HTMLResponse)
async def product_detail(request: Request, product_id: int) -> HTMLResponse:
    """
    Render the product detail page.

    Args:
        request: The HTTP request object.
        product_id: The ID of the product.

    Returns:
        An HTMLResponse containing the rendered product detail page.
    """
    try:
        return templates.TemplateResponse(
            "product.html", {"request": request, "product_id": product_id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
