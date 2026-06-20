from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from rag_valida_distrattori_forti import valuta_domanda_distrattori_forti


CAMPI_OBBLIGATORI = [
    "id",
    "categoria",
    "livello",
    "domanda",
    "opzioni",
    "risposta_corretta",
    "spiegazione",
]

PAROLE_DEBOLI_DISTRACTOR = [
    "tutte le precedenti",
    "nessuna delle precedenti",
    "non so",
    "non riguarda",
    "completamente diverso",
]


def tokenizza(testo: str) -> set[str]:
    parole = re.findall(r"[a-zA-ZÀ-ÿ0-9]+", testo.lower())
    return {
        parola
        for parola in parole
        if len(parola) > 3
    }


def carica_json(percorso: Path) -> dict:
    if not percorso.exists():
        raise SystemExit(f"File non trovato: {percorso}")

    dati = json.loads(percorso.read_text(encoding="utf-8"))

    if isinstance(dati, list):
        return {
            "metadati": {
                "origine": "rag",
                "nota": "Lista normalizzata dal filtro review.",
            },
            "domande": dati,
        }

    if not isinstance(dati, dict):
        raise SystemExit("Il file deve contenere un oggetto JSON o una lista.")

    if "domande" not in dati:
        dati = {
            "metadati": {
                "origine": "rag",
                "nota": "Oggetto singolo normalizzato dal filtro review.",
            },
            "domande": [dati],
        }

    return dati


def valida_domanda(
    domanda: dict,
    posizione: int,
    problemi_bloccanti: list[str],
    avvisi_review: list[str],
) -> None:
    for campo in CAMPI_OBBLIGATORI:
        if campo not in domanda:
            problemi_bloccanti.append(
                f"Domanda {posizione}: campo mancante `{campo}`."
            )

    testo_domanda = str(domanda.get("domanda", "")).strip()
    spiegazione = str(domanda.get("spiegazione", "")).strip()
    risposta_corretta = str(domanda.get("risposta_corretta", "")).strip()
    opzioni = domanda.get("opzioni", [])

    if not testo_domanda:
        problemi_bloccanti.append(f"Domanda {posizione}: testo domanda vuoto.")

    if not spiegazione:
        problemi_bloccanti.append(f"Domanda {posizione}: spiegazione vuota.")

    if not risposta_corretta:
        problemi_bloccanti.append(f"Domanda {posizione}: risposta corretta vuota.")

    if not isinstance(opzioni, list):
        problemi_bloccanti.append(f"Domanda {posizione}: `opzioni` deve essere una lista.")
        return

    if len(opzioni) != 4:
        problemi_bloccanti.append(
            f"Domanda {posizione}: deve avere esattamente 4 opzioni."
        )
        return

    opzioni_pulite = [
        str(opzione).strip()
        for opzione in opzioni
    ]

    if any(not opzione for opzione in opzioni_pulite):
        problemi_bloccanti.append(
            f"Domanda {posizione}: una o più opzioni sono vuote."
        )

    if len(set(opzioni_pulite)) != 4:
        problemi_bloccanti.append(
            f"Domanda {posizione}: ci sono opzioni duplicate."
        )

    if risposta_corretta and risposta_corretta not in opzioni_pulite:
        problemi_bloccanti.append(
            f"Domanda {posizione}: risposta corretta non presente tra le opzioni."
        )

    if len(testo_domanda) < 25:
        avvisi_review.append(
            f"Domanda {posizione}: domanda molto breve, controllare se è abbastanza chiara."
        )

    if len(spiegazione) < 45:
        avvisi_review.append(
            f"Domanda {posizione}: spiegazione breve, potrebbe non essere abbastanza didattica."
        )

    distrattori = [
        opzione
        for opzione in opzioni_pulite
        if opzione != risposta_corretta
    ]

    for distrattore in distrattori:
        distrattore_lower = distrattore.lower()

        for parola_debole in PAROLE_DEBOLI_DISTRACTOR:
            if parola_debole in distrattore_lower:
                avvisi_review.append(
                    f"Domanda {posizione}: possibile distrattore debole: `{distrattore}`."
                )

    avvisi_distrattori = valuta_domanda_distrattori_forti(
        domanda=domanda,
        posizione=posizione,
    )

    for avviso in avvisi_distrattori:
        avvisi_review.append(
            f"Domanda {posizione}: {avviso['messaggio']}"
        )

    lunghezze = [
        len(opzione)
        for opzione in opzioni_pulite
        if opzione
    ]

    if lunghezze:
        lunghezza_minima = min(lunghezze)
        lunghezza_massima = max(lunghezze)

        if lunghezza_minima > 0 and lunghezza_massima / lunghezza_minima > 2.8:
            avvisi_review.append(
                f"Domanda {posizione}: opzioni con lunghezze molto diverse, la risposta potrebbe risaltare."
            )

    if not str(domanda.get("fonte_rag", "")).strip():
        avvisi_review.append(
            f"Domanda {posizione}: manca `fonte_rag`, utile per controllare la fonte."
        )


def prepara_domanda_review(domanda: dict, posizione: int) -> dict:
    return {
        "id_review": f"RAG-REV-{positione_corretta(posizione)}",
        "id_originale": str(domanda.get("id", f"RAG-{posizione:04d}")),
        "categoria": str(domanda.get("categoria", "rag_generato")),
        "livello": str(domanda.get("livello", "intermedio")),
        "domanda": str(domanda.get("domanda", "")).strip(),
        "opzioni": [
            str(opzione).strip()
            for opzione in domanda.get("opzioni", [])
        ],
        "risposta_corretta": str(domanda.get("risposta_corretta", "")).strip(),
        "spiegazione": str(domanda.get("spiegazione", "")).strip(),
        "fonte_rag": str(domanda.get("fonte_rag", "")).strip(),
        "regola_distrattori": str(
            domanda.get("regola_distrattori", "tre_distrattori_forti")
        ),
        "stato_review": "da_revisionare",
        "nota_importante": (
            "Questa domanda NON è ancora nel database ufficiale. "
            "Va revisionata prima di qualsiasi importazione."
        ),
        "checklist_review": {
            "fonte_rag_verificata": False,
            "domanda_chiara": False,
            "risposta_corretta_verificata": False,
            "tre_distrattori_forti": False,
            "spiegazione_didattica": False,
            "lingua_controllata": False,
            "approvata_per_database_ufficiale": False,
        },
    }


def positione_corretta(posizione: int) -> str:
    return f"{posizione:04d}"


def crea_report(
    percorso_input: Path,
    percorso_output: Path,
    numero_domande: int,
    problemi_bloccanti: list[str],
    avvisi_review: list[str],
) -> str:
    stato = "OK"

    if problemi_bloccanti:
        stato = "BLOCCATO"

    righe = [
        "# Review quiz generato da RAG",
        "",
        f"- File sorgente: `{percorso_input}`",
        f"- File review: `{percorso_output}`",
        f"- Domande trovate: {numero_domande}",
        f"- Stato: {stato}",
        "",
    ]

    if numero_domande == 0:
        righe.extend(
            [
                "## Nota",
                "",
                "Il file contiene zero domande reali. Questo va bene in modalità sicura.",
                "La pipeline ha creato solo il contenitore temporaneo.",
                "",
            ]
        )

    if problemi_bloccanti:
        righe.append("## Problemi bloccanti")
        righe.append("")
        righe.extend(f"- {problema}" for problema in problemi_bloccanti)
        righe.append("")

    if avvisi_review:
        righe.append("## Avvisi da revisionare")
        righe.append("")
        righe.extend(f"- {avviso}" for avviso in avvisi_review)
        righe.append("")

    if not problemi_bloccanti and not avvisi_review:
        righe.append("## Risultato")
        righe.append("")
        righe.append("Nessun problema bloccante e nessun avviso rilevato.")
        righe.append("")

    righe.extend(
        [
            "## Regola di sicurezza",
            "",
            "Questo script non modifica mai i file dentro `data/`.",
            "Le domande generate dal RAG passano prima dalla cartella `review/rag/`.",
            "Solo dopo revisione e approvazione potranno essere importate nei database ufficiali.",
            "",
        ]
    )

    return "\n".join(righe)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepara la review sicura di un quiz JSON generato dal RAG."
    )

    parser.add_argument(
        "--input",
        default="dist/generated/rag_quiz_generato.json",
    )

    parser.add_argument(
        "--output",
        default="review/rag/quiz_da_revisionare.json",
    )

    parser.add_argument(
        "--report",
        default="reports/rag_review_quiz.md",
    )

    args = parser.parse_args()

    percorso_input = Path(args.input)
    percorso_output = Path(args.output)
    percorso_report = Path(args.report)

    dati = carica_json(percorso_input)
    domande = dati.get("domande", [])

    if not isinstance(domande, list):
        raise SystemExit("La chiave `domande` deve contenere una lista.")

    problemi_bloccanti: list[str] = []
    avvisi_review: list[str] = []

    domande_review = []

    for posizione, domanda in enumerate(domande, start=1):
        if not isinstance(domanda, dict):
            problemi_bloccanti.append(
                f"Domanda {posizione}: elemento non valido, deve essere un oggetto JSON."
            )
            continue

        valida_domanda(
            domanda=domanda,
            posizione=posizione,
            problemi_bloccanti=problemi_bloccanti,
            avvisi_review=avvisi_review,
        )

        domande_review.append(
            prepara_domanda_review(
                domanda=domanda,
                posizione=posizione,
            )
        )

    review = {
        "metadati": {
            "origine": "rag",
            "tipo": "review_prima_di_database_ufficiale",
            "file_sorgente": str(percorso_input),
            "numero_domande": len(domande_review),
            "stato": "bloccato" if problemi_bloccanti else "da_revisionare",
            "regola_sicurezza": (
                "Questo file non modifica i database ufficiali. "
                "Serve solo per revisione controllata."
            ),
        },
        "domande_da_revisionare": domande_review,
    }

    percorso_output.parent.mkdir(parents=True, exist_ok=True)
    percorso_output.write_text(
        json.dumps(review, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    percorso_report.parent.mkdir(parents=True, exist_ok=True)
    percorso_report.write_text(
        crea_report(
            percorso_input=percorso_input,
            percorso_output=percorso_output,
            numero_domande=len(domande),
            problemi_bloccanti=problemi_bloccanti,
            avvisi_review=avvisi_review,
        ),
        encoding="utf-8",
    )

    print("✅ Review RAG preparata")
    print(f"📌 File review locale: {percorso_output}")
    print(f"📌 Report: {percorso_report}")

    if problemi_bloccanti:
        print("❌ Problemi bloccanti trovati. Il file NON è pronto.")
        raise SystemExit(1)

    if avvisi_review:
        print(f"⚠️ Avvisi da controllare: {len(avvisi_review)}")
    else:
        print("✅ Nessun avviso di review")


if __name__ == "__main__":
    main()
