// Infix to postfix visualizer: a stack column and an output column.
// The server (infix.py) records every step. This file only replays the recording.
(function () {
    const panel = document.getElementById("viz");
    if (!panel) return;

    const el = (id) => document.getElementById(id);
    const playButton = el("viz-play");
    const speed = el("viz-speed");
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    let steps = [], chars = [], index = 0, timer = null, playing = false;

    function esc(text) {
        const span = document.createElement("span");
        span.textContent = text;
        return span.innerHTML;
    }

    // ---------- Empty state (also used by the Reset button) ----------
    function reset() {
        clearTimeout(timer);
        playing = false;
        steps = [];
        chars = [];
        index = 0;
        el("viz-tokens").innerHTML = "";
        el("viz-stack").innerHTML = '<p class="muted col-empty">Stack is empty</p>';
        el("viz-output").innerHTML = '<p class="muted col-empty">Output will appear here</p>';
        el("viz-title").textContent = "Enter an infix expression and click Convert";
        el("viz-why").textContent = "";
        el("viz-controls").hidden = true;
    }

    // ---------- Which token is where? ----------
    // Replays the steps up to now: "written" tokens are in the output,
    // "discarded" are parentheses that were thrown away, everything else is
    // either still waiting on the stack or not scanned yet.
    function tokenStates() {
        const state = chars.map(() => "waiting");
        const onStack = [];
        for (let k = 0; k <= index; k++) {
            const s = steps[k];
            if (s.new_stack !== null) {                    // pushed
                onStack.push(s.i);
            } else if (s.popped !== null) {                // popped from the stack
                const t = onStack.pop();
                if (s.new_output !== null) {
                    state[t] = "written";                  // operator moved to the output
                } else {
                    state[t] = "discarded";                // '(' thrown away
                    state[s.i] = "discarded";              // and the ')' that found it
                }
            } else if (s.new_output !== null) {            // operand went straight to the output
                state[s.i] = "written";
            }
        }
        return state;
    }

    // ---------- Drawing ----------
    function stackHTML(items, popped, newOnTop) {
        let html = "";
        if (popped) html += '<div class="s-item ghost">' + esc(popped) + "</div>";
        if (!items.length) return html + '<p class="muted col-empty">Stack is empty</p>';

        items.slice().reverse().forEach((value, k) => {
            const classes = (k === 0 ? " top" : "") + (k === 0 && newOnTop ? " new" : "");
            html += '<div class="s-item' + classes + '">' + esc(value) +
                    (k === 0 ? '<span class="tag">top</span>' : "") + "</div>";
        });
        return html;
    }

    function outputHTML(items, newIndex, finished) {
        if (!items.length) return '<p class="muted col-empty">Output will appear here</p>';
        return '<div class="out-row">' + items.map((value, i) =>
            '<span class="o-item' + (i === newIndex ? " new" : "") + (finished ? " final" : "") + '">' +
            esc(value) + "</span>").join("") + "</div>";
    }

    function render() {
        const step = steps[index];
        const last = index === steps.length - 1;
        const state = tokenStates();

        el("viz-tokens").innerHTML = chars.map((c, i) => {
            const cls = i === step.i ? "current" : state[i];
            return '<span class="tok ' + cls + '">' + esc(c) + "</span>";
        }).join("");

        el("viz-stack").innerHTML = stackHTML(step.stack, step.popped, step.new_stack !== null);
        el("viz-output").innerHTML = outputHTML(step.output, step.new_output, last);

        el("viz-title").textContent = step.title;
        el("viz-why").textContent = step.why;
        el("viz-count").textContent = "Step " + (index + 1) + " of " + steps.length;

        el("viz-prev").disabled = index === 0;
        el("viz-next").disabled = last;
        if (!playing) playButton.textContent = last ? "Replay" : "Play";
    }

    // ---------- Playing ----------
    function schedule() {
        clearTimeout(timer);
        timer = setTimeout(() => {
            if (index < steps.length - 1) {
                index += 1;
                render();
                schedule();
            } else {
                pause();
            }
        }, Number(speed.value));
    }

    function play() {
        playing = true;
        playButton.textContent = "Pause";
        schedule();
    }

    function pause() {
        clearTimeout(timer);
        playing = false;
        render();
    }

    playButton.addEventListener("click", () => {
        if (playing) { pause(); return; }
        if (index >= steps.length - 1) { index = 0; render(); }
        play();
    });
    el("viz-next").addEventListener("click", () => { pause(); if (index < steps.length - 1) index += 1; render(); });
    el("viz-prev").addEventListener("click", () => { pause(); if (index > 0) index -= 1; render(); });
    el("viz-restart").addEventListener("click", () => { index = 0; render(); play(); });
    speed.addEventListener("change", () => { if (playing) schedule(); });

    // Reset button: clear the input, the result and the visualizer
    const resetButton = el("postfix-reset");
    if (resetButton) {
        resetButton.addEventListener("click", () => {
            el("expression").value = "";
            ["output", "detail", "status"].forEach((id) => { el(id).textContent = ""; });
            reset();
            el("expression").focus();
        });
    }

    // app.js announces every finished conversion
    document.addEventListener("calc:result", (event) => {
        const data = event.detail;
        if (!data.ok || !data.steps) {
            reset();
            return;
        }
        clearTimeout(timer);
        playing = false;
        steps = data.steps;
        chars = data.tokens;
        index = 0;
        el("viz-controls").hidden = false;
        render();
        if (!reduceMotion) play();
    });

    reset();
})();