(function () {
  "use strict";

  const VERSION = "rag-knowledge-extractors-v33-final-polish";

  const STOPWORDS = new Set([
    "alla", "allo", "alle", "agli", "dalla", "dallo", "delle", "degli", "della", "dell", "nella", "nello", "nelle", "negli",
    "che", "con", "come", "per", "tra", "fra", "sono", "essere", "viene", "vengono", "questo", "questa", "questi", "quelle", "quelli",
    "anche", "deve", "devono", "può", "possono", "più", "meno", "molto", "ogni", "suo", "sua", "suoi", "loro", "del", "dei", "una", "uno", "gli", "non", "nel", "sul", "sui", "dal", "dai", "hai", "abbiamo", "hanno", "fare", "usare", "usati", "usato", "usata",
    "documento", "testo", "pagina", "sezione", "argomento", "argomenti", "rag", "quiz", "test", "manuale", "materiale", "fonte", "prova",
    "secondo", "afferma", "indica", "spiega", "creato", "creata", "inserito", "inserita", "cartella", "progetto", "contenuti", "contenuto", "distrattore", "medio", "obiettivo", "riguarda", "risposta", "corretta", "esempio", "forte", "debole", "metodo", "migliore"
  ]);

  const CATEGORY_RULES = [
    { id: "sicurezza", label: "Sicurezza", terms: ["sicurezza", "protezione", "rischio", "accesso", "password", "credenziali", "malware", "phishing", "backup", "firewall", "ransomware", "antivirus", "vulnerabilità", "autenticazione"] },
    { id: "formazione", label: "Formazione", terms: ["formazione", "corso", "lezione", "studio", "apprendimento", "verifica", "esame", "competenza", "didattico", "spiegare"] },
    { id: "lavoro", label: "Lavoro", terms: ["azienda", "lavoro", "cliente", "processo", "reparto", "responsabile", "procedura", "attività", "dipendente", "utenti"] },
    { id: "sport", label: "Sport e allenamento", terms: ["allenamento", "esercizio", "serie", "ripetizioni", "recupero", "forza", "corsa", "mobilità", "carico"] },
    { id: "curriculum", label: "Curriculum", terms: ["curriculum", "esperienza", "profilo", "competenze", "istruzione", "candidato", "ruolo", "progetto"] },
    { id: "storia", label: "Storia o racconto", terms: ["racconto", "personaggio", "storia", "scena", "capitolo", "narrazione", "dialogo"] },
    { id: "poesia", label: "Poesia", terms: ["poesia", "verso", "strofa", "rima", "metafora", "immagine", "ritmo"] },
    { id: "generico", label: "Generico", terms: [] }
  ];

  const RELATION_PATTERNS = [
    { type: "causa", label: "causa", patterns: [/\bperch[eé]\b/i, /\ba causa di\b/i, /\bpoich[eé]\b/i, /\bquindi\b/i, /\bdi conseguenza\b/i] },
    { type: "richiede", label: "richiede", patterns: [/\brichiede\b/i, /\bdeve\b/i, /\bdevono\b/i, /\bnecessita\b/i, /\bserve\b/i, /\bbisogna\b/i] },
    { type: "evita", label: "evita", patterns: [/\bevitar[ea]\b/i, /\bpreviene\b/i, /\bripara da\b/i, /\brimuove\b/i, /\brallenta\b/i, /\bruce\b/i] },
    { type: "protegge", label: "protegge", patterns: [/\bprotegge\b/i, /\bproteggere\b/i, /\bdifende\b/i, /\bsalvaguarda\b/i] },
    { type: "appartiene_a", label: "appartiene a", patterns: [/\bfa parte di\b/i, /\bappartiene a\b/i, /\binclude\b/i, /\bcomprende\b/i, /\bcontiene\b/i] },
    { type: "prima_dopo", label: "prima/dopo", patterns: [/\bprima\b/i, /\bdopo\b/i, /\bsuccessivamente\b/i, /\bin seguito\b/i] },
    { type: "problema_soluzione", label: "problema/soluzione", patterns: [/\bproblema\b/i, /\bsoluzione\b/i, /\brisolvere\b/i, /\bcontrollo\b/i, /\bcorrezione\b/i] }
  ];

  const NOISE_PATTERNS = [
    /^\s*#{1,6}\s*documento\b/i,
    /^\s*#{1,6}\s*$/i,
    /\bquesto documento\s+(?:è stato|e stato|serve|può essere|puo essere|viene)/i,
    /\bfonte di prova per il motore rag\b/i,
    /\bprogetto quiz\b/i,
    /\bcartella\s+[`']?rag\/?documenti/i,
    /\bmateriale formativo chiaro da cui il sistema rag\b/i,
    /\bdocumento rag di test\b/i,
    /\bpensato come manuale tecnico avanzato\b/i,
    /\bdistrattore medio\b/i,
    /\besempio\s+(?:più|piu)\s+forte\b/i,
    /\besempio\s+debole\b/i,
    /\bmetodo\s+migliore\b/i,
    /^\s*(titolo|autore|data|versione)\s*[:=-]/i
  ];

  function textOf(documentInputOrText) {
    if (typeof documentInputOrText === "string") return documentInputOrText;
    if (documentInputOrText && documentInputOrText.text) return documentInputOrText.text.clean || documentInputOrText.text.original || "";
    return "";
  }

  function normalize(text) {
    return String(text || "")
      .replace(/\u00A0/g, " ")
      .replace(/[“”]/g, '"')
      .replace(/[‘’]/g, "'")
      .replace(/\s+/g, " ")
      .trim();
  }

  function stripMarkdown(text) {
    return normalize(text)
      .replace(/^#{1,6}\s*/, "")
      .replace(/^[-*+]\s+/, "")
      .replace(/`([^`]+)`/g, "$1")
      .replace(/\*\*([^*]+)\*\*/g, "$1")
      .replace(/__([^_]+)__/g, "$1")
      .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1");
  }

  function isNoiseSentence(sentence) {
    const clean = normalize(sentence);
    if (!clean) return true;
    if (clean.length < 18) return true;
    if (clean.length > 420) return true;
    if (NOISE_PATTERNS.some((pattern) => pattern.test(clean))) return true;
    if (/^#{1,6}\s/.test(clean)) return true;
    const lower = clean.toLowerCase();
    const badStarts = ["questo documento è stato", "questo documento e stato", "può essere inserito", "puo essere inserito", "rag di test"];
    if (badStarts.some((start) => lower.startsWith(start))) return true;
    return false;
  }

  function splitParagraphs(text) {
    return String(text || "")
      .split(/\n{2,}/)
      .map(stripMarkdown)
      .filter((paragraph) => paragraph.length > 0 && !isNoiseSentence(paragraph));
  }

  function splitSentences(text) {
    const lines = String(text || "")
      .split(/\n+/)
      .map(stripMarkdown)
      .filter((line) => line && !/^#{1,6}\s*documento/i.test(line));

    const protectedText = lines.join(". ").replace(/\b(es|dr|sig|prof|ing|avv)\./gi, (match) => match.replace(".", "§"));
    return protectedText
      .split(/(?<=[.!?])\s+|[•;]+/)
      .map((sentence) => stripMarkdown(sentence.replace(/§/g, ".")))
      .filter((sentence) => !isNoiseSentence(sentence));
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

  function titleCasePhrase(phrase) {
    const clean = stripMarkdown(phrase).toLowerCase();
    if (!clean) return "";
    return clean.charAt(0).toUpperCase() + clean.slice(1);
  }

  function canonicalConceptKey(value) {
    return normalize(value)
      .toLowerCase()
      .replace(/\bautenticazione\s+due\s+fattori\b/g, "autenticazione a due fattori")
      .replace(/\bemail\b/g, "e-mail")
      .replace(/\be mail\b/g, "e-mail")
      .replace(/[^a-zà-öø-ÿ0-9\s]/gi, " ")
      .replace(/\b(a|ad|di|del|della|dei|degli|le|la|il|lo|gli|i|un|una|uno)\b/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function simplifyPhrase(phrase) {
    let clean = stripMarkdown(phrase)
      .replace(/^(il|lo|la|i|gli|le|un|uno|una)\s+/i, "")
      .replace(/^(deve|devono|può|possono|serve|richiede|significa che|distrattore medio:?|obiettivo:?|non:?|secondo il documento:?|documento rag di test:?|rag di test:?)\s+/i, "")
      .replace(/\s+(deve|devono|può|possono|serve|richiede)$/i, "")
      .replace(/\bautenticazione\s+due\s+fattori\b/i, "autenticazione a due fattori")
      .replace(/[.,:;!?]+$/g, "")
      .trim();

    if (clean.length > 58) clean = clean.slice(0, 58).replace(/\s+\S*$/, "");
    return titleCasePhrase(clean);
  }

  function badConceptLabel(label) {
    const clean = normalize(label).toLowerCase();
    if (!clean || clean.length < 4 || clean.length > 65) return true;
    if (/^#/.test(clean)) return true;
    if (/\b(documento rag|questo documento|secondo il documento|fonte|prova|motore rag|progetto quiz|cartella|distrattore medio|esempio debole|esempio più forte|esempio piu forte|metodo migliore|manuale tecnico avanzato|materiale formativo|opzione|risposta corretta)\b/.test(clean)) return true;
    if (/\b(deve|devono|può essere|puo essere|afferma|richiede che|significa che|non riguarda solo|può dire|puo dire)\b/.test(clean)) return true;
    if (clean.split(/\s+/).length > 6) return true;
    return false;
  }

  function topKeywords(text, limit) {
    const freq = frequencyMap(words(text));
    return Array.from(freq.entries())
      .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
      .slice(0, limit || 20)
      .map(([term, count]) => ({ term, count }));
  }

  function extractCandidatePhrases(text) {
    const candidates = [];
    const sentenceList = splitSentences(text);

    sentenceList.forEach((sentence) => {
      const explicitTerms = sentence.match(/\b(?:autenticazione a due fattori|password manager|aggiornamenti software|sicurezza informatica|e-mail sospette|email sospette|dati riservati|comportamenti corretti|attacco ransomware|cancellazione accidentale|utenti autorizzati|informazioni riservate|sistemi digitali|password sicura|responsabile della sicurezza|reparto it|integrità|integrita|disponibilità|disponibilita|password sicura)\b/gi) || [];
      explicitTerms.forEach((term) => candidates.push(simplifyPhrase(term)));

      const chunks = sentence
        .split(/[,;:.()\[\]{}]/)
        .map(stripMarkdown)
        .filter((chunk) => chunk.length >= 8 && chunk.length <= 110);

      chunks.forEach((chunk) => {
        const chunkWords = words(chunk);
        if (chunkWords.length >= 2 && chunkWords.length <= 5) {
          candidates.push(simplifyPhrase(chunkWords.join(" ")));
        }
      });
    });

    return candidates.filter((candidate) => candidate && !badConceptLabel(candidate));
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
    const lowerTerm = normalize(term).toLowerCase();
    if (!lowerTerm) return "";
    return sentences.find((sentence) => sentenceContains(sentence, lowerTerm)) ||
      sentences.find((sentence) => words(lowerTerm).some((word) => sentenceContains(sentence, word))) || "";
  }

  function confidenceFromEvidence(term, count, evidence) {
    let score = 0.48;
    if (count >= 2) score += 0.14;
    if (count >= 4) score += 0.1;
    if (evidence.length >= 55) score += 0.12;
    if (term.split(/\s+/).length >= 2) score += 0.1;
    if (badConceptLabel(term)) score -= 0.2;
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
        const term = simplifyPhrase(match[1]);
        const description = stripMarkdown(match[2]);
        if (!badConceptLabel(term) && description.length >= 8) {
          definitions.push({ term, description, evidence: sentence, confidence: 0.82 });
        }
      });
    });

    return definitions.slice(0, 12);
  }

  function extractExamples(sentences) {
    return sentences
      .filter((sentence) => /\bad esempio\b|\besempio\b|\bcome\b|\btipo\b/i.test(sentence))
      .filter((sentence) => !isNoiseSentence(sentence))
      .slice(0, 10)
      .map((sentence) => ({ text: sentence, confidence: 0.7 }));
  }

  function extractConcepts(documentInputOrText, options) {
    const settings = Object.assign({ limit: 18 }, options || {});
    const text = textOf(documentInputOrText);
    const sentences = splitSentences(text);
    const phraseFreq = frequencyMap(extractCandidatePhrases(text));
    const keywordList = topKeywords(text, 40);
    const concepts = [];
    const seen = new Set();

    function addConcept(label, count) {
      const cleanLabel = simplifyPhrase(label);
      const key = canonicalConceptKey(cleanLabel);
      if (concepts.length >= settings.limit) return;
      if (seen.has(key) || badConceptLabel(cleanLabel)) return;
      const evidence = evidenceForTerm(sentences, cleanLabel) || evidenceForTerm(sentences, words(cleanLabel)[0]);
      if (!evidence) return;
      const category = categoryForText(`${cleanLabel} ${evidence}`);
      concepts.push({
        id: `concept_${concepts.length + 1}`,
        label: cleanLabel,
        category: category.label,
        categoryId: category.id,
        importance: Math.max(1, Math.min(5, Math.ceil((count || 1) + (evidence.length > 80 ? 1 : 0)))),
        evidence,
        confidence: confidenceFromEvidence(cleanLabel, count || 1, evidence)
      });
      seen.add(key);
    }

    Array.from(phraseFreq.entries())
      .sort((a, b) => b[1] - a[1] || b[0].length - a[0].length)
      .forEach(([phrase, count]) => addConcept(phrase, count));

    keywordList.forEach((item) => addConcept(item.term, item.count));

    return concepts;
  }

  function cleanSubjectOrObject(value) {
    return stripMarkdown(value)
      .replace(/^(il documento|questo documento|la sezione|secondo il documento)\s*/i, "")
      .replace(/^che\s+/i, "")
      .replace(/^password\s+non\s+/i, "password ")
      .replace(/^anche\s+se\s+un\s+attaccante\s+scopre\s+la\s+password/i, "attaccante che scopre la password")
      .replace(/^può\s+dire\s+che\s+/i, "")
      .replace(/^metodo\s+migliore\s*/i, "password manager")
      .replace(/^usare\s+la\s+stessa\s+password\s*/i, "uso della stessa password")
      .replace(/\s+/g, " ")
      .replace(/[.;:]+$/g, "")
      .trim();
  }

  function isBadFactPart(value) {
    const clean = normalize(value).toLowerCase();
    if (!clean || clean.length < 3) return true;
    if (/^#/.test(clean)) return true;
    if (/\b(fonte di prova|motore rag|progetto quiz|cartella|questo documento è stato|può essere inserito|documento rag di test|pensato come manuale tecnico avanzato|distrattore medio|esempio debole|esempio più forte|esempio piu forte)\b/.test(clean)) return true;
    if (/^(non|obiettivo|l'obiettivo|lo scopo|titolo|documento)$/i.test(clean)) return true;
    return false;
  }

  function parseFactFromSentence(sentence, index) {
    const clean = stripMarkdown(sentence);
    if (isNoiseSentence(clean)) return null;

    const patterns = [
      /^(.{3,90}?)\s+(deve|devono|può|possono|protegge|comprende|include|richiede|evita|riduce|aumenta|migliora|corregge|controlla|segnala|usa|utilizza|serve)\s+(.{5,190})$/i,
      /^(.{3,90}?)\s+(è|sono|rappresenta|indica|significa)\s+(.{5,190})$/i
    ];

    for (const pattern of patterns) {
      const match = clean.match(pattern);
      if (!match) continue;
      const subject = cleanSubjectOrObject(match[1]);
      const predicate = normalize(match[2]).toLowerCase();
      const object = cleanSubjectOrObject(match[3]);
      if (isBadFactPart(subject) || isBadFactPart(object)) continue;
      if (subject.length > 90 || object.length > 190) continue;
      return {
        id: `fact_${index + 1}`,
        subject,
        predicate,
        object,
        evidence: clean,
        confidence: predicate === "è" || predicate === "sono" ? 0.7 : 0.76
      };
    }

    const parts = clean.split(/[,;:]/).map(cleanSubjectOrObject).filter(Boolean);
    if (parts.length >= 2 && parts[0].length <= 70 && parts[1].length <= 170 && !isBadFactPart(parts[0]) && !isBadFactPart(parts[1])) {
      return {
        id: `fact_${index + 1}`,
        subject: parts[0],
        predicate: "afferma",
        object: parts.slice(1).join("; "),
        evidence: clean,
        confidence: 0.55
      };
    }

    return null;
  }

  function extractFacts(documentInputOrText, options) {
    const settings = Object.assign({ limit: 24 }, options || {});
    const sentences = splitSentences(textOf(documentInputOrText));
    const facts = [];
    const seen = new Set();

    sentences.forEach((sentence, index) => {
      if (facts.length >= settings.limit) return;
      const fact = parseFactFromSentence(sentence, index);
      if (!fact) return;
      const key = `${canonicalConceptKey(fact.subject)}|${fact.predicate}|${canonicalConceptKey(fact.object)}`.toLowerCase();
      if (seen.has(key)) return;
      seen.add(key);
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

  function makeFriendlyRelation(type, from, to, evidence) {
    const cleanFrom = cleanSubjectOrObject(from);
    const cleanTo = cleanSubjectOrObject(to);
    const templates = {
      causa: {
        question: `Quale causa o conseguenza collega ${cleanFrom} al resto del documento?`,
        answer: `${cleanFrom} è collegato a ${cleanTo}.`
      },
      richiede: {
        question: `Che cosa richiede ${cleanFrom} secondo il documento?`,
        answer: `${cleanFrom} richiede ${cleanTo}.`
      },
      evita: {
        question: `Che cosa aiuta a evitare ${cleanFrom}?`,
        answer: `${cleanFrom} aiuta a evitare ${cleanTo}.`
      },
      protegge: {
        question: `Che cosa protegge ${cleanFrom}?`,
        answer: `${cleanFrom} protegge ${cleanTo}.`
      },
      appartiene_a: {
        question: `A quale insieme appartiene ${cleanFrom}?`,
        answer: `${cleanFrom} appartiene a ${cleanTo}.`
      },
      prima_dopo: {
        question: `Quale ordine temporale emerge su ${cleanFrom}?`,
        answer: `${cleanFrom} è collegato in ordine temporale a ${cleanTo}.`
      },
      problema_soluzione: {
        question: `Quale problema o soluzione riguarda ${cleanFrom}?`,
        answer: `${cleanFrom} riguarda ${cleanTo}.`
      }
    };
    const item = templates[type] || { question: `Quale relazione emerge su ${cleanFrom}?`, answer: `${cleanFrom} è collegato a ${cleanTo}.` };
    return {
      questionHint: item.question,
      answerText: item.answer,
      evidence
    };
  }

  function extractRelations(documentInputOrText, concepts, facts, options) {
    const settings = Object.assign({ limit: 24 }, options || {});
    const sentences = splitSentences(textOf(documentInputOrText));
    const conceptList = Array.isArray(concepts) ? concepts : [];
    const relations = [];
    const seen = new Set();

    function addRelation(type, from, to, evidence, confidence) {
      const cleanFrom = cleanSubjectOrObject(from);
      const cleanTo = cleanSubjectOrObject(to);
      if (!cleanFrom || !cleanTo || isBadFactPart(cleanFrom) || isBadFactPart(cleanTo)) return;
      if (cleanFrom.length > 90 || cleanTo.length > 170) return;
      const key = `${type}|${canonicalConceptKey(cleanFrom)}|${canonicalConceptKey(cleanTo)}`.toLowerCase();
      if (seen.has(key) || relations.length >= settings.limit) return;
      seen.add(key);
      const friendly = makeFriendlyRelation(type, cleanFrom, cleanTo, evidence);
      relations.push({
        id: `relation_${relations.length + 1}`,
        type,
        typeLabel: (RELATION_PATTERNS.find((r) => r.type === type) || {}).label || type,
        from: cleanFrom,
        to: cleanTo,
        questionHint: friendly.questionHint,
        answerText: friendly.answerText,
        evidence,
        confidence: confidence || 0.62
      });
    }

    sentences.forEach((sentence) => {
      if (relations.length >= settings.limit) return;
      const type = relationTypeForSentence(sentence);
      if (!type) return;
      const mentioned = conceptList.filter((concept) => sentenceContains(sentence, concept.label)).slice(0, 2);
      if (mentioned.length >= 2) {
        addRelation(type, mentioned[0].label, mentioned[1].label, sentence, 0.78);
      } else {
        const fact = parseFactFromSentence(sentence, relations.length);
        if (fact) addRelation(type, fact.subject, fact.object, sentence, 0.72);
      }
    });

    (Array.isArray(facts) ? facts : []).forEach((fact) => {
      if (relations.length >= settings.limit) return;
      if (!/protegge|richiede|evita|riduce|include|comprende|serve|deve|devono/i.test(fact.predicate)) return;
      const type = /protegge/i.test(fact.predicate)
        ? "protegge"
        : /richiede|serve|deve|devono/i.test(fact.predicate)
          ? "richiede"
          : /evita|riduce/i.test(fact.predicate)
            ? "evita"
            : "appartiene_a";
      addRelation(type, fact.subject, fact.object, fact.evidence, Math.max(0.58, (fact.confidence || 0.65) - 0.04));
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

    let topics = Array.from(grouped.entries()).map(([category, items]) => ({
      category,
      concepts: Array.from(new Set(items.slice(0, 6).map((item) => item.label))).slice(0, 5),
      importance: items.reduce((sum, item) => sum + (item.importance || 1), 0),
      evidence: items[0] ? items[0].evidence : ""
    })).sort((a, b) => b.importance - a.importance).slice(0, 8);
    if (topics.some((topic) => !/^generico$/i.test(topic.category))) {
      topics = topics.filter((topic) => !/^generico$/i.test(topic.category));
    }
    return topics;
  }

  function buildKnowledgeBase(documentInputOrText, options) {
    const documentInput = typeof documentInputOrText === "string"
      ? (window.RagDocumentInputUnicoV1 ? window.RagDocumentInputUnicoV1.fromText(documentInputOrText) : { text: { clean: documentInputOrText }, title: "Documento" })
      : documentInputOrText;

    const sourceText = textOf(documentInput);
    const sentences = splitSentences(sourceText);
    const concepts = extractConcepts(documentInput, options);
    const definitions = extractDefinitions(sentences);
    const examples = extractExamples(sentences);
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
    categoryForText,
    canonicalConceptKey
  };
})();


/*
  RAG_QUALITY_V33_WEAK_CONCEPT_FILTER
  Filtro didattico morbido, non censura contenuto.
  Non blocca documenti. Evita solo che frammenti sporchi diventino card.
  Controlli: intercettare|verifica sistema
*/
(function () {
  "use strict";

  const weakConceptPatternsV33 = [
    /hotel\s+aeroporto/i,
    /intercettare\s+traffico/i,
    /traffico\s+utenti/i,
    /poi\s+verifica\s+sistema/i,
    /verifica\s+sistema\s+funzioni/i,
    /esempio\s+debole/i,
    /esempio\s+pi[uù]\s+forte/i,
    /metodo\s+migliore/i,
    /documento\s+rag\s+di\s+test/i,
    /distrattore\s+medio/i
  ];

  function normalizeV33(value) {
    return String(value || "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function isWeakConceptV33(value) {
    const clean = normalizeV33(value);
    if (!clean) return true;
    return weakConceptPatternsV33.some((pattern) => pattern.test(clean));
  }

  function cleanConceptArrayV33(items) {
    if (!Array.isArray(items)) return items;

    const seenExact = new Set();

    return items.filter((item) => {
      const title = normalizeV33(
        item?.title ||
        item?.titolo ||
        item?.name ||
        item?.nome ||
        item?.concept ||
        item?.concetto ||
        item
      );

      if (isWeakConceptV33(title)) return false;

      const key = title.toLowerCase();

      if (seenExact.has(key)) return false;
      seenExact.add(key);

      return true;
    });
  }

  function cleanKnowledgeObjectV33(result) {
    if (!result || typeof result !== "object") return result;

    if (Array.isArray(result.concepts)) {
      result.concepts = cleanConceptArrayV33(result.concepts);
    }

    if (Array.isArray(result.concetti)) {
      result.concetti = cleanConceptArrayV33(result.concetti);
    }

    if (result.knowledgeBase && Array.isArray(result.knowledgeBase.concepts)) {
      result.knowledgeBase.concepts = cleanConceptArrayV33(result.knowledgeBase.concepts);
    }

    if (result.baseConoscenza && Array.isArray(result.baseConoscenza.concetti)) {
      result.baseConoscenza.concetti = cleanConceptArrayV33(result.baseConoscenza.concetti);
    }

    return result;
  }

  window.RagQualityV33WeakConceptFilter = {
    weakConceptPatternsV33,
    isWeakConceptV33,
    cleanConceptArrayV33,
    cleanKnowledgeObjectV33
  };
})();

