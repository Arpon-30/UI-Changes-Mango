/* =====================================================================
   AmropaliNet - client logic
   Language + theme, camera/upload, analysis, garden spread, encyclopedia
   ===================================================================== */
(() => {
    "use strict";

    const I18N = window.MANGO_I18N;
    const DISEASES = window.MANGO_DISEASES;
    const BY_KEY = Object.fromEntries(DISEASES.map((d) => [d.key, d]));
    const root = document.documentElement;
    const $ = (s, el = document) => el.querySelector(s);
    const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
    const show = (el) => el.classList.remove("hidden");
    const hide = (el) => el.classList.add("hidden");
    const store = {
        get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
        set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } }
    };
    const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const photoOf = (key) => "/static/img/diseases/" + key.toLowerCase().replace(/\s+/g, "-") + ".jpg";
    const imgSrc = (b64, url) => (b64 ? "data:image/jpeg;base64," + b64 : url || null);
    const DEMO = new URLSearchParams(location.search).has("demo");

    /* ---------------- Language ---------------- */
    let lang = root.getAttribute("lang") === "bn" ? "bn" : "en";
    const t = (key) => (I18N[lang] && I18N[lang][key]) || I18N.en[key] || key;
    const L = (obj) => (obj && (obj[lang] || obj.en)) || "";
    const BN_DIGITS = "০১২৩৪৫৬৭৮৯";
    const num = (s) => (lang === "bn" ? String(s).replace(/\d/g, (d) => BN_DIGITS[d]) : String(s));
    const pct = (x, dp = 1) => num((x * 100).toFixed(dp)) + "%";

    function applyI18n() {
        root.setAttribute("lang", lang);
        document.title = t("meta.title");
        $$("[data-i18n]").forEach((el) => { el.textContent = t(el.dataset.i18n); });
        $$("[data-i18n-attr]").forEach((el) => {
            el.dataset.i18nAttr.split(";").forEach((pair) => {
                const [attr, key] = pair.split(":");
                if (attr && key) el.setAttribute(attr.trim(), t(key.trim()));
            });
        });
        $$("[data-lang]").forEach((b) => {
            const on = b.dataset.lang === lang;
            b.classList.toggle("is-on", on);
            b.setAttribute("aria-pressed", String(on));
        });
        // Dynamic parts re-render in the new language
        renderCards();
        renderSdgs();
        renderDemoLabels();
        renderGardenTabs();
        renderGardenInfo();
        if (lastResult) renderResult(lastResult, false);
        if (lastNoMango) renderNotMango(lastNoMango.conf, false);
        if (statusState) setStatus(statusState.kind, statusState.titleKey, statusState.detail, statusState.detailKey);
        if (sheet.open && sheetKey) fillSheet(sheetKey);
    }

    function setLang(next) {
        if (next === lang) return;
        lang = next;
        store.set("mangoai-lang", lang);
        applyI18n();
    }
    $$("[data-lang]").forEach((b) => b.addEventListener("click", () => setLang(b.dataset.lang)));

    /* ---------------- Theme ---------------- */
    function setTheme(theme, save = true) {
        root.setAttribute("data-theme", theme);
        $$("[data-theme-set]").forEach((b) => {
            const on = b.dataset.themeSet === theme;
            b.classList.toggle("is-on", on);
            b.setAttribute("aria-pressed", String(on));
        });
        const meta = $('meta[name="theme-color"]');
        if (meta) meta.setAttribute("content", theme === "dark" ? "#0F1D13" : "#2E7D32");
        if (save) store.set("mangoai-theme", theme);
    }
    $$("[data-theme-set]").forEach((b) => b.addEventListener("click", () => setTheme(b.dataset.themeSet)));
    setTheme(root.getAttribute("data-theme") === "dark" ? "dark" : "light", false);

    /* ---------------- Header, menu, active link ---------------- */
    const header = $("#header");
    const nav = $("#nav");
    const menuBtn = $("#menu-btn");
    const fab = $(".fab");

    function closeMenu() {
        nav.classList.remove("is-open");
        menuBtn.setAttribute("aria-expanded", "false");
    }
    menuBtn.addEventListener("click", () => {
        const open = !nav.classList.contains("is-open");
        nav.classList.toggle("is-open", open);
        menuBtn.setAttribute("aria-expanded", String(open));
    });
    $$(".nav__link").forEach((a) => a.addEventListener("click", closeMenu));
    document.addEventListener("click", (e) => {
        if (nav.classList.contains("is-open") && !nav.contains(e.target) && !menuBtn.contains(e.target)) closeMenu();
    });

    let ticking = false;
    window.addEventListener("scroll", () => {
        if (ticking) return;
        ticking = true;
        requestAnimationFrame(() => {
            header.classList.toggle("is-scrolled", window.scrollY > 8);
            ticking = false;
        });
    }, { passive: true });

    const navLinks = $$(".nav__link");
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            const id = entry.target.id;
            navLinks.forEach((a) => a.classList.toggle("is-active", a.getAttribute("href") === "#" + id));
            fab.classList.toggle("is-hidden", id === "detect" || id === "home");
        });
    }, { rootMargin: "-45% 0px -50% 0px" });
    $$("main > section[id]").forEach((s) => sectionObserver.observe(s));

    /* ---------------- Reveal on scroll ---------------- */
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("is-in");
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12 });
    $$(".reveal").forEach((el) => revealObserver.observe(el));

    /* ---------------- Toast ---------------- */
    const toast = $("#toast");
    const toastMsg = $("#toast-msg");
    const toastDetail = $("#toast-detail");
    let toastTimer = null;
    // detail: optional technical reason from the server (shown small, untranslated)
    function showError(key, detail) {
        toastMsg.textContent = t(key);
        toastDetail.textContent = detail || "";
        show(toast);
        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => hide(toast), detail ? 15000 : 7000);
    }
    $("#toast-close").addEventListener("click", () => hide(toast));

    /* ---------------- Upload / camera ---------------- */
    const scanner = $("#scanner");
    const drop = $("#drop");
    const preview = $("#preview");
    const previewImg = $("#preview-img");
    const inputCamera = $("#input-camera");
    const inputGallery = $("#input-gallery");
    const btnCheck = $("#btn-check");
    const loading = $("#loading");
    const results = $("#results");
    const nomango = $("#nomango");

    const MAX_SIZE = 10 * 1024 * 1024;
    const SERVER_TYPES = ["image/jpeg", "image/png", "image/webp", "image/bmp", "image/tiff"];
    const MAX_SIDE = 1600;

    let currentFile = null;
    let previewUrl = null;
    let lastResult = null;
    let lastNoMango = null;

    function openPicker(kind) {
        const input = kind === "camera" ? inputCamera : inputGallery;
        input.value = "";
        input.click();
    }
    $$("[data-action]").forEach((b) => b.addEventListener("click", () => {
        if (sheet.open) sheet.close();
        openPicker(b.dataset.action);
        document.getElementById("detect").scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth" });
    }));
    [inputCamera, inputGallery].forEach((inp) => inp.addEventListener("change", () => {
        if (inp.files && inp.files[0]) handleFile(inp.files[0]);
    }));

    // Drag and drop (desktop)
    ["dragenter", "dragover"].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add("is-over"); }));
    ["dragleave", "dragend"].forEach((ev) => drop.addEventListener(ev, () => drop.classList.remove("is-over")));
    drop.addEventListener("drop", (e) => {
        e.preventDefault();
        drop.classList.remove("is-over");
        const f = e.dataTransfer && e.dataTransfer.files[0];
        if (f) handleFile(f);
    });

    // Resize big phone photos in the browser: faster upload, stays under 10 MB
    function loadImage(file) {
        return new Promise((resolve, reject) => {
            const url = URL.createObjectURL(file);
            const img = new Image();
            img.onload = () => { URL.revokeObjectURL(url); resolve(img); };
            img.onerror = () => { URL.revokeObjectURL(url); reject(new Error("decode")); };
            img.src = url;
        });
    }

    async function prepareFile(file) {
        let img;
        try {
            img = await loadImage(file);
        } catch (e) {
            // Browser cannot decode (e.g. TIFF): send as-is if the server accepts it
            if (SERVER_TYPES.includes(file.type) && file.size <= MAX_SIZE) return file;
            throw new Error(SERVER_TYPES.includes(file.type) ? "err.size" : "err.type");
        }
        const side = Math.max(img.naturalWidth, img.naturalHeight);
        if (side <= MAX_SIDE && file.size <= 2 * 1024 * 1024 && SERVER_TYPES.includes(file.type)) return file;

        const scale = Math.min(1, MAX_SIDE / side);
        const canvas = document.createElement("canvas");
        canvas.width = Math.round(img.naturalWidth * scale);
        canvas.height = Math.round(img.naturalHeight * scale);
        canvas.getContext("2d").drawImage(img, 0, 0, canvas.width, canvas.height);
        const blob = await new Promise((r) => canvas.toBlob(r, "image/jpeg", 0.9));
        if (!blob) throw new Error("err.bad");
        const name = (file.name || "mango").replace(/\.[^.]+$/, "") + ".jpg";
        return new File([blob], name, { type: "image/jpeg" });
    }

    async function handleFile(file) {
        if (!file.type.startsWith("image/")) return showError("err.type");
        if (file.size > 40 * 1024 * 1024) return showError("err.size");
        hide(toast);
        try {
            currentFile = await prepareFile(file);
        } catch (e) {
            return showError(e.message.startsWith("err.") ? e.message : "err.bad");
        }
        if (currentFile.size > MAX_SIZE) { currentFile = null; return showError("err.size"); }

        if (previewUrl) URL.revokeObjectURL(previewUrl);
        previewUrl = URL.createObjectURL(currentFile);
        previewImg.src = previewUrl;
        lastResult = null;
        lastNoMango = null;
        hide(results);
        hide(nomango);
        hide(drop);
        show(preview);
        btnCheck.disabled = false;
        btnCheck.focus({ preventScroll: true });
    }

    function resetScanner() {
        currentFile = null;
        lastResult = null;
        lastNoMango = null;
        if (previewUrl) URL.revokeObjectURL(previewUrl);
        previewUrl = null;
        previewImg.removeAttribute("src");
        hide(preview);
        hide(results);
        hide(nomango);
        show(drop);
    }
    $("#btn-change").addEventListener("click", () => { resetScanner(); openPicker("gallery"); });
    $("#btn-nomango-again").addEventListener("click", () => {
        resetScanner();
        openPicker("camera");
        scanner.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "center" });
    });
    $("#btn-again").addEventListener("click", () => {
        resetScanner();
        scanner.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "center" });
    });

    /* ---------------- Analyze ---------------- */
    function setBusy(busy) {
        scanner.classList.toggle("is-busy", busy);
        btnCheck.disabled = busy;
        $("#btn-change").disabled = busy;
        (busy ? show : hide)(loading);
    }

    // Real AA-ENet output for a dataset photo (Bacterial Canker), shown with ?demo=1
    function demoResult() {
        const order = ["Bacterial Canker", "Anthracnose", "Scab", "Stem End Rot", "Sooty Mould", "Powdery Mildew", "Healthy"];
        const scores = [0.9538, 0.0138, 0.0092, 0.0081, 0.0064, 0.0051, 0.0036];
        return {
            demo: true,
            predicted_class: order[0],
            confidence: scores[0],
            all_scores: order.map((c, i) => ({ class: c, score: scores[i] })),
            original_url: "/static/img/demo/photo.jpg",
            gradcam_url: "/static/img/demo/heat.jpg",
            marked_url: "/static/img/demo/marked.jpg",
            affected_percent: 8.7
        };
    }

    btnCheck.addEventListener("click", async () => {
        if (!currentFile) return;
        setBusy(true);
        hide(toast);
        try {
            let data;
            if (DEMO) {
                await new Promise((r) => setTimeout(r, 1600));
                data = demoResult();
            } else {
                const form = new FormData();
                form.append("image", currentFile);
                const res = await fetch("/api/analyze", { method: "POST", body: form });
                if (!res.ok) {
                    setBusy(false);
                    return handleApiError(await readError(res), false);
                }
                data = await res.json();
                if (!data.is_mango) { setBusy(false); return renderNotMango(data.mango_confidence); }
            }
            setBusy(false);
            lastResult = data;
            renderResult(data, true);
        } catch (e) {
            setBusy(false);
            showError(navigator.onLine === false ? "err.network" : (e instanceof TypeError ? "err.network" : "err.server"));
        }
    });

    /* ---------------- API errors ---------------- */
    async function readError(res) {
        let detail = null;
        try { detail = (await res.json()).detail; } catch (e) { /* not JSON */ }
        if (detail && typeof detail === "object") return { status: res.status, ...detail };
        return { status: res.status, code: null, message: typeof detail === "string" ? detail : "" };
    }

    function handleApiError(err, fromReport) {
        switch (err.code) {
            case "not_mango":
                return fromReport ? showError("err.notmango") : renderNotMango(err.mango_confidence);
            case "model_missing":
                setStatus("error", "st.model", err.message);
                return showError("err.model", err.message);
            case "mango_check_unavailable":
                setStatus("error", "st.clip", err.message);
                return showError("err.clip", err.message);
            case "bad_type": return showError("err.type");
            case "too_large": return showError("err.size");
            default:
                if (err.status === 422) return fromReport ? showError("err.notmango") : renderNotMango(null);
                if (err.status === 400) return showError("err.bad", err.message);
                return showError("err.server", err.message);
        }
    }

    function renderNotMango(conf, animate = true) {
        lastNoMango = { conf };
        lastResult = null;
        hide(results);
        $("#nomango-img").src = previewUrl || "";
        const p = conf == null ? "-" : pct(conf, 0);
        $("#nomango-sub").textContent = t("nm.sub").replace("{pct}", p);
        show(nomango);
        if (animate) {
            nomango.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "center" });
            nomango.focus({ preventScroll: true });
        }
    }

    /* ---------------- Model status (from /api/health) ---------------- */
    const statusBar = $("#model-status");
    let statusState = null;
    function setStatus(kind, titleKey, detail, detailKey) {
        statusState = kind ? { kind, titleKey, detail, detailKey } : null;
        if (!kind) return hide(statusBar);
        statusBar.className = "status status--" + kind;
        $("#status-icon").textContent = kind === "loading" ? "⏳" : "⚠️";
        $("#status-title").textContent = t(titleKey);
        $("#status-detail").textContent = detailKey ? t(detailKey) : (detail || "");
    }
    async function checkHealth(attempt = 0) {
        if (DEMO) return;
        try {
            const h = await (await fetch("/api/health", { cache: "no-store" })).json();
            if (h.model === "error") return setStatus("error", "st.model", h.model_error);
            if (h.mango_check === "error") return setStatus("error", "st.clip", h.mango_check_error);
            if ((h.model === "loading" || h.mango_check === "loading") && attempt < 200) {
                setStatus("loading", "st.loading", null, "st.loadingd");
                return setTimeout(() => checkHealth(attempt + 1), 3000);
            }
            setStatus(null);
        } catch (e) {
            setStatus("error", "st.offline", null, "st.offlined");
        }
    }

    function renderResult(data, animate) {
        const d = BY_KEY[data.predicted_class] || BY_KEY.Healthy;
        const healthy = d.key === "Healthy";
        const conf = Number(data.confidence) || 0;

        $("#demo-note").classList.toggle("hidden", !data.demo);
        const verdict = $("#verdict");
        verdict.classList.toggle("is-sick", !healthy);

        $("#verdict-title").innerHTML = healthy
            ? esc(t("res.healthy")) + " 🌿"
            : esc(t("res.sick")) + " <em>" + esc(L(d.name)) + "</em>";
        $("#verdict-sci").textContent = d.sci;
        $("#verdict-meta").innerHTML =
            `<span class="pill pill--${d.risk}">${esc(t("res.risk"))}: ${esc(t("risk." + d.risk))}</span>` +
            d.parts.map((p) => `<span class="pill">${esc(t("part." + p))}</span>`).join("");
        $("#verdict-warn").classList.toggle("hidden", conf >= 0.7);
        $("#ring-pct").textContent = pct(conf, 0);

        const ring = $("#ring-fill");
        const C = 2 * Math.PI * 50;
        ring.style.strokeDasharray = C;
        if (animate) {
            ring.style.strokeDashoffset = C;
            requestAnimationFrame(() => requestAnimationFrame(() => { ring.style.strokeDashoffset = C * (1 - conf); }));
        } else {
            ring.style.strokeDashoffset = C * (1 - conf);
        }

        $("#todo-list").innerHTML = L(d.remedies).map((r) => `<li>${esc(num(r))}</li>`).join("");
        $("#signs-list").innerHTML = L(d.symptoms).map((s) => `<li>${esc(s)}</li>`).join("");

        const scores = $("#scores");
        scores.innerHTML = (data.all_scores || []).map((s, i) => {
            const dd = BY_KEY[s.class];
            return `<div class="score${i === 0 ? " is-top" : ""}">
                <span>${esc(dd ? L(dd.name) : s.class)}</span><span>${pct(s.score, 1)}</span>
                <div class="score__bar"><i data-w="${(s.score * 100).toFixed(2)}"></i></div>
            </div>`;
        }).join("");
        requestAnimationFrame(() => requestAnimationFrame(() => {
            $$(".score__bar i", scores).forEach((b) => { b.style.width = b.dataset.w + "%"; });
        }));

        const heat = $("#heat");
        const orig = imgSrc(data.original_base64, data.original_url) || previewUrl;
        const cam = imgSrc(data.gradcam_base64, data.gradcam_url);
        const marked = healthy ? null : imgSrc(data.marked_base64, data.marked_url);
        $("#img-original").src = orig || "";
        if (cam) $("#img-heat").src = cam;
        if (marked) $("#img-marked").src = marked;
        $("#img-heat").closest("figure").classList.toggle("hidden", !cam);
        $("#fig-marked").classList.toggle("hidden", !marked);
        heat.classList.toggle("heat--three", !!(cam && marked));
        $(".heat__note", $("#heat-card")).classList.toggle("hidden", !cam);
        $("#heat-legend").classList.toggle("hidden", !cam);
        heat.classList.toggle("hidden", !orig && !cam);
        const aff = $("#heat-affected");
        if (healthy) aff.textContent = t("res.noaffected");
        else if (data.affected_percent != null) aff.textContent = t("res.affected").replace("{pct}", num(Math.round(data.affected_percent)) + "%");
        else aff.textContent = "";
        aff.classList.toggle("is-healthy", healthy);
        $("#img-original").alt = t("res.photo");
        $("#img-heat").alt = t("res.heat");
        $("#img-marked").alt = t("res.marked");

        $("#btn-to-garden").onclick = () => selectGarden(d.key, true);

        hide(nomango);
        show(results);
        if (animate) {
            results.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "start" });
            results.focus({ preventScroll: true });
        }
    }

    /* ---------------- Report ---------------- */
    const reportForm = $("#report-form");
    const reportName = $("#report-name");
    const reportErr = $("#report-err");
    const reportBusy = $("#report-busy");
    const btnReport = $("#btn-report");

    $("#btn-to-report").addEventListener("click", (e) => {
        e.preventDefault();
        $("#report").scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "center" });
        setTimeout(() => reportName.focus({ preventScroll: true }), reducedMotion ? 0 : 450);
    });

    reportName.addEventListener("input", () => {
        if (reportName.value.trim()) { reportForm.classList.remove("has-error"); hide(reportErr); }
    });

    reportForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = reportName.value.trim();
        if (!name) {
            reportForm.classList.add("has-error");
            show(reportErr);
            reportName.focus();
            return;
        }
        if (!currentFile) return;
        if (lastResult && lastResult.demo) return showError("rep.demo");

        show(reportBusy);
        btnReport.disabled = true;
        try {
            const form = new FormData();
            form.append("image", currentFile);
            form.append("user_name", name);
            const res = await fetch("/api/report", { method: "POST", body: form });
            if (!res.ok) {
                handleApiError(await readError(res), true);
            } else {
                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "AmropaliNet_Report_" + name.replace(/[^\p{L}\p{N}_-]+/gu, "_") + ".pdf";
                document.body.appendChild(a);
                a.click();
                a.remove();
                setTimeout(() => URL.revokeObjectURL(url), 2000);
            }
        } catch (err) {
            showError("err.network");
        } finally {
            hide(reportBusy);
            btnReport.disabled = false;
        }
    });

    /* ---------------- Garden impact (top view of an orchard) ---------------- */
    const orchard = $("#orchard");
    const treesG = $("#orchard-trees");
    const wavesG = $("#orchard-waves");
    const stages = $("#stages");
    const COLS = 6, ROWS = 3, SOURCE = { c: 2, r: 1 };
    const TREES = [];
    for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
            TREES.push({ x: 60 + c * 96, y: 60 + r * 105, d: Math.hypot(c - SOURCE.c, r - SOURCE.r) });
        }
    }
    let gardenKey = "Anthracnose";
    let gardenTimers = [];
    let gardenPlayed = false;

    treesG.innerHTML = TREES.map(({ x, y }, i) => `
        <g class="g-tree" style="--i:${i}">
            <ellipse cx="${x + 7}" cy="${y + 9}" rx="37" ry="34" fill="#000" opacity=".22"/>
            <circle class="g-canopy" cx="${x}" cy="${y}" r="38" fill="url(#g-canopy)"/>
            <circle cx="${x - 12}" cy="${y - 10}" r="14" fill="#fff" opacity=".07"/>
            <circle cx="${x + 13}" cy="${y + 6}" r="16" fill="#000" opacity=".06"/>
            <circle cx="${x - 6}" cy="${y + 16}" r="11" fill="#fff" opacity=".05"/>
            <circle class="g-sick" cx="${x}" cy="${y}" r="38" fill="url(#g-sick)"/>
            <g class="g-spots">
                <circle cx="${x - 10}" cy="${y - 6}" r="5"/><circle cx="${x + 12}" cy="${y + 4}" r="4"/><circle cx="${x - 2}" cy="${y + 15}" r="3.5"/>
            </g>
            <circle class="g-ring" cx="${x}" cy="${y}" r="42"/>
        </g>`).join("");
    const treeEls = $$(".g-tree", treesG);

    function lighten(hex, amt) {
        const n = parseInt(hex.slice(1), 16);
        const mix = (v) => Math.round(v + (255 - v) * amt);
        return `rgb(${mix(n >> 16)}, ${mix((n >> 8) & 255)}, ${mix(n & 255)})`;
    }

    function clearGarden() {
        gardenTimers.forEach(clearTimeout);
        gardenTimers = [];
        wavesG.innerHTML = "";
        treeEls.forEach((el) => el.classList.remove("is-sick", "is-safe"));
        $$("li", stages).forEach((li) => li.classList.remove("is-on"));
    }

    function at(ms, fn) { gardenTimers.push(setTimeout(fn, reducedMotion ? 0 : ms)); }

    function wave() {
        if (reducedMotion) return;
        const src = TREES[SOURCE.r * COLS + SOURCE.c];
        wavesG.insertAdjacentHTML("beforeend", `<circle class="g-wave" cx="${src.x}" cy="${src.y}" r="40"/>`);
        const w = wavesG.lastElementChild;
        w.addEventListener("animationend", () => w.remove());
    }

    function playGarden() {
        clearGarden();
        const d = BY_KEY[gardenKey];
        orchard.style.setProperty("--tone", d.tone);
        orchard.style.setProperty("--tone-light", lighten(d.tone, 0.45));
        orchard.setAttribute("aria-label", t("garden.map") + ": " + L(d.name) + " - " + L(d.spread));
        const healthy = d.key === "Healthy";
        stages.classList.toggle("is-healthy", healthy);
        if (healthy) {
            treeEls.forEach((el, i) => at(150 + i * 60, () => el.classList.add("is-safe")));
            return;
        }
        const stageLi = $$("li", stages);
        const sick = (pred) => TREES.forEach((tr, i) => { if (pred(tr.d)) at(tr.d * 260, () => treeEls[i].classList.add("is-sick")); });
        at(200, () => { stageLi[0].classList.add("is-on"); sick((dd) => dd === 0); wave(); });
        at(2000, () => { stageLi[1].classList.add("is-on"); wave(); gardenTimers.push(setTimeout(() => sick((dd) => dd > 0 && dd < 1.5), 0)); });
        at(4000, () => { stageLi[2].classList.add("is-on"); wave(); gardenTimers.push(setTimeout(() => sick((dd) => dd >= 1.5), 0)); });
    }

    function renderGardenTabs() {
        const tabs = $("#garden-tabs");
        tabs.innerHTML = DISEASES.map((d) => `
            <button class="tab" type="button" role="tab" data-key="${esc(d.key)}" aria-selected="${d.key === gardenKey}">
                ${d.emoji} ${esc(L(d.name))}
            </button>`).join("");
        $$(".tab", tabs).forEach((b) => b.addEventListener("click", () => selectGarden(b.dataset.key, false)));
    }

    function renderGardenInfo() {
        const d = BY_KEY[gardenKey];
        const parts = d.parts.length
            ? d.parts.map((p) => `<span class="pill">${esc(t("part." + p))}</span>`).join("")
            : `<span class="pill pill--none">${esc(t("risk.none"))}</span>`;
        $("#garden-info").innerHTML = `
            <h3><span class="emoji" aria-hidden="true">${d.emoji}</span>${esc(L(d.name))}</h3>
            <span class="pill pill--${d.risk}">${esc(t("res.risk"))}: ${esc(t("risk." + d.risk))}</span>
            <div class="info-row"><h4>${esc(t("garden.parts"))}</h4><div class="parts">${parts}</div></div>
            <div class="info-row"><h4>${esc(t("garden.spread"))}</h4><p>${esc(L(d.spread))}</p></div>
            <div class="info-row"><h4>${esc(t("garden.season"))}</h4><p>${esc(num(L(d.season)))}</p></div>
            <div class="info-row"><h4>${esc(t("garden.look"))}</h4><ul>${L(d.symptoms).slice(0, 3).map((s) => `<li>${esc(s)}</li>`).join("")}</ul></div>`;
        const info = $("#garden-info");
        info.style.animation = "none";
        void info.offsetWidth;
        info.style.animation = "";
    }

    function selectGarden(key, scroll) {
        gardenKey = key;
        $$("#garden-tabs .tab").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.key === key)));
        renderGardenInfo();
        playGarden();
        gardenPlayed = true;
        if (scroll) document.getElementById("garden").scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth" });
    }
    $("#btn-replay").addEventListener("click", playGarden);

    new IntersectionObserver((entries, obs) => {
        if (entries[0].isIntersecting) {
            if (!gardenPlayed) { playGarden(); gardenPlayed = true; }
            obs.disconnect();
        }
    }, { threshold: 0.35 }).observe(orchard);

    /* ---------------- Encyclopedia ---------------- */
    const cards = $("#cards");
    let filter = "all";

    function renderCards() {
        cards.innerHTML = DISEASES.map((d) => `
            <button class="card" type="button" data-key="${esc(d.key)}" style="--tone:${d.tone}">
                <span class="card__photo"><img src="${photoOf(d.key)}" alt="" loading="lazy" width="253" height="253" /></span>
                <span class="card__name">${esc(L(d.name))}</span>
                <span class="card__sci">${esc(d.sci)}</span>
                <span class="card__short">${esc(L(d.short))}</span>
                <span class="card__foot">
                    <span class="pill pill--${d.risk}">${esc(t("risk." + d.risk))}</span>
                    <span class="card__more">${esc(t("dis.open"))} <i aria-hidden="true">→</i></span>
                </span>
            </button>`).join("");
        $$(".card", cards).forEach((c) => c.addEventListener("click", () => openSheet(c.dataset.key)));
        applyFilter(false);
    }

    function applyFilter(animate) {
        let i = 0;
        $$(".card", cards).forEach((c) => {
            const d = BY_KEY[c.dataset.key];
            const match = filter === "all" || d.parts.includes(filter);
            c.classList.toggle("is-dim", !match);
            c.classList.remove("pop");
            if (match && animate) {
                c.style.animationDelay = (i++ * 50) + "ms";
                void c.offsetWidth;
                c.classList.add("pop");
            }
        });
    }
    $$(".filter").forEach((f) => f.addEventListener("click", () => {
        filter = f.dataset.filter;
        $$(".filter").forEach((x) => {
            x.classList.toggle("is-active", x === f);
            x.setAttribute("aria-pressed", String(x === f));
        });
        applyFilter(true);
    }));

    /* ---------------- Disease detail sheet ---------------- */
    const sheet = $("#sheet");
    const sheetBody = $("#sheet-body");
    let sheetKey = null;
    let sheetOpener = null;

    function fillSheet(key) {
        const d = BY_KEY[key];
        const list = (arr, tag = "ul") => `<${tag}>${arr.map((x) => `<li>${esc(num(x))}</li>`).join("")}</${tag}>`;
        sheetBody.innerHTML = `
            <div class="sheet__hero" style="--tone:${d.tone}">
                <button class="sheet__close" type="button" aria-label="${esc(t("dis.close"))}">✕</button>
                <img class="sheet__photo" src="${photoOf(d.key)}" alt="" width="253" height="253" />
                <h3 id="sheet-title">${esc(L(d.name))}</h3>
                <p class="card__sci">${esc(d.sci)}</p>
                <div class="verdict__meta" style="margin-top:10px">
                    <span class="pill pill--${d.risk}">${esc(t("res.risk"))}: ${esc(t("risk." + d.risk))}</span>
                    ${d.parts.map((p) => `<span class="pill">${esc(t("part." + p))}</span>`).join("")}
                </div>
            </div>
            <div class="sheet__body">
                <p class="sheet__desc">${esc(L(d.desc))}</p>
                <div class="sheet__grid">
                    <div class="sheet__block"><h4>👀 ${esc(t("dis.symptoms"))}</h4>${list(L(d.symptoms))}</div>
                    <div class="sheet__block"><h4>🌬️ ${esc(t("dis.spread"))}</h4><p>${esc(L(d.spread))}</p></div>
                </div>
                <div class="sheet__block"><h4>✅ ${esc(t("dis.treatment"))}</h4>${list(L(d.remedies), "ol")}</div>
                <div class="sheet__block"><h4>🛡️ ${esc(t("dis.prevent"))}</h4>${list(L(d.prevent))}</div>
            </div>
            <div class="sheet__cta">
                <button class="btn btn--mango" type="button" data-sheet-scan><span aria-hidden="true">📷</span><span>${esc(t("dis.scan"))}</span></button>
            </div>`;
        $(".sheet__close", sheetBody).addEventListener("click", () => sheet.close());
        $("[data-sheet-scan]", sheetBody).addEventListener("click", () => {
            sheet.close();
            openPicker("camera");
            document.getElementById("detect").scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth" });
        });
    }

    function openSheet(key) {
        sheetKey = key;
        sheetOpener = document.activeElement;
        fillSheet(key);
        if (typeof sheet.showModal === "function") sheet.showModal();
        else sheet.setAttribute("open", "");
        sheetBody.scrollTop = 0;
        document.body.style.overflow = "hidden";
    }
    sheet.addEventListener("close", () => {
        document.body.style.overflow = "";
        sheetKey = null;
        if (sheetOpener && sheetOpener.focus) sheetOpener.focus({ preventScroll: true });
    });
    sheet.addEventListener("click", (e) => { if (e.target === sheet) sheet.close(); });

    /* ---------------- Hero preview + How it works (real model output) ---------------- */
    function renderDemoLabels() {
        $("#hero-result-name").textContent = L(BY_KEY.Anthracnose.name);
        $("#hero-result-pct").textContent = pct(0.954, 0);
        $("#wf-name").textContent = L(BY_KEY["Bacterial Canker"].name);
        $("#wf-pct").textContent = pct(0.954, 0) + " " + t("res.sure");
    }

    const workflow = $("#workflow");
    const WF_TIMES = [1500, 2000, 1900, 1900, 2800];
    let wfStep = 0, wfTimer = null, wfVisible = false;
    function setStep(n) {
        wfStep = n;
        workflow.dataset.step = String(n);
        $$(".workflow__steps li", workflow).forEach((li) => {
            const i = Number(li.dataset.step);
            li.classList.toggle("is-on", i === n);
            li.classList.toggle("is-done", i < n);
        });
    }
    function runWorkflow() {
        clearTimeout(wfTimer);
        if (!wfVisible || reducedMotion) return;
        wfTimer = setTimeout(() => { setStep((wfStep + 1) % 5); runWorkflow(); }, WF_TIMES[wfStep]);
    }
    $$(".workflow__steps li", workflow).forEach((li) => li.addEventListener("click", () => { setStep(Number(li.dataset.step)); runWorkflow(); }));
    setStep(reducedMotion ? 4 : 0);
    new IntersectionObserver((entries) => {
        wfVisible = entries[0].isIntersecting;
        if (wfVisible) runWorkflow(); else clearTimeout(wfTimer);
    }, { threshold: 0.3 }).observe(workflow);

    /* ---------------- SDG goals ---------------- */
    const SDGS = [[1, "#E5243B"], [2, "#DDA63A"], [12, "#BF8B2E"], [13, "#3F7E44"], [15, "#56C02B"]];
    function renderSdgs() {
        $("#sdg-grid").innerHTML = SDGS.map(([n, c]) => `
            <li class="sdg__card" style="--c:${c}">
                <b>${num(n)}</b>
                <div><strong>${esc(t("sdg." + n + "t"))}</strong><span>${esc(t("sdg." + n + "d"))}</span></div>
            </li>`).join("");
        $$(".eco__sdgs span").forEach((sp) => { sp.textContent = "SDG " + num(sp.dataset.n); });
    }

    /* ---------------- Init ---------------- */
    applyI18n();
    checkHealth();
})();
