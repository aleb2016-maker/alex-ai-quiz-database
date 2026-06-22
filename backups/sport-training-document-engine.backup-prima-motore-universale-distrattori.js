(function () {
  "use strict";

  let quizCorrente = {
    domande: [],
    indice: 0,
    punteggio: 0,
    risposto: false
  };

  function normalizzaTesto(testo) {
    return String(testo || "")
      .replace(/\r/g, "\n")
      .replace(/riscaldamen\s*\n?\s*to/gi, "riscaldamento")
      .replace(/riscaldame\s*\n?\s*nto/gi, "riscaldamento")
      .replace(/\briscaldamen\b/gi, "riscaldamento")
      .replace(/\briscaldame\b/gi, "riscaldamento")
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
      .replace(/\s+e\s+(\d+)\s+di\s+/gi, "\n$1 minuti di ")
      .replace(/[ \t]+/g, " ")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
  }

  function pulisciRiga(riga) {
    return String(riga || "")
      .replace(/^[-•–]\s*/g, "")
      .replace(/\s+/g, " ")
      .replace(/\s+,/g, ",")
      .trim();
  }

  function iniziaNuovoBlocco(riga) {
    return (
      /^\d+\s*(minuti|minuto|serie|ripetizioni)\b/i.test(riga) ||
      /^riposo\b/i.test(riga) ||
      /^recupero\b/i.test(riga) ||
      /^giorno\s+\d+/i.test(riga)
    );
  }

  function estraiBlocchi(testo) {
    const testoPulito = normalizzaTesto(testo);

    const righe = testoPulito
      .split("\n")
      .map(pulisciRiga)
      .filter(Boolean);

    const blocchi = [];
    let corrente = "";

    function salva() {
      const blocco = pulisciRiga(corrente);

      if (blocco) {
        blocchi.push(blocco);
      }

      corrente = "";
    }

    righe.forEach(function (riga) {
      if (iniziaNuovoBlocco(riga)) {
        salva();
        corrente = riga;
      } else if (corrente) {
        corrente += " " + riga;
      } else {
        corrente = riga;
      }
    });

    salva();

    const finali = [];

    blocchi.forEach(function (blocco) {
      blocco
        .replace(/\s+(?=\d+\s*(minuti|minuto|serie|ripetizioni)\b)/gi, "\n")
        .replace(/\s+(?=riposo\b)/gi, "\n")
        .replace(/\s+(?=recupero\b)/gi, "\n")
        .split("\n")
        .map(pulisciRiga)
        .filter(Boolean)
        .forEach(function (pezzo) {
          const p = pezzo.toLowerCase();

          const valido =
            /\d+\s*(minuti|minuto|serie|ripetizioni)/i.test(pezzo) ||
            /riposo|recupero|relax|camminata|bicicletta|nuoto|corsa|riscaldamento|defaticamento|flessibilit|equilibrio|stretching|mobilit|forza|cardio/.test(p);

          if (valido) {
            finali.push(pezzo);
          }
        });
    });

    const senzaDuplicatiConsecutivi = [];

    finali.forEach(function (blocco) {
      const ultimo = senzaDuplicatiConsecutivi[senzaDuplicatiConsecutivi.length - 1];

      if (ultimo && ultimo.toLowerCase() === blocco.toLowerCase()) {
        return;
      }

      senzaDuplicatiConsecutivi.push(blocco);
    });

    return senzaDuplicatiConsecutivi.slice(0, 20);
  }

  function classifica(blocco) {
    const t = blocco.toLowerCase();

    if (/riposo|recupero|relax/.test(t)) {
      return {
        titolo: "Recupero",
        badge: "Riposo",
        tipo: "riposo",
        descrizione: "Abbassa il ritmo e permette al corpo di recuperare prima del blocco successivo."
      };
    }

    if (/riscaldamento/.test(t)) {
      return {
        titolo: "Riscaldamento",
        badge: "Preparazione",
        tipo: "riscaldamento",
        descrizione: "Prepara muscoli, articolazioni e respiro prima della parte principale dell’allenamento."
      };
    }

    if (/defaticamento/.test(t)) {
      return {
        titolo: "Defaticamento",
        badge: "Chiusura",
        tipo: "defaticamento",
        descrizione: "Riduce gradualmente lo sforzo e aiuta il corpo a chiudere l’allenamento in modo controllato."
      };
    }

    if (/camminata|bicicletta|nuoto|corsa|cardio/.test(t)) {
      return {
        titolo: "Cardio leggero",
        badge: "Resistenza",
        tipo: "cardio",
        descrizione: "Allena la resistenza con un’attività aerobica semplice come camminata, bicicletta o nuoto."
      };
    }

    if (/flessibilit|stretching|mobilità|mobilita/.test(t)) {
      return {
        titolo: "Flessibilità",
        badge: "Mobilità",
        tipo: "flessibilita",
        descrizione: "Migliora mobilità, scioltezza e libertà di movimento."
      };
    }

    if (/equilibrio|postura|stabilit/.test(t)) {
      return {
        titolo: "Equilibrio",
        badge: "Controllo",
        tipo: "equilibrio",
        descrizione: "Migliora stabilità, postura e controllo del corpo."
      };
    }

    if (/forza|squat|plank|affondi|pesi|push/.test(t)) {
      return {
        titolo: "Forza",
        badge: "Potenziamento",
        tipo: "forza",
        descrizione: "Sviluppa forza, controllo muscolare e resistenza allo sforzo."
      };
    }

    return {
      titolo: "Blocco allenamento",
      badge: "Workout",
      tipo: "circuito",
      descrizione: "Organizza una parte pratica della scheda in una fase riconoscibile dell’allenamento."
    };
  }

  function estraiDurata(blocco) {
    const match = blocco.match(/(\d+)\s*(minuti|minuto|serie|ripetizioni)/i);
    return match ? match[1] + " " + match[2] : "";
  }

  function creaCard(blocco, indice) {
    const info = classifica(blocco);

    return {
      numero: indice + 1,
      titolo: info.titolo,
      badge: info.badge,
      tipo: info.tipo,
      durata: estraiDurata(blocco),
      descrizione: info.descrizione,
      originale: blocco
    };
  }

  function generaCards() {
    const input = document.getElementById("documentoInput");
    const testo = input ? input.value : "";
    return estraiBlocchi(testo).map(creaCard);
  }

  function icona(tipo) {
    const map = {
      cardio: "🚴‍♂️",
      riscaldamento: "🤸",
      riposo: "😴",
      defaticamento: "🌿",
      flessibilita: "🧘",
      equilibrio: "⚖️",
      forza: "🏋️",
      circuito: "🏃"
    };

    return map[tipo] || "🏃";
  }

  function escapeHtml(valore) {
    return String(valore || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function mescola(array) {
    const copia = array.slice();

    for (let indice = copia.length - 1; indice > 0; indice -= 1) {
      const casuale = Math.floor(Math.random() * (indice + 1));
      const temporaneo = copia[indice];
      copia[indice] = copia[casuale];
      copia[casuale] = temporaneo;
    }

    return copia;
  }

  function areaOutput() {
    return document.getElementById("output");
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
    const cards = generaCards();

    if (!cards.length) {
      mostraErrore("Riassunto non generato", "Non sono stati trovati blocchi di allenamento leggibili.");
      return;
    }

    const minutiTotali = cards.reduce(function (totale, card) {
      const numero = parseInt(card.durata, 10);
      return totale + (Number.isFinite(numero) ? numero : 0);
    }, 0);

    areaOutput().innerHTML = `
      <section class="output-card">
        <span class="pill">Riassunto</span>
        <h2>Riassunto scheda allenamento</h2>
        <p>
          La scheda contiene <strong>${cards.length}</strong> blocchi principali.
          ${minutiTotali ? `La durata totale indicata è di circa <strong>${minutiTotali} minuti</strong>.` : ""}
        </p>

        <h3>Struttura riconosciuta</h3>
        <ol>
          ${cards.map(function (card) {
            return `<li><strong>${escapeHtml(card.titolo)}</strong>${card.durata ? ` - ${escapeHtml(card.durata)}` : ""}</li>`;
          }).join("")}
        </ol>

        <h3>Obiettivo</h3>
        <p>
          Trasformare la scheda in una sequenza chiara: preparazione, lavoro cardio,
          recupero, mobilità, equilibrio e chiusura dell’allenamento.
        </p>
      </section>
    `;
  }

  function generaCardVisive() {
    const cards = generaCards();

    if (!cards.length) {
      mostraErrore("Card generate: 0", "Non sono stati trovati blocchi di allenamento leggibili.");
      return;
    }

    areaOutput().innerHTML = `
      <section class="output-card">
        <span class="pill">Card</span>
        <h2>Card allenamento generate: ${cards.length}</h2>
        <p>Ogni blocco della scheda è stato trasformato in una card visiva.</p>

        <div class="cards-grid">
          ${cards.map(function (card) {
            return `
              <article class="sport-card">
                <div class="icon">${icona(card.tipo)}</div>
                <span class="badge">${escapeHtml(card.badge)}</span>
                <h3>${card.numero}. ${escapeHtml(card.titolo)}</h3>
                ${card.durata ? `<div class="duration">${escapeHtml(card.durata)}</div>` : ""}
                <p>${escapeHtml(card.descrizione)}</p>
                <div class="originale">Dal testo: ${escapeHtml(card.originale)}</div>
              </article>
            `;
          }).join("")}
        </div>
      </section>
    `;
  }

  function creaDomandaQuiz(card, indice) {
    const banca = {
      riscaldamento: {
        domanda: "Qual è la funzione più corretta del riscaldamento in questa scheda?",
        corretta: "Preparare gradualmente muscoli, articolazioni e respiro prima della parte principale.",
        sbagliate: [
          "Aumentare subito l’intensità per trasformare il riscaldamento nella fase principale.",
          "Far recuperare completamente il corpo prima ancora di iniziare l’allenamento vero.",
          "Chiudere l’allenamento riportando il corpo lentamente a una condizione di riposo."
        ],
        spiegazione: "Il riscaldamento non è la parte più intensa e non è la chiusura: serve a preparare il corpo in modo progressivo."
      },

      cardio: {
        domanda: "Qual è l’obiettivo principale del blocco cardio leggero?",
        corretta: "Mantenere uno sforzo aerobico moderato per allenare resistenza e continuità.",
        sbagliate: [
          "Portare subito lo sforzo al massimo per lavorare soprattutto sulla forza esplosiva.",
          "Usare il movimento solo come recupero passivo, senza un vero lavoro di resistenza.",
          "Concentrarsi principalmente sulla mobilità articolare, lasciando in secondo piano il fiato."
        ],
        spiegazione: "Il cardio leggero lavora sulla continuità dello sforzo e sulla resistenza, non sulla forza massima o sul recupero passivo."
      },

      riposo: {
        domanda: "Perché nella scheda sono presenti fasi di riposo o recupero?",
        corretta: "Per far abbassare il ritmo e mantenere migliore qualità nei blocchi successivi.",
        sbagliate: [
          "Per interrompere del tutto la sequenza e rendere inutile il blocco successivo.",
          "Per sostituire il riscaldamento con una fase senza movimento prima dello sforzo.",
          "Per aumentare l’intensità accumulando più fatica tra una fase e l’altra."
        ],
        spiegazione: "Il recupero serve a gestire la fatica: non elimina l’allenamento e non aumenta l’intensità."
      },

      flessibilita: {
        domanda: "A cosa serve il blocco di flessibilità dentro la scheda?",
        corretta: "A migliorare mobilità, scioltezza e libertà di movimento.",
        sbagliate: [
          "A lavorare soprattutto sulla resistenza cardiovascolare con ritmo costante.",
          "A sostituire l’equilibrio allenando solo la stabilità su un appoggio.",
          "A chiudere lo sforzo come fase di defaticamento senza lavoro sulla mobilità."
        ],
        spiegazione: "La flessibilità riguarda mobilità e ampiezza del movimento, non cardio, equilibrio puro o semplice defaticamento."
      },

      equilibrio: {
        domanda: "Qual è lo scopo degli esercizi di equilibrio?",
        corretta: "Migliorare stabilità, postura e controllo del corpo durante il movimento.",
        sbagliate: [
          "Mantenere uno sforzo aerobico continuo per allenare soprattutto il fiato.",
          "Aumentare la mobilità articolare senza lavorare sul controllo della posizione.",
          "Far recuperare il corpo restando completamente fermi tra due blocchi intensi."
        ],
        spiegazione: "L’equilibrio lavora su stabilità e controllo: è diverso da cardio, flessibilità e riposo."
      },

      defaticamento: {
        domanda: "Perché il defaticamento viene inserito verso la fine?",
        corretta: "Per ridurre gradualmente lo sforzo e accompagnare il corpo verso il recupero.",
        sbagliate: [
          "Per preparare il corpo prima della parte più intensa dell’allenamento.",
          "Per sostituire il cardio mantenendo ancora alta l’intensità principale.",
          "Per eliminare il recupero e continuare ad accumulare fatica fino alla fine."
        ],
        spiegazione: "Il defaticamento è una chiusura progressiva: non è riscaldamento e non mantiene alta l’intensità."
      },

      forza: {
        domanda: "Qual è l’obiettivo principale di un blocco di forza?",
        corretta: "Sviluppare controllo muscolare, forza e capacità di sostenere lo sforzo.",
        sbagliate: [
          "Mantenere solo un ritmo aerobico leggero senza lavoro muscolare specifico.",
          "Migliorare esclusivamente la mobilità articolare senza stimolare la muscolatura.",
          "Far abbassare il ritmo come pausa completa tra due esercizi."
        ],
        spiegazione: "Il blocco di forza stimola i muscoli e il controllo dello sforzo, non è solo cardio, mobilità o pausa."
      },

      circuito: {
        domanda: "Che ruolo ha questo blocco nella struttura della scheda?",
        corretta: card.descrizione,
        sbagliate: [
          "Ha una funzione simile, ma serve soprattutto a cambiare fase senza un obiettivo preciso.",
          "Ha una funzione vicina, ma lavora più sul recupero che sull’attività indicata.",
          "Ha una funzione collegata, ma sostituisce la progressione invece di completarla."
        ],
        spiegazione: "Il blocco va interpretato in base alla sua funzione nella sequenza dell’allenamento."
      }
    };

    const modello = banca[card.tipo] || banca.circuito;

    const opzioni = mescola([
      { testo: modello.corretta, corretta: true },
      { testo: modello.sbagliate[0], corretta: false },
      { testo: modello.sbagliate[1], corretta: false },
      { testo: modello.sbagliate[2], corretta: false }
    ]);

    return {
      numero: indice + 1,
      titoloBlocco: card.titolo,
      domanda: modello.domanda,
      opzioni: opzioni,
      spiegazione: modello.spiegazione
    };
  }

  function creaQuizDaCards(cards) {
    const viste = new Set();

    const cardsUniche = cards.filter(function (card) {
      const chiave = card.tipo + "::" + card.titolo;

      if (viste.has(chiave)) {
        return false;
      }

      viste.add(chiave);
      return true;
    });

    return cardsUniche.slice(0, 10).map(creaDomandaQuiz);
  }

  function generaTest() {
    const cards = generaCards();

    if (!cards.length) {
      mostraErrore("Test non generato", "Non sono stati trovati blocchi di allenamento leggibili.");
      return;
    }

    quizCorrente = {
      domande: creaQuizDaCards(cards),
      indice: 0,
      punteggio: 0,
      risposto: false
    };

    areaOutput().innerHTML = `
      <section class="output-card">
        <span class="pill">Test interattivo</span>
        <h2>Test generato dalla scheda</h2>
        <p>
          Il test è pronto. Le risposte corrette non sono visibili:
          devi scegliere una risposta e poi andare avanti.
        </p>

        <button id="btnAvviaQuiz" class="quiz-start-button" type="button">
          Inizia test
        </button>

        <div id="quizBox"></div>
      </section>
    `;

    document.getElementById("btnAvviaQuiz").addEventListener("click", function () {
      mostraDomandaQuiz();
    });
  }

  function mostraDomandaQuiz() {
    const quizBox = document.getElementById("quizBox");

    if (!quizBox) {
      return;
    }

    const totale = quizCorrente.domande.length;
    const domanda = quizCorrente.domande[quizCorrente.indice];
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

    const feedback = document.getElementById("quizFeedback");
    const ultimaDomanda = quizCorrente.indice >= quizCorrente.domande.length - 1;

    feedback.innerHTML = `
      <div class="${corretta ? "feedback-ok" : "feedback-ko"}">
        <strong>${corretta ? "Risposta corretta." : "Risposta sbagliata."}</strong>
        <p>${escapeHtml(domanda.spiegazione)}</p>
      </div>

      <button id="btnQuizNext" class="quiz-next-button" type="button">
        ${ultimaDomanda ? "Vedi risultato finale" : "Prossima domanda"}
      </button>
    `;

    document.getElementById("btnQuizNext").addEventListener("click", function () {
      if (ultimaDomanda) {
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
    const voto = Math.round((quizCorrente.punteggio / totale) * 100);

    let giudizio = "Da ripassare";

    if (voto >= 90) {
      giudizio = "Ottimo lavoro";
    } else if (voto >= 70) {
      giudizio = "Buon risultato";
    } else if (voto >= 60) {
      giudizio = "Sufficiente";
    }

    quizBox.innerHTML = `
      <div class="quiz-panel">
        <h3>Risultato finale</h3>
        <p class="quiz-final-score">
          ${quizCorrente.punteggio}/${totale} risposte corrette · ${voto}%
        </p>
        <p><strong>${giudizio}</strong></p>

        <button id="btnRiprovaQuiz" class="quiz-start-button" type="button">
          Ripeti test
        </button>
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
    const cards = generaCards();

    if (!cards.length) {
      mostraErrore("Domande studio non generate", "Non sono stati trovati blocchi di allenamento leggibili.");
      return;
    }

    areaOutput().innerHTML = `
      <section class="output-card">
        <span class="pill">Studio</span>
        <h2>Domande di studio generate</h2>
        <p>
          Queste domande servono per ripassare la scheda in modo ragionato,
          non come test a scelta multipla.
        </p>

        <div class="study-grid">
          ${cards.map(function (card) {
            return `
              <article class="study-card">
                <span class="badge">${escapeHtml(card.badge)}</span>
                <h3>${escapeHtml(card.titolo)}</h3>

                <p class="study-question">
                  Quale ruolo ha questa fase dentro la scheda di allenamento?
                </p>

                <p class="study-answer">
                  ${escapeHtml(card.descrizione)}
                </p>

                <p class="study-extra">
                  Rileggi il blocco originale e prova a spiegare con parole tue
                  perché è stato inserito in quel punto della sequenza.
                </p>

                <div class="originale">
                  Dal testo: ${escapeHtml(card.originale)}
                </div>
              </article>
            `;
          }).join("")}
        </div>
      </section>
    `;
  }

  function caricaFile(evento) {
    const file = evento.target.files && evento.target.files[0];

    if (!file) {
      return;
    }

    if (/\.pdf$/i.test(file.name)) {
      alert("Per ora questa pagina di test legge direttamente TXT. Per PDF serve collegare il parser PDF della demo principale.");
      return;
    }

    const reader = new FileReader();

    reader.onload = function () {
      document.getElementById("documentoInput").value = String(reader.result || "");
    };

    reader.readAsText(file);
  }

  function aggiungiStiliQuiz() {
    if (document.getElementById("quiz-interattivo-style")) {
      return;
    }

    const style = document.createElement("style");
    style.id = "quiz-interattivo-style";
    style.textContent = `
      .quiz-start-button,
      .quiz-next-button {
        margin-top: 18px;
        border: 0;
        border-radius: 999px;
        padding: 15px 24px;
        color: white;
        font-size: 18px;
        font-weight: 950;
        cursor: pointer;
        background: linear-gradient(135deg, #be123c, #9333ea);
        box-shadow: 0 16px 34px rgba(124, 58, 237, 0.34);
      }

      .quiz-panel {
        margin-top: 24px;
        padding: 24px;
        border-radius: 24px;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.14);
      }

      .quiz-progress {
        display: inline-block;
        margin-bottom: 16px;
        padding: 8px 13px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.13);
        font-weight: 950;
        color: #dbeafe;
      }

      .quiz-options {
        display: grid;
        gap: 14px;
        margin-top: 18px;
      }

      .quiz-option {
        width: 100%;
        min-height: 64px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 18px;
        padding: 16px;
        text-align: left;
        color: #f8fafc;
        font-size: 17px;
        font-weight: 850;
        cursor: pointer;
        background: rgba(15, 23, 42, 0.72);
      }

      .quiz-option.correct {
        background: rgba(22, 163, 74, 0.85);
      }

      .quiz-option.wrong {
        background: rgba(220, 38, 38, 0.85);
      }

      .feedback-ok,
      .feedback-ko {
        margin-top: 18px;
        padding: 16px;
        border-radius: 18px;
        font-weight: 850;
      }

      .feedback-ok {
        background: rgba(22, 163, 74, 0.22);
        border: 1px solid rgba(34, 197, 94, 0.55);
      }

      .feedback-ko {
        background: rgba(220, 38, 38, 0.22);
        border: 1px solid rgba(248, 113, 113, 0.55);
      }

      .quiz-final-score {
        font-size: 28px;
        font-weight: 950;
        color: #bae6fd;
      }

      .study-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 18px;
        margin-top: 24px;
      }

      .study-card {
        padding: 22px;
        border-radius: 24px;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.14);
      }

      .study-question {
        font-weight: 950;
        color: #bae6fd;
      }

      .study-answer {
        font-weight: 850;
      }

      .study-extra {
        color: #dbeafe;
        font-size: 15px;
      }
    `;

    document.head.appendChild(style);
  }

  function avvia() {
    aggiungiStiliQuiz();

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

  window.sportTrainingDocumentEngine = {
    normalizzaTesto,
    estraiBlocchi,
    generaRiassunto,
    generaCardVisive,
    generaTest,
    generaDomandeStudio
  };
})();
