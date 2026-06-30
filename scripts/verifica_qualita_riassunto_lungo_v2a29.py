#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PAGINA_REALE = ROOT / "demo-rag" / "test-documenti-universale.html"
UNIVERSAL = ROOT / "demo-rag" / "universal-document-learning-engine.js"
MANAGER = ROOT / "runtime" / "web" / "rag-large-document-manager-v1.js"
SUMMARIZER = ROOT / "runtime" / "web" / "rag-large-document-progressive-summary-v2.js"


class ScriptParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "script":
            src = dict(attrs).get("src")
            if src:
                self.scripts.append(src)


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


def node_dedupe_check():
    js = r"""
const summarizer = require("./runtime/web/rag-large-document-progressive-summary-v2.js");
const input = [
  "La procedura richiede controlli periodici e registri aggiornati per ogni reparto.",
  "La procedura richiede controlli periodici e registri aggiornati per ogni reparto.",
  "Ogni anomalia deve essere classificata, assegnata a un responsabile e chiusa con evidenze.",
  "Ogni anomalia deve essere classificata, assegnata a un responsabile e chiusa con evidenze."
];
const output = summarizer.dedupeSentences(input);
console.log(JSON.stringify({ input: input.length, output: output.length }));
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
        raise AssertionError(proc.stderr or proc.stdout)

    import json
    return json.loads(proc.stdout.strip())


def main():
    problemi = []
    html = leggi(PAGINA_REALE)
    universal = leggi(UNIVERSAL)
    scripts = "\n".join(script_src())

    if "rag-motori-intelligenti-browser-v2a19.js" in html:
        problemi.append("V2A19 caricato dalla pagina reale")
    if "rag-quality-summary-cards-v34a.js" in html:
        problemi.append("V34A caricato dalla pagina reale")
    if "test-documenti-universale-pulito-v2a24.html" in html or "v2a24" in html.lower():
        problemi.append("V2A24 usato dalla pagina reale")

    if "../runtime/web/rag-large-document-manager-v1.js" not in scripts:
        problemi.append("manager documenti lunghi non caricato")
    if "../runtime/web/rag-large-document-progressive-summary-v2.js" not in scripts:
        problemi.append("summarizer progressivo non caricato")

    try:
        ponte = corpo_funzione(universal, "applicaQualitaRiassuntoLungoEsistenteV2A29")
        genera_riassunto = corpo_funzione(universal, "generaRiassunto")
        render_lungo = corpo_funzione(universal, "renderizzaRiassuntoLungoV2A28")
        genera_card = corpo_funzione(universal, "generaCardVisive")
        genera_test = corpo_funzione(universal, "generaTest")
        genera_domande = corpo_funzione(universal, "generaDomandeStudio")
    except AssertionError as errore:
        problemi.append(str(errore))
        ponte = genera_riassunto = render_lungo = genera_card = genera_test = genera_domande = ""

    if "createProgressiveSummary" not in genera_riassunto:
        problemi.append("generaRiassunto non usa piu' il motore progressivo")
    if "applicaQualitaRiassuntoLungoEsistenteV2A29(sezioni, testo, profilo)" not in genera_riassunto:
        problemi.append("il riassunto lungo non passa dal ponte qualita' V2A29")
    if "renderizzaRiassuntoLungoV2A28(profilo, progressive, sezioniFinali, qualita.report)" not in genera_riassunto:
        problemi.append("il render lungo non usa sezioni finali revisionate")

    required_bridge_tokens = [
        "correggiSpaziPunteggiaturaV35G",
        "normalizzaTesto",
        "summarizer.normalizeText",
        "summarizer.dedupeSentences",
        "summarizer.areSentencesTooSimilar",
        "deduplicaFrasiRiassuntoLungoV2A28",
        "finali_mozzati_correggibili",
        "frasi_duplicate_rimosse",
        "motori_esistenti_usati",
    ]
    for token in required_bridge_tokens:
        if token not in ponte:
            problemi.append(f"ponte qualita' non usa token atteso: {token}")

    forbidden_quiz_calls = [
        "rag_bridge_motori_qualita_esistenti_v35b",
        "rag_motore_test_riutilizzabile_v35d",
        "creaQuiz(",
        "mappa_opzioni_v35d",
        "risposta_corretta",
        "opzioni_visibili",
    ]
    for token in forbidden_quiz_calls:
        if token in ponte:
            problemi.append(f"ponte qualita' richiama motore/campo quiz-test vietato: {token}")

    if "V35B bridge quiz" not in ponte or "V35D motore test" not in ponte:
        problemi.append("ponte non dichiara esplicitamente l'esclusione dei motori quiz/test")

    for nome, corpo in [
        ("generaCardVisive", genera_card),
        ("generaTest", genera_test),
        ("generaDomandeStudio", genera_domande),
    ]:
        if "applicaQualitaRiassuntoLungoEsistenteV2A29" in corpo or "V2A29" in corpo:
            problemi.append(f"{nome} e' stato modificato/contaminato dal ponte V2A29")

    if 'replace(/\\s+([,.!?;:])/g, "$1")' not in universal:
        problemi.append("V35G non corregge gli spazi prima della punteggiatura")
    v35g = corpo_funzione(universal, "correggiSpaziPunteggiaturaV35G")
    if "throw" in v35g:
        problemi.append("V35G blocca invece di correggere")

    if "Controllo qualità: grammatica, punteggiatura, ripetizioni e coerenza verificati." not in render_lungo:
        problemi.append("report qualita' discreto non visibile nel riassunto lungo")

    if "Sicurezza informatica aziendale" in html or "Sicurezza informatica aziendale" in universal:
        problemi.append("marker demo sicurezza presente nella pagina reale o nel motore universale")

    try:
        dedupe = node_dedupe_check()
        if dedupe["output"] >= dedupe["input"]:
            problemi.append("dedupeSentences non riduce duplicati nella fixture")
    except AssertionError as errore:
        problemi.append("controllo dedupe Node fallito: " + str(errore))

    for path in [MANAGER, SUMMARIZER]:
        proc = subprocess.run(["node", "--check", str(path.relative_to(ROOT))], cwd=ROOT, text=True, capture_output=True)
        if proc.returncode != 0:
            problemi.append(f"node --check fallito per {path.relative_to(ROOT)}: {proc.stderr}")

    if problemi:
        print("QUALITA RIASSUNTO LUNGO V2A29: KO")
        for problema in problemi:
            print(f"- {problema}")
        return 1

    print("QUALITA RIASSUNTO LUNGO V2A29: OK")
    print("- riassunto lungo ancora su manager + progressive summary")
    print("- ponte qualita' V2A29 collegato dopo il motore lungo e prima del render")
    print("- V35G corregge senza bloccare")
    print("- dedupe/coerenza usano funzioni esistenti del summarizer")
    print("- motori quiz/test esclusi dal riassunto")
    return 0


if __name__ == "__main__":
    sys.exit(main())
