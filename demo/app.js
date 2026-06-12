const DATA_URL = "../dist/database_quiz_finale.json";

let databaseQuiz = [];
let domandeTest = [];
let indiceDomandaCorrente = 0;
let risposteCorrette = 0;
let risposteSbagliate = 0;
let rispostaGiaData = false;

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

    domanda.opzioni.forEach((opzione, indice) => {
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
        domanda.spiegazione || "Spiegazione non disponibile.";

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
    if (!elementi.setupBox) {
        return;
    }

    if (document.getElementById("itsProjectCards")) {
        return;
    }

    const intro = document.getElementById("demoIntro");

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

    if (intro) {
        intro.insertAdjacentElement("afterend", sezione);
        return;
    }

    elementi.setupBox.insertBefore(sezione, elementi.setupBox.firstChild);
}
