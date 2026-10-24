// Queue and deque visualizer. Python (queues.py) does the work with linked list nodes
// and sends back the new list. This file draws it and plays the animation.
(function () {
    const root = document.getElementById("qd");
    if (!root) return;

    const $ = (selector) => root.querySelector(selector);
    const data = { queue: JSON.parse(root.dataset.queue), deque: JSON.parse(root.dataset.deque) };
    const ADD_ACTIONS = ["enqueue", "addFront", "addRear"];

    const INFO = {
        queue: {
            title: "Queue (first in, first out)",
            desc: "The first item added is the first one removed, like people waiting in line. " +
                  "Enqueue adds at the rear. Dequeue removes from the front.",
            left: "<strong>Front</strong><span>← out: dequeue</span>",
            right: "<strong>Rear</strong><span>← in: enqueue</span>",
            defaultAdd: "enqueue",
        },
        deque: {
            title: "Deque (double-ended queue)",
            desc: "Items can be added and removed at both ends, so it works as a queue, a stack, or both.",
            left: "<strong>Front</strong><span>→ in: addFront</span><span>← out: removeFront</span>",
            right: "<strong>Rear</strong><span>← in: addRear</span><span>→ out: removeRear</span>",
            defaultAdd: "addRear",
        },
    };

    let mode = "queue";
    let busy = false;

    function esc(text) {
        const span = document.createElement("span");
        span.textContent = text;
        return span.innerHTML;
    }

    function setStatus(text, kind) {
        const status = $("#qd-status");
        status.textContent = text || "";
        status.dataset.kind = kind || "info";
    }

    // Draws the boxes. `change` says what just happened so the right box can animate.
    function render(items, change) {
        let html = "";
        const added = change && change.change === "add";
        const removed = change && change.change === "remove";

        const ghost = (side) =>
            '<div class="q-slot"><span class="q-tag"></span><div class="q-box ghost-' + side + '">' +
            esc(change.value) + "</div></div>";

        if (removed && change.end === "front") html += ghost("left");

        items.forEach((value, i) => {
            let tag = "";
            if (items.length === 1) tag = "front, rear";
            else if (i === 0) tag = "front";
            else if (i === items.length - 1) tag = "rear";

            let enter = "";
            if (added && change.end === "front" && i === 0) enter = " enter-left";
            if (added && change.end === "rear" && i === items.length - 1) enter = " enter-right";

            html += '<div class="q-slot"><span class="q-tag">' + tag + '</span><div class="q-box' + enter + '">' +
                    esc(value) + "</div></div>";
        });

        if (!items.length) html += '<p class="muted q-empty">Empty. Add some data below.</p>';
        if (removed && change.end === "rear") html += ghost("right");

        $("#qd-items").innerHTML = html;

        $("#qd-info").textContent = items.length
            ? "Size: " + items.length + "   Front: " + items[0] + "   Rear: " + items[items.length - 1]
            : "Size: 0 (empty)";
    }

    // Briefly highlights the end of the line where the operation happened
    function flash(end) {
        const target = end === "front" ? $("#qd-left") : end === "rear" ? $("#qd-right") : null;
        if (!target) return;
        target.classList.remove("flash");
        void target.offsetWidth;            // restart the animation
        target.classList.add("flash");
    }

    function setMode(next) {
        mode = next;
        root.querySelectorAll(".seg").forEach((button) =>
            button.setAttribute("aria-pressed", String(button.dataset.mode === mode)));
        root.querySelectorAll(".q-ops").forEach((group) => { group.hidden = group.dataset.for !== mode; });
        $("#qd-title").textContent = INFO[mode].title;
        $("#qd-desc").textContent = INFO[mode].desc;
        $("#qd-left").innerHTML = INFO[mode].left;
        $("#qd-right").innerHTML = INFO[mode].right;
        setStatus("");
        render(data[mode], null);
    }

    async function run(action) {
        if (busy) return;
        const input = $("#qd-value");

        const body = new FormData();
        body.set("mode", mode);
        body.set("action", action);
        body.set("value", input.value);

        busy = true;
        let result;
        try {
            const response = await fetch(root.dataset.url, { method: "POST", body: body });
            result = await response.json();
        } catch (error) {
            result = { ok: false, error: "Something went wrong. Please try again." };
        }
        busy = false;

        if (!result.ok) {
            setStatus(result.error, "error");
            return;
        }
        data[mode] = result.items;
        render(result.items, result);
        flash(result.end);
        setStatus(result.message, "info");
        if (ADD_ACTIONS.includes(action)) input.value = "";
        input.focus();
    }

    root.querySelectorAll(".seg").forEach((button) =>
        button.addEventListener("click", () => setMode(button.dataset.mode)));

    root.addEventListener("click", (event) => {
        const button = event.target.closest("[data-action]");
        if (button) run(button.dataset.action);
    });

    // Enter in the box adds the data with the main add function
    $("#qd-value").addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            run(INFO[mode].defaultAdd);
        }
    });

    setMode("queue");
})();