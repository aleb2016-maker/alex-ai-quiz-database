(function () {
  "use strict";

  const VERSION = "rag-didactic-planner-v1";

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function docStats(kb) {
    const stats = kb && kb.document && kb.document.metadata && kb.document.metadata.stats
      ? kb.document.metadata.stats
      : {};
    return {
      chars: stats.chars || 0,
      words: stats.words || 0,
      sentences: stats.sentences || 0
    };
  }

  function chooseSummaryType(kb) {
    const stats = docStats(kb);
    if (stats.words >= 2500) return "riassunto_strutturato_lungo";
    if ((kb.topics || []).length >= 4) return "riassunto_per_argomenti";
    return "riassunto_breve_guidato";
  }

  function chooseGraphicStyle(kb) {
    const topics = kb.topics || [];
    const categories = topics.map((topic) => String(topic.category || "").toLowerCase());
    const joined = categories.join(" ");

    if (/sicurezza|lavoro|azienda/.test(joined)) {
      return { id: "professionale_scuro", label: "Professionale scuro", iconSet: "security_business", density: "media" };
    }
    if (/sport/.test(joined)) {
      return { id: "sport_dinamico", label: "Sport dinamico", iconSet: "sport", density: "alta" };
    }
    if (/curriculum/.test(joined)) {
      return { id: "cv_pulito", label: "CV pulito", iconSet: "profile", density: "media" };
    }
    if (/poesia|storia/.test(joined)) {
      return { id: "narrativo", label: "Narrativo", iconSet: "story", density: "bassa" };
    }
    return { id: "studio_generico", label: "Studio generico", iconSet: "learning", density: "media" };
  }

  function planCards(kb) {
    const conceptCount = (kb.concepts || []).length;
    const stats = docStats(kb);
    const base = stats.words > 1800 ? 10 : stats.words > 800 ? 8 : 5;
    return {
      count: clamp(Math.min(conceptCount || base, base), 3, 12),
      source: "concetti",
      strategy: "una_card_per_concetto_importante",
      includeEvidence: true
    };
  }

  function planStudyQuestions(kb) {
    const relationCount = (kb.relations || []).length;
    const conceptCount = (kb.concepts || []).length;
    return {
      count: clamp(Math.max(4, Math.min(10, relationCount + Math.ceil(conceptCount / 3))), 4, 12),
      source: relationCount ? "relazioni" : "concetti",
      strategy: relationCount ? "domande_sui_legami" : "domande_sui_concetti",
      includeModelAnswer: true
    };
  }

  function planTest(kb) {
    const factCount = (kb.facts || []).length;
    const conceptCount = (kb.concepts || []).length;
    return {
      count: clamp(Math.max(4, Math.min(10, factCount || conceptCount)), 4, 12),
      source: factCount >= 3 ? "fatti" : "concetti",
      distractorSource: "categorie_e_concetti_vicini",
      optionsPerQuestion: 4,
      requireEvidence: true
    };
  }

  function planPdf(kb) {
    const cardPlan = planCards(kb);
    return {
      layout: cardPlan.count > 8 ? "2_card_per_pagina" : "1_o_2_card_per_pagina",
      avoidCutText: true,
      includeTitle: true,
      includeEvidence: false,
      professionalClean: true
    };
  }

  function buildPlan(kb) {
    return {
      version: VERSION,
      createdAt: new Date().toISOString(),
      documentTitle: kb && kb.document ? kb.document.title : "Documento utente",
      confidence: kb ? kb.confidence : 0,
      cards: planCards(kb || {}),
      summary: {
        type: chooseSummaryType(kb || {}),
        source: "argomenti_principali",
        includeBullets: true,
        includeKeyPoints: true
      },
      studyQuestions: planStudyQuestions(kb || {}),
      test: planTest(kb || {}),
      distractors: {
        strategy: "categorie_vicine_non_corrette",
        avoidAbsurdOptions: true,
        avoidDuplicates: true
      },
      graphicStyle: chooseGraphicStyle(kb || {}),
      pdf: planPdf(kb || {})
    };
  }

  window.RagDidacticPlannerV1 = {
    VERSION,
    buildPlan,
    planCards,
    planStudyQuestions,
    planTest,
    chooseGraphicStyle,
    chooseSummaryType
  };
})();
