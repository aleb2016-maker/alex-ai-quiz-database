(function () {
  "use strict";

  const VERSION = "rag-text-cleaner-ocr-v1";

  function asText(value) {
    return String(value == null ? "" : value);
  }

  function countMatches(text, pattern) {
    const match = asText(text).match(pattern);
    return match ? match.length : 0;
  }

  function normalizeUnicode(text) {
    return asText(text)
      .normalize("NFKC")
      .replace(/\u00A0/g, " ")
      .replace(/[“”]/g, '"')
      .replace(/[‘’]/g, "'")
      .replace(/[‐‑‒–—]/g, "-")
      .replace(/[•●▪◦]/g, "- ");
  }

  function removeControlNoise(text) {
    return asText(text)
      .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, "")
      .replace(/\r\n?/g, "\n");
  }

  function fixHyphenatedLineBreaks(text) {
    return asText(text).replace(/([A-Za-zÀ-ÖØ-öø-ÿ])[-]\n([a-zà-öø-ÿ])/g, "$1$2");
  }

  function isListOrTitleLine(line) {
    const clean = line.trim();
    if (!clean) return true;
    if (/^[-*•]\s+/.test(clean)) return true;
    if (/^\d+[.)]\s+/.test(clean)) return true;
    if (/^[A-ZÀ-ÖØ-Þ0-9 ,.:'’'"()/-]{5,}$/.test(clean) && clean.length < 90) return true;
    if (/[:;]$/.test(clean)) return true;
    return false;
  }

  function shouldJoinLines(previous, current) {
    const a = previous.trim();
    const b = current.trim();
    if (!a || !b) return false;
    if (isListOrTitleLine(a)) return false;
    if (/^[A-ZÀ-ÖØ-Þ]/.test(b) && /[.!?]$/.test(a)) return false;
    if (/^[\-|*•\d]/.test(b)) return false;
    if (/[.!?]$/.test(a)) return false;
    if (a.length < 28) return false;
    return true;
  }

  function joinBrokenLines(text) {
    const rawLines = asText(text).split("\n");
    const lines = [];

    for (const raw of rawLines) {
      const line = raw.replace(/[ \t]+$/g, "");
      if (!lines.length) {
        lines.push(line);
        continue;
      }

      const last = lines[lines.length - 1];
      if (shouldJoinLines(last, line)) {
        lines[lines.length - 1] = `${last.trim()} ${line.trim()}`;
      } else {
        lines.push(line);
      }
    }

    return lines.join("\n");
  }

  function normalizeSpaces(text) {
    return asText(text)
      .replace(/[\t ]+/g, " ")
      .replace(/ ?\n ?/g, "\n")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
  }

  function cleanTableLine(line) {
    return line
      .replace(/\s*[|│]\s*/g, " | ")
      .replace(/\s{3,}/g, " | ")
      .replace(/\|\s*\|/g, "|")
      .trim();
  }

  function detectTableLines(text) {
    const rows = [];
    const lines = asText(text).split("\n");

    lines.forEach((line, index) => {
      const clean = line.trim();
      if (!clean) return;

      const pipeCells = clean.split("|").filter((cell) => cell.trim()).length;
      const manySpaces = /\S\s{3,}\S/.test(clean);
      const numberColumns = countMatches(clean, /\b\d+(?:[,.]\d+)?\b/g) >= 2;

      if (pipeCells >= 2 || (manySpaces && numberColumns)) {
        rows.push({ index, raw: line, normalized: cleanTableLine(line) });
      }
    });

    return rows;
  }

  function simplifyTables(text) {
    const tableRows = detectTableLines(text);
    if (!tableRows.length) return { text, tableRows };

    const byIndex = new Map(tableRows.map((row) => [row.index, row.normalized]));
    const lines = asText(text).split("\n").map((line, index) => byIndex.get(index) || line);
    return { text: lines.join("\n"), tableRows };
  }

  function detectCorruption(text) {
    const clean = asText(text);
    const length = clean.length;
    const replacementChars = countMatches(clean, /�/g);
    const strangeRuns = countMatches(clean, /[^\sA-Za-zÀ-ÖØ-öø-ÿ0-9.,;:!?()\[\]{}'"/\\%€$@#&+*=<>|\-\n]{2,}/g);
    const words = clean.split(/\s+/).filter(Boolean);
    const shortWords = words.filter((word) => word.length <= 1).length;

    const replacementRatio = length ? replacementChars / length : 0;
    const shortWordRatio = words.length ? shortWords / words.length : 0;

    const warnings = [];
    if (length < 40) warnings.push("testo_troppo_corto");
    if (replacementRatio > 0.01) warnings.push("caratteri_non_decodificati");
    if (strangeRuns > 6) warnings.push("rumore_ocr_probabile");
    if (words.length > 20 && shortWordRatio > 0.38) warnings.push("molte_parole_spezzate");

    return {
      length,
      words: words.length,
      replacementChars,
      strangeRuns,
      shortWordRatio,
      warnings,
      isProbablyCorrupted: warnings.length >= 2
    };
  }

  function cleanText(inputText, options) {
    const settings = Object.assign({ joinLines: true, simplifyTables: true }, options || {});
    const original = asText(inputText);

    const report = {
      version: VERSION,
      originalChars: original.length,
      steps: [],
      tableRows: [],
      corruption: null
    };

    let text = original;

    text = removeControlNoise(text);
    report.steps.push("remove_control_noise");

    text = normalizeUnicode(text);
    report.steps.push("normalize_unicode");

    text = fixHyphenatedLineBreaks(text);
    report.steps.push("fix_hyphenated_line_breaks");

    if (settings.joinLines) {
      text = joinBrokenLines(text);
      report.steps.push("join_broken_lines");
    }

    if (settings.simplifyTables) {
      const tableResult = simplifyTables(text);
      text = tableResult.text;
      report.tableRows = tableResult.tableRows;
      report.steps.push("simplify_tables");
    }

    text = normalizeSpaces(text);
    report.steps.push("normalize_spaces");

    report.cleanedChars = text.length;
    report.removedChars = Math.max(0, original.length - text.length);
    report.corruption = detectCorruption(text);

    return {
      text,
      report
    };
  }

  window.RagTextCleanerOCRV1 = {
    VERSION,
    cleanText,
    normalizeUnicode,
    joinBrokenLines,
    detectTableLines,
    detectCorruption
  };
})();
