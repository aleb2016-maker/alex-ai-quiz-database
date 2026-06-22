(function () {
  "use strict";

  let quizCorrente = {
    domande: [],
    indice: 0,
    punteggio: 0,
    risposto: false
  };

  const profiliDocumento = {
    sport: {
      nome: "Sport e allenamento",
      icona: "🏃",
      classe: "theme-sport",
      rami: ["preparazione", "attività principale", "recupero", "mobilità", "controllo"],
      parole: ["allenamento", "camminata", "bicicletta", "nuoto", "riscaldamento", "riposo", "flessibilità", "equilibrio", "defaticamento", "cardio"],
      domandaStudio: "Quale funzione ha questa fase dentro la scheda di allenamento?"
    },

    curriculum: {
      nome: "Curriculum vitae",
      icona: "👤",
      classe: "theme-cv",
      rami: ["profilo", "esperienze", "competenze", "formazione", "obiettivi"],
      parole: ["curriculum", "esperienza", "competenze", "formazione", "istruzione", "lavoro", "profilo", "cv", "stage", "azienda"],
      domandaStudio: "Che cosa comunica questa parte del curriculum a chi lo legge?"
    },

    personale: {
      nome: "Documento personale",
      icona: "📄",
      classe: "theme-personal",
      rami: ["dati principali", "scadenze", "informazioni utili", "avvisi", "azioni da fare"],
      parole: ["documento", "carta", "codice fiscale", "residenza", "scadenza", "numero", "tessera", "certificato", "anagrafica"],
      domandaStudio: "Quale informazione importante devo ricordare da questa parte del documento?"
    },

    aziendale: {
      nome: "Documento aziendale",
      icona: "🏢",
      classe: "theme-business",
      rami: ["obiettivi", "processi", "responsabilità", "rischi", "procedure"],
      parole: ["azienda", "procedura", "processo", "cliente", "responsabile", "rischio", "sicurezza", "report", "obiettivo", "attività"],
      domandaStudio: "Quale ruolo ha questa parte dentro l’organizzazione del lavoro?"
    },

    storia: {
      nome: "Storia o racconto",
      icona: "📚",
      classe: "theme-story",
      rami: ["personaggi", "ambientazione", "problema", "svolta", "finale"],
      parole: ["racconto", "storia", "personaggio", "capitolo", "protagonista", "villaggio", "viaggio", "finale", "scena"],
      domandaStudio: "Che funzione narrativa ha questa parte della storia?"
    },

    poesia: {
      nome: "Poesia",
      icona: "🪶",
      classe: "theme-poetry",
      rami: ["tema", "immagini poetiche", "emozioni", "ritmo", "significato"],
      parole: ["poesia", "verso", "strofa", "rima", "metafora", "immagine", "emozione", "silenzio", "cuore", "vento"],
      domandaStudio: "Che effetto espressivo produce questa parte della poesia?"
    },

    hobby: {
      nome: "Tempo libero, hobby o progetto",
      icona: "🎨",
      classe: "theme-hobby",
      rami: ["attività", "materiali", "passaggi", "obiettivi", "risultato finale"],
      parole: ["hobby", "progetto", "tempo libero", "materiali", "costruire", "creare", "disegno", "musica", "gioco", "ricetta"],
      domandaStudio: "A cosa serve questa parte nello sviluppo dell’attività o del progetto?"
    }
  };

  function normalizzaTesto(testo) {
    return String(testo || "")
      .replace(/\r/g, "\n")
      .replace(/riscaldamen\s*\n?\s*to/gi, "riscaldamento")
      .replace(/riscaldame\s*\n?\s*nto/gi, "riscaldamento")
      .replace(/\briscaldamen\b/gi, "riscaldamento")
      .replace(/defaticamen\s*\n?\s*to/gi, "defaticamento")
      .replace(/\bdefaticamen\b/gi, "defaticamento")
      .replace(/camminat\s*\n?\s*a/gi, "camminata")
      .replace(/\bcamminat\b/gi, "camminata")
      .replace(/biciclett\s*\n?\s*a/gi, "bicicletta")
      .replace(/equilibri\s*\n?\s*o/gi, "equilibrio")
      .replace(/flessibilit\s*\n?\s*[àa]/gi, "flessibilità")
      .replace(/mobilit\s*\n?\s*[àa]/gi, "mobilità")
      .replace(/\n\s*,\s*/g, ", ")
      .replace(/\n\s*o\s+/gi, " o ")
      .replace(/[ \t]+/g, " ")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
  }

  function escapeHtml(valore) {
    return String(valore || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function leggiTesto() {
    const input = document.getElementById("documentoInput");
    return input ? input.value : "";
  }

  function areaOutput() {
    return document.getElementById("output");
  }

  function riconosciTema(testo) {
    const testoNormale = normalizzaTesto(testo).toLowerCase();

    let migliore = "hobby";
    let punteggioMigliore = -1;

    Object.entries(profiliDocumento).forEach(function ([chiave, profilo]) {
      let punteggio = 0;

      profilo.parole.forEach(function (parola) {
        if (testoNormale.includes(parola)) {
          punteggio += 1;
        }
      });

      if (punteggio > punteggioMigliore) {
        migliore = chiave;
        punteggioMigliore = punteggio;
      }
    });

    return profiliDocumento[migliore];
  }

  function righeUtili(testo) {
    return normalizzaTesto(testo)
      .split("\n")
      .map(function (riga) {
        return riga
          .replace(/^[-•–]\s*/g, "")
          .replace(/\s+/g, " ")
          .trim();
      })
      .filter(function (riga) {
        return riga.length > 3;
      });
  }

  function spezzaInBlocchi(testo) {
    const righe = righeUtili(testo);

    const blocchi = [];

    righe.forEach(function (riga) {
      riga
        .replace(/\s+(?=\d+\s*(minuti|minuto|serie|ripetizioni)\b)/gi, "\n")
        .replace(/\s+(?=riposo\b)/gi, "\n")
        .replace(/\s+(?=recupero\b)/gi, "\n")
        .split("\n")
        .map(function (pezzo) {
          return pezzo.trim();
        })
        .filter(Boolean)
        .forEach(function (pezzo) {
          blocchi.push(pezzo);
        });
    });

    if (!blocchi.length) {
      return [normalizzaTesto(testo).slice(0, 220)];
    }

    return blocchi.slice(0, 12);
  }

  function scegliTitoloDaRamo(ramo, blocco, profilo) {
    const testo = blocco.toLowerCase();

    if (profilo.classe === "theme-sport") {
      if (/riscaldamento/.test(testo)) return "Riscaldamento";
      if (/camminata|bicicletta|nuoto|corsa|cardio/.test(testo)) return "Cardio leggero";
      if (/riposo|recupero/.test(testo)) return "Recupero";
      if (/flessibilit|stretching|mobilità|mobilita/.test(testo)) return "Flessibilità";
      if (/equilibrio/.test(testo)) return "Equilibrio";
      if (/defaticamento|relax/.test(testo)) return "Defaticamento";
    }

    return ramo.charAt(0).toUpperCase() + ramo.slice(1);
  }

  function creaDescrizione(ramo, blocco, profilo) {
    const testo = blocco.toLowerCase();

    if (profilo.classe === "theme-sport") {
      if (/riscaldamento/.test(testo)) return "Prepara corpo, respiro e articolazioni prima della parte principale.";
      if (/camminata|bicicletta|nuoto|corsa|cardio/.test(testo)) return "Allena resistenza e continuità con uno sforzo aerobico moderato.";
      if (/riposo|recupero/.test(testo)) return "Permette di abbassare il ritmo e ripartire meglio nel blocco successivo.";
      if (/flessibilit|stretching|mobilità|mobilita/.test(testo)) return "Migliora mobilità, scioltezza e libertà di movimento.";
      if (/equilibrio/.test(testo)) return "Allena stabilità, postura e controllo del corpo.";
      if (/defaticamento|relax/.test(testo)) return "Riduce gradualmente lo sforzo e accompagna il corpo verso il recupero.";
    }

    if (profilo.classe === "theme-cv") {
      return "Evidenzia un elemento utile per presentare profilo, competenze o percorso della persona.";
    }

    if (profilo.classe === "theme-personal") {
      return "Contiene un’informazione da leggere con attenzione perché può servire per riconoscere dati, scadenze o azioni importanti.";
    }

    if (profilo.classe === "theme-business") {
      return "Descrive un punto utile per capire obiettivi, responsabilità, processo o rischio operativo.";
    }

    if (profilo.classe === "theme-story") {
      return "Aiuta a seguire lo sviluppo narrativo, collegando personaggi, situazione e avanzamento della storia.";
    }

    if (profilo.classe === "theme-poetry") {
      return "Mette in evidenza immagini, emozioni o significati che danno forza espressiva al testo.";
    }

    return "Descrive un passaggio utile per capire attività, materiali, obiettivo o risultato del progetto.";
  }

  function creaCards(testo) {
    const profilo = riconosciTema(testo);
    const blocchi = spezzaInBlocchi(testo);

    const cards = blocchi.map(function (blocco, indice) {
      const ramo = profilo.rami[indice % profilo.rami.length];

      return {
        numero: indice + 1,
        profilo: profilo,
        ramo: ramo,
        titolo: scegliTitoloDaRamo(ramo, blocco, profilo),
        descrizione: creaDescrizione(ramo, blocco, profilo),
        originale: blocco
      };
    });

    return {
      profilo: profilo,
      cards: cards
    };
  }

  function mostraErrore(titolo, testo) {
    areaOutput().innerHTML = `
      <section class="output-card">
        <span class="pill">Errore</span>
        <h2>${escapeHtml(titolo)}</h2>
        <p>${escapeHtml(testo)}</p>
      </section>
    `;
  }

  function generaRiassunto() {
    const testo = leggiTesto();

    if (!testo.trim()) {
      mostraErrore("Documento mancante", "Incolla o carica prima un documento.");
      return;
    }

    const risultato = creaCards(testo);
    const profilo = risultato.profilo;
    const cards = risultato.cards;

    areaOutput().innerHTML = `
      <section class="output-card ${profilo.classe}">
        <span class="pill">${profilo.icona} ${escapeHtml(profilo.nome)}</span>
        <h2>Riassunto documento</h2>
        <p>
          Il testo è stato riconosciuto come <strong>${escapeHtml(profilo.nome)}</strong>.
          Sono stati individuati <strong>${cards.length}</strong> blocchi principali.
        </p>

        <h3>Struttura riconosciuta</h3>
        <ol>
          ${cards.map(function (card) {
            return `<li><strong>${escapeHtml(card.titolo)}</strong>: ${escapeHtml(card.descrizione)}</li>`;
          }).join("")}
        </ol>

        <h3>Obiettivo del documento</h3>
        <p>
          Trasformare il contenuto in materiale chiaro per studio, presentazione,
          ripasso, test interattivi e card visive.
        </p>
      </section>
    `;
  }

  function generaCardVisive() {
    const testo = leggiTesto();

    if (!textExists(testo)) {
      mostraErrore("Documento mancante", "Incolla o carica prima un documento.");
      return;
    }

    const risultato = creaCards(testo);
    const profilo = risultato.profilo;
    const cards = risultato.cards;

    areaOutput().innerHTML = `
      <section class="output-card ${profilo.classe}">
        <span class="pill">${profilo.icona} ${escapeHtml(profilo.nome)}</span>
        <h2>Card generate: ${cards.length}</h2>
        <p>Ogni blocco del documento è stato trasformato in una card visiva coerente con il tema.</p>

        <div class="cards-grid">
          ${cards.map(function (card) {
            return `
              <article class="universal-card ${profilo.classe}">
                <div class="icon">${profilo.icona}</div>
                <span class="badge">${escapeHtml(card.ramo)}</span>
                <h3>${card.numero}. ${escapeHtml(card.titolo)}</h3>
                <p>${escapeHtml(card.descrizione)}</p>
                <div class="originale">Dal testo: ${escapeHtml(card.originale)}</div>
              </article>
            `;
          }).join("")}
        </div>
      </section>
    `;
  }

  function textExists(testo) {
    return String(testo || "").trim().length > 0;
  }

  function mescola(array) {
    const copia = array.slice();

    for (let i = copia.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      const tmp = copia[i];
      copia[i] = copia[j];
      copia[j] = tmp;
    }

    return copia;
  }

  function creaDistrattoriForti(card, cards) {
    const altri = cards.filter(function (altra) {
      return altra.numero !== card.numero;
    });

    const daAltriBlocchi = altri.slice(0, 3).map(function (altra) {
      return {
        testo: `${altra.descrizione} Però questa risposta sposta il focus sul blocco "${altra.titolo}", non su quello richiesto.`,
        corretta: false
      };
    });

    const genericiForti = [
      {
        testo: "Riconosce una funzione vicina, ma confonde il ruolo del blocco con una fase diversa del documento.",
        corretta: false
      },
      {
        testo: "Coglie una parte del significato, ma attribuisce al blocco un obiettivo secondario invece di quello principale.",
        corretta: false
      },
      {
        testo: "Interpreta il contenuto in modo plausibile, ma non rispetta il punto specifico evidenziato nel testo.",
        corretta: false
      }
    ];

    return daAltriBlocchi.concat(genericiForti).slice(0, 3);
  }

  function creaQuiz() {
    const testo = leggiTesto();

    if (!textExists(testo)) {
      mostraErrore("Documento mancante", "Incolla o carica prima un documento.");
      return null;
    }

    const risultato = creaCards(testo);
    const cards = risultato.cards.slice(0, 10);

    const domande = cards.map(function (card) {
      const corretta = {
        testo: card.descrizione,
        corretta: true
      };

      const opzioni = mescola([corretta].concat(creaDistrattoriForti(card, cards)));

      return {
        domanda: `Nel blocco "${card.originale}", quale interpretazione è più corretta?`,
        spiegazione: `La risposta corretta è collegata al ramo "${card.ramo}" e alla funzione specifica del blocco.`,
        opzioni: opzioni
      };
    });

    return {
      profilo: risultato.profilo,
      domande: domande
    };
  }

  function generaTest() {
    const quiz = creaQuiz();

    if (!quiz) {
      return;
    }

    quizCorrente = {
      domande: quiz.domande,
      indice: 0,
      punteggio: 0,
      risposto: false,
      profilo: quiz.profilo
    };

    areaOutput().innerHTML = `
      <section class="output-card ${quiz.profilo.classe}">
        <span class="pill">${quiz.profilo.icona} Test interattivo</span>
        <h2>Test generato dal documento</h2>
        <p>
          Il test è pronto. Le risposte corrette non sono visibili:
          scegli una risposta e poi vai avanti.
        </p>

        <button id="btnAvviaQuiz" class="quiz-start-button" type="button">
          Inizia test
        </button>

        <div id="quizBox"></div>
      </section>
    `;

    document.getElementById("btnAvviaQuiz").addEventListener("click", mostraDomandaQuiz);
  }

  function mostraDomandaQuiz() {
    const quizBox = document.getElementById("quizBox");
    const domanda = quizCorrente.domande[quizCorrente.indice];
    const totale = quizCorrente.domande.length;

    quizCorrente.risposto = false;

    quizBox.innerHTML = `
      <div class="quiz-panel">
        <div class="quiz-progress">
          Domanda ${quizCorrente.indice + 1} di ${totale}
          · Punteggio: ${quizCorrente.punteggio}/${totale}
        </div>

        <h3>${escapeHtml(domanda.domanda)}</h3>

        <div class="quiz-options">
          ${domanda.opzioni.map(function (opzione, indice) {
            const lettera = String.fromCharCode(65 + indice);

            return `
              <button
                type="button"
                class="quiz-option"
                data-corretta="${opzione.corretta ? "si" : "no"}"
              >
                <strong>${lettera}.</strong> ${escapeHtml(opzione.testo)}
              </button>
            `;
          }).join("")}
        </div>

        <div id="quizFeedback"></div>
      </div>
    `;

    Array.from(document.querySelectorAll(".quiz-option")).forEach(function (bottone) {
      bottone.addEventListener("click", function () {
        gestisciRisposta(bottone);
      });
    });
  }

  function gestisciRisposta(bottoneScelto) {
    if (quizCorrente.risposto) {
      return;
    }

    quizCorrente.risposto = true;

    const corretta = bottoneScelto.dataset.corretta === "si";
    const domanda = quizCorrente.domande[quizCorrente.indice];

    if (corretta) {
      quizCorrente.punteggio += 1;
    }

    Array.from(document.querySelectorAll(".quiz-option")).forEach(function (bottone) {
      bottone.disabled = true;

      if (bottone.dataset.corretta === "si") {
        bottone.classList.add("correct");
      }

      if (bottone === bottoneScelto && !corretta) {
        bottone.classList.add("wrong");
      }
    });

    const ultima = quizCorrente.indice >= quizCorrente.domande.length - 1;
    const feedback = document.getElementById("quizFeedback");

    feedback.innerHTML = `
      <div class="${corretta ? "feedback-ok" : "feedback-ko"}">
        <strong>${corretta ? "Risposta corretta." : "Risposta sbagliata."}</strong>
        <p>${escapeHtml(domanda.spiegazione)}</p>
      </div>

      <button id="btnQuizNext" class="quiz-next-button" type="button">
        ${ultima ? "Vedi risultato finale" : "Prossima domanda"}
      </button>
    `;

    document.getElementById("btnQuizNext").addEventListener("click", function () {
      if (ultima) {
        mostraRisultatoQuiz();
      } else {
        quizCorrente.indice += 1;
        mostraDomandaQuiz();
      }
    });
  }

  function mostraRisultatoQuiz() {
    const quizBox = document.getElementById("quizBox");
    const totale = quizCorrente.domande.length;
    const percentuale = Math.round((quizCorrente.punteggio / totale) * 100);

    quizBox.innerHTML = `
      <div class="quiz-panel">
        <h3>Risultato finale</h3>
        <p class="quiz-final-score">${quizCorrente.punteggio}/${totale} corrette · ${percentuale}%</p>
        <button id="btnRiprovaQuiz" class="quiz-start-button" type="button">Ripeti test</button>
      </div>
    `;

    document.getElementById("btnRiprovaQuiz").addEventListener("click", function () {
      quizCorrente.indice = 0;
      quizCorrente.punteggio = 0;
      quizCorrente.domande = mescola(quizCorrente.domande);
      mostraDomandaQuiz();
    });
  }

  function generaDomandeStudio() {
    const testo = leggiTesto();

    if (!textExists(testo)) {
      mostraErrore("Documento mancante", "Incolla o carica prima un documento.");
      return;
    }

    const risultato = creaCards(testo);
    const profilo = risultato.profilo;
    const cards = risultato.cards;

    areaOutput().innerHTML = `
      <section class="output-card ${profilo.classe}">
        <span class="pill">${profilo.icona} Domande studio</span>
        <h2>Domande di studio generate</h2>
        <p>Domande utili per ripassare il documento in modo ragionato.</p>

        <div class="study-grid">
          ${cards.map(function (card) {
            return `
              <article class="study-card">
                <span class="badge">${escapeHtml(card.ramo)}</span>
                <h3>${escapeHtml(card.titolo)}</h3>
                <p class="study-question">${escapeHtml(profilo.domandaStudio)}</p>
                <p class="study-answer">${escapeHtml(card.descrizione)}</p>
                <p class="study-extra">
                  Rileggi il blocco originale e prova a spiegare con parole tue
                  perché questa parte è importante.
                </p>
                <div class="originale">Dal testo: ${escapeHtml(card.originale)}</div>
              </article>
            `;
          }).join("")}
        </div>
      </section>
    `;
  }

  function caricaFile(evento) {
    const file = evento.target.files && evento.target.files[0];

    if (!file) return;

    if (/\.pdf$/i.test(file.name)) {
      alert("Questa pagina di test universale legge TXT. Il parser PDF verrà collegato nel blocco successivo.");
      return;
    }

    const reader = new FileReader();

    reader.onload = function () {
      document.getElementById("documentoInput").value = String(reader.result || "");
    };

    reader.readAsText(file);
  }

  function avvia() {
    document.getElementById("btnFile").addEventListener("click", function () {
      document.getElementById("fileInput").click();
    });

    document.getElementById("fileInput").addEventListener("change", caricaFile);
    document.getElementById("btnRiassunto").addEventListener("click", generaRiassunto);
    document.getElementById("btnCard").addEventListener("click", generaCardVisive);
    document.getElementById("btnTest").addEventListener("click", generaTest);
    document.getElementById("btnStudio").addEventListener("click", generaDomandeStudio);
  }

  document.addEventListener("DOMContentLoaded", avvia);

  window.universalDocumentLearningEngine = {
    riconosciTema,
    creaCards,
    generaRiassunto,
    generaCardVisive,
    generaTest,
    generaDomandeStudio
  };
})();
