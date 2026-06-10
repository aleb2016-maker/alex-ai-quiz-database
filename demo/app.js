const databaseUrl = "../dist/database_quiz_finale.json";

let database = [];
let currentQuestion = null;
let correctAnswers = 0;
let answeredQuestions = 0;

const categorySelect = document.getElementById("categorySelect");
const levelSelect = document.getElementById("levelSelect");
const newQuestionButton = document.getElementById("newQuestionButton");

const totalQuestions = document.getElementById("totalQuestions");
const scoreValue = document.getElementById("scoreValue");

const categoryBadge = document.getElementById("categoryBadge");
const levelBadge = document.getElementById("levelBadge");
const questionId = document.getElementById("questionId");
const questionText = document.getElementById("questionText");

const questionImageBox = document.getElementById("questionImageBox");
const questionImage = document.getElementById("questionImage");

const optionsBox = document.getElementById("optionsBox");
const feedbackBox = document.getElementById("feedbackBox");
const explanationBox = document.getElementById("explanationBox");
const explanationText = document.getElementById("explanationText");

const confettiCanvas = document.getElementById("confettiCanvas");
const confettiContext = confettiCanvas.getContext("2d");

function normalizzaTesto(testo) {
    if (!testo) {
        return "";
    }

    return testo.toString().trim().toLowerCase();
}

function creaPercorsoAsset(percorso) {
    if (!percorso) {
        return "";
    }

    if (percorso.startsWith("http")) {
        return percorso;
    }

    return `../${percorso}`;
}

async function caricaDatabase() {
    try {
        const risposta = await fetch(databaseUrl);
        database = await risposta.json();

        popolaFiltri();
        aggiornaTotaleDomande();
        caricaNuovaDomanda();

    } catch (errore) {
        questionText.textContent = "Errore nel caricamento del database.";
        feedbackBox.className = "feedback-box ko";
        feedbackBox.textContent = "Controlla che il file dist/database_quiz_finale.json esista.";
        feedbackBox.classList.remove("hidden");
    }
}

function popolaFiltri() {
    const categorie = [...new Set(database.map(domanda => domanda.categoria))].sort();
    const livelli = [...new Set(database.map(domanda => domanda.livello))].sort();

    categorie.forEach(categoria => {
        const option = document.createElement("option");
        option.value = categoria;
        option.textContent = categoria;
        categorySelect.appendChild(option);
    });

    livelli.forEach(livello => {
        const option = document.createElement("option");
        option.value = livello;
        option.textContent = livello;
        levelSelect.appendChild(option);
    });
}

function filtraDomande() {
    const categoriaScelta = categorySelect.value;
    const livelloScelto = levelSelect.value;

    return database.filter(domanda => {
        const categoriaOk =
            categoriaScelta === "tutte" ||
            domanda.categoria === categoriaScelta;

        const livelloOk =
            livelloScelto === "tutti" ||
            domanda.livello === livelloScelto;

        return categoriaOk && livelloOk;
    });
}

function aggiornaTotaleDomande() {
    const domandeFiltrate = filtraDomande();
    totalQuestions.textContent = domandeFiltrate.length;
}

function aggiornaPunteggio() {
    scoreValue.textContent = `${correctAnswers}/${answeredQuestions}`;
}

function caricaNuovaDomanda() {
    const domandeFiltrate = filtraDomande();

    aggiornaTotaleDomande();

    if (domandeFiltrate.length === 0) {
        currentQuestion = null;

        questionText.textContent = "Nessuna domanda trovata per questi filtri.";
        categoryBadge.textContent = "Categoria";
        levelBadge.textContent = "Livello";
        questionId.textContent = "Nessuna domanda";

        optionsBox.innerHTML = "";
        questionImageBox.classList.add("hidden");
        feedbackBox.classList.add("hidden");
        explanationBox.classList.add("hidden");

        return;
    }

    const indiceCasuale = Math.floor(Math.random() * domandeFiltrate.length);
    currentQuestion = domandeFiltrate[indiceCasuale];

    mostraDomanda(currentQuestion);
}

function mostraDomanda(domanda) {
    categoryBadge.textContent = domanda.categoria || "Categoria";
    levelBadge.textContent = domanda.livello || "Livello";
    questionId.textContent = domanda.id || "ID domanda";
    questionText.textContent = domanda.domanda || "Domanda non disponibile";

    feedbackBox.classList.add("hidden");
    explanationBox.classList.add("hidden");
    optionsBox.innerHTML = "";

    mostraImmagineDomanda(domanda);
    mostraOpzioni(domanda);
}

function mostraImmagineDomanda(domanda) {
    if (domanda.tipo_domanda === "immagine" && domanda.immagine_domanda) {
        questionImage.src = creaPercorsoAsset(domanda.immagine_domanda);
        questionImageBox.classList.remove("hidden");
    } else {
        questionImage.src = "";
        questionImageBox.classList.add("hidden");
    }
}

function mostraOpzioni(domanda) {
    const opzioni = domanda.opzioni || [];
    const immaginiOpzioni = domanda.immagini_opzioni || [];

    opzioni.forEach((opzione, indice) => {
        const bottone = document.createElement("button");
        bottone.className = "option-button";

        const testoOpzione = document.createElement("span");
        testoOpzione.textContent = opzione;
        bottone.appendChild(testoOpzione);

        if (immaginiOpzioni[indice]) {
            const immagine = document.createElement("img");
            immagine.src = creaPercorsoAsset(immaginiOpzioni[indice]);
            immagine.alt = `Opzione ${indice + 1}`;
            immagine.className = "option-image";
            bottone.appendChild(immagine);
        }

        bottone.addEventListener("click", () => {
            controllaRisposta(opzione, bottone);
        });

        optionsBox.appendChild(bottone);
    });
}

function controllaRisposta(rispostaScelta, bottoneScelto) {
    if (!currentQuestion) {
        return;
    }

    const rispostaCorretta = currentQuestion.risposta_corretta;
    const rispostaUtente = rispostaScelta;

    const corretta =
        normalizzaTesto(rispostaUtente) === normalizzaTesto(rispostaCorretta);

    answeredQuestions++;

    const bottoni = document.querySelectorAll(".option-button");

    bottoni.forEach(bottone => {
        bottone.classList.add("disabled");

        const testoBottone = bottone.querySelector("span").textContent;

        if (normalizzaTesto(testoBottone) === normalizzaTesto(rispostaCorretta)) {
            bottone.classList.add("correct");
        }
    });

    if (corretta) {
        correctAnswers++;
        bottoneScelto.classList.add("correct");

        feedbackBox.className = "feedback-box ok";
        feedbackBox.textContent = "Risposta corretta! Ottimo lavoro.";
        avviaCoriandoli();
    } else {
        bottoneScelto.classList.add("wrong");

        feedbackBox.className = "feedback-box ko";
        feedbackBox.textContent = `Risposta sbagliata. Risposta corretta: ${rispostaCorretta}`;
    }

    explanationText.textContent =
        currentQuestion.spiegazione || "Spiegazione non disponibile.";

    feedbackBox.classList.remove("hidden");
    explanationBox.classList.remove("hidden");

    aggiornaPunteggio();
}

function ridimensionaCanvas() {
    confettiCanvas.width = window.innerWidth;
    confettiCanvas.height = window.innerHeight;
}

function avviaCoriandoli() {
    ridimensionaCanvas();

    const coriandoli = [];
    const colori = [
        "#38bdf8",
        "#a78bfa",
        "#f472b6",
        "#facc15",
        "#22c55e",
        "#fb7185"
    ];

    for (let i = 0; i < 160; i++) {
        coriandoli.push({
            x: Math.random() * confettiCanvas.width,
            y: -20 - Math.random() * confettiCanvas.height * 0.35,
            size: 6 + Math.random() * 9,
            speedY: 3 + Math.random() * 5,
            speedX: -2 + Math.random() * 4,
            rotation: Math.random() * 360,
            rotationSpeed: -8 + Math.random() * 16,
            color: colori[Math.floor(Math.random() * colori.length)],
            life: 120 + Math.random() * 50
        });
    }

    function anima() {
        confettiContext.clearRect(
            0,
            0,
            confettiCanvas.width,
            confettiCanvas.height
        );

        coriandoli.forEach(coriandolo => {
            coriandolo.x += coriandolo.speedX;
            coriandolo.y += coriandolo.speedY;
            coriandolo.rotation += coriandolo.rotationSpeed;
            coriandolo.life--;

            confettiContext.save();
            confettiContext.translate(coriandolo.x, coriandolo.y);
            confettiContext.rotate(coriandolo.rotation * Math.PI / 180);
            confettiContext.fillStyle = coriandolo.color;
            confettiContext.fillRect(
                -coriandolo.size / 2,
                -coriandolo.size / 2,
                coriandolo.size,
                coriandolo.size * 1.8
            );
            confettiContext.restore();
        });

        const ancoraVivi = coriandoli.some(coriandolo => coriandolo.life > 0);

        if (ancoraVivi) {
            requestAnimationFrame(anima);
        } else {
            confettiContext.clearRect(
                0,
                0,
                confettiCanvas.width,
                confettiCanvas.height
            );
        }
    }

    anima();
}

categorySelect.addEventListener("change", () => {
    aggiornaTotaleDomande();
    caricaNuovaDomanda();
});

levelSelect.addEventListener("change", () => {
    aggiornaTotaleDomande();
    caricaNuovaDomanda();
});

newQuestionButton.addEventListener("click", caricaNuovaDomanda);

window.addEventListener("resize", ridimensionaCanvas);

ridimensionaCanvas();
caricaDatabase();
aggiornaPunteggio();