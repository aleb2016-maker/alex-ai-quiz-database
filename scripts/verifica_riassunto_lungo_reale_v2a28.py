#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PAGINA_REALE = ROOT / "demo-rag" / "test-documenti-universale.html"
UNIVERSAL = ROOT / "demo-rag" / "universal-document-learning-engine.js"
CONCEPT_V46 = ROOT / "demo-rag" / "rag-concept-document-engine-v46.js"


class ScriptParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "script":
            attrs_dict = dict(attrs)
            if attrs_dict.get("src"):
                self.scripts.append(attrs_dict["src"])


def leggi(path):
    return path.read_text(encoding="utf-8")


def corpo_funzione(sorgente, nome):
    marker = f"function {nome}("
    start = sorgente.find(marker)
    if start < 0:
        raise AssertionError(f"Funzione mancante: {nome}")

    brace = sorgente.find("{", start)
    profondita = 0
    for pos in range(brace, len(sorgente)):
        if sorgente[pos] == "{":
            profondita += 1
        elif sorgente[pos] == "}":
            profondita -= 1
            if profondita == 0:
                return sorgente[start : pos + 1]

    raise AssertionError(f"Funzione non chiusa: {nome}")


def script_src():
    parser = ScriptParser()
    parser.feed(leggi(PAGINA_REALE))
    return parser.scripts


def run_fixture_lunga():
    js = r"""
const manager = require("./runtime/web/rag-large-document-manager-v1.js");
const summarizer = require("./runtime/web/rag-large-document-progressive-summary-v2.js");

function pagina(n) {
  const temi = [
    "procedure operative e responsabilita assegnate",
    "controlli periodici e registri verificabili",
    "formazione interna e onboarding dei reparti",
    "continuita operativa e gestione degli incidenti",
    "fornitori, documentazione tecnica e audit"
  ];
  const tema = temi[n % temi.length];
  return `--- PAGINA ${n} ---
Pagina ${n}: Il documento descrive ${tema}. Ogni reparto deve mantenere evidenze aggiornate, verifiche ripetibili e una lista di azioni tracciabili.
La sezione ${n} collega obiettivi, ruoli, tempi, controlli e rischi residui, spiegando come trasformare indicazioni generali in istruzioni operative.
Il materiale insiste su procedure leggibili, responsabilita chiare, verifiche settimanali, controlli mensili, revisioni trimestrali e miglioramento continuo.
Quando emergono anomalie, il team deve registrare il problema, classificare la priorita, assegnare un responsabile e chiudere l'attivita con evidenze verificabili.
`;
}

(async () => {
  const testo = Array.from({ length: 120 }, (_, i) => pagina(i + 1)).join("\n\n");
  const pages = manager.splitTxtMdIntoLogicalPages(testo);
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
    fileName: "fixture-120-pagine.md",
    totalPages: pages.length,
    extractedPages: pages.length,
    totalChars: testo.length,
    chunks,
    batches
  }, {
    sentencesPerBatch: 5,
    maxCharsPerBatchSummary: 1500,
    finalSentences: 14,
    maxFinalChars: 4500
  });

  const partialText = progressive.partials.map(p => p.summary).join("\n");
  const lines = partialText.split(/[.!?]\s+|\n+/).filter(x => x.trim().length > 30);
  const repeated = (partialText.match(/La procedura richiede/g) || []).length;
  const result = {
    pages: pages.length,
    chunks: chunks.length,
    batches: batches.length,
    partials: progressive.partials.length,
    finalChars: progressive.finalSummary.summary.length,
    partialChars: partialText.length,
    lines: lines.length,
    repeated
  };
  console.log(JSON.stringify(result));
})().catch((error) => {
  console.error(error && error.stack ? error.stack : String(error));
  process.exit(1);
});
"""
    proc = subprocess.run(
        ["node"],
        input=js,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    if proc.returncode != 0:
        raise AssertionError("fixture lunga Node fallita: " + (proc.stderr or proc.stdout))

    import json
    return json.loads(proc.stdout.strip().splitlines()[-1])


def main():
    problemi = []
    html = leggi(PAGINA_REALE)
    universal = leggi(UNIVERSAL)
    concept = leggi(CONCEPT_V46)

    scripts = script_src()
    scripts_joined = "\n".join(scripts)

    if "rag-motori-intelligenti-browser-v2a19.js" in html:
        problemi.append("pagina reale carica V2A19")

    if "rag-quality-summary-cards-v34a.js" in html:
        problemi.append("pagina reale carica V34A")

    if "../runtime/web/rag-large-document-manager-v1.js" not in scripts_joined:
        problemi.append("pagina reale non carica RagLargeDocumentManagerV1")

    if "../runtime/web/rag-large-document-progressive-summary-v2.js" not in scripts_joined:
        problemi.append("pagina reale non carica RagLargeDocumentProgressiveSummaryV2")

    if 'replaceButton("btnRiassunto"' in concept:
        problemi.append("V46 intercetta ancora btnRiassunto prima del motore universale")

    try:
        genera_riassunto = corpo_funzione(universal, "generaRiassunto")
        genera_card = corpo_funzione(universal, "generaCardVisive")
        genera_test = corpo_funzione(universal, "generaTest")
        genera_domande = corpo_funzione(universal, "generaDomandeStudio")
    except AssertionError as errore:
        problemi.append(str(errore))
        genera_riassunto = genera_card = genera_test = genera_domande = ""

    richiesti_riassunto = [
        "deveUsareRiassuntoLungoV2A28",
        "creaParagrafiRiassunto",
        "creaReportDocumentoLungoV2A28",
        "RagLargeDocumentProgressiveSummaryV2",
        "createProgressiveSummary",
        "renderizzaRiassuntoLungoV2A28",
    ]

    for token in richiesti_riassunto:
        if token not in genera_riassunto:
            problemi.append(f"generaRiassunto non contiene {token}")

    if "SOGLIA_RIASSUNTO_LUNGO_CARATTERI_V2A28 = 10000" not in universal:
        problemi.append("soglia lungo 10.000 caratteri mancante")

    if "partials.slice(0, 36)" not in universal or "Dettagli importanti per batch" not in universal:
        problemi.append("render lungo non include dettagli da molti batch")

    for nome, corpo in [
        ("generaCardVisive", genera_card),
        ("generaTest", genera_test),
        ("generaDomandeStudio", genera_domande),
    ]:
        if "RagLargeDocument" in corpo or "V2A28" in corpo:
            problemi.append(f"{nome} e' stato contaminato dal riassunto lungo")

    if "Sicurezza informatica aziendale" in html or "Sicurezza informatica aziendale" in universal:
        problemi.append("testo demo sicurezza presente nella pagina reale o nel motore universale")

    if 'replace(/\\s+([,.!?;:])/g, "$1")' not in universal:
        problemi.append("V35G non corregge gli spazi prima della punteggiatura")

    if "creaParagrafiRiassunto" not in genera_riassunto or "if (!deveUsareRiassuntoLungoV2A28(testo))" not in genera_riassunto:
        problemi.append("creaParagrafiRiassunto non resta fallback per testi brevi")

    try:
        fixture = run_fixture_lunga()
        if fixture["pages"] < 120:
            problemi.append(f"fixture lunga non simula 120 pagine: {fixture['pages']}")
        if fixture["chunks"] < 100:
            problemi.append(f"chunk insufficienti su fixture lunga: {fixture['chunks']}")
        if fixture["batches"] < 15:
            problemi.append(f"batch insufficienti su fixture lunga: {fixture['batches']}")
        if fixture["partials"] != fixture["batches"]:
            problemi.append("parziali diversi dai batch nella fixture lunga")
        if fixture["partialChars"] < 9000 or fixture["lines"] < 35:
            problemi.append(
                f"riassunto lungo troppo corto: partialChars={fixture['partialChars']} lines={fixture['lines']}"
            )
        if fixture["finalChars"] < 1200:
            problemi.append(f"sintesi finale progressiva troppo corta: {fixture['finalChars']}")
        if fixture["repeated"] > 4:
            problemi.append(f"ripetizione eccessiva nella fixture lunga: {fixture['repeated']}")
    except AssertionError as errore:
        problemi.append(str(errore))

    if problemi:
        print("RIASSUNTO LUNGO V2A28: KO")
        for problema in problemi:
            print(f"- {problema}")
        return 1

    print("RIASSUNTO LUNGO V2A28: OK")
    print("- pagina reale senza V2A19/V34A")
    print("- btnRiassunto libero dall'intercettazione V46")
    print("- generaRiassunto usa soglia breve/lungo e motore progressivo esistente")
    print("- card/test/domande studio senza V2A28")
    print("- fixture lunga produce chunk, batch e molte righe di sintesi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
