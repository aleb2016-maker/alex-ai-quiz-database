(function () {
  "use strict";

  const stato = {
    file: null,
    tipo: "",
    pdfCache: null,
    fonte: "",
    testo: ""
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
      .replace(/[|\\/_]{2,}/g, " ")
      .replace(/[^\S\r\n]+/g, " ")
      .replace(/\s+\n/g, "\n")
      .replace(/\n\s+/g, "\n")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
  }

  function analizzaQualitaTesto(testo, fonte, confidenza) {
    const pulito = pulisciTesto(testo);
    const senzaSpazi = pulito.replace(/\s/g, "");
    const lettere = pulito.match(/[A-Za-zÀ-ÿ]/g) || [];
    const parole = pulito.match(/[A-Za-zÀ-ÿ]{2,}/g) || [];
    const paroleForti = pulito.match(/[A-Za-zÀ-ÿ]{3,}/g) || [];
    const numeri = pulito.match(/[0-9]/g) || [];
    const simboliStrani = pulito.match(/[^A-Za-zÀ-ÿ0-9\s.,;:!?'"()€%ÀÈÉÌÒÙàèéìòù-]/g) || [];

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
      paroleForti.map(function (p) {
        return p.toLowerCase();
      })
    );

    const rapportoLettere = senzaSpazi.length ? lettere.length / senzaSpazi.length : 0;
    const rapportoSimboli = senzaSpazi.length ? simboliStrani.length / senzaSpazi.length : 1;
    const rapportoRigheCorte = righe.length ? righeCorte / righe.length : 1;

    const fonteOcr = fonte === "ocr-immagine" || fonte === "ocr-pdf";

    const confidenzaOk =
      !fonteOcr ||
      confidenza === null ||
      confidenza === undefined ||
      confidenza >= 70;

    const valido =
      paroleForti.length >= 8 &&
      paroleUniche.size >= 6 &&
      rapportoLettere >= 0.62 &&
      rapportoSimboli <= 0.10 &&
      rapportoRigheCorte <= 0.50 &&
      numeri.length <= lettere.length * 1.4 &&
      confidenzaOk;

    return {
      valido,
      testo: pulito,
      parole: parole.length,
      paroleForti: paroleForti.length,
      paroleUniche: paroleUniche.size,
      rapportoLettere,
      rapportoSimboli,
      rapportoRigheCorte,
      confidenza
    };
  }

  function riconosciTema(testo, fonte) {
    const analisi = analizzaQualitaTesto(testo, fonte, null);

    if (!analisi.valido) {
      return "Immagine o file senza testo documentale affidabile";
    }

    const t = pulisciTesto(testo).toLowerCase();

    const profili = [
      {
        nome: "Curriculum vitae",
        parole: ["curriculum", "esperienza", "esperienze", "competenze", "formazione", "obiettivo", "sviluppatore", "github"]
      },
      {
        nome: "Sport e allenamento",
        parole: ["allenamento", "riscaldamento", "camminata", "bicicletta", "nuoto", "cardio", "stretching", "defaticamento", "squat", "plank"]
      },
      {
        nome: "Documento personale",
        parole: ["codice fiscale", "residenza", "scadenza", "numero documento", "certificato", "tessera"]
      },
      {
        nome: "Documento aziendale",
        parole: ["azienda", "procedura", "processo", "responsabile", "cliente", "rischio", "sicurezza", "report", "kpi"]
      },
      {
        nome: "Poesia",
        parole: ["poesia", "verso", "strofa", "rima", "metafora"]
      },
      {
        nome: "Hobby o progetto",
        parole: ["progetto", "materiali", "strumenti", "passaggi", "attività", "costruire", "creare", "ricetta"]
      }
    ];

    let migliore = {
      nome: "Documento leggibile, tema non riconosciuto",
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
          score
        };
      }
    });

    const sembraFumetto =
      fonte === "ocr-immagine" ||
      fonte === "ocr-pdf";

    const haDialoghi =
      /[!?]/.test(testo) ||
      /\b(ciao|ehi|guarda|andiamo|aiuto|piacere|sono|disse|rispose|leo|roma|mappa|ristorante)\b/i.test(testo);

    if (sembraFumetto && haDialoghi && migliore.score < 3) {
      return "Fumetto / dialoghi";
    }

    if (migliore.score < 1) {
      return "Documento leggibile, tema non riconosciuto";
    }

    return migliore.nome;
  }

  function mostraRisultato(testo, fonte, confidenza) {
    const analisi = analizzaQualitaTesto(testo, fonte, confidenza);
    const tema = analisi.valido
      ? riconosciTema(testo, fonte)
      : "Immagine o file senza testo documentale affidabile";

    const classe = analisi.valido ? "quality-ok" : "quality-bad";

    el("risultato").innerHTML = `
      <section class="result-card">
        <span class="pill">Analisi OCR</span>
        <h2>${escapeHtml(tema)}</h2>

        <p class="${classe}">
          ${analisi.valido
            ? "Testo valido: può essere copiato e usato nel motore universale."
            : "Testo non utilizzabile: OCR spazzatura oppure immagine senza testo documentale utile."}
        </p>

        <p>
          Fonte: <strong>${escapeHtml(fonte || "sconosciuta")}</strong><br>
          Confidenza OCR: <strong>${confidenza === null || confidenza === undefined ? "n/d" : Math.round(confidenza) + "%"}</strong><br>
          Parole rilevate: <strong>${analisi.parole}</strong><br>
          Parole uniche: <strong>${analisi.paroleUniche}</strong><br>
          Qualità lettere: <strong>${Math.round(analisi.rapportoLettere * 100)}%</strong><br>
          Simboli strani: <strong>${Math.round(analisi.rapportoSimboli * 100)}%</strong>
        </p>

        <p>
          ${analisi.valido
            ? "Puoi copiare il testo e incollarlo nel motore universale."
            : "Non viene classificato come Sport, Poesia o altro tema a caso."}
        </p>
      </section>
    `;

    if (analisi.valido) {
      setStatus("Testo valido estratto. Tema riconosciuto: " + tema, "quality-ok");
    } else {
      setStatus("File gestito: testo non affidabile, quindi non viene usato.", "quality-bad");
    }

    return analisi;
  }

  async function leggiTxt(file) {
    return pulisciTesto(await file.text());
  }

  async function caricaPdf(file) {
    const buffer = await file.arrayBuffer();
    return await window.pdfjsLib.getDocument({ data: buffer }).promise;
  }

  async function leggiPdfTestoDiretto(pdf) {
    const parti = [];

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
        parti.push(testoPagina);
      }
    }

    return pulisciTesto(parti.join("\n\n"));
  }

  async function renderPdfPaginaBlob(pdf, numeroPagina) {
    const pagina = await pdf.getPage(numeroPagina);
    const viewport = pagina.getViewport({ scale: 2.6 });
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

    return {
      testo: pulisciTesto(
        risultato &&
        risultato.data &&
        risultato.data.text
          ? risultato.data.text
          : ""
      ),
      confidenza:
        risultato &&
        risultato.data &&
        typeof risultato.data.confidence === "number"
          ? risultato.data.confidence
          : null
    };
  }

  async function ocrPdf(pdf) {
    const maxPagine = Math.min(pdf.numPages, 8);
    const testi = [];
    const confidenze = [];

    for (let pagina = 1; pagina <= maxPagine; pagina += 1) {
      setStatus("OCR PDF pagina " + pagina + " di " + maxPagine, "quality-warn");

      const blob = await renderPdfPaginaBlob(pdf, pagina);
      const risultato = await ocrBlob(blob, "OCR PDF pagina " + pagina + "/" + maxPagine);

      if (risultato.testo) testi.push(risultato.testo);
      if (typeof risultato.confidenza === "number") confidenze.push(risultato.confidenza);
    }

    const confidenzaMedia = confidenze.length
      ? confidenze.reduce(function (a, b) { return a + b; }, 0) / confidenze.length
      : null;

    return {
      testo: pulisciTesto(testi.join("\n\n")),
      confidenza: confidenzaMedia
    };
  }

  async function gestisciCaricamento(file) {
    const nome = file.name || "";
    const tipo = file.type || "";

    stato.file = file;
    stato.tipo = tipo;
    stato.pdfCache = null;
    stato.fonte = "";
    stato.testo = "";

    el("testoEstratto").value = "";
    el("risultato").innerHTML = "";

    const preview = el("preview");
    preview.style.display = "none";
    preview.removeAttribute("src");

    if (/^image\//i.test(tipo) || /\.(png|jpe?g|webp)$/i.test(nome)) {
      preview.src = URL.createObjectURL(file);
      preview.style.display = "block";

      setStatus(
        "Immagine caricata. Non la classifico e non invento testo. Premi “Estrai testo OCR dal file” solo se l’immagine contiene scritte leggibili.",
        "quality-warn"
      );

      el("risultato").innerHTML = `
        <section class="result-card">
          <span class="pill">Immagine</span>
          <h2>Immagine caricata</h2>
          <p class="quality-warn">
            Questa è un’immagine. Non viene classificata come Sport, Poesia o altro tema.
            Se contiene testo leggibile, usa il pulsante OCR.
          </p>
        </section>
      `;

      return;
    }

    if (/\.txt$/i.test(nome) || tipo.startsWith("text/")) {
      setStatus("Lettura TXT in corso...", "quality-warn");

      const testo = await leggiTxt(file);
      const analisi = mostraRisultato(testo, "txt", null);

      if (analisi.valido) {
        el("testoEstratto").value = testo;
        stato.testo = testo;
        stato.fonte = "txt";
      }

      return;
    }

    if (/\.pdf$/i.test(nome) || tipo === "application/pdf") {
      setStatus("Lettura PDF: controllo testo selezionabile.", "quality-warn");

      const pdf = await caricaPdf(file);
      stato.pdfCache = pdf;

      const testo = await leggiPdfTestoDiretto(pdf);
      const analisi = analizzaQualitaTesto(testo, "pdf", null);

      if (analisi.valido) {
        el("testoEstratto").value = testo;
        stato.testo = testo;
        stato.fonte = "pdf";

        mostraRisultato(testo, "pdf", null);
        return;
      }

      setStatus(
        "PDF immagine o fumetto rilevato. Non metto testo spazzatura. Premi “Estrai testo OCR dal file” per provare l’OCR sulle pagine.",
        "quality-warn"
      );

      el("risultato").innerHTML = `
        <section class="result-card">
          <span class="pill">PDF immagine</span>
          <h2>PDF senza testo selezionabile utile</h2>
          <p class="quality-warn">
            Probabilmente è un fumetto, una scansione o un PDF composto da immagini.
            Usa il pulsante OCR per tentare l’estrazione del testo.
          </p>
        </section>
      `;

      return;
    }

    setStatus("Formato non supportato. Usa TXT, PDF, JPG, PNG o WEBP.", "quality-bad");
  }

  async function avviaOcrSulFile() {
    if (!stato.file) {
      setStatus("Prima carica un file.", "quality-bad");
      return;
    }

    const nome = stato.file.name || "";
    const tipo = stato.file.type || "";

    try {
      if (/^image\//i.test(tipo) || /\.(png|jpe?g|webp)$/i.test(nome)) {
        setStatus("Avvio OCR immagine...", "quality-warn");

        const risultato = await ocrBlob(stato.file, "OCR immagine");
        const analisi = mostraRisultato(risultato.testo, "ocr-immagine", risultato.confidenza);

        if (analisi.valido) {
          el("testoEstratto").value = risultato.testo;
          stato.testo = risultato.testo;
          stato.fonte = "ocr-immagine";
        } else {
          el("testoEstratto").value = "";
        }

        return;
      }

      if (/\.pdf$/i.test(nome) || tipo === "application/pdf") {
        setStatus("Avvio OCR PDF immagine/fumetto...", "quality-warn");

        const pdf = stato.pdfCache || await caricaPdf(stato.file);
        stato.pdfCache = pdf;

        const risultato = await ocrPdf(pdf);
        const analisi = mostraRisultato(risultato.testo, "ocr-pdf", risultato.confidenza);

        if (analisi.valido) {
          el("testoEstratto").value = risultato.testo;
          stato.testo = risultato.testo;
          stato.fonte = "ocr-pdf";
        } else {
          el("testoEstratto").value = "";
        }

        return;
      }

      setStatus("OCR disponibile solo per immagini e PDF immagine.", "quality-bad");
    } catch (errore) {
      console.error(errore);
      setStatus("Errore OCR: " + errore.message, "quality-bad");
      el("testoEstratto").value = "";
    }
  }

  function analizzaTestoManuale() {
    const testo = el("testoEstratto").value.trim();

    if (!testo) {
      setStatus("Non c’è testo da analizzare.", "quality-bad");
      return;
    }

    mostraRisultato(testo, "manuale", null);
  }

  async function copiaTesto() {
    const testo = el("testoEstratto").value.trim();
    const analisi = analizzaQualitaTesto(testo, "manuale", null);

    if (!testo || !analisi.valido) {
      setStatus("Testo non copiato: è vuoto o non affidabile.", "quality-bad");
      return;
    }

    await navigator.clipboard.writeText(testo);
    setStatus("Testo copiato. Ora puoi incollarlo nel motore universale.", "quality-ok");
  }

  function avvia() {
    el("btnFile").addEventListener("click", function () {
      el("fileInput").click();
    });

    el("fileInput").addEventListener("change", async function (evento) {
      const file = evento.target.files && evento.target.files[0];
      if (!file) return;

      try {
        await gestisciCaricamento(file);
      } catch (errore) {
        console.error(errore);
        setStatus("Errore caricamento file: " + errore.message, "quality-bad");
      } finally {
        evento.target.value = "";
      }
    });

    const btnOcr = el("btnOcrFile");
    if (btnOcr) {
      btnOcr.addEventListener("click", avviaOcrSulFile);
    }

    el("btnAnalizza").addEventListener("click", analizzaTestoManuale);
    el("btnCopia").addEventListener("click", copiaTesto);
  }

  document.addEventListener("DOMContentLoaded", avvia);
})();
