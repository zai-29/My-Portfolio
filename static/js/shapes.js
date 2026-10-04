// 3D preview that follows the form inputs.
//   circle   -> cylinder of radius r and height 1
//   triangle -> triangular prism with the given base and height, depth 1
// The floor grid shows the scale. Each square is 1, 10, 100... of the chosen unit.
(function () {
    const stage = document.getElementById("stage");
    if (!stage) return;

    if (!window.THREE) {
        stage.textContent = "The 3D preview needs an internet connection to load Three.js.";
        return;
    }

    const type = stage.dataset.shape;
    const root = document.documentElement;
    const css = (name) => getComputedStyle(root).getPropertyValue(name).trim();

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 5000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    stage.appendChild(renderer.domElement);

    scene.add(new THREE.AmbientLight(0xffffff, 0.65));
    const light = new THREE.DirectionalLight(0xffffff, 0.85);
    light.position.set(30, 60, 40);
    scene.add(light);

    const fillMaterial = new THREE.MeshStandardMaterial({ roughness: 0.45, metalness: 0.1 });
    const lineMaterial = new THREE.LineBasicMaterial();

    // Unit-sized geometry that is scaled to the inputs
    let geometry;
    if (type === "circle") {
        geometry = new THREE.CylinderGeometry(1, 1, 1, 64);
        geometry.translate(0, 0.5, 0);               // bottom sits on the floor
    } else {
        const outline = new THREE.Shape();
        outline.moveTo(-0.5, 0);
        outline.lineTo(0.5, 0);
        outline.lineTo(0, 1);
        outline.closePath();
        geometry = new THREE.ExtrudeGeometry(outline, { depth: 1, bevelEnabled: false });
        geometry.translate(0, 0, -0.5);
    }
    const mesh = new THREE.Mesh(geometry, fillMaterial);
    mesh.add(new THREE.LineSegments(new THREE.EdgesGeometry(geometry, 30), lineMaterial));
    scene.add(mesh);

    // Floor grid (rebuilt when the theme changes so its colors update)
    let grid;
    function applyTheme() {
        fillMaterial.color.set(css("--accent"));
        lineMaterial.color.set(css("--ink"));
        if (grid) { scene.remove(grid); grid.geometry.dispose(); grid.material.dispose(); }
        grid = new THREE.GridHelper(40, 40, css("--grid-a"), css("--grid-b"));
        grid.scale.setScalar(target.step);
        scene.add(grid);
    }

    // Where the shape is heading, and where it is now (eased every frame)
    const target = { sx: 3, sy: 1, sz: 3, ty: 0.5, extent: 6, step: 1 };
    const now = { sx: 3, sy: 1, sz: 3, ty: 0.5, dist: 9 };

    function readInputs() {
        const num = (id) => parseFloat(document.getElementById(id).value);
        if (type === "circle") {
            const r = num("radius");
            if (!(r > 0)) return;
            Object.assign(target, { sx: r, sy: 1, sz: r, ty: 0.5, extent: Math.max(2 * r, 1) });
        } else {
            const b = num("base"), h = num("height");
            if (!(b > 0 && h > 0)) return;
            Object.assign(target, { sx: b, sy: h, sz: 1, ty: h / 2, extent: Math.max(b, h, 1) });
        }
        const step = Math.pow(10, Math.max(0, Math.ceil(Math.log10(target.extent / 10))));
        if (step !== target.step) { target.step = step; if (grid) grid.scale.setScalar(step); }

        const unit = document.getElementById("unit").value;
        document.getElementById("grid-note").textContent =
            "Each grid square is " + step.toLocaleString() + " " + unit + ".";
    }

    // Orbit camera: drag to turn, slow spin when idle
    let azimuth = -0.6, elevation = 0.45;
    let dragging = false, lastX = 0, lastY = 0;
    stage.addEventListener("pointerdown", (e) => {
        dragging = true; lastX = e.clientX; lastY = e.clientY; stage.setPointerCapture(e.pointerId);
    });
    stage.addEventListener("pointermove", (e) => {
        if (!dragging) return;
        azimuth -= (e.clientX - lastX) * 0.01;
        elevation = Math.min(1.4, Math.max(0.05, elevation + (e.clientY - lastY) * 0.01));
        lastX = e.clientX; lastY = e.clientY;
    });
    const release = () => { dragging = false; };
    stage.addEventListener("pointerup", release);
    stage.addEventListener("pointercancel", release);

    ["radius", "base", "height"].forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.addEventListener("input", readInputs);
    });
    document.getElementById("unit").addEventListener("change", readInputs);

    function resize() {
        const size = stage.clientWidth;
        renderer.setSize(size, size, false);
    }
    window.addEventListener("resize", resize);
    new MutationObserver(applyTheme).observe(root, { attributes: true, attributeFilter: ["data-theme"] });

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const ease = reduceMotion ? 1 : 0.14;

    function animate() {
        requestAnimationFrame(animate);
        for (const key of ["sx", "sy", "sz", "ty"]) now[key] += (target[key] - now[key]) * ease;
        now.dist += (Math.max(8, target.extent * 2.3) - now.dist) * ease;
        mesh.scale.set(now.sx, now.sy, now.sz);

        if (!dragging && !reduceMotion) azimuth += 0.004;
        camera.position.set(
            now.dist * Math.sin(azimuth) * Math.cos(elevation),
            now.ty + now.dist * Math.sin(elevation),
            now.dist * Math.cos(azimuth) * Math.cos(elevation)
        );
        camera.lookAt(0, now.ty, 0);
        renderer.render(scene, camera);
    }

    readInputs();
    Object.assign(now, { sx: target.sx, sy: target.sy, sz: target.sz, ty: target.ty });
    applyTheme();
    resize();
    animate();
})();
