(() => {
  const HTML2CANVAS_CDN = "https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js";
  const JSPDF_CDN = "https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js";

  const PAGE_W = 960;
  const PAGE_H = 540;

  const CANVAS_W = 1600;
  const CANVAS_H = 900;

  const DARK_BG = "#0f172a";
  const WHITE = "#ffffff";

  const GROUPS = [
    {
      key: "cards",
      title: "Card",
      itemSelectors: [
        "[data-pdf-card]", ".training-card", ".generated-card", ".card-generata",
        ".card-preview", ".smart-card", ".document-card", ".course-card",
        ".result-card", ".rag-card", ".universal-card"
      ],
      containerSelectors: ["[data-export-section=\"cards\"]", "#cards", "#cards-output", ".cards-output", ".generated-cards"]
    },
    {
      key: "summary",
      title: "Riassunti",
      itemSelectors: ["[data-pdf-summary]", ".summary-card", ".riassunto-card", ".summary-block"],
      containerSelectors: ["[data-export-section=\"summary\"]", "#riassunto", "#riassunti", ".riassunto-output", ".summary-output"]
    },
    {
      key: "study",
      title: "Domande studio",
      itemSelectors: ["[data-pdf-study]", ".study-question-card", ".domande-studio-card", ".question-card"],
      containerSelectors: ["[data-export-section=\"study\"]", "#domande-studio", "#study-questions", ".study-questions-output"]
    },
    {
      key: "test",
      title: "Test",
      itemSelectors: ["[data-pdf-test]", ".quiz-card", ".test-card", ".question-test-card"],
      containerSelectors: ["[data-export-section=\"test\"]", "#test", "#quiz", ".test-output", ".quiz-output"]
    }
  ];

  function log(...args) {
    console.log("[pdf-browser-export-v6]", ...args);
  }

  function ensureLib(src, check) {
    return new Promise((resolve, reject) => {
      if (check()) return resolve();

      const existing = Array.from(document.querySelectorAll("script")).find((s) => s.src === src);
      if (existing) {
        const timer = setInterval(() => {
          if (check()) {
            clearInterval(timer);
            resolve();
          }
        }, 100);
        setTimeout(() => {
          clearInterval(timer);
          reject(new Error("Timeout caricamento libreria: " + src));
        }, 15000);
        return;
      }

      const script = document.createElement("script");
      script.src = src;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error("Errore caricamento libreria: " + src));
      document.head.appendChild(script);
    });
  }

  async function ensureDependencies() {
    await ensureLib(HTML2CANVAS_CDN, () => !!window.html2canvas);
    await ensureLib(JSPDF_CDN, () => !!(window.jspdf && window.jspdf.jsPDF));
  }

  function isVisible(el) {
    if (!el) return false;
    const style = getComputedStyle(el);
    if (style.display === "none" || style.visibility === "hidden" || Number(style.opacity) === 0) return false;
    const rect = el.getBoundingClientRect();
    return rect.width >= 120 && rect.height >= 40;
  }

  function unique(elements) {
    const seen = new Set();
    const out = [];
    for (const el of elements) {
      if (!el || seen.has(el)) continue;
      seen.add(el);
      out.push(el);
    }
    return out;
  }

  function findBySelectors(selectors) {
    return unique(
      selectors
        .flatMap((selector) => Array.from(document.querySelectorAll(selector)))
        .filter(isVisible)
    );
  }

  function collectItems(group) {
    const direct = findBySelectors(group.itemSelectors);
    if (direct.length) return direct;

    const containers = findBySelectors(group.containerSelectors);
    if (containers.length) return containers;

    return [];
  }

  function collectGroups() {
    return GROUPS.map((group) => ({
      ...group,
      items: collectItems(group)
    })).filter((group) => group.items.length > 0);
  }

  async function captureElement(el) {
    el.scrollIntoView({ block: "center", inline: "center" });
    await new Promise((resolve) => setTimeout(resolve, 140));

    return await window.html2canvas(el, {
      scale: 2,
      useCORS: true,
      allowTaint: true,
      backgroundColor: null,
      scrollX: 0,
      scrollY: 0
    });
  }

  function roundedRect(ctx, x, y, width, height, radius) {
    const r = Math.min(radius, width / 2, height / 2);
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + width, y, x + width, y + height, r);
    ctx.arcTo(x + width, y + height, x, y + height, r);
    ctx.arcTo(x, y + height, x, y, r);
    ctx.arcTo(x, y, x + width, y, r);
    ctx.closePath();
  }

  function drawPageBackground(ctx) {
    ctx.fillStyle = DARK_BG;
    ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);
  }

  function drawTitle(ctx, title) {
    ctx.fillStyle = WHITE;
    ctx.font = "900 58px system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif";
    ctx.textBaseline = "top";
    ctx.fillText(title, 96, 86);
  }

  function drawShadow(ctx, x, y, w, h, radius) {
    ctx.save();
    ctx.shadowColor = "rgba(0,0,0,0.38)";
    ctx.shadowBlur = 32;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 18;
    ctx.fillStyle = "rgba(0,0,0,0.28)";
    roundedRect(ctx, x, y, w, h, radius);
    ctx.fill();
    ctx.restore();
  }

  function fitInside(srcW, srcH, maxW, maxH) {
    const scale = Math.min(maxW / srcW, maxH / srcH);
    return { w: srcW * scale, h: srcH * scale };
  }

  function composeTextPage(groupTitle, itemCanvas) {
    const scene = document.createElement("canvas");
    scene.width = CANVAS_W;
    scene.height = CANVAS_H;

    const ctx = scene.getContext("2d");
    drawPageBackground(ctx);
    drawTitle(ctx, groupTitle);

    const slotX = 96;
    const slotY = 182;
    const slotMaxW = CANVAS_W - 192;
    const slotMaxH = CANVAS_H - slotY - 96;

    const fitted = fitInside(itemCanvas.width, itemCanvas.height, slotMaxW, slotMaxH);

    // Se il blocco è molto basso, non lo allunghiamo: lo mettiamo come nella demo,
    // con abbastanza spazio sotto e senza tagliare testi.
    const boxW = fitted.w;
    const boxH = fitted.h;
    const x = slotX + (slotMaxW - boxW) / 2;
    const y = slotY;

    const radius = 44;

    drawShadow(ctx, x, y, boxW, boxH, radius);

    ctx.save();
    roundedRect(ctx, x, y, boxW, boxH, radius);
    ctx.clip();

    // Fondo bianco sotto l'immagine: evita trasparenze ma mantiene il clipping stondato.
    ctx.fillStyle = WHITE;
    ctx.fillRect(x, y, boxW, boxH);

    ctx.drawImage(itemCanvas, x, y, boxW, boxH);
    ctx.restore();

    return scene;
  }

  function composeCardPage(cardCanvas) {
    const scene = document.createElement("canvas");
    scene.width = CANVAS_W;
    scene.height = CANVAS_H;

    const ctx = scene.getContext("2d");
    drawPageBackground(ctx);

    const fitted = fitInside(cardCanvas.width, cardCanvas.height, CANVAS_W - 28, CANVAS_H - 28);
    const x = (CANVAS_W - fitted.w) / 2;
    const y = (CANVAS_H - fitted.h) / 2;
    ctx.drawImage(cardCanvas, x, y, fitted.w, fitted.h);

    return scene;
  }

  function addCanvasPage(pdf, canvas, isFirstPage) {
    if (!isFirstPage) pdf.addPage([PAGE_W, PAGE_H], "landscape");

    const dataUrl = canvas.toDataURL("image/png");
    pdf.addImage(dataUrl, "PNG", 0, 0, PAGE_W, PAGE_H, undefined, "FAST");
  }

  async function exportSectionsToPdf(options = {}) {
    await ensureDependencies();

    const groups = collectGroups();
    if (!groups.length) {
      throw new Error("Nessun contenuto trovato per il PDF. Genera prima card/riassunti/domande/test.");
    }

    log("gruppi trovati:", groups.map((g) => `${g.key}:${g.items.length}`).join(", "));

    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF({ orientation: "landscape", unit: "pt", format: [PAGE_W, PAGE_H] });

    let hasPage = false;

    for (const group of groups) {
      for (const item of group.items) {
        const captured = await captureElement(item);

        let pageCanvas;
        if (group.key === "cards") {
          pageCanvas = composeCardPage(captured);
        } else {
          pageCanvas = composeTextPage(group.title, captured);
        }

        addCanvasPage(pdf, pageCanvas, !hasPage);
        hasPage = true;
      }
    }

    pdf.save(options.fileName || "materiale-generato.pdf");
  }

  function findPdfButton() {
    const buttons = Array.from(document.querySelectorAll("button, a"));
    return buttons.find((btn) => /scarica\s*pdf|download\s*pdf/i.test(btn.textContent || ""));
  }

  function installHook() {
    const btn = findPdfButton();

    if (btn && !btn.dataset.browserPdfHookedV6) {
      btn.dataset.browserPdfHookedV6 = "1";
      btn.addEventListener("click", async (event) => {
        event.preventDefault();
        event.stopPropagation();

        const old = btn.textContent;
        btn.disabled = true;
        btn.textContent = "Genero PDF...";

        try {
          await exportSectionsToPdf({ fileName: "materiale-generato.pdf" });
        } catch (err) {
          alert(err.message || String(err));
          console.error(err);
        } finally {
          btn.disabled = false;
          btn.textContent = old;
        }
      }, true);

      log("Hook V6 installato su bottone esistente");
      return;
    }

    if (document.querySelector("#alexBrowserPdfButtonV6")) return;

    const floating = document.createElement("button");
    floating.id = "alexBrowserPdfButtonV6";
    floating.type = "button";
    floating.textContent = "Scarica PDF";
    floating.style.cssText = [
      "position:fixed","right:18px","bottom:18px","z-index:999999",
      "padding:14px 18px","border:0","border-radius:14px",
      "background:#b91c1c","color:white","font-weight:800",
      "box-shadow:0 12px 28px rgba(0,0,0,.28)","cursor:pointer"
    ].join(";");

    floating.addEventListener("click", async () => {
      floating.disabled = true;
      const old = floating.textContent;
      floating.textContent = "Genero PDF...";

      try {
        await exportSectionsToPdf({ fileName: "materiale-generato.pdf" });
      } catch (err) {
        alert(err.message || String(err));
        console.error(err);
      } finally {
        floating.disabled = false;
        floating.textContent = old;
      }
    });

    document.body.appendChild(floating);
  }

  window.AlexBrowserPdfExportV6 = {
    ensureDependencies,
    collectGroups,
    exportSectionsToPdf,
    installHook
  };

  document.addEventListener("DOMContentLoaded", () => setTimeout(installHook, 700));
})();
