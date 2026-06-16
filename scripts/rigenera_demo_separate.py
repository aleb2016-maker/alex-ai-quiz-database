import json
import shutil
from pathlib import Path
from collections import Counter

ROOT = Path(".").resolve()

DATA_DIR = ROOT / "data"
DIST_DIR = ROOT / "dist"
DEMO_MENU_DIR = ROOT / "demo"
DEMO_AI_DIR = ROOT / "demo-ai"
DEMO_SCIENZE_DIR = ROOT / "demo-scienze"

QUIZ_AI_FILES = {
    "ai": "AI",
    "informatica": "Informatica",
    "matematica": "Matematica",
    "inglese": "Inglese",
    "logica_numerica": "Logica numerica",
    "logica_verbale": "Logica verbale",
    "ragionamento_astratto": "Ragionamento astratto",
    "ragionamento_critico": "Ragionamento critico",
    "logica_visiva": "Logica visiva",
}

SCIENZE_FILES = {
    "scienze": "Scienze generali",
    "scienze_generali": "Scienze generali",
    "biologia": "Biologia",
    "chimica": "Chimica",
    "fisica": "Fisica",
    "fisica_quantistica": "Fisica quantistica",
}


def leggi_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def scrivi_json(path, dati):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(dati, file, ensure_ascii=False, indent=2)


def sembra_domanda(elemento):
    if not isinstance(elemento, dict):
        return False

    campi_domanda = {"domanda", "question", "testo", "titolo"}
    campi_opzioni = {"opzioni", "options", "risposte", "answers"}

    ha_domanda = any(campo in elemento for campo in campi_domanda)
    ha_opzioni = any(campo in elemento for campo in campi_opzioni)

    return ha_domanda and ha_opzioni


def estrai_lista_domande(contenuto):
    if isinstance(contenuto, list):
        return [elemento for elemento in contenuto if sembra_domanda(elemento)]

    if isinstance(contenuto, dict):
        for chiave in ["domande", "questions", "items", "quiz"]:
            valore = contenuto.get(chiave)
            if isinstance(valore, list):
                return [elemento for elemento in valore if sembra_domanda(elemento)]

        valori = list(contenuto.values())
        if valori and all(isinstance(valore, dict) for valore in valori):
            return [elemento for elemento in valori if sembra_domanda(elemento)]

    return []


def nome_file_senza_estensione(path):
    return path.stem.lower().strip()


def prepara_domande_da_file(path, nome_materia):
    contenuto = leggi_json(path)
    domande_originali = estrai_lista_domande(contenuto)

    domande_preparate = []

    for domanda_originale in domande_originali:
        domanda = dict(domanda_originale)

        domanda.setdefault("_materia_demo", nome_materia)
        domanda.setdefault("_file_origine", str(path.relative_to(ROOT)))

        if not domanda.get("materia"):
            domanda["materia"] = nome_materia

        if not domanda.get("categoria"):
            domanda["categoria"] = nome_materia

        domande_preparate.append(domanda)

    return domande_preparate


def raccogli_domande():
    if not DATA_DIR.exists():
        raise SystemExit("ERRORE: cartella data/ non trovata. Devi lanciare lo script dalla root del progetto.")

    domande_quiz_ai = []
    domande_scienze = []

    conteggio_file = Counter()

    for path in sorted(DATA_DIR.rglob("*.json")):
        parti_path = {parte.lower() for parte in path.parts}

        if "traduzioni" in parti_path:
            continue

        file_stem = nome_file_senza_estensione(path)

        if file_stem in QUIZ_AI_FILES:
            nome_materia = QUIZ_AI_FILES[file_stem]
            domande = prepara_domande_da_file(path, nome_materia)
            domande_quiz_ai.extend(domande)
            conteggio_file[str(path.relative_to(ROOT))] = len(domande)

        elif file_stem in SCIENZE_FILES:
            nome_materia = SCIENZE_FILES[file_stem]
            domande = prepara_domande_da_file(path, nome_materia)
            domande_scienze.extend(domande)
            conteggio_file[str(path.relative_to(ROOT))] = len(domande)

    return domande_quiz_ai, domande_scienze, conteggio_file


APP_JS = r'''
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
  return domanda.immagine_domanda || domanda.immagine || domanda.image || domanda.image_path || "";
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
      if (typeof opzione === "object" && opzione !== null) {
        return {
          indiceOriginale: indice,
          letteraOriginale: String.fromCharCode(65 + indice),
          testo:
            opzione.testo ||
            opzione.text ||
            opzione.risposta ||
            opzione.value ||
            opzione.label ||
            "",
          immagine:
            opzione.immagine ||
            opzione.image ||
            opzione.image_path ||
            "",
          correttaEsplicita:
            opzione.corretta === true ||
            opzione.correct === true ||
            opzione.is_correct === true
        };
      }

      return {
        indiceOriginale: indice,
        letteraOriginale: String.fromCharCode(65 + indice),
        testo: String(opzione),
        immagine: "",
        correttaEsplicita: false
      };
    });
  }

  if (!Array.isArray(opzioniGrezze) && typeof opzioniGrezze === "object" && opzioniGrezze !== null) {
    opzioni = Object.entries(opzioniGrezze).map(([lettera, valore], indice) => {
      if (typeof valore === "object" && valore !== null) {
        return {
          indiceOriginale: indice,
          letteraOriginale: lettera.toUpperCase(),
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
            "",
          correttaEsplicita:
            valore.corretta === true ||
            valore.correct === true ||
            valore.is_correct === true
        };
      }

      return {
        indiceOriginale: indice,
        letteraOriginale: lettera.toUpperCase(),
        testo: String(valore),
        immagine: "",
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
        <span>${conteggio} domande</span>
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
}

function avviaQuiz() {
  const materiaScelta = document.getElementById("materiaSelect").value;
  const livelloScelto = document.getElementById("livelloSelect").value;
  const numeroDomande = Number(document.getElementById("numeroDomandeSelect").value);

  STATO.domandeFiltrate = STATO.domande.filter((domanda) => {
    const materiaOk =
      materiaScelta === "tutte" ||
      materiaDomanda(domanda) === materiaScelta;

    const livelloOk =
      livelloScelto === "tutti" ||
      livelloDomanda(domanda) === livelloScelto;

    return materiaOk && livelloOk;
  });

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
      <div class="progress">
        Domanda ${STATO.indiceDomanda + 1}/${STATO.domandeQuiz.length}
      </div>

      <div class="meta">
        <span>${materiaDomanda(domanda)}</span>
        <span>${livelloDomanda(domanda)}</span>
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
    button.className = "option-button";

    const immagineOpzione = correggiPercorsoImmagine(opzione.immagine);

    button.innerHTML = `
      <span>${opzione.testo}</span>
      ${
        immagineOpzione
          ? `<img class="option-image" src="${immagineOpzione}" alt="Figura opzione">`
          : ""
      }
    `;

    button.addEventListener("click", () => controllaRisposta(button, opzione, opzioni));

    opzioniBox.appendChild(button);
  });
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


STYLE_CSS = r'''
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #f3f5f8;
  color: #172033;
}

.header {
  padding: 32px 18px;
  text-align: center;
  background: linear-gradient(135deg, #12213f, #254a8b);
  color: white;
}

.header h1 {
  margin: 0 0 8px;
  font-size: 2rem;
}

.header p {
  margin: 0;
  opacity: 0.9;
}

.container {
  max-width: 1080px;
  margin: 0 auto;
  padding: 22px 16px 50px;
}

.total-counter {
  background: white;
  border-radius: 18px;
  padding: 22px;
  margin-bottom: 18px;
  box-shadow: 0 8px 26px rgba(20, 30, 55, 0.08);
  text-align: center;
}

.total-counter strong {
  font-size: 2.4rem;
  display: block;
}

.counter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 12px;
  margin-bottom: 22px;
}

.counter-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 8px 22px rgba(20, 30, 55, 0.07);
}

.counter-card strong {
  display: block;
  margin-bottom: 6px;
}

.counter-card span {
  color: #566177;
}

.controls {
  background: white;
  border-radius: 18px;
  padding: 18px;
  margin-bottom: 22px;
  box-shadow: 0 8px 26px rgba(20, 30, 55, 0.08);
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 14px;
  align-items: end;
}

label {
  display: grid;
  gap: 6px;
  font-weight: 700;
}

select,
button {
  border: none;
  border-radius: 12px;
  padding: 13px 14px;
  font-size: 1rem;
}

select {
  background: #eef2f7;
}

button {
  background: #1b66d2;
  color: white;
  font-weight: 800;
  cursor: pointer;
}

button:hover {
  filter: brightness(0.95);
}

button.secondary {
  margin-top: 18px;
  background: #172033;
}

.quiz-card,
.result-box,
.empty-box {
  background: white;
  border-radius: 22px;
  padding: 24px;
  box-shadow: 0 10px 30px rgba(20, 30, 55, 0.1);
}

.progress {
  font-weight: 800;
  color: #1b66d2;
  margin-bottom: 10px;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
}

.meta span {
  background: #eef2f7;
  color: #34405a;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 0.9rem;
  font-weight: 700;
}

.quiz-card h2 {
  margin: 0 0 18px;
  line-height: 1.35;
}

.question-image {
  display: block;
  max-width: min(520px, 100%);
  margin: 12px auto 20px;
  border-radius: 14px;
  background: #f8fafc;
  border: 1px solid #dce3ee;
}

.options {
  display: grid;
  gap: 12px;
}

.option-button {
  background: #eef2f7;
  color: #172033;
  text-align: left;
  display: grid;
  gap: 10px;
  border: 2px solid transparent;
}

.option-button.correct {
  background: #d8f7df;
  border-color: #20a447;
}

.option-button.wrong {
  background: #ffe0e0;
  border-color: #d83232;
}

.option-image {
  max-width: 210px;
  border-radius: 12px;
  border: 1px solid #d8dfe9;
  background: white;
}

.explanation {
  margin-top: 18px;
  padding: 16px;
  border-radius: 14px;
  background: #fff7da;
  color: #3e3210;
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
  margin-bottom: 18px;
  color: #1b66d2;
  text-decoration: none;
  font-weight: 800;
}
'''


def crea_demo(nome_demo, titolo, sottotitolo, cartella, domande):
    cartella.mkdir(parents=True, exist_ok=True)

    scrivi_json(cartella / "database_quiz.json", domande)

    html = f'''<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{titolo}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header class="header">
    <h1>{titolo}</h1>
    <p>{sottotitolo}</p>
  </header>

  <main class="container">
    <a class="back-link" href="../demo/index.html">← Torna al menu demo</a>

    <section class="total-counter">
      <span>Domande disponibili in questa demo</span>
      <strong id="totaleDomande">0</strong>
    </section>

    <section id="conteggioMaterie" class="counter-grid"></section>

    <section class="controls">
      <label>
        Materia
        <select id="materiaSelect"></select>
      </label>

      <label>
        Livello
        <select id="livelloSelect"></select>
      </label>

      <label>
        Numero domande
        <select id="numeroDomandeSelect">
          <option value="10">10 domande</option>
          <option value="20">20 domande</option>
          <option value="30">30 domande</option>
        </select>
      </label>

      <button onclick="avviaQuiz()">Genera test</button>
    </section>

    <section id="areaQuiz"></section>
    <section id="risultatoFinale"></section>
  </main>

  <script src="app.js"></script>
</body>
</html>
'''

    (cartella / "index.html").write_text(html, encoding="utf-8")
    (cartella / "app.js").write_text(APP_JS, encoding="utf-8")
    (cartella / "style.css").write_text(STYLE_CSS, encoding="utf-8")


def crea_menu_demo():
    DEMO_MENU_DIR.mkdir(parents=True, exist_ok=True)

    html = '''<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Menu demo quiz</title>
  <style>
    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f3f5f8;
      color: #172033;
    }

    header {
      padding: 36px 18px;
      text-align: center;
      background: linear-gradient(135deg, #12213f, #254a8b);
      color: white;
    }

    header h1 {
      margin: 0 0 8px;
      font-size: 2rem;
    }

    main {
      max-width: 980px;
      margin: 0 auto;
      padding: 28px 16px 60px;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 18px;
    }

    .card {
      display: block;
      text-decoration: none;
      color: inherit;
      background: white;
      border-radius: 24px;
      padding: 26px;
      box-shadow: 0 10px 30px rgba(20, 30, 55, 0.1);
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .card:hover {
      transform: translateY(-3px);
      box-shadow: 0 14px 36px rgba(20, 30, 55, 0.14);
    }

    .card h2 {
      margin: 0 0 10px;
      color: #1b66d2;
    }

    .card p {
      margin: 0 0 18px;
      color: #566177;
      line-height: 1.5;
    }

    .button {
      display: inline-block;
      background: #1b66d2;
      color: white;
      font-weight: 800;
      border-radius: 999px;
      padding: 11px 16px;
    }
  </style>
</head>
<body>
  <header>
    <h1>Demo Quiz</h1>
    <p>Le sezioni sono ora separate: Quiz AI e Scienze hanno pagine e contatori indipendenti.</p>
  </header>

  <main>
    <div class="grid">
      <a class="card" href="../demo-ai/index.html">
        <h2>Demo Quiz AI</h2>
        <p>AI, Informatica, Matematica, Inglese, Logica testuale e Logica visiva.</p>
        <span class="button">Apri Quiz AI</span>
      </a>

      <a class="card" href="../demo-scienze/index.html">
        <h2>Demo Scienze</h2>
        <p>Scienze generali, Biologia, Chimica, Fisica e Fisica quantistica.</p>
        <span class="button">Apri Scienze</span>
      </a>
    </div>
  </main>
</body>
</html>
'''

    (DEMO_MENU_DIR / "index.html").write_text(html, encoding="utf-8")


def stampa_report(nome, domande):
    conteggio = Counter(domanda.get("_materia_demo", "Senza materia") for domanda in domande)

    print()
    print("=" * 70)
    print(nome)
    print("=" * 70)
    print(f"Totale: {len(domande)}")

    for materia, totale in sorted(conteggio.items()):
        print(f"- {materia}: {totale}")


def main():
    domande_quiz_ai, domande_scienze, conteggio_file = raccogli_domande()
    domande_totali = domande_quiz_ai + domande_scienze

    DIST_DIR.mkdir(parents=True, exist_ok=True)

    scrivi_json(DIST_DIR / "database_quiz_finale.json", domande_totali)

    crea_demo(
        nome_demo="Quiz AI",
        titolo="Demo Quiz AI",
        sottotitolo="AI, Informatica, Matematica, Inglese, Logica testuale e Logica visiva.",
        cartella=DEMO_AI_DIR,
        domande=domande_quiz_ai,
    )

    crea_demo(
        nome_demo="Scienze",
        titolo="Demo Scienze",
        sottotitolo="Scienze generali, Biologia, Chimica, Fisica e Fisica quantistica.",
        cartella=DEMO_SCIENZE_DIR,
        domande=domande_scienze,
    )

    crea_menu_demo()

    print()
    print("File sorgente letti:")
    for nome_file, totale in sorted(conteggio_file.items()):
        print(f"- {nome_file}: {totale}")

    stampa_report("DEMO QUIZ AI", domande_quiz_ai)
    stampa_report("DEMO SCIENZE", domande_scienze)
    stampa_report("DATABASE COMPLETO", domande_totali)

    print()
    print("=" * 70)
    print("CONTROLLO NUMERI ATTESI")
    print("=" * 70)

    controlli = [
        ("Quiz AI", len(domande_quiz_ai), 440),
        ("Scienze", len(domande_scienze), 200),
        ("Totale", len(domande_totali), 640),
    ]

    problemi = False

    for nome, valore, atteso in controlli:
        if valore < atteso:
            problemi = True
            print(f"ATTENZIONE: {nome} ha {valore} domande, ma ne erano attese almeno {atteso}.")
        else:
            print(f"OK: {nome} ha {valore} domande.")

    if problemi:
        print()
        print("Il problema NON è nella demo nuova: mancano ancora domande nei file data/ oppure i file hanno nomi diversi da quelli previsti.")
        print("Controlla i file dentro data/ e rilancia questo script.")
    else:
        print()
        print("OK: database e demo separate rigenerate correttamente.")


if __name__ == "__main__":
    main()
