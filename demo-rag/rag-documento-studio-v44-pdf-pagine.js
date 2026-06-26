(function () {
  function caricaScript(src, check) {
    return new Promise(function (resolve, reject) {
      if (check()) return resolve();
      const old = Array.from(document.querySelectorAll("script")).find(s => s.src && s.src.includes(src));
      if (old && check()) return resolve();
      const s = document.createElement("script");
      s.src = src;
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }

  async function preparaLibrerie() {
    await caricaScript(
      "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js",
      function () { return !!window.html2canvas; }
    );
    await caricaScript(
      "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js",
      function () { return !!(window.jspdf && window.jspdf.jsPDF); }
    );
  }

  function pulisciTesto(testo) {
    return String(testo || "")
      .replace(/\s+/g, " ")
      .replace(/\u00a0/g, " ")
      .trim();
  }

  function trovaTitolo(testo) {
    return Array.from(document.querySelectorAll("h1,h2,h3,h4")).find(function (el) {
      return pulisciTesto(el.textContent).toLowerCase().includes(testo.toLowerCase());
    });
  }

  function trovaBloccoDaTitolo(testo) {
    const titolo = trovaTitolo(testo);
    if (!titolo) return null;
    return titolo.closest("section, article, .panel, .rag-section, .output-section, .result-section, .section")
      || titolo.parentElement;
  }

  function trovaCardsVisibili() {
    const elementi = Array.from(document.querySelectorAll(
      ".rag-graphic-card, .graphic-card, .study-card, .learning-card, .card-item, [class*='card']"
    ));

    const cards = elementi.filter(function (el) {
      const box = el.getBoundingClientRect();
      const testo = pulisciTesto(el.textContent);
      const no = el.closest("button, textarea, input, nav, header");
      return !no && box.width >= 180 && box.height >= 220 && testo.length >= 30;
    });

    const uniche = [];
    const visti = new Set();

    cards.forEach(function (card) {
      const chiave = pulisciTesto(card.textContent).slice(0, 120);
      if (!visti.has(chiave)) {
        visti.add(chiave);
        uniche.push(card);
      }
    });

    return uniche;
  }

  function creaPagina(titolo, kicker) {
    const pagina = document.createElement("section");
    pagina.className = "v44-pdf-page";
    pagina.innerHTML = `
      <div class="v44-pdf-kicker">${kicker || ""}</div>
      <h1>${titolo}</h1>
      <div class="v44-pdf-body"></div>
    `;
    return pagina;
  }

  function ripulisciClone(clone) {
    clone.querySelectorAll("button,input,textarea").forEach(function (el) { el.remove(); });

    clone.querySelectorAll("*").forEach(function (el) {
      if (el.children.length === 0) {
        el.textContent = pulisciTesto(el.textContent);
      }
    });

    const headings = clone.querySelectorAll("h1,h2,h3,h4");
    if (headings.length > 0) {
      headings.forEach(function (h, index) {
        if (index === 0 && /riassunto pulito/i.test(pulisciTesto(h.textContent))) {
          h.remove();
        }
      });
    }

    return clone;
  }

  function creaPaginaRiassunto() {
    const pagina = creaPagina("Riassunto pulito", "RIASSUNTO");
    const body = pagina.querySelector(".v44-pdf-body");
    const blocco = trovaBloccoDaTitolo("Riassunto");

    if (!blocco) {
      body.innerHTML = "<p>Nessun riassunto trovato.</p>";
      return pagina;
    }

    const clone = ripulisciClone(blocco.cloneNode(true));
    body.appendChild(clone);
    return pagina;
  }

  function creaCardClone(card) {
    const clone = ripulisciClone(card.cloneNode(true));
    clone.classList.add("v44-pdf-card-clone");
    return clone;
  }

  function testoLungoElements(card) {
    return Array.from(card.querySelectorAll("p, li, span, div"))
      .filter(function (el) {
        const t = pulisciTesto(el.textContent);
        return t.length > 30 && el.children.length === 0;
      })
      .sort(function (a, b) {
        return pulisciTesto(b.textContent).length - pulisciTesto(a.textContent).length;
      });
  }

  function troncaElemento(el) {
    const testo = pulisciTesto(el.textContent);
    if (testo.length < 40) return false;

    let nuovo = testo;
    if (nuovo.length > 170) {
      nuovo = nuovo.slice(0, 160).replace(/[,:;\s]+[^,:;\s]*$/, "").trim() + "…";
    } else if (nuovo.length > 120) {
      nuovo = nuovo.slice(0, 112).replace(/[,:;\s]+[^,:;\s]*$/, "").trim() + "…";
    } else {
      nuovo = nuovo.slice(0, 96).replace(/[,:;\s]+[^,:;\s]*$/, "").trim() + "…";
    }

    if (nuovo !== testo) {
      el.textContent = nuovo;
      return true;
    }
    return false;
  }

  function forzaFitCard(card) {
    card.style.overflow = "hidden";

    let zoom = 1;
    let tentativi = 0;

    while (card.scrollHeight > card.clientHeight && zoom > 0.84 && tentativi < 12) {
      zoom -= 0.02;
      card.style.zoom = String(zoom);
      tentativi += 1;
    }

    if (card.scrollHeight <= card.clientHeight) return true;

    const elementi = testoLungoElements(card);
    for (const el of elementi) {
      if (card.scrollHeight <= card.clientHeight) break;
      troncaElemento(el);
    }

    if (card.scrollHeight <= card.clientHeight) return true;

    let shrink = 0;
    while (card.scrollHeight > card.clientHeight && shrink < 8) {
      const paragrafi = card.querySelectorAll("p, li, span");
      paragrafi.forEach(function (el) {
        const st = window.getComputedStyle(el);
        const fs = parseFloat(st.fontSize);
        if (fs > 13) el.style.fontSize = (fs - 0.5) + "px";
        const lh = parseFloat(st.lineHeight);
        if (!Number.isNaN(lh) && lh > 15) el.style.lineHeight = (lh - 0.5) + "px";
      });
      shrink += 1;
    }

    return card.scrollHeight <= card.clientHeight;
  }

  function creaPaginaCard(cards, singola) {
    const pagina = creaPagina("Card colorate con disegni", "CARD");
    const body = pagina.querySelector(".v44-pdf-body");
    const grid = document.createElement("div");
    grid.className = singola ? "v44-pdf-card-grid single" : "v44-pdf-card-grid";

    cards.forEach(function (card) {
      grid.appendChild(card);
    });

    body.appendChild(grid);
    return pagina;
  }

  function generaPagineCard(area) {
    const sorgenti = trovaCardsVisibili();
    const pagine = [];
    let i = 0;

    while (i < sorgenti.length) {
      const cloneA = creaCardClone(sorgenti[i]);
      const cloneB = sorgenti[i + 1] ? creaCardClone(sorgenti[i + 1]) : null;

      if (cloneB) {
        const paginaTest = creaPaginaCard([cloneA, cloneB], false);
        area.appendChild(paginaTest);

        const fitA = forzaFitCard(cloneA);
        const fitB = forzaFitCard(cloneB);

        if (fitA && fitB) {
          pagine.push(paginaTest);
          i += 2;
        } else {
          paginaTest.remove();

          const singleA = creaPaginaCard([creaCardClone(sorgenti[i])], true);
          area.appendChild(singleA);
          forzaFitCard(singleA.querySelector(".v44-pdf-card-clone"));
          pagine.push(singleA);

          const singleB = creaPaginaCard([creaCardClone(sorgenti[i + 1])], true);
          area.appendChild(singleB);
          forzaFitCard(singleB.querySelector(".v44-pdf-card-clone"));
          pagine.push(singleB);

          i += 2;
        }
      } else {
        const paginaSingle = creaPaginaCard([cloneA], true);
        area.appendChild(paginaSingle);
        forzaFitCard(cloneA);
        pagine.push(paginaSingle);
        i += 1;
      }
    }

    return pagine;
  }

  async function scaricaPdfPaginato() {
    await preparaLibrerie();

    const cards = trovaCardsVisibili();
    if (!cards.length) {
      alert("Prima genera il materiale: non trovo card da esportare.");
      return;
    }

    const area = document.createElement("div");
    area.id = "v44PdfArea";
    area.style.position = "fixed";
    area.style.left = "-20000px";
    area.style.top = "0";
    area.style.width = "1240px";
    area.style.zIndex = "-9999";
    document.body.appendChild(area);

    const pagine = [];
    const p1 = creaPaginaRiassunto();
    area.appendChild(p1);
    pagine.push(p1);

    generaPagineCard(area).forEach(function (p) { pagine.push(p); });

    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF("landscape", "pt", "a4");
    const pageW = pdf.internal.pageSize.getWidth();
    const pageH = pdf.internal.pageSize.getHeight();

    for (let i = 0; i < pagine.length; i++) {
      const canvas = await window.html2canvas(pagine[i], {
        backgroundColor: "#07111f",
        scale: 2,
        useCORS: true,
        logging: false,
        windowWidth: 1240,
        windowHeight: 760
      });

      const img = canvas.toDataURL("image/jpeg", 0.96);
      const ratio = Math.min(pageW / canvas.width, pageH / canvas.height);
      const w = canvas.width * ratio;
      const h = canvas.height * ratio;
      const x = (pageW - w) / 2;
      const y = (pageH - h) / 2;

      if (i > 0) pdf.addPage();
      pdf.setFillColor(7, 17, 31);
      pdf.rect(0, 0, pageW, pageH, "F");
      pdf.addImage(img, "JPEG", x, y, w, h);
    }

    area.remove();
    pdf.save("materiale-studio-rag-paginato.pdf");
  }

  function collegaBottone() {
    const bottoni = Array.from(document.querySelectorAll("button,a"));
    const btn = bottoni.find(function (b) {
      return pulisciTesto(b.textContent).toLowerCase().includes("scarica pdf");
    });

    if (!btn) return;

    const nuovo = btn.cloneNode(true);
    btn.parentNode.replaceChild(nuovo, btn);

    nuovo.addEventListener("click", function (ev) {
      ev.preventDefault();
      ev.stopPropagation();
      scaricaPdfPaginato().catch(function (err) {
        console.error(err);
        alert("Errore PDF: " + (err.message || err));
      });
    }, true);
  }

  document.addEventListener("DOMContentLoaded", function () {
    setTimeout(collegaBottone, 1200);
  });
})();
