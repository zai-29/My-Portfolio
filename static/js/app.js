// Shared behaviour: dark mode, no-reload forms, history, linked list.
(function () {
    const $ = (selector, root = document) => root.querySelector(selector);

    // ---------- Helpers ----------
    async function send(url, formData) {
        try {
            const response = await fetch(url, { method: "POST", body: formData });
            return await response.json();
        } catch (err) {
            return { ok: false, error: "Something went wrong. Please try again." };
        }
    }

    function setStatus(text, kind) {
        const status = $("#status");
        if (!status) return;
        status.textContent = text || "";
        status.dataset.kind = kind || "info";
    }

    function setHistory(html) {
        const box = $("#history");
        if (box && html !== undefined) box.innerHTML = html;
    }

    function showResult(data) {
        const output = $("#output"), detail = $("#detail");
        if (data.ok) {
            setStatus("");
            output.textContent = data.result;
            if (detail) detail.textContent = data.detail || "";
        } else {
            output.textContent = "";
            if (detail) detail.textContent = "";
            setStatus(data.error, "error");
        }
        setHistory(data.history);
        document.dispatchEvent(new CustomEvent("calc:result", { detail: data }));
    }

    // ---------- Clear history (works on every page that has one) ----------
    document.addEventListener("click", async (event) => {
        const button = event.target.closest("[data-clear-history]");
        if (!button) return;
        const data = await send("/history/" + button.dataset.clearHistory + "/clear", new FormData());
        setHistory(data.history);
    });

    // ---------- String methods ----------
    const stringForm = $("#string-form");
    if (stringForm) {
        const select = $("#method");
        const sync = () => {
            const args = JSON.parse(select.selectedOptions[0].dataset.args || "[]");
            [1, 2].forEach((n) => {
                const wrap = $("#arg" + n + "-wrap");
                wrap.hidden = args.length < n;
                if (args.length >= n) $("#arg" + n + "-label").textContent = args[n - 1];
            });
        };
        select.addEventListener("change", sync);
        sync();
        stringForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            showResult(await send(stringForm.action, new FormData(stringForm)));
        });
    }

    // ---------- Area of circle and triangle ----------
    const areaForm = $("#area-form") || $("#postfix-form");
    if (areaForm) {
        areaForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            showResult(await send(areaForm.action, new FormData(areaForm)));
        });
    }

    // ---------- Doubly linked list ----------
    document.querySelectorAll(".ll-form").forEach((form) => {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            const data = await send(form.getAttribute("action"), new FormData(form, event.submitter));
            if (data.html) $("#list-view").innerHTML = data.html;
            setStatus(data.message || data.error, data.ok ? "info" : "error");
            if (data.ok) {
                form.reset();
                const firstInput = $("input", form);
                if (firstInput) firstInput.focus();
            }
        });
    });
})();
