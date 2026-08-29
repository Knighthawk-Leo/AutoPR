# Simple Calculator

A minimal calculator web app built with FastAPI and plain HTML/CSS.

## Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://127.0.0.1:8000 in your browser.

## Features

- Add, subtract, multiply, divide two numbers
- Factorial (`n!`) of the first number — the second number is ignored
- Percentage (`%`) — computes `a% of b`
- Server-rendered UI (Jinja2 templates)
- Input validation: divide-by-zero, non-numeric and blank entries, and
  factorial of negatives, decimals, or values above 500
