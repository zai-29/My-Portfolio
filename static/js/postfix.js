// Animates the infix to postfix conversion, one step at a time.
// The server sends every step (the stack and the output at that moment).
// This file only draws them, using the same node boxes as the linked list page.
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

    function nodeBox(value, classes) {
        return '<div class="node' + classes + '"><span class="ptr"></span>' +
               '<span class="val">' + esc(value) + '</span><span class="ptr"></span></div>';
    }

    // Same drawing as the doubly linked list page:  None <-> [node] <-> [node] <-> None
    function chain(items, newIndex, lastLabel, popped, finished, emptyText) {
        if (!items.length && !popped) return '<p class="muted">' + emptyText + "</p>";

        let html = '<span class="null">None</span>';
        items.forEach((value, i) => {
            let label = "";
            if (items.length === 1) label = "head, " + lastLabel;
            else if (i === 0) label = "head";
            else if (i === items.length - 1) label = lastLabel;

            const classes = (i === newIndex ? " new" : "") + (finished ? " final" : "");
            html += '<span class="link"></span><div class="slot"><span class="label">' + label +
                    "</span>" + nodeBox(value, classes) + "</div>";
        });

        // The node that was just popped fades upward
        if (popped) {
            html += '<div class="ghostwrap"><span class="link"></span><div class="slot">' +
                    '<span class="label"></span>' + nodeBox(popped, "") + "</div></div>";
        }
        return html + '<span class="link"></span><span class="null">None</span>';
    }

    function render() {
        const step = steps[index];
        const last = index === steps.length - 1;

        el("viz-tokens").innerHTML = chars.map((c, i) => {
            const state = i === step.i ? " current" : i < step.i ? " done" : "";
            return '<span class="tok' + state + '">' + esc(c) + "</span>";
        }).join("");

        el("viz-stack").innerHTML = chain(step.stack, step.new_stack, "top", step.popped, false, "The stack is empty.");
        el("viz-output").innerHTML = chain(step.output, step.new_output, "tail", null, last, "The output is empty.");

        el("viz-title").textContent = step.title;
        el("viz-why").textContent = step.why;
        el("viz-count").textContent = "Step " + (index + 1) + " of " + steps.length;

        el("viz-prev").disabled = index === 0;
        el("viz-next").disabled = last;
        if (!playing) playButton.textContent = last ? "Replay" : "Play";
    }

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

    // app.js announces every finished conversion
    document.addEventListener("calc:result", (event) => {
        const data = event.detail;
        clearTimeout(timer);
        playing = false;

        if (!data.ok || !data.steps) {
            panel.hidden = true;
            return;
        }
        steps = data.steps;
        chars = data.tokens;
        index = 0;
        panel.hidden = false;
        render();
        if (!reduceMotion) play();
    });
})();