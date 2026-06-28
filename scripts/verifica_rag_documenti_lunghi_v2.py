#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import json

ROOT = Path(__file__).resolve().parents[1]

manager = ROOT / "runtime/web/rag-large-document-manager-v1.js"
summarizer = ROOT / "runtime/web/rag-large-document-progressive-summary-v2.js"
html = ROOT / "demo-rag/test-rag-documenti-lunghi-v2.html"
doc = ROOT / "rag/documenti/test_documento_lungo_aziendale_120_pagine.md"
report = ROOT / "reports/rag_documenti_lunghi_v2.md"

for path in [manager, summarizer, html]:
    if not path.exists():
        print(f"ERRORE: file mancante {path.relative_to(ROOT)}")
        sys.exit(1)

summarizer_text = summarizer.read_text(encoding="utf-8")
html_text = html.read_text(encoding="utf-8")

required_js = [
    "summarizeBatch",
    "mergeProgressiveSummaries",
    "createProgressiveSummary",
    "extractKeywords",
    "pickBestSentences",
    "memoryPolicy",
    "DOCUMENT_PROFILES",
    "detectDocumentProfile",
    "buildProfileAwareKeywords",
    "dedupeSentences",
    "areSentencesTooSimilar"
]

for token in required_js:
    if token not in summarizer_text:
        print(f"ERRORE: token JS mancante {token}")
        sys.exit(1)

required_html = [
    "test-rag-documenti-lunghi-v2",
    "rag-large-document-manager-v1.js",
    "rag-large-document-progressive-summary-v2.js",
    "Analizza e genera riassunto progressivo",
    "Riassunto finale progressivo",
    "Riassunti parziali per batch",
    "Profilo"
]

for token in required_html:
    if token not in html_text:
        print(f"ERRORE: token HTML mancante {token}")
        sys.exit(1)

for forbidden in [
    "test-documenti-universale.html",
    "pdf-export-browser-v6.js",
    "btnScaricaPdf",
    "btnScaricaTxt",
    "btnScaricaHtml",
    "btnScaricaJson",
    "rag-graphic-intelligence",
    "rag-demo-graphic-bridge"
]:
    if forbidden in html_text:
        print(f"ERRORE: collegamento vietato nella pagina V2: {forbidden}")
        sys.exit(1)

if not doc.exists():
    generator = ROOT / "scripts/crea_documento_lungo_test_rag_v1.py"
    if not generator.exists():
        print("ERRORE: documento test mancante e generatore V1 assente")
        sys.exit(1)
    subprocess.run([sys.executable, str(generator)], cwd=ROOT, check=True)

node_code = r"""
const fs = require('fs');
const manager = require('./runtime/web/rag-large-document-manager-v1.js');
const summarizer = require('./runtime/web/rag-large-document-progressive-summary-v2.js');

(async () => {
  const text = fs.readFileSync('./rag/documenti/test_documento_lungo_aziendale_120_pagine.md', 'utf8');

  if (typeof manager.splitTxtMdIntoLogicalPages !== 'function') {
    throw new Error('manager.splitTxtMdIntoLogicalPages mancante');
  }

  if (typeof summarizer.detectDocumentProfile !== 'function') {
    throw new Error('summarizer.detectDocumentProfile mancante');
  }

  if (typeof summarizer.buildProfileAwareKeywords !== 'function') {
    throw new Error('summarizer.buildProfileAwareKeywords mancante');
  }

  const profileChecks = [
    ['poetry', 'poesia versi strofa rima metafora voce poetica natura amore'],
    ['sport', 'scheda allenamento esercizi serie ripetizioni recupero forza resistenza'],
    ['curriculum', 'curriculum vitae profilo professionale esperienze competenze formazione lavoro'],
    ['story', 'racconto personaggio trama scena dialogo ambientazione narratore finale'],
    ['personal', 'documento identità codice fiscale residenza modulo certificato firma'],
    ['hobby', 'progetto creativo hobby app musica disegno tempo libero realizzare'],
    ['business', 'azienda procedure policy audit workflow fornitori responsabilità operative'],
    ['cybersecurity', 'sicurezza firewall phishing password backup privacy incidenti accessi']
  ];

  for (const [expected, sample] of profileChecks) {
    const detected = summarizer.detectDocumentProfile(sample);
    if (!detected || detected.id !== expected) {
      throw new Error('profilo documento errato: atteso=' + expected + ' trovato=' + (detected && detected.id));
    }
  }

  const pages = manager.splitTxtMdIntoLogicalPages(text);

  if (pages.length !== 120) {
    throw new Error('pagine logiche attese 120, trovate ' + pages.length);
  }

  const chunks = manager.createPageChunks(pages, {
    maxCharsPerChunk: 4000,
    chunkOverlap: 400
  });

  const batches = manager.createBatches(chunks, {
    maxPagesPerBatch: 5,
    maxChunksPerBatch: 8,
    maxCharsPerBatch: 28000
  });

  const progressive = await summarizer.createProgressiveSummary({
    fileName: 'test_documento_lungo_aziendale_120_pagine.md',
    totalPages: 120,
    extractedPages: pages.length,
    totalChars: pages.reduce((sum, page) => sum + page.text.length, 0),
    chunks,
    batches
  }, {
    sentencesPerBatch: 5,
    finalSentences: 14
  });

  if (chunks.length < 50) {
    throw new Error('chunk troppo pochi: ' + chunks.length);
  }

  if (batches.length < 5) {
    throw new Error('batch troppo pochi: ' + batches.length);
  }

  if (progressive.partials.length !== batches.length) {
    throw new Error('parziali diversi dai batch');
  }

  if (!progressive.finalSummary || progressive.finalSummary.summary.length < 800) {
    throw new Error('riassunto finale troppo corto');
  }

  if (!progressive.finalSummary.profile || !progressive.finalSummary.profileLabel) {
    throw new Error('profilo finale mancante');
  }

  if (!['business', 'cybersecurity'].includes(progressive.finalSummary.profile)) {
    throw new Error('profilo finale inatteso per documento aziendale: ' + progressive.finalSummary.profile);
  }

  const finalText = progressive.finalSummary.summary;
  const finalSentences = summarizer.splitSentences(finalText);
  const normalizedSentences = finalSentences.map(sentence =>
    sentence.toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^\w\s]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
  );

  const uniqueSentences = new Set(normalizedSentences);

  if (finalSentences.length >= 6 && uniqueSentences.size < Math.ceil(finalSentences.length * 0.75)) {
    throw new Error('riassunto finale troppo ripetitivo: frasi=' + finalSentences.length + ' uniche=' + uniqueSentences.size);
  }

  const repeatedPattern = (finalText.match(/Ogni attivit[aà] deve indicare/gi) || []).length;

  if (repeatedPattern > 2) {
    throw new Error('riassunto finale ripete troppe volte la stessa apertura: ' + repeatedPattern);
  }

  const weakKeywords = new Set([
    'quali', 'aprire', 'entro', 'stati', 'passaggi', 'riferimento',
    'controllo', 'operativo', 'responsabile', 'team', 'registro',
    'evita', 'informali', 'rende', 'fornitori'
  ]);

  const badKeywords = progressive.finalSummary.keywords.filter(keyword =>
    weakKeywords.has(String(keyword).toLowerCase().trim())
  );

  if (badKeywords.length) {
    throw new Error('keyword finali troppo generiche: ' + badKeywords.join(', '));
  }

  const joinedKeywords = progressive.finalSummary.keywords.join(' ').toLowerCase();

  const domainHits = [
    'sicurezza',
    'password',
    'phishing',
    'backup',
    'privacy',
    'incidenti',
    'audit',
    'continuità',
    'fornitori',
    'workflow',
    'documentazione'
  ].filter(keyword => joinedKeywords.includes(keyword));

  if (domainHits.length < 6) {
    throw new Error('keyword finali poco informative: hit=' + domainHits.join(', '));
  }

  if (!progressive.memoryPolicy || progressive.memoryPolicy.indexOf('non duplicano') === -1) {
    throw new Error('memoryPolicy mancante o debole');
  }

  console.log(JSON.stringify({
    pages: pages.length,
    chunks: chunks.length,
    batches: batches.length,
    partials: progressive.partials.length,
    finalSummaryChars: progressive.finalSummary.summary.length,
    profile: progressive.finalSummary.profile,
    profileLabel: progressive.finalSummary.profileLabel,
    keywords: progressive.finalSummary.keywords.slice(0, 12)
  }, null, 2));
})();
"""

completed = subprocess.run(
    ["node", "-e", node_code],
    cwd=ROOT,
    text=True,
    capture_output=True
)

if completed.returncode != 0:
    print(completed.stdout)
    print(completed.stderr)
    print("ERRORE: test Node V2 fallito")
    sys.exit(1)

try:
    metrics = json.loads(completed.stdout)
except Exception:
    print(completed.stdout)
    print("ERRORE: output Node non JSON")
    sys.exit(1)

report.write_text(
    "\n".join([
        "# Report RAG documenti lunghi V2A",
        "",
        "## Stato",
        "",
        "- V2A separata creata.",
        "- Usa il manager V1 per pagine, chunk e batch.",
        "- Genera riassunti parziali batch per batch.",
        "- Genera un riassunto finale progressivo.",
        "- Riconosce il profilo del documento e usa keyword adatte al tema.",
        "- Non collega la demo ufficiale.",
        "- Non tocca PDF export.",
        "- Non tocca TXT/HTML/JSON export.",
        "- Non tocca grafica.",
        "",
        "## Metriche test",
        "",
        f"- Pagine logiche: {metrics['pages']}",
        f"- Chunk: {metrics['chunks']}",
        f"- Batch: {metrics['batches']}",
        f"- Riassunti parziali: {metrics['partials']}",
        f"- Caratteri riassunto finale: {metrics['finalSummaryChars']}",
        f"- Profilo riconosciuto: {metrics['profileLabel']} ({metrics['profile']})",
        f"- Keyword finali: {', '.join(metrics['keywords'])}",
        "",
        "## Prossimo passo",
        "",
        "V2B: aggiungere generazione progressiva delle card, sempre su pagina separata.",
        ""
    ]),
    encoding="utf-8"
)

print("OK: verifica RAG documenti lunghi V2A superata")
print(
    f"OK: pages={metrics['pages']} chunks={metrics['chunks']} "
    f"batches={metrics['batches']} partials={metrics['partials']} "
    f"finalSummaryChars={metrics['finalSummaryChars']} "
    f"profile={metrics['profileLabel']}"
)
print("OK: report aggiornato reports/rag_documenti_lunghi_v2.md")
