(function () {
  function normalizza(testo) {
    return (testo || "").replace(/\s+/g, " ").trim().toLowerCase();
  }

  function bottoneGenera(btn) {
    if (!btn) return null;

    const testo = normalizza(btn.textContent);

    if (testo.includes("genera riassunto")) return "riassunto";
    if (testo.includes("genera card")) return "card";
    if (testo.includes("genera test")) return "test";
    if (testo.includes("genera domande studio")) return "domande";

    return null;
  }

  function visibile(el) {
    if (!el) return false;
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return s.display !== "none" && s.visibility !== "hidden" && r.width > 80 && r.height > 40;
  }

  function trovaOutput(tipo) {
    const parole = {
      riassunto: ["riassunto", "summary"],
      card: ["card", "schede"],
      test: ["test", "quiz", "domande del test"],
      domande: ["domande studio", "domande di studio", "studio"]
    }[tipo] || [];

    const selettori = [
      "#summaryOutput",
      "#riassuntoOutput",
      "#cardsOutput",
      "#cardOutput",
      "#testOutput",
      "#quizOutput",
      "#studyQuestionsOutput",
      "#domandeStudioOutput",
      "#output",
      "#result",
      "#results",
      ".output",
      ".results",
      ".generated-output",
      ".generated-cards",
      ".cards-output",
      ".summary-output",
      ".test-output",
      ".study-output"
    ];

    for (const sel of selettori) {
      const el = document.querySelector(sel);
      if (visibile(el)) return el;
    }

    const candidati = Array.from(document.querySelectorAll("section, article, div"))
      .filter(visibile)
      .filter((el) => {
        if (el.closest("#full-width-action-zone")) return false;
        const t = normalizza(el.textContent);
        return parole.some((p) => t.includes(p));
      });

    if (candidati.length) {
      return candidati[candidati.length - 1];
    }

    return document.querySelector("main") || document.body;
  }

  function mostraAvviso(tipo) {
    let box = document.getElementById("generazione-in-corso-box");

    if (!box) {
      box = document.createElement("div");
      box.id = "generazione-in-corso-box";
      box.style.cssText = `
        margin: 18px 0;
        padding: 18px 22px;
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(20,68,104,0.95), rgba(13,63,54,0.95));
        border: 1px solid rgba(90,255,195,0.35);
        color: white;
        font-weight: 900;
        font-size: 1.05rem;
        box-shadow: 0 12px 26px rgba(0,0,0,0.30), 0 0 22px rgba(0,255,170,0.13);
      `;

      const zona = document.getElementById("full-width-action-zone");
      if (zona && zona.parentElement) {
        zona.parentElement.insertBefore(box, zona.nextSibling);
      } else {
        document.body.prepend(box);
      }
    }

    const label = {
      riassunto: "riassunto",
      card: "card",
      test: "test",
      domande: "domande studio"
    }[tipo] || "materiale";

    box.textContent = "Generazione " + label + " in corso...";

    return box;
  }

  function scorriAlRisultato(tipo) {
    const avviso = mostraAvviso(tipo);

    avviso.scrollIntoView({
      behavior: "smooth",
      block: "center"
    });

    [700, 1400, 2400, 3600].forEach((tempo) => {
      setTimeout(() => {
        const target = trovaOutput(tipo);
        if (target) {
          target.scrollIntoView({
            behavior: "smooth",
            block: "start"
          });
        }
      }, tempo);
    });
  }

  document.addEventListener("click", function (event) {
    const btn = event.target.closest("button, a, [role='button']");
    const tipo = bottoneGenera(btn);

    if (!tipo) return;

    scorriAlRisultato(tipo);
  }, true);
})();
