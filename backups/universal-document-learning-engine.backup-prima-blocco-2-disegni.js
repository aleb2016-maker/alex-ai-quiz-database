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
      parole: ["allenamento", "camminata", "bicicletta", "nuoto", "riscaldamento", "riposo", "flessibilità", "equilibrio", "defaticamento", "cardio"],
      sezioni: [
        {
          ramo: "preparazione",
          titolo: "Preparazione",
          parole: ["riscaldamento", "attivazione"],
          descrizione: "Prepara corpo, respiro e articolazioni prima della parte principale.",
          domandaStudio: "Perché questa fase va messa prima del lavoro principale?"
        },
        {
          ramo: "attività principale",
          titolo: "Attività principale",
          parole: ["camminata", "bicicletta", "nuoto", "corsa", "cardio"],
          descrizione: "Allena resistenza e continuità con uno sforzo aerobico moderato.",
          domandaStudio: "Quale capacità fisica viene allenata in questa fase?"
        },
        {
          ramo: "recupero",
          titolo: "Recupero",
          parole: ["riposo", "recupero", "relax"],
          descrizione: "Fa abbassare il ritmo e permette di ripartire meglio nel blocco successivo.",
          domandaStudio: "Perché il recupero aiuta a mantenere qualità nella scheda?"
        },
        {
          ramo: "mobilità",
          titolo: "Mobilità e flessibilità",
          parole: ["flessibilità", "mobilità", "stretching"],
          descrizione: "Migliora scioltezza, ampiezza del movimento e controllo articolare.",
          domandaStudio: "Che differenza c’è tra questa fase e il cardio?"
        },
        {
          ramo: "controllo",
          titolo: "Equilibrio e controllo",
          parole: ["equilibrio", "postura", "stabilità"],
          descrizione: "Allena stabilità, postura e controllo del corpo.",
          domandaStudio: "Quale controllo del corpo viene richiesto in questa fase?"
        }
      ]
    },

    curriculum: {
      nome: "Curriculum vitae",
      icona: "👤",
      classe: "theme-cv",
      parole: ["curriculum", "esperienza", "competenze", "formazione", "istruzione", "lavoro", "profilo", "cv", "stage", "azienda", "obiettivo"],
      sezioni: [
        {
          ramo: "profilo",
          titolo: "Profilo professionale",
          parole: ["sviluppatore", "profilo", "junior", "senior", "interesse", "mi occupo", "sono"],
          descrizione: "Presenta chi è la persona, il settore di interesse e la direzione professionale.",
          domandaStudio: "Che immagine professionale comunica questa parte?"
        },
        {
          ramo: "esperienze",
          titolo: "Esperienze e progetti",
          parole: ["esperienza", "progetti", "stage", "lavoro", "attività", "collaborazione"],
          descrizione: "Mostra attività concrete, progetti svolti o esperienze utili per valutare il percorso.",
          domandaStudio: "Quale esperienza concreta può interessare a un’azienda?"
        },
        {
          ramo: "competenze",
          titolo: "Competenze",
          parole: ["competenze", "skill", "strumenti", "github", "javascript", "python", "programmazione", "problem solving"],
          descrizione: "Raccoglie capacità, strumenti e conoscenze tecniche o trasversali.",
          domandaStudio: "Quali competenze emergono e come possono essere usate sul lavoro?"
        },
        {
          ramo: "formazione",
          titolo: "Formazione",
          parole: ["formazione", "diploma", "corso", "istruzione", "percorso", "studio"],
          descrizione: "Spiega il percorso di studio o aggiornamento che sostiene il profilo.",
          domandaStudio: "In che modo la formazione rafforza il profilo?"
        },
        {
          ramo: "obiettivo",
          titolo: "Obiettivo professionale",
          parole: ["obiettivo", "crescere", "entrare", "team", "ruolo", "full stack", "sviluppare"],
          descrizione: "Chiarisce dove vuole arrivare la persona e quale ruolo cerca.",
          domandaStudio: "Che direzione professionale viene dichiarata?"
        }
      ]
    },

    personale: {
      nome: "Documento personale",
      icona: "📄",
      classe: "theme-personal",
      parole: ["documento", "carta", "codice fiscale", "residenza", "scadenza", "numero", "tessera", "certificato", "anagrafica"],
      sezioni: [
        {
          ramo: "dati principali",
          titolo: "Dati principali",
          parole: ["nome", "cognome", "nato", "residenza", "indirizzo", "codice fiscale"],
          descrizione: "Contiene dati utili per identificare correttamente la persona o il documento.",
          domandaStudio: "Quali dati servono per riconoscere il documento?"
        },
        {
          ramo: "scadenze",
          titolo: "Scadenze",
          parole: ["scadenza", "valido", "validità", "rinnovo", "data"],
          descrizione: "Indica date importanti da controllare per evitare dimenticanze.",
          domandaStudio: "Quale scadenza va ricordata?"
        },
        {
          ramo: "azioni",
          titolo: "Azioni da fare",
          parole: ["fare", "presentare", "inviare", "portare", "richiedere", "consegnare"],
          descrizione: "Evidenzia un’azione pratica collegata al documento.",
          domandaStudio: "Che cosa bisogna fare dopo aver letto questa parte?"
        }
      ]
    },

    aziendale: {
      nome: "Documento aziendale",
      icona: "🏢",
      classe: "theme-business",
      parole: ["azienda", "procedura", "processo", "cliente", "responsabile", "rischio", "sicurezza", "report", "obiettivo", "attività"],
      sezioni: [
        {
          ramo: "obiettivo",
          titolo: "Obiettivo",
          parole: ["obiettivo", "scopo", "finalità", "risultato"],
          descrizione: "Spiega il risultato che il documento o la procedura vuole ottenere.",
          domandaStudio: "Qual è lo scopo operativo di questa parte?"
        },
        {
          ramo: "processo",
          titolo: "Processo",
          parole: ["processo", "procedura", "fase", "passaggio", "flusso"],
          descrizione: "Descrive come si svolge un’attività o una procedura aziendale.",
          domandaStudio: "Quale passaggio del processo viene spiegato?"
        },
        {
          ramo: "responsabilità",
          titolo: "Responsabilità",
          parole: ["responsabile", "ruolo", "team", "operatore", "referente"],
          descrizione: "Chiarisce chi deve occuparsi di una parte del lavoro.",
          domandaStudio: "Chi è coinvolto e con quale responsabilità?"
        },
        {
          ramo: "rischi",
          titolo: "Rischi e attenzione",
          parole: ["rischio", "sicurezza", "errore", "controllo", "attenzione", "problema"],
          descrizione: "Segnala elementi da controllare per ridurre errori o rischi.",
          domandaStudio: "Quale rischio bisogna prevenire?"
        }
      ]
    },

    storia: {
      nome: "Storia o racconto",
      icona: "📚",
      classe: "theme-story",
      parole: ["racconto", "storia", "personaggio", "capitolo", "protagonista", "villaggio", "viaggio", "finale", "scena"],
      sezioni: [
        {
          ramo: "personaggi",
          titolo: "Personaggi",
          parole: ["personaggio", "protagonista", "ragazzo", "ragazza", "uomo", "donna", "bambino"],
          descrizione: "Introduce chi agisce nella storia e quale ruolo ha.",
          domandaStudio: "Che ruolo ha questo personaggio nella storia?"
        },
        {
          ramo: "ambientazione",
          titolo: "Ambientazione",
          parole: ["luogo", "città", "villaggio", "bosco", "casa", "strada", "notte", "giorno"],
          descrizione: "Costruisce il luogo o il contesto in cui avviene la scena.",
          domandaStudio: "Che atmosfera crea questa ambientazione?"
        },
        {
          ramo: "problema",
          titolo: "Problema narrativo",
          parole: ["problema", "pericolo", "paura", "ostacolo", "conflitto", "difficoltà"],
          descrizione: "Crea tensione e dà alla storia qualcosa da risolvere.",
          domandaStudio: "Quale problema fa andare avanti la storia?"
        },
        {
          ramo: "svolta",
          titolo: "Svolta",
          parole: ["scoprì", "capì", "decise", "all’improvviso", "ma", "però"],
          descrizione: "Cambia la direzione della storia e porta verso una conseguenza.",
          domandaStudio: "Che cosa cambia in questo punto?"
        }
      ]
    },

    poesia: {
      nome: "Poesia",
      icona: "🪶",
      classe: "theme-poetry",
      parole: ["poesia", "verso", "strofa", "rima", "metafora", "immagine", "emozione", "silenzio", "cuore", "vento"],
      sezioni: [
        {
          ramo: "tema",
          titolo: "Tema centrale",
          parole: ["amore", "tempo", "vita", "notte", "silenzio", "ricordo", "paura"],
          descrizione: "Fa emergere l’idea o il sentimento principale del testo.",
          domandaStudio: "Quale tema centrale emerge da questi versi?"
        },
        {
          ramo: "immagini",
          titolo: "Immagini poetiche",
          parole: ["vento", "mare", "luce", "ombra", "cielo", "cuore", "strada"],
          descrizione: "Usa immagini per rendere più forte l’emozione o il significato.",
          domandaStudio: "Quale immagine rende più espressiva questa parte?"
        },
        {
          ramo: "emozione",
          titolo: "Emozione",
          parole: ["tristezza", "gioia", "paura", "speranza", "dolore", "serenità"],
          descrizione: "Trasmette uno stato d’animo e orienta il tono della poesia.",
          domandaStudio: "Quale emozione comunica questa parte?"
        }
      ]
    },

    hobby: {
      nome: "Tempo libero, hobby o progetto",
      icona: "🎨",
      classe: "theme-hobby",
      parole: ["hobby", "progetto", "tempo libero", "materiali", "costruire", "creare", "disegno", "musica", "gioco", "ricetta"],
      sezioni: [
        {
          ramo: "attività",
          titolo: "Attività",
          parole: ["attività", "fare", "creare", "costruire", "giocare", "disegnare"],
          descrizione: "Spiega che cosa si vuole realizzare o praticare.",
          domandaStudio: "Qual è l’attività principale descritta?"
        },
        {
          ramo: "materiali",
          titolo: "Materiali o strumenti",
          parole: ["materiali", "strumenti", "oggetti", "file", "ingredienti"],
          descrizione: "Indica cosa serve per svolgere l’attività.",
          domandaStudio: "Quali strumenti o materiali servono?"
        },
        {
          ramo: "passaggi",
          titolo: "Passaggi",
          parole: ["passaggio", "prima", "poi", "dopo", "procedura", "fase"],
          descrizione: "Mostra l’ordine delle azioni da seguire.",
          domandaStudio: "Qual è il passaggio più importante?"
        },
        {
          ramo: "risultato",
          titolo: "Risultato finale",
          parole: ["risultato", "finale", "ottenere", "prodotto", "obiettivo"],
          descrizione: "Chiarisce quale risultato si vuole raggiungere.",
          domandaStudio: "Che risultato finale si vuole ottenere?"
        }
      ]
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

  function textExists(testo) {
    return String(testo || "").trim().length > 0;
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

  function righePulite(testo) {
    return normalizzaTesto(testo)
      .split("\n")
      .map(function (riga) {
        return riga
          .replace(/^[-•–]\s*/g, "")
          .replace(/\s+/g, " ")
          .trim();
      })
      .filter(function (riga) {
        return riga.length > 2;
      });
  }

  function riconosciTema(testo) {
    const t = normalizzaTesto(testo).toLowerCase();

    let migliore = "hobby";
    let punteggioMigliore = -1;

    Object.entries(profiliDocumento).forEach(function ([chiave, profilo]) {
      let punteggio = 0;

      profilo.parole.forEach(function (parola) {
        if (t.includes(parola)) {
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

  function lineaContiene(linea, parole) {
    const l = linea.toLowerCase();

    return parole.some(function (parola) {
      return l.includes(parola.toLowerCase());
    });
  }

  function primaLineaNonUsata(righe, usate) {
    for (let i = 0; i < righe.length; i += 1) {
      if (!usate.has(i)) {
        return i;
      }
    }

    return -1;
  }

  function trovaLineaPerSezione(sezione, righe, usate) {
    for (let i = 0; i < righe.length; i += 1) {
      if (usate.has(i)) {
        continue;
      }

      if (lineaContiene(righe[i], sezione.parole)) {
        return i;
      }
    }

    return -1;
  }

  function costruisciCardDaSezioni(testo, profilo) {
    const righe = righePulite(testo);
    const usate = new Set();
    const cards = [];

    profilo.sezioni.forEach(function (sezione) {
      let indice = trovaLineaPerSezione(sezione, righe, usate);

      if (indice === -1 && cards.length < 2) {
        indice = primaLineaNonUsata(righe, usate);
      }

      if (indice === -1) {
        return;
      }

      usate.add(indice);

      let originale = righe[indice];

      if (
        profilo.classe === "theme-cv" &&
        sezione.ramo === "profilo" &&
        righe[indice + 1] &&
        !usate.has(indice + 1) &&
        righe[indice].length < 35
      ) {
        originale = righe[indice] + " — " + righe[indice + 1];
        usate.add(indice + 1);
      }

      cards.push({
        numero: cards.length + 1,
        profilo: profilo,
        ramo: sezione.ramo,
        titolo: sezione.titolo,
        descrizione: sezione.descrizione,
        domandaStudio: sezione.domandaStudio,
        originale: originale
      });
    });

    return cards.slice(0, 6);
  }

  function creaCards(testo) {
    const profilo = riconosciTema(testo);
    let cards = costruisciCardDaSezioni(testo, profilo);

    if (!cards.length) {
      const righe = righePulite(testo).slice(0, 4);

      cards = righe.map(function (riga, indice) {
        const sezione = profilo.sezioni[indice % profilo.sezioni.length];

        return {
          numero: indice + 1,
          profilo: profilo,
          ramo: sezione.ramo,
          titolo: sezione.titolo,
          descrizione: sezione.descrizione,
          domandaStudio: sezione.domandaStudio,
          originale: riga
        };
      });
    }

    return {
      profilo: profilo,
      cards: cards
    };
  }

  function generaRiassunto() {
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
        <h2>Riassunto documento</h2>
        <p>
          Il testo è stato riconosciuto come <strong>${escapeHtml(profilo.nome)}</strong>.
          Sono state isolate <strong>${cards.length}</strong> parti realmente utili.
        </p>

        <h3>Parti principali</h3>
        <ol>
          ${cards.map(function (card) {
            return `
              <li>
                <strong>${escapeHtml(card.titolo)}:</strong>
                ${escapeHtml(card.descrizione)}
                <br>
                <em>Riferimento:</em> ${escapeHtml(card.originale)}
              </li>
            `;
          }).join("")}
        </ol>
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
        <p>Ogni card rappresenta una parte diversa del documento, senza ripetere la stessa frase generica.</p>

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

    const daAltri = altri.slice(0, 3).map(function (altra) {
      return {
        testo: altra.descrizione,
        corretta: false
      };
    });

    const fallback = [
      {
        testo: "Individua un dettaglio collegato, ma lo interpreta come obiettivo principale invece che come supporto.",
        corretta: false
      },
      {
        testo: "Descrive una funzione possibile nel documento, ma non quella più adatta al blocco indicato.",
        corretta: false
      },
      {
        testo: "Coglie un elemento del testo, ma lo collega a una sezione diversa.",
        corretta: false
      }
    ];

    return daAltri.concat(fallback).slice(0, 3);
  }

  function creaQuiz() {
    const testo = leggiTesto();

    if (!textExists(testo)) {
      mostraErrore("Documento mancante", "Incolla o carica prima un documento.");
      return null;
    }

    const risultato = creaCards(testo);
    const cards = risultato.cards.slice(0, 8);

    const domande = cards.map(function (card) {
      const corretta = {
        testo: card.descrizione,
        corretta: true
      };

      return {
        domanda: `Nel blocco "${card.originale}", quale interpretazione è più corretta?`,
        spiegazione: `Il blocco appartiene alla sezione "${card.titolo}" e va letto per la sua funzione specifica.`,
        opzioni: mescola([corretta].concat(creaDistrattoriForti(card, cards)))
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
        <p>Le risposte corrette non sono visibili. Scegli una risposta e poi vai avanti.</p>

        <button id="btnAvviaQuiz" class="quiz-start-button" type="button">Inizia test</button>
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
        <p>Domande mirate, una per ogni parte davvero utile del documento.</p>

        <div class="study-grid">
          ${cards.map(function (card) {
            return `
              <article class="study-card">
                <span class="badge">${escapeHtml(card.ramo)}</span>
                <h3>${escapeHtml(card.titolo)}</h3>
                <p class="study-question">${escapeHtml(card.domandaStudio)}</p>
                <p class="study-answer">${escapeHtml(card.descrizione)}</p>
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
