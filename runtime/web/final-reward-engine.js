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
