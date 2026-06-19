from pathlib import Path
import json
import re
import sys
from collections import Counter
from difflib import SequenceMatcher

ROOT = Path.cwd()
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

REPORT_MD = REPORTS / "validatore_duplicati_database.md"
REPORT_JSON = REPORTS / "validatore_duplicati_database.json"

OFFICIAL_FILES = [
    "data/scienze.json",
    "data/biologia.json",
    "data/chimica.json",
    "data/fisica.json",
    "data/fisica_quantistica.json",
    "data/ai.json",
    "data/informatica.json",
    "data/matematica.json",
    "data/inglese.json",
    "data/logica/logica_numerica.json",
    "data/logica/logica_verbale.json",
    "data/logica/ragionamento_astratto.json",
    "data/logica/ragionamento_critico.json",
    "data/logica/logica_visiva.json",
]


def normalize(value):
    text = str(value or "").lower().strip()

    replacements = {
        "²": "2",
        "³": "3",
        "⁴": "4",
        "⁵": "5",
        "⁶": "6",
        "⁷": "7",
        "⁸": "8",
        "⁹": "9",
        "⁰": "0",
        "−": "-",
        "×": "*",
        "÷": "/",
    }

    for source, target in replacements.items():
        text = text.replace(source, target)

    # Il trattino è messo in fondo alla classe caratteri per evitare range regex errati.
    text = re.sub(r"[^a-z0-9àèéìòùç+*/=^()\s-]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def load_questions(path):
    data = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ["domande", "questions", "quiz", "data"]:
            value = data.get(key)

            if isinstance(value, list):
                return value

    raise ValueError(f"Formato database non riconosciuto: {path}")


def get_id(item):
    return str(
        item.get("id")
        or item.get("codice")
        or item.get("question_id")
        or item.get("uid")
        or ""
    ).strip()


def get_question_text(item):
    for key in ["domanda", "question", "testo", "testo_domanda", "prompt"]:
        value = item.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

    return ""


def get_options(item):
    raw = (
        item.get("opzioni")
        or item.get("options")
        or item.get("risposte")
        or item.get("answers")
    )

    if isinstance(raw, list):
        return [str(value).strip() for value in raw]

    if isinstance(raw, dict):
        return [str(raw.get(key, "")).strip() for key in ["A", "B", "C", "D"]]

    return []


def main():
    problems = []
    warnings = []
    all_items = []

    for relative_path in OFFICIAL_FILES:
        path = ROOT / relative_path

        try:
            questions = load_questions(path)
        except Exception as error:
            problems.append({
                "file": relative_path,
                "id": "",
                "messaggio": f"Errore lettura file: {error}",
            })
            continue

        for item in questions:
            if not isinstance(item, dict):
                problems.append({
                    "file": relative_path,
                    "id": "",
                    "messaggio": "Elemento non oggetto JSON.",
                })
                continue

            all_items.append((relative_path, item))

    ids = [get_id(item) for _, item in all_items]
    id_counts = Counter(ids)

    for question_id, count in id_counts.items():
        if question_id and count > 1:
            problems.append({
                "file": "database ufficiali",
                "id": question_id,
                "messaggio": f"ID duplicato usato {count} volte",
            })

    question_texts = {}

    for relative_path, item in all_items:
        question_id = get_id(item)
        question_text = normalize(get_question_text(item))

        # Per LOG-VIS il testo della domanda può essere volutamente neutro e identico.
        # La distinzione reale sta nelle immagini, nelle opzioni e nel visual_logic.
        # Quindi non blocchiamo i duplicati testuali delle domande visive.
        if question_text and not question_id.startswith("LOG-VIS"):
            if question_text in question_texts:
                problems.append({
                    "file": relative_path,
                    "id": question_id,
                    "messaggio": f"Domanda identica a {question_texts[question_text]}",
                })
            else:
                question_texts[question_text] = question_id

        options = get_options(item)
        normalized_options = [normalize(option) for option in options if option]

        if len(normalized_options) != len(set(normalized_options)):
            problems.append({
                "file": relative_path,
                "id": question_id,
                "messaggio": "Opzioni duplicate o identiche nella stessa domanda",
            })

    textual_questions = [
        (relative_path, get_id(item), normalize(get_question_text(item)))
        for relative_path, item in all_items
        if not get_id(item).startswith("LOG-VIS")
    ]

    for index, (file_a, id_a, text_a) in enumerate(textual_questions):
        if len(text_a) < 45:
            continue

        for file_b, id_b, text_b in textual_questions[index + 1:]:
            if len(text_b) < 45:
                continue

            if id_a == id_b:
                continue

            score = SequenceMatcher(None, text_a, text_b).ratio()

            if score >= 0.965:
                warnings.append({
                    "id_a": id_a,
                    "id_b": id_b,
                    "similarita": round(score, 4),
                    "messaggio": "Domande molto simili: verificare se sono davvero distinte",
                })

    result = {
        "esito": "KO" if problems else "OK",
        "domande_controllate": len(all_items),
        "problemi": problems,
        "avvisi": warnings,
    }

    REPORT_JSON.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Validatore duplicati database",
        "",
        f"Domande controllate: {len(all_items)}",
        f"Problemi bloccanti: {len(problems)}",
        f"Avvisi similarità: {len(warnings)}",
        "",
    ]

    if problems:
        lines.extend(["## Problemi bloccanti", ""])
        for problem in problems:
            lines.append(
                f"- `{problem['file']}` `{problem['id']}`: {problem['messaggio']}"
            )
    else:
        lines.extend(["## Problemi bloccanti", "", "✅ Nessun duplicato bloccante."])

    if warnings:
        lines.extend(["", "## Avvisi similarità", ""])
        for warning in warnings[:80]:
            lines.append(
                f"- `{warning['id_a']}` / `{warning['id_b']}` "
                f"similarità {warning['similarita']}: {warning['messaggio']}"
            )

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if problems:
        print("❌ Validatore duplicati database fallito.")
        print(f"Problemi bloccanti: {len(problems)}")
        print(f"Report: {REPORT_MD}")
        for problem in problems[:40]:
            print(f"- {problem['file']} {problem['id']}: {problem['messaggio']}")
        sys.exit(1)

    print("✅ Validatore duplicati database superato.")
    print(f"Domande controllate: {len(all_items)}")
    print(f"Avvisi similarità: {len(warnings)}")
    print(f"Report: {REPORT_MD}")


if __name__ == "__main__":
    main()
