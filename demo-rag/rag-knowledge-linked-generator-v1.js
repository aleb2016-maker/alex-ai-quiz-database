(function () {
  "use strict";

  const VERSION = "rag-knowledge-linked-generator-v33-final-polish";

  const GENERIC_DISTRACTORS = [
    "Un elemento non indicato dal documento",
    "Una conclusione non dimostrata dal testo",
    "Una risposta simile ma non corretta",
    "Un dettaglio secondario non richiesto"
  ];

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
      .replace(/__([^_]+)__/g, "$1")
      .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1");
  }

  function truncate(text, max) {
    const value = stripMarkdown(text);
    if (value.length <= max) return value;
    return value.slice(0, Math.max(0, max - 1)).replace(/\s+\S*$/, "").trim() + "…";
  }

  function canonical(value) {
    return clean(value)
      .toLowerCase()
      .replace(/\bautenticazione\s+due\s+fattori\b/g, "autenticazione a due fattori")
      .replace(/\bemail\b/g, "e-mail")
      .replace(/\be mail\b/g, "e-mail")
      .replace(/[^a-zà-öø-ÿ0-9\s]/gi, " ")
      .replace(/\b(a|ad|di|del|della|dei|degli|le|la|il|lo|gli|i|un|una|uno)\b/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function uniqueBy(items, keyFn) {
    const seen = new Set();
    const output = [];
    (items || []).forEach((item) => {
      const key = canonical(keyFn(item));
      if (!key) return;
      const nearDuplicate = Array.from(seen).some((oldKey) => {
        if (oldKey === key) return true;
        if (oldKey.length < 8 || key.length < 8) return false;
        return oldKey.startsWith(key) || key.startsWith(oldKey);
      });
      if (nearDuplicate) return;
      seen.add(key);
      output.push(item);
    });
    return output;
  }

  function rawBadText(text) {
    const value = clean(text).toLowerCase();
    if (!value) return true;
    if (/^#/.test(value)) return true;
    if (/\b(problema_soluzione|prima_dopo|appartiene_a|relation_|concept_|fact_)\b/.test(value)) return true;
    if (/\b(fonte di prova per il motore rag|progetto quiz|cartella rag\/documenti|documento rag di test|pensato come manuale tecnico avanzato|distrattore medio)\b/.test(value)) return true;
    if (/^(non|obiettivo|l'obiettivo|lo scopo|documento)$/i.test(value)) return true;
    return false;
  }

  function displayTitle(text, fallback) {
    let value = stripMarkdown(text)
      .replace(/^(il|lo|la|i|gli|le|un|uno|una)\s+/i, "")
      .replace(/^(che cosa|quale|secondo il documento)\s+/i, "")
      .replace(/\bautenticazione\s+due\s+fattori\b/i, "autenticazione a due fattori")
      .replace(/[.:;]+$/g, "")
      .trim();
    if (!value || rawBadText(value)) return fallback || "Punto importante";
    if (value.length > 70) value = value.slice(0, 70).replace(/\s+\S*$/, "").trim();
    return value.charAt(0).toUpperCase() + value.slice(1);
  }

  function readableEvidence(evidence, fallback) {
    const value = stripMarkdown(evidence);
    if (!value || rawBadText(value)) return fallback || "Punto ricavato dal documento caricato.";
    return truncate(value, 230);
  }

  function lowerFirst(text) {
    const value = clean(text);
    if (!value) return value;
    return value.charAt(0).toLowerCase() + value.slice(1);
  }

  function friendlySubject(text) {
    let value = displayTitle(text, "questo punto")
      .replace(/^Password non/i, "password")
      .replace(/^Password sicura/i, "password sicura")
      .replace(/^L'utente/i, "utente")
      .replace(/^La sicurezza informatica/i, "sicurezza informatica")
      .replace(/^Un sistema informatico/i, "sistema informatico")
      .replace(/^Integrità significa che/i, "integrità")
      .replace(/^Disponibilità significa che/i, "disponibilità")
      .replace(/^Usare la stessa password/i, "uso della stessa password")
      .trim();
    if (!value || rawBadText(value)) return "questo punto";
    return value;
  }

  function isExampleOnlyConcept(concept) {
    const rawLabelV331 = clean(concept && concept.label).toLowerCase();
    const rawEvidenceV331 = clean(concept && concept.evidence).toLowerCase();
    const joinedV331 = rawLabelV331 + " " + rawEvidenceV331;

    /*
      RAG_QUALITY_V331_CARD_FILTER
      Filtro didattico sulle card generate.
      Non censura il documento: evita solo che frammenti sporchi diventino card finali.
    */
    if (
      joinedV331.includes("hotel aeroporto") ||
      joinedV331.includes("intercettare traffico") ||
      joinedV331.includes("traffico utenti") ||
      joinedV331.includes("poi verifica sistema") ||
      joinedV331.includes("verifica sistema funzioni") ||
      joinedV331.includes("esempio debole") ||
      joinedV331.includes("esempio più forte") ||
      joinedV331.includes("esempio piu forte") ||
      joinedV331.includes("metodo migliore") ||
      joinedV331.includes("documento rag di test") ||
      joinedV331.includes("distrattore medio")
    ) {
      return true;
    }


    const label = displayTitle(concept && concept.label, "");
    const evidence = clean(concept && concept.evidence).toLowerCase();
    if (!label) return true;
    if (/(hotel\s+aeroporto|intercettare\s+traffico\s+utenti|poi\s+verifica\s+sistema|dati\s+sanitari\s+informazioni\s+riservate\s+clienti)/i.test(label)) return true;
    if (/(ad esempio|per esempio|esempio|tipo)/i.test(evidence) && (concept.importance || 1) <= 2) {
      if (!/(sicurezza informatica|autenticazione|password|password manager|aggiornamenti|e-mail|email|ransomware|integrità|integrita|disponibilità|disponibilita|backup|antivirus|endpoint)/i.test(label)) return true;
    }
    return false;
  }

  function compactOption(text, max) {
    let value = stripMarkdown(text)
      .replace(/^(che|di|da|a|per|con|il|lo|la|i|gli|le|un|uno|una)\s+/i, "")
      .replace(/[.;:]+$/g, "")
      .trim();
    if (!value || rawBadText(value)) return "";
    if (/^(documento rag|esempio debole|esempio più forte|esempio piu forte|pensato come manuale|non riguarda|può dire che|anche se)/i.test(value)) return "";
    if (value.length < 4 || value.length > (max || 70)) return "";
    if (/\.\.\.|…/.test(value)) return "";
    return value.charAt(0).toUpperCase() + value.slice(1);
  }

  function evidenceRef(item) {
    return item && item.evidence ? truncate(item.evidence, 210) : "";
  }

  function isGoodConcept(concept) {
    if (!concept || rawBadText(concept.label)) return false;
    const label = displayTitle(concept.label, "");
    if (!label || label.length < 4 || label.length > 70) return false;
    if (/\b(distrattore|medio|documento rag|manuale tecnico|materiale formativo)\b/i.test(label)) return false;
    return true;
  }

  function isGoodFact(fact) {
    if (!fact) return false;
    const subject = displayTitle(fact.subject, "");
    const object = compactOption(fact.object, 95) || displayTitle(fact.object, "");
    if (!subject || !object) return false;
    if (rawBadText(subject) || rawBadText(object)) return false;
    if (subject.length > 70 || object.length > 95) return false;
    if (/^(non|obiettivo|l'obiettivo)$/i.test(subject)) return false;
    if (/^(non riguarda|esempio debole|esempio più forte|esempio piu forte|può dire che|anche se|documento rag di test)/i.test(subject)) return false;
    if (/documento rag di test|pensato come manuale tecnico|materiale formativo|esempio debole|esempio più forte|esempio piu forte/i.test(subject + " " + object)) return false;
    return true;
  }

  function generateCards(kb, plan) {
    const cardPlan = plan && plan.cards ? plan.cards : { count: 8 };
    const concepts = uniqueBy(kb.concepts || [], (concept) => concept.label)
      .filter(isGoodConcept)
      .filter((concept) => !/^(comportamenti corretti azienda|documento rag|esempio debole|esempio più forte|esempio piu forte)$/i.test(displayTitle(concept.label, "")))
      .filter((concept) => !isExampleOnlyConcept(concept))
      .sort((a, b) => (b.importance || 1) - (a.importance || 1))
      .slice(0, cardPlan.count || 8);

    return concepts.map((concept, index) => {
      const title = displayTitle(concept.label, "Punto importante");
      return {
        id: `card_${index + 1}`,
        type: "concept_card",
        title: `${index + 1}. ${title}`,
        badge: concept.category || "concetto",
        body: readableEvidence(concept.evidence, `${title} è un concetto importante del documento.`),
        iconHint: concept.categoryId || "learning",
        sourceConceptId: concept.id,
        evidence: evidenceRef(concept),
        confidence: concept.confidence || 0.5
      };
    });
  }

  function generateSummary(kb, plan) {
    const topics = (kb.topics || []).filter((topic) => topic.concepts && topic.concepts.length);
    const facts = (kb.facts || []).filter(isGoodFact);
    const summaryType = plan && plan.summary ? plan.summary.type : "riassunto_per_argomenti";
    const title = kb.document && kb.document.title ? kb.document.title : "Documento";
    let cleanTopics = topics.map((topic) => ({
      category: displayTitle(topic.category, "Tema"),
      concepts: uniqueBy((topic.concepts || [])
        .map((item) => displayTitle(item, ""))
        .filter(Boolean)
        .filter((item) => !rawBadText(item))
        .filter((item) => !/(hotel\s+aeroporto|intercettare\s+traffico|distrattore|esempio debole|esempio più forte|metodo migliore)/i.test(item)), (item) => item)
    })).filter((topic) => topic.concepts.length);
    if (cleanTopics.some((topic) => !/^generico$/i.test(topic.category))) {
      cleanTopics = cleanTopics.filter((topic) => !/^generico$/i.test(topic.category));
    }

    const intro = cleanTopics.length
      ? `Il documento "${title}" è organizzato intorno a questi temi principali: ${cleanTopics.slice(0, 3).map((topic) => topic.category).join(", ")}.`
      : `Il documento "${title}" contiene informazioni utili da trasformare in materiale di studio.`;

    const keyPoints = cleanTopics.slice(0, 6).map((topic) => ({
      title: topic.category,
      text: `Concetti principali: ${topic.concepts.slice(0, 5).join(", ")}.`,
      evidence: ""
    })).filter((point) => point.text && !rawBadText(point.text));

    const factPoints = facts.slice(0, 6).map((fact) => ({
      title: displayTitle(fact.subject, "Punto"),
      text: truncate(`${displayTitle(fact.subject, "Questo punto")} ${clean(fact.predicate)} ${stripMarkdown(fact.object)}.`, 180),
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

  function relationLabel(type) {
    return {
      causa: "causa e conseguenza",
      richiede: "requisito",
      evita: "prevenzione",
      protegge: "protezione",
      appartiene_a: "categoria",
      prima_dopo: "ordine",
      problema_soluzione: "problema e soluzione"
    }[type] || "collegamento";
  }

  function cleanRelationQuestion(relation) {
    const from = friendlySubject(relation.from);
    const to = displayTitle(relation.to, "un altro punto del documento");
    const fromLower = from.toLowerCase();
    const toText = lowerFirst(to);
    if (!from || !to || rawBadText(from) || rawBadText(to)) return null;
    if (from.length > 75 || to.length > 90) return null;

    if (/password sicura|password/.test(fromLower)) {
      return {
        question: /non/.test(clean(relation.from).toLowerCase()) ? "Come non devono essere gestite le password?" : "Quali caratteristiche deve avere una password sicura?",
        answer: `${from} richiede ${toText}.`
      };
    }

    if (/utente/.test(fromLower)) {
      return {
        question: "Che cosa deve ricordare l'utente?",
        answer: `L'utente deve ricordare ${toText}.`
      };
    }

    if (/integrità|integrita/.test(fromLower)) {
      return {
        question: "Che cosa significa integrità secondo il documento?",
        answer: `Integrità significa che i dati ${toText}.`
      };
    }

    if (/disponibilità|disponibilita/.test(fromLower)) {
      return {
        question: "Che cosa significa disponibilità secondo il documento?",
        answer: `Disponibilità significa che sistemi, documenti e servizi ${toText}.`
      };
    }

    if (/autenticazione a due fattori|2fa/.test(fromLower)) {
      return {
        question: "A cosa serve l'autenticazione a due fattori?",
        answer: `L'autenticazione a due fattori aggiunge ${toText}.`
      };
    }

    if (/sistema informatico/.test(fromLower)) {
      return {
        question: "Quale rischio riguarda un sistema informatico?",
        answer: `Il sistema informatico può risultare vulnerabile se ${toText}.`
      };
    }

    if (relation.type === "protegge") return {
      question: `Che cosa protegge ${from}?`,
      answer: `${from} protegge ${toText}.`
    };
    if (relation.type === "richiede") return {
      question: `Che cosa richiede ${from}?`,
      answer: `${from} richiede ${toText}.`
    };
    if (relation.type === "evita") return {
      question: `Che cosa aiuta a evitare ${from}?`,
      answer: `${from} aiuta a evitare ${toText}.`
    };
    if (relation.type === "problema_soluzione") return {
      question: `Quale problema o soluzione riguarda ${from}?`,
      answer: `${from} riguarda ${toText}.`
    };
    return {
      question: `Quale collegamento emerge tra ${from} e ${to}?`,
      answer: `${from} è collegato a ${toText}.`
    };
  }

  function questionFromRelation(relation, index) {
    const friendly = cleanRelationQuestion(relation);
    if (!friendly) return null;
    return {
      id: `study_question_${index + 1}`,
      question: truncate(friendly.question, 140),
      answer: truncate(friendly.answer, 230),
      relationType: relation.type,
      relationLabel: relationLabel(relation.type),
      evidence: relation.evidence,
      confidence: relation.confidence || 0.5
    };
  }

  function questionFromConcept(concept, index) {
    const label = displayTitle(concept.label, "questo concetto");
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

  function studyTopic(item) {
    return questionTopic(item && item.question ? item.question : "");
  }

  function isStrongStudyQuestion(item) {
    if (!item || !item.question || !item.answer) return false;
    if (rawBadText(item.question) || rawBadText(item.answer)) return false;
    if (/(Che cosa richiede (Password non|L'utente)|Può dire|Anche se|Esempio debole|Esempio più forte|Metodo migliore)/i.test(item.question)) return false;

    /*
      RAG_QUALITY_V332_STUDY_RELATION_FILTER
      Filtro didattico sulle domande studio.
      Non modifica il documento: evita solo domande finali poco naturali.
    */
    const joinedStudyV332 = clean(`${item.question} ${item.answer}`).toLowerCase();

    if (
      /quale collegamento emerge tra/i.test(joinedStudyV332) ||
      /account verr[aà] bloccato/i.test(joinedStudyV332) ||
      /un pacco/i.test(joinedStudyV332) ||
      /pacco richiede/i.test(joinedStudyV332) ||
      /prima si valuta/i.test(joinedStudyV332) ||
      /poi si distribuisce/i.test(joinedStudyV332) ||
      /si verifica che il sistema/i.test(joinedStudyV332) ||
      /quando una correzione viene pubblicata/i.test(joinedStudyV332)
    ) {
      return false;
    }

    return true;
  }

  function generateStudyQuestions(kb, plan) {
    const questionPlan = plan && plan.studyQuestions ? plan.studyQuestions : { count: 8 };
    const relationQuestions = uniqueBy(kb.relations || [], (relation) => `${relation.type}|${relation.from}|${relation.to}`)
      .map(questionFromRelation)
      .filter(Boolean)
      .filter(isStrongStudyQuestion);

    const relationQuestionList = limitRepeatedTopics(uniqueBy(relationQuestions, (item) => item.question), 1)
      .slice(0, questionPlan.count || 8);

    if (relationQuestionList.length >= 4) return relationQuestionList;

    const conceptQuestions = uniqueBy(kb.concepts || [], (concept) => concept.label)
      .filter(isGoodConcept)
      .map(questionFromConcept)
      .slice(0, questionPlan.count || 8);

    return limitRepeatedTopics(relationQuestionList.concat(conceptQuestions), 1).slice(0, questionPlan.count || 8);
  }

  function makeDistractors(correct, pool, needed) {
    const correctKey = canonical(correct);
    const candidates = (pool || [])
      .map((item) => compactOption(item, 65))
      .filter(Boolean)
      .filter((item) => canonical(item) !== correctKey)
      .filter((item) => {
        const cWords = new Set(correctKey.split(/\s+/).filter((word) => word.length >= 4));
        const words = canonical(item).split(/\s+/).filter((word) => word.length >= 4);
        if (!cWords.size || !words.length) return true;
        const overlap = words.filter((word) => cWords.has(word)).length / Math.max(1, Math.min(words.length, cWords.size));
        return overlap < 0.65;
      });

    const unique = [];
    const seen = new Set();
    candidates.forEach((item) => {
      const key = canonical(item);
      if (!key || seen.has(key)) return;
      seen.add(key);
      unique.push(item);
    });

    return unique.concat(GENERIC_DISTRACTORS).slice(0, needed);
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


  function cleanQuestionSubject(subject) {
    let value = displayTitle(subject, "questo punto")
      .replace(/^Integrità significa che\s+/i, "integrità")
      .replace(/^Disponibilità significa che\s+/i, "disponibilità")
      .replace(/^Password sicura\s+/i, "password sicura")
      .replace(/^Password non\s+/i, "password")
      .replace(/^Metodo migliore\s*/i, "password manager")
      .replace(/^Usare la stessa password\s*/i, "uso della stessa password")
      .replace(/^La sicurezza informatica\s+/i, "sicurezza informatica")
      .replace(/^Un sistema informatico\s+/i, "sistema informatico")
      .trim();
    if (!value || rawBadText(value)) return "questo punto";
    return value.charAt(0).toUpperCase() + value.slice(1);
  }

  function questionTopic(question) {
    const value = clean(question).toLowerCase();
    if (/password|password manager|stessa password/.test(value)) return "password";
    if (/autenticazione|2fa/.test(value)) return "autenticazione";
    if (/sicurezza informatica/.test(value)) return "sicurezza";
    if (/aggiornament/.test(value)) return "aggiornamenti";
    if (/integrità|integrita/.test(value)) return "integrita";
    if (/disponibilità|disponibilita/.test(value)) return "disponibilita";
    return value.replace(/[^a-zà-öø-ÿ0-9\s]/gi, " ").split(/\s+/).slice(0, 3).join(" ");
  }

  function limitRepeatedTopics(questions, maxPerTopic) {
    const counts = new Map();
    const output = [];
    (questions || []).forEach((question) => {
      const topic = questionTopic(question.question);
      const current = counts.get(topic) || 0;
      const dynamicMax = topic === "password" ? 1 : (maxPerTopic || 2);
      if (current >= dynamicMax) return;
      counts.set(topic, current + 1);
      output.push(question);
    });
    return output;
  }

  function isStrongQuestion(question) {
    const value = clean(question).toLowerCase();
    if (!value || value.length < 18 || value.length > 150) return false;
    if (/che cosa dice il documento su\s+(non|l'obiettivo|obiettivo|esempio debole|esempio più forte|esempio piu forte|metodo migliore)/i.test(value)) return false;
    if (/(Esempio debole|Esempio più forte|Metodo migliore|Che cosa richiede L'utente|Che cosa richiede Password non)/i.test(question)) return false;
    if (/\b(documento rag di test|esempio debole|esempio più forte|esempio piu forte|pensato come manuale tecnico|distrattore medio)\b/i.test(value)) return false;
    if (/\?\?/.test(value)) return false;
    return true;
  }

  function questionForFact(fact) {
    const subject = cleanQuestionSubject(fact.subject);
    const object = compactOption(fact.object, 80) || displayTitle(fact.object, "");
    const predicate = clean(fact.predicate).toLowerCase();
    const subjectLower = subject.toLowerCase();

    if (/sicurezza informatica/.test(subjectLower)) return "Che cos'è la sicurezza informatica secondo il documento?";
    if (/integrità/.test(subjectLower)) return "Che cosa significa integrità secondo il documento?";
    if (/disponibilità/.test(subjectLower)) return "Che cosa significa disponibilità secondo il documento?";
    if (/uso della stessa password/.test(subjectLower)) return "Perché non bisogna usare la stessa password su più siti?";
    if (/utente/.test(subjectLower)) return "Che cosa deve ricordare l'utente?";
    if (/password manager/.test(subjectLower)) return "A cosa serve un password manager?";
    if (/password/.test(subjectLower)) return "Quale caratteristica deve avere una password sicura?";
    if (/aggiornament/.test(subjectLower)) return "Perché sono importanti gli aggiornamenti software?";
    if (/autenticazione a due fattori|2fa/.test(subjectLower)) return "A cosa serve l'autenticazione a due fattori?";

    if (/^(è|sono|rappresenta|indica|significa)$/.test(predicate)) return `Quale affermazione è corretta su ${subject}?`;
    if (/^(deve|devono|richiede)$/.test(predicate)) return `Che cosa richiede ${subject}?`;
    if (/^(serve)$/.test(predicate)) return `A cosa serve ${subject}?`;
    if (/^(protegge)$/.test(predicate)) return `Che cosa protegge ${subject}?`;
    if (/^(evita|riduce|previene)$/.test(predicate)) return `Che cosa aiuta a evitare ${subject}?`;
    if (/^(usa|utilizza)$/.test(predicate)) return `Che cosa usa ${subject}?`;
    return `Quale affermazione è corretta su ${subject}?`;
  }

  function generateTest(kb, plan) {
    const testPlan = plan && plan.test ? plan.test : { count: 8, optionsPerQuestion: 4 };
    const facts = uniqueBy(kb.facts || [], (fact) => fact.evidence)
      .filter(isGoodFact)
      .slice(0, testPlan.count || 8);

    const conceptPool = uniqueBy(kb.concepts || [], (concept) => concept.label)
      .filter(isGoodConcept)
      .map((concept) => displayTitle(concept.label, ""));
    const objectPool = (kb.facts || []).filter(isGoodFact).map((fact) => fact.object);
    const pool = conceptPool.concat(objectPool);

    const generated = facts.map((fact, index) => {
      const correct = compactOption(fact.object, 75) || displayTitle(fact.object, "");
      if (!correct) return null;
      const distractors = makeDistractors(correct, pool, (testPlan.optionsPerQuestion || 4) - 1);
      let options = uniqueBy([correct].concat(distractors), (item) => item);
      if (options.length < 4) {
        options = uniqueBy(options.concat(GENERIC_DISTRACTORS), (item) => item);
      }
      options = shuffleStable(options, index).slice(0, 4);
      if (!options.some((item) => canonical(item) === canonical(correct))) {
        options[0] = correct;
        options = shuffleStable(uniqueBy(options, (item) => item), index + 19).slice(0, 4);
      }

      return {
        id: `test_question_${index + 1}`,
        question: truncate(questionForFact(fact), 135),
        options,
        correctAnswer: correct,
        explanation: readableEvidence(fact.evidence, "Risposta ricavata dal documento."),
        sourceFactId: fact.id,
        evidence: fact.evidence,
        confidence: fact.confidence || 0.5
      };
    }).filter(Boolean).filter((question) => isStrongQuestion(question.question) && question.options.length === 4);

    return limitRepeatedTopics(uniqueBy(generated, (question) => question.question), 1).slice(0, testPlan.count || 8);
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
    generateAll,
    displayTitle,
    compactOption
  };
})();


/*
  RAG_QUALITY_V333_FINAL_TEXT_POLISH
  Micro-rifinitura finale output didattico.
  Non censura contenuti e non blocca documenti.
  Ripulisce solo etichette/card/domande già generate.
*/
(function () {
  "use strict";

  function cleanFinalTextV333(value) {
    return String(value || "")
      .replace(/\bricordare\s+ricordare\b/gi, "ricordare")
      .replace(/\brichiede\s+Serve a\b/gi, "serve a")
      .replace(/\bchiede\s+Serve a\b/gi, "serve a")
      .replace(/\bChe cosa richiede Serve a\b/gi, "A cosa serve")
      .replace(/\bGenerico\b/g, "Sicurezza")
      .replace(/\s+/g, " ")
      .trim();
  }

  function polishNodeV333(node) {
    if (!node || node.__ragQualityV333Done) return;

    node.querySelectorAll("*").forEach((el) => {
      if (!el || !el.childNodes) return;

      el.childNodes.forEach((child) => {
        if (child.nodeType === Node.TEXT_NODE) {
          const before = child.nodeValue;
          const after = cleanFinalTextV333(before);

          if (before !== after) {
            child.nodeValue = after;
          }
        }
      });
    });

    node.__ragQualityV333Done = true;
  }

  function runPolishV333() {
    document
      .querySelectorAll(".rag-card, .card, .output-card, section, article")
      .forEach(polishNodeV333);
  }

  window.RagQualityV333FinalTextPolish = {
    cleanFinalTextV333,
    polishNodeV333,
    runPolishV333
  };

  document.addEventListener("DOMContentLoaded", () => {
    runPolishV333();
    setTimeout(runPolishV333, 300);
    setTimeout(runPolishV333, 1000);
  });

  document.addEventListener("click", () => {
    setTimeout(runPolishV333, 300);
    setTimeout(runPolishV333, 1000);
  });
})();

