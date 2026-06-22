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
    function testoBlocco(card) {
      return card.originale || card.titolo || "blocco della scheda";
    }

    const bancaForte = {
      riscaldamento: {
        domanda: `Nel blocco "${testoBlocco(card)}", quale interpretazione è più precisa?`,
        corretta: "È una fase di attivazione graduale: prepara corpo, respiro e articolazioni prima del lavoro principale.",
        sbagliate: [
          "È una fase iniziale di movimento leggero, ma serve soprattutto a far recuperare il corpo dopo uno sforzo già svolto.",
          "È una fase preparatoria, ma il suo scopo principale è aumentare subito l’intensità fino al picco dell’allenamento.",
          "È una fase simile alla mobilità, ma serve soprattutto ad allungare i movimenti senza preparare davvero lo sforzo successivo."
        ],
        spiegazione: "Il riscaldamento prepara gradualmente il corpo. I distrattori sono vicini, ma confondono il riscaldamento con recupero, picco di intensità o mobilità pura."
      },

      cardio: {
        domanda: `Nel blocco "${testoBlocco(card)}", quale obiettivo descrive meglio l’attività proposta?`,
        corretta: "Mantenere uno sforzo aerobico moderato e continuo per lavorare su resistenza e fiato.",
        sbagliate: [
          "Mantenere un movimento continuo, ma con l’obiettivo principale di recuperare energie tra due fasi intense.",
          "Mantenere un’attività leggera, ma concentrandosi soprattutto su mobilità articolare e ampiezza del movimento.",
          "Mantenere uno sforzo costante, ma puntando soprattutto sulla forza muscolare e non sulla resistenza."
        ],
        spiegazione: "Il blocco cardio lavora sulla resistenza aerobica. I distrattori restano plausibili, ma spostano l’obiettivo su recupero, mobilità o forza."
      },

      riposo: {
        domanda: `Nel blocco "${testoBlocco(card)}", qual è la funzione più corretta?`,
        corretta: "Permettere al corpo di abbassare il ritmo e mantenere qualità nei blocchi successivi.",
        sbagliate: [
          "Abbassare il ritmo, ma con lo scopo principale di sostituire il riscaldamento iniziale.",
          "Creare una pausa, ma per aumentare l’intensità complessiva accumulando più fatica.",
          "Interrompere la sequenza, ma rendendo meno importante il lavoro successivo della scheda."
        ],
        spiegazione: "Il recupero serve a gestire la fatica e a ripartire meglio, non a sostituire il riscaldamento o a rendere inutile il resto."
      },

      flessibilita: {
        domanda: `Nel blocco "${testoBlocco(card)}", quale funzione è più coerente con la scheda?`,
        corretta: "Migliorare mobilità, scioltezza e libertà di movimento.",
        sbagliate: [
          "Migliorare il movimento, ma con l’obiettivo principale di allenare il fiato in modo continuo.",
          "Lavorare sul controllo del corpo, ma concentrandosi soprattutto sulla stabilità e non sull’ampiezza del movimento.",
          "Ridurre gradualmente lo sforzo finale, ma senza un vero lavoro sulla mobilità articolare."
        ],
        spiegazione: "La flessibilità riguarda mobilità e scioltezza. I distrattori confondono questo blocco con cardio, equilibrio o defaticamento."
      },

      equilibrio: {
        domanda: `Nel blocco "${testoBlocco(card)}", quale risultato si vuole ottenere soprattutto?`,
        corretta: "Migliorare stabilità, postura e controllo del corpo.",
        sbagliate: [
          "Migliorare il controllo del corpo, ma lavorando soprattutto sulla resistenza del fiato.",
          "Migliorare il movimento, ma puntando principalmente su flessibilità e ampiezza articolare.",
          "Abbassare il ritmo dopo lo sforzo, usando l’esercizio come fase di recupero passivo."
        ],
        spiegazione: "L’equilibrio allena stabilità e controllo. I distrattori sono vicini, ma spostano il focus su cardio, flessibilità o recupero."
      },

      defaticamento: {
        domanda: `Nel blocco "${testoBlocco(card)}", perché questa fase è inserita verso la fine?`,
        corretta: "Per ridurre gradualmente lo sforzo e accompagnare il corpo verso il recupero.",
        sbagliate: [
          "Per preparare il corpo al lavoro principale, come se fosse una fase iniziale di attivazione.",
          "Per mantenere alto lo sforzo aerobico e continuare il blocco principale di resistenza.",
          "Per lavorare soprattutto su stabilità e postura, più che sulla chiusura graduale dello sforzo."
        ],
        spiegazione: "Il defaticamento chiude l’allenamento in modo progressivo. I distrattori lo confondono con riscaldamento, cardio o equilibrio."
      },

      forza: {
        domanda: `Nel blocco "${testoBlocco(card)}", qual è l’obiettivo più corretto?`,
        corretta: "Stimolare controllo muscolare, forza e capacità di sostenere lo sforzo.",
        sbagliate: [
          "Stimolare il corpo, ma lavorando soprattutto sulla resistenza aerobica continua.",
          "Controllare il movimento, ma puntando principalmente su mobilità e scioltezza articolare.",
          "Gestire la fatica, ma come pausa di recupero tra due blocchi più impegnativi."
        ],
        spiegazione: "La forza riguarda lavoro muscolare e controllo dello sforzo. I distrattori la confondono con cardio, mobilità o recupero."
      },

      circuito: {
        domanda: `Nel blocco "${testoBlocco(card)}", quale interpretazione è più adatta?`,
        corretta: card.descrizione,
        sbagliate: [
          "Ha una funzione vicina, ma serve soprattutto come passaggio di recupero tra due fasi.",
          "Ha una funzione simile, ma punta principalmente sulla mobilità invece che sul lavoro indicato.",
          "Ha una funzione collegata, ma modifica l’obiettivo della fase invece di completare la sequenza."
        ],
        spiegazione: "La risposta corretta mantiene il ruolo specifico del blocco dentro la scheda."
      }
    };

    const modello = bancaForte[card.tipo] || bancaForte.circuito;

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
