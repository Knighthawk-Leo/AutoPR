# Arithmancy

A minimal calculator web app built with FastAPI and plain HTML/CSS, dressed as
a page from a Hogwarts spellbook.

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
- Three-mode theme switch — **Light**, **Dark**, **System** — that remembers
  your choice, and in System keeps following the OS as it changes

## Theme

The whole workflow — form, focus, submit, result and error — is rendered in a
**Hogwarts: Scarlet & Gold** theme, in two canvases:

| Canvas | `data-theme` | Feel |
| --- | --- | --- |
| Dark | `:root` | **Midnight at Hogwarts** — a blue-violet night sky under the enchanted ceiling, lit by candle gold |
| Light | `:root[data-theme="light"]` | **The Marauder's Map** — aged parchment, sepia ink, bronze and Express maroon |

### Three modes, two canvases

The switch in the card's top-right offers three modes, but there is no third
palette — "system" is the mode in which the *device*, not the user, picks the
canvas. Two attributes on `<html>` keep the two ideas apart:

| Attribute | Values | Meaning |
| --- | --- | --- |
| `data-theme-mode` | `light` \| `dark` \| `system` | what the user chose |
| `data-theme` | `light` \| `dark` | what that resolved to |

Every colour rule keys off `data-theme` alone, so adding the third mode cost no
new tokens. `data-theme-mode` drives only the switch's selected segment (via the
`--theme-thumb` index) — and it is what makes a *stored* `dark` distinguishable
from a device that merely happens to be dark right now.

**System is the default.** A first-time visitor is in system mode, so the app
follows the OS and keeps following it: `theme.js` subscribes to
`prefers-color-scheme` and repaints, but only while the mode is `system`. The
two explicit modes deliberately ignore the OS. The stored key is unchanged
(`calculator-theme`), and an older stored `light`/`dark` still reads correctly;
only the absence of a value now means `system` rather than "follow the OS until
you pick a side."

The control is a `role="radiogroup"` of three radios rather than a toggle,
because a toggle cannot express three states or say which one is *inherited*.
Each radio's accessible name states what that mode **is** ("Light mode",
"System mode — follow my device") rather than what clicking will do; arrow keys
move within the group on a roving tabindex; and selecting *system* announces
what it currently resolves to, since otherwise the choice would report no
observable change. It ships `hidden` and is revealed by JS — without scripting
none of the three can be chosen, so the OS should decide.

Colours are defined once as custom properties per canvas in `static/style.css`:

| Role | Tokens |
| --- | --- |
| Canvas | `--bg-base`, `--bg-deep`, `--surface`, `--surface-raised`, `--border`, `--border-strong` |
| Gold ramp | `--gold`, `--gold-strong`, `--gold-bright`, `--gold-wash` |
| Scarlet ramp | `--scarlet`, `--scarlet-strong`, `--scarlet-bright`, `--scarlet-wash` |
| Action | `--btn-from`, `--btn-to`, `--btn-fg`, `--btn-border`, `--btn-glow` |
| Atmosphere | `--glow-a`, `--glow-b`, `--sky`, `--sky-opacity`, `--inset-sheen` |
| Rings | `--ring-gold`, `--ring-scarlet`, `--ring-invert` |
| Type | `--font-display` (Cinzel), `--font-body` (EB Garamond) |

The UI uses exactly two colours, split by job:

- **Gold** is the *bright* colour — candlelight, the Snitch, the crest: the
  heading, the primary action, the focus ring, and the result banner.
- **Scarlet** is the *loud* colour — the Express, the house banner, a hex gone
  wrong: the subtitle, invalid input, and the error banner.

The two meet only in the card's top accent bar, which sweeps deep Express
maroon through scarlet into candle gold — the house rule across the page.

### Details worth keeping if you re-tune the palette

- The submit button uses **dark night-ink type on a gold bar**
  (`--btn-fg: #150f22`). Parchment white on `--gold` is only ~2.0:1 and fails
  WCAG badly; the dark ink holds 9.5:1 at the deep end of the gradient and
  13.3:1 at the bright end, so the label survives the whole sweep. Because the
  bar is *already* gold, its focus ring inverts (`--ring-invert`) — a gold ring
  on a gold button is invisible.
- **Scarlet is the failure colour, so it must not also mean "you're fine."**
  Focus is therefore gold, not scarlet: a warm candlelight ring can never be
  misread as an error, and invalid input answers in scarlet without competing
  with it. For the same reason success is gold rather than a third hue — the
  result banner glows, and the error banner is the only place the canvas turns
  red on itself.
- Hue alone still isn't the signal. The error banner keeps two non-colour cues
  — `font-weight: 600` and a `⚡` bolt — while the result banner carries a `✦`,
  so both stay distinguishable in greyscale and for red-blind users.
- **The light palette is written twice** — once in `:root[data-theme="light"]`
  and once in the `@media (prefers-color-scheme: light)` no-JS fallback. Any
  palette edit must be made in both blocks. Note that the fallback is now a
  *no-JS* path only: with scripting on, system mode sets `data-theme` itself
  before the first paint, so `:root:not([data-theme])` never matches.
- The switch's thumb reuses the action bar's gradient, so the selected glyph
  takes `--btn-fg` for the same reason the submit label does.
- `THEME_COLOR` in `static/theme.js` and the inline `<meta name="theme-color">`
  in the template must both track `--bg-base` (`#0b0a12` / `#f4ead3`).
- The webfonts are **optional**. `--font-display` and `--font-body` each end in
  a serif fallback stack, and the stylesheet never blocks on the Google Fonts
  request, so the page renders correctly offline — just in Georgia.

All text pairs clear WCAG AA; body text clears AAA.

### Motion

The starfield/parchment layer (`body::before`) drifts on a slow 11s
`candlelight` opacity cycle, and the theme swap paints a 340ms `.theme-shifting`
transition. The switch's thumb slides between segments on the same duration;
because `.theme-shifting *` replaces the whole `transition` property with
`!important`, the thumb re-declares its own transform transition inside that
block — otherwise it would freeze on exactly the clicks that move it. All of it
is scoped to `prefers-reduced-motion: no-preference`, and a `reduce` block kills
every transition and animation outright.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

`tests/test_workflow.py` covers the calculator behaviour and still passes — the
re-theme changed no routes, field names, option values, class names, or the
`Cannot divide by zero` message.

> **Note:** `tests/test_theme.py` was already stale before this re-theme — it
> encodes a **Silver & Gold** spec two revisions back, asserting `--silver-*`
> token names, `<meta name="color-scheme" content="dark" />`, no light surfaces
> anywhere, and the old subtitle string. It has not been regenerated for
> Hogwarts: Scarlet & Gold and will keep failing until it is rewritten.
