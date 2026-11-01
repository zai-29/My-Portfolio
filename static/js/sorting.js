// Sorting visualizer. Python (sorting.py) sorts the numbers and records every step.
// This file replays the recording as bars.
(function () {
    const root = document.getElementById("sv");
    if (!root) return;

    const $ = (selector) => root.querySelector(selector);
    const INFO = JSON.parse(root.dataset.info);
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const playButton = $("#sv-play");
    const speed = $("#sv-speed");

    let algo = "bubble", steps = [], index = 0, timer = null, playing = false;
    let low = 0, high = 1;           // smallest and biggest number, used to scale the bars

    function setStatus(text, kind) {
        const status = $("#sv-status");
        status.textContent = text || "";
        status.dataset.kind = kind || "info";
    }

    // ---------- Bars ----------
    function barHeight(value) {
        if (high === low) return 60;
        return 12 + 76 * (value - low) / (high - low);      // 12% to 88% of the box
    }

    // Reuses the same elements every step, so the bars animate instead of flickering
    function paint(container, cells) {
        while (container.children.length < cells.length) {
            const column = document.createElement("div");
            column.innerHTML = '<span class="bar-val"></span><div class="bar"></div>';
            container.appendChild(column);
        }
        while (container.children.length > cells.length) container.lastChild.remove();

        cells.forEach((cell, i) => {
            const column = container.children[i];
            column.className = "bar-col" + (cell.dim ? " dim" : "") + (cell.empty ? " empty" : "");
            column.firstChild.textContent = cell.label;
            column.lastChild.className = "bar" + (cell.cls ? " " + cell.cls : "");
            column.lastChild.style.height = cell.empty ? "0%" : barHeight(cell.height) + "%";
        });
    }

    function mainCells(step) {
        return step.array.map((value, i) => {
            const dim = step.span && (i < step.span[0] || i > step.span[1]);
            if (value === null) {                                   // the empty slot in insertion sort
                return { label: "", cls: "hole", height: step.key, dim: dim };
            }
            let cls = "";
            if (step.sorted.includes(i)) cls += " sorted";
            if (i === step.marker) cls += " marker";
            if (i === step.pivot) cls += " pivot";
            if (step.compare.includes(i)) cls += " compare";
            if (step.moved.includes(i)) cls += " moved";
            return { label: String(value), cls: cls.trim(), height: value, dim: dim };
        });
    }

    function auxCells(step) {
        const aux = step.aux;
        return step.array.map((_, column) => {
            const k = column - aux.lo;
            if (k < 0 || k >= aux.values.length) return { label: "", height: 0, empty: true };
            let cls = "";
            if (aux.used.includes(k)) cls += " used";
            if (k === aux.i || k === aux.j) cls += " compare";
            return { label: String(aux.values[k]), cls: cls.trim(), height: aux.values[k] };
        });
    }

    function render() {
        const step = steps[index];
        const last = index === steps.length - 1;

        $("#sv-title").textContent = $("#sv-name").textContent;
        $("#sv-msg").textContent = step.message;

        const keyBox = $("#sv-key");
        keyBox.hidden = step.key === null;
        if (step.key !== null) keyBox.textContent = "Key: " + step.key;

        paint($("#sv-bars"), mainCells(step));

        $("#sv-aux-wrap").hidden = !step.aux;
        if (step.aux) paint($("#sv-aux"), auxCells(step));

        $("#sv-counts").textContent = "Comparisons: " + step.comparisons + "    Swaps / writes: " + step.moves;
        $("#sv-count").textContent = "Step " + (index + 1) + " of " + steps.length;
        $("#sv-scrub").value = index;

        $("#sv-prev").disabled = index === 0;
        $("#sv-next").disabled = last;
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
        if (!steps.length) return;
        if (playing) { pause(); return; }
        if (index >= steps.length - 1) { index = 0; render(); }
        play();
    });
    $("#sv-next").addEventListener("click", () => { pause(); if (index < steps.length - 1) index += 1; render(); });
    $("#sv-prev").addEventListener("click", () => { pause(); if (index > 0) index -= 1; render(); });
    $("#sv-restart").addEventListener("click", () => { index = 0; render(); play(); });
    $("#sv-scrub").addEventListener("input", (event) => {
        const target = Number(event.target.value);     // read it first: pause() redraws the slider
        pause();
        index = target;
        render();
    });
    speed.addEventListener("change", () => { if (playing) schedule(); });

    // ---------- Choosing the algorithm and running it ----------
    function selectAlgo(key) {
        algo = key;
        root.querySelectorAll(".seg").forEach((button) =>
            button.setAttribute("aria-pressed", String(button.dataset.algo === key)));

        const info = INFO[key];
        $("#sv-name").textContent = info.name;
        $("#sv-desc").textContent = info.description;

        if (steps.length) run();           // already showing a sort: redo it with the new algorithm
    }

    async function run() {
        const body = new FormData();
        body.set("algorithm", algo);
        body.set("data", $("#sv-data").value);

        let result;
        try {
            const response = await fetch(root.dataset.url, { method: "POST", body: body });
            result = await response.json();
        } catch (error) {
            result = { ok: false, error: "Something went wrong. Please try again." };
        }
        if (!result.ok) {
            setStatus(result.error, "error");
            return;
        }

        setStatus("");
        clearTimeout(timer);
        playing = false;
        steps = result.steps;
        low = Math.min(...steps[0].array);
        high = Math.max(...steps[0].array);
        index = 0;
        $("#sv-scrub").max = steps.length - 1;
        $("#sv-viz").hidden = false;
        render();
        if (!reduceMotion) play();
    }

    root.querySelectorAll(".seg").forEach((button) =>
        button.addEventListener("click", () => selectAlgo(button.dataset.algo)));
    $("#sv-run").addEventListener("click", run);
    $("#sv-data").addEventListener("keydown", (event) => {
        if (event.key === "Enter") { event.preventDefault(); run(); }
    });
    $("#sv-random").addEventListener("click", () => {
        const numbers = Array.from({ length: 12 }, () => 1 + Math.floor(Math.random() * 99));
        $("#sv-data").value = numbers.join(", ");
    });

    selectAlgo("bubble");
})();