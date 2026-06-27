(function () {
  "use strict";

  const MIN_TEXT_CHARS = 10;

  function normalizeText(value) {
    return String(value || "")
      .replace(/\u00A0/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function collectVisibleUserText() {
    const parts = [];

    document
      .querySelectorAll("textarea, [contenteditable='true']")
      .forEach((el) => {
        const value = el.value || el.textContent || "";
        const clean = normalizeText(value);

        if (clean) {
          parts.push(clean);
        }
      });

    return normalizeText(parts.join("\n"));
  }

  function hasSelectedFile() {
    return Array.from(document.querySelectorAll("input[type='file']"))
      .some((input) => input.files && input.files.length > 0);
  }

  function clearInitialTextBoxesOnly() {
    document
      .querySelectorAll("textarea, [contenteditable='true']")
      .forEach((el) => {
        if ("value" in el) {
          el.value = "";
        } else {
          el.textContent = "";
        }
      });
  }

  function showInputError(message) {
    let box = document.getElementById("rag-input-reale-error");

    if (!box) {
      box = document.createElement("div");
      box.id = "rag-input-reale-error";
      box.style.margin = "16px 0";
      box.style.padding = "14px 16px";
      box.style.borderRadius = "12px";
      box.style.border = "2px solid #b91c1c";
      box.style.background = "#fee2e2";
      box.style.color = "#7f1d1d";
      box.style.fontWeight = "800";
      box.style.lineHeight = "1.45";

      const main =
        document.querySelector("main") ||
        document.querySelector(".container") ||
        document.body;

      main.prepend(box);
    }

    box.textContent = message;
    box.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  function clearInputError() {
    const box = document.getElementById("rag-input-reale-error");
    if (box) {
      box.remove();
    }
  }

  function requireRealInput(text, sourceLabel) {
    const clean = normalizeText(text);

    if (!clean || clean.length < MIN_TEXT_CHARS) {
      throw new Error("Nessun input reale trovato. Carica un file oppure incolla un testo prima di generare.");
    }

    return {
      text: clean,
      source: sourceLabel || "input_utente",
      valid: true,
      chars: clean.length,
      createdAt: new Date().toISOString()
    };
  }

  function isGenerationButton(button) {
    const label = normalizeText(
      button.innerText ||
      button.value ||
      button.getAttribute("aria-label") ||
      ""
    );

    return (
      /genera/i.test(label) ||
      /scarica\s+pdf/i.test(label) ||
      /crea\s+test/i.test(label)
    );
  }

  document.addEventListener("DOMContentLoaded", () => {
    /*
      BLOCCO 1:
      - pulisce solo i riquadri precaricati all'apertura pagina;
      - non vieta nessun contenuto;
      - non cancella il testo dopo il caricamento file;
      - non blocca documenti esempio se l'utente li carica volontariamente.
    */
    clearInitialTextBoxesOnly();

    document.addEventListener("change", function (event) {
      if (event.target && event.target.matches && event.target.matches("input[type='file']")) {
        clearInputError();
      }
    });

    document.addEventListener(
      "click",
      function blockOnlyEmptyGeneration(event) {
        const button = event.target.closest("button, a, input[type='button'], input[type='submit']");

        if (!button) return;
        if (!isGenerationButton(button)) return;

        const visibleText = collectVisibleUserText();
        const fileSelected = hasSelectedFile();

        if (!fileSelected && normalizeText(visibleText).length < MIN_TEXT_CHARS) {
          event.preventDefault();
          event.stopImmediatePropagation();

          showInputError(
            "Errore: nessun documento caricato o testo inserito. Carica un file oppure incolla un testo prima di generare."
          );
          return;
        }

        clearInputError();
      },
      true
    );
  });

  window.RagInputRealeGuard = {
    normalizeText,
    collectVisibleUserText,
    hasSelectedFile,
    requireRealInput,
    showInputError,
    clearInputError,
    clearInitialTextBoxesOnly
  };
})();
