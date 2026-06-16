const DATA_URL = "../dist/database_quiz_finale.json";

let databaseQuiz = [];
let domandeTest = [];
let indiceDomandaCorrente = 0;
let risposteCorrette = 0;
let risposteSbagliate = 0;
let rispostaGiaData = false;

/*
 * Motore generale premi finali quiz
 * Funziona per AI, Scienze e tutte le materie future.
 * Non dipende dal nome della materia e non modifica il database domande.
 */

(function () {
    const PREMI_FINALI_GENERALI = {
        perfetto: [
            {
                disegno: "🏆",
                titolo: "Risultato perfetto",
                frase: "Hai chiuso il quiz senza errori. Precisione totale.",
                motivazione: "Ora puoi alzare la difficoltà oppure provare una nuova materia."
            },
            {
                disegno: "🚀",
                titolo: "Prestazione da fuoriclasse",
                frase: "Hai risposto a tutto correttamente: controllo, memoria e ragionamento hanno lavorato insieme.",
                motivazione: "Ripeti il test più avanti per verificare se il risultato resta stabile."
            },
            {
                disegno: "👑",
                titolo: "Dominio completo",
                frase: "Non hai solo superato il quiz: lo hai dominato.",
                motivazione: "Passa a domande con distrattori più difficili."
            },
            {
                disegno: "💎",
                titolo: "Cristallo perfetto",
                frase: "Zero errori, massima pulizia mentale.",
                motivazione: "Allenati ora sulla velocità, non solo sulla correttezza."
            }
        ],

        eccellente: [
            {
                disegno: "🥇",
                titolo: "Risultato eccellente",
                frase: "Hai fatto pochissimi errori. La preparazione è molto solida.",
                motivazione: "Rivedi solo le domande sbagliate e punta al risultato perfetto."
            },
            {
                disegno: "🔥",
                titolo: "Livello molto alto",
                frase: "Sei vicino al controllo completo dell'argomento.",
                motivazione: "Allenati sulle domande più ambigue, dove due risposte sembrano entrambe valide."
            },
            {
                disegno: "⭐",
                titolo: "Preparazione forte",
                frase: "Il risultato mostra sicurezza e buona capacità di scelta.",
                motivazione: "Ora devi lavorare sui dettagli che fanno perdere l'ultimo punto."
            },
            {
                disegno: "🧠",
                titolo: "Mente precisa",
                frase: "Hai ragionato bene anche davanti ai distrattori.",
                motivazione: "Continua con un test della stessa materia ma a livello più alto."
            }
        ],

        ottimo: [
            {
                disegno: "🎯",
                titolo: "Ottimo risultato",
                frase: "Hai una buona base e sai riconoscere molte risposte corrette.",
                motivazione: "Concentrati sugli errori: probabilmente sono dettagli o distrattori forti."
            },
            {
                disegno: "📈",
                titolo: "Obiettivo quasi centrato",
                frase: "La direzione è giusta. Manca poco per arrivare alla fascia eccellente.",
                motivazione: "Rifai un test simile e controlla se sbagli sempre lo stesso tipo di domanda."
            },
            {
                disegno: "🛡️",
                titolo: "Preparazione resistente",
                frase: "Hai retto bene il test, anche se qualche risposta ti ha messo in difficoltà.",
                motivazione: "Studia le spiegazioni e riprova senza fretta."
            }
        ],

        buono: [
            {
                disegno: "📘",
                titolo: "Buon risultato",
                frase: "Hai superato bene il test, ma alcuni argomenti vanno rinforzati.",
                motivazione: "Rivedi teoria e spiegazioni prima di salire di livello."
            },
            {
                disegno: "🛠️",
                titolo: "Base positiva",
                frase: "La struttura c'è. Ora bisogna renderla più precisa.",
                motivazione: "Allenati sulle domande dove eri indeciso tra due opzioni."
            },
            {
                disegno: "🌉",
                titolo: "Ponte verso il livello alto",
                frase: "Sei sopra la soglia buona, ma puoi salire ancora.",
                motivazione: "Trasforma gli errori in una lista di argomenti da ripassare."
            }
        ],

        sufficiente: [
            {
                disegno: "🌱",
                titolo: "Risultato sufficiente",
                frase: "Hai superato la soglia, ma la preparazione deve diventare più stabile.",
                motivazione: "Riparti dagli argomenti sbagliati e rifai il test."
            },
            {
                disegno: "🔎",
                titolo: "Serve più precisione",
                frase: "Hai capito alcune cose, ma i distrattori riescono ancora a confonderti.",
                motivazione: "Leggi con calma domanda, opzioni e spiegazione finale."
            },
            {
                disegno: "🏗️",
                titolo: "Fondamenta da rinforzare",
                frase: "La base c'è, ma va consolidata prima di aumentare la difficoltà.",
                motivazione: "Meglio ripetere un livello facile o intermedio prima dell'avanzato."
            }
        ],

        allenamento: [
            {
                disegno: "💪",
                titolo: "Allenamento necessario",
                frase: "Questo risultato non è una bocciatura: indica solo dove lavorare.",
                motivazione: "Rifai il test dopo aver studiato le spiegazioni."
            },
            {
                disegno: "🧩",
                titolo: "Pezzi da rimettere insieme",
                frase: "Alcuni concetti non sono ancora collegati bene tra loro.",
                motivazione: "Riparti dalle domande sbagliate e cerca il motivo dell'errore."
            },
            {
                disegno: "🔁",
                titolo: "Riprova guidata",
                frase: "Il modo migliore per crescere è riprovare con calma, errore dopo errore.",
                motivazione: "Fai un nuovo test più breve e controlla subito le spiegazioni."
            }
        ]
    };

    function scegliElementoCasuale(lista) {
        const indice = Math.floor(Math.random() * lista.length);
        return lista[indice];
    }

    function calcolaFascia(risposteCorrette, totaleDomande) {
        if (!totaleDomande || totaleDomande <= 0) {
            return "allenamento";
        }

        const percentuale = Math.round((risposteCorrette / totaleDomande) * 100);

        if (risposteCorrette === totaleDomande) {
            return "perfetto";
        }

        if (percentuale >= 90) {
            return "eccellente";
        }

        if (percentuale >= 80) {
            return "ottimo";
        }

        if (percentuale >= 70) {
            return "buono";
        }

        if (percentuale >= 60) {
            return "sufficiente";
        }

        return "allenamento";
    }

    function creaPremioFinale(datiRisultato) {
        const risposteCorrette = Number(datiRisultato.risposteCorrette || 0);
        const totaleDomande = Number(datiRisultato.totaleDomande || 0);
        const materia = datiRisultato.materia || "Quiz";
        const livello = datiRisultato.livello || "";

        const percentuale = totaleDomande > 0
            ? Math.round((risposteCorrette / totaleDomande) * 100)
            : 0;

        const fascia = calcolaFascia(risposteCorrette, totaleDomande);
        const premio = scegliElementoCasuale(PREMI_FINALI_GENERALI[fascia]);

        return {
            ...premio,
            fascia,
            materia,
            livello,
            risposteCorrette,
            totaleDomande,
            percentuale
        };
    }

    function creaHtmlPremioFinale(premio) {
        const dettaglioMateria = premio.livello
            ? `${premio.materia} · ${premio.livello}`
            : premio.materia;

        return `
            <div class="alex-final-reward-card" data-fascia="${premio.fascia}">
                <div class="alex-final-reward-drawing">${premio.disegno}</div>
                <div class="alex-final-reward-body">
                    <p class="alex-final-reward-kicker">${dettaglioMateria}</p>
                    <h3>${premio.titolo}</h3>
                    <p class="alex-final-reward-score">
                        ${premio.risposteCorrette}/${premio.totaleDomande}
                        corrette · ${premio.percentuale}%
                    </p>
                    <p>${premio.frase}</p>
                    <p class="alex-final-reward-motivation">${premio.motivazione}</p>
                </div>
            </div>
        `;
    }

    function mostraPremioFinale(contenitore, datiRisultato) {
        if (!contenitore) {
            return null;
        }

        const premio = creaPremioFinale(datiRisultato);
        contenitore.innerHTML = creaHtmlPremioFinale(premio);
        return premio;
    }

    window.AlexFinalRewardEngine = {
        creaPremioFinale,
        creaHtmlPremioFinale,
        mostraPremioFinale
    };
})();



function alexLeggiTotaleDomandePremioGenerale() {
    const possibiliListe = [
        typeof domandeQuiz !== "undefined" ? domandeQuiz : null,
        typeof quizCorrente !== "undefined" ? quizCorrente : null,
        typeof domandeScelte !== "undefined" ? domandeScelte : null,
        typeof domandeAttive !== "undefined" ? domandeAttive : null,
        typeof domandeSelezionate !== "undefined" ? domandeSelezionate : null,
        typeof domandeCorrenti !== "undefined" ? domandeCorrenti : null,
        typeof quiz !== "undefined" ? quiz : null
    ];

    const listaValida = possibiliListe.find(lista => {
        return Array.isArray(lista) && lista.length > 0;
    });

    return listaValida ? listaValida.length : 10;
}

function alexLeggiTestoElementoPremioGenerale(idElemento, valoreDefault) {
    const elemento = document.getElementById(idElemento);

    if (!elemento) {
        return valoreDefault;
    }

    if ("value" in elemento && elemento.value) {
        return elemento.value;
    }

    return elemento.textContent?.trim() || valoreDefault;
}

function alexTrovaOCreaContenitorePremioGenerale() {
    let contenitore = document.getElementById("alexFinalRewardContainer");

    if (contenitore) {
        return contenitore;
    }

    contenitore = document.createElement("div");
    contenitore.id = "alexFinalRewardContainer";
    contenitore.className = "alex-final-reward-container";

    const sezioneRisultato =
        document.getElementById("resultSection") ||
        document.getElementById("resultsSection") ||
        document.getElementById("finalResult") ||
        elementi.correctResult?.closest("section") ||
        elementi.correctResult?.closest(".card") ||
        elementi.correctResult?.parentElement?.parentElement ||
        document.body;

    sezioneRisultato.appendChild(contenitore);

    return contenitore;
}

function alexMostraPremioFinaleGenerale() {
    if (!window.AlexFinalRewardEngine) {
        return;
    }

    const contenitore = alexTrovaOCreaContenitorePremioGenerale();

    window.AlexFinalRewardEngine.mostraPremioFinale(contenitore, {
        risposteCorrette,
        totaleDomande: alexLeggiTotaleDomandePremioGenerale(),
        materia: alexLeggiTestoElementoPremioGenerale("subjectSelect", "Quiz"),
        livello: alexLeggiTestoElementoPremioGenerale("levelSelect", "")
    });
}

let ultimoQuizPersonalizzatoJson = "";

/*
    Memoria dei gruppi di domande già usate.

    Esempio:
    categoria = matematica
    livello = avanzato

    Il sistema crea una coda mescolata.
    Le domande vengono estratte una alla volta.
    Non tornano finché la coda non è finita.
*/
let codeDomandePerFiltro = {};

const elementi = {};

const VISUAL_SHAPE_SIDES = {
    freccia: 0,
    cerchio: 0,
    triangolo: 3,
    quadrato: 4,
    rettangolo: 4,
    pentagono: 5,
    esagono: 6,
    ettagono: 7,
};

document.addEventListener("DOMContentLoaded", avviaApp);

async function avviaApp() {
    collegaElementiHtml();
    collegaEventi();

    await caricaDatabase();
    preparaMigliorieDemo();
}

function collegaElementiHtml() {
    elementi.loadingBox = document.getElementById("loadingBox");
    elementi.errorBox = document.getElementById("errorBox");
    elementi.setupBox = document.getElementById("setupBox");
    elementi.quizBox = document.getElementById("quizBox");
    elementi.resultBox = document.getElementById("resultBox");

    elementi.categorySelect = document.getElementById("categorySelect");
    elementi.levelSelect = document.getElementById("levelSelect");
    elementi.questionCountSelect = document.getElementById("questionCountSelect");
    elementi.availableInfo = document.getElementById("availableInfo");
    elementi.startButton = document.getElementById("startButton");

    elementi.progressText = document.getElementById("progressText");
    elementi.scoreText = document.getElementById("scoreText");
    elementi.questionMeta = document.getElementById("questionMeta");
    elementi.progressFill = document.getElementById("progressFill");
    elementi.questionText = document.getElementById("questionText");
    elementi.questionImageBox = document.getElementById("questionImageBox");
    elementi.optionsBox = document.getElementById("optionsBox");
    elementi.feedbackBox = document.getElementById("feedbackBox");
    elementi.explanationBox = document.getElementById("explanationBox");
    elementi.explanationText = document.getElementById("explanationText");
    elementi.nextButton = document.getElementById("nextButton");

    elementi.resultVisual = document.getElementById("resultVisual");
    elementi.resultEmoji = document.getElementById("resultEmoji");
    elementi.resultTitle = document.getElementById("resultTitle");
    elementi.resultPhrase = document.getElementById("resultPhrase");
    elementi.totalQuestionsResult = document.getElementById("totalQuestionsResult");
    elementi.correctResult = document.getElementById("correctResult");
    elementi.wrongResult = document.getElementById("wrongResult");
    elementi.percentageResult = document.getElementById("percentageResult");
    elementi.gradeResult = document.getElementById("gradeResult");
    elementi.judgementResult = document.getElementById("judgementResult");
    elementi.retryButton = document.getElementById("retryButton");
    elementi.settingsButton = document.getElementById("settingsButton");

    elementi.quizCreatorForm = document.getElementById("quizCreatorForm");
    elementi.creatorTitle = document.getElementById("creatorTitle");
    elementi.creatorSubject = document.getElementById("creatorSubject");
    elementi.creatorCustomSubject = document.getElementById("creatorCustomSubject");
    elementi.creatorLevel = document.getElementById("creatorLevel");
    elementi.creatorQuestionMode = document.getElementById("creatorQuestionMode");
    elementi.creatorCustomCount = document.getElementById("creatorCustomCount");
    elementi.creatorFile = document.getElementById("creatorFile");
    elementi.creatorSourceText = document.getElementById("creatorSourceText");
    elementi.creatorStatus = document.getElementById("creatorStatus");
    elementi.creatorQuestionCount = document.getElementById("creatorQuestionCount");
    elementi.quizJsonOutput = document.getElementById("quizJsonOutput");
    elementi.generateQuizJsonButton = document.getElementById("generateQuizJsonButton");
    elementi.copyQuizJsonButton = document.getElementById("copyQuizJsonButton");
    elementi.downloadQuizJsonButton = document.getElementById("downloadQuizJsonButton");

    elementi.confettiCanvas = document.getElementById("confettiCanvas");
}

function collegaEventi() {
    elementi.categorySelect.addEventListener(
        "change",
        aggiornaInfoDomandeDisponibili
    );

    elementi.levelSelect.addEventListener(
        "change",
        aggiornaInfoDomandeDisponibili
    );

    elementi.questionCountSelect.addEventListener(
        "change",
        aggiornaInfoDomandeDisponibili
    );

    elementi.startButton.addEventListener("click", iniziaTest);
    elementi.nextButton.addEventListener("click", vaiAllaProssimaDomanda);
    elementi.retryButton.addEventListener("click", iniziaTest);
    elementi.settingsButton.addEventListener("click", tornaAlleImpostazioni);

    if (elementi.quizCreatorForm) {
        elementi.quizCreatorForm.addEventListener(
            "submit",
            generaQuizPersonalizzatoJson
        );
    }

    if (elementi.copyQuizJsonButton) {
        elementi.copyQuizJsonButton.addEventListener(
            "click",
            copiaQuizPersonalizzatoJson
        );
    }

    if (elementi.downloadQuizJsonButton) {
        elementi.downloadQuizJsonButton.addEventListener(
            "click",
            scaricaQuizPersonalizzatoJson
        );
    }

    if (elementi.creatorFile) {
        elementi.creatorFile.addEventListener(
            "change",
            aggiornaStatoFileQuizCreator
        );
    }
}

async function caricaDatabase() {
    try {
        mostraSolo(elementi.loadingBox);

        /*
            Il parametro Date.now() evita che il browser tenga in memoria
            una vecchia versione del JSON.
        */
        const risposta = await fetch(`${DATA_URL}?v=${Date.now()}`);

        if (!risposta.ok) {
            throw new Error("Impossibile caricare il database quiz.");
        }

        databaseQuiz = await risposta.json();

        if (!Array.isArray(databaseQuiz)) {
            throw new Error("Il database non è una lista di domande.");
        }

        databaseQuiz = filtraDomandeVisualiNonValide(databaseQuiz);

        popolaFiltri();
        aggiornaInfoDomandeDisponibili();
        mostraSolo(elementi.setupBox);

    } catch (errore) {
        elementi.errorBox.textContent = errore.message;
        mostraSolo(elementi.errorBox);
    }
}

function mostraSolo(sezioneVisibile) {
    const sezioni = [
        elementi.loadingBox,
        elementi.errorBox,
        elementi.setupBox,
        elementi.quizBox,
        elementi.resultBox
    ];

    sezioni.forEach(sezione => {
        sezione.classList.add("hidden");
    });

    sezioneVisibile.classList.remove("hidden");
}

function popolaFiltri() {
    const categorieOrdinate = [
    "ai",
    "informatica",
    "matematica",
    "inglese",
    "logica",
    "logica_visiva",
    "scienze",
    "fisica",
    "chimica",
    "biologia",
  ];

    const livelliOrdinati = [
        "facile",
        "intermedio",
        "avanzato"
    ];

    elementi.categorySelect.innerHTML = "";
    elementi.levelSelect.innerHTML = "";

    aggiungiOpzione(
        elementi.categorySelect,
        "tutte",
        "Tutte le categorie"
    );

    categorieOrdinate.forEach(categoria => {
        const esisteCategoria = databaseQuiz.some(domanda => {
            return domandaCorrispondeCategoria(domanda, categoria);
        });

        if (esisteCategoria) {
            aggiungiOpzione( elementi.categorySelect, categoria, formattaCategoriaFiltro(categoria) );
        }
    });

    aggiungiOpzione(
        elementi.levelSelect,
        "tutti",
        "Tutti i livelli"
    );

    livelliOrdinati.forEach(livello => {
        const esisteLivello = databaseQuiz.some(domanda => {
            return domanda.livello === livello;
        });

        if (esisteLivello) {
            aggiungiOpzione(
                elementi.levelSelect,
                livello,
                formattaTesto(livello)
            );
        }
    });
}

function aggiungiOpzione(select, valore, testo) {
    const option = document.createElement("option");
    option.value = valore;
    option.textContent = testo;
    select.appendChild(option);
}

function aggiornaInfoDomandeDisponibili() {
    const domandeFiltrate = ottieniDomandeFiltrate();
    const richieste = ottieniNumeroDomandeRichiesto();
    const numeroTest = Math.min(richieste, domandeFiltrate.length);

    if (domandeFiltrate.length === 0) {
        elementi.availableInfo.textContent =
            "Nessuna domanda disponibile per questo filtro.";

        elementi.startButton.disabled = true;
        return;
    }

    elementi.startButton.disabled = false;

    if (numeroTest < richieste) {
        elementi.availableInfo.textContent =
            `Domande disponibili: ${domandeFiltrate.length}. ` +
            `Il test userà ${numeroTest} domande per evitare ripetizioni.`;
    } else {
        elementi.availableInfo.textContent =
            `Domande disponibili: ${domandeFiltrate.length}. ` +
            `Il test userà ${numeroTest} domande.`;
    }
}

function ottieniDomandeFiltrate() {
    const categoriaScelta = elementi.categorySelect.value;
    const livelloScelto = elementi.levelSelect.value;

    return databaseQuiz.filter(domanda => {
        const categoriaOk = domandaCorrispondeCategoria(domanda, categoriaScelta);

        const livelloOk =
            livelloScelto === "tutti" ||
            domanda.livello === livelloScelto;

        return categoriaOk && livelloOk;
    });
}

function domandaCorrispondeCategoria(domanda, categoriaScelta) {
    if (categoriaScelta === "tutte") {
        return true;
    }

    if (categoriaScelta === "logica_visiva") {
        return domanda.sottocategoria === "logica_visiva";
    }

    if (categoriaScelta === "logica") {
        return (
            domanda.categoria === "logica" &&
            domanda.sottocategoria !== "logica_visiva"
        );
    }

    return domanda.categoria === categoriaScelta;
}

function formattaCategoriaFiltro(categoria) {
    if (categoria === "logica_visiva") {
        return "Logica Visiva";
    }

    return formattaTesto(categoria);
}

function ottieniNumeroDomandeRichiesto() {
    const valore = elementi.questionCountSelect.value;

    if (valore === "all") {
        return ottieniDomandeFiltrate().length;
    }

    return Number(valore);
}

function creaChiaveFiltro() {
    return `${elementi.categorySelect.value}__${elementi.levelSelect.value}`;
}

function iniziaTest() {
    const domandeFiltrate = ottieniDomandeFiltrate();

    if (domandeFiltrate.length === 0) {
        return;
    }

    const richieste = ottieniNumeroDomandeRichiesto();
    const numeroEffettivo = Math.min(richieste, domandeFiltrate.length);

    domandeTest = prendiDomandeSenzaRipetere(
        domandeFiltrate,
        numeroEffettivo
    );

    indiceDomandaCorrente = 0;
    risposteCorrette = 0;
    risposteSbagliate = 0;
    rispostaGiaData = false;

    mostraSolo(elementi.quizBox);
    mostraDomandaCorrente();
}

function prendiDomandeSenzaRipetere(domandeFiltrate, numeroDaPrendere) {
    const chiaveFiltro = creaChiaveFiltro();

    const idsDisponibili = domandeFiltrate.map(domanda => {
        return domanda.id;
    });

    const setIdsDisponibili = new Set(idsDisponibili);

    let coda = codeDomandePerFiltro[chiaveFiltro] || [];

    /*
        Se il filtro cambia o alcune domande non esistono più,
        puliamo la coda.
    */
    coda = coda.filter(id => {
        return setIdsDisponibili.has(id);
    });

    if (coda.length === 0) {
        coda = mescolaArray(idsDisponibili);
    }

    const idsScelti = [];

    while (idsScelti.length < numeroDaPrendere) {
        if (coda.length === 0) {
            /*
                Qui significa che il giro è finito.
                Solo ora il sistema rimischia il gruppo.
                Nel nuovo giro evitiamo di ripescare dentro lo stesso test.
            */
            const idsNonUsatiInQuestoTest = idsDisponibili.filter(id => {
                return !idsScelti.includes(id);
            });

            coda = mescolaArray(idsNonUsatiInQuestoTest);
        }

        const prossimoId = coda.shift();

        if (!idsScelti.includes(prossimoId)) {
            idsScelti.push(prossimoId);
        }
    }

    codeDomandePerFiltro[chiaveFiltro] = coda;

    return idsScelti.map(id => {
        return domandeFiltrate.find(domanda => {
            return domanda.id === id;
        });
    });
}


let codaPosizioniCorretteQuizAi = [];

function mescolaArrayQuizAi(lista) {
    for (let indice = lista.length - 1; indice > 0; indice -= 1) {
        const indiceCasuale = Math.floor(Math.random() * (indice + 1));
        const temporaneo = lista[indice];

        lista[indice] = lista[indiceCasuale];
        lista[indiceCasuale] = temporaneo;
    }

    return lista;
}

function prendiPosizioneCorrettaQuizAi(numeroOpzioni) {
    if (codaPosizioniCorretteQuizAi.length === 0) {
        codaPosizioniCorretteQuizAi = [];

        for (let indice = 0; indice < numeroOpzioni; indice += 1) {
            codaPosizioniCorretteQuizAi.push(indice);
        }

        mescolaArrayQuizAi(codaPosizioniCorretteQuizAi);
    }

    return codaPosizioniCorretteQuizAi.shift();
}

function creaOpzioniMescolateQuizAi(opzioniOriginali, rispostaCorretta) {
    if (!Array.isArray(opzioniOriginali)) {
        return [];
    }

    const opzioniConIndice = opzioniOriginali.map((testo, indiceOriginale) => {
        return {
            testo,
            indiceOriginale,
        };
    });

    const opzioneCorretta = opzioniConIndice.find(opzione => {
        return opzione.testo === rispostaCorretta;
    });

    if (!opzioneCorretta) {
        return mescolaArrayQuizAi(opzioniConIndice);
    }

    const opzioniSbagliate = opzioniConIndice.filter(opzione => {
        return opzione !== opzioneCorretta;
    });

    mescolaArrayQuizAi(opzioniSbagliate);

    const posizioneCorretta = prendiPosizioneCorrettaQuizAi(opzioniConIndice.length);

    const opzioniFinali = [...opzioniSbagliate];

    opzioniFinali.splice(posizioneCorretta, 0, opzioneCorretta);

    return opzioniFinali;
}

function mostraDomandaCorrente() {
    rispostaGiaData = false;

    const domanda = domandeTest[indiceDomandaCorrente];
    const numeroDomanda = indiceDomandaCorrente + 1;
    const totaleDomande = domandeTest.length;

    elementi.progressText.textContent =
        `Domanda ${numeroDomanda}/${totaleDomande}`;

    elementi.scoreText.textContent =
        `Corrette: ${risposteCorrette}`;

    /*
        Qui mostriamo solo categoria e livello.
        L'ID interno della domanda rimane nel database,
        ma non viene mostrato all'utente finale.
    */
    const categoriaMeta =
        domanda.sottocategoria === "logica_visiva"
            ? "Logica Visiva"
            : formattaTesto(domanda.categoria);

    elementi.questionMeta.textContent =
        `${categoriaMeta} · ${formattaTesto(domanda.livello)}`;

    const percentualeAvanzamento =
        (indiceDomandaCorrente / totaleDomande) * 100;

    elementi.progressFill.style.width = `${percentualeAvanzamento}%`;

    elementi.questionText.textContent = domanda.domanda;

    mostraImmagineDomanda(domanda);
    mostraOpzioni(domanda);

    elementi.feedbackBox.className = "feedback hidden";
    elementi.feedbackBox.textContent = "";

    elementi.explanationBox.classList.add("hidden");
    elementi.explanationText.textContent = "";

    elementi.nextButton.classList.add("hidden");

    if (indiceDomandaCorrente === domandeTest.length - 1) {
        elementi.nextButton.textContent = "Vedi report finale";
    } else {
        elementi.nextButton.textContent = "Prossima domanda";
    }
}

function mostraImmagineDomanda(domanda) {
    elementi.questionImageBox.innerHTML = "";
    elementi.questionImageBox.classList.add("hidden");

    if (!domanda.immagine_domanda) {
        return;
    }

    const immagine = document.createElement("img");
    immagine.src = risolviPercorsoAsset(domanda.immagine_domanda);
    immagine.alt = "Immagine della domanda";

    elementi.questionImageBox.appendChild(immagine);
    elementi.questionImageBox.classList.remove("hidden");
}

function mostraOpzioni(domanda) {
    elementi.optionsBox.innerHTML = "";

    const opzioniMescolateQuizAi = creaOpzioniMescolateQuizAi(
        domanda.opzioni,
        domanda.risposta_corretta
    );

    opzioniMescolateQuizAi.forEach((opzioneMescolata, indice) => {
        const opzione = opzioneMescolata.testo;
        const indiceOriginaleOpzione = opzioneMescolata.indiceOriginale;
        const bottone = document.createElement("button");
        bottone.className = "option-button";
        bottone.type = "button";

        const testo = document.createElement("span");
        testo.textContent = opzione;
        bottone.appendChild(testo);

        const immagineOpzione = ottieniImmagineOpzione(
            domanda,
            opzione,
            indice
        );

        if (immagineOpzione) {
            const img = document.createElement("img");
            img.className = "option-image";
            img.src = risolviPercorsoAsset(immagineOpzione);
            img.alt = `Opzione ${opzione}`;
            bottone.appendChild(img);
        }

        bottone.addEventListener("click", () => {
            controllaRisposta(opzione, bottone);
        });

        elementi.optionsBox.appendChild(bottone);
    });
}

function ottieniImmagineOpzione(domanda, opzione, indice) {
    if (!domanda.immagini_opzioni) {
        return null;
    }

    if (Array.isArray(domanda.immagini_opzioni)) {
        return domanda.immagini_opzioni[indice] || null;
    }

    if (typeof domanda.immagini_opzioni === "object") {
        return (
            domanda.immagini_opzioni[opzione] ||
            domanda.immagini_opzioni[String(indice)] ||
            domanda.immagini_opzioni[String(indice + 1)] ||
            null
        );
    }

    return null;
}

function controllaRisposta(opzioneScelta, bottoneScelto) {
    if (rispostaGiaData) {
        return;
    }

    rispostaGiaData = true;

    const domanda = domandeTest[indiceDomandaCorrente];
    const rispostaCorretta = domanda.risposta_corretta;
    const corretta = opzioneScelta === rispostaCorretta;

    const bottoni = elementi.optionsBox.querySelectorAll(".option-button");

    bottoni.forEach(bottone => {
        bottone.disabled = true;

        const testoBottone = bottone.querySelector("span").textContent;

        if (testoBottone === rispostaCorretta) {
            bottone.classList.add("correct");
        }
    });

    if (corretta) {
        risposteCorrette += 1;

        elementi.feedbackBox.textContent = "Risposta corretta!";
        elementi.feedbackBox.className = "feedback good";

        lanciaCoriandoliConDissolvenza();

    } else {
        risposteSbagliate += 1;

        bottoneScelto.classList.add("wrong");

        elementi.feedbackBox.textContent =
            `Risposta sbagliata. La risposta corretta era: ${rispostaCorretta}`;

        elementi.feedbackBox.className = "feedback bad";
    }

    elementi.scoreText.textContent =
        `Corrette: ${risposteCorrette}`;

    elementi.explanationText.textContent =
        ottieniSpiegazioneRisposta(domanda, opzioneScelta);

    elementi.explanationBox.classList.remove("hidden");
    elementi.feedbackBox.classList.remove("hidden");
    elementi.nextButton.classList.remove("hidden");
}

function vaiAllaProssimaDomanda() {
    if (indiceDomandaCorrente < domandeTest.length - 1) {
        indiceDomandaCorrente += 1;
        mostraDomandaCorrente();
        return;
    }

    mostraReportFinale();
}

function mostraReportFinale() {
    const totale = domandeTest.length;
    const percentuale = Math.round((risposteCorrette / totale) * 100);
    const voto = Number(((risposteCorrette / totale) * 10).toFixed(1));
    const profilo = ottieniProfiloRisultato(voto);

    elementi.progressFill.style.width = "100%";

    elementi.resultVisual.className = `result-visual ${profilo.classe}`;
    elementi.resultEmoji.textContent = profilo.emoji;
    elementi.resultTitle.textContent = profilo.titolo;
    elementi.resultPhrase.textContent = profilo.frase;

    elementi.totalQuestionsResult.textContent = totale;
    elementi.correctResult.textContent = risposteCorrette;
    alexMostraPremioFinaleGenerale();
    elementi.wrongResult.textContent = risposteSbagliate;
    elementi.percentageResult.textContent = `${percentuale}%`;

    elementi.gradeResult.textContent = `${formattaVoto(voto)}/10`;
    elementi.judgementResult.textContent = profilo.giudizio;

    mostraSolo(elementi.resultBox);

    if (voto >= 8) {
        lanciaCoriandoliConDissolvenza(true);
    }
}

function ottieniProfiloRisultato(voto) {
    if (voto === 10) {
        return {
            classe: "grade-10",
            emoji: "🏆🚀",
            titolo: "10 pieno! Prestazione eccellente",
            giudizio: "Eccellente",
            frase:
                "Hai completato il test in modo perfetto. Risultato da campione: precisione, concentrazione e preparazione al massimo."
        };
    }

    if (voto >= 9) {
        return {
            classe: "grade-9",
            emoji: "🥇✨",
            titolo: "Risultato ottimo",
            giudizio: "Ottimo",
            frase:
                "Hai fatto un lavoro di altissimo livello. Pochissimi errori e grande controllo degli argomenti."
        };
    }

    if (voto >= 8) {
        return {
            classe: "grade-8",
            emoji: "🌟💪",
            titolo: "Bel risultato",
            giudizio: "Buono",
            frase:
                "Sei sulla strada giusta. La base è forte e con un po' di allenamento puoi arrivare facilmente ancora più in alto."
        };
    }

    if (voto >= 7) {
        return {
            classe: "grade-7",
            emoji: "👍📘",
            titolo: "Buona prova",
            giudizio: "Discreto",
            frase:
                "Hai superato bene il test. Ci sono alcuni punti da sistemare, ma il percorso è positivo."
        };
    }

    if (voto >= 6) {
        return {
            classe: "grade-6",
            emoji: "🌱📚",
            titolo: "Base sufficiente",
            giudizio: "Sufficiente",
            frase:
                "Hai raggiunto la sufficienza. Ora l'obiettivo è trasformare gli errori in allenamento mirato."
        };
    }

    return {
        classe: "grade-low",
        emoji: "🔁🔥",
        titolo: "Allenamento in corso",
        giudizio: "Da migliorare",
        frase:
            "Non è un fallimento: è una mappa degli argomenti da rinforzare. Ripeti il test, leggi le spiegazioni e vedrai miglioramenti."
    };
}

function tornaAlleImpostazioni() {
    aggiornaInfoDomandeDisponibili();
    mostraSolo(elementi.setupBox);
}

function mescolaArray(arrayOriginale) {
    const array = [...arrayOriginale];

    for (let i = array.length - 1; i > 0; i -= 1) {
        const indiceCasuale = Math.floor(Math.random() * (i + 1));

        [array[i], array[indiceCasuale]] = [
            array[indiceCasuale],
            array[i]
        ];
    }

    return array;
}

function formattaTesto(testo) {
    if (!testo) {
        return "";
    }

    return testo
        .replaceAll("_", " ")
        .replace(/\b\w/g, lettera => {
            return lettera.toUpperCase();
        });
}

function formattaVoto(voto) {
    if (Number.isInteger(voto)) {
        return String(voto);
    }

    return String(voto).replace(".", ",");
}

function risolviPercorsoAsset(percorso) {
    if (
        percorso.startsWith("http://") ||
        percorso.startsWith("https://") ||
        percorso.startsWith("../") ||
        percorso.startsWith("/")
    ) {
        return percorso;
    }

    return `../${percorso}`;
}

async function generaQuizPersonalizzatoJson(evento) {
    evento.preventDefault();

    try {
        mostraStatoQuizCreator("Lettura materiale in corso...", false);
        disabilitaAzioniQuizJson();

        const dati = leggiCampiQuizPersonalizzato();
        const validazione = validaImpostazioniQuizPersonalizzato(dati);

        if (!validazione.valid) {
            mostraStatoQuizCreator(validazione.message, true);
            return;
        }

        const testoSorgente = await leggiTestoSorgenteQuiz(dati.file);
        const domandeTrovate = estraiDomandeDaSorgente(testoSorgente, dati.file);

        if (domandeTrovate.length === 0) {
            mostraStatoQuizCreator(
                "Non ho trovato domande valide. Usa JSON strutturato o testo con Domanda, A/B/C/D, Corretta e Spiegazione.",
                true
            );
            return;
        }

        const domandeNormalizzate = normalizzaDomandeImportate(
            domandeTrovate,
            dati
        );

        if (domandeNormalizzate.length === 0) {
            mostraStatoQuizCreator(
                "Le domande trovate sono incomplete: servono domanda, 4 risposte e risposta corretta.",
                true
            );
            return;
        }

        const quantita = ottieniNumeroDomandeDaGenerare(
            dati,
            domandeNormalizzate.length
        );

        const domandeScelte = mescolaArray(domandeNormalizzate).slice(
            0,
            quantita
        );

        const quiz = creaQuizPersonalizzato(dati, domandeScelte, {
            trovate: domandeNormalizzate.length,
            usate: domandeScelte.length,
        });

        ultimoQuizPersonalizzatoJson = JSON.stringify(quiz, null, 2);
        elementi.quizJsonOutput.textContent = ultimoQuizPersonalizzatoJson;
        elementi.copyQuizJsonButton.disabled = false;
        elementi.downloadQuizJsonButton.disabled = false;
        elementi.creatorQuestionCount.textContent =
            `${domandeScelte.length} domande generate`;

        mostraStatoQuizCreator(
            `Test generato: ${domandeScelte.length} domande su ${domandeNormalizzate.length} disponibili.`,
            false
        );
    avviaTestPersonalizzatoGenerato(domandeScelte);
    } catch (errore) {
        mostraStatoQuizCreator(
            errore.message || "Errore durante la generazione del test.",
            true
        );
    }
}


function ottieniDomandeDatabasePerQuizCreator(dati) {
  const categoriaRichiesta = creaSlugQuizCreator(dati.materia);
  const livelloRichiesto = dati.livello;

  return databaseQuiz
    .filter(domanda => {
      const categoriaDomanda = creaSlugQuizCreator(domanda.categoria || "");
      const sottocategoriaDomanda = creaSlugQuizCreator(domanda.sottocategoria || "");

      const categoriaOk =
        categoriaDomanda === categoriaRichiesta ||
        sottocategoriaDomanda === categoriaRichiesta ||
        domandaCorrispondeCategoria(domanda, categoriaRichiesta);

      const livelloOk =
        !livelloRichiesto ||
        livelloRichiesto === "tutti" ||
        domanda.livello === livelloRichiesto;

      return categoriaOk && livelloOk;
    })
    .map((domanda, index) => {
      const opzioni = Array.isArray(domanda.opzioni)
        ? domanda.opzioni.slice(0, 4)
        : normalizzaOpzioniImportate(domanda.opzioni);

      return {
        ...domanda,
        id: domanda.id || creaIdQuizPersonalizzato(
          categoriaRichiesta,
          livelloRichiesto,
          index + 1
        ),
        categoria: domanda.categoria || categoriaRichiesta,
        livello: domanda.livello || livelloRichiesto,
        tipo: domanda.tipo || "testo",
        tipo_domanda: domanda.tipo_domanda || "testo",
        opzioni,
        tags: Array.isArray(domanda.tags)
          ? domanda.tags
          : [categoriaRichiesta, "database"],
        difficolta:
          domanda.difficolta ||
          ottieniDifficoltaDaLivello(domanda.livello || livelloRichiesto),
      };
    })
    .filter(domanda => {
      return (
        domanda.domanda &&
        Array.isArray(domanda.opzioni) &&
        domanda.opzioni.length === 4 &&
        domanda.risposta_corretta &&
        domanda.opzioni.includes(domanda.risposta_corretta)
      );
    });
}

function leggiCampiQuizPersonalizzato() {
    return {
        titolo: elementi.creatorTitle.value.trim(),
        materia: ottieniMateriaQuizCreator(),
        livello: elementi.creatorLevel.value,
        questionMode: elementi.creatorQuestionMode.value,
        customCount: Number(elementi.creatorCustomCount.value),
        file: elementi.creatorFile.files?.[0] || null,
        sourceText: elementi.creatorSourceText.value.trim(),
    };
}

function ottieniMateriaQuizCreator() {
    const personalizzata = elementi.creatorCustomSubject.value.trim();

    if (personalizzata) {
        return personalizzata;
    }

    return elementi.creatorSubject.value;
}

function validaImpostazioniQuizPersonalizzato(dati) {
    if (!dati.titolo) {
        return { valid: false, message: "Inserisci il titolo del quiz." };
    }

    if (!dati.materia) {
        return { valid: false, message: "Scegli o scrivi la materia." };
    }
  /*
    Se non carichi file e non incolli testo, il generatore usa
    le domande già presenti nel database finale filtrando per materia e livello.
  */

    if (
        dati.questionMode === "custom" &&
        (!Number.isInteger(dati.customCount) || dati.customCount < 1)
    ) {
        return {
            valid: false,
            message: "Inserisci un numero di domande valido.",
        };
    }

    return { valid: true, message: "" };
}

async function leggiTestoSorgenteQuiz(file) {
    if (file) {
        if (isPdfFile(file)) {
            return await estraiTestoDaPdf(file);
        }

        return await file.text();
    }

    return elementi.creatorSourceText.value.trim();
}

function isPdfFile(file) {
    return (
        file.type === "application/pdf" ||
        file.name.toLowerCase().endsWith(".pdf")
    );
}

async function estraiTestoDaPdf(file) {
    try {
        const pdfjsLib = await import(
            "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.10.38/pdf.min.mjs"
        );

        pdfjsLib.GlobalWorkerOptions.workerSrc =
            "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.10.38/pdf.worker.min.mjs";

        const buffer = await file.arrayBuffer();
        const pdf = await pdfjsLib.getDocument({ data: buffer }).promise;
        const pagine = [];

        for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber += 1) {
            const pagina = await pdf.getPage(pageNumber);
            const contenuto = await pagina.getTextContent();
            const testoPagina = contenuto.items
                .map(item => item.str)
                .join(" ");

            pagine.push(testoPagina);
        }

        return pagine.join("\n\n");
    } catch (errore) {
        throw new Error(
            "Non riesco a leggere questo PDF. Usa un PDF con testo selezionabile oppure carica JSON/TXT."
        );
    }
}

function estraiDomandeDaSorgente(testo, file) {
    const testoPulito = String(testo || "").trim();

    if (!testoPulito) {
        return [];
    }

    if (sembraJsonQuiz(testoPulito, file)) {
        try {
            const json = JSON.parse(testoPulito);
            return estraiDomandeDaJson(json);
        } catch (errore) {
            throw new Error("Il file JSON non è valido.");
        }
    }

    return estraiDomandeDaTesto(testoPulito);
}

function sembraJsonQuiz(testo, file) {
    return (
        file?.name?.toLowerCase().endsWith(".json") ||
        testo.startsWith("{") ||
        testo.startsWith("[")
    );
}

function estraiDomandeDaJson(json) {
    if (Array.isArray(json)) {
        return json;
    }

    if (!json || typeof json !== "object") {
        return [];
    }

    const possibiliListe = [
        json.domande,
        json.questions,
        json.quiz,
        json.items,
        json.data,
    ];

    const lista = possibiliListe.find(Array.isArray);

    return lista || [];
}

function estraiDomandeDaTesto(testo) {
    const blocchi = testo
        .replace(/\r/g, "")
        .split(/\n\s*\n(?=\s*(?:Domanda|Q|Question|\d+[\).]))/i)
        .map(blocco => blocco.trim())
        .filter(Boolean);

    return blocchi
        .map(parseBloccoDomandaTestuale)
        .filter(Boolean);
}

function parseBloccoDomandaTestuale(blocco) {
    const righe = blocco
        .split("\n")
        .map(riga => riga.trim())
        .filter(Boolean);

    let domanda = "";
    const opzioni = {};
    let corretta = "";
    let spiegazione = "";

    righe.forEach((riga, index) => {
        const opzione = riga.match(/^([A-D])[\)\.:\-]\s*(.+)$/i);

        if (opzione) {
            opzioni[opzione[1].toUpperCase()] = opzione[2].trim();
            return;
        }

        const risposta = riga.match(/^(corretta|risposta corretta|answer|correct)\s*[:\-]\s*(.+)$/i);

        if (risposta) {
            corretta = risposta[2].trim();
            return;
        }

        const spiegazioneMatch = riga.match(/^(spiegazione|explanation)\s*[:\-]\s*(.+)$/i);

        if (spiegazioneMatch) {
            spiegazione = spiegazioneMatch[2].trim();
            return;
        }

        const domandaMatch = riga.match(/^(domanda|question|q)\s*[:\-]\s*(.+)$/i);

        if (domandaMatch) {
            domanda = domandaMatch[2].trim();
            return;
        }

        if (index === 0 && !domanda) {
            domanda = riga.replace(/^\d+[\).]\s*/, "").trim();
        }
    });

    return {
        domanda,
        opzioni,
        risposta_corretta: corretta,
        spiegazione,
    };
}

function normalizzaDomandeImportate(domande, dati) {
    const categoria = creaSlugQuizCreator(dati.materia);
    const livello = dati.livello;

    return domande
        .map((domanda, index) => {
            return normalizzaDomandaImportata(
                domanda,
                categoria,
                livello,
                index + 1
            );
        })
        .filter(Boolean);
}

function normalizzaDomandaImportata(domanda, categoria, livello, index) {
    if (!domanda || typeof domanda !== "object") {
        return null;
    }

    const testoDomanda = prendiPrimoValore(domanda, [
        "domanda",
        "question",
        "testo",
        "prompt",
        "quesito",
    ]);

    const opzioni = normalizzaOpzioniImportate(
        prendiPrimoValore(domanda, [
            "opzioni",
            "options",
            "risposte",
            "answers",
            "choices",
        ])
    );

    const rispostaOriginale = prendiPrimoValore(domanda, [
        "risposta_corretta",
        "rispostaCorretta",
        "correct_answer",
        "correctAnswer",
        "correct",
        "answer",
        "soluzione",
    ]);

    const rispostaCorretta = normalizzaRispostaCorrettaImportata(
        rispostaOriginale,
        opzioni
    );

    const spiegazione = prendiPrimoValore(domanda, [
        "spiegazione",
        "explanation",
        "feedback",
        "motivo",
    ]) || "Spiegazione da completare.";

    if (
        !testoDomanda ||
        opzioni.length < 4 ||
        !rispostaCorretta ||
        !opzioni.includes(rispostaCorretta)
    ) {
        return null;
    }

    return {
        id: creaIdQuizPersonalizzato(categoria, livello, index),
        categoria,
        livello,
        tipo: "testo",
        tipo_domanda: "testo",
        domanda: String(testoDomanda).trim(),
        opzioni: opzioni.slice(0, 4),
        risposta_corretta: rispostaCorretta,
        spiegazione: String(spiegazione).trim(),
        tags: [
            categoria,
            "personalizzato",
        ],
        difficolta: ottieniDifficoltaDaLivello(livello),
    };
}

function prendiPrimoValore(oggetto, chiavi) {
    for (const chiave of chiavi) {
        if (oggetto[chiave] !== undefined && oggetto[chiave] !== null) {
            return oggetto[chiave];
        }
    }

    return "";
}

function normalizzaOpzioniImportate(opzioniOriginali) {
    if (Array.isArray(opzioniOriginali)) {
        return opzioniOriginali
            .map(opzione => {
                if (typeof opzione === "object" && opzione !== null) {
                    return String(
                        opzione.testo ||
                        opzione.text ||
                        opzione.value ||
                        opzione.risposta ||
                        ""
                    ).trim();
                }

                return String(opzione || "").trim();
            })
            .filter(Boolean);
    }

    if (opzioniOriginali && typeof opzioniOriginali === "object") {
        return ["A", "B", "C", "D"]
            .map(lettera => String(opzioniOriginali[lettera] || "").trim())
            .filter(Boolean);
    }

    return [];
}

function normalizzaRispostaCorrettaImportata(rispostaOriginale, opzioni) {
    const risposta = String(rispostaOriginale || "").trim();
    const lettera = risposta.toUpperCase();
    const indiceLettera = ["A", "B", "C", "D"].indexOf(lettera);

    if (indiceLettera >= 0) {
        return opzioni[indiceLettera] || "";
    }

    const rispostaNormalizzata = normalizzaTestoQuizCreator(risposta);

    return opzioni.find(opzione => {
        return normalizzaTestoQuizCreator(opzione) === rispostaNormalizzata;
    }) || "";
}

function ottieniNumeroDomandeDaGenerare(dati, disponibili) {
    if (dati.questionMode === "all") {
        return disponibili;
    }

    if (dati.questionMode === "custom") {
        return Math.min(dati.customCount, disponibili);
    }

    return Math.min(Number(dati.questionMode), disponibili);
}

function creaQuizPersonalizzato(dati, domande, statistiche) {
    const categoria = creaSlugQuizCreator(dati.materia);

    return {
        titolo_quiz: dati.titolo,
        materia: categoria,
        formato: "alex-ai-quiz-database-v1",
        creato_il: new Date().toISOString(),
        origine: {
            file: dati.file?.name || "testo incollato",
            domande_trovate: statistiche.trovate,
            domande_generate: statistiche.usate,
        },
        domande,
    };
}

function creaIdQuizPersonalizzato(categoria, livello, index) {
    const categoriaBreve = categoria
        .split("_")
        .map(parte => parte.slice(0, 3))
        .join("")
        .toUpperCase()
        .slice(0, 9) || "QUIZ";

    const livelloBreve = {
        facile: "FAC",
        intermedio: "INT",
        avanzato: "AV",
    }[livello] || "CUS";

    return `CUSTOM-${categoriaBreve}-${livelloBreve}-${String(index).padStart(4, "0")}`;
}

function ottieniDifficoltaDaLivello(livello) {
    return {
        facile: 1,
        intermedio: 2,
        avanzato: 3,
    }[livello] || 1;
}

function normalizzaTestoQuizCreator(testo) {
    return String(testo || "")
        .toLowerCase()
        .replace(/\s+/g, " ")
        .trim();
}

function creaSlugQuizCreator(testo) {
    return String(testo || "")
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/[^a-z0-9]+/g, "_")
        .replace(/^_+|_+$/g, "")
        || "quiz_personalizzato";
}

function aggiornaStatoFileQuizCreator() {
    const file = elementi.creatorFile.files?.[0];

    if (!file) {
        return;
    }

    mostraStatoQuizCreator(`File selezionato: ${file.name}`, false);
}

function mostraStatoQuizCreator(messaggio, errore) {
    elementi.creatorStatus.textContent = messaggio;
    elementi.creatorStatus.classList.toggle("error", Boolean(errore));
}

function disabilitaAzioniQuizJson() {
    ultimoQuizPersonalizzatoJson = "";
    elementi.copyQuizJsonButton.disabled = true;
    elementi.downloadQuizJsonButton.disabled = true;
}

async function copiaQuizPersonalizzatoJson() {
    if (!ultimoQuizPersonalizzatoJson) {
        mostraStatoQuizCreator("Genera prima il JSON.", true);
        return;
    }

    try {
        await navigator.clipboard.writeText(ultimoQuizPersonalizzatoJson);
        mostraStatoQuizCreator("JSON copiato negli appunti.", false);
    } catch (errore) {
        mostraStatoQuizCreator(
            "Copia non riuscita: seleziona il testo dall'anteprima.",
            true
        );
    }
}

function scaricaQuizPersonalizzatoJson() {
    if (!ultimoQuizPersonalizzatoJson) {
        mostraStatoQuizCreator("Genera prima il JSON.", true);
        return;
    }

    const titolo = elementi.creatorTitle.value.trim() || "quiz-personalizzato";
    const nomeFile = `${creaSlugQuizCreator(titolo)}.json`;
    const blob = new Blob(
        [ultimoQuizPersonalizzatoJson],
        { type: "application/json;charset=utf-8" }
    );
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = nomeFile;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);

    mostraStatoQuizCreator(`File pronto: ${nomeFile}`, false);
}

function filtraDomandeVisualiNonValide(domande) {
    return domande.filter(domanda => {
        const risultato = validateVisualLogicQuestion(domanda);

        if (risultato.valid) {
            return true;
        }

        console.error(
            `Domanda logica visiva esclusa: ${domanda.id || "ID_MANCANTE"}`,
            risultato.errors
        );

        return false;
    });
}

function isVisualLogicQuestion(question) {
    return (
        question?.sottocategoria === "logica_visiva" ||
        String(question?.id || "").startsWith("LOG-VIS")
    );
}

function validateVisualLogicQuestion(question) {
    const errors = [];

    if (!isVisualLogicQuestion(question)) {
        return { valid: true, errors };
    }

    const visualLogic = question.visual_logic;

    if (!visualLogic || typeof visualLogic !== "object") {
        return {
            valid: false,
            errors: ["Manca il contratto visual_logic della domanda visiva."],
        };
    }

    const sequence = Array.isArray(visualLogic.sequence)
        ? visualLogic.sequence
        : [];

    const expectedAnswer = visualLogic.expected_answer;
    const usesPosition = Boolean(visualLogic.uses_position);

    if (sequence.length === 0) {
        errors.push("visual_logic.sequence deve contenere almeno una figura.");
    }

    if (!expectedAnswer || typeof expectedAnswer !== "object") {
        errors.push("Manca visual_logic.expected_answer.");
    }

    sequence.forEach((figure, index) => {
        errors.push(
            ...validateVisualFigure(
                figure,
                `sequenza figura ${index + 1}`,
                usesPosition
            )
        );
    });

    if (expectedAnswer) {
        errors.push(
            ...validateVisualFigure(
                expectedAnswer,
                "risposta corretta attesa",
                usesPosition
            )
        );
    }

    const optionMap = visualLogic.options || {};
    const correct = question.risposta_corretta;
    const correctFigure = optionMap[correct];

    if (!correctFigure) {
        errors.push("La risposta corretta non è presente nelle opzioni visuali.");
    } else if (!figuresMatch(correctFigure, expectedAnswer)) {
        errors.push("La risposta corretta non rispetta la regola dichiarata.");
    }

    (question.opzioni || []).forEach(option => {
        const figure = optionMap[option];

        errors.push(
            ...validateVisualFigure(
                figure,
                `opzione ${option}`,
                usesPosition
            )
        );

        if (option !== correct && figuresMatch(figure, correctFigure)) {
            errors.push(`L'opzione ${option} è uguale alla risposta corretta.`);
        }
    });

    const colorRule = visualLogic.rule?.color_alternation;

    if (colorRule?.enabled) {
        errors.push(
            ...validateColorAlternation(
                sequence,
                expectedAnswer,
                colorRule.colors || []
            )
        );
    }

    errors.push(...validateMirrorInstruction(question, visualLogic));
    errors.push(...validateVisualExplanation(question, expectedAnswer, visualLogic));
    errors.push(...validateWrongOptionExplanations(question));

    return {
        valid: errors.length === 0,
        errors,
    };
}

function validateVisualFigure(figure, label, usesPosition) {
    const errors = [];

    if (!figure || typeof figure !== "object") {
        return [`${label}: la figura deve essere un oggetto strutturato.`];
    }

    const outerShape = normalizeVisualText(figure.outer_shape);
    const outerColor = normalizeVisualText(figure.outer_color);
    const expectedSides = VISUAL_SHAPE_SIDES[outerShape];

    if (!outerShape) {
        errors.push(`${label}: manca la forma esterna.`);
    }

    if (!outerColor) {
        errors.push(`${label}: manca il colore esterno.`);
    }

    if (expectedSides === undefined) {
        errors.push(`${label}: forma esterna non riconosciuta.`);
    } else if (!Number.isInteger(figure.sides)) {
        errors.push(`${label}: manca il numero di lati.`);
    } else if (figure.sides !== expectedSides) {
        errors.push(`${label}: numero di lati incoerente con la forma.`);
    }

    if (!Array.isArray(figure.inner_objects)) {
        errors.push(`${label}: manca l'elenco completo degli oggetti interni.`);
        return errors;
    }

    figure.inner_objects.forEach((item, index) => {
        const itemLabel = `${label}, oggetto interno ${index + 1}`;

        if (!item || typeof item !== "object") {
            errors.push(`${itemLabel}: deve essere un oggetto strutturato.`);
            return;
        }

        if (!normalizeVisualText(item.type)) {
            errors.push(`${itemLabel}: manca il tipo.`);
        }

        if (!normalizeVisualText(item.color)) {
            errors.push(`${itemLabel}: manca il colore.`);
        }

        if (!Number.isInteger(item.quantity) || item.quantity < 0) {
            errors.push(`${itemLabel}: manca una quantità valida.`);
        }

        if (usesPosition && !normalizeVisualText(item.position)) {
            errors.push(`${itemLabel}: manca la posizione.`);
        }
    });

    return errors;
}

function validateColorAlternation(sequence, expectedAnswer, colors) {
    const errors = [];

    if (!Array.isArray(colors) || colors.length < 2) {
        return ["La regola di alternanza colori deve dichiarare almeno due colori."];
    }

    [...sequence, expectedAnswer].forEach((figure, index) => {
        const observed = normalizeVisualText(figure?.outer_color);
        const expected = normalizeVisualText(colors[index % colors.length]);

        if (observed !== expected) {
            errors.push(
                `Alternanza colori non rispettata in posizione ${index + 1}.`
            );
        }
    });

    return errors;
}

function validateMirrorInstruction(question, visualLogic) {
    const errors = [];
    const sequence = Array.isArray(visualLogic.sequence)
        ? visualLogic.sequence
        : [];

    const mirrorAxis = normalizeVisualText(visualLogic.rule?.mirror_axis);
    const isMirror = (
        normalizeVisualText(visualLogic.type) === "mirror" ||
        mirrorAxis !== ""
    );

    if (!isMirror || sequence.length !== 1) {
        return errors;
    }

    const questionText = normalizeVisualText(question.domanda);

    if (!/figura speculare rispetto all'asse (verticale|orizzontale)/.test(questionText)) {
        errors.push(
            "Domanda speculare ambigua: manca l'asse verticale/orizzontale nella consegna."
        );
    }

    if (!["verticale", "orizzontale"].includes(mirrorAxis)) {
        errors.push("La regola speculare deve dichiarare asse verticale o orizzontale.");
    }

    return errors;
}

function validateVisualExplanation(question, expectedAnswer, visualLogic) {
    const errors = [];
    const explanation = normalizeVisualText(question.spiegazione);
    const requirements = getVisualExplanationRequirements(visualLogic);

    if (explanation.length < 45) {
        errors.push("La spiegazione è troppo breve per una domanda visiva.");
    }

    if (!expectedAnswer) {
        return errors;
    }

    if (
        requirements.shape &&
        !explanation.includes(normalizeVisualText(expectedAnswer.outer_shape))
    ) {
        errors.push("La spiegazione non cita la forma rilevante.");
    }

    if (
        requirements.color &&
        !visualTextIncludesTerm(explanation, expectedAnswer.outer_color)
    ) {
        errors.push("La spiegazione non cita il colore rilevante.");
    }

    if (
        requirements.sides &&
        Number.isInteger(expectedAnswer.sides) &&
        !explanation.includes(String(expectedAnswer.sides))
    ) {
        errors.push("La spiegazione non cita il numero di lati rilevante.");
    }

    (expectedAnswer.inner_objects || []).forEach(item => {
        const itemType = normalizeVisualText(item.type);

        if (!requirements.innerTypes.has(itemType)) {
            return;
        }

        if (
            Number.isInteger(item.quantity) &&
            item.quantity > 1 &&
            !explanation.includes(String(item.quantity))
        ) {
            errors.push("La spiegazione non cita la quantità degli elementi rilevanti.");
        }

        if (!visualTextIncludesTerm(explanation, item.type)) {
            errors.push("La spiegazione non cita il tipo degli elementi rilevanti.");
        }

        if (
            requirements.color &&
            !visualTextIncludesTerm(explanation, item.color)
        ) {
            errors.push("La spiegazione non cita il colore degli elementi rilevanti.");
        }
    });

    return errors;
}

function getVisualExplanationRequirements(visualLogic) {
    const ruleText = normalizeVisualText(visualLogic?.rule?.description);
    const figures = [
        ...(Array.isArray(visualLogic?.sequence) ? visualLogic.sequence : []),
        visualLogic?.expected_answer,
        ...Object.values(visualLogic?.options || {}),
    ].filter(figure => figure && typeof figure === "object");

    const shapes = new Set(
        figures
            .map(figure => normalizeVisualText(figure.outer_shape))
            .filter(Boolean)
    );

    const innerTypes = new Set();

    figures.forEach(figure => {
        (figure.inner_objects || []).forEach(item => {
            const itemType = normalizeVisualText(item.type);
            const typeIsPartOfRule = (
                visualTextIncludesTerm(ruleText, itemType) ||
                (
                    itemType === "linee" &&
                    (
                        ruleText.includes("diagonal") ||
                        ruleText.includes("diagonale")
                    )
                )
            );

            if (itemType && itemType !== "direzione" && typeIsPartOfRule) {
                innerTypes.add(itemType);
            }
        });
    });

    return {
        shape: (
            shapes.size > 1 ||
            /(forma|cerchio|quadrato|triangolo|esagono|freccia)/.test(ruleText)
        ),
        color: (
            Boolean(visualLogic?.rule?.color_alternation?.enabled) ||
            ruleText.includes("colore") ||
            ruleText.includes("colori")
        ),
        sides: ruleText.includes("lati"),
        innerTypes,
    };
}

function validateWrongOptionExplanations(question) {
    const errors = [];
    const optionExplanations = question.spiegazioni_opzioni;

    if (!optionExplanations || typeof optionExplanations !== "object") {
        return ["Manca il dizionario spiegazioni_opzioni per le risposte."];
    }

    (question.opzioni || []).forEach(option => {
        if (option === question.risposta_corretta) {
            return;
        }

        const explanation = normalizeVisualText(optionExplanations[option]);

        if (explanation.length < 35) {
            errors.push(`L'opzione ${option} non spiega chiaramente cosa non torna.`);
            return;
        }

        if (!/(sbaglia|non|manca|incoerente)/.test(explanation)) {
            errors.push(`L'opzione ${option} non dice chiaramente cosa non torna.`);
        }
    });

    return errors;
}

function figuresMatch(left, right) {
    return JSON.stringify(canonicalVisualFigure(left)) ===
        JSON.stringify(canonicalVisualFigure(right));
}

function canonicalVisualFigure(figure) {
    if (!figure || typeof figure !== "object") {
        return null;
    }

    const innerObjects = Array.isArray(figure.inner_objects)
        ? figure.inner_objects
        : [];

    return {
        outer_shape: normalizeVisualText(figure.outer_shape),
        outer_color: normalizeVisualText(figure.outer_color),
        sides: figure.sides,
        inner_objects: innerObjects
            .map(item => ({
                type: normalizeVisualText(item.type),
                color: normalizeVisualText(item.color),
                quantity: item.quantity,
                position: normalizeVisualText(item.position),
            }))
            .sort((left, right) => {
                return JSON.stringify(left).localeCompare(JSON.stringify(right));
            }),
    };
}

function normalizeVisualText(value) {
    return String(value || "").toLowerCase().trim();
}

function visualTextIncludesTerm(text, term) {
    const normalizedTerm = normalizeVisualText(term);

    if (!normalizedTerm) {
        return true;
    }

    return (
        text.includes(normalizedTerm) ||
        (
            normalizedTerm.length > 4 &&
            text.includes(normalizedTerm.slice(0, -1))
        )
    );
}

function ottieniSpiegazioneRisposta(domanda, opzioneScelta) {
    const spiegazioneBase =
        domanda.spiegazione || "Spiegazione non disponibile.";

    const spiegazioneOpzione =
        domanda.spiegazioni_opzioni?.[opzioneScelta];

    if (
        opzioneScelta !== domanda.risposta_corretta &&
        spiegazioneOpzione
    ) {
        return `${spiegazioneOpzione} ${spiegazioneBase}`;
    }

    return spiegazioneBase;
}

function lanciaCoriandoliConDissolvenza(versioneGrande = false) {
    const canvas = elementi.confettiCanvas;
    const ctx = canvas.getContext("2d");

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const colori = [
        "#facc15",
        "#22c55e",
        "#38bdf8",
        "#a78bfa",
        "#fb7185",
        "#f97316",
        "#5eead4",
        "#ffffff",
        "#f0abfc"
    ];

    /*
        Tanti coriandoli come nella prima versione.
        Risposta corretta normale: tanti coriandoli.
        Report finale buono/ottimo: ancora più coriandoli.
    */
    const quantita = versioneGrande ? 260 : 130;
    const particelle = [];

    for (let i = 0; i < quantita; i += 1) {
        particelle.push({
            x: Math.random() * canvas.width,
            y: -40 - Math.random() * 220,

            larghezza: 7 + Math.random() * 10,
            altezza: 9 + Math.random() * 14,

            velocitaY: 3.2 + Math.random() * 4.8,
            velocitaX: -2.8 + Math.random() * 5.6,

            rotazione: Math.random() * Math.PI,
            velocitaRotazione: -0.16 + Math.random() * 0.32,

            colore: colori[Math.floor(Math.random() * colori.length)],

            opacita: 1,

            /*
                La dissolvenza non parte subito.
                Parte solo sotto metà schermo, circa tra il 58% e il 72%.
            */
            puntoInizioDissolvenza:
                canvas.height * (0.58 + Math.random() * 0.14),

            dissolvenzaIniziata: false,

            /*
                Più basso è il numero, più lentamente spariscono.
                Qui la dissolvenza è morbida.
            */
            velocitaDissolvenza: 0.010 + Math.random() * 0.006
        });
    }

    function anima() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        let particelleVive = 0;

        particelle.forEach(particella => {
            /*
                I coriandoli si muovono sempre.
                Non si fermano a metà schermo.
            */
            particella.x += particella.velocitaX;
            particella.y += particella.velocitaY;

            /*
                Piccola gravità: continuano a cadere in modo naturale.
            */
            particella.velocitaY += 0.025;

            /*
                Piccola oscillazione laterale.
            */
            particella.x += Math.sin(particella.y * 0.025) * 0.45;

            particella.rotazione += particella.velocitaRotazione;

            /*
                Solo quando il coriandolo supera il punto sotto metà schermo
                inizia la dissolvenza.
            */
            if (particella.y >= particella.puntoInizioDissolvenza) {
                particella.dissolvenzaIniziata = true;
            }

            /*
                Prima resta completamente visibile.
                Dopo continua a scendere e sfuma piano.
            */
            if (particella.dissolvenzaIniziata) {
                particella.opacita -= particella.velocitaDissolvenza;
            }

            const ancoraVisibile =
                particella.opacita > 0 &&
                particella.y < canvas.height + 140;

            if (ancoraVisibile) {
                particelleVive += 1;

                ctx.save();

                ctx.globalAlpha = particella.opacita;
                ctx.translate(particella.x, particella.y);
                ctx.rotate(particella.rotazione);
                ctx.fillStyle = particella.colore;

                ctx.fillRect(
                    -particella.larghezza / 2,
                    -particella.altezza / 2,
                    particella.larghezza,
                    particella.altezza
                );

                ctx.restore();
            }
        });

        if (particelleVive > 0) {
            requestAnimationFrame(anima);
        } else {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
    }

    anima();
}

/* ===== MIGLIORIE DEMO PROFESSIONALE ===== */

function preparaMigliorieDemo() {
    creaIntroDemo();
    creaCardsProgettoIts();
    valorizzaLogicaVisivaNelMenu();
    creaNotaCategoriaDemo();
    creaReportProfessionaleDemo();
    osservaReportFinaleDemo();
}

function creaIntroDemo() {
    if (!elementi.setupBox) {
        return;
    }

    if (document.getElementById("demoIntro")) {
        aggiornaBadgeQualitaDemo();
        return;
    }

    const intro = document.createElement("section");
    intro.id = "demoIntro";
    intro.className = "demo-intro";

    intro.innerHTML = `
        <h2>Allenati con quiz controllati</h2>
        <p>
            Scegli categoria, livello e numero di domande per iniziare l'allenamento.
        </p>
        <div class="quality-badges" id="qualityBadgesDemo"></div>
    `;

    elementi.setupBox.insertBefore(intro, elementi.setupBox.firstChild);

    aggiornaBadgeQualitaDemo();
}

function aggiornaBadgeQualitaDemo() {
    const badgeBox = document.getElementById("qualityBadgesDemo");

    if (!badgeBox) {
        return;
    }

    const totaleDomande = Array.isArray(databaseQuiz)
        ? databaseQuiz.length
        : 215;

    badgeBox.innerHTML = `
        <span class="quality-badge">${totaleDomande} domande</span>
        <span class="quality-badge">5 categorie</span>
        <span class="quality-badge">controlli qualità automatici</span>
    `;
}

function valorizzaLogicaVisivaNelMenu() {
    if (!elementi.categorySelect) {
        return;
    }

    const opzioneLogicaVisiva = elementi.categorySelect.querySelector(
        'option[value="logica_visiva"]'
    );

    if (opzioneLogicaVisiva) {
        opzioneLogicaVisiva.textContent =
            "Logica Visiva · con immagini SVG";
    }
}

function creaNotaCategoriaDemo() {
    if (!elementi.categorySelect) {
        return;
    }

    if (!document.getElementById("categoryNoteDemo")) {
        const nota = document.createElement("p");
        nota.id = "categoryNoteDemo";
        nota.className = "category-note-demo";

        const contenitore = elementi.categorySelect.parentElement
            || elementi.setupBox;

        contenitore.appendChild(nota);
    }

    elementi.categorySelect.addEventListener(
        "change",
        aggiornaNotaCategoriaDemo
    );

    aggiornaNotaCategoriaDemo();
}

function aggiornaNotaCategoriaDemo() {
    const nota = document.getElementById("categoryNoteDemo");

    if (!nota || !elementi.categorySelect) {
        return;
    }

    if (elementi.categorySelect.value === "logica_visiva") {
        nota.textContent =
            "Questa sezione include esercizi visuali con immagini SVG e controllo qualità dedicato.";
        return;
    }

    nota.textContent =
        "Le domande includono risposta corretta, distrattori e spiegazione finale.";
}

function creaReportProfessionaleDemo() {
    if (!elementi.resultBox) {
        return;
    }

    if (document.getElementById("professionalReportDemo")) {
        return;
    }

    const report = document.createElement("section");
    report.id = "professionalReportDemo";
    report.className = "professional-report hidden";

    elementi.resultBox.appendChild(report);
}

function osservaReportFinaleDemo() {
    if (!elementi.resultBox) {
        return;
    }

    const osservatore = new MutationObserver(() => {
        if (!elementi.resultBox.classList.contains("hidden")) {
            aggiornaReportProfessionaleDemo();
        }
    });

    osservatore.observe(
        elementi.resultBox,
        {
            attributes: true,
            attributeFilter: ["class"],
        }
    );
}

function aggiornaReportProfessionaleDemo() {
    const report = document.getElementById("professionalReportDemo");

    if (!report) {
        return;
    }

    const totaleDomande = domandeTest.length
        || risposteCorrette + risposteSbagliate;

    if (totaleDomande === 0) {
        return;
    }

    const percentuale = Math.round(
        (risposteCorrette / totaleDomande) * 100
    );

    const puntiForti = creaPuntiFortiDemo(percentuale);
    const areeDaMigliorare = creaAreeDaMigliorareDemo(percentuale);

    const categorieAllenate = Array.from(
        new Set(
            domandeTest.map(domanda => {
                return nomeCategoriaReportDemo(
                    domanda.sottocategoria === "logica_visiva"
                        ? "logica_visiva"
                        : domanda.categoria
                );
            })
        )
    ).join(", ");

    report.innerHTML = `
        <h3>Report di allenamento</h3>
        <div class="professional-report-grid">
            <div class="professional-report-card">
                <strong>Punti forti</strong>
                <ul>
                    ${puntiForti.map(voce => `<li>${voce}</li>`).join("")}
                </ul>
            </div>
            <div class="professional-report-card">
                <strong>Aree da migliorare</strong>
                <ul>
                    ${areeDaMigliorare.map(voce => `<li>${voce}</li>`).join("")}
                </ul>
            </div>
            <div class="professional-report-card">
                <strong>Sessione</strong>
                <ul>
                    <li>${totaleDomande} domande completate</li>
                    <li>${risposteCorrette} corrette e ${risposteSbagliate} da rivedere</li>
                    <li>Categorie: ${categorieAllenate}</li>
                </ul>
            </div>
            <div class="professional-report-card">
                <strong>Metodo consigliato</strong>
                <ul>
                    <li>Rileggi le spiegazioni delle risposte sbagliate.</li>
                    <li>Ripeti un test sullo stesso livello.</li>
                    <li>Passa al livello successivo solo quando superi l'80%.</li>
                </ul>
            </div>
        </div>
    `;

    report.classList.remove("hidden");
}

function creaPuntiFortiDemo(percentuale) {
    if (percentuale >= 90) {
        return [
            "Ottima precisione nelle risposte.",
            "Buona tenuta su tutto il test.",
            "Preparazione adatta a esercitazioni più avanzate.",
        ];
    }

    if (percentuale >= 70) {
        return [
            "Buona base di comprensione.",
            "Risultato positivo per continuare l'allenamento.",
            "Hai individuato correttamente molte regole del test.",
        ];
    }

    return [
        "Hai completato la sessione fino alla fine.",
        "Il test ha evidenziato gli argomenti su cui lavorare.",
        "Le spiegazioni finali possono aiutarti a recuperare gli errori.",
    ];
}

function creaAreeDaMigliorareDemo(percentuale) {
    if (percentuale >= 90) {
        return [
            "Riduci gli errori residui con test più difficili.",
            "Allenati su domande avanzate e logica visiva.",
            "Prova sessioni più lunghe per aumentare la stabilità.",
        ];
    }

    if (percentuale >= 70) {
        return [
            "Rivedi le domande sbagliate prima di cambiare livello.",
            "Consolida gli argomenti dove hai esitato.",
            "Ripeti la categoria per migliorare velocità e precisione.",
        ];
    }

    return [
        "Riparti dal livello facile o intermedio.",
        "Studia bene la spiegazione dopo ogni risposta.",
        "Fai sessioni brevi ma frequenti per consolidare le basi.",
    ];
}

function nomeCategoriaReportDemo(categoria) {
    if (categoria === "logica_visiva") {
        return "Logica Visiva";
    }

    return String(categoria || "")
        .replaceAll("_", " ")
        .replace(/\b\w/g, lettera => lettera.toUpperCase());
}


/* ===== CARD PROGETTO ITS ===== */

function creaCardsProgettoIts() {
    const page = document.querySelector(".page");

    if (!page) {
        return;
    }

    if (document.getElementById("itsProjectCards")) {
        return;
    }

    const sezione = document.createElement("section");
    sezione.id = "itsProjectCards";
    sezione.className = "its-project-cards";

    sezione.innerHTML = `
        <h3>Progetto in sintesi</h3>

        <div class="its-card-grid">
            <article class="its-card">
                <div class="its-card-icon">🎯</div>
                <h4>Demo e motore riutilizzabile</h4>
                <p>
                    Non è solo una demo online per studiare: è una base
                    riutilizzabile per creare test interattivi in qualsiasi
                    ambito, con domande strutturate, livelli di difficoltà
                    e spiegazioni finali.
                </p>
            </article>

            <article class="its-card">
                <div class="its-card-icon">📚</div>
                <h4>Preparazione personale</h4>
                <p>
                    Può essere usata come supporto per test di ingresso,
                    esercitazioni didattiche, studio personale e allenamento
                    per concorsi.
                </p>
            </article>

            <article class="its-card">
                <div class="its-card-icon">⚡</div>
                <h4>Feedback immediato</h4>
                <p>
                    Il quiz mostra subito se la risposta è corretta e alla fine
                    genera un report con percentuale, punti forti e aree da
                    migliorare.
                </p>
            </article>

            <article class="its-card">
                <div class="its-card-icon">✅</div>
                <h4>Grande controllo qualità</h4>
                <p>
                    Script Python verificano struttura JSON, duplicati,
                    domande simili, immagini mancanti, distrattori forti,
                    regole visuali e completezza delle spiegazioni.
                </p>
            </article>

            <article class="its-card">
                <div class="its-card-icon">🧩</div>
                <h4>Logica visiva SVG</h4>
                <p>
                    Include esercizi visuali con immagini SVG e controlli
                    specifici per evitare domande ambigue, regole anticipate
                    o spiegazioni incomplete.
                </p>
            </article>

            <article class="its-card">
                <div class="its-card-icon">💻</div>
                <h4>Base per nuovi quiz</h4>
                <p>
                    Lo stesso motore può essere esteso per creare quiz,
                    simulazioni, test di ingresso, esercitazioni aziendali
                    o percorsi formativi su materie e settori diversi.
                </p>
            </article>
        </div>
    `;

    page.appendChild(sezione);
}


/* ===== AVVIO IMMEDIATO DEL TEST GENERATO ===== */

function alexPreparaPulsanteProvaTestGenerato() {
  const areaAzioni = document.querySelector(".creator-actions");

  if (!areaAzioni) {
    return;
  }

  if (document.getElementById("playGeneratedQuizButton")) {
    return;
  }

  const pulsante = document.createElement("button");
  pulsante.id = "playGeneratedQuizButton";
  pulsante.type = "button";
  pulsante.className = "secondary-button";
  pulsante.textContent = "Prova test generato";
  pulsante.disabled = true;

  pulsante.addEventListener("click", alexAvviaTestGeneratoDalJson);

  areaAzioni.appendChild(pulsante);

  const outputJson = document.getElementById("quizJsonOutput");

  if (outputJson) {
    const osservatore = new MutationObserver(() => {
      alexAggiornaPulsanteProvaTestGenerato();
    });

    osservatore.observe(outputJson, {
      childList: true,
      characterData: true,
      subtree: true,
    });
  }

  alexAggiornaPulsanteProvaTestGenerato();
}

function alexAggiornaPulsanteProvaTestGenerato() {
  const pulsante = document.getElementById("playGeneratedQuizButton");

  if (!pulsante) {
    return;
  }

  try {
    alexOttieniJsonGenerato();
    pulsante.disabled = false;
  } catch {
    pulsante.disabled = true;
  }
}

function alexOttieniJsonGenerato() {
  let testoJson = "";

  if (
    typeof ultimoQuizPersonalizzatoJson !== "undefined" &&
    ultimoQuizPersonalizzatoJson
  ) {
    testoJson = ultimoQuizPersonalizzatoJson;
  } else {
    testoJson = document.getElementById("quizJsonOutput")?.textContent || "";
  }

  testoJson = String(testoJson).trim();

  if (!testoJson || !testoJson.startsWith("{") && !testoJson.startsWith("[")) {
    throw new Error("Prima genera un JSON valido.");
  }

  return JSON.parse(testoJson);
}

function alexEstraiListaDomandeDaJson(json) {
  if (Array.isArray(json)) {
    return json;
  }

  if (!json || typeof json !== "object") {
    return [];
  }

  const possibiliListe = [
    json.domande,
    json.questions,
    json.quiz,
    json.items,
    json.data,
    json.risultato,
    json.risultato?.domande,
    json.risultato?.quiz,
    json.quiz?.domande,
    json.quiz?.questions,
  ];

  const lista = possibiliListe.find(Array.isArray);

  return lista || [];
}

function alexNormalizzaOpzioniPerRunner(opzioniGrezze) {
  if (Array.isArray(opzioniGrezze)) {
    return opzioniGrezze
      .map((opzione) => {
        if (typeof opzione === "string") {
          return opzione.trim();
        }

        if (opzione && typeof opzione === "object") {
          return String(
            opzione.testo ||
            opzione.risposta ||
            opzione.label ||
            opzione.value ||
            ""
          ).trim();
        }

        return "";
      })
      .filter(Boolean);
  }

  if (opzioniGrezze && typeof opzioniGrezze === "object") {
    return ["A", "B", "C", "D"]
      .map((lettera) => String(opzioniGrezze[lettera] || "").trim())
      .filter(Boolean);
  }

  return [];
}

function alexPulisciTestoRisposta(testo) {
  return String(testo || "")
    .replace(/^[A-D][\)\.\-:]\s*/i, "")
    .trim()
    .toLowerCase();
}

function alexTrovaRispostaCorrettaPerRunner(valoreRisposta, opzioniTesto) {
  let valore = valoreRisposta;

  if (valore && typeof valore === "object") {
    valore = valore.lettera || valore.testo || valore.risposta || "";
  }

  if (typeof valore === "number") {
    if (valore >= 0 && valore <= 3) {
      return opzioniTesto[valore] || "";
    }

    if (valore >= 1 && valore <= 4) {
      return opzioniTesto[valore - 1] || "";
    }
  }

  const testoRisposta = String(valore || "").trim();

  if (/^[A-D]$/i.test(testoRisposta)) {
    const indice = testoRisposta.toUpperCase().charCodeAt(0) - 65;
    return opzioniTesto[indice] || "";
  }

  const letteraConPrefisso = testoRisposta.match(/^([A-D])[\)\.\-:]/i);

  if (letteraConPrefisso) {
    const indice = letteraConPrefisso[1].toUpperCase().charCodeAt(0) - 65;
    return opzioniTesto[indice] || "";
  }

  const rispostaIdentica = opzioniTesto.find((opzione) => {
    return opzione.trim().toLowerCase() === testoRisposta.toLowerCase();
  });

  if (rispostaIdentica) {
    return rispostaIdentica;
  }

  const rispostaSimile = opzioniTesto.find((opzione) => {
    return alexPulisciTestoRisposta(opzione) === alexPulisciTestoRisposta(testoRisposta);
  });

  return rispostaSimile || "";
}

function alexNormalizzaDomandaGenerataPerRunner(domandaGrezza, indice) {
  const testoDomanda = String(
    domandaGrezza.domanda ||
    domandaGrezza.question ||
    domandaGrezza.testo ||
    ""
  ).trim();

  const opzioniTesto = alexNormalizzaOpzioniPerRunner(
    domandaGrezza.opzioni ||
    domandaGrezza.risposte ||
    domandaGrezza.options ||
    []
  );

  const rispostaCorretta = alexTrovaRispostaCorrettaPerRunner(
    domandaGrezza.risposta_corretta ||
    domandaGrezza.rispostaCorretta ||
    domandaGrezza.correct_answer ||
    domandaGrezza.corretta ||
    domandaGrezza.correct,
    opzioniTesto
  );

  if (!testoDomanda || opzioniTesto.length !== 4 || !rispostaCorretta) {
    return null;
  }

  return {
    id: domandaGrezza.id || `test_generato_${Date.now()}_${indice + 1}`,
    categoria:
      domandaGrezza.categoria ||
      domandaGrezza.materia ||
      domandaGrezza.subject ||
      "test_generato",
    sottocategoria:
      domandaGrezza.sottocategoria ||
      domandaGrezza.sotto_argomento ||
      "",
    livello:
      domandaGrezza.livello ||
      domandaGrezza.difficolta ||
      domandaGrezza.difficoltà ||
      "intermedio",
    domanda: testoDomanda,
    opzioni: opzioniTesto,
    risposta_corretta: rispostaCorretta,
    spiegazione:
      domandaGrezza.spiegazione ||
      domandaGrezza.explanation ||
      "Spiegazione non disponibile.",
    immagine_domanda: domandaGrezza.immagine_domanda || "",
    immagini_opzioni: domandaGrezza.immagini_opzioni || null,
  };
}

function alexAvviaTestGeneratoDalJson() {
  try {
    const json = alexOttieniJsonGenerato();
    const listaDomande = alexEstraiListaDomandeDaJson(json);

    const domandePulite = listaDomande
      .map(alexNormalizzaDomandaGenerataPerRunner)
      .filter(Boolean);

    if (domandePulite.length === 0) {
      throw new Error(
        "Il JSON generato non contiene domande complete con 4 risposte e risposta corretta."
      );
    }

    domandeTest = domandePulite;
    indiceDomandaCorrente = 0;
    risposteCorrette = 0;
    risposteSbagliate = 0;
    rispostaGiaData = false;

    mostraSolo(elementi.quizBox);
    mostraDomandaCorrente();

    if (typeof mostraStatoQuizCreator === "function") {
      mostraStatoQuizCreator(
        `Test avviato: ${domandePulite.length} domande caricate nel motore.`,
        false
      );
    }

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  } catch (errore) {
    if (typeof mostraStatoQuizCreator === "function") {
      mostraStatoQuizCreator(errore.message, true);
      return;
    }

    alert(errore.message);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  setTimeout(alexPreparaPulsanteProvaTestGenerato, 100);
});


/* ===== AVVIO AUTOMATICO DEL TEST PERSONALIZZATO ===== */

function avviaTestPersonalizzatoGenerato(domandeGenerate) {
  if (!Array.isArray(domandeGenerate) || domandeGenerate.length === 0) {
    mostraStatoQuizCreator(
      "Il test è stato generato, ma non contiene domande valide da avviare.",
      true
    );
    return;
  }

  domandeTest = domandeGenerate;
  indiceDomandaCorrente = 0;
  risposteCorrette = 0;
  risposteSbagliate = 0;
  rispostaGiaData = false;

  mostraSolo(elementi.quizBox);
  mostraDomandaCorrente();

  mostraStatoQuizCreator(
    `Test avviato: ${domandeGenerate.length} domande caricate nel motore interattivo.`,
    false
  );

  window.scrollTo({
    top: 0,
    behavior: "smooth",
  });
}



/* ==========================================================
   FIX GENERATORE NUOVI TEST
   - niente titolo obbligatorio
   - niente numero personalizzato separato
   - se non carichi file, usa il database finale già caricato
   - quando premi "Genera nuovo test", parte subito il quiz
========================================================== */

function alexFixGeneratoreNuoviTest() {
  const form = document.getElementById("quizCreatorForm");
  const creatorTitle = document.getElementById("creatorTitle");
  const creatorCustomCount = document.getElementById("creatorCustomCount");
  const creatorQuestionMode = document.getElementById("creatorQuestionMode");
  const creatorQuestionCount = document.getElementById("creatorQuestionCount");

  if (creatorTitle) {
    creatorTitle.value = "Test generato";
    const contenitoreTitolo = creatorTitle.closest(".form-field") || creatorTitle.parentElement;
    if (contenitoreTitolo) {
      contenitoreTitolo.style.display = "none";
    }
  }

  if (creatorCustomCount) {
    creatorCustomCount.value = "10";
    const contenitoreNumero = creatorCustomCount.closest(".form-field") || creatorCustomCount.parentElement;
    if (contenitoreNumero) {
      contenitoreNumero.style.display = "none";
    }
  }

  if (creatorQuestionMode) {
    const opzioniDesiderate = [
      { value: "5", text: "5 domande" },
      { value: "10", text: "10 domande" },
      { value: "12", text: "12 domande" },
      { value: "20", text: "20 domande" },
      { value: "all", text: "Tutte le domande trovate" },
      { value: "custom", text: "Numero a scelta..." },
    ];

    creatorQuestionMode.innerHTML = "";

    opzioniDesiderate.forEach(opzione => {
      const option = document.createElement("option");
      option.value = opzione.value;
      option.textContent = opzione.text;
      creatorQuestionMode.appendChild(option);
    });

    creatorQuestionMode.value = "10";

    creatorQuestionMode.addEventListener("change", () => {
      if (creatorQuestionMode.value !== "custom") {
        return;
      }

      const valore = window.prompt("Quante domande vuoi generare?", "10");
      const numero = Number(valore);

      if (!Number.isInteger(numero) || numero < 1) {
        creatorQuestionMode.value = "10";
        if (creatorCustomCount) {
          creatorCustomCount.value = "10";
        }
        return;
      }

      if (creatorCustomCount) {
        creatorCustomCount.value = String(numero);
      }

      const optionCustom = creatorQuestionMode.querySelector('option[value="custom"]');
      if (optionCustom) {
        optionCustom.textContent = `${numero} domande`;
      }
    });
  }

  if (creatorQuestionCount) {
    creatorQuestionCount.textContent = `${databaseQuiz.length} domande nel database`;
  }

  if (form && !form.dataset.alexFixAttivo) {
    form.dataset.alexFixAttivo = "true";

    form.addEventListener(
      "submit",
      alexGeneraNuovoTestCorretto,
      true
    );
  }
}

async function alexGeneraNuovoTestCorretto(evento) {
  evento.preventDefault();
  evento.stopImmediatePropagation();

  try {
    mostraStatoQuizCreator("Preparazione nuovo test in corso...", false);
    disabilitaAzioniQuizJson();

    const dati = alexLeggiCampiGeneratorePulito();

    if (!dati.materia) {
      mostraStatoQuizCreator("Scegli una materia.", true);
      return;
    }

    if (
      dati.questionMode === "custom" &&
      (!Number.isInteger(dati.customCount) || dati.customCount < 1)
    ) {
      mostraStatoQuizCreator("Inserisci un numero di domande valido.", true);
      return;
    }

    let domandeNormalizzate = [];

    if (dati.file || dati.sourceText) {
      const testoSorgente = await leggiTestoSorgenteQuiz(dati.file);
      const domandeTrovate = estraiDomandeDaSorgente(testoSorgente, dati.file);

      domandeNormalizzate = normalizzaDomandeImportate(domandeTrovate, dati);
    } else {
      domandeNormalizzate = alexOttieniDomandeDalDatabasePerGeneratore(dati);
    }

    if (domandeNormalizzate.length === 0) {
      mostraStatoQuizCreator(
        `Non ho trovato domande valide per "${dati.materia}" con livello "${dati.livello}". Controlla di avere ricostruito dist/database_quiz_finale.json.`,
        true
      );
      return;
    }

    const quantita = ottieniNumeroDomandeDaGenerare(
      dati,
      domandeNormalizzate.length
    );

    const domandeScelte = mescolaArray(domandeNormalizzate).slice(0, quantita);

    const quiz = creaQuizPersonalizzato(dati, domandeScelte, {
      trovate: domandeNormalizzate.length,
      usate: domandeScelte.length,
    });

    ultimoQuizPersonalizzatoJson = JSON.stringify(quiz, null, 2);

    elementi.quizJsonOutput.textContent = ultimoQuizPersonalizzatoJson;
    elementi.copyQuizJsonButton.disabled = false;
    elementi.downloadQuizJsonButton.disabled = false;
    elementi.creatorQuestionCount.textContent =
      `${domandeScelte.length} domande generate`;

    mostraStatoQuizCreator(
      `Test generato: ${domandeScelte.length} domande su ${domandeNormalizzate.length} disponibili.`,
      false
    );

    alexAvviaTestGeneratoSubito(domandeScelte);
  } catch (errore) {
    mostraStatoQuizCreator(
      errore.message || "Errore durante la generazione del test.",
      true
    );
  }
}

function alexLeggiCampiGeneratorePulito() {
  const creatorSubject = document.getElementById("creatorSubject");
  const creatorCustomSubject = document.getElementById("creatorCustomSubject");
  const creatorLevel = document.getElementById("creatorLevel");
  const creatorQuestionMode = document.getElementById("creatorQuestionMode");
  const creatorCustomCount = document.getElementById("creatorCustomCount");
  const creatorFile = document.getElementById("creatorFile");
  const creatorSourceText = document.getElementById("creatorSourceText");

  const materiaPersonalizzata = creatorCustomSubject?.value?.trim() || "";
  const materia = materiaPersonalizzata || creatorSubject?.value || "scienze";
  const questionMode = creatorQuestionMode?.value || "10";
  const customCount = Number(creatorCustomCount?.value || "10");

  return {
    titolo: `Test ${formattaTesto(materia)}`,
    materia,
    livello: creatorLevel?.value || "facile",
    questionMode,
    customCount,
    file: creatorFile?.files?.[0] || null,
    sourceText: creatorSourceText?.value?.trim() || "",
  };
}

function alexOttieniDomandeDalDatabasePerGeneratore(dati) {
  const categoriaRichiesta = creaSlugQuizCreator(dati.materia);
  const livelloRichiesto = dati.livello;

  if (!Array.isArray(databaseQuiz) || databaseQuiz.length === 0) {
    return [];
  }

  return databaseQuiz
    .filter(domanda => {
      const categoriaDomanda = creaSlugQuizCreator(domanda.categoria || "");
      const sottocategoriaDomanda = creaSlugQuizCreator(domanda.sottocategoria || "");

      const tags = Array.isArray(domanda.tags)
        ? domanda.tags.map(tag => creaSlugQuizCreator(tag))
        : [];

      const categoriaOk =
        categoriaDomanda === categoriaRichiesta ||
        sottocategoriaDomanda === categoriaRichiesta ||
        tags.includes(categoriaRichiesta) ||
        domandaCorrispondeCategoria(domanda, categoriaRichiesta);

      const livelloOk =
        !livelloRichiesto ||
        livelloRichiesto === "tutti" ||
        domanda.livello === livelloRichiesto;

      return categoriaOk && livelloOk;
    })
    .map((domanda, index) => {
      const opzioni = Array.isArray(domanda.opzioni)
        ? domanda.opzioni.slice(0, 4)
        : normalizzaOpzioniImportate(domanda.opzioni);

      const rispostaCorretta = alexNormalizzaRispostaDatabase(
        domanda.risposta_corretta,
        opzioni
      );

      return {
        ...domanda,
        id: domanda.id || creaIdQuizPersonalizzato(
          categoriaRichiesta,
          livelloRichiesto,
          index + 1
        ),
        categoria: domanda.categoria || categoriaRichiesta,
        livello: domanda.livello || livelloRichiesto,
        tipo: domanda.tipo || "testo",
        tipo_domanda: domanda.tipo_domanda || "testo",
        opzioni,
        risposta_corretta: rispostaCorretta,
        spiegazione: domanda.spiegazione || "Spiegazione non disponibile.",
        tags: Array.isArray(domanda.tags)
          ? domanda.tags
          : [categoriaRichiesta, "database"],
        difficolta:
          domanda.difficolta ||
          ottieniDifficoltaDaLivello(domanda.livello || livelloRichiesto),
      };
    })
    .filter(domanda => {
      return (
        domanda.domanda &&
        Array.isArray(domanda.opzioni) &&
        domanda.opzioni.length === 4 &&
        domanda.risposta_corretta &&
        domanda.opzioni.includes(domanda.risposta_corretta)
      );
    });
}

function alexNormalizzaRispostaDatabase(risposta, opzioni) {
  const valore = String(risposta || "").trim();

  if (/^[A-D]$/i.test(valore)) {
    const indice = valore.toUpperCase().charCodeAt(0) - 65;
    return opzioni[indice] || "";
  }

  return opzioni.find(opzione => {
    return normalizzaTestoQuizCreator(opzione) === normalizzaTestoQuizCreator(valore);
  }) || valore;
}

function alexAvviaTestGeneratoSubito(domandeGenerate) {
  if (!Array.isArray(domandeGenerate) || domandeGenerate.length === 0) {
    mostraStatoQuizCreator(
      "Il test è stato generato, ma non contiene domande valide da avviare.",
      true
    );
    return;
  }

  domandeTest = domandeGenerate;
  indiceDomandaCorrente = 0;
  risposteCorrette = 0;
  risposteSbagliate = 0;
  rispostaGiaData = false;

  mostraSolo(elementi.quizBox);
  mostraDomandaCorrente();

  window.scrollTo({
    top: 0,
    behavior: "smooth",
  });
}

document.addEventListener("DOMContentLoaded", () => {
  setTimeout(alexFixGeneratoreNuoviTest, 300);
  setTimeout(alexFixGeneratoreNuoviTest, 900);
});



/* ==========================================================
   GENERATORE PULITO FINALE
   - Demo sopra: solo materie preparazione AI
   - Generatore sotto: layout largo come la demo sopra
   - Tre menu: Materia, Livello, Numero domande
   - Due pulsanti sotto: Carica JSON/TXT/PDF, Genera test
========================================================== */

(function () {
  const materieDemoAI = [
    "ai",
    "informatica",
    "matematica",
    "inglese",
    "logica",
    "logica_visiva",
  ];

  let alexQuizPulitoDomande = [];
  let alexQuizPulitoIndice = 0;
  let alexQuizPulitoPunteggio = 0;
  let alexQuizPulitoBloccato = false;

  function alexInitGeneratorePulito() {
    alexPulisciDemoSopra();
    alexCreaGeneratorePulitoSotto();
  }

  function alexPulisciDemoSopra() {
    const selects = document.querySelectorAll("select");

    selects.forEach((select) => {
      if (select.id === "alexGenMateria") {
        return;
      }

      const valori = [...select.options].map((option) => option.value);

      const sembraMenuCategoria =
        valori.includes("ai") &&
        valori.includes("informatica");

      if (!sembraMenuCategoria) {
        return;
      }

      [...select.options].forEach((option) => {
        if (!materieDemoAI.includes(option.value)) {
          option.remove();
        }
      });
    });
  }

  function alexCreaGeneratorePulitoSotto() {
    const vecchioForm = document.getElementById("quizCreatorForm");

    if (!vecchioForm || document.getElementById("alexGeneratorePulito")) {
      return;
    }

    const contenitore =
      vecchioForm.closest("section") ||
      vecchioForm.closest(".card") ||
      vecchioForm.parentElement;

    vecchioForm.style.display = "none";

    if (contenitore) {
      contenitore.querySelectorAll("button").forEach((button) => {
        if (!button.closest("#alexGeneratorePulito")) {
          button.style.display = "none";
        }
      });

      contenitore.querySelectorAll("textarea").forEach((textarea) => {
        textarea.style.display = "none";
      });
    }

    const pannello = document.createElement("div");
    pannello.id = "alexGeneratorePulito";
    pannello.innerHTML = `
      <div class="alex-gen-menu-row">
        <label class="alex-gen-field">
          <span>Materia</span>
          <select id="alexGenMateria">
            <option value="scienze">Scienze</option>
            <option value="fisica">Fisica</option>
            <option value="chimica">Chimica</option>
            <option value="biologia">Biologia</option>
            <option value="astronomia">Astronomia</option>
            <option value="scienze_della_terra">Scienze della Terra</option>
            <option value="fisica_quantistica_base">Fisica quantistica base</option>
            <option value="ai">Intelligenza artificiale</option>
            <option value="informatica">Informatica</option>
            <option value="matematica">Matematica</option>
            <option value="inglese">Inglese</option>
            <option value="logica">Logica</option>
            <option value="logica_visiva">Logica visiva</option>
          </select>
        </label>

        <label class="alex-gen-field">
          <span>Livello</span>
          <select id="alexGenLivello">
            <option value="tutti">Tutti i livelli</option>
            <option value="facile">Facile</option>
            <option value="intermedio">Intermedio</option>
            <option value="avanzato">Avanzato</option>
          </select>
        </label>

        <label class="alex-gen-field">
          <span>Numero domande</span>
          <select id="alexGenNumero">
            <option value="10">10 domande</option>
            <option value="20">20 domande</option>
            <option value="all">Tutte le domande trovate</option>
          </select>
        </label>
      </div>

      <div class="alex-gen-actions">
        <input
          id="alexGenFile"
          type="file"
          accept=".json,.txt,.pdf"
          hidden
        >

        <button type="button" id="alexGenCaricaFile">
          Carica JSON / TXT / PDF
        </button>

        <button type="button" id="alexGenGeneraTest">
          Genera test
        </button>

        <span id="alexGenNomeFile"></span>
      </div>

      <div id="alexQuizPulitoRunner" class="alex-quiz-pulito-runner">
        <h2>Test generato</h2>
        <p>Qui comparirà il quiz creato dal generatore.</p>
      </div>
    `;

    vecchioForm.insertAdjacentElement("beforebegin", pannello);

    document
      .getElementById("alexGenCaricaFile")
      .addEventListener("click", () => {
        document.getElementById("alexGenFile").click();
      });

    document
      .getElementById("alexGenFile")
      .addEventListener("change", () => {
        const file = document.getElementById("alexGenFile").files[0];
        const nomeFile = document.getElementById("alexGenNomeFile");

        if (file) {
          nomeFile.textContent = `File caricato: ${file.name}`;
        } else {
          nomeFile.textContent = "";
        }
      });

    document
      .getElementById("alexGenGeneraTest")
      .addEventListener("click", alexGeneraTestPulito);
  }

  async function alexGeneraTestPulito() {
    const runner = document.getElementById("alexQuizPulitoRunner");

    runner.innerHTML = `
      <h2>Test generato</h2>
      <p>Sto preparando il test...</p>
    `;

    try {
      const materia = document.getElementById("alexGenMateria").value;
      const livello = document.getElementById("alexGenLivello").value;
      const numeroScelto = document.getElementById("alexGenNumero").value;
      const file = document.getElementById("alexGenFile").files[0];

      let domande = [];

      if (file) {
        domande = await alexLeggiDomandeDaFile(file, materia, livello);
      } else {
        domande = alexPescaDalDatabase(materia, livello);
      }

      if (!domande.length) {
        runner.innerHTML = `
          <h2>Test generato</h2>
          <p class="alex-gen-error">
            Nessuna domanda trovata per questa scelta.
          </p>
        `;
        return;
      }

      const numeroFinale =
        numeroScelto === "all"
          ? domande.length
          : Math.min(Number(numeroScelto), domande.length);

      alexQuizPulitoDomande = alexMescola(domande).slice(0, numeroFinale);
      alexQuizPulitoIndice = 0;
      alexQuizPulitoPunteggio = 0;
      alexQuizPulitoBloccato = false;

      alexMostraDomandaPulita();

      runner.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    } catch (errore) {
      runner.innerHTML = `
        <h2>Test generato</h2>
        <p class="alex-gen-error">${alexEscape(errore.message)}</p>
      `;
    }
  }

  async function alexLeggiDomandeDaFile(file, materia, livello) {
    if (file.name.toLowerCase().endsWith(".pdf")) {
      throw new Error(
        "PDF caricato. Il pulsante unico è pronto, ma il parser PDF lo colleghiamo nel passaggio successivo. Ora usa JSON o TXT strutturato."
      );
    }

    const testo = await file.text();

    let dati;

    try {
      dati = JSON.parse(testo);
    } catch {
      throw new Error("Il file deve contenere JSON valido.");
    }

    const lista =
      Array.isArray(dati)
        ? dati
        : Array.isArray(dati.quiz)
          ? dati.quiz
          : Array.isArray(dati.domande)
            ? dati.domande
            : [];

    return lista
      .map((domanda, indice) => alexNormalizzaDomanda(domanda, materia, livello, indice))
      .filter(Boolean);
  }

  function alexPescaDalDatabase(materia, livello) {
    if (!Array.isArray(databaseQuiz)) {
      return [];
    }

    return databaseQuiz
      .filter((domanda) => alexMateriaOk(domanda, materia))
      .filter((domanda) => {
        return livello === "tutti" || domanda.livello === livello;
      })
      .map((domanda, indice) => alexNormalizzaDomanda(domanda, materia, livello, indice))
      .filter(Boolean);
  }

  function alexMateriaOk(domanda, materia) {
    const categoria = alexSlug(domanda.categoria);
    const sottocategoria = alexSlug(domanda.sottocategoria);

    const tags = Array.isArray(domanda.tags)
      ? domanda.tags.map(alexSlug)
      : [];

    if (categoria === materia || sottocategoria === materia || tags.includes(materia)) {
      return true;
    }

    if (materia === "fisica") {
      return sottocategoria.includes("fisica") || tags.some((tag) => tag.includes("fisica"));
    }

    if (materia === "chimica") {
      return sottocategoria.includes("chimica") || tags.some((tag) => tag.includes("chimica"));
    }

    if (materia === "biologia") {
      return sottocategoria.includes("biologia") || tags.some((tag) => tag.includes("biologia"));
    }

    return false;
  }

  function alexNormalizzaDomanda(domanda, materia, livello, indice) {
    const opzioni = alexNormalizzaOpzioni(domanda.opzioni);

    let rispostaCorretta =
      domanda.risposta_corretta ||
      domanda.corretta ||
      domanda.answer ||
      "";

    if (/^[A-D]$/i.test(String(rispostaCorretta))) {
      const posizione = String(rispostaCorretta).toUpperCase().charCodeAt(0) - 65;
      rispostaCorretta = opzioni[posizione] || rispostaCorretta;
    }

    const rispostaTrovata = opzioni.find((opzione) => {
      return alexSlug(opzione) === alexSlug(rispostaCorretta);
    });

    rispostaCorretta = rispostaTrovata || rispostaCorretta;

    if (!domanda.domanda || opzioni.length !== 4 || !opzioni.includes(rispostaCorretta)) {
      return null;
    }

    return {
      id: domanda.id || `GEN-${Date.now()}-${indice}`,
      categoria: domanda.categoria || materia,
      livello: domanda.livello || livello || "intermedio",
      domanda: domanda.domanda,
      opzioni,
      risposta_corretta: rispostaCorretta,
      spiegazione: domanda.spiegazione || "Spiegazione non disponibile.",
    };
  }

  function alexNormalizzaOpzioni(opzioniOriginali) {
    if (Array.isArray(opzioniOriginali)) {
      return opzioniOriginali.map(String).map((x) => x.trim()).filter(Boolean).slice(0, 4);
    }

    if (opzioniOriginali && typeof opzioniOriginali === "object") {
      return ["A", "B", "C", "D"]
        .map((lettera) => opzioniOriginali[lettera] || opzioniOriginali[lettera.toLowerCase()])
        .map(String)
        .map((x) => x.trim())
        .filter(Boolean)
        .slice(0, 4);
    }

    return [];
  }

  function alexMostraDomandaPulita() {
    const runner = document.getElementById("alexQuizPulitoRunner");
    const domanda = alexQuizPulitoDomande[alexQuizPulitoIndice];

    alexQuizPulitoBloccato = false;

    runner.innerHTML = `
      <div class="alex-quiz-head">
        <div>
          <h2>Test generato</h2>
          <p>
            Domanda ${alexQuizPulitoIndice + 1}/${alexQuizPulitoDomande.length}
            · ${alexEscape(domanda.categoria)}
            · ${alexEscape(domanda.livello)}
          </p>
        </div>
        <div class="alex-quiz-score">
          Punteggio: ${alexQuizPulitoPunteggio}
        </div>
      </div>

      <div class="alex-quiz-question">
        ${alexEscape(domanda.domanda)}
      </div>

      <div class="alex-quiz-options">
        ${domanda.opzioni
          .map((opzione, indice) => `
            <button
              type="button"
              class="alex-quiz-option"
              data-risposta="${alexEscape(opzione)}"
            >
              <strong>${String.fromCharCode(65 + indice)})</strong>
              ${alexEscape(opzione)}
            </button>
          `)
          .join("")}
      </div>

      <div id="alexQuizFeedback" class="alex-quiz-feedback"></div>
    `;

    runner.querySelectorAll(".alex-quiz-option").forEach((button) => {
      button.addEventListener("click", () => {
        alexControllaRispostaPulita(button.dataset.risposta);
      });
    });
  }

  function alexControllaRispostaPulita(risposta) {
    if (alexQuizPulitoBloccato) {
      return;
    }

    alexQuizPulitoBloccato = true;

    const domanda = alexQuizPulitoDomande[alexQuizPulitoIndice];
    const feedback = document.getElementById("alexQuizFeedback");
    const corretta = risposta === domanda.risposta_corretta;

    if (corretta) {
      alexQuizPulitoPunteggio += 1;
    }

    document.querySelectorAll(".alex-quiz-option").forEach((button) => {
      const valore = button.dataset.risposta;

      if (valore === domanda.risposta_corretta) {
        button.classList.add("correct");
      } else if (valore === risposta) {
        button.classList.add("wrong");
      } else {
        button.classList.add("disabled");
      }
    });

    feedback.innerHTML = `
      <p>
        <strong>${corretta ? "Corretto." : "Sbagliato."}</strong>
        Risposta corretta: ${alexEscape(domanda.risposta_corretta)}
      </p>
      <p>${alexEscape(domanda.spiegazione)}</p>
      <button type="button" id="alexQuizAvanti">
        ${
          alexQuizPulitoIndice === alexQuizPulitoDomande.length - 1
            ? "Vedi risultato finale"
            : "Domanda successiva"
        }
      </button>
    `;

    document.getElementById("alexQuizAvanti").addEventListener("click", () => {
      if (alexQuizPulitoIndice === alexQuizPulitoDomande.length - 1) {
        alexMostraRisultatoPulito();
      } else {
        alexQuizPulitoIndice += 1;
        alexMostraDomandaPulita();
      }
    });
  }

  function alexMostraRisultatoPulito() {
    const runner = document.getElementById("alexQuizPulitoRunner");
    const totale = alexQuizPulitoDomande.length;
    const percentuale = Math.round((alexQuizPulitoPunteggio / totale) * 100);

    runner.innerHTML = `
      <h2>Risultato test generato</h2>
      <p>
        Hai risposto correttamente a
        <strong>${alexQuizPulitoPunteggio}</strong>
        domande su <strong>${totale}</strong>.
      </p>
      <p>Percentuale: <strong>${percentuale}%</strong></p>
      <button type="button" id="alexQuizRicomincia">
        Rifai questo test
      </button>
    `;

    document.getElementById("alexQuizRicomincia").addEventListener("click", () => {
      alexQuizPulitoIndice = 0;
      alexQuizPulitoPunteggio = 0;
      alexQuizPulitoBloccato = false;
      alexMostraDomandaPulita();
    });
  }

  function alexSlug(testo) {
    return String(testo || "")
      .trim()
      .toLowerCase()
      .replace(/[àá]/g, "a")
      .replace(/[èé]/g, "e")
      .replace(/[ìí]/g, "i")
      .replace(/[òó]/g, "o")
      .replace(/[ùú]/g, "u")
      .replace(/\s+/g, "_")
      .replace(/-/g, "_");
  }

  function alexMescola(lista) {
    const copia = [...lista];

    for (let i = copia.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [copia[i], copia[j]] = [copia[j], copia[i]];
    }

    return copia;
  }

  function alexEscape(testo) {
    return String(testo || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  document.addEventListener("DOMContentLoaded", () => {
    setTimeout(alexInitGeneratorePulito, 150);
    setTimeout(alexInitGeneratorePulito, 700);
    setTimeout(alexInitGeneratorePulito, 1400);
  });
})();



/* ==========================================================
   PATCH FILE + TESTO FUNZIONANTI
   - Carica JSON/TXT/PDF e poi Genera test
   - Incolla testo/JSON/testo PDF e poi Genera test
   - Se non c'è file e non c'è testo, usa il database
========================================================== */

(function () {
  let domandeAttive = [];
  let indiceAttivo = 0;
  let punteggioAttivo = 0;
  let rispostaBloccata = false;

  function inizializzaPatchFileTesto() {
    const pannello = document.getElementById("alexGeneratorePulito");
    const bottoneGenera = document.getElementById("alexGenGeneraTest");
    const azioni = document.querySelector("#alexGeneratorePulito .alex-gen-actions");

    if (!pannello || !bottoneGenera || !azioni) {
      return;
    }

    if (pannello.dataset.fileTestoOk === "true") {
      return;
    }

    pannello.dataset.fileTestoOk = "true";

    let boxTesto = document.getElementById("alexGenBoxTesto");

    if (!boxTesto) {
      boxTesto = document.createElement("div");
      boxTesto.id = "alexGenBoxTesto";
      boxTesto.innerHTML = `
        <label for="alexGenTestoIncollato">
          Incolla testo, JSON o testo copiato da PDF
        </label>

        <textarea
          id="alexGenTestoIncollato"
          rows="8"
          placeholder="Puoi incollare un JSON con domande già strutturate, oppure testo copiato da un PDF con formato tipo: domanda, A), B), C), D), risposta corretta, spiegazione."
        ></textarea>
      `;

      azioni.insertAdjacentElement("afterend", boxTesto);
    }

    const nuovoBottoneGenera = bottoneGenera.cloneNode(true);
    bottoneGenera.replaceWith(nuovoBottoneGenera);

    nuovoBottoneGenera.addEventListener("click", generaTestDaFileTestoODatabase);
  }

  async function generaTestDaFileTestoODatabase() {
    const runner = document.getElementById("alexQuizPulitoRunner");

    runner.innerHTML = `
      <h2>Test generato</h2>
      <p>Sto preparando il test...</p>
    `;

    try {
      const materia = document.getElementById("alexGenMateria").value;
      const livello = document.getElementById("alexGenLivello").value;
      const numero = document.getElementById("alexGenNumero").value;
      const file = document.getElementById("alexGenFile").files[0];
      const testoIncollato = document.getElementById("alexGenTestoIncollato").value.trim();

      let domande = [];

      if (file) {
        domande = await leggiDomandeDaFile(file, materia, livello);
      } else if (testoIncollato) {
        domande = leggiDomandeDaTesto(testoIncollato, materia, livello);
      } else {
        domande = pescaDalDatabase(materia, livello);
      }

      if (!domande.length) {
        throw new Error(
          "Non ho trovato domande valide. Usa JSON valido oppure testo strutturato con domanda, A), B), C), D), risposta corretta e spiegazione."
        );
      }

      const numeroFinale =
        numero === "all"
          ? domande.length
          : Math.min(Number(numero), domande.length);

      domandeAttive = mescola(domande).slice(0, numeroFinale);
      indiceAttivo = 0;
      punteggioAttivo = 0;
      rispostaBloccata = false;

      mostraDomanda();

      runner.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    } catch (errore) {
      runner.innerHTML = `
        <h2>Test generato</h2>
        <p class="alex-gen-error">${escapeHtml(errore.message)}</p>
      `;
    }
  }

  async function leggiDomandeDaFile(file, materia, livello) {
    const nome = file.name.toLowerCase();

    if (nome.endsWith(".pdf")) {
      const testoPdf = await estraiTestoDaPdf(file);
      return leggiDomandeDaTesto(testoPdf, materia, livello);
    }

    const testo = await file.text();
    return leggiDomandeDaTesto(testo, materia, livello);
  }

  async function estraiTestoDaPdf(file) {
    await caricaPdfJs();

    const buffer = await file.arrayBuffer();

    const pdf = await window.pdfjsLib.getDocument({
      data: buffer,
    }).promise;

    let testoCompleto = "";

    for (let numeroPagina = 1; numeroPagina <= pdf.numPages; numeroPagina++) {
      const pagina = await pdf.getPage(numeroPagina);
      const contenuto = await pagina.getTextContent();

      const testoPagina = contenuto.items
        .map((item) => item.str)
        .join(" ");

      testoCompleto += "\n" + testoPagina;
    }

    if (!testoCompleto.trim()) {
      throw new Error("Il PDF non contiene testo leggibile. Potrebbe essere una scansione immagine.");
    }

    return testoCompleto;
  }

  function caricaPdfJs() {
    return new Promise((resolve, reject) => {
      if (window.pdfjsLib) {
        resolve();
        return;
      }

      const script = document.createElement("script");
      script.src = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js";

      script.onload = () => {
        window.pdfjsLib.GlobalWorkerOptions.workerSrc =
          "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

        resolve();
      };

      script.onerror = () => {
        reject(
          new Error(
            "Non riesco a caricare il lettore PDF. Controlla la connessione internet oppure usa JSON/TXT."
          )
        );
      };

      document.head.appendChild(script);
    });
  }

  function leggiDomandeDaTesto(testo, materia, livello) {
    const daJson = provaLeggereJson(testo, materia, livello);

    if (daJson.length) {
      return daJson;
    }

    return provaLeggereTestoStrutturato(testo, materia, livello);
  }

  function provaLeggereJson(testo, materia, livello) {
    try {
      const dati = JSON.parse(testo);

      const lista =
        Array.isArray(dati)
          ? dati
          : Array.isArray(dati.quiz)
            ? dati.quiz
            : Array.isArray(dati.domande)
              ? dati.domande
              : [];

      return lista
        .map((domanda, indice) => normalizzaDomanda(domanda, materia, livello, indice))
        .filter(Boolean);
    } catch {
      return [];
    }
  }

  function provaLeggereTestoStrutturato(testo, materia, livello) {
    const testoPulito = testo
      .replace(/\r/g, "")
      .replace(/\n{3,}/g, "\n\n");

    const blocchi = testoPulito
      .split(/\n\s*(?=(?:\d+[\.\)]|domanda\s*\d*[:\-]|q\s*\d*[:\-]))/gi)
      .map((blocco) => blocco.trim())
      .filter(Boolean);

    const blocchiFinali = blocchi.length > 1 ? blocchi : [testoPulito];

    return blocchiFinali
      .map((blocco, indice) => estraiDomandaDaBlocco(blocco, materia, livello, indice))
      .filter(Boolean);
  }

  function estraiDomandaDaBlocco(blocco, materia, livello, indice) {
    const opzioniTrovate = [];
    const regexOpzioni = /^\s*([A-D])\s*[\)\.\:\-]\s*(.+)$/gim;

    let match;

    while ((match = regexOpzioni.exec(blocco)) !== null) {
      opzioniTrovate.push({
        lettera: match[1].toUpperCase(),
        testo: match[2].trim(),
        posizione: match.index,
      });
    }

    if (opzioniTrovate.length < 4) {
      return null;
    }

    const primeOpzioni = opzioniTrovate.slice(0, 4);
    const inizioOpzioni = primeOpzioni[0].posizione;

    let testoDomanda = blocco.slice(0, inizioOpzioni).trim();

    testoDomanda = testoDomanda
      .replace(/^\s*\d+[\.\)]\s*/i, "")
      .replace(/^\s*domanda\s*\d*[:\-]\s*/i, "")
      .replace(/^\s*q\s*\d*[:\-]\s*/i, "")
      .trim();

    const rispostaMatch = blocco.match(
      /(?:risposta\s*(?:corretta)?|corretta|answer)\s*[:\-]\s*([A-D]|.+)/i
    );

    if (!testoDomanda || !rispostaMatch) {
      return null;
    }

    const opzioni = primeOpzioni.map((opzione) => opzione.testo);

    let rispostaCorretta = rispostaMatch[1].trim();

    if (/^[A-D]$/i.test(rispostaCorretta)) {
      const posizione = rispostaCorretta.toUpperCase().charCodeAt(0) - 65;
      rispostaCorretta = opzioni[posizione];
    } else {
      const rispostaTrovata = opzioni.find((opzione) => {
        return slug(opzione) === slug(rispostaCorretta);
      });

      rispostaCorretta = rispostaTrovata || rispostaCorretta;
    }

    if (!opzioni.includes(rispostaCorretta)) {
      return null;
    }

    const spiegazioneMatch = blocco.match(
      /(?:spiegazione|perché|perche)\s*[:\-]\s*([\s\S]+)/i
    );

    const spiegazione = spiegazioneMatch
      ? spiegazioneMatch[1].trim()
      : "Spiegazione non disponibile.";

    return {
      id: `TESTO-${Date.now()}-${indice + 1}`,
      categoria: materia,
      livello: livello === "tutti" ? "intermedio" : livello,
      domanda: testoDomanda,
      opzioni,
      risposta_corretta: rispostaCorretta,
      spiegazione,
    };
  }

  function pescaDalDatabase(materia, livello) {
    if (!Array.isArray(window.databaseQuiz) && !Array.isArray(databaseQuiz)) {
      return [];
    }

    const archivio = Array.isArray(window.databaseQuiz)
      ? window.databaseQuiz
      : databaseQuiz;

    return archivio
      .filter((domanda) => materiaOk(domanda, materia))
      .filter((domanda) => {
        return livello === "tutti" || domanda.livello === livello;
      })
      .map((domanda, indice) => normalizzaDomanda(domanda, materia, livello, indice))
      .filter(Boolean);
  }

  function materiaOk(domanda, materia) {
    const categoria = slug(domanda.categoria);
    const sottocategoria = slug(domanda.sottocategoria);

    const tags = Array.isArray(domanda.tags)
      ? domanda.tags.map(slug)
      : [];

    if (categoria === materia || sottocategoria === materia || tags.includes(materia)) {
      return true;
    }

    if (materia === "fisica") {
      return sottocategoria.includes("fisica") || tags.some((tag) => tag.includes("fisica"));
    }

    if (materia === "chimica") {
      return sottocategoria.includes("chimica") || tags.some((tag) => tag.includes("chimica"));
    }

    if (materia === "biologia") {
      return sottocategoria.includes("biologia") || tags.some((tag) => tag.includes("biologia"));
    }

    return false;
  }

  function normalizzaDomanda(domanda, materia, livello, indice) {
    const opzioni = normalizzaOpzioni(domanda.opzioni);

    let rispostaCorretta =
      domanda.risposta_corretta ||
      domanda.corretta ||
      domanda.answer ||
      "";

    if (/^[A-D]$/i.test(String(rispostaCorretta))) {
      const posizione = String(rispostaCorretta).toUpperCase().charCodeAt(0) - 65;
      rispostaCorretta = opzioni[posizione] || rispostaCorretta;
    }

    const rispostaTrovata = opzioni.find((opzione) => {
      return slug(opzione) === slug(rispostaCorretta);
    });

    rispostaCorretta = rispostaTrovata || rispostaCorretta;

    if (!domanda.domanda || opzioni.length !== 4 || !opzioni.includes(rispostaCorretta)) {
      return null;
    }

    return {
      id: domanda.id || `GEN-${Date.now()}-${indice}`,
      categoria: domanda.categoria || materia,
      livello: domanda.livello || livello || "intermedio",
      domanda: domanda.domanda,
      opzioni,
      risposta_corretta: rispostaCorretta,
      spiegazione: domanda.spiegazione || "Spiegazione non disponibile.",
    };
  }

  function normalizzaOpzioni(opzioniOriginali) {
    if (Array.isArray(opzioniOriginali)) {
      return opzioniOriginali
        .map(String)
        .map((opzione) => opzione.trim())
        .filter(Boolean)
        .slice(0, 4);
    }

    if (opzioniOriginali && typeof opzioniOriginali === "object") {
      return ["A", "B", "C", "D"]
        .map((lettera) => opzioniOriginali[lettera] || opzioniOriginali[lettera.toLowerCase()])
        .map(String)
        .map((opzione) => opzione.trim())
        .filter(Boolean)
        .slice(0, 4);
    }

    return [];
  }

  function mostraDomanda() {
    const runner = document.getElementById("alexQuizPulitoRunner");
    const domanda = domandeAttive[indiceAttivo];

    rispostaBloccata = false;

    runner.innerHTML = `
      <div class="alex-quiz-head">
        <div>
          <h2>Test generato</h2>
          <p>
            Domanda ${indiceAttivo + 1}/${domandeAttive.length}
            · ${escapeHtml(domanda.categoria)}
            · ${escapeHtml(domanda.livello)}
          </p>
        </div>
        <div class="alex-quiz-score">
          Punteggio: ${punteggioAttivo}
        </div>
      </div>

      <div class="alex-quiz-question">
        ${escapeHtml(domanda.domanda)}
      </div>

      <div class="alex-quiz-options">
        ${domanda.opzioni
          .map((opzione, indice) => `
            <button
              type="button"
              class="alex-quiz-option"
              data-risposta="${escapeHtml(opzione)}"
            >
              <strong>${String.fromCharCode(65 + indice)})</strong>
              ${escapeHtml(opzione)}
            </button>
          `)
          .join("")}
      </div>

      <div id="alexQuizFeedback" class="alex-quiz-feedback"></div>
    `;

    runner.querySelectorAll(".alex-quiz-option").forEach((button) => {
      button.addEventListener("click", () => {
        controllaRisposta(button.dataset.risposta);
      });
    });
  }

  function controllaRisposta(risposta) {
    if (rispostaBloccata) {
      return;
    }

    rispostaBloccata = true;

    const domanda = domandeAttive[indiceAttivo];
    const feedback = document.getElementById("alexQuizFeedback");
    const corretta = risposta === domanda.risposta_corretta;

    if (corretta) {
      punteggioAttivo += 1;
    }

    document.querySelectorAll(".alex-quiz-option").forEach((button) => {
      const valore = button.dataset.risposta;

      if (valore === domanda.risposta_corretta) {
        button.classList.add("correct");
      } else if (valore === risposta) {
        button.classList.add("wrong");
      } else {
        button.classList.add("disabled");
      }
    });

    feedback.innerHTML = `
      <p>
        <strong>${corretta ? "Corretto." : "Sbagliato."}</strong>
        Risposta corretta: ${escapeHtml(domanda.risposta_corretta)}
      </p>
      <p>${escapeHtml(domanda.spiegazione)}</p>
      <button type="button" id="alexQuizAvanti">
        ${
          indiceAttivo === domandeAttive.length - 1
            ? "Vedi risultato finale"
            : "Domanda successiva"
        }
      </button>
    `;

    document.getElementById("alexQuizAvanti").addEventListener("click", () => {
      if (indiceAttivo === domandeAttive.length - 1) {
        mostraRisultato();
      } else {
        indiceAttivo += 1;
        mostraDomanda();
      }
    });
  }

  function mostraRisultato() {
    const runner = document.getElementById("alexQuizPulitoRunner");
    const totale = domandeAttive.length;
    const percentuale = Math.round((punteggioAttivo / totale) * 100);

    runner.innerHTML = `
      <h2>Risultato test generato</h2>
      <p>
        Hai risposto correttamente a
        <strong>${punteggioAttivo}</strong>
        domande su <strong>${totale}</strong>.
      </p>
      <p>Percentuale: <strong>${percentuale}%</strong></p>
      <button type="button" id="alexQuizRicomincia">
        Rifai questo test
      </button>
    `;

    document.getElementById("alexQuizRicomincia").addEventListener("click", () => {
      indiceAttivo = 0;
      punteggioAttivo = 0;
      rispostaBloccata = false;
      mostraDomanda();
    });
  }

  function slug(testo) {
    return String(testo || "")
      .trim()
      .toLowerCase()
      .replace(/[àá]/g, "a")
      .replace(/[èé]/g, "e")
      .replace(/[ìí]/g, "i")
      .replace(/[òó]/g, "o")
      .replace(/[ùú]/g, "u")
      .replace(/\s+/g, "_")
      .replace(/-/g, "_");
  }

  function mescola(lista) {
    const copia = [...lista];

    for (let i = copia.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [copia[i], copia[j]] = [copia[j], copia[i]];
    }

    return copia;
  }

  function escapeHtml(testo) {
    return String(testo || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  document.addEventListener("DOMContentLoaded", () => {
    setTimeout(inizializzaPatchFileTesto, 400);
    setTimeout(inizializzaPatchFileTesto, 1000);
    setTimeout(inizializzaPatchFileTesto, 1800);
  });
})();

