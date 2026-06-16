
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
