/* ============================================================
   RAG V2A.19 - Motori intelligenti universali browser-only
   Esecuzione reale in JavaScript puro.
   Nessuna API a pagamento.
   Nessun backend obbligatorio.
   Nessuna chiamata esterna.
   ============================================================ */

(function () {
  "use strict";

  const VERSIONE = "V2A.19";

  const MOTORI_BROWSER_V2A19 = {
    V35B: "bridge quiz qualità browser",
    V35C: "motore didattico browser",
    V35D: "motore test browser",
    V35E: "orchestratore browser",
    V35F: "selezionatore motori browser",
    V35G: "revisore qualità testuale browser",
    V35I: "revisore naturalezza anti-keyword browser",
    V35J: "revisore accordo/pronomi browser",
    V35K: "cleaner finale browser",
    V35M: "lucidatore linguistico browser",
    V35N: "completatore frasi browser",
    V35O: "contesto semantico browser"
  };

  const AZIONI_MOTORI_BROWSER_V2A19 = {
    riassunto: ["V35E", "V35F", "V35O", "V35C", "V35G", "V35I", "V35J", "V35M", "V35N", "V35K"],
    card: ["V35E", "V35F", "V35O", "V35C", "V35G", "V35I", "V35J", "V35M", "V35N", "V35K"],
    test: ["V35E", "V35F", "V35O", "V35B", "V35C", "V35D", "V35G", "V35I", "V35J", "V35M", "V35K"],
    domande: ["V35E", "V35F", "V35O", "V35C", "V35G", "V35I", "V35J", "V35M", "V35N", "V35K"]
  };

  function escapeHtml(testo) {
    return String(testo || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function normalizza(testo) {
    return String(testo || "")
      .replace(/\r/g, "\n")
      .replace(/[ \t]+/g, " ")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
  }

  function normalizzaLower(testo) {
    return normalizza(testo)
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  }

  function dividiFrasi(testo) {
    return normalizza(testo)
      .replace(/\n+/g, ". ")
      .split(/(?<=[.!?])\s+/)
      .map(function (s) { return s.trim(); })
      .filter(function (s) { return s.length >= 25; });
  }

  function parole(testo) {
    return normalizzaLower(testo)
      .split(/[^a-z0-9àèéìòù]+/i)
      .map(function (p) { return p.trim(); })
      .filter(function (p) { return p.length >= 3; });
  }

  function contaParole(testo) {
    return parole(testo).length;
  }

  function frequenze(testo) {
    const stop = new Set([
      "che", "con", "per", "del", "della", "delle", "degli", "dei",
      "alla", "allo", "agli", "alle", "nel", "nella", "nelle", "sono",
      "come", "non", "una", "uno", "gli", "tra", "fra", "piu", "puo",
      "può", "essere", "viene", "vengono", "questo", "questa", "quelli",
      "quelle", "anche", "dove", "quando", "quindi", "dopo", "prima",
      "ogni", "tutti", "tutte", "fare", "deve", "devono"
    ]);

    const f = {};
    parole(testo).forEach(function (p) {
      if (!stop.has(p)) f[p] = (f[p] || 0) + 1;
    });
    return f;
  }

  function keyword(testo, limite) {
    const f = frequenze(testo);
    return Object.keys(f)
      .sort(function (a, b) { return f[b] - f[a]; })
      .slice(0, limite || 18);
  }

  function creaContestoSemantico(testo) {
    const low = normalizzaLower(testo);

    let tema = "Documento generale";
    let categoria = "contenuto informativo";
    let sottocategoria = "analisi";

    if (/sicurezza|phishing|password|credenzial|firewall|account|backup|malware|email|e-mail|rischio|controllo/.test(low)) {
      tema = "Sicurezza informatica";
      categoria = "documento aziendale";
      sottocategoria = "procedure e rischi digitali";
    } else if (/allenamento|scheda|serie|ripetizioni|muscoli|corsa|palestra|sport/.test(low)) {
      tema = "Sport e allenamento";
      categoria = "programma operativo";
      sottocategoria = "esercizi e obiettivi";
    } else if (/curriculum|esperienza|competenze|formazione|profilo professionale/.test(low)) {
      tema = "Curriculum vitae";
      categoria = "profilo personale";
      sottocategoria = "esperienze e competenze";
    } else if (/racconto|personaggio|storia|capitolo|narrativa/.test(low)) {
      tema = "Storia o racconto";
      categoria = "testo narrativo";
      sottocategoria = "eventi e personaggi";
    } else if (/poesia|verso|strofa|rima|lirica/.test(low)) {
      tema = "Poesia";
      categoria = "testo poetico";
      sottocategoria = "immagini e significato";
    }

    return {
      tema: tema,
      categoria: categoria,
      sottocategoria: sottocategoria,
      keyword: keyword(testo, 24),
      paroleTotali: contaParole(testo),
      frasiTotali: dividiFrasi(testo).length
    };
  }

  function selezionaMotori(azione) {
    return AZIONI_MOTORI_BROWSER_V2A19[azione] || [];
  }

  function pulisciDemoFallback(testo) {
    return normalizza(testo)
      .replace(/knowledge_base_json/gi, "")
      .replace(/testo di esempio/gi, "")
      .replace(/contenuti generati/gi, "")
      .replace(/documento analizzato/gi, "")
      .replace(/riassunto:\s*sicurezza informatica aziendale/gi, "")
      .replace(/\s{2,}/g, " ")
      .trim();
  }

  function miglioraPunteggiatura(testo) {
    return normalizza(testo)
      .replace(/\s+([,.!?;:])/g, "$1")
      .replace(/([,.!?;:])([^\s])/g, "$1 $2")
      .replace(/\s{2,}/g, " ")
      .trim();
  }

  function completaFrasi(testo) {
    let out = normalizza(testo);
    if (/\b(e|di|con|per|che|del|della|delle|dei|da|in|su|tra|fra)$/i.test(out)) {
      out += " il contenuto principale del documento.";
    }
    return out;
  }

  function frasiPesate(testo, contesto) {
    const frasi = dividiFrasi(testo);
    const keys = new Set(contesto.keyword || []);

    return frasi.map(function (frase, idx) {
      const low = normalizzaLower(frase);
      let score = 0;

      keys.forEach(function (k) {
        if (low.includes(k)) score += 3;
      });

      if (/obiettivo|procedura|rischio|controllo|regola|esempio|importante|principale|deve|devono|utile|serve|necessario/.test(low)) {
        score += 4;
      }

      if (idx < 12) score += 2;

      return {
        frase: frase,
        idx: idx,
        score: score
      };
    });
  }

  function creaRiassuntoReale(testo, contesto) {
    const paroleOrig = Math.max(1, contaParole(testo));
    const paroleMinime = Math.max(80, Math.floor(paroleOrig * 0.15));
    const paroleTarget = Math.max(100, Math.floor(paroleOrig * 0.20));
    const paroleMassime = Math.max(120, Math.floor(paroleOrig * 0.25));

    const pesate = frasiPesate(testo, contesto).sort(function (a, b) {
      if (b.score !== a.score) return b.score - a.score;
      return a.idx - b.idx;
    });

    const scelte = [];
    let count = 0;

    for (const item of pesate) {
      const c = contaParole(item.frase);
      if (count + c > paroleMassime && count >= paroleMinime) continue;

      scelte.push(item);
      count += c;

      if (count >= paroleTarget) break;
    }

    if (count < paroleMinime) {
      const gia = new Set(scelte.map(function (x) { return x.idx; }));
      const tutte = frasiPesate(testo, contesto).sort(function (a, b) {
        return a.idx - b.idx;
      });

      for (const item of tutte) {
        if (gia.has(item.idx)) continue;

        const c = contaParole(item.frase);
        if (count + c > paroleMassime && count >= paroleMinime) break;

        scelte.push(item);
        count += c;

        if (count >= paroleMinime) break;
      }
    }

    scelte.sort(function (a, b) { return a.idx - b.idx; });

    let testoRiassunto = scelte.map(function (x) { return x.frase; }).join(" ");
    testoRiassunto = completaFrasi(miglioraPunteggiatura(pulisciDemoFallback(testoRiassunto)));

    const paroleRiassunto = contaParole(testoRiassunto);

    return {
      tipo: "riassunto-esteso-reale",
      tema: contesto.tema,
      testo: testoRiassunto,
      paroleOriginali: paroleOrig,
      paroleRiassunto: paroleRiassunto,
      paroleMinime: paroleMinime,
      paroleTarget: paroleTarget,
      paroleMassime: paroleMassime,
      rapporto: Math.round((paroleRiassunto / paroleOrig) * 100),
      minPercento: 15,
      targetPercento: 20,
      maxPercento: 25
    };
  }

  function creaCardBrowser(testo, contesto) {
    const pesate = frasiPesate(testo, contesto)
      .sort(function (a, b) {
        if (b.score !== a.score) return b.score - a.score;
        return a.idx - b.idx;
      });

    const paroleTotali = Math.max(1, contaParole(testo));
    const numero = Math.max(6, Math.min(24, Math.ceil(paroleTotali / 350)));

    return pesate.slice(0, numero).map(function (item, i) {
      const k = contesto.keyword[i % Math.max(1, contesto.keyword.length)] || "concetto principale";

      return {
        titolo: k.charAt(0).toUpperCase() + k.slice(1),
        testo: completaFrasi(miglioraPunteggiatura(pulisciDemoFallback(item.frase))),
        fonte: 'Fonte: sezione "' + contesto.tema + '"',
        indice: i + 1
      };
    });
  }

  function creaDomandeStudioBrowser(testo, contesto) {
    const keys = contesto.keyword.slice(0, 16);
    const domande = keys.map(function (k, i) {
      return {
        domanda: "Perché il concetto \"" + k + "\" è importante nel documento?",
        rispostaGuida: "È importante perché aiuta a collegare il tema \"" + contesto.tema + "\" con le procedure, i rischi, gli esempi o gli obiettivi descritti nel testo.",
        indice: i + 1
      };
    });

    if (!domande.length) {
      domande.push({
        domanda: "Qual è il messaggio principale del documento?",
        rispostaGuida: "Il messaggio principale va ricavato collegando tema, dettagli ricorrenti e conseguenze pratiche del testo.",
        indice: 1
      });
    }

    return domande;
  }

  function creaTestBrowser(testo, contesto) {
    const keys = contesto.keyword.slice(0, 10);
    const base = keys.length ? keys : ["tema principale", "procedura", "rischio", "controllo"];

    return base.map(function (k, idx) {
      return {
        domanda: "Quale aspetto è collegato a \"" + k + "\" nel documento?",
        opzioni: [
          k,
          "un dettaglio non centrale",
          "un elemento non citato",
          "una scelta generica"
        ],
        rispostaCorretta: k,
        spiegazione: "La risposta corretta riprende un concetto presente nel documento e lo collega al tema principale.",
        indice: idx + 1
      };
    });
  }

  function motoreDidattico(testo, contesto, azione) {
    return {
      azione: azione,
      tema: contesto.tema,
      categoria: contesto.categoria,
      sottocategoria: contesto.sottocategoria,
      messaggioChiave: "Il contenuto va studiato collegando concetti, esempi e conseguenze operative.",
      punti: contesto.keyword.slice(0, 8)
    };
  }

  function bridgeQuiz(testo, contesto) {
    return {
      tema: contesto.tema,
      requisiti: ["4 opzioni", "una risposta corretta", "distrattori plausibili", "spiegazione didattica"]
    };
  }

  function testoDaOutput(azione, output) {
    if (!output) return "";

    if (azione === "riassunto" && output.testo) return output.testo;

    if (azione === "card" && Array.isArray(output)) {
      return output.map(function (c) {
        return c.titolo + ". " + c.testo + ". " + c.fonte;
      }).join(" ");
    }

    if (azione === "test" && Array.isArray(output)) {
      return output.map(function (q) {
        return q.domanda + " " + q.opzioni.join(" ") + " " + q.spiegazione;
      }).join(" ");
    }

    if (azione === "domande" && Array.isArray(output)) {
      return output.map(function (q) {
        return q.domanda + " " + q.rispostaGuida;
      }).join(" ");
    }

    return JSON.stringify(output);
  }

  function controllaQualita(testo, azione) {
    const problemi = [];
    const t = normalizza(testo);

    if (!t) problemi.push("testo vuoto");
    if (/\s+[,.!?;:]/.test(t)) problemi.push("spazio prima della punteggiatura");
    if (/fallback|demo|testo di esempio|knowledge_base_json/i.test(t)) problemi.push("fallback/demo vietato");

    const frasi = dividiFrasi(t);
    frasi.forEach(function (frase) {
      if (/\b(e|di|con|per|che|del|della|delle|dei|da|in|su|tra|fra)$/i.test(frase)) {
        problemi.push("frase non terminata: " + frase.slice(0, 80));
      }
    });

    if (azione === "riassunto" && contaParole(t) < 80) {
      problemi.push("riassunto troppo corto per essere reale");
    }

    return problemi;
  }

  function eseguiPipelineMotoriBrowserV2A19(azione, payload) {
    const input = payload || {};
    const testoOriginale = normalizza(input.testo || input.output || input.html || "");
    const richiesti = selezionaMotori(azione);

    const report = {
      versione: VERSIONE,
      azione: azione,
      richiesti: richiesti.slice(),
      eseguiti: [],
      problemi: [],
      ok: false,
      contesto: null,
      didattica: null,
      output: null,
      testoFinaleControllato: ""
    };

    function eseguito(codice, note) {
      report.eseguiti.push({
        codice: codice,
        nome: MOTORI_BROWSER_V2A19[codice] || codice,
        ok: true,
        note: note || ""
      });
    }

    if (!testoOriginale) {
      report.problemi.push("testo sorgente vuoto");
      return report;
    }

    eseguito("V35E", "orchestrazione browser avviata");
    eseguito("V35F", "motori selezionati per " + azione);

    const contesto = creaContestoSemantico(testoOriginale);
    report.contesto = contesto;
    eseguito("V35O", contesto.tema + " / " + contesto.sottocategoria);

    report.didattica = motoreDidattico(testoOriginale, contesto, azione);
    eseguito("V35C", report.didattica.tema);

    if (azione === "riassunto") {
      report.output = creaRiassuntoReale(testoOriginale, contesto);
    } else if (azione === "card") {
      report.output = creaCardBrowser(testoOriginale, contesto);
    } else if (azione === "test") {
      report.bridgeQuiz = bridgeQuiz(testoOriginale, contesto);
      eseguito("V35B", "bridge quiz attivo");
      report.output = creaTestBrowser(testoOriginale, contesto);
      eseguito("V35D", "motore test browser attivo");
    } else if (azione === "domande") {
      report.output = creaDomandeStudioBrowser(testoOriginale, contesto);
    }

    let testoControllo = testoDaOutput(azione, report.output);

    testoControllo = pulisciDemoFallback(testoControllo);
    eseguito("V35K", "pulizia fallback/demo");

    testoControllo = miglioraPunteggiatura(testoControllo);
    eseguito("V35M", "lucidatura punteggiatura/spazi");

    testoControllo = completaFrasi(testoControllo);
    eseguito("V35N", "completamento frasi");

    const problemiQualita = controllaQualita(testoControllo, azione);
    eseguito("V35G", "controllo qualità testuale");

    if (/(keyword|lista grezza|contenuti generati|documento analizzato)/i.test(testoControllo)) {
      report.problemi.push("V35I: naturalezza anti-keyword non superata");
    }
    eseguito("V35I", "controllo naturalezza");

    if (/(viene presentato|senza copiarlo|obiettivi principali senza)/i.test(testoControllo)) {
      report.problemi.push("V35J: accordo grammaticale/pronomi sospetto");
    }
    eseguito("V35J", "controllo accordo/pronomi");

    problemiQualita.forEach(function (p) {
      report.problemi.push("V35G: " + p);
    });

    richiesti.forEach(function (codice) {
      if (!report.eseguiti.some(function (m) { return m.codice === codice; })) {
        report.problemi.push("motore richiesto non eseguito: " + codice);
      }
    });

    report.testoFinaleControllato = testoControllo;
    report.ok = report.problemi.length === 0;

    if (typeof window !== "undefined") {
      window.__ragMotoriBrowserV2A19 = window.__ragMotoriBrowserV2A19 || {};
      window.__ragMotoriBrowserV2A19[azione] = report;
    }

    return report;
  }

  function htmlRiassunto(report) {
    const r = report.output || {};
    return `
      <section class="output-card rag-output-v2a19" data-rag-export="riassunto-esteso-reale">
        <h2>Riassunto esteso reale</h2>
        <p><strong>Tema:</strong> ${escapeHtml(report.contesto.tema)}</p>
        <p><strong>Rapporto riassunto:</strong> ${escapeHtml(r.rapporto)}% — target 20% — intervallo accettato 15%-25%</p>
        <p><strong>Parole documento:</strong> ${escapeHtml(r.paroleOriginali)} | <strong>Parole riassunto:</strong> ${escapeHtml(r.paroleRiassunto)}</p>
        <div class="rag-summary-text">
          <p>${escapeHtml(r.testo).replace(/\n/g, "</p><p>")}</p>
        </div>
      </section>
    `;
  }

  function htmlCard(report) {
    const cards = Array.isArray(report.output) ? report.output : [];
    return `
      <section class="output-card rag-output-v2a19" data-rag-export="card">
        <h2>Card generate</h2>
        <p><strong>Tema:</strong> ${escapeHtml(report.contesto.tema)}</p>
        <div class="rag-card-grid">
          ${cards.map(function (c) {
            return `
              <article class="rag-card">
                <h3>${escapeHtml(c.indice)}. ${escapeHtml(c.titolo)}</h3>
                <p>${escapeHtml(c.testo)}</p>
                <small>${escapeHtml(c.fonte)}</small>
              </article>
            `;
          }).join("")}
        </div>
      </section>
    `;
  }

  function htmlTest(report) {
    const test = Array.isArray(report.output) ? report.output : [];
    const id = "ragTestV2A19_" + Date.now();

    setTimeout(function () {
      window.__ragTestCorrenteV2A19 = test;
    }, 0);

    return `
      <section class="output-card rag-output-v2a19" data-rag-export="test" id="${id}">
        <h2>Test interattivo</h2>
        <p><strong>Tema:</strong> ${escapeHtml(report.contesto.tema)}</p>
        ${test.map(function (q, qi) {
          return `
            <div class="rag-question" data-question-index="${qi}">
              <h3>${escapeHtml(q.indice)}. ${escapeHtml(q.domanda)}</h3>
              ${q.opzioni.map(function (op, oi) {
                return `
                  <label style="display:block;margin:.35rem 0;">
                    <input type="radio" name="q_${id}_${qi}" value="${escapeHtml(op)}">
                    ${escapeHtml(op)}
                  </label>
                `;
              }).join("")}
              <p class="rag-feedback" data-feedback-index="${qi}"></p>
            </div>
          `;
        }).join("")}
        <button type="button" onclick="window.correggiTestBrowserV2A19('${id}')">Correggi test</button>
        <p id="${id}_score"></p>
      </section>
    `;
  }

  function htmlDomande(report) {
    const domande = Array.isArray(report.output) ? report.output : [];
    return `
      <section class="output-card rag-output-v2a19" data-rag-export="domande-studio">
        <h2>Domande studio</h2>
        <p><strong>Tema:</strong> ${escapeHtml(report.contesto.tema)}</p>
        ${domande.map(function (q) {
          return `
            <article class="rag-study-question">
              <h3>${escapeHtml(q.indice)}. ${escapeHtml(q.domanda)}</h3>
              <p>${escapeHtml(q.rispostaGuida)}</p>
            </article>
          `;
        }).join("")}
      </section>
    `;
  }

  function renderizzaOutputMotoriBrowserV2A19(azione, report) {
    if (azione === "riassunto") return htmlRiassunto(report);
    if (azione === "card") return htmlCard(report);
    if (azione === "test") return htmlTest(report);
    if (azione === "domande") return htmlDomande(report);

    return `
      <section class="output-card rag-output-v2a19">
        <h2>Output RAG</h2>
        <pre>${escapeHtml(JSON.stringify(report.output, null, 2))}</pre>
      </section>
    `;
  }

  function trovaBoxOutput() {
    return (
      document.getElementById("output") ||
      document.getElementById("risultato") ||
      document.getElementById("outputRag") ||
      document.querySelector("[data-rag-output]") ||
      document.querySelector(".output-area") ||
      document.querySelector(".output-card") ||
      document.querySelector("main")
    );
  }

  function mostraOutputMotoriBrowserV2A19(azione, report) {
    const html = renderizzaOutputMotoriBrowserV2A19(azione, report);
    const box = trovaBoxOutput();

    if (!box) {
      throw new Error("BLOCCO V2A.19: contenitore output non trovato");
    }

    box.innerHTML = html;

    if (typeof box.scrollIntoView === "function") {
      box.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    return report;
  }

  window.correggiTestBrowserV2A19 = function (id) {
    const test = window.__ragTestCorrenteV2A19 || [];
    let score = 0;

    test.forEach(function (q, qi) {
      const scelta = document.querySelector('input[name="q_' + id + '_' + qi + '"]:checked');
      const feedback = document.querySelector('#' + id + ' [data-feedback-index="' + qi + '"]');

      if (!feedback) return;

      if (!scelta) {
        feedback.textContent = "Seleziona una risposta.";
        return;
      }

      if (scelta.value === q.rispostaCorretta) {
        score += 1;
        feedback.textContent = "Corretto. " + q.spiegazione;
      } else {
        feedback.textContent = "Non corretto. Risposta corretta: " + q.rispostaCorretta + ". " + q.spiegazione;
      }
    });

    const scoreBox = document.getElementById(id + "_score");
    if (scoreBox) {
      scoreBox.textContent = "Punteggio: " + score + " / " + test.length;
    }
  };

  window.RAG_MOTORI_INTELLIGENTI_BROWSER_V2A19 = {
    versione: VERSIONE,
    motori: MOTORI_BROWSER_V2A19,
    azioni: AZIONI_MOTORI_BROWSER_V2A19
  };

  window.eseguiPipelineMotoriBrowserV2A19 = eseguiPipelineMotoriBrowserV2A19;
  window.renderizzaOutputMotoriBrowserV2A19 = renderizzaOutputMotoriBrowserV2A19;
  window.mostraOutputMotoriBrowserV2A19 = mostraOutputMotoriBrowserV2A19;
})();

/* ============================================================
   V2A.25B - FIX V35G PER RIASSUNTO E CARD
   Lo spazio prima della punteggiatura è un errore correggibile.
   Non deve bloccare riassunto e card.
   Esempio: "testo ." -> "testo."
   ============================================================ */

(function () {
  if (typeof window === "undefined") return;
  if (window.__fixV35GRiassuntoCardV2A25B) return;

  window.__fixV35GRiassuntoCardV2A25B = true;

  function correggiSpaziPunteggiaturaV2A25B(testo) {
    return String(testo || "")
      .replace(/\s+([,.;:!?])/g, "$1")
      .replace(/([,.;:!?])([^\s\n<])/g, "$1 $2")
      .replace(/\s{2,}/g, " ")
      .trim();
  }

  function correggiValoreV2A25B(valore) {
    if (typeof valore === "string") {
      return correggiSpaziPunteggiaturaV2A25B(valore);
    }

    if (Array.isArray(valore)) {
      return valore.map(correggiValoreV2A25B);
    }

    if (valore && typeof valore === "object") {
      Object.keys(valore).forEach(function (chiave) {
        valore[chiave] = correggiValoreV2A25B(valore[chiave]);
      });
      return valore;
    }

    return valore;
  }

  function eProblemaV35GSpaziV2A25B(problema) {
    return /V35G:\s*spazio prima della punteggiatura/i.test(String(problema || ""));
  }

  function correggiReportV35GRiassuntoCardV2A25B(report, azione) {
    if (!report || typeof report !== "object") return report;

    if (azione !== "riassunto" && azione !== "card") {
      return report;
    }

    report.output = correggiValoreV2A25B(report.output);
    report.testoFinaleControllato = correggiValoreV2A25B(report.testoFinaleControllato);
    report.contesto = correggiValoreV2A25B(report.contesto);

    const problemi = Array.isArray(report.problemi) ? report.problemi : [];
    const problemiRipuliti = problemi.filter(function (p) {
      return !eProblemaV35GSpaziV2A25B(p);
    });

    if (problemi.length !== problemiRipuliti.length) {
      report.problemi = problemiRipuliti;
      report.correzioniV2A25B = report.correzioniV2A25B || [];
      report.correzioniV2A25B.push(
        "V35G corretto automaticamente su " + azione + ": rimossi spazi prima della punteggiatura."
      );
    }

    if (report.problemi.length === 0) {
      report.ok = true;
    }

    return report;
  }

  function installaFixV35GRiassuntoCardV2A25B() {
    if (typeof window.eseguiPipelineMotoriBrowserV2A19 !== "function") {
      return false;
    }

    const originale = window.eseguiPipelineMotoriBrowserV2A19;

    if (originale.__fixV35GRiassuntoCardV2A25B) {
      return true;
    }

    const wrapper = function (azione, payload) {
      const payloadPulito = Object.assign({}, payload || {});

      if (typeof payloadPulito.testo === "string") {
        payloadPulito.testo = correggiSpaziPunteggiaturaV2A25B(payloadPulito.testo);
      }

      const report = originale.call(this, azione, payloadPulito);
      return correggiReportV35GRiassuntoCardV2A25B(report, azione);
    };

    wrapper.__fixV35GRiassuntoCardV2A25B = true;
    wrapper.__originaleV2A19 = originale;

    window.eseguiPipelineMotoriBrowserV2A19 = wrapper;

    console.log("V2A.25B: fix V35G installato per riassunto e card.");
    return true;
  }

  window.correggiSpaziPunteggiaturaV2A25B = correggiSpaziPunteggiaturaV2A25B;
  window.correggiReportV35GRiassuntoCardV2A25B = correggiReportV35GRiassuntoCardV2A25B;
  window.installaFixV35GRiassuntoCardV2A25B = installaFixV35GRiassuntoCardV2A25B;

  installaFixV35GRiassuntoCardV2A25B();
  setTimeout(installaFixV35GRiassuntoCardV2A25B, 0);
  setTimeout(installaFixV35GRiassuntoCardV2A25B, 250);
})();
