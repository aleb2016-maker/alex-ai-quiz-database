
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
