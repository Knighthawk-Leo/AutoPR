"""Every step of the workflow must render in the Silver & Gold theme."""

import re

import pytest

TOKEN_RE = re.compile(r"^\s*(--[a-z0-9-]+)\s*:\s*([^;]+);", re.MULTILINE)
HEX_RE = re.compile(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")

# Every colour from a superseded theme that must be fully gone.
LEGACY_COLORS = [
    # Original light purple/green theme.
    "#667eea",
    "#764ba2",
    "#5568c9",
    "#e8f5e9",
    "#256029",
    "#fdecea",
    "#b3261e",
    # Dark Red & Blue theme.
    "#05070f",
    "#0a0f1e",
    "#111a2e",
    "#16223c",
    "#253352",
    "#3a4c7a",
    "#e9eefb",
    "#9db0d6",
    "#2f6fed",
    "#1d4ed8",
    "#7fb2ff",
    "#0e1e3c",
    "#d92b3f",
    "#a4162a",
    "#ff8d99",
    "#33101a",
    # Bright Gold & Dark Black theme.
    "#000000",
    "#0b0a07",
    "#16130d",
    "#1f1a11",
    "#3a3222",
    "#61522f",
    "#fbf6e9",
    "#bfae86",
    "#ffc72c",
    "#c98f00",
    "#ffdf7a",
    "#2b1f04",
    "#cf7c1c",
    "#8a4f0a",
    "#f3b169",
    "#2a1607",
]

# rgba() glows that superseded themes painted onto the canvas.
LEGACY_GLOWS = [
    "rgba(164, 22, 42",  # Red & Blue
    "rgba(29, 78, 216",
    "rgba(138, 79, 10",  # Gold & Black bronze glow
    "rgba(201, 143, 0",  # Gold & Black gold glow
]

CANVAS_TOKENS = ["--bg-base", "--bg-deep", "--surface", "--surface-raised"]
SILVER_RAMP = ["--silver", "--silver-strong", "--silver-bright", "--silver-wash"]
GOLD_RAMP = ["--gold", "--gold-strong", "--gold-bright", "--gold-wash"]

# The two metals, excluding their dark `-wash` fills.
SILVER_METAL = ["--silver", "--silver-strong", "--silver-bright"]
GOLD_METAL = ["--gold", "--gold-strong", "--gold-bright"]


def tokens(css: str) -> dict[str, str]:
    return {name: value.strip() for name, value in TOKEN_RE.findall(css)}


def _normalize(selector: str) -> str:
    return re.sub(r"\s*,\s*", ", ", " ".join(selector.split()))


def rule(css: str, selector: str) -> str:
    """Return the declaration block whose *full* selector list matches.

    Matching the whole list (not just one selector in it) keeps shared rules
    such as `.result, .error { ... }` from shadowing the state-specific
    `.error { ... }` block that follows them.
    """
    stripped = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    wanted = _normalize(selector)
    for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", stripped):
        if _normalize(selectors) == wanted:
            return body
    raise AssertionError(f"selector {selector!r} not found in stylesheet")


def rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def luminance(hex_color: str) -> float:
    channels = []
    for channel in rgb(hex_color):
        c = channel / 255
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg: str, bg: str) -> float:
    light, dark = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def is_dark(hex_color: str) -> bool:
    return luminance(hex_color) < 0.12


def warmth(hex_color: str) -> int:
    """Red minus blue. Positive is a warm colour, negative is a cool one."""
    r, _, b = rgb(hex_color)
    return r - b


def saturation_spread(hex_color: str) -> int:
    channels = rgb(hex_color)
    return max(channels) - min(channels)


class TestPalette:
    def test_root_declares_dark_color_scheme(self, css_text):
        assert "color-scheme: dark" in rule(css_text, ":root")

    @pytest.mark.parametrize("token", CANVAS_TOKENS + ["--text", "--text-muted"])
    def test_core_tokens_exist(self, css_text, token):
        assert token in tokens(css_text)

    @pytest.mark.parametrize("token", SILVER_RAMP)
    def test_silver_ramp_exists(self, css_text, token):
        assert token in tokens(css_text)

    @pytest.mark.parametrize("token", GOLD_RAMP)
    def test_gold_ramp_exists(self, css_text, token):
        assert token in tokens(css_text)

    def test_canvas_base_is_not_true_black(self, css_text):
        """Silver needs graphite, not black, or it stops reading as metal."""
        base = tokens(css_text)["--bg-base"].lower()
        assert base not in {"#000", "#000000"}, "--bg-base collapsed to true black"
        assert is_dark(base)

    @pytest.mark.parametrize(
        "token", CANVAS_TOKENS + ["--gold-wash", "--silver-wash"]
    )
    def test_surfaces_are_dark(self, css_text, token):
        assert is_dark(tokens(css_text)[token])

    @pytest.mark.parametrize(
        "token", CANVAS_TOKENS + ["--border", "--border-strong"]
    )
    def test_canvas_leans_cool(self, css_text, token):
        """The canvas is cool graphite; the old theme's warm black is gone."""
        r, g, b = rgb(tokens(css_text)[token])
        assert b >= r, f"{token} is warm-leaning (r={r}, b={b})"

    @pytest.mark.parametrize("token", GOLD_METAL)
    def test_gold_is_a_warm_metal(self, css_text, token):
        r, g, b = rgb(tokens(css_text)[token])
        assert r >= g > b, f"{token} = rgb({r}, {g}, {b}) is not gold"

    @pytest.mark.parametrize("token", SILVER_METAL)
    def test_silver_is_a_cool_metal(self, css_text, token):
        r, g, b = rgb(tokens(css_text)[token])
        assert b >= g >= r, f"{token} = rgb({r}, {g}, {b}) is not silver"

    @pytest.mark.parametrize("token", SILVER_METAL)
    def test_silver_stays_near_neutral(self, css_text, token):
        """Silver is a grey with a cool cast — not a blue."""
        spread = saturation_spread(tokens(css_text)[token])
        assert spread <= 40, f"{token} is too saturated to read as silver ({spread})"

    def test_the_two_metals_are_clearly_different_temperatures(self, css_text):
        table = tokens(css_text)
        assert warmth(table["--gold"]) > 100, "gold is not warm enough"
        assert warmth(table["--silver"]) < 0, "silver is not cool"

    @pytest.mark.parametrize(
        ("bright", "base"),
        [("--silver-bright", "--silver"), ("--gold-bright", "--gold")],
    )
    def test_bright_variants_are_brighter(self, css_text, bright, base):
        table = tokens(css_text)
        assert luminance(table[bright]) > luminance(table[base])

    @pytest.mark.parametrize(
        ("strong", "base"),
        [("--silver-strong", "--silver"), ("--gold-strong", "--gold")],
    )
    def test_strong_variants_are_deeper(self, css_text, strong, base):
        table = tokens(css_text)
        assert luminance(table[strong]) < luminance(table[base])

    def test_no_legacy_theme_colors(self, css_text):
        lowered = css_text.lower()
        found = [color for color in LEGACY_COLORS if color in lowered]
        assert not found, f"legacy theme colors still present: {found}"

    def test_no_legacy_glows(self, css_text):
        found = [glow for glow in LEGACY_GLOWS if glow in css_text]
        assert not found, f"legacy canvas glows still present: {found}"

    def test_no_superseded_accent_tokens_remain(self, css_text):
        leftovers = re.findall(r"--(?:bronze|red|blue)[a-z-]*", css_text)
        assert not leftovers, f"superseded tokens still referenced: {sorted(set(leftovers))}"

    def test_no_light_surfaces_anywhere(self, css_text):
        """Fills below :root must never be light; only pure black/white escape."""
        body = css_text[css_text.index("body {") :]
        offenders = {
            hit.group(0)
            for hit in HEX_RE.finditer(body)
            if not is_dark(hit.group(0))
            and hit.group(0).lower() not in {"#ffffff", "#fff"}
        }
        assert not offenders, f"non-dark hex colors used as fills: {sorted(offenders)}"


class TestWorkflowSurfaces:
    def test_body_uses_graphite_canvas(self, css_text):
        assert "background-color: var(--bg-base)" in rule(css_text, "body")

    def test_body_carries_both_silver_and_gold_sheen(self, css_text):
        body = rule(css_text, "body")
        assert "rgba(141, 154, 173" in body, "missing silver sheen"
        assert "rgba(184, 134, 42" in body, "missing gold sheen"

    def test_card_is_a_dark_surface(self, css_text):
        card = rule(css_text, ".calculator")
        assert "var(--surface)" in card
        assert "border: 1px solid var(--border)" in card

    def test_card_has_silver_to_gold_accent_bar(self, css_text):
        accent = rule(css_text, ".calculator::before")
        assert "linear-gradient(90deg, var(--silver), var(--gold))" in accent

    def test_heading_is_silver(self, css_text):
        assert "color: var(--silver-bright)" in rule(css_text, "h1")

    def test_subtitle_is_gold(self, css_text):
        assert "color: var(--gold)" in rule(css_text, ".subtitle")

    def test_inputs_are_dark_with_light_text(self, css_text):
        block = rule(css_text, "input, select")
        assert "color: var(--text)" in block
        assert "background-color: var(--bg-deep)" in block

    def test_focus_state_is_gold(self, css_text):
        focus = rule(
            css_text,
            "input:focus-visible, select:focus-visible, input:focus, select:focus",
        )
        assert "border-color: var(--gold)" in focus
        assert "box-shadow: var(--ring-gold)" in focus

    def test_invalid_input_is_silver(self, css_text):
        invalid = rule(css_text, "input:invalid:not(:placeholder-shown)")
        assert "border-color: var(--silver)" in invalid
        assert "box-shadow: var(--ring-silver)" in invalid

    def test_invalid_state_is_not_confusable_with_focus(self, css_text):
        """Focus and invalid must not both be gold."""
        invalid = rule(css_text, "input:invalid:not(:placeholder-shown)")
        assert "gold" not in invalid

    def test_invalid_state_outranks_the_resting_border(self, css_text):
        """Silver must visibly beat the graphite border it replaces."""
        table = tokens(css_text)
        assert luminance(table["--silver"]) > luminance(table["--border-strong"]) * 3

    def test_button_blends_silver_into_gold(self, css_text):
        button = rule(css_text, "button")
        assert "linear-gradient(90deg, var(--silver), var(--gold))" in button

    def test_button_label_is_graphite_on_metal(self, css_text):
        """White on bright silver or gold is unreadable — the label is graphite."""
        button = rule(css_text, "button")
        assert "color: var(--bg-base)" in button
        assert "#fff" not in button.lower()

    def test_result_state_is_gold(self, css_text):
        result = rule(css_text, ".result")
        assert "var(--gold-bright)" in result
        assert "var(--gold-wash)" in result
        assert "silver" not in result

    def test_error_state_is_silver(self, css_text):
        error = rule(css_text, ".error")
        assert "var(--silver-bright)" in error
        assert "var(--silver-wash)" in error
        assert "gold" not in error

    def test_outcomes_differ_by_temperature(self, css_text):
        """The palette has no red, so warm-vs-cool separates the two outcomes."""
        table = tokens(css_text)
        assert warmth(table["--gold-bright"]) > 0
        assert warmth(table["--silver-bright"]) <= 0
        assert warmth(table["--gold-wash"]) > warmth(table["--silver-wash"])

    def test_error_carries_a_weight_cue(self, css_text):
        """Hue alone must not be the only signal that something failed."""
        assert "font-weight" in rule(css_text, ".error")

    @pytest.mark.parametrize(
        ("selector", "glyph"),
        [(".result::before", "2713"), (".error::before", "26a0")],
    )
    def test_outcomes_carry_distinct_glyphs(self, css_text, selector, glyph):
        """Both banners stay distinguishable in greyscale."""
        block = rule(css_text, selector)
        assert "content:" in block
        assert glyph in block.lower()

    def test_reduced_motion_is_respected(self, css_text):
        assert "@media (prefers-reduced-motion: reduce)" in css_text


class TestContrast:
    """WCAG 2.1 contrast for text rendered at each step of the workflow."""

    @pytest.mark.parametrize(
        ("fg", "bg", "minimum"),
        [
            ("--text", "--surface", 7.0),  # values inside the result banner: AAA
            ("--text", "--surface-raised", 7.0),  # top of the card gradient
            ("--text", "--bg-deep", 7.0),  # typed input text
            ("--text-muted", "--surface", 4.5),  # field labels
            ("--text-muted", "--surface-raised", 4.5),
            ("--silver-bright", "--surface", 4.5),  # the h1
            ("--silver-bright", "--bg-base", 4.5),
            ("--gold", "--surface", 4.5),  # gold subtitle on the card
            ("--gold", "--bg-base", 4.5),  # gold on the raw canvas
            ("--gold-bright", "--gold-wash", 4.5),  # result banner
            ("--silver-bright", "--silver-wash", 4.5),  # error banner
        ],
    )
    def test_token_pairs_meet_wcag(self, css_text, fg, bg, minimum):
        table = tokens(css_text)
        ratio = contrast(table[fg], table[bg])
        assert ratio >= minimum, f"{fg} on {bg} is only {ratio:.2f}:1"

    @pytest.mark.parametrize("bg", ["--silver", "--gold"])
    def test_button_label_readable_across_gradient(self, css_text, bg):
        """The label must hold up at both ends of the silver-to-gold bar."""
        table = tokens(css_text)
        ratio = contrast(table["--bg-base"], table[bg])
        assert ratio >= 4.5, f"graphite on {bg} is only {ratio:.2f}:1"

    def test_focus_ring_is_visible_against_the_field(self, css_text):
        table = tokens(css_text)
        ratio = contrast(table["--gold"], table["--bg-deep"])
        assert ratio >= 3.0, f"gold focus ring is only {ratio:.2f}:1 on the field"

    def test_invalid_ring_is_visible_against_the_field(self, css_text):
        table = tokens(css_text)
        ratio = contrast(table["--silver"], table["--bg-deep"])
        assert ratio >= 3.0, f"silver invalid ring is only {ratio:.2f}:1 on the field"


class TestTemplate:
    def test_declares_dark_color_scheme(self, template_text):
        assert '<meta name="color-scheme" content="dark" />' in template_text

    def test_browser_chrome_matches_graphite_canvas(self, css_text, template_text):
        base = tokens(css_text)["--bg-base"]
        assert f'<meta name="theme-color" content="{base}" />' in template_text

    def test_is_responsive(self, template_text):
        assert 'name="viewport"' in template_text

    def test_theme_subtitle_rendered(self, template_text):
        assert 'class="subtitle"' in template_text
        assert "Silver &amp; Gold" in template_text

    def test_no_stale_theme_name(self, template_text):
        for stale in ("Dark Red", "Blue", "Bronze", "Dark Black"):
            assert stale not in template_text, f"stale theme name {stale!r}"

    def test_no_inline_styles_override_theme(self, template_text):
        assert not re.search(r"<[^>]*\sstyle\s*=", template_text)

    def test_outcome_banners_are_announced(self, template_text):
        assert 'class="result" role="status"' in template_text
        assert 'class="error" role="alert"' in template_text
