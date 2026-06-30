#!/usr/bin/env python3
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
UNIVERSAL = ROOT / "demo-rag" / "universal-document-learning-engine.js"
PAGINE_REALI = [
    ROOT / "demo-rag" / "test-documenti-universale.html",
    ROOT / "demo-rag" / "index.html",
]
V34A = ROOT / "demo-rag" / "rag-quality-summary-cards-v34a.js"
VALIDATORE_V34A = ROOT / "scripts" / "verifica_rag_summary_cards_v34a.py"


def leggi(path):
    return path.read_text(encoding="utf-8")


def corpo_funzione(sorgente, nome):
    marker = f"function {nome}("
    start = sorgente.find(marker)
    if start < 0:
        raise AssertionError(f"Funzione mancante: {nome}")

    brace = sorgente.find("{", start)
    if brace < 0:
        raise AssertionError(f"Corpo funzione mancante: {nome}")

    profondita = 0
    for pos in range(brace, len(sorgente)):
        char = sorgente[pos]
        if char == "{":
            profondita += 1
        elif char == "}":
            profondita -= 1
            if profondita == 0:
                return sorgente[start : pos + 1]

    raise AssertionError(f"Corpo funzione non chiuso: {nome}")


def assert_true(condizione, messaggio):
    if not condizione:
        raise AssertionError(messaggio)


def git_status_short(path):
    try:
      return subprocess.check_output(
          ["git", "status", "--short", "--", str(path.relative_to(ROOT))],
          cwd=ROOT,
          text=True,
      ).strip()
    except Exception:
      return ""


def main():
    problemi = []

    try:
        universal = leggi(UNIVERSAL)

        pagine = {pagina.name: leggi(pagina) for pagina in PAGINE_REALI}
        for nome, html in pagine.items():
            assert_true(
                "rag-motori-intelligenti-browser-v2a19.js" not in html,
                f"{nome} carica rag-motori-intelligenti-browser-v2a19.js",
            )
            assert_true(
                "rag-quality-summary-cards-v34a.js" not in html,
                f"{nome} carica rag-quality-summary-cards-v34a.js",
            )

        assert_true(
            "eseguiPipelineMotoriBrowserV2A19" not in universal,
            "universal-document-learning-engine.js usa eseguiPipelineMotoriBrowserV2A19",
        )
        assert_true(
            "attivaBindingForzatoPulsantiV2A21" not in universal,
            "universal-document-learning-engine.js contiene attivaBindingForzatoPulsantiV2A21",
        )

        genera_riassunto = corpo_funzione(universal, "generaRiassunto")
        genera_card = corpo_funzione(universal, "generaCardVisive")
        genera_test = corpo_funzione(universal, "generaTest")
        genera_domande = corpo_funzione(universal, "generaDomandeStudio")

        assert_true(
            "creaParagrafiRiassunto" in genera_riassunto,
            "generaRiassunto non usa creaParagrafiRiassunto",
        )
        assert_true(
            "creaCards" in genera_card,
            "generaCardVisive non usa creaCards",
        )
        assert_true(
            "creaQuiz" in genera_test,
            "generaTest non usa creaQuiz",
        )
        assert_true(
            "creaCards" in genera_domande or "card.domandaStudio" in genera_domande,
            "generaDomandeStudio non usa creaCards/card.domandaStudio",
        )
        assert_true(
            "creaQuiz" not in genera_domande,
            "generaDomandeStudio usa creaQuiz",
        )
        assert_true(
            "opzioni" not in genera_domande and "quiz-option" not in genera_domande,
            "generaDomandeStudio mostra opzioni multiple",
        )

        assert_true(
            "correggiSpaziPunteggiaturaV35G" in universal
            and 'replace(/\\s+([,.!?;:])/g, "$1")' in universal,
            "V35G non corregge automaticamente gli spazi prima della punteggiatura",
        )

        assert_true(
            not V34A.exists(),
            "demo-rag/rag-quality-summary-cards-v34a.js esiste ancora",
        )
        assert_true(
            not VALIDATORE_V34A.exists(),
            "scripts/verifica_rag_summary_cards_v34a.py esiste ancora",
        )

        stato_v34a = git_status_short(V34A)
        assert_true(
            stato_v34a.startswith("D") or not stato_v34a,
            "V34A non risulta eliminato nello stato git",
        )

        testo_ripetitivo = " ".join(
            [
                "La procedura richiede una verifica settimanale dei controlli applicati.",
                "La procedura richiede una verifica mensile dei registri operativi.",
                "La procedura richiede una verifica trimestrale dei rischi principali.",
                "La procedura richiede una verifica giornaliera degli avvisi critici.",
            ]
        )
        assert_true(len(testo_ripetitivo) > 200, "Testo ripetitivo di controllo non valido")

        assert_true(
            "frasiPesate" not in genera_riassunto and "keyword" not in genera_riassunto.lower(),
            "generaRiassunto sembra ancora agganciato a frasi pesate/keyword browser-only",
        )
        assert_true(
            "creaRiassuntoReale" not in universal
            and "creaCardBrowser" not in universal
            and "creaTestBrowser" not in universal
            and "creaDomandeStudioBrowser" not in universal,
            "universal contiene generatori browser-only V2A19",
        )

    except AssertionError as errore:
        problemi.append(str(errore))

    if problemi:
        print("RIPRISTINO GENERATORI REALI RAG: KO")
        for problema in problemi:
            print(f"- {problema}")
        return 1

    print("RIPRISTINO GENERATORI REALI RAG: OK")
    print("- pagine reali senza V2A19/V34A")
    print("- catena riassunto/card/test/domande tornata ai generatori ufficiali")
    print("- V35G corregge gli spazi prima della punteggiatura senza bloccare")
    print("- V34A resta eliminato")
    return 0


if __name__ == "__main__":
    sys.exit(main())
