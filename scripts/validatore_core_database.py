from pathlib import Path
import json
import re
import sys

ROOT = Path.cwd()
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

REPORT_MD = REPORTS / "validatore_core_database.md"
REPORT_JSON = REPORTS / "validatore_core_database.json"

OFFICIAL_FILES = [
    ("Scienze generali", "data/scienze.json"),
    ("Biologia", "data/biologia.json"),
    ("Chimica", "data/chimica.json"),
    ("Fisica", "data/fisica.json"),
    ("Fisica quantistica", "data/fisica_quantistica.json"),
    ("AI", "data/ai.json"),
    ("Informatica", "data/informatica.json"),
    ("Matematica", "data/matematica.json"),
    ("Inglese", "data/inglese.json"),
    ("Logica numerica", "data/logica/logica_numerica.json"),
    ("Logica verbale", "data/logica/logica_verbale.json"),
    ("Ragionamento astratto", "data/logica/ragionamento_astratto.json"),
    ("Ragionamento critico", "data/logica/ragionamento_critico.json"),
    ("Logica visiva", "data/logica/logica_visiva.json"),
]

VALID_LEVELS = {"facile", "intermedio", "avanzato"}
OPTION_KEYS = ["A", "B", "C", "D"]


def normalize_text(value):
    text = str(value or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def compact_text(value):
    text = normalize_text(value)

    # Mantiene simboli matematici importanti.
    # Prima eliminavamo caratteri come ² e +, quindi x² + C poteva diventare troppo simile a x + C.
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

    text = re.sub(r"[^a-z0-9àèéìòùç+\-*/=^()\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def get_question_id(item):
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


def get_explanation(item):
    for key in ["spiegazione", "explanation", "motivazione"]:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def get_level(item):
    return normalize_text(item.get("livello") or item.get("difficulty") or "")


def get_category(item):
    return normalize_text(item.get("categoria") or item.get("category") or "")


def option_to_text(value):
    if isinstance(value, str):
        return value.strip()

    if isinstance(value, dict):
        for key in ["testo", "text", "label", "risposta", "answer"]:
            nested = value.get(key)
            if isinstance(nested, str) and nested.strip():
                return nested.strip()

    return str(value).strip()


def get_options(item):
    raw = (
        item.get("opzioni")
        or item.get("options")
        or item.get("risposte")
        or item.get("answers")
    )

    if isinstance(raw, dict):
        result = {}
        for key in OPTION_KEYS:
            if key in raw:
                result[key] = option_to_text(raw[key])
        return result

    if isinstance(raw, list):
        result = {}
        for index, value in enumerate(raw[:4]):
            result[OPTION_KEYS[index]] = option_to_text(value)
        return result

    return {}


def get_correct_answer(item):
    for key in [
        "risposta_corretta",
        "risposta_corretta_testo",
        "correct_answer",
        "answer",
    ]:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def get_correct_letter(item):
    for key in [
        "risposta_corretta_lettera",
        "lettera_corretta",
        "correct_option",
        "correct_letter",
    ]:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().upper()
    return ""


def answer_matches_options(answer, correct_letter, options):
    if not options:
        return False

    if answer.upper() in options:
        return True

    if correct_letter in options:
        expected_text = normalize_text(options[correct_letter])
        answer_text = normalize_text(answer)

        if expected_text and answer_text and expected_text == answer_text:
            return True

    answer_text = normalize_text(answer)

    for option_text in options.values():
        if normalize_text(option_text) == answer_text:
            return True

    return False


def check_for_backup_json_inside_data():
    problems = []

    data_dir = ROOT / "data"

    if not data_dir.exists():
        return problems

    for path in data_dir.rglob("*.json"):
        lower = path.name.lower()

        if "backup" in lower or ".bak" in lower:
            problems.append({
                "file": str(path.relative_to(ROOT)),
                "id": "",
                "tipo": "file_non_ufficiale_in_data",
                "messaggio": "File backup/non ufficiale trovato dentro data/: i motori potrebbero scansionarlo come database reale.",
            })

    return problems


def validate_question(file_label, file_path, item, index):
    problems = []
    warnings = []

    qid = get_question_id(item)
    question_text = get_question_text(item)
    explanation = get_explanation(item)
    level = get_level(item)
    category = get_category(item)
    options = get_options(item)
    answer = get_correct_answer(item)
    correct_letter = get_correct_letter(item)

    location = qid or f"indice_{index + 1}"

    if not qid:
        problems.append("manca id/codice domanda")

    if not question_text:
        problems.append("manca testo domanda")

    if not explanation:
        problems.append("manca spiegazione")

    if not level:
        problems.append("manca livello")
    elif level not in VALID_LEVELS:
        problems.append(f"livello non valido: {level}")

    if not category:
        warnings.append("categoria mancante o vuota")

    if len(options) != 4:
        problems.append(f"numero opzioni non valido: {len(options)}, attese 4")

    if len(options) == 4:
        missing_option_keys = [key for key in OPTION_KEYS if key not in options]

        if missing_option_keys:
            problems.append(f"mancano opzioni: {missing_option_keys}")

        empty_options = [key for key, value in options.items() if not value.strip()]

        if empty_options:
            problems.append(f"opzioni vuote: {empty_options}")

        normalized_options = [compact_text(value) for value in options.values()]
        unique_options = set(normalized_options)

        if len(unique_options) != len(normalized_options):
            problems.append("opzioni duplicate o quasi identiche nello stesso quiz")

    if not answer:
        problems.append("manca risposta_corretta")
    elif options and not answer_matches_options(answer, correct_letter, options):
        problems.append("risposta_corretta non coincide con nessuna delle 4 opzioni")

    if correct_letter and correct_letter not in OPTION_KEYS:
        problems.append(f"risposta_corretta_lettera non valida: {correct_letter}")

    is_visual = qid.startswith("LOG-VIS")

    if not is_visual:
        answer_compact = compact_text(answer)
        question_compact = compact_text(question_text)

        if answer_compact and len(answer_compact) >= 18 and answer_compact in question_compact:
            warnings.append("la risposta corretta sembra comparire già nel testo della domanda")

    return [
        {
            "file": str(file_path),
            "id": location,
            "tipo": "problema",
            "messaggio": message,
        }
        for message in problems
    ], [
        {
            "file": str(file_path),
            "id": location,
            "tipo": "avviso",
            "messaggio": message,
        }
        for message in warnings
    ]


def main():
    all_problems = []
    all_warnings = []
    all_ids = {}
    all_questions = {}

    all_problems.extend(check_for_backup_json_inside_data())

    total_questions = 0

    for label, relative_path in OFFICIAL_FILES:
        path = ROOT / relative_path

        if not path.exists():
            all_problems.append({
                "file": relative_path,
                "id": "",
                "tipo": "file_mancante",
                "messaggio": f"File ufficiale mancante: {relative_path}",
            })
            continue

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as error:
            all_problems.append({
                "file": relative_path,
                "id": "",
                "tipo": "json_non_valido",
                "messaggio": f"JSON non leggibile: {error}",
            })
            continue

        if not isinstance(data, list):
            all_problems.append({
                "file": relative_path,
                "id": "",
                "tipo": "struttura_non_valida",
                "messaggio": "Il file deve contenere una lista di domande.",
            })
            continue

        if not data:
            all_problems.append({
                "file": relative_path,
                "id": "",
                "tipo": "file_vuoto",
                "messaggio": "Il file non contiene domande.",
            })
            continue

        total_questions += len(data)

        for index, item in enumerate(data):
            if not isinstance(item, dict):
                all_problems.append({
                    "file": relative_path,
                    "id": f"indice_{index + 1}",
                    "tipo": "elemento_non_oggetto",
                    "messaggio": "La domanda non è un oggetto JSON.",
                })
                continue

            qid = get_question_id(item)
            question_text = get_question_text(item)

            problems, warnings = validate_question(label, relative_path, item, index)
            all_problems.extend(problems)
            all_warnings.extend(warnings)

            if qid:
                if qid in all_ids:
                    all_problems.append({
                        "file": relative_path,
                        "id": qid,
                        "tipo": "id_duplicato",
                        "messaggio": f"ID già usato in {all_ids[qid]}",
                    })
                else:
                    all_ids[qid] = relative_path

            if qid and not qid.startswith("LOG-VIS"):
                normalized_question = compact_text(question_text)

                if normalized_question:
                    if normalized_question in all_questions:
                        all_problems.append({
                            "file": relative_path,
                            "id": qid,
                            "tipo": "domanda_duplicata",
                            "messaggio": f"Domanda identica già presente in {all_questions[normalized_question]}",
                        })
                    else:
                        all_questions[normalized_question] = qid

    result = {
        "esito": "KO" if all_problems else "OK",
        "domande_totali_controllate": total_questions,
        "problemi": all_problems,
        "avvisi": all_warnings,
    }

    REPORT_JSON.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Validatore core database",
        "",
        f"Domande totali controllate: {total_questions}",
        f"Problemi bloccanti: {len(all_problems)}",
        f"Avvisi: {len(all_warnings)}",
        "",
    ]

    if all_problems:
        lines.extend(["## Problemi bloccanti", ""])

        for problem in all_problems:
            lines.append(
                f"- `{problem['file']}` `{problem['id']}`: {problem['messaggio']}"
            )

    if all_warnings:
        lines.extend(["", "## Avvisi", ""])

        for warning in all_warnings:
            lines.append(
                f"- `{warning['file']}` `{warning['id']}`: {warning['messaggio']}"
            )

    if not all_problems:
        lines.extend(["## Esito", "", "✅ Nessun problema bloccante trovato."])

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if all_problems:
        print("❌ Validatore core database fallito.")
        print(f"Problemi bloccanti: {len(all_problems)}")
        print(f"Report: {REPORT_MD}")
        for problem in all_problems[:40]:
            print(f"- {problem['file']} {problem['id']}: {problem['messaggio']}")
        if len(all_problems) > 40:
            print(f"... altri {len(all_problems) - 40} problemi nel report.")
        sys.exit(1)

    print("✅ Validatore core database superato.")
    print(f"Domande controllate: {total_questions}")
    print(f"Avvisi non bloccanti: {len(all_warnings)}")
    print(f"Report: {REPORT_MD}")


if __name__ == "__main__":
    main()
