(function () {
  function normalize(text) {
    return (text || "").replace(/\s+/g, " ").trim().toLowerCase();
  }

  function findByText(part) {
    const nodes = Array.from(
      document.querySelectorAll("button, a, label, [role='button']")
    );
    return nodes.find((el) => normalize(el.textContent).includes(part));
  }

  function iconSvg(type) {
    const icons = {
      summary: `
        <svg viewBox="0 0 64 64" aria-hidden="true">
          <rect x="14" y="8" width="28" height="40" rx="6" fill="#ffffff"></rect>
          <path d="M20 20h16" stroke="#3d72ff" stroke-width="4" stroke-linecap="round"></path>
          <path d="M20 28h14" stroke="#ff8a54" stroke-width="4" stroke-linecap="round"></path>
          <path d="M20 36h12" stroke="#15c48b" stroke-width="4" stroke-linecap="round"></path>
          <circle cx="44" cy="42" r="10" fill="#1fd184"></circle>
          <path d="M39.5 42l3 3 6-7" fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></path>
        </svg>
      `,
      cards: `
        <svg viewBox="0 0 64 64" aria-hidden="true">
          <rect x="12" y="16" width="40" height="28" rx="6" fill="#ffffff"></rect>
          <circle cx="24" cy="29" r="5" fill="#4b83ff"></circle>
          <path d="M18 40c2-5 6-8 11-8s9 3 11 8" fill="none" stroke="#4b83ff" stroke-width="4" stroke-linecap="round"></path>
          <path d="M34 24h10" stroke="#ff8a54" stroke-width="4" stroke-linecap="round"></path>
          <path d="M34 31h10" stroke="#15c48b" stroke-width="4" stroke-linecap="round"></path>
        </svg>
      `,
      test: `
        <svg viewBox="0 0 64 64" aria-hidden="true">
          <rect x="18" y="10" width="28" height="42" rx="6" fill="#ffffff"></rect>
          <rect x="24" y="6" width="16" height="8" rx="4" fill="#7b6cff"></rect>
          <path d="M26 22h12" stroke="#4b83ff" stroke-width="4" stroke-linecap="round"></path>
          <path d="M26 30h12" stroke="#4b83ff" stroke-width="4" stroke-linecap="round"></path>
          <path d="M26 38h12" stroke="#4b83ff" stroke-width="4" stroke-linecap="round"></path>
          <path d="M22 22l2 2 3-4" fill="none" stroke="#17c786" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></path>
          <path d="M22 30l2 2 3-4" fill="none" stroke="#17c786" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></path>
          <path d="M22 38l2 2 3-4" fill="none" stroke="#17c786" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></path>
        </svg>
      `,
      study: `
        <svg viewBox="0 0 64 64" aria-hidden="true">
          <path d="M23 47h18" stroke="#2f7cff" stroke-width="4" stroke-linecap="round"></path>
          <path d="M15 42c5-1 9-1 14 1V25c-5-2-9-2-14-1z" fill="#ffffff"></path>
          <path d="M35 43c5-2 9-2 14-1V24c-5-1-9-1-14 1z" fill="#dff0ff"></path>
          <path d="M32 10c7 0 12 5 12 11 0 5-3 8-6 10v5H26v-5c-3-2-6-5-6-10 0-6 5-11 12-11z" fill="#ffd451"></path>
          <path d="M28 18l4-3 4 3-1.5 5h-5z" fill="#ff9f43"></path>
          <path d="M32 6v-3" stroke="#ffd451" stroke-width="4" stroke-linecap="round"></path>
          <path d="M21 10l-2-2" stroke="#ffd451" stroke-width="4" stroke-linecap="round"></path>
          <path d="M43 10l2-2" stroke="#ffd451" stroke-width="4" stroke-linecap="round"></path>
        </svg>
      `
    };
    return icons[type] || "";
  }

  function decorateGenerator(el, type, label, className) {
    if (!el) return;
    el.classList.add("action-btn-gen", className);

    if (el.dataset.decorated === "1") return;

    el.dataset.decorated = "1";
    el.innerHTML = `
      <span class="gen-icon-wrap">${iconSvg(type)}</span>
      <span class="gen-label">${label}</span>
    `;
  }

  function installLayout() {
    const upload = findByText("carica file pdf");
    const ocr = findByText("ripulisci testo ocr");
    const summary = findByText("genera riassunto");
    const cards = findByText("genera card");
    const test = findByText("genera test");
    const study = findByText("genera domande studio");

    const all = [upload, ocr, summary, cards, test, study];
    if (all.some((x) => !x)) {
      console.warn("Layout bottoni: alcuni pulsanti non sono stati trovati.");
      return;
    }

    const titleNode = Array.from(document.querySelectorAll("h1,h2,h3,h4,div"))
      .find((el) => normalize(el.textContent).includes("flusso finale del motore documenti"));

    const anchorSection = titleNode ? titleNode.closest("section, div") : null;
    const hostParent =
      (anchorSection && anchorSection.parentElement) ||
      (upload.closest("section, div") && upload.closest("section, div").parentElement) ||
      document.body;

    let zone = document.getElementById("full-width-action-zone");
    if (!zone) {
      zone = document.createElement("section");
      zone.id = "full-width-action-zone";
      hostParent.insertBefore(zone, anchorSection || hostParent.firstChild);
    }

    zone.innerHTML = `
      <div class="fw-top"></div>
      <div class="fw-bottom"></div>
    `;

    upload.classList.add("action-btn-top");
    ocr.classList.add("action-btn-top");

    /* IMPORTANTE:
       usiamo gli STESSI pulsanti veri, quindi i listener dei motori restano attivi */
    decorateGenerator(summary, "summary", "Genera riassunto", "gen-summary");
    decorateGenerator(cards, "cards", "Genera card", "gen-cards");
    decorateGenerator(test, "test", "Genera test", "gen-test");
    decorateGenerator(study, "study", "Genera domande studio", "gen-study");

    zone.querySelector(".fw-top").append(upload, ocr);
    zone.querySelector(".fw-bottom").append(summary, cards, test, study);
  }

  document.addEventListener("DOMContentLoaded", installLayout);
  window.addEventListener("load", installLayout);
  setTimeout(installLayout, 250);
  setTimeout(installLayout, 900);
  setTimeout(installLayout, 1600);
})();
