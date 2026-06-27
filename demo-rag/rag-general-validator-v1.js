(function () {
  "use strict";

  const VERSION = "rag-general-validator-v1";

  function clean(text) {
    return String(text || "").replace(/\s+/g, " ").trim();
  }

  function normalizeKey(text) {
    return clean(text).toLowerCase();
  }

  function hasDuplicateKeys(items, keyFn) {
    const seen = new Set();
    const duplicates = [];
    items.forEach((item) => {
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
    return matches / evWords.length >= 0.65;
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

    const score = Math.max(0, 100 - errors.length * 35 - warnings.length * 3);
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

    if (!cards.length) warnings.push("nessuna_card_generata");
    if (!studyQuestions.length) warnings.push("nessuna_domanda_studio_generata");
    if (!test.length) warnings.push("nessun_test_generato");

    const duplicateCards = hasDuplicateKeys(cards, (card) => card.title);
    if (duplicateCards.length) warnings.push(`card_duplicate:${duplicateCards.slice(0, 5).join(",")}`);

    const duplicateQuestions = hasDuplicateKeys(test, (question) => question.question);
    if (duplicateQuestions.length) warnings.push(`domande_test_duplicate:${duplicateQuestions.slice(0, 5).join(",")}`);

    cards.forEach((card) => {
      if (!card.title || !card.body) errors.push(`card_incompleta:${card.id || "senza_id"}`);
      if (card.evidence && !evidenceExistsInDocument(card.evidence, documentText)) warnings.push(`card_non_dimostrata:${card.id || "senza_id"}`);
      if (typeof card.confidence === "number" && card.confidence < 0.45) warnings.push(`card_fiducia_bassa:${card.id || "senza_id"}`);
    });

    studyQuestions.forEach((question) => {
      if (!question.question || !question.answer) errors.push(`domanda_studio_incompleta:${question.id || "senza_id"}`);
      if (question.evidence && !evidenceExistsInDocument(question.evidence, documentText)) warnings.push(`domanda_studio_non_dimostrata:${question.id || "senza_id"}`);
    });

    test.forEach((question) => {
      if (!question.question || !Array.isArray(question.options) || !question.correctAnswer) {
        errors.push(`test_incompleto:${question.id || "senza_id"}`);
        return;
      }
      if (question.options.length !== 4) warnings.push(`opzioni_non_quattro:${question.id || "senza_id"}`);
      if (!question.options.includes(question.correctAnswer)) errors.push(`risposta_corretta_fuori_opzioni:${question.id || "senza_id"}`);
      if (hasDuplicateKeys(question.options, (option) => option).length) warnings.push(`opzioni_duplicate:${question.id || "senza_id"}`);
      if (question.evidence && !evidenceExistsInDocument(question.evidence, documentText)) warnings.push(`test_non_dimostrato:${question.id || "senza_id"}`);
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
    evidenceExistsInDocument
  };
})();
