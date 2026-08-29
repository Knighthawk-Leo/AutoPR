import math
from typing import Optional

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Simple Calculator")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# math.factorial grows fast enough that a large input would tie up the worker
# and produce an unreadable answer, so the input is capped instead.
MAX_FACTORIAL_INPUT = 500

# Operations that only use the first number.
UNARY_OPS = {"fact"}


def compute(a: float, b: Optional[float], op: str) -> float:
    if op == "fact":
        if a < 0:
            raise ValueError("Factorial is not defined for negative numbers")
        if not a.is_integer():
            raise ValueError("Factorial needs a whole number")
        if a > MAX_FACTORIAL_INPUT:
            raise ValueError(f"Factorial is limited to {MAX_FACTORIAL_INPUT} or less")
        return math.factorial(int(a))

    if b is None:
        raise ValueError("Second number is required for this operation")

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
    if op == "pct":
        # "a% of b" — the same thing the % key does on a pocket calculator.
        return a * b / 100
    raise ValueError(f"Unknown operation: {op}")


def parse_number(raw: str, field: str) -> float:
    try:
        return float(raw)
    except ValueError:
        raise ValueError(f"{field} is not a valid number")


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
    a: str = Form(""),
    b: str = Form(""),
    op: str = Form("add"),
):
    # The numbers arrive as raw strings so a blank or malformed entry can be
    # reported in the page instead of becoming a 422 error response.
    raw_a, raw_b = a.strip(), b.strip()

    result = None
    error = None
    try:
        value_a = parse_number(raw_a, "First number")
        value_b = None if op in UNARY_OPS or not raw_b else parse_number(raw_b, "Second number")
        result = compute(value_a, value_b, op)
    except ValueError as exc:
        error = str(exc)

    return templates.TemplateResponse(
        request,
        "index.html",
        {"result": result, "error": error, "a": raw_a, "b": raw_b, "op": op},
    )
