(function () {
  "use strict";

  const VERSION = "rag-document-input-unico-v1";
  const LONG_DOCUMENT_CHARS = 25000;
  const VERY_LONG_DOCUMENT_CHARS = 90000;

  function nowIso() {
    return new Date().toISOString();
  }

  function safeString(value) {
    return String(value == null ? "" : value);
  }

  function normalizeText(value) {
    return safeString(value).replace(/\u00A0/g, " ").replace(/[ \t]+/g, " ").trim();
  }

  function slugify(text) {
    return normalizeText(text)
      .toLowerCase()
      .replace(/[^a-z0-9à-öø-ÿ]+/gi, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 70) || "documento";
  }

  function extensionFromName(name) {
    const clean = safeString(name).trim();
    const dot = clean.lastIndexOf(".");
    return dot >= 0 ? clean.slice(dot + 1).toLowerCase() : "";
  }

  function sourceTypeFromFile(file) {
    const extension = extensionFromName(file && file.name);
    if (extension === "pdf") return "pdf";
    if (extension === "md" || extension === "markdown") return "md";
    if (extension === "txt") return "txt";
    return extension || "file";
  }

  function readFileAsText(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(safeString(reader.result));
      reader.onerror = () => reject(reader.error || new Error("Errore lettura file."));
      reader.readAsText(file);
    });
  }

  function readFileAsArrayBuffer(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(reader.error || new Error("Errore lettura file binario."));
      reader.readAsArrayBuffer(file);
    });
  }

  async function readPdfWithPdfJs(file) {
    if (!window.pdfjsLib || !window.pdfjsLib.getDocument) {
      throw new Error("PDF non leggibile in questa pagina: pdf.js non è collegato. Usa il parser PDF già presente nella pagina principale oppure incolla il testo estratto.");
    }

    const buffer = await readFileAsArrayBuffer(file);
    const pdf = await window.pdfjsLib.getDocument({ data: buffer }).promise;
    const pages = [];

    for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber += 1) {
      const page = await pdf.getPage(pageNumber);
      const content = await page.getTextContent();
      const pageText = content.items.map((item) => item.str || "").join(" ");
      pages.push(`\n\n[PAGINA ${pageNumber}]\n${pageText}`);
    }

    return pages.join("\n").trim();
  }

  async function extractTextFromFile(file) {
    const sourceType = sourceTypeFromFile(file);

    if (sourceType === "pdf") {
      return readPdfWithPdfJs(file);
    }

    return readFileAsText(file);
  }

  function detectDocumentFlags(text, sourceType, cleanerReport) {
    const clean = safeString(text);
    const lines = clean.split(/\n/);
    const tableRows = cleanerReport && Array.isArray(cleanerReport.tableRows)
      ? cleanerReport.tableRows.length
      : 0;

    const flags = {
      isLongDocument: clean.length >= LONG_DOCUMENT_CHARS,
      isVeryLongDocument: clean.length >= VERY_LONG_DOCUMENT_CHARS,
      hasTables: tableRows > 0 || lines.some((line) => /\S\s{3,}\S/.test(line) || line.includes("|")),
      isOCR: sourceType === "ocr" || /\bOCR\b|testo\s+estratto\s+da\s+immagine/i.test(clean),
      probablyCorrupted: Boolean(cleanerReport && cleanerReport.corruption && cleanerReport.corruption.isProbablyCorrupted),
      tooShort: clean.trim().length < 40
    };

    return flags;
  }

  function makeStats(text) {
    const clean = safeString(text);
    const words = clean.split(/\s+/).filter(Boolean);
    const lines = clean.split(/\n/).filter((line) => line.trim());
    const sentences = clean.split(/[.!?]+/).filter((sentence) => sentence.trim().length > 8);

    return {
      chars: clean.length,
      words: words.length,
      lines: lines.length,
      sentences: sentences.length
    };
  }

  function buildDocumentInput(params) {
    const input = Object.assign({
      rawText: "",
      title: "Documento utente",
      sourceType: "manuale",
      origin: "utente",
      file: null,
      status: "loaded",
      warnings: [],
      errors: []
    }, params || {});

    const rawText = safeString(input.rawText);
    const cleaner = window.RagTextCleanerOCRV1;
    const cleaned = cleaner && cleaner.cleanText
      ? cleaner.cleanText(rawText)
      : { text: rawText.trim(), report: { version: "no_cleaner", tableRows: [], corruption: null } };

    const sourceType = input.sourceType || (input.file ? sourceTypeFromFile(input.file) : "manuale");
    const title = normalizeText(input.title || (input.file && input.file.name) || "Documento utente");
    const createdAt = nowIso();
    const flags = detectDocumentFlags(cleaned.text, sourceType, cleaned.report);
    const stats = makeStats(cleaned.text);

    const warnings = Array.from(new Set([
      ...(input.warnings || []),
      ...(flags.tooShort ? ["testo_troppo_corto"] : []),
      ...(flags.isLongDocument ? ["documento_lungo"] : []),
      ...(flags.isVeryLongDocument ? ["documento_molto_lungo"] : []),
      ...(flags.hasTables ? ["contiene_tabelle"] : []),
      ...(flags.probablyCorrupted ? ["testo_probabilmente_corrotto"] : [])
    ]));

    return {
      id: `doc_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
      version: VERSION,
      title,
      slug: slugify(title),
      source: {
        type: sourceType,
        origin: input.origin || "utente",
        fileName: input.file ? input.file.name : null,
        fileSize: input.file ? input.file.size : null,
        fileType: input.file ? input.file.type : null,
        extension: input.file ? extensionFromName(input.file.name) : null
      },
      reading: {
        status: input.status || "loaded",
        startedAt: input.startedAt || createdAt,
        completedAt: createdAt,
        errors: input.errors || [],
        warnings
      },
      text: {
        original: rawText,
        clean: cleaned.text,
        preview: cleaned.text.slice(0, 500)
      },
      metadata: {
        createdAt,
        stats,
        flags,
        cleanerReport: cleaned.report
      }
    };
  }

  async function fromFile(file) {
    const startedAt = nowIso();
    const sourceType = sourceTypeFromFile(file);

    try {
      const rawText = await extractTextFromFile(file);
      return buildDocumentInput({
        rawText,
        title: file.name,
        sourceType,
        origin: "file_caricato_utente",
        file,
        status: "loaded",
        startedAt
      });
    } catch (error) {
      return buildDocumentInput({
        rawText: "",
        title: file && file.name ? file.name : "Documento non letto",
        sourceType,
        origin: "file_caricato_utente",
        file,
        status: "error",
        startedAt,
        errors: [error && error.message ? error.message : String(error)]
      });
    }
  }

  function fromText(text, title, sourceType) {
    return buildDocumentInput({
      rawText: text,
      title: title || "Testo incollato dall'utente",
      sourceType: sourceType || "manuale",
      origin: "testo_incollato_utente",
      status: "loaded"
    });
  }

  function fromOCRText(text, title) {
    return buildDocumentInput({
      rawText: text,
      title: title || "Testo OCR utente",
      sourceType: "ocr",
      origin: "ocr_utente",
      status: "loaded"
    });
  }

  function getReadableText(documentInput) {
    return documentInput && documentInput.text ? documentInput.text.clean || documentInput.text.original || "" : "";
  }

  function bindFileInputToTextArea(options) {
    const settings = Object.assign({
      fileInput: null,
      textArea: null,
      statusEl: null,
      onDocument: null
    }, options || {});

    const fileInput = typeof settings.fileInput === "string" ? document.querySelector(settings.fileInput) : settings.fileInput;
    const textArea = typeof settings.textArea === "string" ? document.querySelector(settings.textArea) : settings.textArea;
    const statusEl = typeof settings.statusEl === "string" ? document.querySelector(settings.statusEl) : settings.statusEl;

    if (!fileInput) throw new Error("Manca fileInput per bindFileInputToTextArea.");

    fileInput.addEventListener("change", async () => {
      const file = fileInput.files && fileInput.files[0];
      if (!file) return;

      if (statusEl) statusEl.textContent = `Lettura documento: ${file.name}...`;
      const doc = await fromFile(file);

      if (textArea && doc.reading.status === "loaded") {
        textArea.value = getReadableText(doc);
      }

      if (statusEl) {
        if (doc.reading.status === "loaded") {
          statusEl.textContent = `Documento caricato: ${doc.title} - ${doc.metadata.stats.words} parole.`;
        } else {
          statusEl.textContent = `Errore lettura documento: ${doc.reading.errors.join("; ")}`;
        }
      }

      if (typeof settings.onDocument === "function") {
        settings.onDocument(doc);
      }
    });
  }

  window.RagDocumentInputUnicoV1 = {
    VERSION,
    buildDocumentInput,
    fromFile,
    fromText,
    fromOCRText,
    getReadableText,
    bindFileInputToTextArea,
    detectDocumentFlags,
    makeStats
  };
})();
