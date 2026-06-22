(function () {
  "use strict";

  const stato = {
    ultimoFile: null,
    ultimoTipo: "",
    ultimoTesto: ""
  };

  function el(id) {
    return document.getElementById(id);
  }

  function setStatus(messaggio, classe) {
    const box = el("status");
    box.className = "status " + (classe || "");
    box.textContent = messaggio;
  }

  function escapeHtml(valore) {
    return String(valore || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function pulisciTesto(testo) {
    return String(testo || "")
      .replace(/\r/g, "\n")
      .replace(/[ \t]+/g, " ")
      .replace(/\n\s+/g, "\n")
      .replace(/\s+\n/g, "\n")
      .replace(/[|\\/_]{2,}/g, " ")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
  }

  function analizzaQualitaTesto(testo) {
    const pulito = pulisciTesto(testo);
    const senzaSpazi = pulito.replace(/\s/g, "");
    const lettere = pulito.match(/[A-Za-zÀ-ÿ]/g) || [];
    const parole = pulito.match(/[A-Za-zÀ-ÿ]{3,}/g) || [];
    const numeri = pulito.match(/[0-9]/g) || [];
    const simboli = pulito.match(/[^A-Za-zÀ-ÿ0-9\s.,;:!?'"()€%/-]/g) || [];

    const righe = pulito
      .split("\n")
      .map(function (riga) {
        return riga.trim();
      })
      .filter(Boolean);

    const righeCorte = righe.filter(function (riga) {
      return riga.length <= 5;
    }).length;

    const paroleUniche = new Set(
      parole.map(function (parola) {
        return parola.toLowerCase();
      })
    );

    const rapportoLettere = senzaSpazi.length
      ? lettere.length / senzaSpazi.length
      : 0;

    const rapportoRigheCorte = righe.length
      ? righeCorte / righe.length
      : 1;

    const rapportoSimboli = senzaSpazi.length
      ? simboli.length / senzaSpazi.length
      : 0;

    const valido =
      parole.length >= 6 &&
      paroleUniche.size >= 5 &&
      rapportoLettere >= 0.58 &&
      rapportoRigheCorte <= 0.55 &&
      rapportoSimboli <= 0.18 &&
      numeri.length <= lettere.length * 2;

    let livello = "bad";
    let messaggio = "Testo non utilizzabile: sembra OCR spazzatura o immagine senza documento.";

    if (valido) {
      livello = "ok";
      messaggio = "Testo valido: può essere usato dal motore universale.";
    } else if (parole.length >= 4 && paroleUniche.size >= 3 && rapportoLettere >= 0.45) {
      livello = "warn";
      messaggio = "Testo parziale: puoi correggerlo manualmente prima di usarlo.";
    }

    return {
      valido,
      livello,
      messaggio,
      parole: parole.length,
      paroleUniche: paroleUniche.size,
      rapportoLettere,
      rapportoRigheCorte,
      rapportoSimboli
    };
  }

  function riconosciTipoContenuto(testo) {
    const t = pulisciTesto(testo).toLowerCase();

    const profili = [
      {
        nome: "Sport e allenamento",
        chiave: "sport",
        parole: ["allenamento", "riscaldamento", "camminata", "bicicletta", "nuoto", "cardio", "stretching", "defaticamento", "squat", "plank"]
      },
      {
        nome: "Curriculum vitae",
        chiave: "curriculum",
        parole: ["curriculum", "esperienza", "competenze", "formazione", "obiettivo", "sviluppatore", "github", "profilo professionale"]
      },
      {
        nome: "Documento personale",
        chiave: "personale",
        parole: ["codice fiscale", "residenza", "scadenza", "documento", "tessera", "certificato", "numero documento"]
      },
      {
        nome: "Documento aziendale",
        chiave: "aziendale",
        parole: ["azienda", "procedura", "processo", "responsabile", "cliente", "rischio", "sicurezza", "report", "kpi"]
      },
      {
        nome: "Storia o fumetto",
        chiave: "storia",
        parole: ["storia", "racconto", "personaggio", "protagonista", "capitolo", "scena", "balloon", "dialogo", "disse", "rispose"]
      },
      {
        nome: "Poesia",
        chiave: "poesia",
        parole: ["poesia", "verso", "strofa", "rima", "metafora", "cuore", "vento", "silenzio"]
      },
      {
        nome: "Hobby o progetto",
        chiave: "hobby",
        parole: ["progetto", "materiali", "strumenti", "passaggi", "attività", "costruire", "creare", "ricetta"]
      }
    ];

    let migliore = {
      nome: "Documento non riconosciuto",
      chiave: "generico",
      score: 0
    };

    profili.forEach(function (profilo) {
      let score = 0;

      profilo.parole.forEach(function (parola) {
        if (t.includes(parola)) {
          score += 1;
        }
      });

      if (score > migliore.score) {
        migliore = {
          nome: profilo.nome,
          chiave: profilo.chiave,
          score
        };
      }
    });

    if (migliore.score === 0) {
      return {
        nome: "Documento leggibile, tema non riconosciuto",
        chiave: "generico",
        score: 0
      };
    }

    return migliore;
  }

  async function leggiTxt(file) {
    return pulisciTesto(await file.text());
  }

  async function leggiPdfTestoDiretto(file) {
    if (!window.pdfjsLib) {
      throw new Error("PDF.js non caricato.");
    }

    const buffer = await file.arrayBuffer();
    const pdf = await window.pdfjsLib.getDocument({ data: buffer }).promise;
    const pagine = [];

    for (let numero = 1; numero <= pdf.numPages; numero += 1) {
      setStatus("Controllo testo PDF pagina " + numero + " di " + pdf.numPages, "quality-warn");

      const pagina = await pdf.getPage(numero);
      const contenuto = await pagina.getTextContent();

      const testoPagina = contenuto.items
        .map(function (item) {
          return String(item.str || "").trim();
        })
        .filter(Boolean)
        .join(" ");

      if (testoPagina) {
        pagine.push(testoPagina);
      }
    }

    return pulisciTesto(pagine.join("\n\n"));
  }

  async function renderizzaPaginaPdfComeBlob(pdf, numeroPagina) {
    const pagina = await pdf.getPage(numeroPagina);
    const viewport = pagina.getViewport({ scale: 2.4 });
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");

    canvas.width = Math.floor(viewport.width);
    canvas.height = Math.floor(viewport.height);

    await pagina.render({
      canvasContext: ctx,
      viewport
    }).promise;

    return await new Promise(function (resolve) {
      canvas.toBlob(resolve, "image/png");
    });
  }

  async function ocrBlob(blob, etichetta) {
    if (!window.Tesseract) {
      throw new Error("Tesseract.js non caricato.");
    }

    const risultato = await window.Tesseract.recognize(
      blob,
      "ita+eng",
      {
        logger: function (m) {
          if (!m || !m.status) return;

          const percentuale = m.progress
            ? " " + Math.round(m.progress * 100) + "%"
            : "";

          setStatus(etichetta + ": " + m.status + percentuale, "quality-warn");
        }
      }
    );

    return pulisciTesto(
      risultato &&
      risultato.data &&
      risultato.data.text
        ? risultato.data.text
        : ""
    );
  }

  async function leggiPdfConOcr(file) {
    if (!window.pdfjsLib) {
      throw new Error("PDF.js non caricato.");
    }

    const buffer = await file.arrayBuffer();
    const pdf = await window.pdfjsLib.getDocument({ data: buffer }).promise;
    const maxPagine = Math.min(pdf.numPages, 8);
    const testi = [];

    for (let pagina = 1; pagina <= maxPagine; pagina += 1) {
      setStatus("PDF immagine: preparo OCR pagina " + pagina + " di " + maxPagine, "quality-warn");

      const blob = await renderizzaPaginaPdfComeBlob(pdf, pagina);

      if (!blob) continue;

      const testo = await ocrBlob(blob, "OCR PDF pagina " + pagina + "/" + maxPagine);

      if (testo) {
        testi.push(testo);
      }
    }

    return pulisciTesto(testi.join("\n\n"));
  }

  async function leggiImmagineConOcr(file) {
    const preview = el("preview");
    preview.src = URL.createObjectURL(file);
    preview.style.display = "block";

    return await ocrBlob(file, "OCR immagine");
  }

  async function gestisciFile(file) {
    const nome = file.name || "";
    const tipo = file.type || "";

    stato.ultimoFile = file;
    stato.ultimoTipo = tipo;
    stato.ultimoTesto = "";

    el("testoEstratto").value = "";
    el("risultato").innerHTML = "";
    el("preview").style.display = "none";

    if (/\.txt$/i.test(nome) || tipo.startsWith("text/")) {
      setStatus("Lettura TXT in corso...", "quality-warn");
      return await leggiTxt(file);
    }

    if (/\.pdf$/i.test(nome) || tipo === "application/pdf") {
      setStatus("Lettura PDF: provo prima testo selezionabile...", "quality-warn");

      const testoDiretto = await leggiPdfTestoDiretto(file);
      const qualitaDiretta = analizzaQualitaTesto(testoDiretto);

      if (qualitaDiretta.valido) {
        return testoDiretto;
      }

      setStatus("PDF senza testo selezionabile utile: avvio OCR sulle pagine immagine.", "quality-warn");

      return await leggiPdfConOcr(file);
    }

    if (/^image\//i.test(tipo) || /\.(png|jpe?g|webp)$/i.test(nome)) {
      setStatus("Immagine caricata: avvio OCR.", "quality-warn");
      return await leggiImmagineConOcr(file);
    }

    throw new Error("Formato non supportato. Usa TXT, PDF, JPG, PNG o WEBP.");
  }

  function mostraRisultatoAnalisi(testo) {
    const qualita = analizzaQualitaTesto(testo);
    const tema = qualita.valido
      ? riconosciTipoContenuto(testo)
      : {
          nome: "Immagine o file senza testo documentale utile",
          chiave: "non_documentale",
          score: 0
        };

    const classe = qualita.livello === "ok"
      ? "quality-ok"
      : qualita.livello === "warn"
        ? "quality-warn"
        : "quality-bad";

    el("risultato").innerHTML = `
      <section class="result-card">
        <span class="pill">Analisi OCR</span>
        <h2>${escapeHtml(tema.nome)}</h2>

        <p class="${classe}">
          ${escapeHtml(qualita.messaggio)}
        </p>

        <p>
          Parole rilevate: <strong>${qualita.parole}</strong><br>
          Parole uniche: <strong>${qualita.paroleUniche}</strong><br>
          Qualità lettere: <strong>${Math.round(qualita.rapportoLettere * 100)}%</strong>
        </p>

        <p>
          ${qualita.valido
            ? "Il testo può essere copiato e usato nel motore universale."
            : "Questo file non deve essere trasformato in Sport, Curriculum o altro tema: non contiene testo documentale affidabile."}
        </p>
      </section>
    `;

    if (qualita.valido) {
      setStatus("Testo valido estratto. Tema riconosciuto: " + tema.nome, "quality-ok");
    } else {
      setStatus("File gestito correttamente: non contiene testo documentale affidabile.", "quality-bad");
    }
  }

  async function caricaFileDaInput(evento) {
    const file = evento.target.files && evento.target.files[0];

    if (!file) return;

    try {
      const testo = await gestisciFile(file);
      const testoPulito = pulisciTesto(testo);

      stato.ultimoTesto = testoPulito;
      el("testoEstratto").value = testoPulito;

      mostraRisultatoAnalisi(testoPulito);
    } catch (errore) {
      console.error(errore);

      setStatus("Errore: " + errore.message, "quality-bad");
      el("risultato").innerHTML = `
        <section class="result-card">
          <span class="pill">Errore</span>
          <h2>File non letto</h2>
          <p class="quality-bad">${escapeHtml(errore.message)}</p>
        </section>
      `;
    } finally {
      evento.target.value = "";
    }
  }

  function analizzaTestoManuale() {
    const testo = el("testoEstratto").value;
    mostraRisultatoAnalisi(testo);
  }

  async function copiaTesto() {
    const testo = el("testoEstratto").value.trim();

    if (!testo) {
      setStatus("Non c’è testo da copiare.", "quality-bad");
      return;
    }

    await navigator.clipboard.writeText(testo);
    setStatus("Testo copiato. Ora puoi incollarlo nel motore universale.", "quality-ok");
  }

  function avvia() {
    el("btnFile").addEventListener("click", function () {
      el("fileInput").click();
    });

    el("fileInput").addEventListener("change", caricaFileDaInput);
    el("btnAnalizza").addEventListener("click", analizzaTestoManuale);
    el("btnCopia").addEventListener("click", copiaTesto);
  }

  document.addEventListener("DOMContentLoaded", avvia);
})();
