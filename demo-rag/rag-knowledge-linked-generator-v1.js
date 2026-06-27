(function () {
  "use strict";

  const VERSION = "rag-knowledge-linked-generator-v1";

  function clean(text) {
    return String(text || "").replace(/\s+/g, " ").trim();
  }

  function truncate(text, max) {
    const value = clean(text);
    if (value.length <= max) return value;
    return value.slice(0, Math.max(0, max - 1)).trim() + "…";
  }

  function uniqueBy(items, keyFn) {
    const seen = new Set();
    const output = [];
    items.forEach((item) => {
      const key = keyFn(item);
      if (!key || seen.has(key)) return;
      seen.add(key);
      output.push(item);
    });
    return output;
  }

  function evidenceRef(item) {
    return item && item.evidence ? truncate(item.evidence, 220) : "";
  }

  function generateCards(kb, plan) {
    const cardPlan = plan && plan.cards ? plan.cards : { count: 6 };
    const concepts = uniqueBy(kb.concepts || [], (concept) => clean(concept.label).toLowerCase())
      .sort((a, b) => (b.importance || 1) - (a.importance || 1))
      .slice(0, cardPlan.count);

    return concepts.map((concept, index) => ({
      id: `card_${index + 1}`,
      type: "concept_card",
      title: `${index + 1}. ${concept.label}`,
      badge: concept.category || "concetto",
      body: truncate(concept.evidence || `Concetto importante: ${concept.label}.`, 260),
      iconHint: concept.categoryId || "learning",
      sourceConceptId: concept.id,
      evidence: evidenceRef(concept),
      confidence: concept.confidence || 0.5
    }));
  }

  function generateSummary(kb, plan) {
    const topics = kb.topics || [];
    const facts = kb.facts || [];
    const summaryType = plan && plan.summary ? plan.summary.type : "riassunto_per_argomenti";

    const title = kb.document && kb.document.title ? kb.document.title : "Documento";
    const intro = topics.length
      ? `Il documento "${title}" ruota soprattutto intorno a ${topics.slice(0, 3).map((topic) => topic.category).join(", ")}.`
      : `Il documento "${title}" contiene informazioni da organizzare in punti di studio.`;

    const keyPoints = topics.slice(0, 6).map((topic) => ({
      title: topic.category,
      text: topic.concepts && topic.concepts.length
        ? `Concetti principali: ${topic.concepts.join(", ")}.`
        : truncate(topic.evidence, 180),
      evidence: topic.evidence || ""
    }));

    const factPoints = facts.slice(0, 6).map((fact) => ({
      title: clean(fact.subject),
      text: `${clean(fact.subject)} ${clean(fact.predicate)} ${clean(fact.object)}.`,
      evidence: fact.evidence
    }));

    return {
      id: "summary_1",
      type: summaryType,
      title: `Riassunto - ${title}`,
      intro,
      keyPoints: keyPoints.length ? keyPoints : factPoints,
      confidence: kb.confidence || 0
    };
  }

  function questionFromRelation(relation, index) {
    const typeLabel = {
      causa: "Quale rapporto di causa emerge nel documento?",
      richiede: "Che cosa richiede questo punto secondo il documento?",
      evita: "Che cosa aiuta a evitare questo elemento?",
      protegge: "Che cosa protegge questo elemento?",
      appartiene_a: "A quale insieme o categoria appartiene questo elemento?",
      prima_dopo: "Quale ordine prima/dopo emerge dal testo?",
      problema_soluzione: "Quale problema o soluzione viene indicato?"
    }[relation.type] || "Quale relazione emerge dal documento?";

    return {
      id: `study_question_${index + 1}`,
      question: `${typeLabel} (${clean(relation.from)})`,
      answer: truncate(`${clean(relation.from)} → ${relation.type} → ${clean(relation.to)}.`, 260),
      relationType: relation.type,
      evidence: relation.evidence,
      confidence: relation.confidence || 0.5
    };
  }

  function questionFromConcept(concept, index) {
    return {
      id: `study_question_${index + 1}`,
      question: `Che cosa bisogna ricordare su ${concept.label}?`,
      answer: truncate(concept.evidence || `${concept.label} è un concetto importante del documento.`, 260),
      relationType: "concetto",
      evidence: concept.evidence,
      confidence: concept.confidence || 0.5
    };
  }

  function generateStudyQuestions(kb, plan) {
    const questionPlan = plan && plan.studyQuestions ? plan.studyQuestions : { count: 8 };
    const relations = uniqueBy(kb.relations || [], (relation) => `${relation.type}|${relation.from}|${relation.to}`.toLowerCase())
      .slice(0, questionPlan.count);

    if (relations.length >= 3) {
      return relations.map(questionFromRelation);
    }

    return uniqueBy(kb.concepts || [], (concept) => clean(concept.label).toLowerCase())
      .slice(0, questionPlan.count)
      .map(questionFromConcept);
  }

  function makeDistractors(correct, pool, needed) {
    const normalizedCorrect = clean(correct).toLowerCase();
    const candidates = pool
      .map((item) => clean(item))
      .filter((item) => item.length >= 3)
      .filter((item) => item.toLowerCase() !== normalizedCorrect);

    const unique = [];
    const seen = new Set();
    candidates.forEach((item) => {
      const key = item.toLowerCase();
      if (seen.has(key)) return;
      seen.add(key);
      unique.push(item);
    });

    const fallback = [
      "Un dettaglio non indicato dal documento",
      "Una conseguenza non dimostrata dal testo",
      "Un concetto vicino ma non corretto"
    ];

    return unique.concat(fallback).slice(0, needed);
  }

  function shuffleStable(items, seed) {
    const copy = items.slice();
    for (let i = copy.length - 1; i > 0; i -= 1) {
      const j = Math.abs(Math.sin((seed + 1) * (i + 3)) * 10000) % (i + 1);
      const index = Math.floor(j);
      const tmp = copy[i];
      copy[i] = copy[index];
      copy[index] = tmp;
    }
    return copy;
  }

  function generateTest(kb, plan) {
    const testPlan = plan && plan.test ? plan.test : { count: 6, optionsPerQuestion: 4 };
    const facts = uniqueBy(kb.facts || [], (fact) => clean(fact.evidence).toLowerCase())
      .filter((fact) => clean(fact.subject).length > 0 && clean(fact.object).length > 0)
      .slice(0, testPlan.count);

    const conceptPool = (kb.concepts || []).map((concept) => concept.label);
    const objectPool = (kb.facts || []).map((fact) => fact.object);
    const pool = conceptPool.concat(objectPool);

    return facts.map((fact, index) => {
      const correct = truncate(fact.object, 120);
      const distractors = makeDistractors(correct, pool, (testPlan.optionsPerQuestion || 4) - 1);
      const options = shuffleStable([correct].concat(distractors), index);

      return {
        id: `test_question_${index + 1}`,
        question: `Secondo il documento, che cosa ${clean(fact.predicate)} ${clean(fact.subject)}?`,
        options,
        correctAnswer: correct,
        explanation: truncate(fact.evidence, 260),
        sourceFactId: fact.id,
        evidence: fact.evidence,
        confidence: fact.confidence || 0.5
      };
    });
  }

  function generateAll(kb, plan) {
    return {
      version: VERSION,
      createdAt: new Date().toISOString(),
      documentTitle: kb && kb.document ? kb.document.title : "Documento utente",
      cards: generateCards(kb || {}, plan || {}),
      summary: generateSummary(kb || {}, plan || {}),
      studyQuestions: generateStudyQuestions(kb || {}, plan || {}),
      test: generateTest(kb || {}, plan || {})
    };
  }

  window.RagKnowledgeLinkedGeneratorV1 = {
    VERSION,
    generateCards,
    generateSummary,
    generateStudyQuestions,
    generateTest,
    generateAll
  };
})();
