#!/usr/bin/env python3
from pathlib import Path
import json
import subprocess
import sys
import textwrap

ROOT = Path(__file__).resolve().parents[1]

manager = ROOT / "runtime/web/rag-large-document-manager-v1.js"
summarizer = ROOT / "runtime/web/rag-large-document-progressive-summary-v2.js"
html = ROOT / "demo-rag/test-rag-documenti-lunghi-v2.html"
base_doc = ROOT / "rag/documenti/test_documento_lungo_aziendale_120_pagine.md"
generator = ROOT / "scripts/crea_documento_lungo_test_rag_v1.py"
reports = ROOT / "reports"
reports.mkdir(exist_ok=True)

required = [manager, summarizer, html]

for path in required:
    if not path.exists():
        print(f"ERRORE: file mancante {path.relative_to(ROOT)}")
        sys.exit(1)

if not base_doc.exists():
    if not generator.exists():
        print("ERRORE: documento base 120 pagine mancante e generatore V1 assente")
        sys.exit(1)

    subprocess.run([sys.executable, str(generator)], cwd=ROOT, check=True)

html_text = html.read_text(encoding="utf-8")
summarizer_text = summarizer.read_text(encoding="utf-8")

required_html = [
    "fileInputLarge",
    "Analizza e genera riassunto progressivo",
    "rag-large-document-manager-v1.js",
    "rag-large-document-progressive-summary-v2.js",
    "maxCharsPerChunk",
    "maxPagesPerBatch",
    "maxChunksPerBatch",
    "maxCharsPerBatch",
    "Riassunto finale progressivo",
    "Riassunti parziali per batch",
]

for token in required_html:
    if token not in html_text:
        print(f"ERRORE: token HTML V2A mancante: {token}")
        sys.exit(1)

required_summarizer = [
    "createProgressiveSummary",
    "summarizeBatch",
    "mergeProgressiveSummaries",
    "extractKeywords",
    "detectDocumentProfile",
    "buildProfileAwareKeywords",
    "isConceptKeyword",
]

for token in required_summarizer:
    if token not in summarizer_text:
        print(f"ERRORE: token summarizer V2 mancante: {token}")
        sys.exit(1)

node_code = r"""
const fs = require('fs');
const path = require('path');

const manager = require('./runtime/web/rag-large-document-manager-v1.js');
const summarizer = require('./runtime/web/rag-large-document-progressive-summary-v2.js');

const ROOT = process.cwd();
const REPORTS = path.join(ROOT, 'reports');
const DOCS = path.join(ROOT, 'rag', 'documenti');

const BASE_DOC = path.join(DOCS, 'test_documento_lungo_aziendale_120_pagine.md');

const TARGETS = [180, 240, 300];

function fail(message) {
  throw new Error(message);
}

function safeWrite(filePath, content) {
  fs.writeFileSync(filePath, content, 'utf8');
}

function normalizeText(value) {
  return String(value || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

function validateNoOldFallback(text) {
  const bad = [
    'lorem ipsum',
    'documento generico',
    'contenuto di esempio',
    'fallback demo',
    'fallback vecchio'
  ];

  const normalized = normalizeText(text);

  return bad.filter(item => normalized.includes(item));
}

function buildExpandedRealDocument(basePages, targetPages) {
  const sections = [];

  for (let index = 0; index < targetPages; index += 1) {
    const pageNumber = index + 1;
    const sourcePage = basePages[index % basePages.length];

    const sourceText = String(sourcePage.text || '')
      .split(/\r?\n/)
      .filter(line => {
        const clean = String(line || '').trim();

        return !/^---\s*PAGINA\s+\d+.*---$/i.test(clean)
          && !/^#\s*PAGINA\s+\d+\b.*$/i.test(clean)
          && !/^PAGINA\s+\d+\b.*$/i.test(clean)
          && !/^#\s*Documento\s+reale\s+V2A\.5\s+-\s+Pagina\s+\d+\b.*$/i.test(clean);
      })
      .join('\n')
      .trim();

    sections.push([
      `--- PAGINA ${pageNumber} ---`,
      '',
      `# Documento reale V2A.5 - Sezione ${pageNumber}`,
      '',
      sourceText,
      '',
      `Nota V2A.5 sezione ${pageNumber}: questa sezione viene salvata in un file reale Markdown, riletta dal disco e processata dal manager RAG come input lungo effettivo.`,
      `Concetti controllati sezione ${pageNumber}: sicurezza operativa, gestione documentale, controllo qualità, formazione interna, continuità operativa.`
    ].join('\n'));
  }

  return sections.join('\n\n');
}

function checkMicroConceptKeywords(keywords) {
  if (!Array.isArray(keywords)) {
    return ['keyword non è un array'];
  }

  return keywords.filter(keyword => {
    if (typeof summarizer.isConceptKeyword !== 'function') {
      fail('funzione isConceptKeyword mancante');
    }

    return !summarizer.isConceptKeyword(keyword);
  });
}

async function runTarget(targetPages, basePages) {
  const fileName = `test_documento_lungo_reale_v2a5_${targetPages}_pagine.md`;
  const filePath = path.join(DOCS, fileName);

  const expandedText = buildExpandedRealDocument(basePages, targetPages);
  safeWrite(filePath, expandedText);

  const realTextFromDisk = fs.readFileSync(filePath, 'utf8');
  const fallbackVecchi = validateNoOldFallback(realTextFromDisk);

  if (fallbackVecchi.length) {
    fail(`fallback vecchi trovati nel file reale ${fileName}: ${fallbackVecchi.join(', ')}`);
  }

  const pages = manager.splitTxtMdIntoLogicalPages(realTextFromDisk);

  if (pages.length !== targetPages) {
    fail(`pagine reali attese ${targetPages}, trovate ${pages.length}`);
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
    fileName,
    totalPages: targetPages,
    extractedPages: pages.length,
    totalChars: pages.reduce((sum, page) => sum + String(page.text || '').length, 0),
    chunks,
    batches
  }, {
    sentencesPerBatch: 5,
    finalSentences: 14
  });

  if (!chunks.length || chunks.length < targetPages) {
    fail(`chunk insufficienti per ${targetPages} pagine: ${chunks.length}`);
  }

  if (!batches.length || batches.length <= 30) {
    fail(`batch insufficienti sopra 120 pagine: ${batches.length}`);
  }

  if (!progressive.partials || progressive.partials.length !== batches.length) {
    fail(`parziali diversi dai batch: parziali=${progressive.partials && progressive.partials.length}, batch=${batches.length}`);
  }

  if (!progressive.finalSummary || !progressive.finalSummary.summary) {
    fail('riassunto finale mancante');
  }

  if (progressive.finalSummary.summary.length < 1000) {
    fail(`riassunto finale troppo corto: ${progressive.finalSummary.summary.length}`);
  }

  if (!progressive.finalSummary.profile || !progressive.finalSummary.profileLabel) {
    fail('profilo documento finale mancante');
  }

  const keywords = progressive.finalSummary.keywords || [];

  if (keywords.length < 8) {
    fail(`keyword finali troppo poche: ${keywords.length}`);
  }

  const invalidKeywords = checkMicroConceptKeywords(keywords);

  if (invalidKeywords.length) {
    fail(`keyword non micro-concetti valide: ${invalidKeywords.join(', ')}`);
  }

  const joinedKeywords = normalizeText(keywords.join(' '));

  const domainHits = [
    'sicurezza',
    'password',
    'phishing',
    'backup',
    'privacy',
    'incidenti',
    'audit',
    'continuita',
    'fornitori',
    'workflow',
    'documentazione',
    'procedure'
  ].filter(keyword => joinedKeywords.includes(keyword));

  if (domainHits.length < 4) {
    fail(`keyword poco informative per dominio aziendale/cybersecurity: hit=${domainHits.join(', ')}`);
  }

  const memory = process.memoryUsage();

  const result = {
    versione: 'RAG documenti lunghi V2A.5 flusso reale',
    file_reale: `rag/documenti/${fileName}`,
    pagine_attese: targetPages,
    pagine_riconosciute: pages.length,
    caratteri_input: realTextFromDisk.length,
    chunk: chunks.length,
    batch: batches.length,
    parziali: progressive.partials.length,
    caratteri_riassunto_finale: progressive.finalSummary.summary.length,
    profilo: progressive.finalSummary.profile,
    profilo_label: progressive.finalSummary.profileLabel,
    keyword: keywords.slice(0, 20),
    keyword_non_micro_concetti: invalidKeywords,
    fallback_vecchi: fallbackVecchi,
    domain_hits: domainHits,
    memoria_heap_mb: Number((memory.heapUsed / 1024 / 1024).toFixed(3)),
    memoria_rss_mb: Number((memory.rss / 1024 / 1024).toFixed(3)),
    ok: true
  };

  const jsonPath = path.join(REPORTS, `rag_documenti_lunghi_v2a5_flusso_reale_${targetPages}_pagine.json`);
  const mdPath = path.join(REPORTS, `rag_documenti_lunghi_v2a5_flusso_reale_${targetPages}_pagine.md`);

  safeWrite(jsonPath, JSON.stringify(result, null, 2));

  safeWrite(mdPath, [
    `# Report RAG documenti lunghi V2A.5 — flusso reale ${targetPages} pagine`,
    '',
    `- File reale: rag/documenti/${fileName}`,
    `- Pagine attese: ${targetPages}`,
    `- Pagine riconosciute: ${pages.length}`,
    `- Caratteri input: ${realTextFromDisk.length}`,
    `- Chunk: ${chunks.length}`,
    `- Batch: ${batches.length}`,
    `- Riassunti parziali: ${progressive.partials.length}`,
    `- Caratteri riassunto finale: ${progressive.finalSummary.summary.length}`,
    `- Profilo: ${progressive.finalSummary.profileLabel}`,
    `- Memoria heap MB: ${result.memoria_heap_mb}`,
    `- Memoria RSS MB: ${result.memoria_rss_mb}`,
    `- Esito: OK`,
    '',
    '## Keyword finali',
    '',
    keywords.slice(0, 20).map(keyword => `- ${keyword}`).join('\n'),
    '',
    '## Domain hits',
    '',
    domainHits.map(hit => `- ${hit}`).join('\n'),
    '',
    '## Estratto riassunto finale',
    '',
    progressive.finalSummary.summary.slice(0, 3000)
  ].join('\n'));

  return result;
}

(async () => {
  if (typeof manager.splitTxtMdIntoLogicalPages !== 'function') {
    fail('manager.splitTxtMdIntoLogicalPages mancante');
  }

  if (typeof manager.createPageChunks !== 'function') {
    fail('manager.createPageChunks mancante');
  }

  if (typeof manager.createBatches !== 'function') {
    fail('manager.createBatches mancante');
  }

  if (typeof summarizer.createProgressiveSummary !== 'function') {
    fail('summarizer.createProgressiveSummary mancante');
  }

  const baseText = fs.readFileSync(BASE_DOC, 'utf8');
  const basePages = manager.splitTxtMdIntoLogicalPages(baseText);

  if (basePages.length !== 120) {
    fail(`documento base atteso 120 pagine, trovate ${basePages.length}`);
  }

  const results = [];

  for (const target of TARGETS) {
    console.log(`\n--- V2A.5 flusso reale ${target} pagine ---`);
    const result = await runTarget(target, basePages);
    results.push(result);

    console.log(`File reale: ${result.file_reale}`);
    console.log(`Pagine: ${result.pagine_riconosciute}/${result.pagine_attese}`);
    console.log(`Chunk: ${result.chunk}`);
    console.log(`Batch: ${result.batch}`);
    console.log(`Parziali: ${result.parziali}`);
    console.log(`Riassunto finale: ${result.caratteri_riassunto_finale} caratteri`);
    console.log(`Profilo: ${result.profilo_label}`);
    console.log(`Keyword: ${result.keyword.length}`);
    console.log(`Memoria heap: ${result.memoria_heap_mb} MB`);
    console.log(`Memoria RSS: ${result.memoria_rss_mb} MB`);
    console.log('Esito: OK');
  }

  const summaryJson = path.join(REPORTS, 'rag_documenti_lunghi_v2a5_flusso_reale_riepilogo.json');
  const summaryMd = path.join(REPORTS, 'rag_documenti_lunghi_v2a5_flusso_reale_riepilogo.md');

  safeWrite(summaryJson, JSON.stringify(results, null, 2));

  safeWrite(summaryMd, [
    '# Riepilogo RAG documenti lunghi V2A.5 — flusso reale',
    '',
    ...results.map(result =>
      `- ${result.pagine_attese} pagine: OK, file reale ${result.file_reale}, ${result.chunk} chunk, ${result.batch} batch, ${result.parziali} parziali, riassunto ${result.caratteri_riassunto_finale} caratteri, profilo ${result.profilo_label}, heap ${result.memoria_heap_mb} MB, RSS ${result.memoria_rss_mb} MB.`
    )
  ].join('\n') + '\n');

  console.log('\n=== V2A.5 FLUSSO REALE COMPLETATO ===');
  console.log('Test reali superati: 180, 240, 300');
  console.log(`Report JSON: ${summaryJson}`);
  console.log(`Report MD: ${summaryMd}`);
})().catch(error => {
  console.error('\nERRORE V2A.5:', error && error.message ? error.message : error);
  process.exit(1);
});
"""

result = subprocess.run(
    ["node", "-e", node_code],
    cwd=ROOT,
    text=True,
    capture_output=True,
)

if result.stdout:
    print(result.stdout)

if result.stderr:
    print(result.stderr, file=sys.stderr)

if result.returncode != 0:
    sys.exit(result.returncode)

print("OK: verifica RAG documenti lunghi V2A.5 flusso reale superata")
