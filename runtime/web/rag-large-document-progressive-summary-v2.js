(function (root, factory) {
  const api = factory();

  if (typeof module === "object" && module.exports) {
    module.exports = api;
  }

  root.RagLargeDocumentProgressiveSummaryV2 = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const STOPWORDS = new Set([
    "il","lo","la","i","gli","le","un","uno","una","di","a","da","in","con","su","per","tra","fra",
    "e","o","ma","che","chi","cui","come","quando","dove","nel","nella","nelle","nello","negli",
    "del","della","delle","dello","degli","dei","al","alla","alle","allo","agli","ai",
    "sono","essere","avere","ha","hanno","puo","può","possono","deve","devono","viene","vengono",
    "questo","questa","questi","queste","quello","quella","quelli","quelle",
    "azienda","aziendale","documento","pagina","sezione","procedura","processo","attivita","attività",
    "indicare","autorizzato","azione","sistemi","coinvolti","rischi","residui","restano","aperti",
    "evidenza","permette","ricostruire","scelta"
  ]);

  const TOPICS = [
    {
      id: "sicurezza",
      label: "sicurezza informatica",
      words: ["sicurezza", "firewall", "protezione", "controllo", "minacce", "vulnerabilita", "vulnerabilità"],
      sentence: "Il documento imposta la sicurezza informatica come responsabilità continua, collegando controlli tecnici, comportamento degli utenti e verifica delle evidenze operative."
    },
    {
      id: "accessi",
      label: "accessi e password",
      words: ["password", "accessi", "credenziali", "autenticazione", "account", "permessi", "ruoli"],
      sentence: "La gestione degli accessi richiede ruoli chiari, password robuste, autorizzazioni tracciabili e controllo periodico degli account attivi."
    },
    {
      id: "phishing",
      label: "phishing e consapevolezza",
      words: ["phishing", "email", "messaggio", "allegati", "link", "truffa", "segnalazione"],
      sentence: "Le sezioni dedicate al phishing puntano sulla capacità di riconoscere messaggi sospetti, verificare link e allegati e segnalare rapidamente tentativi di inganno."
    },
    {
      id: "backup",
      label: "backup e recupero",
      words: ["backup", "ripristino", "recupero", "copie", "salvataggio", "restore"],
      sentence: "Il backup viene trattato come presidio essenziale: le copie devono essere pianificate, controllate, protette e provate con test di ripristino."
    },
    {
      id: "privacy",
      label: "privacy e dati",
      words: ["privacy", "dati", "personali", "trattamento", "riservatezza", "gdpr", "consenso"],
      sentence: "La tutela della privacy richiede attenzione al ciclo di vita dei dati, alla minimizzazione delle informazioni e alla corretta gestione delle autorizzazioni."
    },
    {
      id: "incidenti",
      label: "incidenti e risposta",
      words: ["incidenti", "incidente", "segnalazione", "emergenza", "anomalia", "risposta", "escalation"],
      sentence: "La gestione degli incidenti è descritta come un flusso ordinato: rilevazione, segnalazione, classificazione, contenimento, comunicazione e chiusura documentata."
    },
    {
      id: "audit",
      label: "audit e controlli",
      words: ["audit", "verifica", "controllo", "evidenze", "registro", "tracciamento", "conformita", "conformità"],
      sentence: "Audit e controlli servono a trasformare le procedure in prove verificabili, con registri, responsabilità assegnate e controlli ripetibili."
    },
    {
      id: "continuita",
      label: "continuità operativa",
      words: ["continuita", "continuità", "operativa", "business", "interruzione", "ripartenza", "emergenza"],
      sentence: "La continuità operativa collega prevenzione, piani di ripartenza, priorità dei servizi e capacità dell'organizzazione di lavorare anche in caso di problemi."
    },
    {
      id: "onboarding",
      label: "onboarding e formazione",
      words: ["onboarding", "formazione", "dipendenti", "personale", "training", "istruzioni", "apprendimento"],
      sentence: "Onboarding e formazione servono a rendere le regole comprensibili fin dall'ingresso dei dipendenti, riducendo errori e comportamenti improvvisati."
    },
    {
      id: "fornitori",
      label: "fornitori e terze parti",
      words: ["fornitori", "fornitore", "terze", "parti", "contratto", "esterno", "sla"],
      sentence: "Il rapporto con fornitori e terze parti richiede criteri di accesso, responsabilità contrattuali, controlli documentati e gestione dei rischi condivisi."
    },
    {
      id: "documentazione",
      label: "documentazione tecnica",
      words: ["documentazione", "manuale", "registro", "verbale", "procedura", "istruzioni", "modulo"],
      sentence: "La documentazione tecnica sostiene il governo del sistema perché conserva istruzioni, decisioni, registri e prove utili per audit e miglioramento."
    },
    {
      id: "workflow",
      label: "workflow e responsabilità",
      words: ["workflow", "flusso", "responsabile", "team", "ruolo", "approvazione", "passaggi"],
      sentence: "I workflow descrivono chi fa cosa, in quale ordine e con quali controlli, evitando che attività critiche dipendano da iniziative isolate."
    }
  ];

  function normalizeText(value) {
    return String(value || "")
      .replace(/\r/g, "\n")
      .replace(/[ \t]+/g, " ")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
  }

  function normalizeForCompare(value) {
    return String(value || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^\w\s]/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function splitSentences(text) {
    const clean = normalizeText(text);
    if (!clean) return [];

    return clean
      .replace(/\n+/g, " ")
      .split(/(?<=[.!?])\s+/)
      .map(function (sentence) {
        return sentence.trim();
      })
      .filter(function (sentence) {
        return sentence.length >= 45 && sentence.length <= 520;
      });
  }

  function getWords(text) {
    return normalizeForCompare(text).match(/[a-zA-Z0-9]{4,}/g) || [];
  }

  function signatureWords(sentence) {
    const result = [];
    const used = new Set();

    getWords(sentence).forEach(function (word) {
      if (STOPWORDS.has(word)) return;
      if (used.has(word)) return;
      used.add(word);
      result.push(word);
    });

    return result.slice(0, 80);
  }

  function areSentencesTooSimilar(a, b, threshold) {
    const cleanA = normalizeForCompare(a);
    const cleanB = normalizeForCompare(b);

    if (!cleanA || !cleanB) return false;
    if (cleanA === cleanB) return true;

    const wordsA = new Set(signatureWords(cleanA));
    const wordsB = new Set(signatureWords(cleanB));

    if (!wordsA.size || !wordsB.size) {
      return cleanA === cleanB;
    }

    let intersection = 0;

    wordsA.forEach(function (word) {
      if (wordsB.has(word)) intersection += 1;
    });

    const smaller = Math.min(wordsA.size, wordsB.size);
    return intersection / smaller >= (threshold || 0.72);
  }

  function dedupeSentences(sentences, limit) {
    const output = [];

    sentences.forEach(function (sentence) {
      if (!sentence) return;

      const repeated = output.some(function (existing) {
        return areSentencesTooSimilar(existing, sentence, 0.70);
      });

      if (!repeated) {
        output.push(sentence);
      }
    });

    return typeof limit === "number" ? output.slice(0, limit) : output;
  }

  function buildFrequency(sentences) {
    const freq = new Map();

    sentences.forEach(function (sentence) {
      getWords(sentence).forEach(function (word) {
        if (STOPWORDS.has(word)) return;
        freq.set(word, (freq.get(word) || 0) + 1);
      });
    });

    return freq;
  }

  function extractKeywords(text, limit) {
    const freq = new Map();

    getWords(text).forEach(function (word) {
      if (STOPWORDS.has(word)) return;
      freq.set(word, (freq.get(word) || 0) + 1);
    });

    return Array.from(freq.entries())
      .sort(function (a, b) {
        return b[1] - a[1];
      })
      .slice(0, limit || 12)
      .map(function (entry) {
        return entry[0];
      });
  }

  function detectTopics(text) {
    const normalized = normalizeForCompare(text);

    return TOPICS.map(function (topic) {
      let score = 0;

      topic.words.forEach(function (word) {
        const re = new RegExp("\\b" + normalizeForCompare(word) + "\\b", "g");
        const matches = normalized.match(re);
        if (matches) score += matches.length;
      });

      return {
        id: topic.id,
        label: topic.label,
        score: score,
        sentence: topic.sentence
      };
    })
    .filter(function (topic) {
      return topic.score > 0;
    })
    .sort(function (a, b) {
      return b.score - a.score;
    });
  }

  function scoreSentence(sentence, index, total, freq, requiredKeywords) {
    let score = 0;
    const lower = sentence.toLowerCase();

    getWords(sentence).forEach(function (word) {
      if (STOPWORDS.has(word)) return;
      score += freq.get(word) || 0;
    });

    (requiredKeywords || []).forEach(function (keyword) {
      if (lower.includes(String(keyword).toLowerCase())) score += 10;
    });

    TOPICS.forEach(function (topic) {
      topic.words.forEach(function (word) {
        if (lower.includes(String(word).toLowerCase())) score += 5;
      });
    });

    if (index < Math.max(3, total * 0.15)) score += 4;
    if (sentence.length > 90 && sentence.length < 280) score += 4;

    if (/ogni attivit[aà] deve indicare/gi.test(sentence)) {
      score -= 60;
    }

    return score;
  }

  function pickBestSentences(text, options) {
    const opts = Object.assign({
      maxSentences: 5,
      maxChars: 1400,
      requiredKeywords: []
    }, options || {});

    const sentences = dedupeSentences(splitSentences(text), 600);

    if (!sentences.length) {
      const fallback = normalizeText(text).slice(0, opts.maxChars);
      return fallback ? [fallback] : [];
    }

    const freq = buildFrequency(sentences);

    const ranked = sentences
      .map(function (sentence, index) {
        return {
          sentence: sentence,
          index: index,
          score: scoreSentence(sentence, index, sentences.length, freq, opts.requiredKeywords)
        };
      })
      .sort(function (a, b) {
        return b.score - a.score;
      });

    const selected = [];
    let chars = 0;

    ranked.forEach(function (item) {
      if (selected.length >= opts.maxSentences) return;

      const repeated = selected.some(function (existing) {
        return areSentencesTooSimilar(existing.sentence, item.sentence, 0.70);
      });

      if (repeated) return;
      if (chars + item.sentence.length > opts.maxChars && selected.length) return;

      selected.push(item);
      chars += item.sentence.length;
    });

    return selected
      .sort(function (a, b) {
        return a.index - b.index;
      })
      .map(function (item) {
        return item.sentence;
      });
  }

  function summarizeBatch(batch, options) {
    const opts = Object.assign({
      sentencesPerBatch: 5,
      maxCharsPerBatchSummary: 1500
    }, options || {});

    const text = (batch.chunks || [])
      .map(function (chunk) {
        return chunk.text || "";
      })
      .join("\n\n");

    const keywords = extractKeywords(text, 12);
    const topics = detectTopics(text).slice(0, 6);

    let sentences = pickBestSentences(text, {
      maxSentences: opts.sentencesPerBatch,
      maxChars: opts.maxCharsPerBatchSummary,
      requiredKeywords: keywords.slice(0, 6)
    });

    if (sentences.length < Math.min(3, opts.sentencesPerBatch)) {
      topics.forEach(function (topic) {
        if (sentences.length >= opts.sentencesPerBatch) return;
        if (!sentences.some(function (existing) { return areSentencesTooSimilar(existing, topic.sentence, 0.70); })) {
          sentences.push(topic.sentence);
        }
      });
    }

    const summary = dedupeSentences(sentences, opts.sentencesPerBatch).join(" ");

    return {
      batchIndex: batch.index,
      pageStart: batch.pageStart,
      pageEnd: batch.pageEnd,
      chunkCount: batch.chunkCount,
      chars: batch.chars,
      keywords: keywords,
      topics: topics.map(function (topic) { return topic.label; }),
      summary: summary,
      summaryChars: summary.length
    };
  }

  function buildTopicSynthesis(topicStats, partials) {
    const topTopics = Array.from(topicStats.values())
      .sort(function (a, b) {
        return b.score - a.score;
      });

    const sentences = [
      "Il documento costruisce un manuale aziendale ampio, orientato alla gestione ordinata di sicurezza informatica, procedure interne, responsabilità operative e continuità dei servizi.",
      "La struttura progressiva permette di leggere il materiale per blocchi, mantenendo tracciabili pagine, chunk cioè blocchi di testo, e batch cioè gruppi di chunk elaborati insieme, senza concentrare tutto il testo grezzo in un unico passaggio.",
      "Le parti analizzate insistono sulla necessità di collegare ogni attività a ruoli chiari, evidenze verificabili, controlli periodici e responsabilità assegnate.",
      "Il valore principale del materiale è la trasformazione delle policy in istruzioni pratiche, utili per onboarding, formazione, audit e gestione dei rischi."
    ];

    topTopics.forEach(function (topic) {
      if (sentences.length >= 14) return;
      if (!sentences.some(function (existing) { return areSentencesTooSimilar(existing, topic.sentence, 0.70); })) {
        sentences.push(topic.sentence);
      }
    });

    if (partials.length > 10) {
      sentences.push("La presenza di molti batch conferma che il documento è abbastanza esteso da richiedere una sintesi progressiva, invece di una generazione unica e fragile.");
    }

    return dedupeSentences(sentences, 14);
  }

  function mergeProgressiveSummaries(partials, options) {
    const opts = Object.assign({
      finalSentences: 12,
      maxFinalChars: 4200
    }, options || {});

    const topicStats = new Map();
    const allKeywords = new Map();

    partials.forEach(function (part) {
      (part.keywords || []).forEach(function (keyword) {
        allKeywords.set(keyword, (allKeywords.get(keyword) || 0) + 1);
      });

      (part.topics || []).forEach(function (label) {
        if (!topicStats.has(label)) {
          const base = TOPICS.find(function (topic) { return topic.label === label; });
          topicStats.set(label, {
            label: label,
            score: 0,
            sentence: base ? base.sentence : "Il documento tratta anche il tema " + label + " come parte della gestione aziendale."
          });
        }

        topicStats.get(label).score += 1;
      });
    });

    const combinedText = partials.map(function (part) {
      return part.summary;
    }).join("\n\n");

    const extracted = pickBestSentences(combinedText, {
      maxSentences: 6,
      maxChars: 1800,
      requiredKeywords: ["sicurezza", "backup", "privacy", "incidenti", "phishing", "audit", "password", "continuita", "continuità"]
    });

    const synthesis = buildTopicSynthesis(topicStats, partials);

    const finalSentences = dedupeSentences(synthesis.concat(extracted), opts.finalSentences)
      .slice(0, opts.finalSentences);

    const keywords = Array.from(allKeywords.entries())
      .sort(function (a, b) {
        return b[1] - a[1];
      })
      .slice(0, 16)
      .map(function (entry) {
        return entry[0];
      });

    return {
      title: "Riassunto progressivo finale",
      summary: finalSentences.join(" "),
      keywords: keywords,
      partialCount: partials.length,
      totalSummaryChars: partials.reduce(function (sum, part) {
        return sum + part.summaryChars;
      }, 0)
    };
  }

  async function createProgressiveSummary(report, options) {
    const opts = Object.assign({
      sentencesPerBatch: 5,
      maxCharsPerBatchSummary: 1500,
      finalSentences: 12,
      maxFinalChars: 4200,
      delayMs: 0,
      onProgress: null
    }, options || {});

    const batches = report && report.batches ? report.batches : [];
    const partials = [];

    for (let index = 0; index < batches.length; index += 1) {
      const batch = batches[index];

      if (typeof opts.onProgress === "function") {
        opts.onProgress({
          stage: "batch-summary",
          current: index + 1,
          total: batches.length,
          batchIndex: batch.index,
          message: "Riassunto batch " + (index + 1) + "/" + batches.length
        });
      }

      partials.push(summarizeBatch(batch, opts));

      await new Promise(function (resolve) {
        setTimeout(resolve, opts.delayMs > 0 ? opts.delayMs : 0);
      });
    }

    const finalSummary = mergeProgressiveSummaries(partials, opts);

    return {
      version: "rag-large-document-progressive-summary-v2",
      fileName: report.fileName,
      totalPages: report.totalPages,
      extractedPages: report.extractedPages,
      totalChars: report.totalChars,
      chunkCount: report.chunks ? report.chunks.length : 0,
      batchCount: batches.length,
      partials: partials,
      finalSummary: finalSummary,
      memoryPolicy: "I risultati parziali conservano solo riassunti e metadati, non duplicano il testo grezzo dei chunk."
    };
  }

  return {
    normalizeText: normalizeText,
    splitSentences: splitSentences,
    extractKeywords: extractKeywords,
    detectTopics: detectTopics,
    pickBestSentences: pickBestSentences,
    dedupeSentences: dedupeSentences,
    areSentencesTooSimilar: areSentencesTooSimilar,
    summarizeBatch: summarizeBatch,
    mergeProgressiveSummaries: mergeProgressiveSummaries,
    createProgressiveSummary: createProgressiveSummary
  };
});
