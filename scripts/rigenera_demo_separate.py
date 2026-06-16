import json
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
    "logica_numerica": "Logica",
    "logica_verbale": "Logica",
    "ragionamento_astratto": "Logica",
    "ragionamento_critico": "Logica",
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

        domanda["_materia_demo"] = nome_materia
        domanda["_file_origine"] = str(path.relative_to(ROOT))

        if nome_materia == "Logica":
            domanda["materia"] = "Logica"
            domanda["categoria"] = "logica"
        elif nome_materia == "Logica visiva":
            domanda["materia"] = "Logica visiva"
            domanda["categoria"] = "logica_visiva"
        else:
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

function effettoRispostaCorretta(elementoPartenza) {
  const rettangolo = elementoPartenza.getBoundingClientRect();

  const origineX = rettangolo.left + rettangolo.width / 2;
  const origineY = rettangolo.top + rettangolo.height / 2;

  const canvas = document.createElement("canvas");
  canvas.className = "confetti-canvas";
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  canvas.style.position = "fixed";
  canvas.style.left = "0";
  canvas.style.top = "0";
  canvas.style.width = "100vw";
  canvas.style.height = "100vh";
  canvas.style.zIndex = "9999";
  canvas.style.pointerEvents = "none";

  document.body.appendChild(canvas);

  const ctx = canvas.getContext("2d");

  const colori = [
    "#17d98f",
    "#1fe0ff",
    "#4aa3ff",
    "#ffda66",
    "#ff5d73",
    "#ffffff",
    "#b388ff",
    "#ff8a00",
    "#ff4fd8",
    "#7cff6b"
  ];

  const coriandoli = [];
  const quantita = 180;

  for (let i = 0; i < quantita; i++) {
    const lato = Math.random() < 0.5 ? -1 : 1;

    const velocitaLaterale = lato * (180 + Math.random() * 760);
    const velocitaVerticale = -(520 + Math.random() * 760);

    coriandoli.push({
      x: origineX + (Math.random() * 80 - 40),
      y: origineY + (Math.random() * 36 - 18),
      vx: velocitaLaterale,
      vy: velocitaVerticale,
      gravita: 720 + Math.random() * 420,
      resistenza: 0.992 + Math.random() * 0.004,
      larghezza: 10 + Math.random() * 16,
      altezza: 7 + Math.random() * 13,
      rotazione: Math.random() * Math.PI * 2,
      velocitaRotazione: (Math.random() * 10 - 5),
      colore: colori[Math.floor(Math.random() * colori.length)],
      vita: 0,
      durata: 3.8 + Math.random() * 1.5,
      forma: Math.random() < 0.72 ? "rettangolo" : "cerchio",
      oscillazione: Math.random() * Math.PI * 2,
      oscillazioneVelocita: 2 + Math.random() * 4
    });
  }

  let ultimoTempo = performance.now();

  function anima(tempoCorrente) {
    const deltaSecondi = Math.min((tempoCorrente - ultimoTempo) / 1000, 0.033);
    ultimoTempo = tempoCorrente;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    let ancoraVisibili = false;

    for (const pezzo of coriandoli) {
      pezzo.vita += deltaSecondi;

      pezzo.vx *= pezzo.resistenza;
      pezzo.vy += pezzo.gravita * deltaSecondi;

      const movimentoOndulato = Math.sin(
        pezzo.vita * pezzo.oscillazioneVelocita + pezzo.oscillazione
      ) * 38;

      pezzo.x += (pezzo.vx * deltaSecondi) + movimentoOndulato * deltaSecondi;
      pezzo.y += pezzo.vy * deltaSecondi;
      pezzo.rotazione += pezzo.velocitaRotazione * deltaSecondi;

      const parteFinaleVita = Math.max(0, (pezzo.vita - pezzo.durata * 0.72) / (pezzo.durata * 0.28));
      const uscitaBassa = Math.max(0, (pezzo.y - canvas.height * 0.72) / (canvas.height * 0.35));
      const dissolvenza = Math.max(parteFinaleVita, uscitaBassa);
      const opacita = Math.max(0, 1 - dissolvenza);

      if (
        opacita > 0 &&
        pezzo.y < canvas.height + 160 &&
        pezzo.x > -220 &&
        pezzo.x < canvas.width + 220
      ) {
        ancoraVisibili = true;
      }

      ctx.save();
      ctx.globalAlpha = opacita;
      ctx.translate(pezzo.x, pezzo.y);
      ctx.rotate(pezzo.rotazione);
      ctx.fillStyle = pezzo.colore;

      if (pezzo.forma === "cerchio") {
        ctx.beginPath();
        ctx.arc(0, 0, pezzo.larghezza * 0.45, 0, Math.PI * 2);
        ctx.fill();
      } else {
        ctx.fillRect(
          -pezzo.larghezza / 2,
          -pezzo.altezza / 2,
          pezzo.larghezza,
          pezzo.altezza
        );
      }

      ctx.restore();
    }

    if (ancoraVisibili) {
      requestAnimationFrame(anima);
    } else {
      canvas.remove();
    }
  }

  requestAnimationFrame(anima);
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
    effettoRispostaCorretta(buttonCliccato);
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


STYLE_CSS = r'''
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
  width: 1px;
  height: 1px;
  z-index: 9999;
  pointer-events: none;
  overflow: visible;
}

.success-effect span {
  position: absolute;
  left: 0;
  top: 0;
  width: var(--size);
  height: calc(var(--size) * 0.62);
  background: var(--color);
  opacity: 1;
  border-radius: 3px;
  box-shadow:
    0 0 10px rgba(255, 255, 255, 0.38),
    0 0 18px rgba(31, 224, 255, 0.12);
  will-change: transform, opacity;
  animation: confettiSoftBurst var(--dur) forwards;
  animation-delay: var(--delay);
}

.success-effect span:nth-child(3n) {
  border-radius: 999px;
}

.success-effect span:nth-child(4n) {
  height: var(--size);
}

.success-effect span:nth-child(5n) {
  width: calc(var(--size) * 0.65);
  height: calc(var(--size) * 1.15);
}

@keyframes confettiSoftBurst {
  0% {
    transform: translate3d(0, 0, 0) rotate(0deg) scale(0.72);
    opacity: 1;
    animation-timing-function: cubic-bezier(0.18, 0.88, 0.25, 1);
  }

  18% {
    transform: translate3d(calc(var(--open-x) * 0.55), var(--up-y), 0) rotate(calc(var(--rot-mid) * 0.45)) scale(1.08);
    opacity: 1;
    animation-timing-function: cubic-bezier(0.22, 0.72, 0.24, 1);
  }

  42% {
    transform: translate3d(var(--open-x), calc(var(--up-y) * 0.72), 0) rotate(var(--rot-mid)) scale(1);
    opacity: 1;
    animation-timing-function: cubic-bezier(0.28, 0.02, 0.36, 1);
  }

  78% {
    transform: translate3d(calc(var(--fall-x) * 0.82), calc(var(--fall-y) * 0.72), 0) rotate(calc(var(--rot-end) * 0.82)) scale(0.94);
    opacity: 1;
    animation-timing-function: cubic-bezier(0.2, 0.0, 0.2, 1);
  }

  100% {
    transform: translate3d(var(--fall-x), var(--fall-y), 0) rotate(var(--rot-end)) scale(0.76);
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


def crea_demo(titolo, sottotitolo, cartella, domande):
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

    :root {
      --bg-main: #07111f;
      --panel: rgba(12, 23, 40, 0.88);
      --line: rgba(90, 170, 255, 0.22);
      --text-main: #e8f1ff;
      --text-soft: #9fb4d6;
      --blue: #4aa3ff;
      --cyan: #1fe0ff;
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

    header {
      padding: 42px 18px 34px;
      text-align: center;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(135deg, rgba(10, 25, 48, 0.96), rgba(8, 18, 34, 0.96));
    }

    header h1 {
      margin: 0 0 10px;
      font-size: 2.2rem;
      color: #ffffff;
    }

    header p {
      margin: 0;
      color: var(--text-soft);
    }

    main {
      max-width: 980px;
      margin: 0 auto;
      padding: 28px 16px 60px;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 18px;
    }

    .card {
      display: block;
      text-decoration: none;
      color: inherit;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 26px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(8px);
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .card:hover {
      transform: translateY(-4px);
      box-shadow: 0 20px 42px rgba(0, 0, 0, 0.45);
    }

    .card h2 {
      margin: 0 0 10px;
      color: #ffffff;
    }

    .card p {
      margin: 0 0 18px;
      color: var(--text-soft);
      line-height: 1.5;
    }

    .button {
      display: inline-block;
      background: linear-gradient(135deg, var(--blue), #2568ff);
      color: white;
      font-weight: 800;
      border-radius: 999px;
      padding: 11px 16px;
      box-shadow: 0 10px 25px rgba(37, 104, 255, 0.25);
    }
  </style>
</head>
<body>
  <header>
    <h1>Demo Quiz</h1>
    <p>Ambiente demo separato: Quiz AI e Scienze hanno pagine indipendenti e contatori separati.</p>
  </header>

  <main>
    <div class="grid">
      <a class="card" href="../demo-ai/index.html">
        <h2>Demo Quiz AI</h2>
        <p>AI, Informatica, Matematica, Inglese, Logica e Logica visiva.</p>
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
        titolo="Demo Quiz AI",
        sottotitolo="AI, Informatica, Matematica, Inglese, Logica e Logica visiva.",
        cartella=DEMO_AI_DIR,
        domande=domande_quiz_ai,
    )

    crea_demo(
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
