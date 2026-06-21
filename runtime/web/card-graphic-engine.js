/*
  Motore card grafiche RAG.
  Collegamento: materia -> tema grafico, concetto -> icona SVG.
*/
(function () {
  const THEMES = {
    generico: { label: "Generico", palette: ["#334155", "#64748b", "#e2e8f0"], badge: "Generico", baseIcon: "spark", keywords: ["concetto","studio","formazione"] },
    cybersecurity: { label: "Cybersecurity", palette: ["#0f172a", "#7c3aed", "#ef4444"], badge: "Cybersecurity", baseIcon: "shield", keywords: ["sicurezza","backup","password","phishing","malware","firewall","crittografia","autenticazione"] },
    informatica: { label: "Informatica", palette: ["#0b3b66", "#38bdf8", "#1e293b"], badge: "Informatica", baseIcon: "server", keywords: ["database","algoritmo","funzione","variabile","api","frontend","backend","json"] },
    ai: { label: "Intelligenza Artificiale", palette: ["#1e1b4b", "#8b5cf6", "#22d3ee"], badge: "AI", baseIcon: "chip", keywords: ["modello","prompt","dataset","rete neurale","training","inferenza","rag","embedding"] },
    matematica: { label: "Matematica", palette: ["#0f766e", "#22c55e", "#d9f99d"], badge: "Matematica", baseIcon: "chart", keywords: ["equazione","funzione","derivata","integrale","percentuale","frazione"] },
    fisica: { label: "Fisica", palette: ["#172554", "#60a5fa", "#f59e0b"], badge: "Fisica", baseIcon: "atom", keywords: ["forza","energia","velocità","accelerazione","atomo","corrente"] },
    chimica: { label: "Chimica", palette: ["#14532d", "#2dd4bf", "#fb923c"], badge: "Chimica", baseIcon: "flask", keywords: ["atomo","molecola","reazione","legame","acido","base"] },
    biologia: { label: "Biologia", palette: ["#166534", "#4ade80", "#93c5fd"], badge: "Biologia", baseIcon: "dna", keywords: ["cellula","dna","proteina","organismo","fotosintesi","mitosi"] }
  };

  const CONCEPTS = {
    cybersecurity: {
      sicurezza: "shield", backup: "backup", password: "key", phishing: "email-hook",
      malware: "bug", firewall: "wall", autenticazione: "badge-check", crittografia: "lock-code"
    },
    informatica: {
      database: "database", algoritmo: "flow", funzione: "function", variabile: "box",
      api: "api", frontend: "screen", backend: "server", json: "json"
    },
    ai: {
      modello: "chip", prompt: "prompt", dataset: "table", "rete neurale": "network",
      training: "training", inferenza: "inference", rag: "rag", embedding: "vectors"
    },
    matematica: {
      equazione: "formula", funzione: "chart", derivata: "derivative",
      integrale: "integral", percentuale: "percent", frazione: "fraction"
    },
    fisica: {
      forza: "vector", energia: "energy", velocità: "speed",
      accelerazione: "acceleration", atomo: "atom", corrente: "circuit"
    },
    chimica: {
      atomo: "atom", molecola: "molecule", reazione: "reaction",
      legame: "bond", acido: "flask", base: "beaker"
    },
    biologia: {
      cellula: "cell", dna: "dna", proteina: "protein",
      organismo: "organism", fotosintesi: "leaf", mitosi: "mitosis"
    }
  };

  const SYNONYMS = {
    sicurezza: ["sicurezza","protezione","cybersecurity","security"],
    backup: ["backup","copia di sicurezza","salvataggio dati","ripristino"],
    password: ["password","parola chiave","credenziale","credenziali"],
    phishing: ["phishing","email falsa","truffa via email"],
    malware: ["malware","virus","trojan","software malevolo"],
    firewall: ["firewall","filtro di rete","muro di protezione"],
    autenticazione: ["autenticazione","login","accesso","verifica identità"],
    crittografia: ["crittografia","cifratura","testo cifrato"],
    database: ["database","db","base dati","archivio dati"],
    algoritmo: ["algoritmo","procedura","sequenza di istruzioni"],
    funzione: ["funzione","function","procedura riutilizzabile"],
    variabile: ["variabile","contenitore","valore salvato"],
    api: ["api","endpoint","interfaccia applicativa"],
    frontend: ["frontend","interfaccia utente","ui"],
    backend: ["backend","server","logica lato server"],
    json: ["json","file json","oggetto json"],
    modello: ["modello","modello ai","llm"],
    prompt: ["prompt","istruzione","input testuale"],
    dataset: ["dataset","set di dati","dati di addestramento"],
    "rete neurale": ["rete neurale","neural network","nodi collegati"],
    training: ["training","addestramento","allenamento del modello"],
    inferenza: ["inferenza","predizione","generazione risposta"],
    rag: ["rag","retrieval augmented generation","recupero documenti"],
    embedding: ["embedding","vettore","rappresentazione vettoriale"],
    equazione: ["equazione","formula con incognita"],
    derivata: ["derivata","pendenza","tangente"],
    integrale: ["integrale","area sotto la curva"],
    percentuale: ["percentuale","percento","%"],
    frazione: ["frazione","numeratore","denominatore"],
    forza: ["forza","spinta","trazione"],
    energia: ["energia","lavoro","potenza"],
    velocità: ["velocità","rapidità","spostamento"],
    accelerazione: ["accelerazione","variazione velocità"],
    atomo: ["atomo","nucleo","elettrone"],
    corrente: ["corrente","corrente elettrica","elettroni"],
    molecola: ["molecola","composto"],
    reazione: ["reazione","reazione chimica","prodotti","reagenti"],
    legame: ["legame","legame chimico"],
    acido: ["acido","ph acido"],
    base: ["base","ph basico","alcalino"],
    cellula: ["cellula","nucleo cellulare","membrana"],
    dna: ["dna","gene","doppia elica"],
    proteina: ["proteina","amminoacidi","catena proteica"],
    organismo: ["organismo","essere vivente"],
    fotosintesi: ["fotosintesi","clorofilla","luce solare"],
    mitosi: ["mitosi","divisione cellulare","cromosomi"]
  };

  function normalizeText(text) {
    return String(text || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[^a-z0-9%]+/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function getSelectedCardSubject() {
    const select = document.getElementById("ragCardSubjectSelect");
    return select ? select.value : "auto";
  }

  function detectSubject(text, selectedSubject) {
    if (selectedSubject && selectedSubject !== "auto" && THEMES[selectedSubject]) {
      return selectedSubject;
    }

    const normalized = normalizeText(text);
    let bestSubject = "generico";
    let bestScore = 0;

    Object.entries(THEMES).forEach(([subject, theme]) => {
      if (subject === "generico") return;
      let score = 0;

      theme.keywords.forEach(keyword => {
        if (normalized.includes(normalizeText(keyword))) score += 3;
      });

      Object.keys(CONCEPTS[subject] || {}).forEach(concept => {
        if (normalized.includes(normalizeText(concept))) score += 5;
      });

      if (score > bestScore) {
        bestScore = score;
        bestSubject = subject;
      }
    });

    return bestScore > 0 ? bestSubject : "generico";
  }

  function detectConcept(text, subject) {
    const normalized = normalizeText(text);
    const subjects = subject && CONCEPTS[subject] ? [subject] : Object.keys(CONCEPTS);

    let bestConcept = null;
    let bestScore = 0;

    subjects.forEach(currentSubject => {
      Object.keys(CONCEPTS[currentSubject] || {}).forEach(concept => {
        const names = [concept].concat(SYNONYMS[concept] || []);
        let score = 0;

        names.forEach(name => {
          const nameNorm = normalizeText(name);
          if (nameNorm && normalized.includes(nameNorm)) {
            score += 10 + nameNorm.length;
          }
        });

        if (score > bestScore) {
          bestScore = score;
          bestConcept = concept;
        }
      });
    });

    if (bestConcept) return bestConcept;

    const firstUsefulWord = (String(text || "").match(/[A-Za-zÀ-ÖØ-öø-ÿ0-9]{4,}/g) || [])
      .find(word => !["questo","questa","documento","viene","sono","della","delle","come","anche"].includes(normalizeText(word)));

    return firstUsefulWord ? firstUsefulWord.toLowerCase() : "concetto";
  }

  function resolveProfile(text, selectedSubject) {
    const subject = detectSubject(text, selectedSubject);
    const concept = detectConcept(text, subject);
    const theme = THEMES[subject] || THEMES.generico;
    const icon = (CONCEPTS[subject] && CONCEPTS[subject][concept]) || theme.baseIcon || "spark";
    return { subject, concept, theme, icon };
  }

  function svgIcon(icon, palette) {
    const [primary, secondary, accent] = palette;

    if (["shield", "lock-code", "badge-check", "wall"].includes(icon)) {
      return `
        <path d="M110 26 L168 50 V92 C168 130 143 158 110 176 C77 158 52 130 52 92 V50 Z" fill="${accent}" opacity=".92"/>
        <rect x="86" y="96" width="48" height="42" rx="8" fill="${primary}" opacity=".9"/>
        <path d="M96 96 v-15 c0-19 28-19 28 0v15" fill="none" stroke="${primary}" stroke-width="9" stroke-linecap="round"/>`;
    }

    if (icon === "backup") {
      return `
        <path d="M74 126 h86 c20 0 35-14 35-32 0-17-13-30-31-32-7-20-25-32-48-32-28 0-49 18-53 44-20 3-34 17-34 35 0 10 5 17 13 17z" fill="${accent}" opacity=".92"/>
        <path d="M110 118 V78" stroke="${primary}" stroke-width="10" stroke-linecap="round"/>
        <path d="M90 96 l20-20 20 20" fill="none" stroke="${primary}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
        <rect x="72" y="142" width="76" height="24" rx="8" fill="${primary}" opacity=".9"/>`;
    }

    if (icon === "key") {
      return `
        <circle cx="82" cy="88" r="30" fill="none" stroke="${accent}" stroke-width="13"/>
        <path d="M106 100 L170 164" stroke="${accent}" stroke-width="15" stroke-linecap="round"/>
        <path d="M148 142 h32 M132 126 h22" stroke="${accent}" stroke-width="10" stroke-linecap="round"/>`;
    }

    if (icon === "email-hook") {
      return `
        <rect x="44" y="66" width="128" height="82" rx="14" fill="${accent}" opacity=".92"/>
        <path d="M48 76 l60 42 60-42" fill="none" stroke="${primary}" stroke-width="8" stroke-linejoin="round"/>
        <path d="M150 44 c30 18 28 66-2 76" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round"/>`;
    }

    if (icon === "bug") {
      return `
        <circle cx="110" cy="104" r="44" fill="${accent}" opacity=".94"/>
        <circle cx="94" cy="94" r="7" fill="${primary}"/>
        <circle cx="126" cy="94" r="7" fill="${primary}"/>
        <path d="M92 122 c14 10 25 10 38 0" stroke="${primary}" stroke-width="8" stroke-linecap="round"/>
        <path d="M54 104 H28 M192 104 h-26 M72 62 L50 42 M148 62 l22-20" stroke="${accent}" stroke-width="9" stroke-linecap="round"/>`;
    }

    if (icon === "database") {
      return `
        <ellipse cx="110" cy="58" rx="62" ry="24" fill="${accent}" opacity=".95"/>
        <path d="M48 58 v88 c0 14 28 25 62 25s62-11 62-25V58" fill="${accent}" opacity=".75"/>
        <ellipse cx="110" cy="146" rx="62" ry="24" fill="${accent}" opacity=".9"/>
        <path d="M48 90 c0 14 28 25 62 25s62-11 62-25 M48 118 c0 14 28 25 62 25s62-11 62-25" fill="none" stroke="${primary}" stroke-width="6" opacity=".65"/>`;
    }

    if (["flow", "function", "api", "server", "json", "screen", "box"].includes(icon)) {
      return `
        <rect x="34" y="52" width="58" height="40" rx="10" fill="${accent}"/>
        <rect x="128" y="52" width="58" height="40" rx="10" fill="${accent}" opacity=".85"/>
        <rect x="81" y="124" width="58" height="40" rx="10" fill="${accent}" opacity=".7"/>
        <path d="M92 72 h36 M110 92 v32" stroke="#fff" stroke-width="8" stroke-linecap="round"/>`;
    }

    if (["chip", "network", "vectors", "prompt", "rag", "table", "training", "inference"].includes(icon)) {
      return `
        <rect x="66" y="54" width="88" height="88" rx="18" fill="${accent}" opacity=".9"/>
        <path d="M46 72 h20 M46 96 h20 M46 120 h20 M154 72 h20 M154 96 h20 M154 120 h20" stroke="${accent}" stroke-width="8" stroke-linecap="round"/>
        <circle cx="90" cy="86" r="7" fill="${primary}"/><circle cx="128" cy="86" r="7" fill="${primary}"/><circle cx="110" cy="118" r="7" fill="${primary}"/>
        <path d="M90 86 L110 118 L128 86" stroke="${primary}" stroke-width="5" fill="none"/>`;
    }

    if (["chart", "derivative", "integral", "formula", "percent", "fraction"].includes(icon)) {
      return `
        <path d="M44 150 H178 M58 164 V44" stroke="#fff" stroke-width="6" opacity=".75"/>
        <path d="M58 136 C84 126 86 72 116 86 C140 98 142 132 174 58" fill="none" stroke="${accent}" stroke-width="11" stroke-linecap="round"/>
        <path d="M86 112 L150 74" stroke="${primary}" stroke-width="7" stroke-linecap="round" opacity=".88"/>`;
    }

    if (["atom", "energy", "vector", "speed", "acceleration", "circuit"].includes(icon)) {
      return `
        <circle cx="110" cy="104" r="13" fill="${accent}"/>
        <ellipse cx="110" cy="104" rx="76" ry="28" fill="none" stroke="${accent}" stroke-width="7"/>
        <ellipse cx="110" cy="104" rx="76" ry="28" fill="none" stroke="${accent}" stroke-width="7" transform="rotate(60 110 104)"/>
        <ellipse cx="110" cy="104" rx="76" ry="28" fill="none" stroke="${accent}" stroke-width="7" transform="rotate(-60 110 104)"/>`;
    }

    if (["molecule", "reaction", "bond", "flask", "beaker"].includes(icon)) {
      return `
        <circle cx="74" cy="92" r="26" fill="${accent}"/><circle cx="146" cy="72" r="22" fill="${accent}" opacity=".8"/><circle cx="142" cy="138" r="28" fill="${accent}" opacity=".65"/>
        <path d="M96 86 L126 78 M94 104 L120 126" stroke="#fff" stroke-width="8" stroke-linecap="round"/>`;
    }

    if (["dna", "cell", "protein", "organism", "leaf", "mitosis"].includes(icon)) {
      return `
        <path d="M76 34 C148 70 148 138 76 174 M144 34 C72 70 72 138 144 174" fill="none" stroke="${accent}" stroke-width="9" stroke-linecap="round"/>
        <path d="M88 60 h44 M78 88 h64 M78 120 h64 M88 148 h44" stroke="#fff" stroke-width="6" opacity=".7"/>`;
    }

    return `
      <circle cx="110" cy="90" r="46" fill="${accent}" opacity=".9"/>
      <rect x="52" y="142" width="116" height="18" rx="9" fill="${accent}" opacity=".65"/>
      <text x="110" y="104" text-anchor="middle" font-size="24" fill="${primary}" font-family="Arial" font-weight="900">★</text>`;
  }

  function renderSvg(profile) {
    const [primary, secondary, accent] = profile.theme.palette;
    const safeConcept = escapeHtml(profile.concept);
    const gradientId = `rag-card-${profile.subject}-${normalizeText(profile.concept).replaceAll(" ", "-")}`;

    return `
      <svg class="rag-graphic-card-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 210" role="img" aria-label="Illustrazione ${safeConcept}">
        <defs>
          <linearGradient id="${gradientId}" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="${primary}"/>
            <stop offset="100%" stop-color="${secondary}"/>
          </linearGradient>
        </defs>
        <rect width="220" height="210" rx="28" fill="url(#${gradientId})"/>
        <circle cx="48" cy="52" r="34" fill="${accent}" opacity="0.16"/>
        <circle cx="176" cy="176" r="60" fill="#ffffff" opacity="0.08"/>
        ${svgIcon(profile.icon, profile.theme.palette)}
      </svg>`;
  }

  function renderGraphicCard(card, index = 0) {
    const subject = card.materia || card.subject || getSelectedCardSubject();
    const profile = resolveProfile(`${card.fronte || ""} ${card.retro || ""} ${card.concetto || ""}`, subject);
    const [primary, secondary, accent] = profile.theme.palette;

    return `
      <article class="rag-graphic-card" data-materia="${escapeHtml(profile.subject)}" data-concetto="${escapeHtml(profile.concept)}"
        style="--card-primary:${primary};--card-secondary:${secondary};--card-accent:${accent};">
        <div class="rag-graphic-card-badge">${escapeHtml(profile.theme.badge)}</div>
        <div class="rag-graphic-card-image">${card.illustrazione || renderSvg(profile)}</div>
        <h2>${escapeHtml(card.fronte || `Concetto chiave: ${profile.concept}`)}</h2>
        <p>${escapeHtml(card.retro || "")}</p>
        <small>${escapeHtml(card.uso || "Ripassa questo punto e prova a rispiegarlo con parole tue.")}</small>
      </article>`;
  }

  function insertSubjectSelector() {
    if (document.getElementById("ragCardSubjectSelect")) return;

    const controls = document.getElementById("ragControls");
    const generateButton = document.getElementById("generateButton");
    const target = controls || generateButton;

    if (!target || !target.parentNode) return;

    const wrapper = document.createElement("section");
    wrapper.className = "rag-card-subject-box";
    wrapper.innerHTML = `
      <h2>Grafica card per materia</h2>
      <p>Scegli la materia per rendere le card più coerenti. Puoi lasciare automatico se non sei sicuro.</p>
      <label>
        <span>Materia card</span>
        <select id="ragCardSubjectSelect">
          <option value="auto">Automatica / rileva dal contenuto</option>
          <option value="cybersecurity">Cybersecurity</option>
          <option value="informatica">Informatica</option>
          <option value="ai">Intelligenza Artificiale</option>
          <option value="matematica">Matematica</option>
          <option value="fisica">Fisica</option>
          <option value="chimica">Chimica</option>
          <option value="biologia">Biologia</option>
          <option value="generico">Generico</option>
        </select>
      </label>
    `;

    if (controls && controls.parentNode) {
      controls.parentNode.insertBefore(wrapper, controls.nextSibling);
    } else {
      target.parentNode.insertBefore(wrapper, target);
    }
  }

  function buildCardObject(row, index = 0) {
    const selectedSubject = getSelectedCardSubject();
    const text = `${row.concetto || ""} ${row.spiegazione || ""}`;
    const profile = resolveProfile(text, selectedSubject);

    return {
      id: `RAG-CARD-${String(index + 1).padStart(4, "0")}`,
      materia: profile.subject,
      concetto: profile.concept,
      tema: profile.theme.badge,
      icona: profile.icon,
      fronte: `Concetto chiave: ${row.concetto || profile.concept}`,
      retro: row.spiegazione || "",
      uso: "Ripassa questo punto e prova a rispiegarlo con parole tue.",
      illustrazione: renderSvg(profile)
    };
  }

  window.RagCardGraphicEngine = {
    themes: THEMES,
    concepts: CONCEPTS,
    synonyms: SYNONYMS,
    normalizeText,
    detectSubject,
    detectConcept,
    resolveProfile,
    renderSvg,
    renderGraphicCard,
    insertSubjectSelector,
    buildCardObject
  };

  window.cardPalette = function (index, materia = null) {
    const selectedSubject = materia || getSelectedCardSubject();
    const theme = THEMES[selectedSubject] || THEMES.generico;
    return theme.palette;
  };

  window.buildCardIllustration = function (keyword, index = 0) {
    const profile = resolveProfile(String(keyword || ""), getSelectedCardSubject());
    return renderSvg(profile);
  };

  window.makeCards = function (rows, limit = 12) {
    return rows.slice(0, limit).map((row, index) => buildCardObject(row, index));
  };

  window.makeCardsHtmlDocument = function (analysis) {
    const cards = analysis.cards || [];
    const cardsHtml = cards.map((card, index) => renderGraphicCard(card, index)).join("\n");

    return `<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Card RAG - ${escapeHtml(analysis.titolo || "Documento")}</title>
<style>
body{margin:0;font-family:Arial,Helvetica,sans-serif;background:#020617;color:#f8fafc}
main{max-width:1180px;margin:0 auto;padding:42px 20px 70px}
h1{font-size:clamp(34px,5vw,58px);margin:0 0 24px}
.rag-graphic-cards-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(285px,1fr));gap:18px}
.rag-graphic-card{position:relative;overflow:hidden;border-radius:28px;padding:20px;background:linear-gradient(145deg,var(--card-primary),var(--card-secondary));border:1px solid rgba(255,255,255,.16);box-shadow:0 26px 80px rgba(0,0,0,.34);min-height:430px}
.rag-graphic-card::after{content:"";position:absolute;width:160px;height:160px;right:-60px;bottom:-60px;border-radius:50%;background:var(--card-accent);opacity:.13}
.rag-graphic-card-badge{position:relative;z-index:2;display:inline-flex;padding:8px 12px;border-radius:999px;background:rgba(255,255,255,.16);color:#fff;font-size:12px;font-weight:900;letter-spacing:.08em;text-transform:uppercase}
.rag-graphic-card-image{position:relative;z-index:2;margin:18px 0 16px}
.rag-graphic-card-svg{width:100%;height:auto;display:block}
.rag-graphic-card h2{position:relative;z-index:2;font-size:22px;line-height:1.16;margin:0 0 12px}
.rag-graphic-card p{position:relative;z-index:2;color:#f8fafc;line-height:1.55;font-size:15px}
.rag-graphic-card small{position:relative;z-index:2;display:block;color:#e5e7eb;font-weight:800;line-height:1.45;margin-top:14px}
</style>
</head>
<body>
<main>
<h1>Card di ripasso - ${escapeHtml(analysis.titolo || "Documento")}</h1>
<section class="rag-graphic-cards-grid">
${cardsHtml}
</section>
</main>
</body>
</html>`;
  };

  document.addEventListener("DOMContentLoaded", insertSubjectSelector);
  setTimeout(insertSubjectSelector, 150);
})();
