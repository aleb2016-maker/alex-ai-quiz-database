(function () {
  'use strict';

  const GEN_RE = /genera\s+(riassunto|card|test|domande studio)|domande\s+studio/i;
  const TOP_RE = /carica\s+file|ripulisci\s+testo\s+ocr/i;
  const OCR_RE = /apri\s+motore\s+ocr|ocr\s+immagini|pdf\s*\/\s*fumetti|fumetti/i;
  const BAD_RE = /motore universale base collegato ai 4 bottoni/i;

  const OUTPUT_TITLE_RE =
    /^(riassunto generato|riassunto documento|card generate|card generate dal testo|test interattivo|test generato|domande studio|domande studio generate)/i;

  const HELP_RE =
    /flusso finale del motore documenti|7 temi riconosciuti|scarica materiale generato|sport e allenamento|curriculum vitae|documenti personali|documenti aziendali|storie e racconti|poesie|hobby e progetti/i;

  function t(el) {
    return String((el && (el.innerText || el.textContent)) || '')
      .replace(/\s+/g, ' ')
      .trim();
  }

  function visible(el) {
    if (!el) return false;
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 20 && r.height > 20;
  }

  function clickable() {
    return [...document.querySelectorAll(
      'button, a, [role="button"], .btn, .action-card, .generator-card'
    )];
  }

  function climbSmallBlock(el, maxText) {
    let block = el;

    for (let i = 0; i < 5 && block.parentElement && block.parentElement !== document.body; i++) {
      const parent = block.parentElement;
      const text = t(parent);

      if (text.length <= maxText) {
        block = parent;
      } else {
        break;
      }
    }

    return block;
  }

  function getTopAnchor() {
    const topButtons = clickable().filter(el => TOP_RE.test(t(el)));

    if (topButtons.length) {
      let node = topButtons[0];

      while (node && node !== document.body) {
        const count = [...node.querySelectorAll(
          'button, a, [role="button"], .btn, .action-card, .generator-card'
        )].filter(btn => TOP_RE.test(t(btn))).length;

        if (count >= 2) return node;

        node = node.parentElement;
      }

      return climbSmallBlock(topButtons[topButtons.length - 1], 1200);
    }

    const textarea = document.querySelector('textarea');
    return textarea ? climbSmallBlock(textarea, 2500) : document.body.firstElementChild;
  }

  function ensureZone(id, className) {
    let zone = document.getElementById(id);

    if (!zone) {
      zone = document.createElement('section');
      zone.id = id;
      zone.className = className || '';
    }

    return zone;
  }

  function placeBaseZones() {
    const anchor = getTopAnchor();

    const genZone = ensureZone('rag-generator-zone-rigido', 'rag-zone-rigida');
    const outputZone = ensureZone('rag-output-zone-rigido', 'rag-zone-rigida');
    const ocrZone = ensureZone('rag-ocr-zone-rigido', 'rag-zone-rigida');
    const helpZone = ensureZone('rag-help-zone-rigido', 'rag-zone-rigida');

    if (anchor && anchor !== document.body) {
      anchor.insertAdjacentElement('afterend', genZone);
    } else if (!genZone.parentElement) {
      document.body.prepend(genZone);
    }

    genZone.insertAdjacentElement('afterend', outputZone);
    outputZone.insertAdjacentElement('afterend', ocrZone);

    if (!helpZone.parentElement) {
      document.body.appendChild(helpZone);
    }

    if (!helpZone.querySelector('.rag-help-title-rigido')) {
      const h = document.createElement('h2');
      h.className = 'rag-help-title-rigido';
      h.textContent = 'Spiegazioni finali';
      helpZone.prepend(h);
    }

    return { genZone, outputZone, ocrZone, helpZone };
  }

  function moveGeneratorButtons() {
    const { genZone } = placeBaseZones();

    let grid = document.getElementById('rag-generator-grid-rigido');

    if (!grid) {
      grid = document.createElement('div');
      grid.id = 'rag-generator-grid-rigido';
      genZone.appendChild(grid);
    }

    const genButtons = clickable()
      .filter(el => GEN_RE.test(t(el)))
      .filter(el => !grid.contains(el));

    genButtons.forEach(btn => {
      const card = climbSmallBlock(btn, 500);
      grid.appendChild(card);
    });
  }

  function removeBadBadge() {
    [...document.querySelectorAll('p, span, div, section, article')]
      .filter(el => BAD_RE.test(t(el)))
      .forEach(el => {
        if (t(el).length < 160) el.remove();
      });
  }

  function moveOcrButton() {
    const { ocrZone } = placeBaseZones();

    const btn = clickable().find(el => OCR_RE.test(t(el)));
    if (!btn) return;

    const block = climbSmallBlock(btn, 900);

    if (!ocrZone.contains(block)) {
      ocrZone.appendChild(block);
    }
  }

  function blockFromHeading(h) {
    let node = h;

    for (let i = 0; i < 8 && node && node !== document.body; i++) {
      const text = t(node);
      const r = node.getBoundingClientRect();

      if (
        visible(node) &&
        text.length > 50 &&
        r.width > 240 &&
        r.height > 60 &&
        node.querySelector('h1,h2,h3,h4,h5,h6')
      ) {
        return node;
      }

      node = node.parentElement;
    }

    return null;
  }

  function findGeneratedOutput() {
    const existing = document.querySelector('.rag-output-attuale-rigido');

    if (existing && visible(existing) && t(existing).length > 60) {
      return existing;
    }

    const headings = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')]
      .filter(h => visible(h))
      .filter(h => OUTPUT_TITLE_RE.test(t(h)));

    const blocks = headings
      .map(blockFromHeading)
      .filter(Boolean)
      .filter(el => !HELP_RE.test(t(el)));

    return blocks.length ? blocks[blocks.length - 1] : null;
  }

  function addPdfButton(output) {
    if (!output) return;

    output.querySelectorAll('.rag-pdf-rigido-toolbar').forEach(el => el.remove());

    const toolbar = document.createElement('div');
    toolbar.className = 'rag-pdf-rigido-toolbar';

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'rag-pdf-rigido-btn';
    btn.textContent = 'Scarica PDF di questo risultato';

    btn.addEventListener('click', function (ev) {
      ev.preventDefault();
      ev.stopImmediatePropagation();
      printOnly(output);
    }, true);

    toolbar.appendChild(btn);
    output.insertBefore(toolbar, output.firstChild);
  }

  function moveOutput() {
    const { outputZone } = placeBaseZones();
    const output = findGeneratedOutput();

    if (!output) {
      outputZone.innerHTML = '';
      return null;
    }

    document.querySelectorAll('.rag-output-attuale-rigido').forEach(el => {
      el.classList.remove('rag-output-attuale-rigido');
    });

    output.classList.add('rag-output-attuale-rigido');

    if (!outputZone.contains(output)) {
      outputZone.innerHTML = '';
      outputZone.appendChild(output);
    }

    addPdfButton(output);

    return output;
  }

  function moveHelpToBottom() {
    const { helpZone } = placeBaseZones();

    const blocks = [];

    [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')]
      .filter(h => visible(h))
      .filter(h => HELP_RE.test(t(h)))
      .map(blockFromHeading)
      .filter(Boolean)
      .forEach(b => blocks.push(b));

    [...document.querySelectorAll('section, article, div')]
      .filter(el => visible(el))
      .filter(el => HELP_RE.test(t(el)))
      .filter(el => t(el).length > 150)
      .forEach(el => blocks.push(el));

    blocks
      .filter((el, i, arr) => arr.indexOf(el) === i)
      .filter(el => !helpZone.contains(el))
      .filter(el => !el.closest('#rag-generator-zone-rigido'))
      .filter(el => !el.closest('#rag-output-zone-rigido'))
      .filter(el => !el.closest('#rag-ocr-zone-rigido'))
      .forEach(el => {
        helpZone.appendChild(el);
      });
  }

  function printOnly(output) {
    document.querySelectorAll('.rag-print-target-rigido').forEach(el => {
      el.classList.remove('rag-print-target-rigido');
    });

    output.classList.add('rag-print-target-rigido');
    document.body.classList.add('rag-print-mode-rigido');

    const cleanup = function () {
      document.body.classList.remove('rag-print-mode-rigido');
      output.classList.remove('rag-print-target-rigido');
      window.removeEventListener('afterprint', cleanup);
    };

    window.addEventListener('afterprint', cleanup);

    setTimeout(function () {
      window.print();
      setTimeout(cleanup, 1400);
    }, 120);
  }

  function bindGenerators() {
    clickable().forEach(btn => {
      if (!GEN_RE.test(t(btn))) return;
      if (btn.dataset.ragRigidoBound === '1') return;

      btn.dataset.ragRigidoBound = '1';

      btn.addEventListener('click', function () {
        setTimeout(() => fix(true), 180);
        setTimeout(() => fix(true), 650);
        setTimeout(() => fix(true), 1300);
      }, false);
    });
  }

  function addStyle() {
    if (document.getElementById('rag-rigido-style')) return;

    const style = document.createElement('style');
    style.id = 'rag-rigido-style';

    style.textContent = `
      #rag-generator-zone-rigido,
      #rag-output-zone-rigido,
      #rag-ocr-zone-rigido,
      #rag-help-zone-rigido {
        max-width: 1180px !important;
        margin-left: auto !important;
        margin-right: auto !important;
      }

      #rag-generator-zone-rigido {
        margin-top: 24px !important;
        margin-bottom: 18px !important;
      }

      #rag-generator-grid-rigido {
        display: grid !important;
        grid-template-columns: repeat(2, minmax(260px, 1fr)) !important;
        gap: 22px !important;
      }

      #rag-generator-grid-rigido > * {
        min-height: 135px !important;
      }

      #rag-output-zone-rigido {
        margin-top: 16px !important;
        margin-bottom: 20px !important;
      }

      #rag-output-zone-rigido:empty {
        display: none !important;
      }

      #rag-ocr-zone-rigido {
        margin-top: 18px !important;
        margin-bottom: 28px !important;
      }

      #rag-ocr-zone-rigido:empty {
        display: none !important;
      }

      #rag-help-zone-rigido {
        margin-top: 44px !important;
        margin-bottom: 34px !important;
        padding: 16px !important;
        border-radius: 22px !important;
        border: 1px solid rgba(255,255,255,.14) !important;
        background: rgba(255,255,255,.035) !important;
      }

      #rag-help-zone-rigido .rag-help-title-rigido {
        margin: 0 0 12px !important;
        font-size: 24px !important;
        font-weight: 950 !important;
      }

      #rag-help-zone-rigido section,
      #rag-help-zone-rigido article,
      #rag-help-zone-rigido div {
        margin-top: 10px !important;
        margin-bottom: 10px !important;
        padding: 12px !important;
        border-radius: 16px !important;
      }

      #rag-help-zone-rigido h1,
      #rag-help-zone-rigido h2,
      #rag-help-zone-rigido h3 {
        font-size: 19px !important;
        margin: 0 0 6px !important;
      }

      #rag-help-zone-rigido p,
      #rag-help-zone-rigido li {
        font-size: 14px !important;
        line-height: 1.3 !important;
      }

      #rag-help-zone-rigido ul {
        margin-top: 4px !important;
        margin-bottom: 4px !important;
      }

      .rag-pdf-rigido-toolbar {
        display: flex !important;
        justify-content: flex-end !important;
        margin: 0 0 16px !important;
      }

      .rag-pdf-rigido-btn {
        border: 0 !important;
        border-radius: 999px !important;
        padding: 13px 20px !important;
        font-size: 17px !important;
        font-weight: 950 !important;
        color: #fff !important;
        cursor: pointer !important;
        background: linear-gradient(135deg, #cb124d, #a42ee8) !important;
        box-shadow: 0 14px 30px rgba(0,0,0,.28) !important;
      }

      @media print {
        @page {
          size: A4;
          margin: 10mm;
        }

        html,
        body {
          background: white !important;
          margin: 0 !important;
          padding: 0 !important;
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
        }

        body.rag-print-mode-rigido * {
          visibility: hidden !important;
        }

        body.rag-print-mode-rigido .rag-print-target-rigido,
        body.rag-print-mode-rigido .rag-print-target-rigido * {
          visibility: visible !important;
        }

        body.rag-print-mode-rigido .rag-print-target-rigido {
          position: absolute !important;
          left: 0 !important;
          top: 0 !important;
          width: 100% !important;
          max-width: none !important;
          margin: 0 !important;
          padding: 0 !important;
          box-shadow: none !important;
        }

        body.rag-print-mode-rigido .rag-pdf-rigido-toolbar,
        body.rag-print-mode-rigido button {
          display: none !important;
        }

        body.rag-print-mode-rigido article,
        body.rag-print-mode-rigido section,
        body.rag-print-mode-rigido [class*="card"] {
          break-inside: avoid !important;
          page-break-inside: avoid !important;
        }
      }

      @media (max-width: 800px) {
        #rag-generator-grid-rigido {
          grid-template-columns: 1fr !important;
        }
      }
    `;

    document.head.appendChild(style);
  }

  function fix(scroll) {
    addStyle();
    placeBaseZones();
    removeBadBadge();
    moveGeneratorButtons();
    moveOutput();
    moveOcrButton();
    moveHelpToBottom();
    bindGenerators();

    const output = document.querySelector('.rag-output-attuale-rigido');

    if (scroll && output) {
      output.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  }

  function start() {
    fix(false);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }

  window.addEventListener('load', start);
  setTimeout(start, 500);
  setTimeout(start, 1200);

  let timer = null;

  const observer = new MutationObserver(function () {
    clearTimeout(timer);
    timer = setTimeout(function () {
      fix(false);
    }, 120);
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
})();
