/* ════════════════════════════════════════════════════════════════
   MangoAI — Client-side logic
   Theme toggle, classification, remedies, flip cards, animations
   ════════════════════════════════════════════════════════════════ */
(() => {
    "use strict";

    // ── DOM refs ────────────────────────────────────────────────
    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    const dropzone       = $("#dropzone");
    const fileInput      = $("#file-input");
    const previewArea    = $("#preview-area");
    const previewImg     = $("#preview-img");
    const btnRemove      = $("#btn-remove");
    const btnClassify    = $("#btn-classify");

    const loadingSection = $("#loading-section");
    const errorToast     = $("#error-toast");
    const errorMsg       = $("#error-msg");
    const errorClose     = $("#error-close");

    const resultsSection = $("#results-section");
    const resultBadge    = $("#result-badge");
    const resultPct      = $("#result-pct");
    const resultScientific = $("#result-scientific");
    const ringFill       = $("#ring-fill");
    const scoresGrid     = $("#scores-grid");

    const gradcamSection  = $("#gradcam-section");
    const gradcamOriginal = $("#gradcam-original");
    const gradcamHeatmap  = $("#gradcam-heatmap");

    const remediesSection = $("#remedies-section");
    const remediesContent = $("#remedies-content");

    const reportSection  = $("#report-section");
    const reportName     = $("#report-name");
    const nameInputGroup = $("#name-input-group");
    const btnReport      = $("#btn-report");
    const reportLoading  = $("#report-loading");

    const diseaseGrid    = $("#disease-grid");
    const themeToggle    = $("#theme-toggle");
    const themeIcon      = $("#theme-icon");

    // ── Disease Info Database (mirrored from backend) ──────────
    const DISEASE_DATA = {
        "Anthracnose": {
            emoji: "🍂",
            scientific: "Colletotrichum gloeosporioides",
            desc: "A major fungal disease affecting mango leaves, flowers, and fruits. It causes significant post-harvest losses and can devastate entire crops if not managed promptly.",
            symptoms: [
                "Dark brown to black irregular spots on leaves",
                "Water-soaked lesions that enlarge rapidly",
                "Premature leaf drop and defoliation",
                "Blossom blight and twig dieback",
                "Fruit rot that remains latent until ripening"
            ],
            remedies: [
                "Apply copper-based fungicides (Bordeaux mixture)",
                "Use systemic fungicides like Carbendazim or Mancozeb",
                "Prune and destroy infected branches and leaves",
                "Post-harvest: Hot water treatment (50–55°C for 5–10 min)",
                "Maintain good orchard hygiene and spacing"
            ]
        },
        "Bacterial Canker": {
            emoji: "🦠",
            scientific: "Xanthomonas campestris pv. mangiferaeindicae",
            desc: "A serious bacterial infection that affects all above-ground parts of the mango tree. It causes severe economic losses especially in commercial orchards during wet seasons.",
            symptoms: [
                "Water-soaked angular lesions on leaves",
                "Yellow halo surrounding dark lesions",
                "Cracking and gummosis on twigs and branches",
                "Lesions may ooze a yellow bacterial exudate",
                "Severe defoliation and fruit drop"
            ],
            remedies: [
                "Spray copper oxychloride (0.3%) at 15-day intervals",
                "Apply Streptomycin sulfate (500 ppm) sprays",
                "Prune and burn infected plant materials",
                "Avoid overhead irrigation to reduce humidity",
                "Apply copper-based bactericides during rainy season"
            ]
        },
        "Healthy": {
            emoji: "🌿",
            scientific: "Mangifera indica (Normal)",
            desc: "The mango leaf shows no signs of disease or infection. The plant appears to be in excellent health with normal leaf coloration, texture, and structure.",
            symptoms: [
                "Vibrant green leaf coloration",
                "Smooth and glossy leaf surface",
                "No spots, lesions, or discoloration",
                "Normal leaf shape and size",
                "Healthy growth pattern"
            ],
            remedies: [
                "Continue regular monitoring of the plant",
                "Maintain balanced fertilization schedule",
                "Ensure proper irrigation practices",
                "Keep orchard clean and well-maintained",
                "Monitor for early signs of pest or disease"
            ]
        },
        "Powdery Mildew": {
            emoji: "🌫️",
            scientific: "Oidium mangiferae",
            desc: "A common fungal disease that appears as a white powdery coating on mango leaves, flowers, and young fruits. It thrives in dry weather with cool nights and warm days.",
            symptoms: [
                "White powdery coating on leaf surfaces",
                "Affected leaves curl and distort",
                "Flower panicles covered in white powder",
                "Premature flower and fruit drop",
                "Reduced fruit set and yield"
            ],
            remedies: [
                "Spray wettable sulfur (0.2%) or Karathane",
                "Apply Triadimefon (0.1%) fungicide",
                "Use sulfur-based fungicides during dry season",
                "Ensure good orchard ventilation through pruning",
                "Apply fungicides starting at early flowering stage"
            ]
        },
        "Scab": {
            emoji: "🔶",
            scientific: "Elsinoë mangiferae",
            desc: "A fungal disease causing rough, corky, raised spots on mango leaves, twigs, and fruits. It significantly reduces the market value of affected fruits even when severity is moderate.",
            symptoms: [
                "Dark brown to gray corky scab lesions",
                "Raised, rough-textured spots on leaves",
                "Distortion of young leaves and shoots",
                "Small raised grey-to-brownish lesions on fruit",
                "Leaves may become deformed or crinkled"
            ],
            remedies: [
                "Apply Zineb or Maneb fungicides",
                "Spray Copper oxychloride at 15-day intervals",
                "Remove and destroy dead leaves and twigs",
                "Apply copper-based fungicides from flower bud emergence",
                "Continue treatment until fruit reaches half size"
            ]
        },
        "Sooty Mould": {
            emoji: "🖤",
            scientific: "Capnodium mangiferae",
            desc: "A secondary fungal disease that grows on honeydew excreted by sap-sucking insects. While not directly infecting plant tissue, it blocks sunlight and reduces photosynthesis significantly.",
            symptoms: [
                "Black sooty coating covering leaf surfaces",
                "Coating easily wiped off revealing green leaf",
                "Presence of scale insects or aphids nearby",
                "Reduced photosynthesis and plant vigor",
                "Black velvety coating on twigs and fruits"
            ],
            remedies: [
                "Control sap-sucking insects first (insecticides/neem oil)",
                "Spray starch solution to remove sooty coating",
                "Prune heavily infected, dense branches",
                "Apply systemic insecticides for hoppers/mealybugs",
                "Maintain good air circulation in the orchard"
            ]
        },
        "Stem End Rot": {
            emoji: "⚫",
            scientific: "Lasiodiplodia theobromae",
            desc: "A devastating post-harvest fungal disease that begins at the stem end of harvested mango fruits. It can cause up to 60% post-harvest losses if proper handling and treatment protocols are not followed.",
            symptoms: [
                "Dark brown to black rotting starting at stem end",
                "Soft, water-soaked lesion spreading rapidly",
                "White to gray fungal growth on rotted area",
                "Pulp becomes soft and brown",
                "Rapid deterioration after harvest"
            ],
            remedies: [
                "Hot water treatment (52°C for 5 min) post-harvest",
                "Apply Prochloraz (0.05%) fungicide dip",
                "Avoid harvesting immature fruit",
                "Pre-harvest sprays of carbendazim",
                "Post-harvest hot water dips with/without fungicides"
            ]
        }
    };

    // ── State ───────────────────────────────────────────────────
    let currentFile = null;
    let lastClassification = null;

    // ── Helpers ─────────────────────────────────────────────────
    const show = (el) => el.classList.remove("hidden");
    const hide = (el) => el.classList.add("hidden");

    const MAX_SIZE = 10 * 1024 * 1024;
    const ALLOWED = new Set(["image/jpeg", "image/png", "image/webp", "image/bmp", "image/tiff"]);

    function validateFile(file) {
        if (!file) return "No file selected.";
        if (!ALLOWED.has(file.type)) return "Unsupported file type. Please use JPG, PNG, or WebP.";
        if (file.size > MAX_SIZE) return `File too large (${(file.size / 1024 / 1024).toFixed(1)} MB). Max is 10 MB.`;
        return null;
    }

    function showError(msg) {
        errorMsg.textContent = msg;
        show(errorToast);
        errorToast.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    function clearResults() {
        hide(resultsSection);
        hide(gradcamSection);
        hide(remediesSection);
        hide(reportSection);
        hide(errorToast);
        lastClassification = null;
    }

    // ── Theme Toggle ────────────────────────────────────────────
    function initTheme() {
        const saved = localStorage.getItem("mangoai-theme");
        const theme = saved || "dark";
        document.documentElement.setAttribute("data-theme", theme);
        themeIcon.textContent = theme === "dark" ? "🌙" : "☀️";
    }

    function toggleTheme() {
        const current = document.documentElement.getAttribute("data-theme");
        const next = current === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem("mangoai-theme", next);
        themeIcon.textContent = next === "dark" ? "🌙" : "☀️";
    }

    themeToggle.addEventListener("click", toggleTheme);
    themeToggle.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggleTheme(); }
    });
    initTheme();

    // ── Disease Encyclopedia Cards ──────────────────────────────
    function buildDiseaseCards() {
        diseaseGrid.innerHTML = "";
        for (const [name, data] of Object.entries(DISEASE_DATA)) {
            const card = document.createElement("div");
            card.className = "flip-card fade-in";
            card.innerHTML = `
                <div class="flip-card__inner">
                    <div class="flip-card__front">
                        <div class="flip-card__emoji">${data.emoji}</div>
                        <div class="flip-card__name">${name}</div>
                        <div class="flip-card__scientific">${data.scientific}</div>
                        <p class="flip-card__desc">${data.desc}</p>
                        <div class="flip-card__hint">Click to see symptoms & treatment →</div>
                    </div>
                    <div class="flip-card__back">
                        <div class="flip-card__back-title">${data.emoji} ${name}</div>
                        <div class="flip-card__back-subtitle symptoms">⚠️ Symptoms</div>
                        <ul class="flip-card__back-list">
                            ${data.symptoms.map(s => `<li><span class="bullet">•</span>${s}</li>`).join("")}
                        </ul>
                        <div class="flip-card__back-subtitle treatment">✅ Treatment</div>
                        <ul class="flip-card__back-list">
                            ${data.remedies.map(r => `<li><span class="bullet">✓</span>${r}</li>`).join("")}
                        </ul>
                    </div>
                </div>
            `;
            card.addEventListener("click", () => card.classList.toggle("is-flipped"));
            diseaseGrid.appendChild(card);
        }
    }
    buildDiseaseCards();

    // ── File selection ──────────────────────────────────────────
    function handleFile(file) {
        const err = validateFile(file);
        if (err) { showError(err); return; }

        currentFile = file;
        clearResults();

        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            show(previewArea);
            hide(dropzone);
            btnClassify.disabled = false;
        };
        reader.readAsDataURL(file);
    }

    // ── Drag & Drop ─────────────────────────────────────────────
    dropzone.addEventListener("click", () => fileInput.click());
    dropzone.addEventListener("dragenter", (e) => { e.preventDefault(); dropzone.classList.add("drag-over"); });
    dropzone.addEventListener("dragover", (e) => { e.preventDefault(); dropzone.classList.add("drag-over"); });
    dropzone.addEventListener("dragleave", () => dropzone.classList.remove("drag-over"));
    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("drag-over");
        const file = e.dataTransfer.files[0];
        if (file) handleFile(file);
    });

    fileInput.addEventListener("change", () => {
        if (fileInput.files[0]) handleFile(fileInput.files[0]);
    });

    // ── Remove image ────────────────────────────────────────────
    btnRemove.addEventListener("click", () => {
        currentFile = null;
        fileInput.value = "";
        previewImg.src = "";
        hide(previewArea);
        show(dropzone);
        btnClassify.disabled = true;
        clearResults();
    });

    // ── Error close ─────────────────────────────────────────────
    errorClose.addEventListener("click", () => hide(errorToast));

    // ── Classify ────────────────────────────────────────────────
    btnClassify.addEventListener("click", async () => {
        if (!currentFile) return;

        clearResults();
        hide(errorToast);
        show(loadingSection);
        btnClassify.disabled = true;

        const form = new FormData();
        form.append("image", currentFile);

        try {
            const res = await fetch("/api/classify", { method: "POST", body: form });
            const data = await res.json();

            hide(loadingSection);

            if (!res.ok) {
                showError(data.error || "Classification failed.");
                btnClassify.disabled = false;
                return;
            }

            lastClassification = data;
            renderResults(data);
            btnClassify.disabled = false;

        } catch (err) {
            hide(loadingSection);
            showError("Network error — please try again.");
            btnClassify.disabled = false;
        }
    });

    // ── Render results ──────────────────────────────────────────
    function renderResults(data) {
        const cls = data.classification;
        const gcam = data.gradcam;
        const diseaseInfo = data.disease_info || DISEASE_DATA[cls.predicted_class] || {};

        // Result hero
        resultBadge.textContent = cls.predicted_class;
        const pctVal = (cls.confidence * 100).toFixed(2);
        resultPct.textContent = pctVal + "%";

        // Scientific name
        const sciName = diseaseInfo.scientific_name || (DISEASE_DATA[cls.predicted_class] || {}).scientific || "";
        resultScientific.textContent = sciName;

        // Confidence ring animation
        const circumference = 2 * Math.PI * 50; // r=50
        const offset = circumference * (1 - cls.confidence);
        ringFill.style.strokeDasharray = circumference;
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                ringFill.style.strokeDashoffset = offset;
            });
        });

        show(resultsSection);

        // Scores
        scoresGrid.innerHTML = "";
        cls.all_scores.forEach((s, i) => {
            const pct = (s.score * 100).toFixed(2);
            const row = document.createElement("div");
            row.className = "score-row";
            row.innerHTML = `
                <span class="score-row__name ${i === 0 ? "is-top" : ""}">${s.class}</span>
                <div class="score-bar">
                    <div class="score-bar__fill" style="width:0%"></div>
                </div>
                <span class="score-row__pct">${pct}%</span>
            `;
            scoresGrid.appendChild(row);

            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    row.querySelector(".score-bar__fill").style.width = pct + "%";
                });
            });
        });

        // Grad-CAM
        gradcamOriginal.src = "data:image/png;base64," + gcam.original_b64;
        gradcamHeatmap.src = "data:image/png;base64," + gcam.heatmap_b64;
        show(gradcamSection);

        // Remedies
        renderRemedies(cls.predicted_class, diseaseInfo);

        // Report section
        show(reportSection);

        // Trigger fade-in for newly visible sections
        triggerFadeIn();

        // Scroll to results
        resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    // ── Render Remedies ─────────────────────────────────────────
    function renderRemedies(diseaseName, info) {
        const localData = DISEASE_DATA[diseaseName] || {};
        const symptoms = info.symptoms || localData.symptoms || [];
        const remedies = info.remedies || localData.remedies || [];

        if (symptoms.length === 0 && remedies.length === 0) {
            hide(remediesSection);
            return;
        }

        remediesContent.innerHTML = `
            <div class="remedies-column">
                <h3 class="symptoms-title">⚠️ Symptoms</h3>
                <ul class="remedies-list">
                    ${symptoms.map(s => `<li><span class="icon">•</span><span>${s}</span></li>`).join("")}
                </ul>
            </div>
            <div class="remedies-column">
                <h3 class="treatment-title">✅ Recommended Treatment</h3>
                <ul class="remedies-list">
                    ${remedies.map(r => `<li><span class="icon">✓</span><span>${r}</span></li>`).join("")}
                </ul>
            </div>
        `;
        show(remediesSection);
    }

    // ── Report name input → enable button ───────────────────────
    reportName.addEventListener("input", () => {
        const hasName = reportName.value.trim().length > 0;
        btnReport.disabled = !hasName;
        if (hasName) {
            nameInputGroup.classList.remove("has-error");
        }
    });

    // ── Report download ─────────────────────────────────────────
    btnReport.addEventListener("click", async () => {
        if (!currentFile || !lastClassification) return;
        const name = reportName.value.trim();
        if (!name) {
            nameInputGroup.classList.add("has-error");
            reportName.focus();
            return;
        }

        show(reportLoading);
        btnReport.disabled = true;

        const form = new FormData();
        form.append("image", currentFile);
        form.append("user_name", name);

        try {
            const res = await fetch("/api/report", { method: "POST", body: form });

            if (!res.ok) {
                const data = await res.json();
                showError(data.error || "Report generation failed.");
                hide(reportLoading);
                btnReport.disabled = false;
                return;
            }

            // Trigger download
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `AmropaliNet_Report_${name.replace(/\s+/g, "_")}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);

            hide(reportLoading);
            btnReport.disabled = name.length === 0;

        } catch (err) {
            showError("Network error — could not download the report.");
            hide(reportLoading);
            btnReport.disabled = false;
        }
    });

    // ── Intersection Observer for fade-in ───────────────────────
    function triggerFadeIn() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        $$(".fade-in").forEach((el) => {
            if (!el.classList.contains("is-visible")) {
                observer.observe(el);
            }
        });
    }

    // Initialize fade-in on page load
    triggerFadeIn();

    // ── Smooth scroll for nav links ─────────────────────────────
    $$(".navbar__link[href^='#']").forEach((link) => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            const target = document.querySelector(link.getAttribute("href"));
            if (target) {
                target.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        });
    });
})();
