#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patch chirurgica RAG V2A30 - riassunti profile-aware.
Eseguire dalla root del repo: /Users/alessandrobarbarossa/alex-ai-workspace
Modifica solo:
- demo-rag/universal-document-learning-engine.js
- runtime/web/rag-large-document-progressive-summary-v2.js
Crea backup automatici in reports/fix_riassunto_profile_aware_v2a30/backups/
"""
from __future__ import annotations

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
UNIVERSAL = ROOT / "demo-rag" / "universal-document-learning-engine.js"
PROGRESSIVE = ROOT / "runtime" / "web" / "rag-large-document-progressive-summary-v2.js"
REPORT_DIR = ROOT / "reports" / "fix_riassunto_profile_aware_v2a30"
BACKUP_DIR = REPORT_DIR / "backups"


def die(msg: str) -> None:
    print(f"ERRORE: {msg}", file=sys.stderr)
    sys.exit(1)


def backup(path: Path) -> None:
    if not path.exists():
        die(f"File non trovato: {path}")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"{path.name}.{stamp}.bak"
    shutil.copy2(path, dest)
    print(f"Backup creato: {dest}")


def replace_regex(text: str, pattern: str, replacement: str, label: str) -> str:
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.S | re.M)
    if count != 1:
        die(f"Sostituzione fallita o ambigua: {label} (count={count})")
    return new_text


UNIVERSAL_REPLACEMENT = r'''  const STOPWORD_RIASSUNTO_V2A30 = new Set([
    "questo", "questa", "questi", "queste", "quello", "quella", "quelli", "quelle",
    "sono", "essere", "avere", "viene", "vengono", "molto", "anche", "dopo", "prima",
    "ogni", "come", "quando", "dove", "perche", "perché", "testo", "documento", "materiale",
    "parte", "parti", "tema", "temi", "aspetto", "aspetti", "informazioni", "importanti",
    "tratta", "riguarda", "evidenzia", "contenuto", "contenuti", "principale", "principali"
  ]);

  const CONCETTI_PROFILO_RIASSUNTO_V2A30 = {
    "theme-sport": [
      "allenamento", "resistenza", "corsa", "esercizi", "gambe", "addome", "schiena",
      "progressi", "fatica", "recupero", "forza", "mobilità", "mobilita", "programma", "sessione"
    ],
    "theme-poetry": [
      "poesia", "sera silenziosa", "silenzio", "vento", "foglie", "cielo", "nostalgia",
      "ricordo", "natura", "calma", "conforto", "immagini", "emozione", "voce poetica"
    ],
    "theme-story": [
      "storia", "racconto", "protagonista", "personaggi", "ambientazione", "scena",
      "conflitto", "scelta", "viaggio", "sviluppo", "finale", "trama"
    ],
    "theme-cv": [
      "profilo", "esperienza", "competenze", "formazione", "obiettivo", "progetti",
      "lavoro", "ruolo", "mansioni", "tecnologie", "github"
    ],
    "theme-personal": [
      "identità", "identita", "dati", "residenza", "richiesta", "modulo", "certificato",
      "scadenza", "documenti", "firma", "codice fiscale"
    ],
    "theme-business": [
      "obiettivo", "processo", "responsabilità", "responsabilita", "rischi", "controlli",
      "procedure", "workflow", "cliente", "metriche", "attività", "attivita"
    ],
    "theme-hobby": [
      "idea", "progetto", "obiettivo", "strumenti", "fasi", "risultato", "miglioramenti",
      "creativo", "realizzare", "costruire", "tempo libero"
    ]
  };

  function paroleSignificativeRiassuntoV2A30(testo, limite) {
    const parole = normalizzaTesto(testo)
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .match(/[a-z0-9]{4,}/g) || [];

    const frequenze = new Map();

    parole.forEach(function (parola) {
      if (STOPWORD_RIASSUNTO_V2A30.has(parola)) return;
      frequenze.set(parola, (frequenze.get(parola) || 0) + 1);
    });

    return Array.from(frequenze.entries())
      .sort(function (a, b) { return b[1] - a[1]; })
      .slice(0, limite || 8)
      .map(function (entry) { return entry[0]; });
  }

  function concettiProfiloRiassuntoV2A30(testo, profilo) {
    const classe = profilo && profilo.classe ? profilo.classe : "";
    const lista = CONCETTI_PROFILO_RIASSUNTO_V2A30[classe] || [];
    const lower = normalizzaTesto(testo).toLowerCase();
    const trovati = [];

    lista.forEach(function (concetto) {
      if (lower.includes(String(concetto).toLowerCase()) && !trovati.includes(concetto)) {
        trovati.push(concetto);
      }
    });

    if (trovati.length) {
      return trovati.slice(0, 7);
    }

    return paroleSignificativeRiassuntoV2A30(testo, 7);
  }

  function chiudiFraseRiassuntoV2A30(testo) {
    let pulito = correggiSpaziPunteggiaturaV35G(normalizzaTesto(testo));

    pulito = pulito.replace(/\b(e|o|ma|che|di|a|da|in|con|su|per|tra|fra|del|della|dello|dei|degli|delle)$/i, "").trim();

    if (pulito && !/[.!?]$/.test(pulito)) {
      pulito += ".";
    }

    return pulito;
  }

  function deduplicaFrasiRiassuntoV2A30(frasi, limite) {
    const viste = new Set();
    const output = [];

    (frasi || []).forEach(function (frase) {
      const pulita = chiudiFraseRiassuntoV2A30(frase);
      const firma = pulita
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/[^a-z0-9 ]+/g, " ")
        .replace(/\s+/g, " ")
        .split(" ")
        .slice(0, 20)
        .join(" ");

      if (!pulita || pulita.length < 24 || viste.has(firma)) return;

      viste.add(firma);
      output.push(pulita);
    });

    return typeof limite === "number" ? output.slice(0, limite) : output;
  }

  function unisciConcettiRiassuntoV2A30(concetti) {
    const lista = (concetti || []).filter(Boolean).slice(0, 6);

    if (!lista.length) return "i contenuti centrali del testo";
    if (lista.length === 1) return lista[0];
    if (lista.length === 2) return lista[0] + " e " + lista[1];

    return lista.slice(0, -1).join(", ") + " e " + lista[lista.length - 1];
  }

  function fraseAperturaRiassuntoV2A30(profilo, concetti) {
    const classe = profilo && profilo.classe ? profilo.classe : "";
    const focus = unisciConcettiRiassuntoV2A30(concetti);

    if (classe === "theme-sport") {
      return "Il testo descrive un percorso di allenamento centrato su " + focus + ".";
    }

    if (classe === "theme-poetry") {
      return "Il testo ha un tono poetico e mette al centro " + focus + ".";
    }

    if (classe === "theme-story") {
      return "Il testo presenta una struttura narrativa centrata su " + focus + ".";
    }

    if (classe === "theme-cv") {
      return "Il testo riassume un profilo professionale centrato su " + focus + ".";
    }

    if (classe === "theme-personal") {
      return "Il testo raccoglie informazioni personali o amministrative legate a " + focus + ".";
    }

    if (classe === "theme-business") {
      return "Il testo sintetizza un contenuto operativo centrato su " + focus + ".";
    }

    if (classe === "theme-hobby") {
      return "Il testo descrive un progetto o un'attività creativa centrata su " + focus + ".";
    }

    return "Il testo mette in evidenza " + focus + ".";
  }

  function costruisciSintesiBreveRiassuntoV2A30(testo, profilo, frasi) {
    const frasiPulite = deduplicaFrasiRiassuntoV2A30(frasi, 4);
    const concetti = concettiProfiloRiassuntoV2A30(testo, profilo);
    const apertura = fraseAperturaRiassuntoV2A30(profilo, concetti);
    const dettagli = frasiPulite.join(" ");

    if (!dettagli) {
      return apertura;
    }

    if (dettagli.toLowerCase().includes(apertura.toLowerCase())) {
      return chiudiFraseRiassuntoV2A30(dettagli);
    }

    return chiudiFraseRiassuntoV2A30(apertura + " " + dettagli);
  }

  function creaParagrafiRiassunto(testo, profilo) {
    const pulito = normalizzaTesto(testo);
    const frasi = deduplicaFrasiRiassuntoV2A30(frasiRiassuntoEsteso(pulito), 80);
    const sezioni = profilo.sezioni || [];

    if (!pulito) {
      return [{
        titolo: "Sintesi generale",
        testo: "Il documento non contiene abbastanza testo per generare un riassunto."
      }];
    }

    if (pulito.length <= 1800 || frasi.length <= 5) {
      return [{
        titolo: "Sintesi essenziale",
        testo: costruisciSintesiBreveRiassuntoV2A30(pulito, profilo, frasi)
      }];
    }

    const usate = new Set();
    const paragrafi = [];
    const apertura = costruisciSintesiBreveRiassuntoV2A30(pulito, profilo, frasi.slice(0, 6));

    paragrafi.push({
      titolo: "Messaggio chiave",
      testo: apertura
    });

    sezioni.slice(0, 4).forEach(function (sezione) {
      const parole = parolePerSezioneRiassunto(profilo, sezione);
      let blocco = prendiFrasi(frasi, parole, usate, 4);

      if (blocco.length < 2) {
        blocco = blocco.concat(prendiExtra(frasi, usate, 3 - blocco.length));
      }

      blocco = deduplicaFrasiRiassuntoV2A30(blocco, 4);

      if (blocco.length) {
        paragrafi.push({
          titolo: sezione.titolo || "Sezione rilevante",
          testo: chiudiFraseRiassuntoV2A30(blocco.join(" "))
        });
      }
    });

    if (paragrafi.length <= 1) {
      const migliori = deduplicaFrasiRiassuntoV2A30(frasi.slice(0, 8), 6);
      paragrafi.push({
        titolo: "Sintesi generale",
        testo: chiudiFraseRiassuntoV2A30(migliori.join(" ") || apertura)
      });
    }

    return paragrafi
      .map(correggiOutputTestualeV35G)
      .filter(function (paragrafo) {
        return paragrafo.testo && paragrafo.testo.trim().length > 0;
      });
  }
'''

PROFILE_TOPICS_INSERT = r'''

  const PROFILE_TOPICS_V2A30 = {
    business: TOPICS,
    cybersecurity: TOPICS,
    sport: [
      {
        id: "allenamento",
        label: "programma di allenamento",
        words: ["allenamento", "programma", "scheda", "sessione", "routine", "esercizi"],
        sentence: "Il documento descrive un programma di allenamento organizzato, con esercizi, obiettivi e controllo dell'esecuzione."
      },
      {
        id: "resistenza",
        label: "resistenza e corsa",
        words: ["resistenza", "corsa", "corre", "cardio", "fiato", "aerobico"],
        sentence: "La resistenza viene sviluppata attraverso attività di corsa o lavoro cardiovascolare, con attenzione alla continuità dello sforzo."
      },
      {
        id: "forza",
        label: "forza muscolare",
        words: ["forza", "muscoli", "gambe", "addome", "schiena", "carico", "ripetizioni", "serie"],
        sentence: "La parte muscolare coinvolge esercizi per forza, controllo del corpo e lavoro su gruppi come gambe, addome e schiena."
      },
      {
        id: "recupero",
        label: "recupero e fatica",
        words: ["recupero", "fatica", "riposo", "defaticamento", "stanchezza", "adattamento"],
        sentence: "Il recupero e la gestione della fatica servono ad adattare il programma senza sovraccaricare il corpo."
      },
      {
        id: "progressione",
        label: "progressi e adattamento",
        words: ["progressi", "migliorare", "progressione", "modifica", "adatta", "controlla", "monitoraggio"],
        sentence: "Il controllo dei progressi permette di modificare il lavoro in base ai risultati e alle sensazioni fisiche."
      }
    ],
    poetry: [
      {
        id: "tema_poetico",
        label: "tema poetico",
        words: ["poesia", "tema", "verso", "versi", "strofa", "ritmo"],
        sentence: "Il testo sviluppa un tema poetico attraverso immagini, ritmo e concentrazione emotiva."
      },
      {
        id: "natura",
        label: "natura e paesaggio",
        words: ["natura", "vento", "foglie", "cielo", "mare", "luna", "sera", "notte"],
        sentence: "La natura e il paesaggio diventano elementi centrali per costruire l'atmosfera del testo."
      },
      {
        id: "emozioni",
        label: "emozioni e nostalgia",
        words: ["nostalgia", "ricordo", "cuore", "emozione", "sentimento", "paura", "speranza", "conforto"],
        sentence: "Il testo collega immagini esterne e stati interiori, facendo emergere nostalgia, ricordo o conforto."
      },
      {
        id: "silenzio",
        label: "silenzio e calma",
        words: ["silenzio", "silenziosa", "calma", "quieta", "lento", "lentamente"],
        sentence: "Il silenzio e la calma danno al testo un andamento raccolto e contemplativo."
      }
    ],
    story: [
      {
        id: "personaggi",
        label: "personaggi",
        words: ["personaggio", "personaggi", "protagonista", "narratore", "amico", "famiglia"],
        sentence: "Il racconto ruota attorno ai personaggi e alle loro scelte nel corso degli eventi."
      },
      {
        id: "ambientazione",
        label: "ambientazione",
        words: ["ambientazione", "villaggio", "città", "citta", "casa", "bosco", "scena", "luogo"],
        sentence: "L'ambientazione definisce il contesto in cui si muovono i personaggi e prende forma la vicenda."
      },
      {
        id: "conflitto",
        label: "conflitto narrativo",
        words: ["problema", "conflitto", "paura", "ostacolo", "scelta", "pericolo", "sfida"],
        sentence: "Il conflitto narrativo nasce da un problema o da una scelta che modifica il percorso dei personaggi."
      },
      {
        id: "sviluppo",
        label: "sviluppo della storia",
        words: ["poi", "dopo", "decise", "accadde", "capitolo", "finale", "conclusione"],
        sentence: "La storia procede per passaggi successivi fino a una trasformazione o a una conclusione."
      }
    ],
    curriculum: [
      {
        id: "profilo",
        label: "profilo professionale",
        words: ["profilo", "candidato", "professionale", "obiettivo", "presentazione"],
        sentence: "Il curriculum presenta il profilo professionale e l'obiettivo del candidato."
      },
      {
        id: "esperienze",
        label: "esperienze lavorative",
        words: ["esperienza", "esperienze", "lavoro", "ruolo", "mansioni", "stage", "azienda"],
        sentence: "Le esperienze lavorative descrivono ruoli, attività svolte e contesti professionali attraversati."
      },
      {
        id: "competenze",
        label: "competenze tecniche",
        words: ["competenze", "skill", "java", "python", "javascript", "react", "github", "tecnologie"],
        sentence: "Le competenze evidenziano strumenti, tecnologie e capacità utili per il ruolo."
      },
      {
        id: "formazione",
        label: "formazione",
        words: ["formazione", "scuola", "corso", "diploma", "certificazione", "studio"],
        sentence: "La formazione completa il profilo con studi, corsi e certificazioni rilevanti."
      }
    ],
    personal: [
      {
        id: "dati",
        label: "dati personali",
        words: ["nome", "cognome", "residenza", "indirizzo", "codice", "fiscale", "anagrafica"],
        sentence: "Il documento raccoglie dati personali e informazioni utili all'identificazione o alla pratica amministrativa."
      },
      {
        id: "richiesta",
        label: "richiesta o modulo",
        words: ["richiesta", "domanda", "modulo", "istanza", "certificato", "autocertificazione"],
        sentence: "La richiesta o il modulo indicano lo scopo amministrativo del documento."
      },
      {
        id: "scadenze",
        label: "scadenze e validità",
        words: ["scadenza", "validità", "validita", "data", "rinnovo", "termine"],
        sentence: "Date, scadenze e validità chiariscono quando il documento deve essere usato o aggiornato."
      }
    ],
    hobby: [
      {
        id: "idea",
        label: "idea principale",
        words: ["idea", "progetto", "hobby", "creativo", "creativa", "realizzare"],
        sentence: "Il testo presenta un'idea o un progetto personale da sviluppare in modo creativo."
      },
      {
        id: "fasi",
        label: "fasi di realizzazione",
        words: ["fase", "fasi", "costruire", "preparare", "sviluppare", "passaggi"],
        sentence: "Le fasi di realizzazione spiegano come trasformare l'idea in un risultato concreto."
      },
      {
        id: "strumenti",
        label: "strumenti necessari",
        words: ["strumenti", "materiali", "app", "musica", "disegno", "fotografia", "software"],
        sentence: "Gli strumenti necessari aiutano a capire cosa serve per completare il progetto."
      },
      {
        id: "risultato",
        label: "risultato atteso",
        words: ["risultato", "obiettivo", "miglioramento", "finale", "versione"],
        sentence: "Il risultato atteso descrive l'effetto finale o il miglioramento previsto."
      }
    ],
    generic: []
  };

  function getTopicsForProfileV2A30(profileInfo) {
    const id = profileInfo && profileInfo.id ? profileInfo.id : "generic";
    const topics = PROFILE_TOPICS_V2A30[id];

    if (topics && topics.length) return topics;
    if (id === "business" || id === "cybersecurity") return TOPICS;

    return [];
  }

  function requiredKeywordsForProfileV2A30(profileInfo, rawKeywords) {
    const required = [];
    const used = new Set();

    function add(value) {
      const clean = normalizeForCompare(value);
      if (!clean || used.has(clean)) return;
      used.add(clean);
      required.push(value);
    }

    (profileInfo && profileInfo.keywords ? profileInfo.keywords : []).forEach(function (keyword) {
      getKeywordConceptWords(keyword).forEach(add);
    });

    (rawKeywords || []).slice(0, 8).forEach(add);

    if (profileInfo && (profileInfo.id === "business" || profileInfo.id === "cybersecurity")) {
      ["sicurezza", "backup", "privacy", "incidenti", "phishing", "audit", "password", "controlli"].forEach(add);
    }

    return required.slice(0, 14);
  }
'''

DETECT_TOPICS_REPLACEMENT = r'''  function detectTopics(text, profileInfo) {
    const normalized = normalizeForCompare(text);
    const topicsForProfile = getTopicsForProfileV2A30(profileInfo || detectDocumentProfile(text));

    return topicsForProfile.map(function (topic) {
      let score = 0;

      topic.words.forEach(function (word) {
        const cleanWord = normalizeForCompare(word);
        if (!cleanWord) return;

        const re = new RegExp("\\b" + cleanWord.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "\\b", "g");
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
'''

SCORE_SENTENCE_REPLACEMENT = r'''  function scoreSentence(sentence, index, total, freq, requiredKeywords, profileInfo) {
    let score = 0;
    const lower = sentence.toLowerCase();
    const topicsForProfile = getTopicsForProfileV2A30(profileInfo || detectDocumentProfile(sentence));

    getWords(sentence).forEach(function (word) {
      if (STOPWORDS.has(word)) return;
      score += freq.get(word) || 0;
    });

    (requiredKeywords || []).forEach(function (keyword) {
      if (lower.includes(String(keyword).toLowerCase())) score += 10;
    });

    topicsForProfile.forEach(function (topic) {
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
'''

PICK_BEST_REPLACEMENT = r'''  function pickBestSentences(text, options) {
    const opts = Object.assign({
      maxSentences: 5,
      maxChars: 1400,
      requiredKeywords: [],
      profileInfo: null
    }, options || {});

    const profileInfo = opts.profileInfo || detectDocumentProfile(text);
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
          score: scoreSentence(sentence, index, sentences.length, freq, opts.requiredKeywords, profileInfo)
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
'''

SUMMARIZE_BATCH_REPLACEMENT = r'''  function summarizeBatch(batch, options) {
    const opts = Object.assign({
      sentencesPerBatch: 5,
      maxCharsPerBatchSummary: 1500
    }, options || {});

    const text = (batch.chunks || [])
      .map(function (chunk) {
        return chunk.text || "";
      })
      .join("\n\n");

    const profileInfo = detectDocumentProfile(text);
    const keywords = extractKeywords(text, 12);
    const topics = detectTopics(text, profileInfo).slice(0, 6);
    const requiredKeywords = requiredKeywordsForProfileV2A30(profileInfo, keywords);

    let sentences = pickBestSentences(text, {
      maxSentences: opts.sentencesPerBatch,
      maxChars: opts.maxCharsPerBatchSummary,
      requiredKeywords: requiredKeywords,
      profileInfo: profileInfo
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
      profile: profileInfo.id,
      profileLabel: profileInfo.label,
      summary: summary,
      summaryChars: summary.length
    };
  }
'''

BUILD_TOPIC_REPLACEMENT = r'''  function buildTopicSynthesis(topicStats, partials, profileInfo) {
    const topTopics = Array.from(topicStats.values())
      .sort(function (a, b) {
        return b.score - a.score;
      });

    const sentences = [];

    topTopics.forEach(function (topic) {
      if (sentences.length >= 10) return;
      if (!sentences.some(function (existing) { return areSentencesTooSimilar(existing, topic.sentence, 0.70); })) {
        sentences.push(topic.sentence);
      }
    });

    if (!sentences.length) {
      const combinedPartials = (partials || []).map(function (part) { return part.summary || ""; }).join(" ");
      sentences.push.apply(sentences, pickBestSentences(combinedPartials, {
        maxSentences: 5,
        maxChars: 1600,
        requiredKeywords: [],
        profileInfo: profileInfo
      }));
    }

    return dedupeSentences(sentences, 14);
  }
'''

BUILD_FINAL_KEYWORDS_REPLACEMENT = r'''  function buildFinalKeywords(topicStats, allKeywords, profileInfo) {
    const output = [];
    const used = new Set();

    function addKeyword(value) {
      const label = String(value || "").trim();
      const clean = normalizeForCompare(label);

      if (!label || !clean) return;
      if (used.has(clean)) return;
      if (!isConceptKeyword(label)) return;

      used.add(clean);
      output.push(label);
    }

    const profile = profileInfo || DOCUMENT_PROFILES.find(function (item) { return item.id === "generic"; });

    (profile.keywords || []).forEach(addKeyword);

    Array.from(topicStats.values())
      .sort(function (a, b) {
        return b.score - a.score;
      })
      .forEach(function (topic) {
        addKeyword(topic.label);
      });

    Array.from(allKeywords.entries())
      .sort(function (a, b) {
        return b[1] - a[1];
      })
      .forEach(function (entry) {
        const keyword = entry[0];
        if (!isWeakKeyword(keyword)) addKeyword(keyword);
      });

    return output.slice(0, 14);
  }
'''

MERGE_REPLACEMENT = r'''  function mergeProgressiveSummaries(partials, options) {
    const opts = Object.assign({
      finalSentences: 12,
      maxFinalChars: 4200
    }, options || {});

    const allKeywords = new Map();

    partials.forEach(function (part) {
      (part.keywords || []).forEach(function (keyword) {
        allKeywords.set(keyword, (allKeywords.get(keyword) || 0) + 1);
      });
    });

    const combinedText = partials.map(function (part) {
      return part.summary;
    }).join("\n\n");

    const profileInfo = detectDocumentProfile(combinedText + "\n" + Array.from(allKeywords.keys()).join(" "));
    const profileTopics = getTopicsForProfileV2A30(profileInfo);
    const topicStats = new Map();

    partials.forEach(function (part) {
      (part.topics || []).forEach(function (label) {
        if (!topicStats.has(label)) {
          const base = profileTopics.find(function (topic) { return topic.label === label; });
          topicStats.set(label, {
            label: label,
            score: 0,
            sentence: base ? base.sentence : "Il documento sviluppa il tema " + label + " in relazione al contenuto analizzato."
          });
        }

        topicStats.get(label).score += 1;
      });
    });

    const requiredKeywords = requiredKeywordsForProfileV2A30(profileInfo, Array.from(allKeywords.keys()));

    const extracted = pickBestSentences(combinedText, {
      maxSentences: 8,
      maxChars: 2200,
      requiredKeywords: requiredKeywords,
      profileInfo: profileInfo
    });

    const synthesis = buildTopicSynthesis(topicStats, partials, profileInfo);

    const finalSentences = dedupeSentences(extracted.concat(synthesis), opts.finalSentences)
      .slice(0, opts.finalSentences);

    const keywords = buildProfileAwareKeywords(profileInfo, topicStats, allKeywords);

    return {
      title: "Riassunto progressivo finale",
      summary: finalSentences.join(" "),
      keywords: keywords,
      profile: profileInfo.id,
      profileLabel: profileInfo.label,
      partialCount: partials.length,
      totalSummaryChars: partials.reduce(function (sum, part) {
        return sum + part.summaryChars;
      }, 0)
    };
  }
'''


def patch_universal() -> None:
    backup(UNIVERSAL)
    text = UNIVERSAL.read_text(encoding="utf-8")
    text = replace_regex(
        text,
        r"  function creaParagrafiRiassunto\(testo, profilo\) \{.*?\n  function correggiSpaziPunteggiaturaV35G",
        UNIVERSAL_REPLACEMENT + "\n\n  function correggiSpaziPunteggiaturaV35G",
        "creaParagrafiRiassunto V2A30"
    )
    UNIVERSAL.write_text(text, encoding="utf-8")
    print(f"Modificato: {UNIVERSAL}")


def patch_progressive() -> None:
    backup(PROGRESSIVE)
    text = PROGRESSIVE.read_text(encoding="utf-8")

    if "PROFILE_TOPICS_V2A30" not in text:
      text = replace_regex(
          text,
          r"\n\s*function detectDocumentProfile\(text\)",
          PROFILE_TOPICS_INSERT + "\n\n  function detectDocumentProfile(text)",
          "inserimento PROFILE_TOPICS_V2A30"
      )

    text = replace_regex(
        text,
        r"  function detectTopics\(text\) \{.*?\n  function scoreSentence",
        DETECT_TOPICS_REPLACEMENT + "\n\n  function scoreSentence",
        "detectTopics profile-aware"
    )

    text = replace_regex(
        text,
        r"  function scoreSentence\(sentence, index, total, freq, requiredKeywords\) \{.*?\n  function pickBestSentences",
        SCORE_SENTENCE_REPLACEMENT + "\n\n  function pickBestSentences",
        "scoreSentence profile-aware"
    )

    text = replace_regex(
        text,
        r"  function pickBestSentences\(text, options\) \{.*?\n  function summarizeBatch",
        PICK_BEST_REPLACEMENT + "\n\n  function summarizeBatch",
        "pickBestSentences profile-aware"
    )

    text = replace_regex(
        text,
        r"  function summarizeBatch\(batch, options\) \{.*?\n  function buildTopicSynthesis",
        SUMMARIZE_BATCH_REPLACEMENT + "\n\n  function buildTopicSynthesis",
        "summarizeBatch profile-aware"
    )

    text = replace_regex(
        text,
        r"  function buildTopicSynthesis\(topicStats, partials\) \{.*?\n\s*function buildFinalKeywords",
        BUILD_TOPIC_REPLACEMENT + "\n\n  function buildFinalKeywords",
        "buildTopicSynthesis senza frasi aziendali universali"
    )

    text = replace_regex(
        text,
        r"  function buildFinalKeywords\(topicStats, allKeywords\) \{.*?\n  function mergeProgressiveSummaries",
        BUILD_FINAL_KEYWORDS_REPLACEMENT + "\n\n  function mergeProgressiveSummaries",
        "buildFinalKeywords profile-aware"
    )

    text = replace_regex(
        text,
        r"  function mergeProgressiveSummaries\(partials, options\) \{.*?\n  async function createProgressiveSummary",
        MERGE_REPLACEMENT + "\n\n  async function createProgressiveSummary",
        "mergeProgressiveSummaries profile-aware"
    )

    PROGRESSIVE.write_text(text, encoding="utf-8")
    print(f"Modificato: {PROGRESSIVE}")


def write_report() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = REPORT_DIR / "report_fix_riassunto_profile_aware_v2a30.md"
    report.write_text(
        "# Fix riassunto profile-aware V2A30\n\n"
        "Modificati solo i motori riassunto:\n\n"
        "- `demo-rag/universal-document-learning-engine.js`\n"
        "- `runtime/web/rag-large-document-progressive-summary-v2.js`\n\n"
        "## Obiettivo\n\n"
        "- Riassunto breve/medio senza collage forzato a 2500 caratteri.\n"
        "- Riassunto lungo con topic dipendenti dal profilo documento.\n"
        "- Niente frasi universali aziendali/cybersecurity per sport, poesia, racconto, CV, personale o hobby.\n"
        "- Nessun intervento su HTML, CSS, pulsanti, PDF, card, test o domande studio.\n",
        encoding="utf-8"
    )
    print(f"Report scritto: {report}")


def main() -> None:
    if not (ROOT / ".git").exists():
        die("Esegui questo script dalla root del repository Git.")

    patch_universal()
    patch_progressive()
    write_report()

    print("\nOK V2A30: patch applicata.")
    print("Prossimi controlli consigliati:")
    print("  git diff --stat")
    print("  python3 scripts/verifica_qualita_riassunto_lungo_v2a29.py")
    print("  python3 -m http.server 8020")


if __name__ == "__main__":
    main()
