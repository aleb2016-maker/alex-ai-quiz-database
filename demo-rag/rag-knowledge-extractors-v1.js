(function () {
  "use strict";

  const VERSION = "rag-knowledge-extractors-v1";

  const STOPWORDS = new Set([
    "alla", "allo", "alle", "agli", "dalla", "dallo", "delle", "degli", "della", "dell", "nella", "nello", "nelle", "negli",
    "che", "con", "come", "per", "tra", "fra", "sono", "essere", "viene", "vengono", "questo", "questa", "questi", "quelle", "quelli",
    "anche", "deve", "devono", "può", "possono", "più", "meno", "molto", "ogni", "suo", "sua", "suoi", "loro", "del", "dei", "una", "uno", "gli", "non", "nel", "sul", "sui", "dal", "dai", "hai", "abbiamo", "hanno", "fare", "usare", "usati",
    "documento", "testo", "pagina", "sezione", "argomento"
  ]);

  const CATEGORY_RULES = [
    { id: "sicurezza", label: "Sicurezza", terms: ["sicurezza", "protezione", "rischio", "accesso", "password", "credenziali", "malware", "phishing", "backup", "firewall"] },
    { id: "formazione", label: "Formazione", terms: ["formazione", "corso", "lezione", "studio", "apprendimento", "verifica", "esame", "competenza"] },
    { id: "lavoro", label: "Lavoro", terms: ["azienda", "lavoro", "cliente", "processo", "reparto", "responsabile", "procedura", "attività"] },
    { id: "sport", label: "Sport e allenamento", terms: ["allenamento", "esercizio", "serie", "ripetizioni", "recupero", "forza", "corsa", "mobilità", "carico"] },
    { id: "curriculum", label: "Curriculum", terms: ["curriculum", "esperienza", "profilo", "competenze", "istruzione", "candidato", "ruolo", "progetto"] },
    { id: "storia", label: "Storia o racconto", terms: ["racconto", "personaggio", "storia", "scena", "capitolo", "narrazione", "dialogo"] },
    { id: "poesia", label: "Poesia", terms: ["poesia", "verso", "strofa", "rima", "metafora", "immagine", "ritmo"] },
    { id: "generico", label: "Generico", terms: [] }
  ];

  const RELATION_PATTERNS = [
    { type: "causa", patterns: [/\bperch[eé]\b/i, /\ba causa di\b/i, /\bpoich[eé]\b/i, /\bquindi\b/i, /\bdi conseguenza\b/i] },
    { type: "richiede", patterns: [/\brichiede\b/i, /\bdeve\b/i, /\bdevono\b/i, /\bnecessita\b/i, /\bserve\b/i] },
    { type: "evita", patterns: [/\bevitar[ea]\b/i, /\bpreviene\b/i, /\bripara da\b/i, /\brimuove\b/i, /\brallenta\b/i] },
    { type: "protegge", patterns: [/\bprotegge\b/i, /\bproteggere\b/i, /\bdifende\b/i, /\bsalvaguarda\b/i] },
    { type: "appartiene_a", patterns: [/\bfa parte di\b/i, /\bappartiene a\b/i, /\binclude\b/i, /\bcomprende\b/i, /\bcontiene\b/i] },
    { type: "prima_dopo", patterns: [/\bprima\b/i, /\bdopo\b/i, /\bsuccessivamente\b/i, /\bin seguito\b/i] },
    { type: "problema_soluzione", patterns: [/\bproblema\b/i, /\bsoluzione\b/i, /\brisolvere\b/i, /\bcontrollo\b/i, /\bcorrezione\b/i] }
  ];

  function textOf(documentInputOrText) {
    if (typeof documentInputOrText === "string") return documentInputOrText;
    if (documentInputOrText && documentInputOrText.text) return documentInputOrText.text.clean || documentInputOrText.text.original || "";
    return "";
  }

  function normalize(text) {
    return String(text || "").replace(/\u00A0/g, " ").replace(/[ \t]+/g, " ").trim();
  }

  function splitParagraphs(text) {
    return String(text || "")
      .split(/\n{2,}/)
      .map(normalize)
      .filter((paragraph) => paragraph.length > 0);
  }

  function splitSentences(text) {
    const protectedText = String(text || "").replace(/\b(es|dr|sig|prof)\./gi, (match) => match.replace(".", "§"));
    return protectedText
      .split(/(?<=[.!?])\s+|\n+/)
      .map((sentence) => normalize(sentence.replace(/§/g, ".")))
      .filter((sentence) => sentence.length >= 20);
  }

  function words(text) {
    return normalize(text)
      .toLowerCase()
      .replace(/[^a-zà-öø-ÿ0-9\s-]/gi, " ")
      .split(/\s+/)
      .filter((word) => word.length >= 3 && !STOPWORDS.has(word));
  }

  function frequencyMap(items) {
    const map = new Map();
    items.forEach((item) => map.set(item, (map.get(item) || 0) + 1));
    return map;
  }

  function topKeywords(text, limit) {
    const freq = frequencyMap(words(text));
    return Array.from(freq.entries())
      .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
      .slice(0, limit || 20)
      .map(([term, count]) => ({ term, count }));
  }

  function titleCasePhrase(phrase) {
    const clean = normalize(phrase).toLowerCase();
    return clean.charAt(0).toUpperCase() + clean.slice(1);
  }

  function extractCandidatePhrases(text) {
    const candidates = [];
    const sentenceList = splitSentences(text);

    sentenceList.forEach((sentence) => {
      const chunks = sentence
        .split(/[,;:.()\[\]{}]/)
        .map(normalize)
        .filter((chunk) => chunk.length >= 8 && chunk.length <= 90);

      chunks.forEach((chunk) => {
        const chunkWords = words(chunk);
        if (chunkWords.length >= 2 && chunkWords.length <= 7) {
          candidates.push(chunkWords.join(" "));
        }
      });

      const phraseMatches = sentence.match(/\b([A-Za-zÀ-ÖØ-öø-ÿ0-9]+(?:\s+(?:di|dei|delle|del|della|e|o|per|con|senza|su|in|a|da)?\s*[A-Za-zÀ-ÖØ-öø-ÿ0-9]+){1,5})\b/g) || [];
      phraseMatches.forEach((phrase) => {
        const cleanWords = words(phrase);
        if (cleanWords.length >= 2 && cleanWords.length <= 6) {
          candidates.push(cleanWords.join(" "));
        }
      });
    });

    return candidates;
  }

  function categoryForText(text) {
    const lower = normalize(text).toLowerCase();
    const scored = CATEGORY_RULES.map((rule) => {
      const score = rule.terms.reduce((sum, term) => sum + (lower.includes(term) ? 1 : 0), 0);
      return { id: rule.id, label: rule.label, score };
    }).sort((a, b) => b.score - a.score);

    return scored[0] && scored[0].score > 0 ? scored[0] : { id: "generico", label: "Generico", score: 0 };
  }

  function sentenceContains(sentence, term) {
    return normalize(sentence).toLowerCase().includes(normalize(term).toLowerCase());
  }

  function evidenceForTerm(sentences, term) {
    return sentences.find((sentence) => sentenceContains(sentence, term)) || "";
  }

  function confidenceFromEvidence(term, count, evidence) {
    let score = 0.45;
    if (count >= 2) score += 0.15;
    if (count >= 4) score += 0.15;
    if (evidence.length >= 60) score += 0.1;
    if (term.split(/\s+/).length >= 2) score += 0.1;
    return Math.max(0.1, Math.min(0.95, Number(score.toFixed(2))));
  }

  function extractDefinitions(sentences) {
    const definitions = [];
    const patterns = [
      /^(.{3,70}?)\s+(?:è|sono)\s+(.{8,180})$/i,
      /^(.{3,70}?)\s+(?:comprende|include|indica|rappresenta)\s+(.{8,180})$/i,
      /(?:si intende per|viene definito come)\s+(.{3,70}?)\s+(.{8,180})/i
    ];

    sentences.forEach((sentence) => {
      patterns.forEach((pattern) => {
        const match = sentence.match(pattern);
        if (!match) return;
        const term = normalize(match[1]);
        const description = normalize(match[2]);
        if (term.length >= 3 && description.length >= 8) {
          definitions.push({ term: titleCasePhrase(term), description, evidence: sentence, confidence: 0.82 });
        }
      });
    });

    return definitions;
  }

  function extractExamples(sentences) {
    return sentences
      .filter((sentence) => /\bad esempio\b|\besempio\b|\bcome\b|\btipo\b/i.test(sentence))
      .slice(0, 12)
      .map((sentence) => ({ text: sentence, confidence: 0.7 }));
  }

  function extractConcepts(documentInputOrText, options) {
    const settings = Object.assign({ limit: 18 }, options || {});
    const text = textOf(documentInputOrText);
    const sentences = splitSentences(text);
    const phraseFreq = frequencyMap(extractCandidatePhrases(text));
    const keywordList = topKeywords(text, 30);

    const phraseConcepts = Array.from(phraseFreq.entries())
      .filter(([phrase]) => phrase.length >= 6)
      .sort((a, b) => b[1] - a[1] || b[0].length - a[0].length)
      .slice(0, settings.limit)
      .map(([phrase, count], index) => {
        const evidence = evidenceForTerm(sentences, phrase) || evidenceForTerm(sentences, phrase.split(" ")[0]);
        const category = categoryForText(`${phrase} ${evidence}`);
        return {
          id: `concept_${index + 1}`,
          label: titleCasePhrase(phrase),
          category: category.label,
          categoryId: category.id,
          importance: Math.max(1, Math.min(5, Math.ceil(count + (evidence.length > 80 ? 1 : 0)))),
          evidence,
          confidence: confidenceFromEvidence(phrase, count, evidence)
        };
      });

    const existing = new Set(phraseConcepts.map((concept) => concept.label.toLowerCase()));
    keywordList.forEach((item) => {
      if (phraseConcepts.length >= settings.limit) return;
      if (existing.has(item.term)) return;
      const evidence = evidenceForTerm(sentences, item.term);
      if (!evidence) return;
      const category = categoryForText(`${item.term} ${evidence}`);
      phraseConcepts.push({
        id: `concept_${phraseConcepts.length + 1}`,
        label: titleCasePhrase(item.term),
        category: category.label,
        categoryId: category.id,
        importance: Math.max(1, Math.min(5, item.count)),
        evidence,
        confidence: confidenceFromEvidence(item.term, item.count, evidence)
      });
      existing.add(item.term);
    });

    return phraseConcepts;
  }

  function parseFactFromSentence(sentence, index) {
    const clean = normalize(sentence);
    const patterns = [
      /^(.{3,70}?)\s+(deve|devono|può|possono|protegge|comprende|include|richiede|evita|riduce|aumenta|migliora|controlla|segnala|usa|utilizza|serve)\s+(.{5,180})$/i,
      /^(.{3,70}?)\s+(è|sono|rappresenta|indica)\s+(.{5,180})$/i
    ];

    for (const pattern of patterns) {
      const match = clean.match(pattern);
      if (match) {
        return {
          id: `fact_${index + 1}`,
          subject: normalize(match[1]),
          predicate: normalize(match[2]),
          object: normalize(match[3]),
          evidence: clean,
          confidence: clean.length > 45 ? 0.78 : 0.62
        };
      }
    }

    const parts = clean.split(/\s+/);
    if (parts.length >= 7) {
      return {
        id: `fact_${index + 1}`,
        subject: parts.slice(0, Math.min(4, Math.ceil(parts.length / 4))).join(" "),
        predicate: "afferma",
        object: parts.slice(Math.min(4, Math.ceil(parts.length / 4))).join(" "),
        evidence: clean,
        confidence: 0.52
      };
    }

    return null;
  }

  function extractFacts(documentInputOrText, options) {
    const settings = Object.assign({ limit: 24 }, options || {});
    const sentences = splitSentences(textOf(documentInputOrText));
    const facts = [];

    sentences.forEach((sentence, index) => {
      if (facts.length >= settings.limit) return;
      const fact = parseFactFromSentence(sentence, index);
      if (!fact) return;
      facts.push(fact);
    });

    return facts;
  }

  function relationTypeForSentence(sentence) {
    for (const relation of RELATION_PATTERNS) {
      if (relation.patterns.some((pattern) => pattern.test(sentence))) {
        return relation.type;
      }
    }
    return null;
  }

  function extractRelations(documentInputOrText, concepts, facts, options) {
    const settings = Object.assign({ limit: 24 }, options || {});
    const sentences = splitSentences(textOf(documentInputOrText));
    const conceptList = Array.isArray(concepts) ? concepts : [];
    const relations = [];

    sentences.forEach((sentence, index) => {
      if (relations.length >= settings.limit) return;
      const type = relationTypeForSentence(sentence);
      if (!type) return;

      const mentioned = conceptList.filter((concept) => sentenceContains(sentence, concept.label)).slice(0, 2);
      const from = mentioned[0] ? mentioned[0].label : normalize(sentence).split(/\s+/).slice(0, 4).join(" ");
      const to = mentioned[1] ? mentioned[1].label : normalize(sentence).split(/\s+/).slice(-6).join(" ");

      relations.push({
        id: `relation_${index + 1}`,
        type,
        from,
        to,
        evidence: sentence,
        confidence: mentioned.length >= 1 ? 0.76 : 0.58
      });
    });

    const factList = Array.isArray(facts) ? facts : [];
    factList.forEach((fact) => {
      if (relations.length >= settings.limit) return;
      if (!/protegge|richiede|evita|riduce|include|comprende/i.test(fact.predicate)) return;
      const type = /protegge/i.test(fact.predicate)
        ? "protegge"
        : /richiede/i.test(fact.predicate)
          ? "richiede"
          : /evita|riduce/i.test(fact.predicate)
            ? "evita"
            : "appartiene_a";
      relations.push({
        id: `relation_from_${fact.id}`,
        type,
        from: fact.subject,
        to: fact.object,
        evidence: fact.evidence,
        confidence: Math.max(0.55, fact.confidence - 0.05)
      });
    });

    return relations;
  }

  function extractMainTopics(concepts, facts) {
    const conceptList = Array.isArray(concepts) ? concepts : [];
    const grouped = new Map();

    conceptList.forEach((concept) => {
      const key = concept.category || "Generico";
      if (!grouped.has(key)) grouped.set(key, []);
      grouped.get(key).push(concept);
    });

    return Array.from(grouped.entries()).map(([category, items]) => ({
      category,
      concepts: items.slice(0, 5).map((item) => item.label),
      importance: items.reduce((sum, item) => sum + (item.importance || 1), 0),
      evidence: items[0] ? items[0].evidence : ""
    })).sort((a, b) => b.importance - a.importance).slice(0, 8);
  }

  function buildKnowledgeBase(documentInputOrText, options) {
    const documentInput = typeof documentInputOrText === "string"
      ? (window.RagDocumentInputUnicoV1 ? window.RagDocumentInputUnicoV1.fromText(documentInputOrText) : { text: { clean: documentInputOrText }, title: "Documento" })
      : documentInputOrText;

    const concepts = extractConcepts(documentInput, options);
    const definitions = extractDefinitions(splitSentences(textOf(documentInput)));
    const examples = extractExamples(splitSentences(textOf(documentInput)));
    const facts = extractFacts(documentInput, options);
    const relations = extractRelations(documentInput, concepts, facts, options);
    const topics = extractMainTopics(concepts, facts);

    const evidence = [];
    concepts.forEach((item) => item.evidence && evidence.push({ source: item.id, text: item.evidence }));
    facts.forEach((item) => item.evidence && evidence.push({ source: item.id, text: item.evidence }));
    relations.forEach((item) => item.evidence && evidence.push({ source: item.id, text: item.evidence }));

    const averageConfidenceItems = concepts.concat(facts).concat(relations);
    const averageConfidence = averageConfidenceItems.length
      ? averageConfidenceItems.reduce((sum, item) => sum + (item.confidence || 0.5), 0) / averageConfidenceItems.length
      : 0;

    return {
      version: VERSION,
      createdAt: new Date().toISOString(),
      document: {
        id: documentInput.id || "doc_manuale",
        title: documentInput.title || "Documento utente",
        source: documentInput.source || { type: "manuale", origin: "utente" },
        metadata: documentInput.metadata || {}
      },
      topics,
      concepts,
      definitions,
      examples,
      facts,
      relations,
      evidence,
      confidence: Number(averageConfidence.toFixed(2)),
      outputRecommended: {
        cards: concepts.length > 0,
        summary: topics.length > 0 || facts.length > 0,
        studyQuestions: relations.length > 0 || concepts.length > 0,
        test: facts.length >= 3 || concepts.length >= 3
      }
    };
  }

  window.RagKnowledgeExtractorsV1 = {
    VERSION,
    splitParagraphs,
    splitSentences,
    topKeywords,
    extractConcepts,
    extractDefinitions,
    extractExamples,
    extractFacts,
    extractRelations,
    extractMainTopics,
    buildKnowledgeBase,
    categoryForText
  };
})();
