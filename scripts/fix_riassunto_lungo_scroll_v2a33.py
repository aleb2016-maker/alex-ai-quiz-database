from pathlib import Path
from datetime import datetime
import re

ROOT = Path.cwd()
js = ROOT / "demo-rag" / "universal-document-learning-engine.js"

report_dir = ROOT / "reports" / "fix_riassunto_lungo_scroll_v2a33"
backup_dir = report_dir / "backups"
backup_dir.mkdir(parents=True, exist_ok=True)

txt = js.read_text(encoding="utf-8")

backup = backup_dir / f"universal-document-learning-engine.js.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
backup.write_text(txt, encoding="utf-8")

helper_marker = "/* V2A33 - qualità riassunto lungo e scroll output */"

if helper_marker not in txt:
    helper = r'''
  /* V2A33 - qualità riassunto lungo e scroll output */
  function pulisciFraseRiassuntoLungoV2A33(frase) {
    return correggiSpaziPunteggiaturaV35G(String(frase || "")
      .replace(/---\s*PAGINA\s+\d+\s*---/gi, " ")
      .replace(/Titolo pagina\s+\d+\s*:\s*/gi, " ")
      .replace(/Riferimento sezione:\s*[A-Z0-9.\-]+\s*/gi, " ")
      .replace(/^Batch\s+\d+\s*\(pagine[^)]*\):\s*/i, "")
      .replace(/\bchunk cio[eè]\s+blocchi?\s+di\s+testo\b/gi, "blocchi di testo")
      .replace(/\bbatch cio[eè]\s+gruppi?\s+di\s+chunk\s+elaborati\s+insieme\b/gi, "gruppi di elaborazione")
      .replace(/\s+/g, " ")
      .trim());
  }

  function firmaFraseRiassuntoLungoV2A33(frase) {
    return String(frase || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9 ]+/g, " ")
      .replace(/\s+/g, " ")
      .split(" ")
      .filter(function (parola) {
        return parola.length > 3;
      })
      .slice(0, 22)
      .join(" ");
  }

  function frasiPuliteRiassuntoLungoV2A33(testo) {
    return normalizzaTesto(testo)
      .replace(/---\s*PAGINA\s+\d+\s*---/gi, ". ")
      .replace(/\n+/g, " ")
      .split(/(?<=[.!?])\s+/)
      .map(pulisciFraseRiassuntoLungoV2A33)
      .filter(function (frase) {
        if (frase.length < 45 || frase.length > 520) return false;
        if (/^titolo pagina/i.test(frase)) return false;
        if (/^riferimento sezione/i.test(frase)) return false;
        if (/^batch\s+\d+/i.test(frase)) return false;
        return true;
      });
  }

  function deduplicaRiassuntoLungoV2A33(frasi, limite) {
    const viste = new Set();
    const output = [];

    frasi.forEach(function (frase) {
      const firma = firmaFraseRiassuntoLungoV2A33(frase);
      if (!firma || viste.has(firma)) return;

      viste.add(firma);
      output.push(frase);
    });

    return typeof limite === "number" ? output.slice(0, limite) : output;
  }

  function paroleProfiloRiassuntoLungoV2A33(profilo) {
    const parole = [];
    const sezioni = profilo && profilo.sezioni ? profilo.sezioni : [];

    sezioni.forEach(function (sezione) {
      (sezione.parole || []).forEach(function (parola) {
        parole.push(String(parola || "").toLowerCase());
      });
    });

    parolePerSezioneRiassunto(profilo || {}, { parole: [] }).forEach(function (parola) {
      parole.push(String(parola || "").toLowerCase());
    });

    return deduplicaRiassuntoLungoV2A33(parole.filter(Boolean), 80);
  }

  function selezionaFrasiRiassuntoLungoV2A33(frasi, profilo, limite) {
    const paroleProfilo = paroleProfiloRiassuntoLungoV2A33(profilo);
    const frequenze = new Map();

    frasi.forEach(function (frase) {
      normalizzaTesto(frase).toLowerCase().split(/\s+/).forEach(function (parola) {
        const pulita = parola.replace(/[^a-zàèéìòù0-9]/gi, "");
        if (pulita.length < 5) return;
        frequenze.set(pulita, (frequenze.get(pulita) || 0) + 1);
      });
    });

    const classificate = frasi.map(function (frase, indice) {
      const lower = frase.toLowerCase();
      let score = 0;

      paroleProfilo.forEach(function (parola) {
        if (parola && lower.includes(parola)) score += 8;
      });

      lower.split(/\s+/).forEach(function (parola) {
        const pulita = parola.replace(/[^a-zàèéìòù0-9]/gi, "");
        score += frequenze.get(pulita) || 0;
      });

      if (indice < Math.max(5, frasi.length * 0.12)) score += 5;
      if (frase.length >= 90 && frase.length <= 330) score += 6;
      if (/descrive come gestire/i.test(frase)) score -= 4;

      return {
        frase: frase,
        indice: indice,
        score: score
      };
    }).sort(function (a, b) {
      return b.score - a.score;
    });

    const scelte = [];
    const firme = new Set();

    classificate.forEach(function (item) {
      if (scelte.length >= limite) return;

      const firma = firmaFraseRiassuntoLungoV2A33(item.frase);
      if (!firma || firme.has(firma)) return;

      firme.add(firma);
      scelte.push(item);
    });

    return scelte
      .sort(function (a, b) {
        return a.indice - b.indice;
      })
      .map(function (item) {
        return item.frase;
      });
  }

  function costruisciRiassuntoDaChunkV2A33(reportLungo, testoOriginale, profilo) {
    const chunks = reportLungo && reportLungo.chunks ? reportLungo.chunks : [];
    const totalPages = reportLungo && reportLungo.totalPages ? reportLungo.totalPages : 1;
    const targetChars = Math.min(
      55000,
      Math.max(9000, Math.round(String(testoOriginale || "").length * 0.18))
    );

    const sezioni = [];
    const tutteFrasi = [];

    chunks.forEach(function (chunk) {
      frasiPuliteRiassuntoLungoV2A33(chunk.text || "").forEach(function (frase) {
        tutteFrasi.push({
          frase: frase,
          pageStart: chunk.pageStart || 1,
          pageEnd: chunk.pageEnd || chunk.pageStart || 1
        });
      });
    });

    const frasiGlobali = deduplicaRiassuntoLungoV2A33(tutteFrasi.map(function (item) {
      return item.frase;
    }), 1200);

    const sintesi = selezionaFrasiRiassuntoLungoV2A33(frasiGlobali, profilo, 14);

    if (sintesi.length) {
      sezioni.push({
        titolo: "Sintesi generale",
        testo: sintesi.join(" ")
      });
    }

    const macroSezioni = Math.min(8, Math.max(5, Math.ceil(totalPages / 18)));
    const paginePerSezione = Math.max(1, Math.ceil(totalPages / macroSezioni));

    for (let i = 0; i < macroSezioni; i += 1) {
      const paginaInizio = i * paginePerSezione + 1;
      const paginaFine = Math.min(totalPages, (i + 1) * paginePerSezione);

      const frasiGruppo = tutteFrasi
        .filter(function (item) {
          return item.pageStart >= paginaInizio && item.pageStart <= paginaFine;
        })
        .map(function (item) {
          return item.frase;
        });

      const scelte = selezionaFrasiRiassuntoLungoV2A33(
        deduplicaRiassuntoLungoV2A33(frasiGruppo, 300),
        profilo,
        18
      );

      if (scelte.length) {
        sezioni.push({
          titolo: "Macro-sezione " + (i + 1) + " - pagine " + paginaInizio + "-" + paginaFine,
          testo: scelte.join(" ")
        });
      }
    }

    const usate = new Set();
    sezioni.forEach(function (sezione) {
      frasiPuliteRiassuntoLungoV2A33(sezione.testo).forEach(function (frase) {
        usate.add(firmaFraseRiassuntoLungoV2A33(frase));
      });
    });

    let caratteri = sezioni.map(function (s) { return s.testo; }).join(" ").length;
    const rimanenti = frasiGlobali.filter(function (frase) {
      return !usate.has(firmaFraseRiassuntoLungoV2A33(frase));
    });

    let indiceApprofondimento = 1;

    while (caratteri < targetChars && rimanenti.length) {
      const blocco = selezionaFrasiRiassuntoLungoV2A33(rimanenti.splice(0, 180), profilo, 16);

      if (!blocco.length) break;

      sezioni.push({
        titolo: "Approfondimento " + indiceApprofondimento,
        testo: blocco.join(" ")
      });

      caratteri = sezioni.map(function (s) { return s.testo; }).join(" ").length;
      indiceApprofondimento += 1;

      if (indiceApprofondimento > 8) break;
    }

    return sezioni.map(correggiOutputTestualeV35G);
  }

  function miglioraSezioniRiassuntoLungoV2A33(sezioni, progressive, reportLungo, testoOriginale, profilo) {
    const daChunk = costruisciRiassuntoDaChunkV2A33(reportLungo, testoOriginale, profilo);

    if (daChunk && daChunk.length >= 4) {
      return daChunk;
    }

    return (sezioni || []).map(function (sezione) {
      const frasi = deduplicaRiassuntoLungoV2A33(frasiPuliteRiassuntoLungoV2A33(sezione.testo || ""), 24);

      return {
        titolo: sezione.titolo || "Sezione riassunto",
        testo: frasi.join(" ")
      };
    }).filter(function (sezione) {
      return sezione.testo && sezione.testo.trim().length > 0;
    });
  }

  function scorriOutputGeneratoV2A33(azione) {
    if (typeof window === "undefined") return;

    window.setTimeout(function () {
      const output = areaOutput();

      if (!output || typeof output.scrollIntoView !== "function") return;

      output.scrollIntoView({
        behavior: "smooth",
        block: "start"
      });
    }, 120);
  }

'''
    needle = "  function renderizzaRiassuntoLungoV2A28"
    if needle not in txt:
        raise SystemExit("ERRORE: non trovo renderizzaRiassuntoLungoV2A28")

    txt = txt.replace(needle, helper + "\n" + needle, 1)

old_line = "    const sezioniFinali = qualita.sezioni;"
new_line = "    const sezioniFinali = miglioraSezioniRiassuntoLungoV2A33(qualita.sezioni, progressive, reportLungo, testo, profilo);"

if old_line in txt:
    txt = txt.replace(old_line, new_line, 1)

# Ripristina scroll automatico dopo i click principali, senza bloccare la pagina dopo lo scroll.
def patch_listener(match):
    btn_id = match.group(1)
    handler = match.group(2)

    if "scorriOutputGeneratoV2A33" in match.group(0):
        return match.group(0)

    return (
        f'document.getElementById("{btn_id}").addEventListener("click", async function (event) {{\n'
        f'      const risultato = {handler}(event);\n'
        f'      if (risultato && typeof risultato.then === "function") {{\n'
        f'        await risultato;\n'
        f'      }}\n'
        f'      scorriOutputGeneratoV2A33("{btn_id}");\n'
        f'    }});'
    )

txt, count = re.subn(
    r'document\.getElementById\("([^"]+)"\)\.addEventListener\("click",\s*([A-Za-z0-9_]+)\);',
    patch_listener,
    txt
)

js.write_text(txt, encoding="utf-8")

report = report_dir / "report_fix_riassunto_lungo_scroll_v2a33.md"
report.write_text(
    "# Fix V2A33 - riassunto lungo e scroll output\n\n"
    "- Puliti marker grezzi tipo PAGINA/Titolo pagina/Batch dal riassunto lungo.\n"
    "- Ricostruito riassunto lungo dai chunk reali per renderlo più esteso.\n"
    "- Target indicativo: circa 18% del testo, con limite massimo per non bloccare il browser.\n"
    "- Ripristinato scroll automatico all'area output dopo click su pulsanti principali.\n"
    "- La pagina resta libera di muoversi dopo lo scroll.\n"
    f"- Listener aggiornati: {count}\n"
    f"- Backup: {backup}\n",
    encoding="utf-8"
)

print("OK V2A33: riassunto lungo migliorato e scroll ripristinato.")
print(f"Listener aggiornati: {count}")
print(f"Backup: {backup}")
print(f"Report: {report}")
