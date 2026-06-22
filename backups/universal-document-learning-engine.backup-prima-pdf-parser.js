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


  // === BLOCCO 3: PROFILI AVANZATI START ===
  function completaProfiliAvanzati() {
    profiliDocumento.sport.sezioni = [
      {
        ramo: "riscaldamento",
        titolo: "Riscaldamento",
        parole: ["riscaldamento", "attivazione", "preparazione"],
        descrizione: "Prepara corpo, respiro e articolazioni prima della parte principale.",
        domandaStudio: "Perché questa fase va messa prima dello sforzo principale?"
      },
      {
        ramo: "cardio",
        titolo: "Cardio leggero",
        parole: ["camminata", "bicicletta", "nuoto", "corsa", "cardio"],
        descrizione: "Allena resistenza e continuità con uno sforzo aerobico moderato.",
        domandaStudio: "Quale capacità fisica viene allenata in questa fase?"
      },
      {
        ramo: "forza",
        titolo: "Forza e potenziamento",
        parole: ["forza", "squat", "plank", "affondi", "pesi", "piegamenti"],
        descrizione: "Sviluppa controllo muscolare, stabilità e capacità di sostenere lo sforzo.",
        domandaStudio: "Quale parte del corpo o quale capacità viene potenziata?"
      },
      {
        ramo: "mobilità",
        titolo: "Mobilità e flessibilità",
        parole: ["flessibilità", "mobilità", "stretching", "allungamento"],
        descrizione: "Migliora scioltezza, ampiezza del movimento e controllo articolare.",
        domandaStudio: "Che differenza c’è tra questa fase e il lavoro cardio?"
      },
      {
        ramo: "equilibrio",
        titolo: "Equilibrio e controllo",
        parole: ["equilibrio", "postura", "stabilità", "coordinazione"],
        descrizione: "Allena stabilità, postura e controllo del corpo.",
        domandaStudio: "Quale controllo del corpo viene richiesto in questa fase?"
      },
      {
        ramo: "recupero",
        titolo: "Recupero",
        parole: ["riposo", "recupero", "pausa"],
        descrizione: "Fa abbassare il ritmo e permette di ripartire meglio nel blocco successivo.",
        domandaStudio: "Perché il recupero aiuta a mantenere qualità nella scheda?"
      },
      {
        ramo: "defaticamento",
        titolo: "Defaticamento",
        parole: ["defaticamento", "relax", "rilassamento", "chiusura"],
        descrizione: "Riduce gradualmente lo sforzo e accompagna il corpo verso il recupero.",
        domandaStudio: "Perché questa fase è più adatta alla fine dell’allenamento?"
      }
    ];

    profiliDocumento.curriculum.sezioni = [
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
        parole: ["esperienza", "esperienze", "progetti", "stage", "lavoro", "attività", "collaborazione"],
        descrizione: "Mostra attività concrete, progetti svolti o esperienze utili per valutare il percorso.",
        domandaStudio: "Quale esperienza concreta può interessare a un’azienda?"
      },
      {
        ramo: "competenze tecniche",
        titolo: "Competenze tecniche",
        parole: ["html", "css", "javascript", "python", "kotlin", "java", "github", "database", "programmazione"],
        descrizione: "Raccoglie strumenti, linguaggi e conoscenze tecniche spendibili nel lavoro.",
        domandaStudio: "Quali competenze tecniche emergono dal testo?"
      },
      {
        ramo: "competenze trasversali",
        titolo: "Competenze trasversali",
        parole: ["problem solving", "organizzazione", "team", "comunicazione", "precisione", "autonomia"],
        descrizione: "Mostra capacità personali utili per lavorare meglio in gruppo o su progetto.",
        domandaStudio: "Quale qualità personale può fare la differenza sul lavoro?"
      },
      {
        ramo: "formazione",
        titolo: "Formazione",
        parole: ["formazione", "diploma", "corso", "istruzione", "percorso", "studio", "aggiornamento"],
        descrizione: "Spiega il percorso di studio o aggiornamento che sostiene il profilo.",
        domandaStudio: "In che modo la formazione rafforza il profilo?"
      },
      {
        ramo: "obiettivo",
        titolo: "Obiettivo professionale",
        parole: ["obiettivo", "crescere", "entrare", "team", "ruolo", "full stack", "sviluppare"],
        descrizione: "Chiarisce dove vuole arrivare la persona e quale ruolo cerca.",
        domandaStudio: "Che direzione professionale viene dichiarata?"
      },
      {
        ramo: "punti forti",
        titolo: "Punti forti",
        parole: ["punti forti", "forte", "capacità", "motivazione", "interesse", "passione"],
        descrizione: "Evidenzia ciò che rende il profilo più riconoscibile e presentabile.",
        domandaStudio: "Qual è il punto forte da valorizzare?"
      }
    ];

    profiliDocumento.personale.sezioni = [
      {
        ramo: "identità",
        titolo: "Identità",
        parole: ["nome", "cognome", "nato", "nata", "data di nascita", "codice fiscale"],
        descrizione: "Contiene dati utili per identificare correttamente la persona.",
        domandaStudio: "Quali dati servono per riconoscere la persona?"
      },
      {
        ramo: "residenza",
        titolo: "Residenza e contatti",
        parole: ["residenza", "indirizzo", "domicilio", "telefono", "email", "contatto"],
        descrizione: "Raccoglie informazioni utili per contatto, domicilio o riferimento amministrativo.",
        domandaStudio: "Quale dato serve per essere contattati o riconosciuti?"
      },
      {
        ramo: "documento",
        titolo: "Numero documento",
        parole: ["documento", "numero", "carta", "tessera", "certificato", "protocollo"],
        descrizione: "Indica riferimenti ufficiali utili per riconoscere il documento.",
        domandaStudio: "Quale numero o riferimento va conservato?"
      },
      {
        ramo: "scadenze",
        titolo: "Scadenze",
        parole: ["scadenza", "valido", "validità", "rinnovo", "data"],
        descrizione: "Segnala date importanti da controllare per evitare dimenticanze.",
        domandaStudio: "Quale scadenza va ricordata?"
      },
      {
        ramo: "azioni",
        titolo: "Azioni da fare",
        parole: ["fare", "presentare", "inviare", "portare", "richiedere", "consegnare"],
        descrizione: "Evidenzia un’azione pratica collegata al documento.",
        domandaStudio: "Che cosa bisogna fare dopo aver letto questa parte?"
      }
    ];

    profiliDocumento.aziendale.sezioni = [
      {
        ramo: "obiettivo",
        titolo: "Obiettivo",
        parole: ["obiettivo", "scopo", "finalità", "risultato", "target"],
        descrizione: "Spiega il risultato che il documento o la procedura vuole ottenere.",
        domandaStudio: "Qual è lo scopo operativo di questa parte?"
      },
      {
        ramo: "contesto",
        titolo: "Contesto",
        parole: ["contesto", "situazione", "scenario", "cliente", "mercato", "reparto"],
        descrizione: "Spiega dove si colloca l’attività e perché è rilevante.",
        domandaStudio: "Quale contesto bisogna capire prima di agire?"
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
        parole: ["responsabile", "ruolo", "team", "operatore", "referente", "manager"],
        descrizione: "Chiarisce chi deve occuparsi di una parte del lavoro.",
        domandaStudio: "Chi è coinvolto e con quale responsabilità?"
      },
      {
        ramo: "rischi",
        titolo: "Rischi e controlli",
        parole: ["rischio", "sicurezza", "errore", "controllo", "attenzione", "problema"],
        descrizione: "Segnala elementi da controllare per ridurre errori o rischi.",
        domandaStudio: "Quale rischio bisogna prevenire?"
      },
      {
        ramo: "metriche",
        titolo: "Dati e indicatori",
        parole: ["dato", "dati", "percentuale", "numero", "report", "indicatore", "kpi"],
        descrizione: "Raccoglie numeri o indicatori utili per valutare andamento e risultati.",
        domandaStudio: "Quale dato aiuta a valutare il risultato?"
      },
      {
        ramo: "prossimi passi",
        titolo: "Prossimi passi",
        parole: ["prossimo", "azione", "piano", "scadenza", "deadline", "follow up"],
        descrizione: "Indica che cosa va fatto dopo la lettura o dopo la fase descritta.",
        domandaStudio: "Qual è il prossimo passo operativo?"
      }
    ];

    profiliDocumento.storia.sezioni = [
      {
        ramo: "personaggi",
        titolo: "Personaggi",
        parole: ["personaggio", "protagonista", "ragazzo", "ragazza", "uomo", "donna", "bambino", "eroe"],
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
        ramo: "evento iniziale",
        titolo: "Evento iniziale",
        parole: ["inizio", "un giorno", "all’inizio", "cominciò", "partì"],
        descrizione: "Avvia la storia e mette in movimento la narrazione.",
        domandaStudio: "Quale evento fa partire la storia?"
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
      },
      {
        ramo: "finale",
        titolo: "Finale",
        parole: ["finale", "alla fine", "concluse", "tornò", "risolse"],
        descrizione: "Chiude il percorso narrativo e mostra il risultato degli eventi.",
        domandaStudio: "Come si conclude il percorso del personaggio?"
      }
    ];

    profiliDocumento.poesia.sezioni = [
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
      },
      {
        ramo: "metafora",
        titolo: "Metafora",
        parole: ["come", "sembra", "diventa", "metafora", "simbolo"],
        descrizione: "Trasforma un’immagine in un significato più profondo.",
        domandaStudio: "Quale significato nascosto può avere questa immagine?"
      },
      {
        ramo: "ritmo",
        titolo: "Ritmo e suono",
        parole: ["rima", "verso", "strofa", "suono", "ritmo"],
        descrizione: "Dà musicalità al testo e guida la lettura.",
        domandaStudio: "Che effetto produce il ritmo del testo?"
      }
    ];

    profiliDocumento.hobby.sezioni = [
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
        parole: ["materiali", "strumenti", "oggetti", "file", "ingredienti", "attrezzi"],
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
        ramo: "tecnica",
        titolo: "Tecnica",
        parole: ["tecnica", "metodo", "modo", "regola", "procedimento"],
        descrizione: "Spiega il modo corretto o più efficace per svolgere l’attività.",
        domandaStudio: "Quale tecnica rende migliore il risultato?"
      },
      {
        ramo: "obiettivo",
        titolo: "Obiettivo",
        parole: ["obiettivo", "scopo", "risultato", "ottenere", "migliorare"],
        descrizione: "Chiarisce che cosa si vuole raggiungere con l’attività.",
        domandaStudio: "Quale obiettivo si vuole raggiungere?"
      },
      {
        ramo: "risultato",
        titolo: "Risultato finale",
        parole: ["finale", "prodotto", "completo", "finito", "risultato"],
        descrizione: "Mostra quale risultato concreto o creativo si vuole ottenere.",
        domandaStudio: "Come dovrebbe essere il risultato finale?"
      }
    ];
  }

  completaProfiliAvanzati();

  const esempiDocumentiUniversali = {
    sport: `Scheda allenamento settimanale
10 minuti di riscaldamento articolare
25 minuti di camminata veloce o bicicletta
3 serie di squat e plank
5 minuti di equilibrio su una gamba
10 minuti di stretching
5 minuti di defaticamento e relax`,

    curriculum: `Mario Rossi
Sviluppatore junior con interesse per web app, intelligenza artificiale e strumenti digitali.
Esperienze: piccoli progetti HTML, CSS e JavaScript pubblicati su GitHub.
Competenze tecniche: JavaScript, Python base, GitHub, problem solving.
Competenze trasversali: organizzazione, autonomia e voglia di imparare.
Formazione: diploma tecnico e corso di aggiornamento in sviluppo software.
Obiettivo: entrare in un team dove crescere come full stack developer.`,

    personale: `Documento personale
Nome: Mario Rossi
Codice fiscale: RSSMRA80A01H501Z
Residenza: Roma, Via delle Rose 10
Numero documento: AX1234567
Scadenza: 12/09/2028
Azione da fare: controllare la validità prima della prenotazione.`,

    aziendale: `Procedura aziendale sicurezza dati
Obiettivo: ridurre errori nella gestione dei file dei clienti.
Contesto: il reparto amministrativo lavora ogni giorno con documenti sensibili.
Processo: salvare i file nella cartella condivisa corretta e nominare i documenti secondo lo standard.
Responsabilità: ogni operatore controlla i propri file prima dell’invio.
Rischi: invio errato, perdita dati o accesso non autorizzato.
Metriche: numero di errori mensili e tempi di correzione.
Prossimi passi: formazione interna e controllo settimanale.`,

    storia: `Storia breve
Nel piccolo villaggio vicino al bosco viveva una ragazza curiosa.
Un giorno trovò una mappa nascosta sotto una pietra.
Il problema era attraversare il sentiero prima del tramonto.
All’improvviso capì che i simboli sulla mappa indicavano gli alberi più antichi.
Decise di seguirli e trovò l’ingresso di una vecchia biblioteca.
Alla fine tornò al villaggio con un libro che raccontava la memoria del luogo.`,

    poesia: `Poesia
Nel silenzio della notte
il vento sfiora il cuore.
Una luce piccola resiste
tra ombra e ricordo.
Il mare sembra una strada
che porta lontano la paura.
Resta una speranza sottile
come rima nascosta nel tempo.`,

    hobby: `Progetto tempo libero
Attività: creare un piccolo diario illustrato.
Materiali: quaderno, matite colorate, colla e fotografie.
Passaggi: scegliere un tema, disegnare le pagine, aggiungere brevi testi.
Tecnica: usare colori diversi per separare ricordi, idee e obiettivi.
Obiettivo: costruire un oggetto personale e creativo.
Risultato finale: un diario ordinato, colorato e facile da sfogliare.`
  };

  function caricaEsempioTema(tema) {
    const input = document.getElementById("documentoInput");

    if (!input || !esempiDocumentiUniversali[tema]) {
      return;
    }

    input.value = esempiDocumentiUniversali[tema];

    const output = document.getElementById("output");
    if (output) {
      output.innerHTML = "";
    }
  }

  // === BLOCCO 3: PROFILI AVANZATI END ===


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

  function disegnoSvg(card) {
    const tema = card.profilo.classe;
    const ramo = card.ramo;

    if (tema === "theme-sport") {
      if (ramo.includes("attività")) {
        return `
          <svg class="card-svg" viewBox="0 0 240 150" xmlns="http://www.w3.org/2000/svg">
            <rect x="12" y="12" width="216" height="126" rx="28" fill="rgba(255,255,255,0.08)"/>
            <circle cx="68" cy="94" r="22" fill="#22d3ee"/>
            <circle cx="174" cy="94" r="22" fill="#8b5cf6"/>
            <path d="M68 94 L104 56 L138 56 L174 94" stroke="#f8fafc" stroke-width="9" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="122" cy="38" r="13" fill="#f8fafc"/>
          </svg>
        `;
      }

      if (ramo.includes("recupero")) {
        return `
          <svg class="card-svg" viewBox="0 0 240 150" xmlns="http://www.w3.org/2000/svg">
            <rect x="12" y="12" width="216" height="126" rx="28" fill="rgba(255,255,255,0.08)"/>
            <rect x="58" y="86" width="124" height="18" rx="9" fill="#8b5cf6"/>
            <rect x="52" y="72" width="14" height="44" rx="7" fill="#f8fafc"/>
            <rect x="176" y="72" width="14" height="44" rx="7" fill="#f8fafc"/>
            <text x="88" y="60" font-size="30" font-weight="900" fill="#f8fafc">Z</text>
            <text x="124" y="46" font-size="22" font-weight="900" fill="#ddd6fe">Z</text>
          </svg>
        `;
      }

      return `
        <svg class="card-svg" viewBox="0 0 240 150" xmlns="http://www.w3.org/2000/svg">
          <rect x="12" y="12" width="216" height="126" rx="28" fill="rgba(255,255,255,0.08)"/>
          <circle cx="120" cy="38" r="13" fill="#f8fafc"/>
          <path d="M120 54 L120 90" stroke="#22d3ee" stroke-width="9" stroke-linecap="round"/>
          <path d="M120 66 L88 82" stroke="#f472b6" stroke-width="9" stroke-linecap="round"/>
          <path d="M120 66 L152 82" stroke="#f472b6" stroke-width="9" stroke-linecap="round"/>
          <path d="M120 90 L94 118" stroke="#8b5cf6" stroke-width="9" stroke-linecap="round"/>
          <path d="M120 90 L148 118" stroke="#8b5cf6" stroke-width="9" stroke-linecap="round"/>
        </svg>
      `;
    }

    if (tema === "theme-cv") {
      if (ramo.includes("competenze")) {
        return `
          <svg class="card-svg" viewBox="0 0 240 150" xmlns="http://www.w3.org/2000/svg">
            <rect x="18" y="18" width="204" height="114" rx="24" fill="rgba(255,255,255,0.08)"/>
            <rect x="54" y="44" width="132" height="66" rx="14" fill="#1d4ed8"/>
            <path d="M86 74 L104 58 L122 74 L104 90 Z" fill="#93c5fd"/>
            <path d="M132 62 H164" stroke="#f8fafc" stroke-width="8" stroke-linecap="round"/>
            <path d="M132 84 H154" stroke="#f8fafc" stroke-width="8" stroke-linecap="round"/>
          </svg>
        `;
      }

      if (ramo.includes("formazione")) {
        return `
          <svg class="card-svg" viewBox="0 0 240 150" xmlns="http://www.w3.org/2000/svg">
            <rect x="18" y="18" width="204" height="114" rx="24" fill="rgba(255,255,255,0.08)"/>
            <path d="M52 62 L120 34 L188 62 L120 90 Z" fill="#60a5fa"/>
            <path d="M76 78 V98 C100 116 140 116 164 98 V78" fill="#1d4ed8"/>
            <path d="M188 62 V94" stroke="#f8fafc" stroke-width="6" stroke-linecap="round"/>
          </svg>
        `;
      }

      return `
        <svg class="card-svg" viewBox="0 0 240 150" xmlns="http://www.w3.org/2000/svg">
          <rect x="18" y="18" width="204" height="114" rx="24" fill="rgba(255,255,255,0.08)"/>
          <circle cx="82" cy="58" r="24" fill="#93c5fd"/>
          <path d="M44 116 C52 86 112 86 120 116" fill="#60a5fa"/>
          <rect x="132" y="48" width="54" height="12" rx="6" fill="#f8fafc"/>
          <rect x="132" y="72" width="72" height="12" rx="6" fill="#bfdbfe"/>
          <rect x="132" y="96" width="44" height="12" rx="6" fill="#93c5fd"/>
        </svg>
      `;
    }

    if (tema === "theme-personal") {
      return `
        <svg class="card-svg" viewBox="0 0 240 150" xmlns="http://www.w3.org/2000/svg">
          <rect x="54" y="24" width="132" height="102" rx="18" fill="#0f766e"/>
          <path d="M150 24 L186 60 H150 Z" fill="#5eead4"/>
          <rect x="78" y="62" width="72" height="10" rx="5" fill="#f8fafc"/>
          <rect x="78" y="84" width="84" height="10" rx="5" fill="#ccfbf1"/>
          <circle cx="158" cy="102" r="18" fill="#14b8a6"/>
          <path d="M150 102 L156 108 L168 94" stroke="#f8fafc" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      `;
    }

    if (tema === "theme-business") {
      if (ramo.includes("rischi")) {
        return `
          <svg class="card-svg" viewBox="0 0 240 150" xmlns="http://www.w3.org/2000/svg">
            <rect x="18" y="18" width="204" height="114" rx="24" fill="rgba(255,255,255,0.08)"/>
            <path d="M120 30 L176 54 V84 C176 110 150 124 120 134 C90 124 64 110 64 84 V54 Z" fill="#64748b"/>
            <path d="M120 60 V86" stroke="#f8fafc" stroke-width="8" stroke-linecap="round"/>
            <circle cx="120" cy="106" r="6" fill="#f8fafc"/>
          </svg>
        `;
      }

      return `
        <svg class="card-svg" viewBox="0 0 240 150" xmlns="http://www.w3.org/2000/svg">
          <rect x="18" y="18" width="204" height="114" rx="24" fill="rgba(255,255,255,0.08)"/>
          <rect x="46" y="86" width="32" height="34" rx="8" fill="#94a3b8"/>
          <rect x="96" y="58" width="32" height="62" rx="8" fill="#cbd5e1"/>
          <rect x="146" y="36" width="32" height="84" rx="8" fill="#f8fafc"/>
          <path d="M52 60 L96 44 L140 48 L184 28" stroke="#38bdf8" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      `;
    }

    if (tema === "theme-story") {
      return `
        <svg class="card-svg" viewBox="0 0 240 150" xmlns="http://www.w3.org/2000/svg">
          <rect x="18" y="18" width="204" height="114" rx="24" fill="rgba(255,255,255,0.08)"/>
          <path d="M62 42 H112 C124 42 132 52 132 64 V112 H78 C68 112 62 106 62 96 Z" fill="#a78bfa"/>
          <path d="M132 64 C132 52 140 42 152 42 H178 V96 C178 106 172 112 162 112 H132 Z" fill="#7c3aed"/>
          <circle cx="94" cy="72" r="8" fill="#f8fafc"/>
          <path d="M92 98 C110 84 134 84 150 100" stroke="#f8fafc" stroke-width="6" fill="none" stroke-linecap="round"/>
        </svg>
      `;
    }

    if (tema === "theme-poetry") {
      return `
        <svg class="card-svg" viewBox="0 0 240 150" xmlns="http://www.w3.org/2000/svg">
          <rect x="18" y="18" width="204" height="114" rx="24" fill="rgba(255,255,255,0.08)"/>
          <path d="M82 112 C124 38 162 28 184 42 C170 86 130 114 82 112 Z" fill="#f9a8d4"/>
          <path d="M84 112 C112 82 138 60 180 42" stroke="#831843" stroke-width="5" fill="none" stroke-linecap="round"/>
          <circle cx="64" cy="54" r="18" fill="#fce7f3"/>
          <path d="M54 96 Q82 82 110 96 T166 96" stroke="#f8fafc" stroke-width="5" fill="none" stroke-linecap="round"/>
        </svg>
      `;
    }

    return `
      <svg class="card-svg" viewBox="0 0 240 150" xmlns="http://www.w3.org/2000/svg">
        <rect x="18" y="18" width="204" height="114" rx="24" fill="rgba(255,255,255,0.08)"/>
        <circle cx="82" cy="70" r="28" fill="#fb923c"/>
        <circle cx="122" cy="54" r="20" fill="#facc15"/>
        <circle cx="154" cy="86" r="26" fill="#22d3ee"/>
        <path d="M70 112 L178 112" stroke="#f8fafc" stroke-width="8" stroke-linecap="round"/>
        <path d="M96 100 L120 76 L146 100" stroke="#f8fafc" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
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
                <div class="card-hero">
                  ${disegnoSvg(card)}
                </div>
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
    Array.from(document.querySelectorAll("[data-esempio-tema]")).forEach(function (bottone) {
      bottone.addEventListener("click", function () {
        caricaEsempioTema(bottone.dataset.esempioTema);
      });
    });

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
