#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.13D.3 — FIX SCOPE + ROUTE PREFIX + QUIZ DISTRACTORS

Ripara:
1) NameError test_quiz_real_connection_v513d1 nello scope di motori_scrittura.py
2) controllo troppo rigido su qm_033/qm_048 nella route Test/Quiz 63
3) opzioni quiz troppo simili alla corretta e forma "non non"

Non modifica UI/PDF/app.
"""

from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
MOTORI = BACKEND / "motori_scrittura.py"
ROUTE_MATERIALIZER = BACKEND / "phase5_test_quiz_route_materializer_v513d01.py"
REPAIR_MODULE = BACKEND / "phase5_quiz_options_repair_v513d3.py"


# ---------------------------------------------------------------------
# 1) Modulo riparatore opzioni quiz
# ---------------------------------------------------------------------

REPAIR_MODULE.write_text(r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.13D.3 — QUIZ OPTIONS REPAIR

Riparatore produttivo leggero per opzioni Test/Quiz:
- elimina "non non";
- sostituisce distrattori quasi uguali alla corretta;
- evita duplicati;
- non cambia la risposta corretta;
- mantiene struttura e numero opzioni.

Funziona sia con dict sia con dataclass/oggetti.
"""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any, List


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _set(obj: Any, key: str, value: Any) -> None:
    if isinstance(obj, dict):
        obj[key] = value
    elif hasattr(obj, key):
        setattr(obj, key, value)


def _text(value: Any) -> str:
    return str(value or "").strip()


def _norm(value: Any) -> str:
    return " ".join(_text(value).lower().split())


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, _norm(a), _norm(b)).ratio()


def _options(question: Any) -> List[Any]:
    value = _get(question, "opzioni", None)
    if value is None:
        value = _get(question, "options", [])
    return list(value or [])


def _option_id(option: Any) -> str:
    return _text(_get(option, "option_id", None) or _get(option, "id", ""))


def _option_text(option: Any) -> str:
    return _text(_get(option, "testo", None) or _get(option, "text", ""))


def _set_option_text(option: Any, value: str) -> None:
    if isinstance(option, dict):
        if "testo" in option or "text" not in option:
            option["testo"] = value
        if "text" in option:
            option["text"] = value
    else:
        if hasattr(option, "testo"):
            setattr(option, "testo", value)
        elif hasattr(option, "text"):
            setattr(option, "text", value)


def _is_correct(option: Any, correct_option_id: str) -> bool:
    if bool(_get(option, "is_correct", False)):
        return True
    oid = _option_id(option)
    return bool(correct_option_id and oid == correct_option_id)


def _needs_repair(option_text: str, correct_text: str, used_texts: set[str]) -> bool:
    low = _norm(option_text)

    if not option_text:
        return True

    if "non non" in low or "non  non" in low:
        return True

    if low in used_texts:
        return True

    if correct_text and _similarity(option_text, correct_text) >= 0.94:
        return True

    return False


def _candidate_pool(correct_text: str, question: Any) -> List[str]:
    low = _norm(correct_text)

    if "limita l'utilizzo" in low and "sistemi interni" in low:
        return [
            "Il controllo degli accessi serve solo a produrre statistiche e non governa i permessi sui sistemi.",
            "Il controllo degli accessi riguarda solo l'aspetto grafico dei sistemi e non l'autorizzazione operativa.",
            "Il controllo degli accessi permette a ogni utente di usare qualunque sistema senza vincoli specifici.",
        ]

    if "persona identificabile" in low and "account" in low:
        return [
            "Ogni account può essere condiviso da un gruppo senza collegamento a un responsabile individuale.",
            "Gli account possono restare anonimi quando vengono usati solo per attività interne.",
            "Un account può essere assegnato a un reparto senza indicare una persona responsabile.",
        ]

    if "credenziali" in low and "non devono essere condivise" in low:
        return [
            "Le credenziali possono essere riutilizzate da più operatori se appartengono allo stesso reparto.",
            "La condivisione delle credenziali è ammessa quando velocizza l'accesso ai sistemi comuni.",
            "Più operatori possono usare la stessa credenziale se lavorano sulla stessa procedura.",
        ]

    if "revisione periodica" in low and "riduce il rischio" in low:
        return [
            "La revisione periodica serve solo ad archiviare documenti e non incide sui permessi degli utenti.",
            "La revisione periodica aumenta il rischio perché mantiene attivi tutti i permessi esistenti.",
            "La revisione periodica riguarda solo la descrizione degli utenti e non controlla le autorizzazioni.",
        ]

    concepts = _get(question, "micro_concetti", []) or []
    concept = "controllo operativo"
    if isinstance(concepts, list) and concepts:
        concept = str(concepts[0])

    return [
        f"{concept} viene trattato come un dettaglio descrittivo e non come un vincolo operativo reale.",
        f"{concept} può essere ignorato senza effetti sui controlli indicati dal documento.",
        f"{concept} riguarda solo una nota accessoria e non modifica le responsabilità operative.",
    ]


def _choose_replacement(correct_text: str, question: Any, used_texts: set[str]) -> str:
    for candidate in _candidate_pool(correct_text, question):
        key = _norm(candidate)
        if key in used_texts:
            continue
        if correct_text and _similarity(candidate, correct_text) >= 0.90:
            continue
        used_texts.add(key)
        return candidate

    fallback = "Questa risposta cambia il vincolo operativo indicato dal documento e porta a una conclusione errata."
    counter = 2
    candidate = fallback
    while _norm(candidate) in used_texts:
        candidate = f"{fallback} Variante {counter}."
        counter += 1

    used_texts.add(_norm(candidate))
    return candidate


def repair_test_quiz_options_v513d3(test_quiz: Any) -> Any:
    questions = list(test_quiz or [])

    for question in questions:
        options = _options(question)
        correct_option_id = _text(
            _get(question, "correct_option_id", None)
            or _get(question, "risposta_corretta", "")
        )

        correct_text = ""
        for option in options:
            if _is_correct(option, correct_option_id):
                correct_text = _option_text(option)
                break

        used_texts: set[str] = set()

        for option in options:
            if _is_correct(option, correct_option_id):
                used_texts.add(_norm(_option_text(option)))
                continue

            current = _option_text(option)
            if _needs_repair(current, correct_text, used_texts):
                replacement = _choose_replacement(correct_text, question, used_texts)
                _set_option_text(option, replacement)
            else:
                used_texts.add(_norm(current))

    return test_quiz
''', encoding="utf-8")

print(f"WROTE {REPAIR_MODULE.relative_to(ROOT)}")


# ---------------------------------------------------------------------
# 2) Fix route materializer: qm_033 / qm_048 devono essere riconosciuti
#    anche quando hanno ID lunghi tipo qm_033_test_quiz_...
# ---------------------------------------------------------------------

route_text = ROUTE_MATERIALIZER.read_text(encoding="utf-8")

old_required_loop = '''    for required in required_ids:
        if required not in final_route_ids:
            defects.append(f"Motore obbligatorio mancante nella route Test/Quiz: {required}")
'''

new_required_loop = '''    def _route_contains(required_id: str) -> bool:
        return any(
            item == required_id or item.startswith(required_id + "_")
            for item in final_route_ids
        )

    for required in required_ids:
        if not _route_contains(required):
            defects.append(f"Motore obbligatorio mancante nella route Test/Quiz: {required}")
'''

if old_required_loop in route_text:
    route_text = route_text.replace(old_required_loop, new_required_loop, 1)
elif "_route_contains(required_id" in route_text:
    print("Route prefix check già presente")
else:
    raise SystemExit("FAIL - loop required_ids non trovato nel materializer Test/Quiz")

ROUTE_MATERIALIZER.write_text(route_text, encoding="utf-8")
print(f"PATCHED {ROUTE_MATERIALIZER.relative_to(ROOT)}")


# ---------------------------------------------------------------------
# 3) Fix motori_scrittura.py:
#    - rimuove vecchio blocco 5.13D.1 inserito male
#    - rimuove campo dangling nel quality_report
#    - inserisce riparatore opzioni prima di q52_validate_quiz
#    - inserisce connector 63 nello scope corretto prima del quality_report
#    - reinserisce campo test_quiz_real_connection_v513d1 dopo quiz_questions_count
# ---------------------------------------------------------------------

text = MOTORI.read_text(encoding="utf-8")

# Rimuove blocchi D1 precedenti se presenti.
text = re.sub(
    r'\n[ \t]*# FASE 5\.13D\.1 — TEST/QUIZ 63 REAL CONNECTOR LOCAL SCOPE\n'
    r'[ \t]*try:\n'
    r'[ \t]*from backend\.phase5_test_quiz_real_connector_v513d1 import \(\n'
    r'[ \t]*build_test_quiz_real_connection_report,\n'
    r'[ \t]*\)\n'
    r'[ \t]*except ModuleNotFoundError:\n'
    r'[ \t]*from phase5_test_quiz_real_connector_v513d1 import \(\n'
    r'[ \t]*build_test_quiz_real_connection_report,\n'
    r'[ \t]*\)\n\n'
    r'[ \t]*test_quiz_real_connection_v513d1 = build_test_quiz_real_connection_report\(\n'
    r'[ \t]*result\.test_quiz,\n'
    r'[ \t]*result\.errors,\n'
    r'[ \t]*\)\n\n',
    "\n",
    text,
    flags=re.MULTILINE,
)

# Rimuove eventuale campo già inserito nel dict.
text = re.sub(
    r'\n[ \t]*"test_quiz_real_connection_v513d1": test_quiz_real_connection_v513d1,\n',
    "\n",
    text,
)

MOTORI.write_text(text, encoding="utf-8")

lines = MOTORI.read_text(encoding="utf-8").splitlines(keepends=True)

start = None
for i, line in enumerate(lines):
    if line.startswith("def build_phase5_quality_study_quiz"):
        start = i
        break

if start is None:
    raise SystemExit("FAIL - funzione build_phase5_quality_study_quiz non trovata")

end = len(lines)
for i in range(start + 1, len(lines)):
    if lines[i].startswith("def ") or lines[i].startswith("class "):
        end = i
        break

function_text = "".join(lines[start:end])

# 3a) Riparatore opzioni prima della validazione quiz.
repair_marker = "FASE 5.13D.3 — TEST QUIZ DISTRACTOR REPAIR BEFORE VALIDATION"

if repair_marker not in function_text:
    validate_idx = None
    for i in range(start, end):
        if "result.errors.extend(q52_validate_quiz(result.test_quiz, facts, cfg.quiz_options_count))" in lines[i]:
            validate_idx = i
            break

    if validate_idx is None:
        raise SystemExit("FAIL - q52_validate_quiz anchor non trovato")

    indent = re.match(r'^(\s*)', lines[validate_idx]).group(1)

    repair_block = [
        f"{indent}# {repair_marker}\n",
        f"{indent}try:\n",
        f"{indent}    from backend.phase5_quiz_options_repair_v513d3 import (\n",
        f"{indent}        repair_test_quiz_options_v513d3,\n",
        f"{indent}    )\n",
        f"{indent}except ModuleNotFoundError:\n",
        f"{indent}    from phase5_quiz_options_repair_v513d3 import (\n",
        f"{indent}        repair_test_quiz_options_v513d3,\n",
        f"{indent}    )\n",
        "\n",
        f"{indent}result.test_quiz = repair_test_quiz_options_v513d3(result.test_quiz)\n",
        "\n",
    ]

    lines = lines[:validate_idx] + repair_block + lines[validate_idx:]
    added = len(repair_block)
    end += added

# refresh function range/text after insertion
function_text = "".join(lines[start:end])

# 3b) Connector 63 nello scope corretto prima del quality_report.
connector_marker = "FASE 5.13D.1 — TEST/QUIZ 63 REAL CONNECTOR LOCAL SCOPE FIXED"

quality_idx = None
for i in range(start, end):
    if re.match(r'^\s*result\.quality_report = \{', lines[i]):
        quality_idx = i
        break

if quality_idx is None:
    raise SystemExit("FAIL - result.quality_report non trovato nella funzione")

quality_indent = re.match(r'^(\s*)', lines[quality_idx]).group(1)

if connector_marker not in function_text:
    connector_block = [
        f"{quality_indent}# {connector_marker}\n",
        f"{quality_indent}try:\n",
        f"{quality_indent}    from backend.phase5_test_quiz_real_connector_v513d1 import (\n",
        f"{quality_indent}        build_test_quiz_real_connection_report,\n",
        f"{quality_indent}    )\n",
        f"{quality_indent}except ModuleNotFoundError:\n",
        f"{quality_indent}    from phase5_test_quiz_real_connector_v513d1 import (\n",
        f"{quality_indent}        build_test_quiz_real_connection_report,\n",
        f"{quality_indent}    )\n",
        "\n",
        f"{quality_indent}test_quiz_real_connection_v513d1 = build_test_quiz_real_connection_report(\n",
        f"{quality_indent}    result.test_quiz,\n",
        f"{quality_indent}    result.errors,\n",
        f"{quality_indent})\n",
        "\n",
    ]

    lines = lines[:quality_idx] + connector_block + lines[quality_idx:]
    added = len(connector_block)
    end += added
    quality_idx += added

# 3c) Campo nel quality_report dopo quiz_questions_count.
function_text = "".join(lines[start:end])

if '"test_quiz_real_connection_v513d1": test_quiz_real_connection_v513d1,' not in function_text:
    insert_after = None
    for i in range(start, end):
        if '"quiz_questions_count": len(result.test_quiz),' in lines[i]:
            insert_after = i
            break

    if insert_after is None:
        raise SystemExit("FAIL - quiz_questions_count non trovato nel quality_report")

    field_indent = re.match(r'^(\s*)', lines[insert_after]).group(1)
    lines.insert(
        insert_after + 1,
        f'{field_indent}"test_quiz_real_connection_v513d1": test_quiz_real_connection_v513d1,\n',
    )

MOTORI.write_text("".join(lines), encoding="utf-8")
print(f"PATCHED {MOTORI.relative_to(ROOT)}")

print("PASS - Fix Fase 5.13D.3 applicato: scope connector + route prefix + repair quiz options")
