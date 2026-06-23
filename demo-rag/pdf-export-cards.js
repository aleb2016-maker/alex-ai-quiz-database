(() => {
  const DEFAULT_SELECTORS = [
    "[data-pdf-card]",
    ".pdf-card",
    ".rag-card",
    ".generated-card",
    ".output-card",
    ".smart-card",
    ".training-card",
    ".study-card",
    ".card-generata",
    ".card-preview",
    ".result-card",
    ".universal-card",
    ".document-card",
    ".course-card",
    ".summary-card"
  ];

  const API_URL =
    window.ALEX_PDF_EXPORT_API_URL ||
    "http://127.0.0.1:8030/api/export/cards-pdf";

  function log(...args) {
    console.log("[pdf-export-cards]", ...args);
  }

  function uniqueElements(elements) {
    const seen = new Set();
    const result = [];
    for (const el of elements) {
      if (!el || seen.has(el)) continue;
      seen.add(el);
      result.push(el);
    }
    return result;
  }

  function isVisibleCardCandidate(el) {
    const rect = el.getBoundingClientRect();
    if (rect.width < 220 || rect.height < 140) return false;
    const style = window.getComputedStyle(el);
    if (style.display === "none" || style.visibility === "hidden" || Number(style.opacity) === 0) return false;
    const text = (el.innerText || "").trim();
    const hasMedia = el.querySelector("img, canvas, svg");
    return text.length > 20 || hasMedia;
  }

  function findCardElements() {
    let found = [];

    for (const selector of DEFAULT_SELECTORS) {
      found.push(...document.querySelectorAll(selector));
    }

    found = uniqueElements(found).filter(isVisibleCardCandidate);

    if (found.length > 0) return found;

    // Fallback: cerca elementi grandi dentro aree output probabili.
    const outputRoots = [
      "#output",
      "#risultato",
      "#results",
      "#cards-output",
      "#card-output",
      ".output",
      ".results",
      ".cards-output",
      ".generated-output",
      "main"
    ]
      .flatMap((selector) => Array.from(document.querySelectorAll(selector)))
      .filter(Boolean);

    const candidates = [];
    for (const root of outputRoots.length ? outputRoots : [document.body]) {
      candidates.push(...root.querySelectorAll("section, article, div"));
    }

    return uniqueElements(candidates).filter(isVisibleCardCandidate).slice(0, 60);
  }

  function loadImage(src) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = "anonymous";
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = src;
    });
  }

  async function imageElementToDataUrl(img) {
    if (img.src.startsWith("data:image/")) return img.src;

    const loaded = await loadImage(img.src);
    const canvas = document.createElement("canvas");
    canvas.width = loaded.naturalWidth || loaded.width;
    canvas.height = loaded.naturalHeight || loaded.height;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(loaded, 0, 0);
    return canvas.toDataURL("image/png");
  }

  function canvasToDataUrl(canvas) {
    return canvas.toDataURL("image/png");
  }

  function copyComputedStyle(source, target) {
    const computed = window.getComputedStyle(source);
    for (const key of computed) {
      try {
        target.style.setProperty(key, computed.getPropertyValue(key), computed.getPropertyPriority(key));
      } catch (_) {}
    }

    for (let i = 0; i < source.children.length; i++) {
      copyComputedStyle(source.children[i], target.children[i]);
    }
  }

  async function foreignObjectToDataUrl(node) {
    const rect = node.getBoundingClientRect();
    const width = Math.ceil(rect.width);
    const height = Math.ceil(rect.height);

    const clone = node.cloneNode(true);
    copyComputedStyle(node, clone);
    clone.setAttribute("xmlns", "http://www.w3.org/1999/xhtml");

    const serialized = new XMLSerializer().serializeToString(clone);
    const svg = `
      <svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">
        <foreignObject width="100%" height="100%">
          ${serialized}
        </foreignObject>
      </svg>
    `;

    const svgUrl = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
    const img = await loadImage(svgUrl);

    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0);
    return canvas.toDataURL("image/png");
  }

  async function elementToDataUrl(el) {
    if (el.tagName === "CANVAS") return canvasToDataUrl(el);

    if (el.tagName === "IMG") return imageElementToDataUrl(el);

    const directCanvas = el.querySelector("canvas");
    if (directCanvas && el.children.length <= 2) {
      return canvasToDataUrl(directCanvas);
    }

    const directImage = el.matches("img") ? el : el.querySelector(":scope > img");
    if (directImage && el.children.length <= 2) {
      return imageElementToDataUrl(directImage);
    }

    if (window.htmlToImage && typeof window.htmlToImage.toPng === "function") {
      return await window.htmlToImage.toPng(el, {
        cacheBust: true,
        pixelRatio: 2,
        backgroundColor: window.getComputedStyle(el).backgroundColor || "#ffffff"
      });
    }

    if (window.html2canvas) {
      const canvas = await window.html2canvas(el, {
        backgroundColor: null,
        scale: 2,
        useCORS: true
      });
      return canvas.toDataURL("image/png");
    }

    return await foreignObjectToDataUrl(el);
  }

  async function collectCardImages() {
    // Se il motore card espone già immagini finali, usa quelle.
    if (Array.isArray(window.__generatedCardImages) && window.__generatedCardImages.length) {
      return window.__generatedCardImages.map((dataUrl, index) => ({
        name: `card_${String(index + 1).padStart(2, "0")}.png`,
        dataUrl
      }));
    }

    const cards = findCardElements();

    if (!cards.length) {
      throw new Error("Nessuna card trovata. Genera prima le card nella demo.");
    }

    const images = [];
    for (let i = 0; i < cards.length; i++) {
      const el = cards[i];
      el.scrollIntoView({ block: "center", inline: "center" });
      await new Promise((resolve) => setTimeout(resolve, 120));

      const dataUrl = await elementToDataUrl(el);
      images.push({
        name: `card_${String(i + 1).padStart(2, "0")}.png`,
        dataUrl
      });
    }

    return images;
  }

  async function downloadCardsPdf(options = {}) {
    const title = options.title || document.title || "PDF card generate";
    const filename = options.filename || "card-generate.pdf";

    const images = await collectCardImages();
    log("card catturate:", images.length);

    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, filename, images })
    });

    if (!response.ok) {
      let message = `Errore export PDF: ${response.status}`;
      try {
        const data = await response.json();
        if (data.error) message += ` - ${data.error}`;
      } catch (_) {}
      throw new Error(message);
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();

    setTimeout(() => URL.revokeObjectURL(url), 30000);
  }

  function findExistingPdfButton() {
    const buttons = Array.from(document.querySelectorAll("button, a"));
    return buttons.find((btn) => /scarica\s*pdf|download\s*pdf|pdf/i.test(btn.textContent || ""));
  }

  function installButtonHook() {
    const existing = findExistingPdfButton();

    if (existing && !existing.dataset.pdfExportHooked) {
      existing.dataset.pdfExportHooked = "1";
      existing.addEventListener("click", async (event) => {
        event.preventDefault();
        event.stopPropagation();
        existing.disabled = true;
        const oldText = existing.textContent;
        existing.textContent = "Genero PDF...";
        try {
          await downloadCardsPdf();
        } catch (error) {
          alert(error.message || String(error));
          console.error(error);
        } finally {
          existing.disabled = false;
          existing.textContent = oldText;
        }
      }, true);
      log("hook installato su bottone esistente:", existing);
      return;
    }

    if (document.querySelector("#alexScaricaPdfCardButton")) return;

    const btn = document.createElement("button");
    btn.id = "alexScaricaPdfCardButton";
    btn.type = "button";
    btn.textContent = "Scarica PDF Card";
    btn.style.cssText = [
      "position:fixed",
      "right:18px",
      "bottom:18px",
      "z-index:999999",
      "padding:14px 18px",
      "border:0",
      "border-radius:14px",
      "background:#0f4c81",
      "color:white",
      "font-weight:800",
      "box-shadow:0 10px 28px rgba(0,0,0,.28)",
      "cursor:pointer"
    ].join(";");

    btn.addEventListener("click", async () => {
      btn.disabled = true;
      btn.textContent = "Genero PDF...";
      try {
        await downloadCardsPdf();
      } catch (error) {
        alert(error.message || String(error));
        console.error(error);
      } finally {
        btn.disabled = false;
        btn.textContent = "Scarica PDF Card";
      }
    });

    document.body.appendChild(btn);
    log("bottone floating aggiunto");
  }

  window.AlexPdfExportCards = {
    collectCardImages,
    downloadCardsPdf,
    installButtonHook,
    findCardElements
  };

  document.addEventListener("DOMContentLoaded", () => {
    setTimeout(installButtonHook, 700);
  });
})();
