(function (root, factory) {
  const api = factory();

  if (typeof module === "object" && module.exports) {
    module.exports = api;
  }

  root.RagLargeDocumentManagerV1 = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const DEFAULT_OPTIONS = {
    maxCharsPerChunk: 4000,
    chunkOverlap: 400,
    maxPagesPerBatch: 5,
    maxChunksPerBatch: 8,
    maxCharsPerBatch: 28000
  };

  function normalizeText(value) {
    return String(value || "")
      .replace(/\r/g, "\n")
      .replace(/[ \t]+/g, " ")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
  }

  function parsePageSelection(selection, totalPages) {
    const input = String(selection || "").trim();

    if (!input || input.toLowerCase() === "tutto" || input.toLowerCase() === "all") {
      return Array.from({ length: totalPages }, (_, index) => index + 1);
    }

    const selected = new Set();

    input.split(",").forEach(function (part) {
      const clean = part.trim();

      if (!clean) return;

      if (clean.includes("-")) {
        const pieces = clean.split("-").map(function (v) {
          return parseInt(v.trim(), 10);
        });

        const start = Math.max(1, Math.min(pieces[0], totalPages));
        const end = Math.max(1, Math.min(pieces[1], totalPages));

        for (let n = Math.min(start, end); n <= Math.max(start, end); n += 1) {
          selected.add(n);
        }
      } else {
        const n = parseInt(clean, 10);
        if (Number.isFinite(n) && n >= 1 && n <= totalPages) {
          selected.add(n);
        }
      }
    });

    return Array.from(selected).sort(function (a, b) {
      return a - b;
    });
  }

  function splitTextToChunks(text, options) {
    const opts = Object.assign({}, DEFAULT_OPTIONS, options || {});
    const clean = normalizeText(text);

    if (!clean) return [];

    const chunks = [];
    let start = 0;

    while (start < clean.length) {
      let end = Math.min(start + opts.maxCharsPerChunk, clean.length);

      if (end < clean.length) {
        const softBreak = clean.lastIndexOf("\n\n", end);
        const sentenceBreak = clean.lastIndexOf(". ", end);

        if (softBreak > start + 1000) {
          end = softBreak;
        } else if (sentenceBreak > start + 1000) {
          end = sentenceBreak + 1;
        }
      }

      const piece = clean.slice(start, end).trim();

      if (piece) {
        chunks.push({
          index: chunks.length + 1,
          text: piece,
          chars: piece.length
        });
      }

      if (end >= clean.length) break;

      start = Math.max(0, end - opts.chunkOverlap);
    }

    return chunks;
  }

  function splitTxtMdIntoLogicalPages(text) {
    const raw = String(text || "").replace(/\r/g, "\n");
    const markerPattern = /^[ \t]*(?:---[ \t]*PAGINA[ \t]+(\d{1,4})[ \t]*---|#{1,2}[ \t]*Pagina[ \t]+(\d{1,4})(?:[ \t].*)?)[ \t]*$/gim;
    const markers = [];
    let match;

    while ((match = markerPattern.exec(raw)) !== null) {
      markers.push({
        page: parseInt(match[1] || match[2], 10),
        start: match.index,
        contentStart: markerPattern.lastIndex
      });
    }

    if (!markers.length) {
      const clean = normalizeText(raw);
      return [{
        page: 1,
        text: clean,
        chars: clean.length,
        status: clean ? "ok" : "empty",
        source: "txt-md"
      }];
    }

    return markers.map(function (marker, index) {
      const next = markers[index + 1];
      const sliceStart = marker.start;
      const sliceEnd = next ? next.start : raw.length;
      const clean = normalizeText(raw.slice(sliceStart, sliceEnd));

      return {
        page: marker.page,
        text: clean,
        chars: clean.length,
        status: clean ? "ok" : "empty",
        source: "txt-md-logical"
      };
    }).sort(function (a, b) {
      return a.page - b.page;
    });
  }

  function createPageChunks(pages, options) {
    const opts = Object.assign({}, DEFAULT_OPTIONS, options || {});
    const chunks = [];

    pages.forEach(function (page) {
      const pageChunks = splitTextToChunks(page.text, opts);

      pageChunks.forEach(function (chunk) {
        chunks.push({
          id: "p" + page.page + "-c" + chunk.index,
          pageStart: page.page,
          pageEnd: page.page,
          chunkIndexInPage: chunk.index,
          globalIndex: chunks.length + 1,
          chars: chunk.chars,
          text: chunk.text
        });
      });
    });

    return chunks;
  }

  function createBatches(chunks, options) {
    const opts = Object.assign({}, DEFAULT_OPTIONS, options || {});
    const batches = [];

    let current = [];
    let currentChars = 0;
    let currentPages = new Set();

    function flush() {
      if (!current.length) return;

      batches.push({
        index: batches.length + 1,
        chunks: current,
        chunkCount: current.length,
        chars: currentChars,
        pageStart: Math.min.apply(null, Array.from(currentPages)),
        pageEnd: Math.max.apply(null, Array.from(currentPages))
      });

      current = [];
      currentChars = 0;
      currentPages = new Set();
    }

    chunks.forEach(function (chunk) {
      const nextPages = new Set(currentPages);
      nextPages.add(chunk.pageStart);

      const wouldExceedChunks = current.length >= opts.maxChunksPerBatch;
      const wouldExceedChars = currentChars + chunk.chars > opts.maxCharsPerBatch;
      const wouldExceedPages = nextPages.size > opts.maxPagesPerBatch;

      if (current.length && (wouldExceedChunks || wouldExceedChars || wouldExceedPages)) {
        flush();
      }

      current.push(chunk);
      currentChars += chunk.chars;
      currentPages.add(chunk.pageStart);
    });

    flush();

    return batches;
  }

  async function extractTextFromTxtLike(file) {
    const raw = await file.text();
    return splitTxtMdIntoLogicalPages(raw);
  }

  async function extractTextFromPdf(file, options) {
    if (!root.pdfjsLib) {
      throw new Error("pdfjsLib non disponibile. Apri la pagina test con connessione o con PDF.js caricato.");
    }

    const opts = Object.assign({}, DEFAULT_OPTIONS, options || {});
    const data = await file.arrayBuffer();
    const pdf = await root.pdfjsLib.getDocument({ data: data }).promise;
    const selectedPages = parsePageSelection(opts.pageSelection || "tutto", pdf.numPages);

    const pages = [];

    for (let i = 0; i < selectedPages.length; i += 1) {
      const pageNumber = selectedPages[i];

      if (typeof opts.onProgress === "function") {
        opts.onProgress({
          stage: "extracting",
          current: i + 1,
          total: selectedPages.length,
          page: pageNumber,
          message: "Estrazione pagina " + pageNumber + "/" + pdf.numPages
        });
      }

      const page = await pdf.getPage(pageNumber);
      const content = await page.getTextContent();

      const text = normalizeText(
        content.items
          .map(function (item) {
            return item.str || "";
          })
          .join(" ")
      );

      pages.push({
        page: pageNumber,
        text: text,
        chars: text.length,
        status: text ? "ok" : "empty",
        source: "pdf"
      });

      await new Promise(function (resolve) {
        setTimeout(resolve, 0);
      });
    }

    return {
      fileName: file.name,
      fileSize: file.size,
      totalPages: pdf.numPages,
      selectedPages: selectedPages,
      pages: pages
    };
  }

  async function analyzeFile(file, options) {
    const opts = Object.assign({}, DEFAULT_OPTIONS, options || {});
    const name = file && file.name ? file.name : "";
    const lower = name.toLowerCase();

    let extraction;

    if (lower.endsWith(".pdf")) {
      extraction = await extractTextFromPdf(file, opts);
    } else if (lower.endsWith(".txt") || lower.endsWith(".md")) {
      if (typeof opts.onProgress === "function") {
        opts.onProgress({
          stage: "reading",
          current: 1,
          total: 3,
          page: null,
          message: "Lettura file TXT/MD..."
        });
      }

      const pages = await extractTextFromTxtLike(file);

      if (typeof opts.onProgress === "function") {
        opts.onProgress({
          stage: "splitting",
          current: 2,
          total: 3,
          page: null,
          message: "Pagine logiche riconosciute: " + pages.length
        });
      }

      const selectedPages = parsePageSelection(opts.pageSelection || "tutto", pages.length);
      const selectedSet = new Set(selectedPages);
      const selectedLogicalPages = pages.filter(function (page, index) {
        return selectedSet.has(index + 1);
      });

      extraction = {
        fileName: name,
        fileSize: file.size,
        totalPages: pages.length,
        selectedPages: selectedPages,
        pages: selectedLogicalPages
      };
    } else {
      throw new Error("Formato non supportato in V1. Usa PDF, TXT o MD.");
    }

    const chunks = createPageChunks(extraction.pages, opts);
    const batches = createBatches(chunks, opts);

    const totalChars = extraction.pages.reduce(function (sum, page) {
      return sum + page.chars;
    }, 0);

    return {
      version: "rag-large-document-manager-v1",
      fileName: extraction.fileName,
      fileSize: extraction.fileSize,
      totalPages: extraction.totalPages,
      selectedPages: extraction.selectedPages,
      extractedPages: extraction.pages.length,
      totalChars: totalChars,
      emptyPages: extraction.pages.filter(function (p) { return !p.text; }).map(function (p) { return p.page; }),
      pages: extraction.pages,
      chunks: chunks,
      batches: batches,
      options: opts
    };
  }

  function estimateCapacity(report) {
    const pages = report.extractedPages || 0;
    const chars = report.totalChars || 0;
    const chunks = report.chunks ? report.chunks.length : 0;
    const batches = report.batches ? report.batches.length : 0;

    let level = "ok";
    let note = "Documento gestibile in modalità progressiva.";

    if (pages > 100 || chars > 350000 || chunks > 120) {
      level = "large";
      note = "Documento lungo: va elaborato a batch e con output parziali.";
    }

    if (pages > 250 || chars > 800000 || chunks > 250) {
      level = "very-large";
      note = "Documento molto grande: usare selezione pagine, batch piccoli e salvataggio progressivo.";
    }

    return {
      level: level,
      note: note,
      pages: pages,
      chars: chars,
      chunks: chunks,
      batches: batches
    };
  }

  return {
    DEFAULT_OPTIONS: DEFAULT_OPTIONS,
    normalizeText: normalizeText,
    parsePageSelection: parsePageSelection,
    splitTxtMdIntoLogicalPages: splitTxtMdIntoLogicalPages,
    splitTextToChunks: splitTextToChunks,
    createPageChunks: createPageChunks,
    createBatches: createBatches,
    analyzeFile: analyzeFile,
    estimateCapacity: estimateCapacity
  };
});
