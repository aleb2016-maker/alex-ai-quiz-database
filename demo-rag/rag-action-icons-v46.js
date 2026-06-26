(function () {
  "use strict";

  const LABELS = {
    btnRiassunto: "Genera riassunto",
    btnCard: "Genera card",
    btnTest: "Genera test",
    btnStudio: "Genera domande studio",
    btnDomandeStudio: "Genera domande studio"
  };

  function byId(id) {
    return document.getElementById(id);
  }

  function iconRiassunto() {
    return `
      <svg class="rag-action-svg" viewBox="0 0 160 160" aria-hidden="true">
        <defs>
          <linearGradient id="sumPaperV46c" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0%" stop-color="#ffffff"/>
            <stop offset="100%" stop-color="#e0ecff"/>
          </linearGradient>
          <linearGradient id="sumFoldV46c" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0%" stop-color="#9ec5ff"/>
            <stop offset="100%" stop-color="#4978ff"/>
          </linearGradient>
          <linearGradient id="sumAccentV46c" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0%" stop-color="#ffd76a"/>
            <stop offset="100%" stop-color="#ff7a45"/>
          </linearGradient>
        </defs>
        <g filter="drop-shadow(0 12px 16px rgba(0,0,0,.30))">
          <rect x="36" y="18" width="68" height="98" rx="14" fill="url(#sumPaperV46c)"/>
          <path d="M88 18 L104 34 L91 34 Q88 34 88 31 Z" fill="url(#sumFoldV46c)"/>
          <path d="M49 47 H87" stroke="#2763ff" stroke-width="7" stroke-linecap="round"/>
          <path d="M49 63 H90" stroke="#3b82f6" stroke-width="7" stroke-linecap="round"/>
          <path d="M49 79 H80" stroke="#60a5fa" stroke-width="7" stroke-linecap="round"/>
          <rect x="47" y="91" width="40" height="14" rx="5" fill="url(#sumAccentV46c)"/>
          <path d="M54 98 H80" stroke="#7c2d12" stroke-width="3.4" stroke-linecap="round" opacity=".58"/>
        </g>
        <g filter="drop-shadow(0 4px 6px rgba(0,0,0,.20))">
          <path d="M117 70 L121 82 L133 86 L121 90 L117 102 L113 90 L101 86 L113 82 Z" fill="#fff8f0"/>
          <path d="M29 96 L33 104 L42 107 L33 110 L29 118 L26 110 L17 107 L26 104 Z" fill="#fff8f0" opacity=".92"/>
        </g>
      </svg>
    `;
  }

  function iconCard() {
    return `
      <svg class="rag-action-svg" viewBox="0 0 160 160" aria-hidden="true">
        <defs>
          <linearGradient id="paletteV46c" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0%" stop-color="#ffe7ae"/>
            <stop offset="100%" stop-color="#f6bd57"/>
          </linearGradient>
          <linearGradient id="brushWoodV46c" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0%" stop-color="#ffba66"/>
            <stop offset="100%" stop-color="#8c4c1a"/>
          </linearGradient>
          <linearGradient id="ferruleV46c" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0%" stop-color="#f8fafc"/>
            <stop offset="100%" stop-color="#a8b6c7"/>
          </linearGradient>
          <linearGradient id="paintV46c" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0%" stop-color="#ff7adf"/>
            <stop offset="48%" stop-color="#f019a8"/>
            <stop offset="100%" stop-color="#bc127b"/>
          </linearGradient>
        </defs>
        <g filter="drop-shadow(0 14px 18px rgba(0,0,0,.32))">
          <path d="M63 26 C39 30 24 48 24 70 C24 92 44 110 67 110 C78 110 82 103 78 96 C75 91 78 84 88 81 C106 76 117 64 113 48 C109 31 87 23 63 26 Z"
                fill="url(#paletteV46c)"/>
          <circle cx="52" cy="48" r="10" fill="#ef4444"/>
          <circle cx="73" cy="40" r="10" fill="#facc15"/>
          <circle cx="91" cy="48" r="10" fill="#f59e0b"/>
          <circle cx="48" cy="72" r="10" fill="#22c55e"/>
          <circle cx="69" cy="88" r="10.5" fill="#2563eb"/>
          <path d="M75 67 C68 62 62 67 66 74 C72 71 78 72 75 67 Z" fill="#cf8d2e" opacity=".76"/>
        </g>
        <g transform="translate(6 -2) rotate(-24 109 83)" filter="drop-shadow(0 10px 12px rgba(0,0,0,.30))">
          <path d="M101 31 L117 73" stroke="url(#brushWoodV46c)" stroke-width="14" stroke-linecap="round"/>
          <path d="M102 33 L114 70" stroke="#ffd79b" stroke-width="3.6" stroke-linecap="round" opacity=".78"/>
          <rect x="109" y="68" width="16" height="24" rx="4.5" fill="url(#ferruleV46c)"/>
          <path d="M108 90 C104 96 99 104 95 115 C104 111 115 109 124 113 C121 102 118 96 126 89 C120 91 114 92 108 90 Z"
                fill="url(#paintV46c)"/>
          <path d="M100 114 C97 125 103 131 108 123 C111 117 108 112 100 114 Z" fill="#e31b93"/>
          <path d="M114 113 C113 126 122 135 126 126 C129 119 124 113 114 113 Z" fill="#cf137f"/>
          <path d="M109 92 C114 97 119 98 124 93" stroke="#ffb0ec" stroke-width="3.2" stroke-linecap="round" opacity=".78"/>
        </g>
      </svg>
    `;
  }

  function iconTest() {
    return `
      <svg class="rag-action-svg" viewBox="0 0 160 160" aria-hidden="true">
        <defs>
          <linearGradient id="testBoardV46c" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0%" stop-color="#ffffff"/>
            <stop offset="100%" stop-color="#d7ecff"/>
          </linearGradient>
          <linearGradient id="testClipV46c" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0%" stop-color="#a78bfa"/>
            <stop offset="100%" stop-color="#5b21b6"/>
          </linearGradient>
        </defs>
        <g filter="drop-shadow(0 14px 18px rgba(0,0,0,.32))">
          <rect x="42" y="20" width="76" height="100" rx="14" fill="url(#testBoardV46c)"/>
          <rect x="61" y="8" width="39" height="23" rx="9" fill="url(#testClipV46c)"/>
          <circle cx="80.5" cy="18" r="6" fill="#14b8a6"/>
          <circle cx="80.5" cy="18" r="2.4" fill="#a7f3d0"/>

          <circle cx="57" cy="47" r="9" fill="#22c55e"/>
          <path d="M52 47 L56 51 L63 42" fill="none" stroke="#ffffff" stroke-width="4.3" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M74 47 H101" stroke="#334155" stroke-width="6" stroke-linecap="round"/>

          <circle cx="57" cy="70" r="9" fill="#22c55e"/>
          <path d="M52 70 L56 74 L63 65" fill="none" stroke="#ffffff" stroke-width="4.3" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M74 70 H101" stroke="#334155" stroke-width="6" stroke-linecap="round"/>

          <circle cx="57" cy="93" r="9" fill="#22c55e"/>
          <path d="M52 93 L56 97 L63 88" fill="none" stroke="#ffffff" stroke-width="4.3" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M74 93 H101" stroke="#334155" stroke-width="6" stroke-linecap="round"/>
        </g>
      </svg>
    `;
  }

  function iconStudio() {
    return `
      <svg class="rag-action-svg" viewBox="0 0 160 160" aria-hidden="true">
        <defs>
          <radialGradient id="studyBulbV46c" cx="48%" cy="34%" r="74%">
            <stop offset="0%" stop-color="#fffde0"/>
            <stop offset="34%" stop-color="#fde047"/>
            <stop offset="74%" stop-color="#facc15"/>
            <stop offset="100%" stop-color="#f59e0b"/>
          </radialGradient>
          <filter id="studyGlowV46c" x="-70%" y="-70%" width="240%" height="240%">
            <feGaussianBlur stdDeviation="7" result="blur"/>
            <feMerge>
              <feMergeNode in="blur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        <g filter="url(#studyGlowV46c)" stroke="#facc15" stroke-width="6" stroke-linecap="round">
          <path d="M80 10 V26"/>
          <path d="M45 23 L56 35"/>
          <path d="M115 23 L104 35"/>
          <path d="M19 78 H35"/>
          <path d="M125 78 H141"/>
          <path d="M55 122 L45 134"/>
          <path d="M105 122 L115 134"/>
        </g>
        <path d="M80 33 C59 33 46 48 46 68 C46 82 55 91 62 99 C66 103 67 110 67 116 H93 C93 110 94 103 98 99 C105 91 114 82 114 68 C114 48 101 33 80 33 Z"
              fill="url(#studyBulbV46c)" stroke="#fff4a8" stroke-width="3.2" filter="drop-shadow(0 0 20px rgba(250,204,21,.82)) drop-shadow(0 12px 16px rgba(0,0,0,.28))"/>
        <path d="M70 82 C70 72 90 72 90 82" fill="none" stroke="#fff8ef" stroke-width="6" stroke-linecap="round"/>
        <path d="M72 87 V107" stroke="#fff8ef" stroke-width="6" stroke-linecap="round"/>
        <path d="M88 87 V107" stroke="#fff8ef" stroke-width="6" stroke-linecap="round"/>
        <rect x="66" y="116" width="28" height="9" rx="4.5" fill="#f8fafc"/>
        <rect x="63" y="127" width="34" height="9" rx="4.5" fill="#94a3b8"/>
        <rect x="67" y="138" width="26" height="7" rx="3.5" fill="#64748b"/>
        <circle cx="97" cy="46" r="6" fill="#fffaf0" opacity=".9"/>
      </svg>
    `;
  }

  function rebuildButton(buttonId, svgMarkup) {
    const button = byId(buttonId);
    if (!button) return false;

    const label = LABELS[buttonId] || button.textContent.replace(/\s+/g, ' ').trim();
    button.innerHTML = '';

    const holder = document.createElement('div');
    holder.className = 'rag-action-icon-v46';
    holder.innerHTML = svgMarkup;

    const labelEl = document.createElement('div');
    labelEl.className = 'rag-action-label-v46';
    labelEl.textContent = label;

    button.appendChild(holder);
    button.appendChild(labelEl);
    return true;
  }

  function injectStyle() {
    if (byId('ragActionIconsV46Style')) return;

    const style = document.createElement('style');
    style.id = 'ragActionIconsV46Style';
    style.textContent = `
      .rag-action-icon-v46 {
        width: 170px !important;
        height: 148px !important;
        margin: -4px auto 10px auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: transparent !important;
        border: 0 !important;
        box-shadow: none !important;
        border-radius: 0 !important;
        overflow: visible !important;
        flex: 0 0 auto !important;
      }

      .rag-action-icon-v46::before,
      .rag-action-icon-v46::after {
        display: none !important;
        content: none !important;
      }

      .rag-action-icon-v46 .rag-action-svg {
        width: 150px !important;
        height: 150px !important;
        display: block !important;
        overflow: visible !important;
      }

      .rag-action-label-v46 {
        display: block !important;
        font-size: inherit !important;
        font-weight: inherit !important;
        line-height: 1.2 !important;
        text-align: center !important;
        color: inherit !important;
        margin: 0 auto !important;
      }

      #btnRiassunto,
      #btnCard,
      #btnTest,
      #btnStudio,
      #btnDomandeStudio {
        padding-top: 14px !important;
      }
    `;
    document.head.appendChild(style);
  }

  function applyIcons() {
    injectStyle();
    rebuildButton('btnRiassunto', iconRiassunto());
    rebuildButton('btnCard', iconCard());
    rebuildButton('btnTest', iconTest());
    rebuildButton('btnStudio', iconStudio());
    rebuildButton('btnDomandeStudio', iconStudio());
    window.ragActionIconsV46Ready = true;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyIcons);
  } else {
    applyIcons();
  }
})();
