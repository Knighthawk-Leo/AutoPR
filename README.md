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
**Dark Red & Black** theme. Colours are defined once as custom properties in
`:root` (`static/style.css`):

| Role | Tokens |
| --- | --- |
| Canvas | `--bg-base` (`#0a0607`), `--bg-deep`, `--surface`, `--surface-raised` |
| Crimson ramp | `--crimson`, `--crimson-strong`, `--crimson-bright`, `--crimson-wash` |
| Ash ramp | `--ash`, `--ash-strong`, `--ash-bright`, `--ash-wash` |

Conventions: the canvas is **warm black** — near-true black, but tinted red
just enough (`r > b` on every canvas and border token) that crimson sits *in*
the surface rather than floating on top of it. From there the UI uses exactly
one hue, split by volume:

- **Crimson** is the *loud* colour: the subtitle, the submit button, invalid
  input, and the error banner.
- **Ash** is the *quiet* colour — a cold near-white: the heading, the focus
  ring, and the result banner.

The crimson ramp meets itself in the card's top accent bar and in the submit
button gradient, sweeping deep blood red into live crimson.

Three details worth keeping if you re-tune the palette:

- The submit button uses **black type on crimson** (`color: var(--bg-base)`).
  White on `--crimson` is only ~3.4:1 and fails WCAG; black holds 5.3:1 at the
  dark end of the bar and 8.0:1 at the bright end, so the label survives the
  whole gradient.
- **Red is the failure colour, so it must not also mean "you're fine."** Focus
  is therefore ash, not crimson: a cold white ring can never be misread as an
  error, and invalid input answers in crimson without competing with it. For
  the same reason success is ash rather than a second hue — the result banner
  stays quiet and the error banner is the only place the canvas turns red on
  itself.
- Hue alone still isn't the signal. The error banner keeps two non-colour cues
  — `font-weight: 600` and a `⚠` glyph — while the result banner carries a `✓`,
  so both stay distinguishable in greyscale and for red-blind users.

All text pairs clear WCAG AA; body text clears AAA.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

`tests/test_workflow.py` covers the calculator behaviour; `tests/test_theme.py`
asserts the theme itself — the canvas, the two ramps, per-state colour usage,
the non-colour outcome cues, absence of every superseded palette, and contrast
ratios including the button label at both ends of the gradient.

> **Note:** `tests/test_theme.py` still encodes the previous **Silver & Gold**
> spec and has not been regenerated for Dark Red & Black. It asserts the old
> `--silver-*` / `--gold-*` token names, a cool (`b >= r`) canvas, and the old
> subtitle string, so it will fail against the current stylesheet until it is
> rewritten for the new palette.
