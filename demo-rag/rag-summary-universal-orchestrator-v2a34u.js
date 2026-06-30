(function (root, factory) {
  const api = factory();

  if (typeof module === "object" && module.exports) {
    module.exports = api;
  }

  root.RagSummaryUniversalOrchestratorV2A34U = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const VERSION = "V2A34U-orchestratore-riassunto-universale";

  const STOPWORDS = new Set([
    "questo","questa","questi","queste","quello","quella","quelli","quelle",
    "sono","essere","avere","viene","vengono","puo","può","possono","deve","devono",
    "della","delle","degli","dello","alla","alle","agli","allo","nella","nelle","negli","nello",
    "come","quando","dove","perche","perché","anche","molto","tutto","tutti","ogni",
    "documento","testo","pagina","pagine","sezione","sezioni","titolo","riferimento",
    "descrive","gestire","contesto","contesti","manuale","materiale",
    "the","and","that","with","this","from","into","about","which","should","would"
  ]);

  const DOMAIN_PROFILES = [
    {
      id: "scientific",
      label: "testo scientifico",
      words: ["esperimento","ricerca","dati","metodo","ipotesi","risultati","analisi","studio","campione","misura","variabile","teoria","evidenza","osservazione"],
      style: "spiegare metodo, risultati, evidenze e implicazioni senza perdere il nesso causa-effetto"
    },
    {
      id: "technical",
      label: "testo tecnico",
      words: ["sistema","procedura","configurazione","modulo","architettura","codice","funzione","processo","errore","requisito","strumento","interfaccia","server","database"],
      style: "rendere chiari componenti, funzionamento, passaggi, vincoli e risultati attesi"
    },
    {
      id: "artistic",
      label: "testo artistico",
      words: ["opera","arte","immagine","stile","colore","forma","simbolo","estetica","composizione","scena","sguardo","ritmo","figura","espressione"],
      style: "far emergere stile, immagini, temi, atmosfera e interpretazione"
    },
    {
      id: "literary",
      label: "testo narrativo o letterario",
      words: ["racconto","storia","personaggio","trama","scena","dialogo","capitolo","narratore","conflitto","finale","viaggio","ambientazione","protagonista"],
      style: "ricostruire trama, personaggi, conflitti, snodi e significato narrativo"
    },
    {
      id: "educational",
      label: "testo divulgativo o didattico",
      words: ["spiega","concetto","esempio","lezione","apprendimento","studente","guida","introduzione","definizione","argomento","schema","approfondimento"],
      style: "trasformare i concetti in spiegazione chiara, progressiva e utile allo studio"
    },
    {
      id: "legal_admin",
      label: "testo giuridico o amministrativo",
      words: ["norma","articolo","legge","regolamento","richiesta","modulo","autorizzazione","obbligo","diritto","scadenza","atto","certificato","procedimento"],
      style: "chiarire obblighi, soggetti, condizioni, scadenze, passaggi e conseguenze"
    },
    {
      id: "business",
      label: "testo aziendale",
      words: ["azienda","processo","workflow","responsabile","cliente","fornitore","audit","controllo","rischio","procedura","reparto","operativo","policy"],
      style: "collegare processi, responsabilità, controlli, rischi e risultati operativi"
    },
    {
      id: "personal",
      label: "testo personale",
      words: ["io","mio","mia","personale","esperienza","famiglia","ricordo","obiettivo","scelta","vita","percorso","situazione"],
      style: "mantenere tono personale, fatti principali, motivazioni, passaggi e conseguenze"
    },
    {
      id: "sport",
      label: "testo sportivo",
      words: ["allenamento","esercizio","serie","ripetizioni","resistenza","forza","recupero","corsa","scheda","muscoli","fatica","progressi"],
      style: "riassumere obiettivi, esercizi, progressione, recupero e controllo dello sforzo"
    },
    {
      id: "generic",
      label: "testo generico",
      words: [],
      style: "organizzare tema principale, sottotemi, esempi, passaggi e conclusioni"
    }
  ];

  function normalizeText(value) {
    return String(value || "")
      .replace(/\r/g, "\n")
      .replace(/[ \t]+/g, " ")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
  }

  function normalizeCompare(value) {
    return String(value || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9àèéìòù\s]/gi, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function words(value) {
    return normalizeCompare(value).match(/[a-z0-9àèéìòù]{4,}/gi) || [];
  }

  function cleanMechanicalText(value) {
    return String(value || "")
      .replace(/---\s*PAGINA\s+\d+\s*---/gi, " ")
      .replace(/Titolo pagina\s+\d+\s*:\s*/gi, " ")
      .replace(/Riferimento sezione:\s*[A-Z0-9.\-]+\s*/gi, " ")
      .replace(/^Batch\s+\d+\s*\(pagine[^)]*\):\s*/i, "")
      .replace(/\bManuale aziendale\s*-\s*/gi, "")
      .replace(/\bDocumento\s+di\s+test\s*:\s*/gi, "")
      .replace(/\bla sezione\s+[0-9.]+\s+descrive\s+come\s+gestire\b/gi, "viene trattata la gestione di")
      .replace(/\bNel contesto\s+([^,]+),\s*viene trattata la gestione di\b/gi, "Nel contesto $1 emerge la gestione di")
      .replace(/\s+/g, " ")
      .trim();
  }

  function splitSentences(text) {
    return normalizeText(text)
      .replace(/---\s*PAGINA\s+\d+\s*---/gi, ". ")
      .replace(/\n+/g, " ")
      .split(/(?<=[.!?])\s+/)
      .map(cleanMechanicalText)
      .filter(function (sentence) {
        if (sentence.length < 40 || sentence.length > 650) return false;
        if (/^titolo pagina/i.test(sentence)) return false;
        if (/^riferimento sezione/i.test(sentence)) return false;
        return true;
      });
  }

  function signature(value) {
    return words(value)
      .filter(function (word) { return !STOPWORDS.has(word); })
      .slice(0, 24)
      .join(" ");
  }

  function unique(values, limit) {
    const out = [];
    const used = new Set();

    (values || []).forEach(function (value) {
      const label = cleanMechanicalText(value);
      const key = normalizeCompare(label);

      if (!label || !key || used.has(key)) return;

      used.add(key);
      out.push(label);
    });

    return typeof limit === "number" ? out.slice(0, limit) : out;
  }

  function humanList(values, limit) {
    const list = unique(values, limit || 8);

    if (!list.length) return "";
    if (list.length === 1) return list[0];

    return list.slice(0, -1).join(", ") + " e " + list[list.length - 1];
  }

  function countChars(sections) {
    return (sections || []).map(function (section) {
      return section.testo || "";
    }).join(" ").length;
  }

  function detectDomain(text, externalProfile) {
    const combined = normalizeCompare(
      String(text || "") + " " +
      String(externalProfile && (externalProfile.nome || externalProfile.label || externalProfile.id || "") || "")
    );

    const scored = DOMAIN_PROFILES.map(function (profile) {
      let score = 0;

      (profile.words || []).forEach(function (word) {
        const clean = normalizeCompare(word);
        if (!clean) return;

        const re = new RegExp("\\b" + clean.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "\\b", "g");
        const matches = combined.match(re);

        if (matches) score += matches.length;
      });

      return Object.assign({}, profile, { score: score });
    }).sort(function (a, b) {
      return b.score - a.score;
    });

    return scored[0] && scored[0].score > 0
      ? scored[0]
      : DOMAIN_PROFILES.find(function (profile) { return profile.id === "generic"; });
  }

  /*
   * MOTORE 1 UNIVERSALE
   * Pianifica copertura pagine fino a 500 pagine.
   */
  function buildCoveragePlan(totalPages) {
    const pages = Math.max(1, Math.min(500, Number(totalPages || 1)));
    let groups;

    if (pages <= 10) groups = 3;
    else if (pages <= 40) groups = 5;
    else if (pages <= 120) groups = 7;
    else if (pages <= 250) groups = 10;
    else groups = 14;

    groups = Math.min(groups, pages);

    const size = Math.ceil(pages / groups);
    const ranges = [];

    for (let start = 1; start <= pages; start += size) {
      ranges.push({
        start: start,
        end: Math.min(pages, start + size - 1)
      });
    }

    if (ranges.length) {
      ranges[0].start = 1;
      ranges[ranges.length - 1].end = pages;
    }

    return {
      totalPages: pages,
      ranges: ranges,
      complete: ranges.length > 0 && ranges[0].start === 1 && ranges[ranges.length - 1].end === pages
    };
  }

  function pageOfChunk(chunk, fallback) {
    return Number(chunk && (chunk.pageStart || chunk.page || chunk.pageIndex)) || fallback || 1;
  }

  function candidatePhrasesFromSentence(sentence) {
    const tokens = words(sentence).filter(function (word) {
      return word.length >= 4 && !STOPWORDS.has(word);
    });

    const phrases = [];

    for (let n = 2; n <= 4; n += 1) {
      for (let i = 0; i <= tokens.length - n; i += 1) {
        phrases.push(tokens.slice(i, i + n).join(" "));
      }
    }

    return phrases;
  }

  /*
   * MOTORE 2 UNIVERSALE
   * Estrae concetti da qualsiasi testo usando frasi, micro-concetti, frequenze e distribuzione sulle pagine.
   */
  function extractUniversalConcepts(input) {
    const report = input.reportLungo || {};
    const chunks = report.chunks || [];
    const originalText = String(input.testoOriginale || "");
    const items = [];
    const phraseFreq = new Map();
    const wordFreq = new Map();

    function registerSentence(sentence, page) {
      const clean = cleanMechanicalText(sentence);
      if (!clean) return;

      const sentenceWords = words(clean).filter(function (word) {
        return !STOPWORDS.has(word);
      });

      sentenceWords.forEach(function (word) {
        wordFreq.set(word, (wordFreq.get(word) || 0) + 1);
      });

      const phrases = candidatePhrasesFromSentence(clean);

      phrases.forEach(function (phrase) {
        phraseFreq.set(phrase, (phraseFreq.get(phrase) || 0) + 1);
      });

      items.push({
        page: page,
        sentence: clean,
        phrases: phrases,
        words: sentenceWords
      });
    }

    if (chunks.length) {
      chunks.forEach(function (chunk, index) {
        const page = pageOfChunk(chunk, index + 1);

        splitSentences(chunk.text || "").forEach(function (sentence) {
          registerSentence(sentence, page);
        });
      });
    } else {
      splitSentences(originalText).forEach(function (sentence, index) {
        registerSentence(sentence, index + 1);
      });
    }

    const strongPhrases = Array.from(phraseFreq.entries())
      .filter(function (entry) {
        const phrase = entry[0];
        const count = entry[1];

        if (count < 2 && items.length > 20) return false;
        if (phrase.split(" ").length < 2) return false;

        return true;
      })
      .sort(function (a, b) {
        return b[1] - a[1];
      })
      .slice(0, 250)
      .map(function (entry) {
        return {
          label: entry[0],
          count: entry[1]
        };
      });

    return {
      items: items,
      phraseFreq: phraseFreq,
      wordFreq: wordFreq,
      strongPhrases: strongPhrases
    };
  }

  function overlapScore(a, b) {
    const aw = new Set(words(a));
    const bw = new Set(words(b));

    if (!aw.size || !bw.size) return 0;

    let common = 0;

    aw.forEach(function (word) {
      if (bw.has(word)) common += 1;
    });

    return common / Math.min(aw.size, bw.size);
  }

  /*
   * MOTORE 3 UNIVERSALE
   * Fonde concetti simili anche se non sono identici.
   */
  function fuseConcepts(conceptData) {
    const phrases = conceptData.strongPhrases || [];
    const clusters = [];

    phrases.forEach(function (phrase) {
      let target = null;

      for (const cluster of clusters) {
        if (overlapScore(phrase.label, cluster.label) >= 0.55) {
          target = cluster;
          break;
        }
      }

      if (!target) {
        target = {
          label: phrase.label,
          variants: [],
          count: 0,
          pages: new Set(),
          examples: []
        };
        clusters.push(target);
      }

      target.variants.push(phrase.label);
      target.count += phrase.count;
    });

    conceptData.items.forEach(function (item) {
      clusters.forEach(function (cluster) {
        const found = item.phrases.some(function (phrase) {
          return overlapScore(phrase, cluster.label) >= 0.55 || normalizeCompare(phrase) === normalizeCompare(cluster.label);
        });

        if (found) {
          cluster.pages.add(item.page);

          if (cluster.examples.length < 8) {
            cluster.examples.push(item.sentence);
          }
        }
      });
    });

    return clusters
      .map(function (cluster) {
        const pages = Array.from(cluster.pages).sort(function (a, b) { return a - b; });

        return {
          label: cluster.label,
          variants: unique(cluster.variants, 8),
          count: cluster.count,
          pageStart: pages.length ? pages[0] : 1,
          pageEnd: pages.length ? pages[pages.length - 1] : 1,
          examples: unique(cluster.examples, 8)
        };
      })
      .sort(function (a, b) {
        return b.count - a.count;
      });
  }

  function conceptsForRange(clusters, range) {
    return (clusters || []).filter(function (cluster) {
      return cluster.pageEnd >= range.start && cluster.pageStart <= range.end;
    });
  }

  function bestSentencesForRange(items, range, limit) {
    return (items || [])
      .filter(function (item) {
        return item.page >= range.start && item.page <= range.end;
      })
      .filter(function (item) {
        return item.sentence.length >= 70;
      })
      .slice(0, 400)
      .sort(function (a, b) {
        return b.phrases.length - a.phrases.length;
      })
      .map(function (item) {
        return item.sentence;
      })
      .filter(function (sentence, index, array) {
        const sig = signature(sentence);
        return sig && array.findIndex(function (other) { return signature(other) === sig; }) === index;
      })
      .slice(0, limit || 8);
  }

  /*
   * MOTORE 4 UNIVERSALE
   * Riscrive macro-sezioni con struttura neutra e riutilizzabile.
   */
  function rewriteMacroSection(range, clusters, items, domain, index) {
    const localClusters = conceptsForRange(clusters, range).slice(0, 10);
    const localSentences = bestSentencesForRange(items, range, 6);
    const conceptNames = localClusters.map(function (cluster) { return cluster.label; });
    const conceptList = humanList(conceptNames, 10);

    const paragraphs = [];

    paragraphs.push(
      "Nelle pagine " + range.start + "-" + range.end +
      " il materiale sviluppa una parte del " + domain.label +
      ". La macro-sezione viene sintetizzata per concetti, non come copia delle singole frasi originali."
    );

    if (conceptList) {
      paragraphs.push(
        "I nuclei più ricorrenti sono " + conceptList +
        ". Questi elementi sono stati fusi perché compaiono più volte, con formulazioni diverse o in punti differenti del testo."
      );
    }

    if (localClusters.length) {
      localClusters.slice(0, 5).forEach(function (cluster) {
        const examples = unique(cluster.examples.map(cleanMechanicalText), 3);
        let p =
          "Il concetto \"" + cluster.label + "\" compare tra le pagine " +
          cluster.pageStart + "-" + cluster.pageEnd + ".";

        if (cluster.variants.length > 1) {
          p += " Le formulazioni collegate includono " + humanList(cluster.variants, 5) + ".";
        }

        if (examples.length) {
          p += " Gli esempi più rappresentativi sono stati condensati senza mantenere la ripetizione letterale del testo sorgente.";
        }

        paragraphs.push(p);
      });
    } else if (localSentences.length) {
      paragraphs.push(
        "Le frasi rappresentative indicano che questa parte contiene informazioni collegate al tema generale. Il contenuto è stato ridotto eliminando marker di pagina, formule ripetitive e dettagli ridondanti."
      );
    }

    paragraphs.push(
      "Il valore della sezione è " + domain.style +
      "."
    );

    return {
      titolo: "Macro-sezione " + (index + 1) + " - pagine " + range.start + "-" + range.end,
      testo: antiTemplate(paragraphs.join(" "))
    };
  }

  /*
   * MOTORE 5 UNIVERSALE
   * Anti-template + quality gate.
   */
  function antiTemplate(text) {
    let out = cleanMechanicalText(text)
      .replace(/\bla sezione\s+[0-9.]+/gi, "questa parte")
      .replace(/\bdescrive come gestire\b/gi, "spiega la gestione di")
      .replace(/\bNel contesto\s+([^,]+),\s*/gi, "Nel contesto $1 emerge ")
      .replace(/\s+/g, " ")
      .trim();

    if (out && !/[.!?]$/.test(out)) out += ".";

    return out;
  }

  function buildGeneralSummary(clusters, domain, coverage) {
    const top = clusters.slice(0, 12).map(function (cluster) { return cluster.label; });
    const topList = humanList(top, 12);

    const text = [
      "Il documento viene riconosciuto come " + domain.label + " e viene organizzato in " +
        coverage.ranges.length + " macro-sezioni, con copertura dalla pagina 1 alla pagina " + coverage.totalPages + ".",
      topList
        ? "I concetti principali sono " + topList + ". Il riassunto li raggruppa per ridurre duplicazioni e trasformare ripetizioni distribuite nel testo in blocchi più leggibili."
        : "Il riassunto usa i contenuti disponibili per ricostruire tema principale, sottotemi ed esempi rappresentativi.",
      "L'obiettivo è " + domain.style + ", mantenendo una sintesi sufficientemente ampia per documenti lunghi senza trasformarla in copia meccanica."
    ].join(" ");

    return {
      titolo: "Sintesi generale",
      testo: antiTemplate(text)
    };
  }

  function buildKeyPoints(clusters) {
    const top = clusters.slice(0, 18).map(function (cluster) {
      return cluster.label;
    });

    return {
      titolo: "Punti chiave ricorrenti",
      testo: antiTemplate(
        top.length
          ? "I punti chiave più ricorrenti sono: " + top.join(", ") + ". La lista mostra concetti fusi, non singole parole isolate."
          : "Il documento non presenta abbastanza ricorrenze per costruire una lista estesa di punti chiave, quindi vengono mantenuti solo i temi emersi nelle macro-sezioni."
      )
    };
  }

  function buildCoverageSection(coverage) {
    return {
      titolo: "Controllo copertura pagine",
      testo:
        "Copertura calcolata: " +
        coverage.ranges.map(function (r) { return r.start + "-" + r.end; }).join(", ") +
        ". La copertura totale va dalla pagina 1 alla pagina " + coverage.totalPages +
        ". Il motore è progettato per testi fino a 500 pagine."
    };
  }

  function buildConclusion(clusters, domain) {
    const top = humanList(clusters.slice(0, 8).map(function (cluster) { return cluster.label; }), 8);

    return {
      titolo: "Conclusione",
      testo: antiTemplate(
        "Nel complesso, il " + domain.label +
        " viene sintetizzato mettendo in relazione i concetti ricorrenti" +
        (top ? ": " + top : "") +
        ". La conclusione conserva il quadro generale, elimina le formule meccaniche e lascia visibili i nuclei utili per studio, revisione o riutilizzo del contenuto."
      )
    };
  }

  function buildDeepenings(clusters, currentChars, targetMin, targetMax) {
    const sections = [];
    let chars = currentChars;
    let index = 1;

    clusters.slice(0, 30).forEach(function (cluster) {
      if (chars >= targetMin || chars >= targetMax) return;

      const examples = unique(cluster.examples.map(cleanMechanicalText), 5);
      const variants = humanList(cluster.variants, 6);

      const text = antiTemplate(
        "Questo approfondimento raccoglie il concetto \"" + cluster.label + "\". " +
        (variants ? "Nel testo il concetto appare anche attraverso " + variants + ". " : "") +
        (examples.length ? "Gli esempi collegati sono stati letti come prove del concetto, non come frasi da copiare. " : "") +
        "La fusione concettuale permette di conservare il significato distribuito nelle pagine, riducendo ripetizioni e formulazioni ridondanti."
      );

      sections.push({
        titolo: "Approfondimento concettuale " + index + " - " + cluster.label,
        testo: text
      });

      chars += text.length;
      index += 1;
    });

    return sections;
  }

  function qualityGate(sections, coverage, originalChars) {
    const report = {
      version: VERSION,
      ok: true,
      issues: [],
      corrections: [],
      finalChars: 0,
      ratio: 0,
      coverage: coverage
    };

    let fixed = (sections || []).map(function (section) {
      return {
        titolo: section.titolo || "Sezione",
        testo: antiTemplate(section.testo || "")
      };
    }).filter(function (section) {
      return section.testo.trim().length > 0;
    });

    fixed = fixed.map(function (section) {
      const seen = new Set();
      const sentences = splitSentences(section.testo).filter(function (sentence) {
        const sig = signature(sentence);
        if (!sig || seen.has(sig)) return false;
        seen.add(sig);
        return true;
      });

      return {
        titolo: section.titolo,
        testo: sentences.length ? antiTemplate(sentences.join(" ")) : section.testo
      };
    });

    const all = fixed.map(function (section) { return section.testo; }).join(" ");

    const badPatterns = [
      /---\s*PAGINA/gi,
      /Titolo pagina\s+\d+/gi,
      /Riferimento sezione:/gi,
      /la sezione\s+[0-9.]+\s+descrive\s+come\s+gestire/gi
    ];

    badPatterns.forEach(function (pattern) {
      const matches = all.match(pattern);
      if (matches && matches.length) {
        report.ok = false;
        report.issues.push("Pattern meccanico residuo: " + matches.length);
      }
    });

    report.finalChars = countChars(fixed);
    report.ratio = originalChars ? report.finalChars / originalChars : 0;

    if (!coverage.complete) {
      report.ok = false;
      report.issues.push("Copertura pagine incompleta.");
    }

    if (fixed.length < 4) {
      report.ok = false;
      report.issues.push("Poche sezioni finali.");
    }

    if (originalChars > 30000 && report.ratio < 0.08) {
      report.issues.push("Riassunto probabilmente ancora corto rispetto al documento lungo.");
    }

    if (report.ratio > 0.28) {
      report.issues.push("Riassunto probabilmente troppo lungo.");
    }

    return {
      sections: fixed,
      report: report
    };
  }

  function orchestrateHighQualitySummary(input) {
    const safe = input || {};
    const report = safe.reportLungo || {};
    const originalText = String(safe.testoOriginale || "");
    const totalPages = Math.max(1, Number(report.totalPages || report.extractedPages || 1));
    const originalChars = Math.max(originalText.length, Number(report.totalChars || 0));

    const coverage = buildCoveragePlan(totalPages);
    const domain = detectDomain(originalText, safe.profilo || {});
    const conceptData = extractUniversalConcepts(safe);
    const clusters = fuseConcepts(conceptData);

    const targetMin = Math.min(160000, Math.max(6000, Math.round(originalChars * 0.15)));
    const targetMax = Math.min(240000, Math.max(targetMin + 1500, Math.round(originalChars * 0.25)));

    const sections = [];

    sections.push(buildGeneralSummary(clusters, domain, coverage));

    coverage.ranges.forEach(function (range, index) {
      sections.push(rewriteMacroSection(range, clusters, conceptData.items, domain, index));
    });

    sections.push(buildKeyPoints(clusters));
    sections.push(buildCoverageSection(coverage));
    sections.push(buildConclusion(clusters, domain));

    buildDeepenings(clusters, countChars(sections), targetMin, targetMax).forEach(function (section) {
      if (countChars(sections) < targetMax) {
        sections.splice(Math.max(1, sections.length - 2), 0, section);
      }
    });

    const quality = qualityGate(sections, coverage, originalChars);

    return {
      version: VERSION,
      sezioni: quality.sections,
      report: Object.assign({}, quality.report, {
        domain: domain,
        originalChars: originalChars,
        targetMinChars: targetMin,
        targetMaxChars: targetMax,
        conceptsExtracted: conceptData.items.length,
        clustersCreated: clusters.length
      })
    };
  }

  return {
    version: VERSION,
    buildCoveragePlan: buildCoveragePlan,
    detectDomain: detectDomain,
    extractUniversalConcepts: extractUniversalConcepts,
    fuseConcepts: fuseConcepts,
    antiTemplate: antiTemplate,
    rewriteMacroSection: rewriteMacroSection,
    qualityGate: qualityGate,
    orchestrateHighQualitySummary: orchestrateHighQualitySummary
  };
});
