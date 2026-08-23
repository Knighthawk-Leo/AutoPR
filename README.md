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

## Theme

The whole workflow — form, focus, submit, result and error — is rendered in a
**Silver & Gold** theme. Colours are defined once as custom properties in
`:root` (`static/style.css`):

| Role | Tokens |
| --- | --- |
| Canvas | `--bg-base` (`#0b0d10`), `--bg-deep`, `--surface`, `--surface-raised` |
| Silver ramp | `--silver`, `--silver-strong`, `--silver-bright`, `--silver-wash` |
| Gold ramp | `--gold`, `--gold-strong`, `--gold-bright`, `--gold-wash` |

Conventions: the canvas is cool **graphite**, deliberately not true black —
silver needs something to sit against or it stops reading as metal. From there
the UI uses exactly two metals, split by temperature:

- **Gold** is the *live* metal: focus rings, the subtitle, the submit button's
  warm end, and the result banner.
- **Silver** is the *cold* metal: the heading, invalid input, and the error
  banner.

The two meet in the card's top accent bar and in the submit button gradient.

Three details worth keeping if you re-tune the palette:

- The submit button uses **graphite type on metal** (`color: var(--bg-base)`).
  White on bright gold is only ~1.4:1 and fails WCAG; graphite holds 11.4:1 on
  gold and 12.7:1 on silver, so the label survives the whole gradient.
- **This palette contains no red.** Errors therefore cannot signal by hue the
  way a conventional theme would, so the error banner carries two non-colour
  cues — `font-weight: 600` and a `⚠` glyph — while the result banner carries a
  `✓`. Both banners stay distinguishable in greyscale. If you ever need a
  louder failure state, add a third ramp rather than tinting silver.
- Focus (gold) and invalid (silver) are separated by temperature, not
  brightness, so they never read as the same state.

All text pairs clear WCAG AA; body text clears AAA.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

`tests/test_workflow.py` covers the calculator behaviour; `tests/test_theme.py`
asserts the theme itself — a cool graphite (never true-black, never warm)
canvas, a warm gold ramp and a cool near-neutral silver ramp, per-state colour
usage, the non-colour outcome cues, absence of every superseded palette, and
contrast ratios including the graphite-on-metal button label at both ends of
the gradient.
