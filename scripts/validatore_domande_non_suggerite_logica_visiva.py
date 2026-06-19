from pathlib import Path
import json
import re
import sys

ROOT = Path.cwd()
DATA_PATH = ROOT / "data/logica/logica_visiva.json"
REPORT_MD = ROOT / "reports/validatore_domande_non_suggerite_logica_visiva.md"
REPORT_JSON = ROOT / "reports/validatore_domande_non_suggerite_logica_visiva.json"

REPORT_MD.parent.mkdir(exist_ok=True)

LEAK_PATTERNS = [
    "la risposta corretta",
    "deve rispettare",
    "forma resta",
    "forma aumenta",
    "forma cresce",
    "colore alterna",
    "colore resta",
    "lati aumentano",
    "aumenta il numero di lati",
    "numero di lati",
    "pallini interni",
    "quadratini interni",
    "triangoli interni",
    "triangolo interno",
    "oggetti interni",
    "resta un triangolo",
    "restano tre",
    "aumentano di uno",
    "alternano tre",
]


def get_id(item):
    if not isinstance(item, dict):
        return ""

    return str(
        item.get("id")
        or item.get("codice")
        or item.get("question_id")
        or item.get("uid")
        or ""
    )


def is_log_vis(codice):
    return codice.startswith("LOG-VIS")


def get_question(item):
    for key in ["domanda", "question", "testo"]:
        value = item.get(key)

        if isinstance(value, str):
            return value

    return ""


def main():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    problemi = []

    for item in data:
        codice = get_id(item)

        if not is_log_vis(codice):
            continue

        question = get_question(item)
        question_lower = question.lower()

        leaks = [
            pattern
            for pattern in LEAK_PATTERNS
            if pattern in question_lower
        ]

        if leaks:
            problemi.append({
                "id": codice,
                "domanda": question,
                "indizi_trovati": leaks,
            })

    REPORT_JSON.write_text(
        json.dumps(
            {
                "file": str(DATA_PATH),
                "problemi": problemi,
                "esito": "KO" if problemi else "OK",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Validatore domande non suggerite Logica visiva",
        "",
        f"File controllato: `{DATA_PATH}`",
        f"Problemi trovati: {len(problemi)}",
        "",
    ]

    if problemi:
        lines.extend(["## Problemi", ""])

        for problema in problemi:
            lines.append(
                f"- `{problema['id']}` contiene indizi nella domanda: "
                f"{problema['indizi_trovati']}"
            )
            lines.append(f"  - Domanda: {problema['domanda']}")

    else:
        lines.extend([
            "## Esito",
            "",
            "✅ Nessuna domanda di Logica visiva contiene la logica dell'esercizio.",
        ])

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if problemi:
        print("❌ Domande suggerite trovate in Logica visiva.")
        for problema in problemi:
            print(f"- {problema['id']}: {problema['indizi_trovati']}")
        print(f"Report: {REPORT_MD}")
        sys.exit(1)

    print("✅ Validatore domande non suggerite Logica visiva superato.")
    print(f"Report: {REPORT_MD}")


if __name__ == "__main__":
    main()
