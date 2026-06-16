from pathlib import Path
import re

SCRIPT_PATH = Path("scripts/rigenera_demo_separate.py")

NUOVO_APP_JS = r'''
const STATO = {
  domande: [],
  domandeFiltrate: [],
  domandeQuiz: [],
  indiceDomanda: 0,
  punteggio: 0,
  rispostaBloccata: false
};

function testoDomanda(domanda) {
  return domanda.domanda || domanda.question || domanda.testo || domanda.titolo || "Domanda senza testo";
}

function testoSpiegazione(domanda) {
  return domanda.spiegazione || domanda.explanation || domanda.commento || "";
}

function livelloDomanda(domanda) {
  return domanda.livello || domanda.difficulty || domanda.difficolta || "senza livello";
}

function materiaDomanda(domanda) {
  return domanda._materia_demo || domanda.materia || domanda.categoria || domanda.sezione || "Senza materia";
}

function immagineDomanda(domanda) {
  return (
    domanda.immagine_domanda ||
    domanda.question_image ||
    domanda.image_question ||
    domanda.figura_domanda ||
    domanda.percorso_immagine_domanda ||
    domanda.immagine ||
    domanda.image ||
    domanda.image_path ||
    ""
  );
}

function estraiPercorsoDaValore(valore) {
  if (!valore) {
    return "";
  }

  if (typeof valore === "string") {
    return valore;
  }

  if (typeof valore === "object") {
    return (
      valore.immagine ||
      valore.image ||
      valore.image_path ||
      valore.path ||
      valore.src ||
      valore.file ||
      valore.percorso ||
      valore.percorso_immagine ||
      ""
    );
  }

  return "";
}

function immagineOpzioneDaArchivio(domanda, indice, lettera) {
  const archiviPossibili = [
    domanda.immagini_opzioni,
    domanda.opzioni_immagini,
    domanda.immagini_risposte,
    domanda.risposte_immagini,
    domanda.answer_images,
    domanda.option_images,
    domanda.figure_opzioni,
    domanda.figures_options
  ];

  for (const archivio of archiviPossibili) {
    if (!archivio) {
      continue;
    }

    if (Array.isArray(archivio)) {
      const percorso = estraiPercorsoDaValore(archivio[indice]);
      if (percorso) {
        return percorso;
      }
    }

    if (typeof archivio === "object") {
      const chiavi = [
        lettera,
        lettera.toLowerCase(),
        String(indice),
        String(indice + 1)
      ];

      for (const chiave of chiavi) {
        const percorso = estraiPercorsoDaValore(archivio[chiave]);
        if (percorso) {
          return percorso;
        }
      }
    }
  }

  const letteraMinuscola = lettera.toLowerCase();
  const chiaviDirette = [
    `immagine_${letteraMinuscola}`,
    `immagine_${lettera}`,
    `immagine_opzione_${letteraMinuscola}`,
    `immagine_opzione_${lettera}`,
    `immagine_risposta_${letteraMinuscola}`,
    `immagine_risposta_${lettera}`,
    `opzione_${letteraMinuscola}_immagine`,
    `opzione_${lettera}_immagine`,
    `risposta_${letteraMinuscola}_immagine`,
    `risposta_${lettera}_immagine`,
    `image_${letteraMinuscola}`,
    `image_${lettera}`
  ];

  for (const chiave of chiaviDirette) {
    const percorso = estraiPercorsoDaValore(domanda[chiave]);
    if (percorso) {
      return percorso;
    }
  }

  return "";
}

function correggiPercorsoImmagine(percorso) {
  if (!percorso || typeof percorso !== "string") {
    return "";
  }

  if (
    percorso.startsWith("http://") ||
    percorso.startsWith("https://") ||
    percorso.startsWith("data:") ||
    percorso.startsWith("../") ||
    percorso.startsWith("./")
  ) {
    return percorso;
  }

  return "../" + percorso.replace(/^\/+/, "");
}

function mescolaArray(arrayOriginale) {
  const array = [...arrayOriginale];

  for (let indice = array.length - 1; indice > 0; indice--) {
    const indiceCasuale = Math.floor(Math.random() * (indice + 1));
    const temporaneo = array[indice];
    array[indice] = array[indiceCasuale];
    array[indiceCasuale] = temporaneo;
  }

  return array;
}

function normalizzaOpzioni(domanda) {
  const opzioniGrezze =
    domanda.opzioni ||
    domanda.options ||
    domanda.risposte ||
    domanda.answers ||
    [];

  let opzioni = [];

  if (Array.isArray(opzioniGrezze)) {
    opzioni = opzioniGrezze.map((opzione, indice) => {
      const letteraOriginale = String.fromCharCode(65 + indice);

      if (typeof opzione === "object" && opzione !== null) {
        const testo =
          opzione.testo ||
          opzione.text ||
          opzione.risposta ||
          opzione.value ||
          opzione.label ||
          "";

        const immagine =
          opzione.immagine ||
          opzione.image ||
          opzione.image_path ||
          opzione.path ||
          opzione.src ||
          opzione.file ||
          opzione.percorso ||
          opzione.percorso_immagine ||
          opzione.immagine_opzione ||
          opzione.immagine_risposta ||
          immagineOpzioneDaArchivio(domanda, indice, letteraOriginale);

        return {
          indiceOriginale: indice,
          letteraOriginale,
          testo,
          immagine,
          correttaEsplicita:
            opzione.corretta === true ||
            opzione.correct === true ||
            opzione.is_correct === true
        };
      }

      return {
        indiceOriginale: indice,
        letteraOriginale,
        testo: String(opzione),
        immagine: immagineOpzioneDaArchivio(domanda, indice, letteraOriginale),
        correttaEsplicita: false
      };
    });
  }

  if (!Array.isArray(opzioniGrezze) && typeof opzioniGrezze === "object" && opzioniGrezze !== null) {
    opzioni = Object.entries(opzioniGrezze).map(([lettera, valore], indice) => {
      const letteraOriginale = lettera.toUpperCase();

      if (typeof valore === "object" && valore !== null) {
        return {
          indiceOriginale: indice,
          letteraOriginale,
          testo:
            valore.testo ||
            valore.text ||
            valore.risposta ||
            valore.value ||
            valore.label ||
            "",
          immagine:
            valore.immagine ||
            valore.image ||
            valore.image_path ||
            valore.path ||
            valore.src ||
            valore.file ||
            valore.percorso ||
            valore.percorso_immagine ||
            valore.immagine_opzione ||
            valore.immagine_risposta ||
            immagineOpzioneDaArchivio(domanda, indice, letteraOriginale),
          correttaEsplicita:
            valore.corretta === true ||
            valore.correct === true ||
            valore.is_correct === true
        };
      }

      return {
        indiceOriginale: indice,
        letteraOriginale,
        testo: String(valore),
        immagine: immagineOpzioneDaArchivio(domanda, indice, letteraOriginale),
        correttaEsplicita: false
      };
    });
  }

  const rispostaCorrettaGrezza =
    domanda.risposta_corretta ||
    domanda.correct_answer ||
    domanda.correct ||
    domanda.answer ||
    domanda.soluzione ||
    "";

  const rispostaCorretta = String(rispostaCorrettaGrezza).trim();

  opzioni = opzioni.map((opzione) => {
    const testoOpzione = String(opzione.testo).trim();
    const letteraOpzione = String(opzione.letteraOriginale).trim().toUpperCase();

    const corretta =
      opzione.correttaEsplicita ||
      rispostaCorretta.toUpperCase() === letteraOpzione ||
      rispostaCorretta === testoOpzione;

    return {
      ...opzione,
      corretta
    };
  });

  return mescolaArray(opzioni);
}

function calcolaDomandeFiltrateCorrenti() {
  const materiaScelta = document.getElementById("materiaSelect").value;
  const livelloScelto = document.getElementById("livelloSelect").value;

  return STATO.domande.filter((domanda) => {
    const materiaOk =
      materiaScelta === "tutte" ||
      materiaDomanda(domanda) === materiaScelta;

    const livelloOk =
      livelloScelto === "tutti" ||
      livelloDomanda(domanda) === livelloScelto;

    return materiaOk && livelloOk;
  });
}

function aggiornaNumeroDomandeDisponibili() {
  const selectNumero = document.getElementById("numeroDomandeSelect");
  const domandeFiltrate = calcolaDomandeFiltrateCorrenti();
  const massimo = domandeFiltrate.length;

  selectNumero.innerHTML = "";

  if (massimo === 0) {
    const option = document.createElement("option");
    option.value = "0";
    option.textContent = "0 domande";
    selectNumero.appendChild(option);
    return;
  }

  const scelteBase = [10, 20, 30, 40, 50, 80, 100];
  const scelte = scelteBase.filter((numero) => numero <= massimo);

  if (!scelte.includes(massimo)) {
    scelte.push(massimo);
  }

  scelte.sort((a, b) => a - b);

  for (const numero of scelte) {
    const option = document.createElement("option");
    option.value = String(numero);

    if (numero === massimo) {
      option.textContent = `Tutte disponibili (${numero})`;
    } else {
      option.textContent = `${numero} domande`;
    }

    selectNumero.appendChild(option);
  }

  const preferita = scelte.includes(10) ? 10 : scelte[0];
  selectNumero.value = String(preferita);
}

function aggiornaContatori() {
  const totale = STATO.domande.length;
  document.getElementById("totaleDomande").textContent = totale;

  const conteggioMaterie = new Map();

  for (const domanda of STATO.domande) {
    const materia = materiaDomanda(domanda);
    conteggioMaterie.set(materia, (conteggioMaterie.get(materia) || 0) + 1);
  }

  const contenitore = document.getElementById("conteggioMaterie");
  contenitore.innerHTML = "";

  [...conteggioMaterie.entries()]
    .sort((a, b) => a[0].localeCompare(b[0], "it"))
    .forEach(([materia, conteggio]) => {
      const card = document.createElement("div");
      card.className = "counter-card";
      card.innerHTML = `
        <strong>${materia}</strong>
        <span>${conteggio}</span>
      `;
      contenitore.appendChild(card);
    });
}

function popolaFiltri() {
  const materie = [...new Set(STATO.domande.map(materiaDomanda))]
    .sort((a, b) => a.localeCompare(b, "it"));

  const livelli = [...new Set(STATO.domande.map(livelloDomanda))]
    .sort((a, b) => a.localeCompare(b, "it"));

  const selectMateria = document.getElementById("materiaSelect");
  const selectLivello = document.getElementById("livelloSelect");

  selectMateria.innerHTML = `<option value="tutte">Tutte le materie</option>`;
  selectLivello.innerHTML = `<option value="tutti">Tutti i livelli</option>`;

  for (const materia of materie) {
    const option = document.createElement("option");
    option.value = materia;
    option.textContent = materia;
    selectMateria.appendChild(option);
  }

  for (const livello of livelli) {
    const option = document.createElement("option");
    option.value = livello;
    option.textContent = livello;
    selectLivello.appendChild(option);
  }

  selectMateria.addEventListener("change", aggiornaNumeroDomandeDisponibili);
  selectLivello.addEventListener("change", aggiornaNumeroDomandeDisponibili);

  aggiornaNumeroDomandeDisponibili();
}

function avviaQuiz() {
  const numeroDomande = Number(document.getElementById("numeroDomandeSelect").value);

  STATO.domandeFiltrate = calcolaDomandeFiltrateCorrenti();
  STATO.domandeQuiz = mescolaArray(STATO.domandeFiltrate).slice(0, numeroDomande);
  STATO.indiceDomanda = 0;
  STATO.punteggio = 0;
  STATO.rispostaBloccata = false;

  document.getElementById("risultatoFinale").innerHTML = "";

  if (STATO.domandeQuiz.length === 0) {
    document.getElementById("areaQuiz").innerHTML = `
      <div class="empty-box">
        Nessuna domanda trovata con questi filtri.
      </div>
    `;
    return;
  }

  mostraDomanda();
}

function mostraDomanda() {
  STATO.rispostaBloccata = false;

  const domanda = STATO.domandeQuiz[STATO.indiceDomanda];
  const opzioni = normalizzaOpzioni(domanda);

  const areaQuiz = document.getElementById("areaQuiz");

  const percorsoImmagineDomanda = correggiPercorsoImmagine(immagineDomanda(domanda));
  const bloccoImmagineDomanda = percorsoImmagineDomanda
    ? `<img class="question-image" src="${percorsoImmagineDomanda}" alt="Figura della domanda">`
    : "";

  areaQuiz.innerHTML = `
    <div class="quiz-card">
      <div class="quiz-top-row">
        <div class="progress">
          ${STATO.indiceDomanda + 1}/${STATO.domandeQuiz.length}
        </div>

        <div class="meta">
          <span>${materiaDomanda(domanda)}</span>
          <span>${livelloDomanda(domanda)}</span>
        </div>
      </div>

      <h2>${testoDomanda(domanda)}</h2>

      ${bloccoImmagineDomanda}

      <div id="opzioniBox" class="options"></div>

      <div id="spiegazioneBox" class="explanation hidden"></div>

      <button id="prossimaDomandaBtn" class="secondary hidden" onclick="prossimaDomanda()">
        Prossima domanda
      </button>
    </div>
  `;

  const opzioniBox = document.getElementById("opzioniBox");

  opzioni.forEach((opzione) => {
    const button = document.createElement("button");
    const immagineOpzione = correggiPercorsoImmagine(opzione.immagine);

    button.className = immagineOpzione
      ? "option-button visual-option"
      : "option-button";

    const testoOpzione = opzione.testo ? `<span class="option-text">${opzione.testo}</span>` : "";

    button.innerHTML = `
      ${
        immagineOpzione
          ? `<img class="option-image" src="${immagineOpzione}" alt="Figura opzione">`
          : ""
      }
      ${testoOpzione}
    `;

    button.addEventListener("click", () => controllaRisposta(button, opzione, opzioni));

    opzioniBox.appendChild(button);
  });
}

function effettoRispostaCorretta() {
  const effetto = document.createElement("div");
  effetto.className = "success-effect";

  for (let i = 0; i < 22; i++) {
    const particella = document.createElement("span");
    particella.style.setProperty("--x", `${Math.random() * 220 - 110}px`);
    particella.style.setProperty("--y", `${Math.random() * -180 - 40}px`);
    particella.style.setProperty("--delay", `${Math.random() * 0.18}s`);
    effetto.appendChild(particella);
  }

  document.body.appendChild(effetto);

  setTimeout(() => {
    effetto.remove();
  }, 900);
}

function controllaRisposta(buttonCliccato, opzioneScelta, opzioni) {
  if (STATO.rispostaBloccata) {
    return;
  }

  STATO.rispostaBloccata = true;

  const buttons = [...document.querySelectorAll(".option-button")];

  buttons.forEach((button, indice) => {
    const opzione = opzioni[indice];

    if (opzione.corretta) {
      button.classList.add("correct");
    }

    if (button === buttonCliccato && !opzioneScelta.corretta) {
      button.classList.add("wrong");
    }
  });

  if (opzioneScelta.corretta) {
    STATO.punteggio += 1;
    document.querySelector(".quiz-card")?.classList.add("correct-glow");
    effettoRispostaCorretta();
  } else {
    buttonCliccato.classList.add("shake");
  }

  const domanda = STATO.domandeQuiz[STATO.indiceDomanda];
  const spiegazione = testoSpiegazione(domanda);

  const spiegazioneBox = document.getElementById("spiegazioneBox");
  spiegazioneBox.classList.remove("hidden");
  spiegazioneBox.innerHTML = spiegazione
    ? `<strong>Spiegazione:</strong><br>${spiegazione}`
    : `<strong>Spiegazione:</strong><br>Nessuna spiegazione disponibile per questa domanda.`;

  document.getElementById("prossimaDomandaBtn").classList.remove("hidden");
}

function prossimaDomanda() {
  STATO.indiceDomanda += 1;

  if (STATO.indiceDomanda >= STATO.domandeQuiz.length) {
    mostraRisultatoFinale();
    return;
  }

  mostraDomanda();
}

function mostraRisultatoFinale() {
  document.getElementById("areaQuiz").innerHTML = "";

  const totale = STATO.domandeQuiz.length;
  const punteggio = STATO.punteggio;
  const percentuale = Math.round((punteggio / totale) * 100);

  let giudizio = "Da rivedere";
  if (percentuale >= 95) giudizio = "Eccellente";
  else if (percentuale >= 90) giudizio = "Ottimo";
  else if (percentuale >= 80) giudizio = "Buono";
  else if (percentuale >= 70) giudizio = "Discreto";
  else if (percentuale >= 60) giudizio = "Sufficiente";

  document.getElementById("risultatoFinale").innerHTML = `
    <div class="result-box">
      <h2>Risultato finale</h2>
      <p><strong>${punteggio}/${totale}</strong> risposte corrette</p>
      <p>${percentuale}% - ${giudizio}</p>
      <button onclick="avviaQuiz()">Genera nuovo test</button>
    </div>
  `;
}

async function caricaDatabase() {
  try {
    const risposta = await fetch("database_quiz.json?versione=" + Date.now());
    STATO.domande = await risposta.json();

    if (!Array.isArray(STATO.domande)) {
      throw new Error("Il database_quiz.json deve contenere una lista di domande.");
    }

    aggiornaContatori();
    popolaFiltri();

  } catch (errore) {
    document.getElementById("areaQuiz").innerHTML = `
      <div class="empty-box">
        Errore nel caricamento del database: ${errore.message}
      </div>
    `;
  }
}

document.addEventListener("DOMContentLoaded", caricaDatabase);
'''

NUOVO_STYLE_CSS = r'''
* {
  box-sizing: border-box;
}

:root {
  --bg-main: #07111f;
  --bg-panel: rgba(12, 23, 40, 0.88);
  --bg-panel-2: rgba(17, 31, 52, 0.92);
  --line: rgba(90, 170, 255, 0.22);
  --text-main: #e8f1ff;
  --text-soft: #9fb4d6;
  --blue: #4aa3ff;
  --cyan: #1fe0ff;
  --green: #17d98f;
  --red: #ff5d73;
  --yellow: #ffda66;
  --shadow: 0 18px 50px rgba(0, 0, 0, 0.35);
}

body {
  margin: 0;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: var(--text-main);
  background:
    radial-gradient(circle at top left, rgba(38, 92, 170, 0.25), transparent 30%),
    radial-gradient(circle at top right, rgba(0, 224, 255, 0.14), transparent 28%),
    linear-gradient(180deg, #040b15 0%, #07111f 45%, #09182a 100%);
  min-height: 100vh;
}

.header {
  position: relative;
  overflow: hidden;
  padding: 20px 14px 18px;
  text-align: center;
  border-bottom: 1px solid var(--line);
  background:
    linear-gradient(135deg, rgba(10, 25, 48, 0.96), rgba(8, 18, 34, 0.96));
}

.header::before {
  content: "";
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, transparent 0%, rgba(31, 224, 255, 0.08) 50%, transparent 100%);
  pointer-events: none;
}

.header h1 {
  margin: 0 0 6px;
  font-size: 1.65rem;
  letter-spacing: 0.4px;
  color: #ffffff;
  text-shadow: 0 0 18px rgba(74, 163, 255, 0.24);
}

.header p {
  margin: 0;
  color: var(--text-soft);
  font-size: 0.95rem;
}

.container {
  max-width: 1120px;
  margin: 0 auto;
  padding: 14px 14px 50px;
}

.total-counter,
.controls,
.quiz-card,
.result-box,
.empty-box,
.counter-card {
  background: var(--bg-panel);
  border: 1px solid var(--line);
  box-shadow: var(--shadow);
  backdrop-filter: blur(8px);
}

.total-counter {
  border-radius: 18px;
  padding: 12px 16px;
  margin-bottom: 10px;
  text-align: left;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.total-counter span {
  color: var(--text-soft);
  font-size: 0.92rem;
}

.total-counter strong {
  font-size: 1.9rem;
  display: block;
  color: #ffffff;
  text-shadow: 0 0 20px rgba(31, 224, 255, 0.24);
}

.counter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 8px;
  margin-bottom: 12px;
}

.counter-card {
  border-radius: 14px;
  padding: 10px 12px;
  background: var(--bg-panel-2);
}

.counter-card strong {
  display: block;
  margin-bottom: 3px;
  color: #ffffff;
  font-size: 0.92rem;
}

.counter-card span {
  color: var(--cyan);
  font-weight: 800;
}

.controls {
  border-radius: 18px;
  padding: 12px;
  margin-bottom: 14px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 10px;
  align-items: end;
}

label {
  display: grid;
  gap: 5px;
  font-weight: 700;
  color: var(--text-main);
  font-size: 0.92rem;
}

select,
button {
  border: 1px solid rgba(90, 170, 255, 0.18);
  border-radius: 13px;
  padding: 11px 12px;
  font-size: 0.98rem;
}

select {
  background: #0d1b2d;
  color: var(--text-main);
}

button {
  background: linear-gradient(135deg, var(--blue), #2568ff);
  color: white;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 10px 25px rgba(37, 104, 255, 0.25);
}

button:hover {
  filter: brightness(1.07);
}

button.secondary {
  margin-top: 16px;
  background: linear-gradient(135deg, #12213f, #0d1629);
}

.quiz-card,
.result-box,
.empty-box {
  border-radius: 22px;
  padding: 18px;
}

.quiz-card.correct-glow {
  animation: cardSuccess 0.8s ease;
}

.quiz-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.progress {
  font-weight: 900;
  color: var(--cyan);
  background: rgba(31, 224, 255, 0.1);
  border: 1px solid rgba(31, 224, 255, 0.25);
  border-radius: 999px;
  padding: 6px 11px;
  white-space: nowrap;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 6px;
}

.meta span {
  background: rgba(74, 163, 255, 0.12);
  color: #d9ecff;
  border: 1px solid rgba(74, 163, 255, 0.2);
  border-radius: 999px;
  padding: 5px 9px;
  font-size: 0.85rem;
  font-weight: 700;
}

.quiz-card h2 {
  margin: 0 0 14px;
  line-height: 1.38;
  color: #ffffff;
  font-size: 1.18rem;
}

.question-image {
  display: block;
  max-width: min(460px, 100%);
  margin: 10px auto 16px;
  border-radius: 14px;
  background: white;
  border: 1px solid rgba(90, 170, 255, 0.25);
}

.options {
  display: grid;
  gap: 10px;
}

.option-button {
  background: #0d1b2d;
  color: var(--text-main);
  text-align: left;
  display: grid;
  gap: 8px;
  border: 1px solid rgba(90, 170, 255, 0.18);
  transition:
    transform 0.15s ease,
    border-color 0.15s ease,
    box-shadow 0.15s ease,
    background 0.15s ease;
}

.option-button:hover {
  transform: translateY(-1px);
  border-color: rgba(31, 224, 255, 0.5);
  box-shadow: 0 10px 28px rgba(31, 224, 255, 0.08);
}

.option-button.correct {
  background: rgba(23, 217, 143, 0.16);
  border-color: rgba(23, 217, 143, 0.85);
  box-shadow:
    0 0 0 2px rgba(23, 217, 143, 0.16),
    0 0 28px rgba(23, 217, 143, 0.22);
  animation: correctPulse 0.65s ease;
}

.option-button.wrong {
  background: rgba(255, 93, 115, 0.16);
  border-color: rgba(255, 93, 115, 0.75);
}

.option-button.shake {
  animation: shake 0.35s ease;
}

.visual-option {
  min-height: 120px;
  align-items: center;
  justify-items: center;
  text-align: center;
}

.option-image {
  max-width: min(260px, 100%);
  max-height: 180px;
  object-fit: contain;
  border-radius: 12px;
  border: 1px solid rgba(90, 170, 255, 0.22);
  background: white;
  padding: 4px;
}

.option-text {
  color: var(--text-main);
  font-size: 0.95rem;
}

.explanation {
  margin-top: 16px;
  padding: 14px;
  border-radius: 14px;
  background: rgba(255, 218, 102, 0.1);
  border: 1px solid rgba(255, 218, 102, 0.24);
  color: #fff3c5;
  line-height: 1.5;
}

.hidden {
  display: none;
}

.result-box {
  text-align: center;
}

.back-link {
  display: inline-block;
  margin-bottom: 12px;
  color: var(--cyan);
  text-decoration: none;
  font-weight: 800;
}

.back-link:hover {
  text-decoration: underline;
}

.success-effect {
  position: fixed;
  left: 50%;
  top: 52%;
  width: 1px;
  height: 1px;
  z-index: 9999;
  pointer-events: none;
}

.success-effect span {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--green);
  box-shadow: 0 0 14px rgba(23, 217, 143, 0.9);
  animation: particle 0.85s ease-out forwards;
  animation-delay: var(--delay);
}

@keyframes particle {
  from {
    transform: translate(0, 0) scale(1);
    opacity: 1;
  }

  to {
    transform: translate(var(--x), var(--y)) scale(0.3);
    opacity: 0;
  }
}

@keyframes correctPulse {
  0% {
    transform: scale(1);
  }

  45% {
    transform: scale(1.025);
  }

  100% {
    transform: scale(1);
  }
}

@keyframes cardSuccess {
  0% {
    box-shadow: var(--shadow);
  }

  45% {
    box-shadow:
      var(--shadow),
      0 0 42px rgba(23, 217, 143, 0.32);
  }

  100% {
    box-shadow: var(--shadow);
  }
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }

  25% {
    transform: translateX(-6px);
  }

  50% {
    transform: translateX(6px);
  }

  75% {
    transform: translateX(-4px);
  }
}

@media (min-width: 720px) {
  .options:has(.visual-option) {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 600px) {
  .quiz-top-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .meta {
    justify-content: flex-start;
  }

  .total-counter {
    align-items: flex-start;
    flex-direction: column;
  }
}
'''

def sostituisci_blocco(nome_blocco, nuovo_contenuto, testo):
    pattern = rf"{nome_blocco} = r'''\n.*?\n'''"
    sostituzione = f"{nome_blocco} = r'''\n{nuovo_contenuto.strip()}\n'''"

    nuovo_testo, numero_sostituzioni = re.subn(
        pattern,
        sostituzione,
        testo,
        flags=re.DOTALL
    )

    if numero_sostituzioni != 1:
        raise SystemExit(f"ERRORE: impossibile aggiornare il blocco {nome_blocco}.")

    return nuovo_testo

def main():
    if not SCRIPT_PATH.exists():
        raise SystemExit("ERRORE: scripts/rigenera_demo_separate.py non trovato.")

    testo = SCRIPT_PATH.read_text(encoding="utf-8")
    testo = sostituisci_blocco("APP_JS", NUOVO_APP_JS, testo)
    testo = sostituisci_blocco("STYLE_CSS", NUOVO_STYLE_CSS, testo)

    SCRIPT_PATH.write_text(testo, encoding="utf-8")

    print("OK: interfaccia demo aggiornata nel generatore.")
    print("Correzioni applicate:")
    print("- effetti grafici risposta corretta/sbagliata ripristinati")
    print("- parte superiore resa più compatta")
    print("- numero domande dinamico, Logica visiva può arrivare a 40")
    print("- opzioni con immagini ripristinate per Logica visiva")

if __name__ == "__main__":
    main()
