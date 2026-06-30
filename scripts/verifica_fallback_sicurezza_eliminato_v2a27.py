#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
PAGINA_REALE = ROOT / "demo-rag" / "test-documenti-universale.html"
INDEX = ROOT / "demo-rag" / "index.html"
UNIVERSAL = ROOT / "demo-rag" / "universal-document-learning-engine.js"

MARKER_DEMO = [
    "Sicurezza informatica aziendale",
    "E-mail sospette",
    "Password manager",
    "Aggiornamenti controllati",
    "Rischi e controlli",
    "La sicurezza informatica comprende pratiche",
    "documento_rag_sicurezza_informatica_aziendale",
]


class ScriptParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "script":
            return
        values = dict(attrs)
        src = values.get("src")
        if src:
            self.scripts.append(src)


def leggi(path):
    return path.read_text(encoding="utf-8")


def marker_presenti(testo):
    return [marker for marker in MARKER_DEMO if marker in testo]


def script_locali_caricati():
    parser = ScriptParser()
    parser.feed(leggi(PAGINA_REALE))
    locali = []

    for src in parser.scripts:
        src_senza_query = src.split("?", 1)[0]
        if src_senza_query.startswith(("http://", "https://")):
            continue
        path = (PAGINA_REALE.parent / src_senza_query).resolve()
        try:
            path.relative_to(ROOT)
        except ValueError:
            continue
        locali.append(path)

    return locali


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


def main():
    problemi = []
    html = leggi(PAGINA_REALE)

    presenti_pagina = marker_presenti(html)
    if presenti_pagina:
        problemi.append(
            "test-documenti-universale.html contiene marker demo: "
            + ", ".join(presenti_pagina)
        )

    if "rag-quality-summary-cards-v34a.js" in html:
        problemi.append("V34A e' ancora caricato dalla pagina reale")

    if "rag-motori-intelligenti-browser-v2a19.js" in html:
        problemi.append("V2A19 e' ancora caricato dalla pagina reale")

    runtime = script_locali_caricati()
    for path in runtime:
        if not path.exists():
            problemi.append(f"Script caricato ma mancante: {path.relative_to(ROOT)}")
            continue

        testo = leggi(path)
        presenti = marker_presenti(testo)
        if presenti:
            problemi.append(
                f"Script runtime {path.relative_to(ROOT)} contiene fallback demo utilizzabile: "
                + ", ".join(presenti)
            )

    universal = leggi(UNIVERSAL)
    presenti_universal = marker_presenti(universal)
    if presenti_universal:
        problemi.append(
            "universal-document-learning-engine.js contiene testo demo come fallback: "
            + ", ".join(presenti_universal)
        )

    try:
        leggi_testo = corpo_funzione(universal, "leggiTesto")
        if "Sicurezza informatica" in leggi_testo or "documento_rag_sicurezza" in leggi_testo:
            problemi.append("leggiTesto contiene un fallback demo sicurezza")
        if not re.search(r"return\s+input\s*\?\s*input\.value\s*:\s*\"\"", leggi_testo):
            problemi.append("leggiTesto non risulta limitata al valore della textarea")
    except AssertionError as errore:
        problemi.append(str(errore))

    if "Documento mancante" not in universal or "Incolla o carica prima un documento." not in universal:
        problemi.append("input vuoto non mostra errore chiaro nel motore universale")

    concept_engine = ROOT / "demo-rag" / "rag-concept-document-engine-v46.js"
    if concept_engine in runtime:
        concept = leggi(concept_engine)
        if "if (text.length < 40) return null;" not in concept:
            problemi.append("concept engine non blocca input insufficiente")
        if "Carica un testo con contenuti reali" not in concept:
            problemi.append("concept engine non mostra errore chiaro su contenuto insufficiente")

    index = leggi(INDEX)
    if "rag-quality-summary-cards-v34a.js" in index:
        problemi.append("V34A e' ancora caricato da index.html")
    if "rag-motori-intelligenti-browser-v2a19.js" in index:
        problemi.append("V2A19 e' ancora caricato da index.html")

    if problemi:
        print("FALLBACK SICUREZZA V2A27: KO")
        for problema in problemi:
            print(f"- {problema}")
        return 1

    print("FALLBACK SICUREZZA V2A27: OK")
    print("- pagina reale senza marker demo sicurezza")
    print("- script runtime caricati senza fallback demo utilizzabile")
    print("- input vuoto produce errore/nessun contenuto, non fallback")
    print("- V34A e V2A19 restano non caricati")
    return 0


if __name__ == "__main__":
    sys.exit(main())
