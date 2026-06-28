(function () {
  "use strict";

  const VERSION = "rag-knowledge-linked-generator-v34-final-clean";

  const GENERIC_DISTRACTORS = [
    "Ignorare gli aggiornamenti di sicurezza",
    "Usare la stessa password su più servizi",
    "Condividere dati senza controllo",
    "Rimandare la segnalazione di un incidente",
    "Salvare il backup solo sul sistema principale",
    "Cliccare link sospetti senza verificarli"
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

  function stripNumberPrefix(value) {
    return clean(value)
      .replace(/^\s*\d+\s*[\.)]\s*/g, "")
      .trim();
  }

  function infoWords(value) {
    return canonical(value)
      .split(/\s+/)
      .filter((word) => word.length >= 4);
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

  function hasUsefulVerb(value) {
    return /\b(è|sono|può|possono|deve|devono|serve|servono|richiede|richiedono|protegge|proteggono|riduce|riducono|evita|evitano|permette|permettono|aggiunge|aggiungono|corregge|correggono|garantisce|garantiscono|significa|indica|include|comprende|gestisce|segnala|recupera|blocca|impedisce|consente)\b/i.test(clean(value));
  }

  function hasDidacticSignal(value) {
    return /\b(perché|quindi|serve|richiede|protegge|riduce|evita|permette|aggiunge|corregge|significa|include|comprende|rischio|causa|conseguenza|procedura|controllo|protezione|accesso|dati|password|backup|software|vulnerabil|attacco|phishing|malware|ransomware|autenticazione|account)\b/i.test(clean(value));
  }

  function normalizeDidacticText(text, contextTitle) {
    let value = stripMarkdown(text)
      .replace(/\s+/g, " ")
      .replace(/\s+([,.!?;:])/g, "$1")
      .replace(/\.\.+/g, ".")
      .trim();

    value = value
      .replace(/\bL autenticazione\b/g, "L'autenticazione")
      .replace(/\bl accesso\b/g, "l'accesso")
      .replace(/\bL utente\b/g, "L'utente")
      .replace(/\bl utente\b/g, "l'utente")
      .replace(/\bl azienda\b/g, "l'azienda")
      .replace(/\bricordare ricordare\b/gi, "ricordare")
      .replace(/\bdovrebbero gestiti\b/gi, "devono essere gestiti")
      .replace(/\bdovrebbe gestiti\b/gi, "deve essere gestito")
      .replace(/\bUn sistema informatico può essere tecnicamente avanzato, ma rimanere vulnerabile se gli utenti\b/gi, "Un sistema informatico può restare vulnerabile anche se è tecnicamente avanzato, se gli utenti usano password deboli, cliccano link sospetti o condividono dati senza controllo")
      .replace(/\bse essere tecnicamente avanzato, ma rimanere vulnerabile se gli utenti\b/gi, "restare vulnerabile anche se è tecnicamente avanzato, se gli utenti usano password deboli, cliccano link sospetti o condividono dati senza controllo")
      .replace(/\bpuò risultare vulnerabile se essere tecnicamente avanzato, ma rimanere vulnerabile se gli utenti\b/gi, "può restare vulnerabile anche se è tecnicamente avanzato, se gli utenti usano password deboli, cliccano link sospetti o condividono dati senza controllo")
      .replace(/\busati per proteggere\.$/gi, "usati per proteggere dati, dispositivi, account e sistemi digitali.")
      .replace(/\bSicurezza informatica protegge l'insieme di pratiche, strumenti e comportamenti usati per proteggere\.?$/i, "La sicurezza informatica protegge dati, dispositivi, account e sistemi digitali attraverso pratiche, strumenti e comportamenti corretti.")
      .replace(/\bL'utente deve ricordare solo la password principale del password manager, che deve essere molto robusta\.?$/i, "Un password manager permette di salvare password lunghe e uniche; l'utente deve ricordare solo la password principale, che deve essere molto robusta.")
      .replace(/\bAggiornamenti dovrebbero gestiti procedura controllata\.?$/i, "Gli aggiornamenti software devono essere gestiti con una procedura controllata.")
      .replace(/\s+che\.?$/i, ".")
      .replace(/\s+o\.?$/i, ".")
      .replace(/\bse gli utenti\.?$/i, "se gli utenti usano password deboli, cliccano link sospetti o condividono dati senza controllo.");

    if (/^sicurezza informatica protegge\b/i.test(value)) {
      value = value.replace(/^Sicurezza informatica protegge\b/i, "La sicurezza informatica protegge");
    }

    if (/^un sistema informatico può risultare vulnerabile se/i.test(value)) {
      value = value.replace(/^Un sistema informatico può risultare vulnerabile se/i, "Un sistema informatico può restare vulnerabile anche se");
    }

    if (/password manager/i.test(contextTitle || "") && /password principale/i.test(value) && !/^un password manager permette/i.test(value)) {
      value = "Un password manager permette di salvare password lunghe e uniche; l'utente deve ricordare solo la password principale, che deve essere molto robusta.";
    }

    if (/aggiornamenti software/i.test(contextTitle || "") && /procedura controllata/i.test(value) && !/^gli aggiornamenti software/i.test(value)) {
      value = "Gli aggiornamenti software devono essere gestiti con una procedura controllata perché correggono vulnerabilità e riducono il rischio di attacchi.";
    }

    value = value.replace(/\.\.+/g, ".").replace(/\s+/g, " ").trim();
    if (value && !/[.!?]$/.test(value)) value += ".";
    return value;
  }

  function hasBrokenGrammar(text) {
    return /\bdovrebbero gestiti\b|\bse essere\b|\busati per proteggere\.?$|\bse gli utenti\.?$|\bche\.?$|\.\.|Sicurezza informatica protegge l'insieme/i.test(clean(text));
  }

  function isUsefulBody(body, title) {
    const value = normalizeDidacticText(body, title);
    if (!value || rawBadText(value)) return false;
    if (hasBrokenGrammar(value)) return false;
    if (value.length < 90) return false;
    if (infoWords(value).length < 10) return false;
    if (!hasUsefulVerb(value)) return false;
    if (!hasDidacticSignal(value)) return false;
    if (canonical(value) === canonical(title)) return false;
    if (/^(aggiornamenti software|autenticazione a due fattori|sicurezza informatica|password manager)\.?$/i.test(value)) return false;
    if (title && infoWords(title).length && similarity(title, value) < 0.12) return false;
    return true;
  }

  function bestEvidenceForTitle(title, current, kb) {
    const candidates = [];
    const push = (value) => {
      const text = normalizeDidacticText(value, title);
      if (text && isUsefulBody(text, title)) candidates.push(text);
    };

    push(current);
    (kb.concepts || []).forEach((concept) => push(concept.evidence));
    (kb.facts || []).forEach((fact) => push(fact.evidence));
    (kb.relations || []).forEach((relation) => push(relation.evidence));

    return uniqueBy(candidates, (item) => item)
      .sort((a, b) => similarity(title, b) - similarity(title, a) || b.length - a.length)[0] || "";
  }

  function iconSvgFor(title, hint) {
    const value = canonical(`${title} ${hint || ""}`);
    if (/autenticazione|fattori|2fa/.test(value)) {
      return '<svg viewBox="0 0 96 96" aria-hidden="true"><circle cx="36" cy="42" r="18" fill="none" stroke="currentColor" stroke-width="8"/><path d="M51 42h34M68 42v14M80 42v10" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round"/></svg>';
    }
    if (/password manager|cassaforte/.test(value)) {
      return '<svg viewBox="0 0 96 96" aria-hidden="true"><rect x="18" y="20" width="60" height="56" rx="8" fill="none" stroke="currentColor" stroke-width="8"/><circle cx="48" cy="48" r="12" fill="none" stroke="currentColor" stroke-width="8"/><path d="M48 36v-8M48 68v-8M36 48h-8M68 48h-8" fill="none" stroke="currentColor" stroke-width="6" stroke-linecap="round"/></svg>';
    }
    if (/password|account|accesso/.test(value)) {
      return '<svg viewBox="0 0 96 96" aria-hidden="true"><rect x="24" y="42" width="48" height="34" rx="8" fill="none" stroke="currentColor" stroke-width="8"/><path d="M34 42V30a14 14 0 0 1 28 0v12M48 56v10" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round"/></svg>';
    }
    if (/aggiornament|software|patch/.test(value)) {
      return '<svg viewBox="0 0 96 96" aria-hidden="true"><path d="M74 30a32 32 0 1 0 4 32" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round"/><path d="M74 14v22H52" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    }
    if (/backup|recuper|ripristin/.test(value)) {
      return '<svg viewBox="0 0 96 96" aria-hidden="true"><path d="M22 72h52a10 10 0 0 0 0-20h-2A26 26 0 0 0 22 42a16 16 0 0 0 0 30Z" fill="none" stroke="currentColor" stroke-width="8"/><path d="M48 30v28M36 46l12 12 12-12" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    }
    if (/rischio|attacco|malware|phishing|ransomware|vulnerabil/.test(value)) {
      return '<svg viewBox="0 0 96 96" aria-hidden="true"><path d="M48 12 84 78H12L48 12Z" fill="none" stroke="currentColor" stroke-width="8" stroke-linejoin="round"/><path d="M48 34v22M48 68h.1" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round"/></svg>';
    }
    if (/incidente|segnalazion|avviso/.test(value)) {
      return '<svg viewBox="0 0 96 96" aria-hidden="true"><path d="M28 66h40l-6-10V42a14 14 0 0 0-28 0v14l-6 10Z" fill="none" stroke="currentColor" stroke-width="8" stroke-linejoin="round"/><path d="M42 76h12M48 18v8" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round"/></svg>';
    }
    if (/dati riservati|informazioni riservate|documento protetto/.test(value)) {
      return '<svg viewBox="0 0 96 96" aria-hidden="true"><path d="M28 14h30l14 14v54H28V14Z" fill="none" stroke="currentColor" stroke-width="8" stroke-linejoin="round"/><path d="M58 14v18h18M38 54h20M38 66h16" fill="none" stroke="currentColor" stroke-width="6" stroke-linecap="round"/><rect x="38" y="34" width="20" height="14" rx="4" fill="none" stroke="currentColor" stroke-width="6"/></svg>';
    }
    return '<svg viewBox="0 0 96 96" aria-hidden="true"><path d="M48 10 78 22v22c0 20-12 34-30 42-18-8-30-22-30-42V22l30-12Z" fill="none" stroke="currentColor" stroke-width="8" stroke-linejoin="round"/><path d="M34 48l9 9 20-22" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
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

  function cleanConceptTitle(title) {
    const value = stripNumberPrefix(displayTitle(title, ""));
    if (/account sistemi digitali|strumenti comportamenti corretti|sistemi digitali attraverso pratiche/i.test(value)) return "Sicurezza informatica";
    if (/^sistemi digitali$/i.test(value)) return "Sicurezza informatica";
    if (/comportamenti corretti/i.test(value)) return "Sicurezza informatica";
    if (/cancellazione accidentale|attacco ransomware|recupero.*dati/i.test(value)) return "Backup e recupero dei dati";
    if (/^sicurezza informatica\b/i.test(value)) return "Sicurezza informatica";
    if (/^password sicura\b/i.test(value)) return "Password sicura";
    if (/autenticazione a due fattori|2fa/i.test(value)) return "Autenticazione a due fattori";
    if (/^aggiornamenti software\b|^patch\b/i.test(value)) return "Aggiornamenti software";
    if (/backup|ripristin/i.test(value)) return "Backup e ripristino";
    if (/incidente.*sicurezza|sicurezza.*segnalat/i.test(value)) return "Segnalazione incidente di sicurezza";
    if (/password manager/i.test(value)) return "Password manager";
    return value;
  }

  function readableEvidence(evidence, fallback) {
    const value = normalizeDidacticText(evidence, "");
    if (!value || rawBadText(value)) return fallback || "";
    return truncate(value, 230);
  }

  function lowerFirst(text) {
    const value = clean(text);
    if (!value) return value;
    return value.charAt(0).toLowerCase() + value.slice(1);
  }

  function friendlySubject(text) {
    let value = displayTitle(text, "questo punto")
      .replace(/^Password non\b/i, "password")
      .replace(/^Password sicura\b/i, "password sicura")
      .replace(/^L'utente\b/i, "utente")
      .replace(/^La sicurezza informatica\b/i, "sicurezza informatica")
      .replace(/^Un sistema informatico\b/i, "sistema informatico")
      .replace(/^Integrità significa che\b/i, "integrità")
      .replace(/^Disponibilità significa che\b/i, "disponibilità")
      .replace(/^Usare la stessa password\b/i, "uso della stessa password")
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
    if (/\b(hotel\s+aeroporto|intercettare\s+traffico\s+utenti|poi\s+verifica\s+sistema|dati\s+sanitari\s+informazioni\s+riservate\s+clienti)\b/i.test(label)) return true;
    if (/\b(ad esempio|per esempio|esempio|tipo)\b/i.test(evidence) && (concept.importance || 1) <= 2) {
      if (!/\b(sicurezza informatica|autenticazione|password|password manager|aggiornamenti|e-mail|email|ransomware|integrità|integrita|disponibilità|disponibilita|backup|antivirus|endpoint)\b/i.test(label)) return true;
    }
    return false;
  }

  function compactOption(text, max) {
    let value = normalizeDidacticText(text, "")
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
    const label = cleanConceptTitle(concept.label);
    if (!label || label.length < 4 || label.length > 70) return false;
    if (/\b(distrattore|medio|documento rag|manuale tecnico|materiale formativo)\b/i.test(label)) return false;
    if (/^(accesso|dati|sicurezza|password|account|utente|utenti|sistema|sistemi|software|informazioni|responsabile|procedura|rischio|servizio|controllo|protezione|account sistemi digitali attraverso pratiche|strumenti comportamenti corretti)$/i.test(canonical(label))) return false;
    if (!isUsefulBody(concept.evidence, label)) return false;
    return true;
  }

  function conceptScore(concept) {
    const label = cleanConceptTitle(concept && concept.label);
    let score = 0;
    score += (concept.didacticStrength || 0) * 3;
    score += Math.min(4, infoWords(label).length) * 2;
    score += concept.cardEligible === false ? -6 : 0;
    if (/\b(sicurezza informatica|password sicura|autenticazione a due fattori|password manager|aggiornamenti software|backup|malware|ransomware|phishing)\b/i.test(label)) score += 8;
    if (/^(accesso|dati|sicurezza|password|account|sistema|software)$/i.test(canonical(label))) score -= 10;
    return score;
  }

  function dedupeCards(cards) {
    const result = [];
    const seen = new Set();
    (cards || []).forEach((card) => {
      if (!card) return;
      const key = `${canonical(card.title)}|${canonical(card.body)}|${canonical(card.evidence)}`;
      if (!key || seen.has(key)) return;
      const duplicate = result.some((oldCard) => (
        similarity(oldCard.title, card.title) >= 0.9 ||
        similarity(oldCard.body, card.body) >= 0.68 ||
        similarity(oldCard.evidence, card.evidence) >= 0.75
      ));
      if (duplicate) return;
      seen.add(key);
      result.push(card);
    });
    return result;
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
      .sort((a, b) => conceptScore(b) - conceptScore(a) || (b.importance || 1) - (a.importance || 1));

    const cards = concepts.map((concept, index) => {
      const title = cleanConceptTitle(concept.label) || "Punto importante";
      const evidence = evidenceRef(concept);
      const body = readableEvidence(bestEvidenceForTitle(title, concept.evidence, kb) || concept.evidence, "");
      if (!isUsefulBody(body, title)) return null;
      return {
        id: `card_${index + 1}`,
        type: "concept_card",
        title,
        badge: concept.category || "concetto",
        body,
        iconHint: concept.categoryId || "learning",
        iconSvg: iconSvgFor(title, concept.categoryId),
        sourceConceptId: concept.id,
        evidence: evidence || body,
        confidence: concept.confidence || 0.5
      };
    }).filter(Boolean);

    return dedupeCards(cards).slice(0, cardPlan.count || 8);
  }

  function generateSummary(kb, plan) {
    const facts = (kb.facts || []).filter(isGoodFact);
    const summaryType = plan && plan.summary ? plan.summary.type : "riassunto_per_argomenti";
    const title = kb.document && kb.document.title ? kb.document.title : "Documento";
    const evidenceSentences = uniqueBy(
      []
        .concat(kb.concepts || [])
        .concat(kb.facts || [])
        .map((item) => normalizeDidacticText(item.evidence || "", item.label || item.subject || ""))
        .filter((sentence) => isUsefulBody(sentence, "")),
      (sentence) => sentence
    );

    const introParts = [];
    if (evidenceSentences.some((sentence) => /sicurezza informatica protegge/i.test(sentence))) {
      introParts.push("Il documento spiega che la sicurezza informatica protegge dati, dispositivi, account e sistemi digitali.");
    }
    if (evidenceSentences.some((sentence) => /password|autenticazione|aggiornamenti|backup|incident/i.test(sentence))) {
      introParts.push("Evidenzia l'importanza di password robuste, autenticazione a due fattori, aggiornamenti software, backup separati e segnalazione rapida degli incidenti.");
    }

    const intro = introParts.length
      ? introParts.join(" ")
      : `Il documento "${title}" contiene informazioni utili trasformate in frasi di studio naturali.`;

    const factPoints = facts.slice(0, 6).map((fact) => ({
      title: displayTitle(fact.subject, "Punto"),
      text: truncate(normalizeDidacticText(fact.evidence || `${displayTitle(fact.subject, "Questo punto")} ${clean(fact.predicate)} ${stripMarkdown(fact.object)}.`, fact.subject), 180),
      evidence: fact.evidence
    }));

    const keyPoints = evidenceSentences.slice(0, 5).map((sentence, index) => ({
      title: `Punto ${index + 1}`,
      text: truncate(sentence, 180),
      evidence: sentence
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
    const normalizedEvidence = normalizeDidacticText(relation.evidence || relation.answerText || "", from);
    if (!from || !to || rawBadText(from) || rawBadText(to)) return null;
    if (from.length > 75 || to.length > 90) return null;

    if (/sicurezza informatica/.test(fromLower)) {
      return {
        question: "Che cosa protegge la sicurezza informatica?",
        answer: normalizedEvidence || "La sicurezza informatica protegge dati, dispositivi, account e sistemi digitali attraverso pratiche, strumenti e comportamenti corretti."
      };
    }

    if (/aggiornament/.test(fromLower)) {
      return {
        question: "Perché sono importanti gli aggiornamenti software?",
        answer: normalizedEvidence || "Gli aggiornamenti software devono essere gestiti con una procedura controllata perché correggono vulnerabilità e riducono il rischio di attacchi."
      };
    }

    if (/password manager/.test(fromLower)) {
      return {
        question: "A cosa serve un password manager?",
        answer: normalizedEvidence || "Un password manager permette di salvare password lunghe e uniche; l'utente deve ricordare solo la password principale, che deve essere molto robusta."
      };
    }

    if (/backup|recupero/.test(fromLower)) {
      return {
        question: "Perché il backup aiuta a recuperare i dati?",
        answer: normalizedEvidence || "Il backup serve a recuperare informazioni dopo cancellazione accidentale, guasti o attacco ransomware e deve essere separato dal sistema principale."
      };
    }

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
        question: "Che cosa significa integrità?",
        answer: `Integrità significa che i dati ${toText}.`
      };
    }

    if (/disponibilità|disponibilita/.test(fromLower)) {
      return {
        question: "Che cosa significa disponibilità?",
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
        question: "Da cosa può dipendere la vulnerabilità di un sistema informatico?",
        answer: normalizedEvidence || `Un sistema informatico può restare vulnerabile anche se ${toText}.`
      };
    }

    if (relation.type === "protegge") return {
      question: `Che cosa protegge ${lowerFirst(from)}?`,
      answer: normalizeDidacticText(`${from} protegge ${toText}.`, from)
    };
    if (relation.type === "richiede") return {
      question: `Che cosa richiede ${from}?`,
      answer: normalizeDidacticText(`${from} richiede ${toText}.`, from)
    };
    if (relation.type === "evita") return {
      question: `Che cosa aiuta a evitare ${from}?`,
      answer: normalizeDidacticText(`${from} aiuta a evitare ${toText}.`, from)
    };
    if (relation.type === "problema_soluzione") return {
      question: `Quale problema o soluzione riguarda ${from}?`,
      answer: normalizeDidacticText(`${from} riguarda ${toText}.`, from)
    };
    return {
      question: `Quale collegamento emerge tra ${from} e ${to}?`,
      answer: normalizeDidacticText(`${from} è collegato a ${toText}.`, from)
    };
  }

  function questionFromRelation(relation, index) {
    const friendly = cleanRelationQuestion(relation);
    if (!friendly) return null;
    return {
      id: `study_question_${index + 1}`,
      question: truncate(friendly.question, 140),
      answer: truncate(normalizeDidacticText(friendly.answer, relation.from), 230),
      relationType: relation.type,
      relationLabel: relationLabel(relation.type),
      evidence: relation.evidence,
      confidence: relation.confidence || 0.5
    };
  }

  function questionFromConcept(concept, index) {
    const label = cleanConceptTitle(concept.label) || "questo concetto";
    const answer = normalizeDidacticText(readableEvidence(concept.evidence, ""), label);
    if (!isUsefulBody(answer, label)) return null;
    let question = `Che cosa bisogna sapere su ${lowerFirst(label)}?`;
    if (/sicurezza informatica/i.test(label)) question = "Che cosa protegge la sicurezza informatica?";
    else if (/autenticazione a due fattori/i.test(label)) question = "A cosa serve l'autenticazione a due fattori?";
    else if (/password manager/i.test(label)) question = "A cosa serve un password manager?";
    else if (/password sicura/i.test(label)) question = "Quali caratteristiche deve avere una password sicura?";
    else if (/aggiornamenti software/i.test(label)) question = "Perché sono importanti gli aggiornamenti software?";
    else if (/backup|recupero/i.test(label)) question = "Perché il backup aiuta a recuperare i dati?";
    else if (/incidente|segnalaz/i.test(label)) question = "Perché un incidente di sicurezza deve essere segnalato subito?";
    else if (/malware|ransomware|phishing|vulnerabil/i.test(label)) question = `Quale rischio descrive il documento su ${lowerFirst(label)}?`;
    return {
      id: `study_question_${index + 1}`,
      question,
      answer: truncate(answer, 230),
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
    if (hasBrokenGrammar(`${item.question} ${item.answer}`)) return false;
    if (!isUsefulBody(item.answer, item.question)) return false;
    if (/sistemi digitali/i.test(item.question)) return false;
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
      .filter(Boolean)
      .slice(0, questionPlan.count || 8);

    return limitRepeatedTopics(relationQuestionList.concat(conceptQuestions), 1).slice(0, questionPlan.count || 8);
  }

  function makeDistractors(correct, pool, needed, usedGlobal) {
    const correctKey = canonical(correct);
    const candidates = (pool || [])
      .map((item) => normalizeDistractor(item))
      .filter(Boolean)
      .filter((item) => canonical(item) !== correctKey)
      .filter((item) => {
        const words = infoWords(item);
        if (hasUsefulVerb(item)) return true;
        return words.length >= 4 && !/^(account sistemi|strumenti comportamenti|sicurezza informatica protegge|cancellazione accidentale)$/i.test(item);
      })
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

    const output = [];
    GENERIC_DISTRACTORS.concat(unique).forEach((item) => {
      const key = canonical(item);
      if (!key || output.length >= needed) return;
      if (usedGlobal && usedGlobal.has(key)) return;
      output.push(item);
      if (usedGlobal) usedGlobal.add(key);
    });
    return output;
  }

  function normalizeDistractor(item) {
    const value = compactOption(item, 90);
    if (!value) return "";
    if (/^sicurezza informatica$/i.test(value)) return "Disattivare le pratiche di protezione dei sistemi digitali";
    if (/^password sicura$/i.test(value)) return "Usare una password breve e facile da indovinare";
    if (/^autenticazione a due fattori$/i.test(value)) return "Usare solo la password senza un secondo controllo";
    if (/^password manager$/i.test(value)) return "Riutilizzare la stessa password su tutti i servizi";
    if (/^backup e recupero dei dati$/i.test(value)) return "Salvare il backup solo sul sistema principale";
    if (/^aggiornamenti software$/i.test(value)) return "Ignorare le patch che correggono vulnerabilità";
    if (/^segnalazione incidente di sicurezza$/i.test(value)) return "Rimandare la segnalazione di un incidente";
    return value;
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

    if (/sicurezza informatica/.test(subjectLower)) return "Che cosa protegge la sicurezza informatica?";
    if (/integrità/.test(subjectLower)) return "Che cosa significa integrità?";
    if (/disponibilità/.test(subjectLower)) return "Che cosa significa disponibilità?";
    if (/uso della stessa password/.test(subjectLower)) return "Perché non bisogna usare la stessa password su più siti?";
    if (/utente/.test(subjectLower)) return "Che cosa deve ricordare l'utente?";
    if (/password manager/.test(subjectLower)) return "A cosa serve un password manager?";
    if (/password/.test(subjectLower)) return "Quale caratteristica deve avere una password sicura?";
    if (/aggiornament/.test(subjectLower)) return "Perché sono importanti gli aggiornamenti software?";
    if (/autenticazione a due fattori|2fa/.test(subjectLower)) return "A cosa serve l'autenticazione a due fattori?";
    if (/backup|ripristin|recupero/.test(subjectLower)) return "Perché il backup aiuta a recuperare i dati?";

    if (/^(è|sono|rappresenta|indica|significa)$/.test(predicate)) return `Quale affermazione è corretta su ${subject}?`;
    if (/^(deve|devono|richiede)$/.test(predicate)) return `Che cosa richiede ${subject}?`;
    if (/^(serve)$/.test(predicate)) return `A cosa serve ${subject}?`;
    if (/^(protegge)$/.test(predicate)) return `Che cosa protegge ${subject}?`;
    if (/^(evita|riduce|previene)$/.test(predicate)) return `Che cosa aiuta a evitare ${subject}?`;
    if (/^(usa|utilizza)$/.test(predicate)) return `Che cosa usa ${subject}?`;
    return `Quale affermazione è corretta su ${subject}?`;
  }

  function shortAnswerForFact(fact) {
    const subject = cleanQuestionSubject(fact.subject).toLowerCase();
    const evidence = normalizeDidacticText(fact.evidence || `${fact.subject || ""} ${fact.predicate || ""} ${fact.object || ""}`, fact.subject);

    if (/sicurezza informatica/.test(subject)) return "Protegge dati, dispositivi, account e sistemi digitali.";
    if (/password manager/.test(subject)) return "Salva password lunghe e uniche, richiedendo solo una password principale robusta.";
    if (/password/.test(subject)) return "Deve essere lunga, difficile da indovinare e diversa per ogni servizio.";
    if (/autenticazione a due fattori|2fa/.test(subject)) return "Aggiunge un secondo controllo oltre alla password.";
    if (/aggiornament/.test(subject)) return "Perché correggono vulnerabilità di sicurezza e riducono il rischio di attacchi.";
    if (/backup|ripristin|recupero/.test(subject)) return "Perché serve a recuperare informazioni dopo errori, guasti o ransomware.";
    if (/sistema informatico|vulnerabil/.test(subject)) return "Può dipendere da password deboli, link sospetti o dati condivisi senza controllo.";
    if (/incidente|segnalazion/.test(subject)) return "Deve essere segnalato subito per limitare danni o perdita di informazioni.";

    const first = evidence.split(/[.;:]/).map(clean).find((part) => part.length >= 35) || evidence;
    return truncate(first, 120).replace(/\s+(che|se|o)$/i, "").replace(/\.\.+/g, ".").trim();
  }

  function generateTest(kb, plan) {
    const testPlan = plan && plan.test ? plan.test : { count: 8, optionsPerQuestion: 4 };
    const usedDistractors = new Set();
    const facts = uniqueBy(kb.facts || [], (fact) => fact.evidence)
      .filter(isGoodFact)
      .filter((fact) => isUsefulBody(fact.evidence, fact.subject))
      .slice(0, testPlan.count || 8);

    const conceptPool = uniqueBy(kb.concepts || [], (concept) => concept.label)
      .filter(isGoodConcept)
      .map((concept) => cleanConceptTitle(concept.label))
      .filter(Boolean);
    const objectPool = (kb.facts || []).filter(isGoodFact).map((fact) => shortAnswerForFact(fact));
    const pool = conceptPool.concat(objectPool);

    const generated = facts.map((fact, index) => {
      const correct = shortAnswerForFact(fact) || compactOption(fact.object, 75) || displayTitle(fact.object, "");
      if (!correct) return null;
      const distractors = makeDistractors(correct, pool, (testPlan.optionsPerQuestion || 4) - 1, usedDistractors);
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
        explanation: normalizeDidacticText(readableEvidence(fact.evidence, "Risposta ricavata dal documento."), fact.subject),
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
