from __future__ import annotations

import json
import sys
from pathlib import Path


CAMPI_OBBLIGATORI = [
    "id",
    "categoria",
    "livello",
    "domanda",
    "opzioni",
    "risposta_corretta",
    "spiegazione",
]


def aggiungi_problema(problemi: list[str], messaggio: str) -> None:
    problemi.append(f"- {messaggio}")


def valida_domanda(domanda: dict, posizione: int, problemi: list[str]) -> None:
    for campo in CAMPI_OBBLIGATORI:
        if campo not in domanda:
            aggiungi_problema(
                problemi,
                f"Domanda {posizione}: campo mancante `{campo}`.",
            )

    opzioni = domanda.get("opzioni", [])

    if not isinstance(opzioni, list):
        aggiungi_problema(
            problemi,
            f"Domanda {posizione}: `opzioni` deve essere una lista.",
        )
        return

    if len(opzioni) != 4:
        aggiungi_problema(
            problemi,
            f"Domanda {posizione}: deve avere esattamente 4 opzioni.",
        )

    opzioni_pulite = [
        str(opzione).strip()
        for opzione in opzioni
    ]

    if any(not opzione for opzione in opzioni_pulite):
        aggiungi_problema(
            problemi,
            f"Domanda {posizione}: una o più opzioni sono vuote.",
        )

    if len(set(opzioni_pulite)) != len(opzioni_pulite):
        aggiungi_problema(
            problemi,
            f"Domanda {posizione}: ci sono opzioni duplicate.",
        )

    risposta_corretta = str(domanda.get("risposta_corretta", "")).strip()

    if risposta_corretta and risposta_corretta not in opzioni_pulite:
        aggiungi_problema(
            problemi,
            f"Domanda {posizione}: risposta_corretta non presente tra le opzioni.",
        )

    for campo in ["domanda", "risposta_corretta", "spiegazione"]:
        valore = str(domanda.get(campo, "")).strip()
        if not valore:
            aggiungi_problema(
                problemi,
                f"Domanda {posizione}: `{campo}` è vuoto.",
            )


def main() -> None:
    if len(sys.argv) < 2:
        percorso_file = Path("dist/generated/rag_quiz_generato.json")
    else:
        percorso_file = Path(sys.argv[1])

    if not percorso_file.exists():
        raise SystemExit(f"File non trovato: {percorso_file}")

    dati = json.loads(percorso_file.read_text(encoding="utf-8"))

    problemi: list[str] = []

    if not isinstance(dati, dict):
        aggiungi_problema(problemi, "Il file deve contenere un oggetto JSON.")
        domande = []
    else:
        domande = dati.get("domande", [])

    if not isinstance(domande, list):
        aggiungi_problema(problemi, "`domande` deve essere una lista.")
        domande = []

    if len(domande) == 0:
        stato = "OK - contenitore temporaneo senza domande reali"
        nota = (
            "Il file è valido come contenitore temporaneo. "
            "Non ci sono ancora domande da controllare."
        )
    else:
        for posizione, domanda in enumerate(domande, start=1):
            if not isinstance(domanda, dict):
                aggiungi_problema(
                    problemi,
                    f"Domanda {posizione}: deve essere un oggetto JSON.",
                )
                continue

            valida_domanda(domanda, posizione, problemi)

        stato = "OK" if not problemi else "PROBLEMI TROVATI"
        nota = f"Domande controllate: {len(domande)}"

    Path("reports").mkdir(exist_ok=True)

    report = [
        "# Validazione quiz JSON generato da RAG",
        "",
        f"- File controllato: `{percorso_file}`",
        f"- Stato: {stato}",
        f"- Nota: {nota}",
        "",
    ]

    if problemi:
        report.append("## Problemi")
        report.extend(problemi)
    else:
        report.append("## Risultato")
        report.append("Nessun problema bloccante trovato.")

    Path("reports/rag_validazione_quiz_json.md").write_text(
        "\n".join(report),
        encoding="utf-8",
    )

    print("✅ Validazione RAG quiz JSON completata")
    print(f"📌 Stato: {stato}")
    print("📌 Report: reports/rag_validazione_quiz_json.md")

    if problemi:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
