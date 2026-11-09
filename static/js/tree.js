// Binary search tree visualizer. Python (binary_tree.py and tree_steps.py) does the work
// and records every step. This file draws the tree and replays the steps.
(function () {
    const root = document.getElementById("tv");
    if (!root) return;

    const $ = (selector) => root.querySelector(selector);
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const playButton = $("#tv-play");
    const speed = $("#tv-speed");
    const NEEDS_NUMBER = ["insert", "search", "delete"];

    let current = JSON.parse(root.dataset.tree);    // the tree as it is now
    let initial = current;                           // the tree before the operation that is playing
    let steps = [], index = 0, timer = null, playing = false;
    let shown = new Set();                           // numbers drawn last time (new ones pop in)

    function setStatus(text, kind) {
        const status = $("#tv-status");
        status.textContent = text || "";
        status.dataset.kind = kind || "info";
    }

    // ---------- Drawing the tree ----------
    const GAP = 54, ROW = 74, RADIUS = 21, PAD = 32;

    // Every node gets a column (its position in sorted order) and a row (its depth).
    // That keeps the tree tidy and stops nodes from overlapping.
    function layout(tree) {
        const nodes = [], edges = [];
        let column = 0, deepest = 0;
        function place(node, depth) {
            if (!node) return null;
            const left = place(node.left, depth + 1);
            const me = { value: node.value, column: column++, depth: depth };
            const right = place(node.right, depth + 1);
            deepest = Math.max(deepest, depth);
            nodes.push(me);
            if (left) edges.push([me, left]);
            if (right) edges.push([me, right]);
            return me;
        }
        place(tree, 0);
        return { nodes: nodes, edges: edges, columns: column, deepest: deepest };
    }

    function draw(tree, step) {
        const holder = $("#tv-tree");
        if (!tree) {
            holder.innerHTML = '<p class="muted tv-empty">The tree is empty. Insert a number or press Random tree.</p>';
            shown = new Set();
            return;
        }

        const lay = layout(tree);
        const width = (lay.columns - 1) * GAP + 2 * PAD;
        const height = lay.deepest * ROW + 2 * PAD;
        const x = (n) => PAD + n.column * GAP;
        const y = (n) => PAD + n.depth * ROW;
        const has = (list, value) => !!step && list.includes(value);

        let svg = '<svg class="tree-svg" viewBox="0 0 ' + width + " " + height + '" ' +
                  'style="width:100%;max-width:' + Math.max(width * 1.4, 240) + 'px" role="img" aria-label="The binary search tree">';

        lay.edges.forEach(([a, b]) => {
            svg += '<line class="t-edge" x1="' + x(a) + '" y1="' + y(a) + '" x2="' + x(b) + '" y2="' + y(b) + '"/>';
        });

        lay.nodes.forEach((n) => {
            let cls = "t-node";
            if (has(step && step.visited, n.value)) cls += " visited";
            if (has(step && step.focus, n.value)) cls += " focus";
            if (has(step && step.found, n.value)) cls += " found";
            if (has(step && step.remove, n.value)) cls += " remove";
            if (!shown.has(n.value)) cls += " pop";
            svg += '<g class="' + cls + '"><circle cx="' + x(n) + '" cy="' + y(n) + '" r="' + RADIUS + '"/>' +
                   '<text x="' + x(n) + '" y="' + y(n) + '">' + n.value + "</text></g>";
        });

        holder.innerHTML = svg + "</svg>";
        shown = new Set(lay.nodes.map((n) => n.value));
    }

    // The tree on screen at a given step: the last tree a step carried, or the starting tree
    function treeAt(i) {
        for (let k = i; k >= 0; k--) {
            if ("tree" in steps[k]) return steps[k].tree;
        }
        return initial;
    }

    function render() {
        if (!steps.length) {
            draw(current, null);
            return;
        }
        const step = steps[index];
        const last = index === steps.length - 1;

        draw(treeAt(index), step);
        $("#tv-msg").textContent = step.message;

        const wrap = $("#tv-output-wrap");
        wrap.hidden = step.output === null;
        if (step.output !== null) {
            $("#tv-output-label").textContent =
                /traversal/i.test($("#tv-title").textContent) ? "Visited order" : "Path from the root";
            $("#tv-output").innerHTML = step.output.map((value, i) =>
                '<span class="chip' + (i === step.output.length - 1 ? " new" : "") + '">' + value + "</span>").join("");
        }

        $("#tv-count").textContent = "Step " + (index + 1) + " of " + steps.length;
        $("#tv-scrub").value = index;
        $("#tv-prev").disabled = index === 0;
        $("#tv-next").disabled = last;
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
    $("#tv-next").addEventListener("click", () => { pause(); if (index < steps.length - 1) index += 1; render(); });
    $("#tv-prev").addEventListener("click", () => { pause(); if (index > 0) index -= 1; render(); });
    $("#tv-restart").addEventListener("click", () => { index = 0; render(); play(); });
    $("#tv-scrub").addEventListener("input", (event) => {
        const target = Number(event.target.value);       // read it first: pause() redraws the slider
        pause();
        index = target;
        render();
    });
    speed.addEventListener("change", () => { if (playing) schedule(); });

    // ---------- Running an operation ----------
    async function run(action) {
        const input = $("#tv-value");
        const body = new FormData();
        body.set("action", action);
        body.set("value", input.value);

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

        setStatus(result.message, "info");
        clearTimeout(timer);
        playing = false;
        initial = result.before;
        current = result.after;
        steps = result.steps;
        index = 0;
        $("#tv-title").textContent = result.title;
        $("#tv-controls").hidden = steps.length === 0;

        if (steps.length) {
            $("#tv-scrub").max = steps.length - 1;
            render();
            if (!reduceMotion) play();
        } else {
            $("#tv-msg").textContent = result.message;
            $("#tv-output-wrap").hidden = true;
            draw(current, null);
        }

        if (action === "insert" || action === "delete") input.value = "";
        if (NEEDS_NUMBER.includes(action)) input.focus();
    }

    root.addEventListener("click", (event) => {
        const button = event.target.closest("[data-action]");
        if (button) run(button.dataset.action);
    });
    $("#tv-value").addEventListener("keydown", (event) => {
        if (event.key === "Enter") { event.preventDefault(); run("insert"); }
    });

    draw(current, null);
})();