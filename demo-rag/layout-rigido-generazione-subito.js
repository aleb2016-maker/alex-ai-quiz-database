(function () {
  const ACTION_TEXTS = [
    "carica file pdf",
    "carica file txt",
    "carica file pdf / txt",
    "ripulisci testo ocr",
    "genera riassunto",
    "genera card",
    "genera test",
    "genera domande studio",
    "apri motore ocr"
  ];

  const DOWNLOAD_TEXTS = [
    "scarica materiale generato",
    "scarica txt",
    "scarica html",
    "scarica pdf",
    "scarica json"
  ];

  const EXPLANATION_TEXTS = [
    "flusso finale del motore documenti",
    "testo incollato",
    "txt e pdf con testo",
    "immagini, tabelle e fumetti",
    "output finale",
    "7 temi riconosciuti",
    "sport e allenamento",
    "curriculum vitae",
    "documenti personali",
    "documenti aziendali",
    "storie e racconti",
    "poesie",
    "hobby e progetti",
    "spiegazioni finali"
  ];

  const OUTPUT_SELECTORS = [
    "#output",
    "#outputs",
    "#result",
    "#results",
    "#risultato",
    "#risultati",
    "#summaryOutput",
    "#cardsOutput",
    "#testOutput",
    "#studyOutput",
    "#domandeStudioOutput",
    ".output",
    ".outputs",
    ".result",
    ".results",
    ".generated-output",
    ".generated-results",
    ".area-output",
    ".output-area",
    ".result-area"
  ];

  function norm(value) {
    return (value || "")
      .toLowerCase()
      .replace(/\s+/g, " ")
      .trim();
  }

  function textOf(element) {
    return norm(element.innerText || element.textContent || "");
  }

  function containsAny(element, list) {
    const text = textOf(element);
    return list.some(item => text.includes(item));
  }

  function getMainRoot() {
    return (
      document.querySelector("main") ||
      document.querySelector(".container") ||
      document.querySelector(".app") ||
      document.body
    );
  }

  function createBlock(id) {
    let block = document.getElementById(id);

    if (!block) {
      block = document.createElement("section");
      block.id = id;
    }

    return block;
  }

  function usefulParent(element) {
    const parent = element.closest(
      "section, article, .section, .panel, .card, .box, .tool-card, .action-card"
    );

    if (!parent) return element;

    const parentText = textOf(parent);
    const elementText = textOf(element);

    if (parentText.length <= Math.max(elementText.length + 180, 260)) {
      return parent;
    }

    return element;
  }

  function findInteractiveByTexts(texts) {
    const items = Array.from(
      document.querySelectorAll("button, a, label, [role='button']")
    );

    const found = [];

    for (const item of items) {
      if (
        item.closest("#azioni-generazione-rigide") ||
        item.closest("#download-subito-sotto-input")
      ) {
        continue;
      }

      if (containsAny(item, texts)) {
        const parent = usefulParent(item);

        if (!found.includes(parent)) {
          found.push(parent);
        }
      }
    }

    return found;
  }

  function findInputPanel() {
    const textarea = document.querySelector("textarea");

    if (textarea) {
      return (
        textarea.closest("section, article, .section, .panel, .card, .box") ||
        textarea
      );
    }

    const candidates = Array.from(
      document.querySelectorAll("section, article, .section, .panel, .card, .box")
    );

    return candidates.find(candidate => {
      const text = textOf(candidate);
      return (
        text.includes("incolla un documento") ||
        text.includes("incolla testo") ||
        text.includes("carica un txt")
      );
    });
  }

  function moveDownloads(root) {
    const downloadBlock = createBlock("download-subito-sotto-input");
    const inputPanel = findInputPanel();

    if (inputPanel && inputPanel.parentNode) {
      inputPanel.insertAdjacentElement("afterend", downloadBlock);
    } else if (!downloadBlock.parentNode) {
      root.prepend(downloadBlock);
    }

    const candidates = Array.from(
      document.querySelectorAll("section, article, .section, .panel, .card, .box")
    );

    for (const candidate of candidates) {
      if (
        candidate === downloadBlock ||
        candidate.closest("#download-subito-sotto-input") ||
        candidate.closest("#azioni-generazione-rigide") ||
        candidate.closest("#spiegazioni-finali-compatte")
      ) {
        continue;
      }

      if (containsAny(candidate, DOWNLOAD_TEXTS)) {
        downloadBlock.appendChild(candidate);
      }
    }
  }

  function moveActions(root) {
    const actionBlock = createBlock("azioni-generazione-rigide");
    const downloadBlock = document.getElementById("download-subito-sotto-input");
    const inputPanel = findInputPanel();

    if (downloadBlock && downloadBlock.parentNode) {
      downloadBlock.insertAdjacentElement("afterend", actionBlock);
    } else if (inputPanel && inputPanel.parentNode) {
      inputPanel.insertAdjacentElement("afterend", actionBlock);
    } else if (!actionBlock.parentNode) {
      root.prepend(actionBlock);
    }

    const actions = findInteractiveByTexts(ACTION_TEXTS);

    for (const action of actions) {
      actionBlock.appendChild(action);
    }
  }

  function moveOutputs() {
    const actionBlock = document.getElementById("azioni-generazione-rigide");
    const outputBlock = createBlock("risultati-generati-subito");

    if (actionBlock && actionBlock.parentNode) {
      actionBlock.insertAdjacentElement("afterend", outputBlock);
    }

    for (const selector of OUTPUT_SELECTORS) {
      document.querySelectorAll(selector).forEach(element => {
        if (
          element === outputBlock ||
          element.closest("#risultati-generati-subito") ||
          element.closest("#download-subito-sotto-input") ||
          element.closest("#azioni-generazione-rigide") ||
          element.closest("#spiegazioni-finali-compatte")
        ) {
          return;
        }

        outputBlock.appendChild(element);
      });
    }
  }

  function moveExplanations(root) {
    const explanationBlock = createBlock("spiegazioni-finali-compatte");

    if (!explanationBlock.parentNode) {
      root.appendChild(explanationBlock);
    }

    const candidates = Array.from(
      document.querySelectorAll("section, article, .section, .panel, .card, .box")
    );

    for (const candidate of candidates) {
      if (
        candidate === explanationBlock ||
        candidate.closest("#spiegazioni-finali-compatte") ||
        candidate.closest("#download-subito-sotto-input") ||
        candidate.closest("#azioni-generazione-rigide") ||
        candidate.closest("#risultati-generati-subito")
      ) {
        continue;
      }

      if (containsAny(candidate, EXPLANATION_TEXTS)) {
        explanationBlock.appendChild(candidate);
      }
    }

    root.appendChild(explanationBlock);
  }

  function hideUselessLabels() {
    document.querySelectorAll("body *").forEach(element => {
      const text = textOf(element);

      if (
        text.includes("motore universale collegato") &&
        text.length < 90
      ) {
        element.classList.add("layout-rigido-nascosto");
      }
    });
  }

  function applyLayout() {
    const root = getMainRoot();

    moveDownloads(root);
    moveActions(root);
    moveOutputs();
    moveExplanations(root);
    hideUselessLabels();
  }

  let locked = false;

  function safeApply() {
    if (locked) return;

    locked = true;

    requestAnimationFrame(() => {
      applyLayout();
      locked = false;
    });
  }

  document.addEventListener("DOMContentLoaded", safeApply);
  window.addEventListener("load", safeApply);
  document.addEventListener("click", () => {
    setTimeout(safeApply, 80);
    setTimeout(safeApply, 350);
  });

  const observer = new MutationObserver(() => safeApply());

  observer.observe(document.documentElement, {
    childList: true,
    subtree: true
  });
})();
