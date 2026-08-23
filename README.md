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
- Server-rendered UI (Jinja2 templates)
- Divide-by-zero handling
