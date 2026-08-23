/* ==========================================================================
   Theme toggle — shifts the entire UI between light and dark.

   All colour lives in CSS custom properties, so flipping `data-theme` on
   <html> repaints every surface at once. This file only owns: the stored
   preference, the button's accessible state, the address-bar colour, and
   following the OS while the user hasn't chosen a side.

   The pre-paint resolution (avoiding a flash of the wrong theme) happens in
   an inline snippet in <head> — it must run before the first paint, so it
   cannot live in this deferred file.
   ========================================================================== */

(function () {
    "use strict";

    var STORAGE_KEY = "calculator-theme";
    var SHIFT_CLASS = "theme-shifting";
    var SHIFT_MS = 340;

    var root = document.documentElement;
    var media = window.matchMedia("(prefers-color-scheme: light)");
    var shiftTimer = null;

    /* Keeps the mobile address bar in step with the canvas. Must match
       --bg-base for each theme in style.css. */
    var THEME_COLOR = {
        dark: "#0a0607",
        light: "#fdf8f8"
    };

    function readStored() {
        try {
            var value = localStorage.getItem(STORAGE_KEY);
            return value === "light" || value === "dark" ? value : null;
        } catch (err) {
            /* Private mode / blocked storage — fall back to the OS. */
            return null;
        }
    }

    function writeStored(theme) {
        try {
            localStorage.setItem(STORAGE_KEY, theme);
        } catch (err) {
            /* Preference just won't persist; the toggle still works. */
        }
    }

    function systemTheme() {
        return media.matches ? "light" : "dark";
    }

    function currentTheme() {
        return root.getAttribute("data-theme") === "light" ? "light" : "dark";
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

    function syncButton(button, theme) {
        var next = theme === "light" ? "dark" : "light";
        var action = "Switch to " + next + " mode";

        /* aria-pressed describes the state ("dark mode is on"); the label
           describes what the click will do. */
        button.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
        button.setAttribute("aria-label", action);
        button.setAttribute("title", action);
    }

    function announce(region, theme) {
        if (region) {
            region.textContent = theme === "light" ? "Light mode" : "Dark mode";
        }
    }

    function applyTheme(theme, options) {
        var opts = options || {};

        if (opts.animate && theme !== currentTheme()) {
            runShift();
        }

        root.setAttribute("data-theme", theme);
        setMetaThemeColor(theme);

        var button = document.getElementById("theme-toggle");
        if (button) {
            syncButton(button, theme);
        }
        if (opts.announce) {
            announce(document.getElementById("theme-status"), theme);
        }
    }

    function init() {
        var button = document.getElementById("theme-toggle");
        var stored = readStored();

        /* The inline head snippet already set the attribute; this re-runs the
           same resolution so the button, meta tag and <html> can't drift. */
        applyTheme(stored || systemTheme(), { animate: false });

        if (button) {
            button.hidden = false;
            button.addEventListener("click", function () {
                var next = currentTheme() === "light" ? "dark" : "light";
                writeStored(next);
                applyTheme(next, { animate: true, announce: true });
            });
        }

        /* Follow the OS only while the user hasn't made an explicit choice. */
        var onSystemChange = function () {
            if (readStored() === null) {
                applyTheme(systemTheme(), { animate: true });
            }
        };

        if (typeof media.addEventListener === "function") {
            media.addEventListener("change", onSystemChange);
        } else if (typeof media.addListener === "function") {
            media.addListener(onSystemChange); /* Safari < 14 */
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
