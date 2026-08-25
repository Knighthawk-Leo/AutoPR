/* ==========================================================================
   Theme switch — shifts the entire UI between three modes.

       light   explicit: parchment, always
       dark    explicit: night sky, always
       system  deferred: whatever the device asks for, and it keeps
               following the device as that preference changes

   Two attributes carry this on <html>:

       data-theme-mode   the choice     -> light | dark | system
       data-theme        the resolution -> light | dark

   All colour lives in CSS custom properties keyed off `data-theme`, so
   flipping it repaints every surface at once. "system" is not a third
   palette — it is the mode in which the OS, rather than the user, decides
   what `data-theme` should be. `data-theme-mode` exists so the control can
   show which of the three is selected, and so a stored "dark" is
   distinguishable from a device that merely happens to be dark right now.

   This file owns: the stored preference, the segmented control's state and
   keyboard model, the address-bar colour, and the OS subscription.

   The pre-paint resolution (avoiding a flash of the wrong theme) happens in
   an inline snippet in <head> — it must run before the first paint, so it
   cannot live in this deferred file.
   ========================================================================== */

(function () {
    "use strict";

    var STORAGE_KEY = "calculator-theme";
    var DEFAULT_MODE = "system";
    var MODES = ["light", "dark", "system"];
    var SHIFT_CLASS = "theme-shifting";
    var SHIFT_MS = 340;

    var root = document.documentElement;
    var lightQuery = window.matchMedia("(prefers-color-scheme: light)");
    var shiftTimer = null;

    /* Keeps the mobile address bar in step with the canvas. Must match
       --bg-base for each theme in style.css — night sky, then parchment. */
    var THEME_COLOR = {
        dark: "#0b0a12",
        light: "#f4ead3"
    };

    function isMode(value) {
        return MODES.indexOf(value) !== -1;
    }

    function readStored() {
        try {
            var value = localStorage.getItem(STORAGE_KEY);
            return isMode(value) ? value : null;
        } catch (err) {
            /* Private mode / blocked storage — fall back to the device. */
            return null;
        }
    }

    function writeStored(mode) {
        try {
            localStorage.setItem(STORAGE_KEY, mode);
        } catch (err) {
            /* Preference just won't persist; the switch still works. */
        }
    }

    function systemTheme() {
        return lightQuery.matches ? "light" : "dark";
    }

    /* The one place a mode becomes a palette. */
    function resolve(mode) {
        return mode === "system" ? systemTheme() : mode;
    }

    function currentMode() {
        var mode = root.getAttribute("data-theme-mode");
        return isMode(mode) ? mode : DEFAULT_MODE;
    }

    function currentTheme() {
        return root.getAttribute("data-theme") === "light" ? "light" : "dark";
    }

    function options() {
        var group = document.getElementById("theme-switch");
        return group
            ? Array.prototype.slice.call(
                  group.querySelectorAll(".theme-switch__option")
              )
            : [];
    }

    function setMetaThemeColor(theme) {
        var meta = document.querySelector('meta[name="theme-color"]');
        if (meta) {
            meta.setAttribute("content", THEME_COLOR[theme]);
        }
    }

    /* Paints the transition class on for one shift, then takes it back off so
       ordinary hover/focus transitions keep their own timings. */
    function runShift() {
        root.classList.add(SHIFT_CLASS);
        if (shiftTimer !== null) {
            clearTimeout(shiftTimer);
        }
        shiftTimer = setTimeout(function () {
            root.classList.remove(SHIFT_CLASS);
            shiftTimer = null;
        }, SHIFT_MS);
    }

    /* A radiogroup exposes selection through aria-checked, and takes a single
       tab stop: the checked option is the only one reachable by Tab, and the
       arrow keys move within the group (a "roving tabindex"). */
    function syncOptions(mode) {
        options().forEach(function (option) {
            var selected = option.getAttribute("data-mode") === mode;
            option.setAttribute("aria-checked", selected ? "true" : "false");
            option.tabIndex = selected ? 0 : -1;
        });
    }

    /* The controls' own names stay literal ("Light mode", "System mode") so
       none of the three is ever ambiguous; the flavour lives here, in the
       after-the-fact confirmation, where the plain name is still spelled out.
       System also reports what it currently resolves to — otherwise choosing
       it would announce no observable change. */
    function describe(mode, theme) {
        if (mode === "light") {
            return "Lumos — light mode";
        }
        if (mode === "dark") {
            return "Nox — dark mode";
        }
        return (
            "Attuned to your device — system mode, currently " +
            (theme === "light" ? "light" : "dark")
        );
    }

    function announce(mode, theme) {
        var region = document.getElementById("theme-status");
        if (region) {
            region.textContent = describe(mode, theme);
        }
    }

    function applyMode(mode, options_) {
        var opts = options_ || {};
        var theme = resolve(mode);

        if (opts.animate && theme !== currentTheme()) {
            runShift();
        }

        root.setAttribute("data-theme-mode", mode);
        root.setAttribute("data-theme", theme);
        setMetaThemeColor(theme);
        syncOptions(mode);

        if (opts.announce) {
            announce(mode, theme);
        }
    }

    function select(mode, opts) {
        if (!isMode(mode)) {
            return;
        }
        writeStored(mode);
        applyMode(mode, opts);
    }

    /* Arrow keys move the selection and the focus together, which is the
       expected behaviour for a radiogroup. Home/End jump to the ends. */
    function onKeydown(event) {
        var all = options();
        var index = all.indexOf(event.target);
        if (index === -1) {
            return;
        }

        var next = null;
        switch (event.key) {
            case "ArrowRight":
            case "ArrowDown":
                next = (index + 1) % all.length;
                break;
            case "ArrowLeft":
            case "ArrowUp":
                next = (index - 1 + all.length) % all.length;
                break;
            case "Home":
                next = 0;
                break;
            case "End":
                next = all.length - 1;
                break;
            default:
                return;
        }

        event.preventDefault();
        select(all[next].getAttribute("data-mode"), {
            animate: true,
            announce: true
        });
        all[next].focus();
    }

    function init() {
        var group = document.getElementById("theme-switch");
        var stored = readStored();

        /* The inline head snippet already set both attributes; this re-runs
           the same resolution so the control, meta tag and <html> can't
           drift. */
        applyMode(stored || DEFAULT_MODE, { animate: false });

        if (group) {
            group.hidden = false;

            group.addEventListener("click", function (event) {
                var option = event.target.closest
                    ? event.target.closest(".theme-switch__option")
                    : null;
                if (option) {
                    select(option.getAttribute("data-mode"), {
                        animate: true,
                        announce: true
                    });
                }
            });

            group.addEventListener("keydown", onKeydown);
        }

        /* In system mode the device stays in charge, so a change to the OS
           preference has to repaint us. In the two explicit modes it is
           deliberately ignored. */
        var onSystemChange = function () {
            if (currentMode() === "system") {
                applyMode("system", { animate: true });
            }
        };

        if (typeof lightQuery.addEventListener === "function") {
            lightQuery.addEventListener("change", onSystemChange);
        } else if (typeof lightQuery.addListener === "function") {
            lightQuery.addListener(onSystemChange); /* Safari < 14 */
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
