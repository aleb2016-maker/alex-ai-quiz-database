(function () {
  "use strict";

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
      if (blocco) blocchi.push(blocco);
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

          if (valido) finali.push(pezzo);
        });
    });

    const senzaDuplicatiConsecutivi = [];

    finali.forEach(function (blocco) {
      const ultimo = senzaDuplicatiConsecutivi[senzaDuplicatiConsecutivi.length - 1];

      if (ultimo && ultimo.toLowerCase() === blocco.toLowerCase()) return;

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
        descrizione: "Fase di recupero per abbassare il ritmo e preparare il corpo al blocco successivo."
      };
    }

    if (/riscaldamento/.test(t)) {
      return {
        titolo: "Riscaldamento",
        badge: "Preparazione",
        tipo: "riscaldamento",
        descrizione: "Attivazione iniziale per preparare muscoli, articolazioni e respiro."
      };
    }

    if (/defaticamento/.test(t)) {
      return {
        titolo: "Defaticamento",
        badge: "Chiusura",
        tipo: "defaticamento",
        descrizione: "Fase finale per ridurre gradualmente lo sforzo e favorire il recupero."
      };
    }

    if (/camminata|bicicletta|nuoto|corsa|cardio/.test(t)) {
      return {
        titolo: "Cardio leggero",
        badge: "Resistenza",
        tipo: "cardio",
        descrizione: "Attività aerobica a scelta, utile per lavorare su resistenza e continuità."
      };
    }

    if (/flessibilit|stretching|mobilità|mobilita/.test(t)) {
      return {
        titolo: "Flessibilità",
        badge: "Mobilità",
        tipo: "flessibilita",
        descrizione: "Blocco dedicato alla mobilità e alla scioltezza del movimento."
      };
    }

    if (/equilibrio|postura|stabilit/.test(t)) {
      return {
        titolo: "Equilibrio",
        badge: "Controllo",
        tipo: "equilibrio",
        descrizione: "Esercizi per stabilità, postura e controllo del corpo."
      };
    }

    if (/forza|squat|plank|affondi|pesi|push/.test(t)) {
      return {
        titolo: "Forza",
        badge: "Potenziamento",
        tipo: "forza",
        descrizione: "Blocco di potenziamento per forza, controllo e resistenza muscolare."
      };
    }

    return {
      titolo: "Blocco allenamento",
      badge: "Workout",
      tipo: "circuito",
      descrizione: "Parte della scheda trasformata in attività pratica."
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
    const testo = document.getElementById("documentoInput").value;
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
          Trasformare la scheda in una sequenza chiara: attivazione, cardio,
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

  function generaTest() {
    const cards = generaCards();

    if (!cards.length) {
      mostraErrore("Test non generato", "Non sono stati trovati blocchi di allenamento leggibili.");
      return;
    }

    const domande = cards.slice(0, 10).map(function (card, indice) {
      return {
        numero: indice + 1,
        domanda: `Qual è la funzione del blocco "${card.titolo}"?`,
        corretta: card.descrizione,
        opzioni: [
          card.descrizione,
          "Serve a eliminare tutte le altre fasi della scheda.",
          "Serve solo a rendere la scheda più lunga.",
          "Serve a cambiare argomento rispetto all’allenamento."
        ]
      };
    });

    areaOutput().innerHTML = `
      <section class="output-card">
        <span class="pill">Test</span>
        <h2>Test generato dalla scheda</h2>
        <p>Sono state create ${domande.length} domande basate sui blocchi riconosciuti.</p>

        ${domande.map(function (item) {
          return `
            <div class="question-box">
              <h3>${item.numero}. ${escapeHtml(item.domanda)}</h3>
              <ol type="A">
                ${item.opzioni.map(function (opzione) {
                  return `<li>${escapeHtml(opzione)}</li>`;
                }).join("")}
              </ol>
              <p class="answer"><strong>Risposta corretta:</strong> ${escapeHtml(item.corretta)}</p>
            </div>
          `;
        }).join("")}
      </section>
    `;
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
        <p>Domande utili per capire e ripassare la scheda.</p>

        <ol>
          ${cards.map(function (card) {
            return `
              <li>
                <strong>Che cosa serve nel blocco "${escapeHtml(card.titolo)}"?</strong>
                <p>${escapeHtml(card.descrizione)}</p>
              </li>
            `;
          }).join("")}
        </ol>
      </section>
    `;
  }

  function caricaFile(evento) {
    const file = evento.target.files && evento.target.files[0];

    if (!file) return;

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

  window.sportTrainingDocumentEngine = {
    normalizzaTesto,
    estraiBlocchi,
    generaRiassunto,
    generaCardVisive,
    generaTest,
    generaDomandeStudio
  };
})();
