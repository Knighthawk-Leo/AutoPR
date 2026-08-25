from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Arithmancy")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def compute(a: float, b: float, op: str) -> float:
    if op == "add":
        return a + b
    if op == "sub":
        return a - b
    if op == "mul":
        return a * b
    if op == "div":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    raise ValueError(f"Unknown operation: {op}")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"result": None, "error": None, "a": "", "b": "", "op": "add"},
    )


@app.post("/", response_class=HTMLResponse)
def calculate(
    request: Request,
    a: float = Form(...),
    b: float = Form(...),
    op: str = Form(...),
):
    result = None
    error = None
    try:
        result = compute(a, b, op)
    except ValueError as exc:
        error = str(exc)
    return templates.TemplateResponse(
        request,
        "index.html",
        {"result": result, "error": error, "a": a, "b": b, "op": op},
    )
