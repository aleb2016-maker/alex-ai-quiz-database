(function () {
  "use strict";

  const VERSION = "rag-general-validator-v34-final-clean";

  function clean(text) {
    return String(text || "").replace(/\s+/g, " ").trim();
  }

  function normalizeKey(text) {
    return clean(text).toLowerCase();
  }

  function canonical(text) {
    return clean(text)
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9à-öø-ÿ\s]/gi, " ")
      .replace(/\b(a|ad|di|del|della|dei|degli|le|la|il|lo|gli|i|un|una|uno|che|per|con|come|sono|essere|documento|secondo)\b/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function infoWords(text) {
    return canonical(text).split(/\s+/).filter((word) => word.length >= 4);
  }

  function similarity(a, b) {
    const aWords = new Set(infoWords(a));
    const bWords = new Set(infoWords(b));
    if (!aWords.size || !bWords.size) return 0;
    let overlap = 0;
    aWords.forEach((word) => {
      if (bWords.has(word)) overlap += 1;
    });
    return overlap / Math.min(aWords.size, bWords.size);
  }

  function hasUsefulVerb(text) {
    return /\b(è|sono|può|possono|deve|devono|serve|servono|richiede|richiedono|protegge|proteggono|riduce|riducono|evita|evitano|permette|permettono|aggiunge|aggiungono|corregge|correggono|garantisce|garantiscono|significa|indica|include|comprende|gestisce|segnala|recupera|blocca|impedisce|consente)\b/i.test(clean(text));
  }

  function hasDidacticSignal(text) {
    return /\b(perché|quindi|serve|richiede|protegge|riduce|evita|permette|aggiunge|corregge|significa|include|comprende|rischio|causa|conseguenza|procedura|controllo|protezione|accesso|dati|password|backup|software|vulnerabil|attacco|phishing|malware|ransomware|autenticazione|account)\b/i.test(clean(text));
  }

  function hasBrokenGrammar(text) {
    return /\bdovrebbero gestiti\b|\bse essere\b|\bricordare ricordare\b|\busati per proteggere\.?$|\bse gli utenti\.?$|\bche\.?$|\.\.|Sicurezza informatica protegge l'insieme/i.test(clean(text));
  }

  function weakCardBody(card) {
    const title = clean(card && card.title);
    const body = clean(card && card.body);
    if (!body || body.length < 90) return true;
    if (hasBrokenGrammar(body)) return true;
    if (infoWords(body).length < 10) return true;
    if (canonical(body) === canonical(title)) return true;
    if (!hasUsefulVerb(body)) return true;
    if (!hasDidacticSignal(body)) return true;
    if (/^(aggiornamenti software|autenticazione a due fattori|sicurezza informatica|password manager)\.?$/i.test(body)) return true;
    return false;
  }

  function titleBodyMismatch(card) {
    const title = clean(card && card.title);
    const body = clean(card && card.body);
    if (!title || !body || infoWords(title).length === 0) return false;
    return similarity(title, body) < 0.12;
  }

  function hasDuplicateKeys(items, keyFn) {
    const seen = new Set();
    const duplicates = [];
    (items || []).forEach((item) => {
      const key = normalizeKey(keyFn(item));
      if (!key) return;
      if (seen.has(key)) duplicates.push(key);
      seen.add(key);
    });
    return duplicates;
  }

  function evidenceExistsInDocument(evidence, documentText) {
    const ev = clean(evidence);
    const doc = clean(documentText);
    if (!ev) return false;
    if (!doc) return true;
    if (doc.includes(ev)) return true;
    const evWords = ev.toLowerCase().split(/\s+/).filter((word) => word.length >= 4);
    if (!evWords.length) return false;
    const matches = evWords.filter((word) => doc.toLowerCase().includes(word)).length;
    return matches / evWords.length >= 0.62;
  }

  function containsRawTechnicalText(text) {
    const value = clean(text).toLowerCase();
    return /#\s*documento|problema_soluzione|prima_dopo|appartiene_a|relation_|concept_|fact_|→|\s->\s|che cosa afferma #|secondo il documento, che cosa afferma #/.test(value);
  }


  function tooLongOption(text) {
    const value = clean(text);
    return value.length > 80 || /…|\.\.\./.test(value);
  }

  function weakOption(text) {
    const value = clean(text).toLowerCase();
    if (!value || value.length < 4) return true;
    if (/documento rag di test|pensato come manuale tecnico|materiale formativo|distrattore medio|esempio debole|esempio più forte|esempio piu forte|metodo migliore|hotel aeroporto|intercettare traffico utenti/.test(value)) return true;
    if (/^(non|obiettivo|documento)$/.test(value)) return true;
    return false;
  }

  function weakQuestion(text) {
    const value = clean(text).toLowerCase();
    if (!value.endsWith("?")) return true;
    if (/secondo il documento\?$/.test(value)) return true;
    if (/che cosa protegge sicurezza informatica\?/i.test(value)) return true;
    if (/^che cosa bisogna ricordare su\b/.test(value)) return true;
    if (/^quale collegamento emerge tra\b/.test(value)) return true;
    if (/che cosa afferma\s*(#|documento|può essere|puo essere|-)\b/.test(value)) return true;
    if (/secondo il documento, che cosa afferma/.test(value)) return true;
    if (/che cosa dice il documento su (non|l\'obiettivo|obiettivo|esempio debole|esempio più forte|esempio piu forte|metodo migliore)\b/.test(value)) return true;
    if (/documento rag di test|pensato come manuale tecnico|distrattore medio|esempio debole|esempio più forte|esempio piu forte|metodo migliore|hotel aeroporto|intercettare traffico utenti/.test(value)) return true;
    return false;
  }

  function validateKnowledgeBase(kb, documentText) {
    const errors = [];
    const warnings = [];

    if (!kb) {
      return { valid: false, errors: ["base_conoscenza_mancante"], warnings: [], score: 0 };
    }

    if (!kb.document) errors.push("documento_mancante");
    if (!Array.isArray(kb.concepts) || kb.concepts.length === 0) warnings.push("nessun_concetto_estratto");
    if (!Array.isArray(kb.facts) || kb.facts.length === 0) warnings.push("nessun_fatto_estratto");
    if (!Array.isArray(kb.relations) || kb.relations.length === 0) warnings.push("nessuna_relazione_estratta");

    const duplicateConcepts = hasDuplicateKeys(kb.concepts || [], (concept) => concept.label);
    if (duplicateConcepts.length) warnings.push(`concetti_duplicati:${duplicateConcepts.slice(0, 5).join(",")}`);

    (kb.concepts || []).forEach((concept) => {
      if (containsRawTechnicalText(concept.label)) warnings.push(`concetto_sporco:${concept.id || "senza_id"}`);
      if (clean(concept.label).length > 70) warnings.push(`concetto_troppo_lungo:${concept.id || "senza_id"}`);
      if (/distrattore medio|documento rag di test|manuale tecnico|esempio debole|esempio più forte|esempio piu forte|metodo migliore|hotel aeroporto|intercettare traffico utenti/i.test(concept.label)) warnings.push(`concetto_non_didattico:${concept.id || "senza_id"}`);
    });

    (kb.facts || []).forEach((fact) => {
      if (containsRawTechnicalText(fact.subject) || containsRawTechnicalText(fact.object)) warnings.push(`fatto_sporco:${fact.id || "senza_id"}`);
      if (clean(fact.subject).length > 100 || clean(fact.object).length > 210) warnings.push(`fatto_troppo_lungo:${fact.id || "senza_id"}`);
    });

    (kb.relations || []).forEach((relation) => {
      if (!relation.questionHint || !relation.answerText) warnings.push(`relazione_senza_testo_utente:${relation.id || "senza_id"}`);
      if (containsRawTechnicalText(relation.questionHint) || containsRawTechnicalText(relation.answerText)) warnings.push(`relazione_testo_sporco:${relation.id || "senza_id"}`);
    });

    const allEvidenceItems = []
      .concat(kb.concepts || [])
      .concat(kb.facts || [])
      .concat(kb.relations || []);

    allEvidenceItems.forEach((item) => {
      if (!item.evidence) {
        warnings.push(`prova_mancante:${item.id || "senza_id"}`);
      } else if (!evidenceExistsInDocument(item.evidence, documentText)) {
        warnings.push(`prova_non_ritrovata:${item.id || "senza_id"}`);
      }

      if (typeof item.confidence === "number" && item.confidence < 0.45) {
        warnings.push(`fiducia_bassa:${item.id || "senza_id"}`);
      }
    });

    const score = Math.max(0, 100 - errors.length * 35 - warnings.length * 2);
    return { valid: errors.length === 0, errors, warnings, score };
  }

  function validateGeneratedOutput(output, kb, documentText) {
    const errors = [];
    const warnings = [];

    if (!output) {
      return { valid: false, errors: ["output_mancante"], warnings: [], score: 0 };
    }

    const cards = output.cards || [];
    const test = output.test || [];
    const studyQuestions = output.studyQuestions || [];
    const summary = output.summary || null;

    if (!cards.length) warnings.push("nessuna_card_generata");
    if (!studyQuestions.length) warnings.push("nessuna_domanda_studio_generata");
    if (!test.length) warnings.push("nessun_test_generato");

    if (summary) {
      const summaryText = clean([
        summary.intro || "",
        (summary.keyPoints || []).map((point) => `${point.title || ""} ${point.text || ""}`).join(" ")
      ].join(" "));
      if (hasBrokenGrammar(summaryText)) errors.push("riassunto_sgrammaticato");
      if (/Concetti principali:/i.test(summaryText)) errors.push("riassunto_label_grezze");
    }

    const duplicateCards = hasDuplicateKeys(cards, (card) => card.title);
    if (duplicateCards.length) warnings.push(`card_duplicate:${duplicateCards.slice(0, 5).join(",")}`);

    cards.forEach((card, index) => {
      cards.slice(index + 1).forEach((other) => {
        if (similarity(card.body, other.body) >= 0.68 || similarity(card.evidence, other.evidence) >= 0.75) {
          warnings.push(`card_quasi_duplicata:${card.id || "senza_id"}:${other.id || "senza_id"}`);
        }
      });
    });

    const duplicateQuestions = hasDuplicateKeys(test, (question) => question.question);
    if (duplicateQuestions.length) warnings.push(`domande_test_duplicate:${duplicateQuestions.slice(0, 5).join(",")}`);

    cards.forEach((card) => {
      if (!card.title || !card.body) errors.push(`card_incompleta:${card.id || "senza_id"}`);
      if (hasBrokenGrammar(`${card.title} ${card.body}`)) errors.push(`card_sgrammaticata:${card.id || "senza_id"}`);
      if (containsRawTechnicalText(card.title) || containsRawTechnicalText(card.body)) warnings.push(`card_testo_sporco:${card.id || "senza_id"}`);
      if (weakCardBody(card)) warnings.push(`card_body_debole:${card.id || "senza_id"}`);
      if (titleBodyMismatch(card)) warnings.push(`card_titolo_body_mismatch:${card.id || "senza_id"}`);
      if (!card.iconSvg && !card.iconHint) warnings.push(`card_senza_icona:${card.id || "senza_id"}`);
      if (card.evidence && !evidenceExistsInDocument(card.evidence, documentText)) warnings.push(`card_non_dimostrata:${card.id || "senza_id"}`);
      if (typeof card.confidence === "number" && card.confidence < 0.45) warnings.push(`card_fiducia_bassa:${card.id || "senza_id"}`);
    });

    studyQuestions.forEach((question) => {
      if (!question.question || !question.answer) errors.push(`domanda_studio_incompleta:${question.id || "senza_id"}`);
      if (hasBrokenGrammar(`${question.question} ${question.answer}`)) errors.push(`domanda_studio_sgrammaticata:${question.id || "senza_id"}`);
      if (weakQuestion(question.question)) warnings.push(`domanda_studio_debole:${question.id || "senza_id"}`);
      if (containsRawTechnicalText(question.question) || containsRawTechnicalText(question.answer)) warnings.push(`domanda_studio_testo_sporco:${question.id || "senza_id"}`);
      if (question.evidence && !evidenceExistsInDocument(question.evidence, documentText)) warnings.push(`domanda_studio_non_dimostrata:${question.id || "senza_id"}`);
    });

    const usedOptions = new Map();
    test.forEach((question) => {
      if (!question.question || !Array.isArray(question.options) || !question.correctAnswer) {
        errors.push(`test_incompleto:${question.id || "senza_id"}`);
        return;
      }
      if (weakQuestion(question.question)) warnings.push(`domanda_test_debole:${question.id || "senza_id"}`);
      if (hasBrokenGrammar(`${question.question} ${question.correctAnswer} ${(question.options || []).join(" ")}`)) errors.push(`test_sgrammaticato:${question.id || "senza_id"}`);
      if (containsRawTechnicalText(question.question)) warnings.push(`domanda_test_sporca:${question.id || "senza_id"}`);
      if (question.options.length !== 4) warnings.push(`opzioni_non_quattro:${question.id || "senza_id"}`);
      if (!question.options.includes(question.correctAnswer)) errors.push(`risposta_corretta_fuori_opzioni:${question.id || "senza_id"}`);
      if (hasDuplicateKeys(question.options, (option) => option).length) warnings.push(`opzioni_duplicate:${question.id || "senza_id"}`);
      question.options.forEach((option) => {
        const optionKey = canonical(option);
        if (optionKey) usedOptions.set(optionKey, (usedOptions.get(optionKey) || 0) + 1);
        if (containsRawTechnicalText(option)) warnings.push(`opzione_sporca:${question.id || "senza_id"}`);
        if (tooLongOption(option)) warnings.push(`opzione_troppo_lunga:${question.id || "senza_id"}`);
        if (weakOption(option)) warnings.push(`opzione_debole:${question.id || "senza_id"}`);
      });
      if (question.evidence && !evidenceExistsInDocument(question.evidence, documentText)) warnings.push(`test_non_dimostrato:${question.id || "senza_id"}`);
    });

    Array.from(usedOptions.entries()).forEach(([option, count]) => {
      if (count >= 3) warnings.push(`opzione_ripetuta:${option}`);
    });

    const score = Math.max(0, 100 - errors.length * 30 - warnings.length * 2);
    return { valid: errors.length === 0, errors, warnings, score };
  }

  function validateAll(params) {
    const settings = Object.assign({ kb: null, output: null, documentText: "" }, params || {});
    const kbValidation = validateKnowledgeBase(settings.kb, settings.documentText);
    const outputValidation = validateGeneratedOutput(settings.output, settings.kb, settings.documentText);
    const valid = kbValidation.valid && outputValidation.valid;
    const score = Math.round((kbValidation.score + outputValidation.score) / 2);

    return {
      version: VERSION,
      valid,
      score,
      knowledgeBase: kbValidation,
      output: outputValidation,
      createdAt: new Date().toISOString()
    };
  }

  window.RagGeneralValidatorV1 = {
    VERSION,
    validateKnowledgeBase,
    validateGeneratedOutput,
    validateAll,
    evidenceExistsInDocument,
    containsRawTechnicalText,
    weakOption,
    weakCardBody,
    similarity
  };
})();
