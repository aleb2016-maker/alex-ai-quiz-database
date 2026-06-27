(function () {
  "use strict";

  const VERSION = "rag-knowledge-linked-generator-v2-quality";

  function clean(text) {
    return String(text || "")
      .replace(/\u00A0/g, " ")
      .replace(/[“”]/g, '"')
      .replace(/[‘’]/g, "'")
      .replace(/\s+/g, " ")
      .trim();
  }

  function stripMarkdown(text) {
    return clean(text)
      .replace(/^#{1,6}\s*/, "")
      .replace(/^[-*+]\s+/, "")
      .replace(/`([^`]+)`/g, "$1")
      .replace(/\*\*([^*]+)\*\*/g, "$1")
      .replace(/__([^_]+)__/g, "$1");
  }

  function truncate(text, max) {
    const value = stripMarkdown(text);
    if (value.length <= max) return value;
    return value.slice(0, Math.max(0, max - 1)).replace(/\s+\S*$/, "").trim() + "…";
  }

  function uniqueBy(items, keyFn) {
    const seen = new Set();
    const output = [];
    (items || []).forEach((item) => {
      const key = clean(keyFn(item)).toLowerCase();
      if (!key || seen.has(key)) return;
      seen.add(key);
      output.push(item);
    });
    return output;
  }

  function evidenceRef(item) {
    return item && item.evidence ? truncate(item.evidence, 220) : "";
  }

  function badUserText(text) {
    const value = clean(text).toLowerCase();
    if (!value) return true;
    if (/^#/.test(value)) return true;
    if (/\b(problema_soluzione|prima_dopo|appartiene_a|relation_|concept_|fact_)\b/.test(value)) return true;
    if (/\b(secondo il documento, che cosa afferma #|che cosa afferma #|# documento)\b/.test(value)) return true;
    if (/\b(fonte di prova per il motore rag|progetto quiz|cartella rag\/documenti)\b/.test(value)) return true;
    return false;
  }

  function safeTitle(text, fallback) {
    const value = stripMarkdown(text)
      .replace(/^(il|lo|la|i|gli|le|un|uno|una)\s+/i, "")
      .replace(/[.:;]+$/g, "")
      .trim();
    if (!value || badUserText(value)) return fallback || "Punto importante";
    return truncate(value, 64);
  }

  function readableEvidence(evidence, fallback) {
    const value = stripMarkdown(evidence);
    if (!value || badUserText(value)) return fallback || "Punto ricavato dal documento caricato.";
    return truncate(value, 260);
  }

  function compactAnswer(text, max) {
    let value = stripMarkdown(text)
      .replace(/^(che|di|da|a|per|con)\s+/i, "")
      .replace(/[.;:]+$/g, "")
      .trim();
    if (!value || badUserText(value)) value = "Un punto indicato dal documento";
    return truncate(value, max || 95);
  }

  function generateCards(kb, plan) {
    const cardPlan = plan && plan.cards ? plan.cards : { count: 8 };
    const concepts = uniqueBy(kb.concepts || [], (concept) => concept.label)
      .filter((concept) => !badUserText(concept.label))
      .sort((a, b) => (b.importance || 1) - (a.importance || 1))
      .slice(0, cardPlan.count || 8);

    return concepts.map((concept, index) => ({
      id: `card_${index + 1}`,
      type: "concept_card",
      title: `${index + 1}. ${safeTitle(concept.label, "Punto importante")}`,
      badge: concept.category || "concetto",
      body: readableEvidence(concept.evidence, `${concept.label} è un concetto importante del documento.`),
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
    const cleanTopics = topics.filter((topic) => topic.concepts && topic.concepts.length);
    const intro = cleanTopics.length
      ? `Il documento "${title}" è organizzato intorno a questi temi principali: ${cleanTopics.slice(0, 3).map((topic) => topic.category).join(", ")}.`
      : `Il documento "${title}" contiene informazioni utili da trasformare in materiale di studio.`;

    const keyPoints = cleanTopics.slice(0, 6).map((topic) => ({
      title: safeTitle(topic.category, "Tema"),
      text: topic.concepts && topic.concepts.length
        ? `Concetti principali: ${topic.concepts.filter((item) => !badUserText(item)).slice(0, 5).join(", ")}.`
        : readableEvidence(topic.evidence, "Tema ricavato dal documento."),
      evidence: topic.evidence || ""
    })).filter((point) => point.text && !badUserText(point.text));

    const factPoints = facts.slice(0, 6).map((fact) => ({
      title: safeTitle(fact.subject, "Punto"),
      text: truncate(`${clean(fact.subject)} ${clean(fact.predicate)} ${clean(fact.object)}.`, 190),
      evidence: fact.evidence
    })).filter((point) => !badUserText(point.title) && !badUserText(point.text));

    return {
      id: "summary_1",
      type: summaryType,
      title: `Riassunto - ${title}`,
      intro,
      keyPoints: keyPoints.length ? keyPoints : factPoints,
      confidence: kb.confidence || 0
    };
  }

  function relationLabel(type) {
    return {
      causa: "rapporto causa/conseguenza",
      richiede: "requisito",
      evita: "prevenzione",
      protegge: "protezione",
      appartiene_a: "categoria",
      prima_dopo: "ordine temporale",
      problema_soluzione: "problema e soluzione"
    }[type] || "relazione";
  }

  function questionFromRelation(relation, index) {
    const question = relation.questionHint && !badUserText(relation.questionHint)
      ? relation.questionHint
      : `Quale ${relationLabel(relation.type)} emerge su ${safeTitle(relation.from, "questo punto")}?`;

    const answer = relation.answerText && !badUserText(relation.answerText)
      ? relation.answerText
      : `${safeTitle(relation.from, "Questo punto")} è collegato a ${compactAnswer(relation.to, 140)}.`;

    return {
      id: `study_question_${index + 1}`,
      question: truncate(question, 150),
      answer: truncate(answer, 260),
      relationType: relation.type,
      relationLabel: relationLabel(relation.type),
      evidence: relation.evidence,
      confidence: relation.confidence || 0.5
    };
  }

  function questionFromConcept(concept, index) {
    const label = safeTitle(concept.label, "questo concetto");
    return {
      id: `study_question_${index + 1}`,
      question: `Che cosa bisogna ricordare su ${label}?`,
      answer: readableEvidence(concept.evidence, `${label} è un concetto importante del documento.`),
      relationType: "concetto",
      relationLabel: "concetto",
      evidence: concept.evidence,
      confidence: concept.confidence || 0.5
    };
  }

  function generateStudyQuestions(kb, plan) {
    const questionPlan = plan && plan.studyQuestions ? plan.studyQuestions : { count: 8 };
    const relations = uniqueBy(kb.relations || [], (relation) => `${relation.type}|${relation.from}|${relation.to}`)
      .filter((relation) => !badUserText(relation.from) && !badUserText(relation.to))
      .slice(0, questionPlan.count || 8);

    if (relations.length >= 3) {
      return relations.map(questionFromRelation).filter((item) => !badUserText(item.question) && !badUserText(item.answer));
    }

    return uniqueBy(kb.concepts || [], (concept) => concept.label)
      .filter((concept) => !badUserText(concept.label))
      .slice(0, questionPlan.count || 8)
      .map(questionFromConcept);
  }

  function optionCandidate(value) {
    const item = compactAnswer(value, 90);
    if (!item || badUserText(item)) return "";
    if (item.length < 4 || item.length > 95) return "";
    if (/^(il|lo|la|i|gli|le|un|uno|una)$/i.test(item)) return "";
    return item;
  }

  function makeDistractors(correct, pool, needed) {
    const normalizedCorrect = clean(correct).toLowerCase();
    const candidates = (pool || [])
      .map(optionCandidate)
      .filter(Boolean)
      .filter((item) => item.toLowerCase() !== normalizedCorrect)
      .filter((item) => {
        const cWords = new Set(normalizedCorrect.split(/\s+/).filter((word) => word.length >= 4));
        const words = item.toLowerCase().split(/\s+/).filter((word) => word.length >= 4);
        if (!cWords.size || !words.length) return true;
        const overlap = words.filter((word) => cWords.has(word)).length / Math.max(1, Math.min(words.length, cWords.size));
        return overlap < 0.75;
      });

    const unique = [];
    const seen = new Set();
    candidates.forEach((item) => {
      const key = item.toLowerCase();
      if (seen.has(key)) return;
      seen.add(key);
      unique.push(item);
    });

    const fallback = [
      "Un elemento non indicato dal documento",
      "Una conclusione non dimostrata dal testo",
      "Un concetto simile ma non corretto"
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

  function questionForFact(fact) {
    const subject = safeTitle(fact.subject, "questo punto");
    const predicate = clean(fact.predicate).toLowerCase();

    if (/^(è|sono|rappresenta|indica|significa)$/.test(predicate)) {
      return `Che cosa dice il documento su ${subject}?`;
    }
    if (/^(deve|devono|richiede)$/.test(predicate)) {
      return `Che cosa richiede ${subject} secondo il documento?`;
    }
    if (/^(serve)$/.test(predicate)) {
      return `A cosa serve ${subject} secondo il documento?`;
    }
    if (/^(protegge)$/.test(predicate)) {
      return `Che cosa protegge ${subject}?`;
    }
    if (/^(evita|riduce|previene)$/.test(predicate)) {
      return `Che cosa aiuta a evitare o ridurre ${subject}?`;
    }
    if (/^(usa|utilizza)$/.test(predicate)) {
      return `Che cosa usa ${subject} secondo il documento?`;
    }
    return `Quale affermazione è corretta su ${subject}?`;
  }

  function generateTest(kb, plan) {
    const testPlan = plan && plan.test ? plan.test : { count: 8, optionsPerQuestion: 4 };
    const facts = uniqueBy(kb.facts || [], (fact) => fact.evidence)
      .filter((fact) => !badUserText(fact.subject) && !badUserText(fact.object))
      .slice(0, testPlan.count || 8);

    const conceptPool = (kb.concepts || []).map((concept) => concept.label);
    const objectPool = (kb.facts || []).map((fact) => fact.object);
    const relationPool = (kb.relations || []).map((relation) => relation.to);
    const pool = conceptPool.concat(objectPool).concat(relationPool);

    return facts.map((fact, index) => {
      const correct = optionCandidate(fact.object) || compactAnswer(fact.evidence, 90);
      const distractors = makeDistractors(correct, pool, (testPlan.optionsPerQuestion || 4) - 1);
      const options = shuffleStable([correct].concat(distractors), index).slice(0, 4);

      return {
        id: `test_question_${index + 1}`,
        question: truncate(questionForFact(fact), 150),
        options,
        correctAnswer: correct,
        explanation: readableEvidence(fact.evidence, "Risposta ricavata dal documento."),
        sourceFactId: fact.id,
        evidence: fact.evidence,
        confidence: fact.confidence || 0.5
      };
    }).filter((question) => !badUserText(question.question) && question.options.length === 4);
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
