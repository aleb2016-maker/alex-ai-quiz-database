from __future__ import annotations

import copy
import importlib
import inspect
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


REPORT_JSON = ROOT / "reports" / "compatibilita_batch_motori_legacy_v1.json"
REPORT_MD = ROOT / "reports" / "compatibilita_batch_motori_legacy_v1.md"


# FASE 5.5.3 — COMPATIBILITY TEST BATCH MOTORI LEGACY V1
#
# Lista controllata: solo motori/revisori reali candidati.
# Non include validator puri, benchmark, test, scanner o patch.
CANDIDATE_FUNCTIONS = [
    "scripts.rag_motore_didattico_riutilizzabile_v35c.refine_output",
    "scripts.rag_motore_didattico_riutilizzabile_v35c.refine_summary",
    "scripts.rag_motore_didattico_riutilizzabile_v35c.refine_cards",
    "scripts.rag_motore_didattico_riutilizzabile_v35c.refine_study_questions",

    "scripts.rag_revisore_qualita_testuale_v35g.refine_output",
    "scripts.rag_revisore_qualita_testuale_v35g.refine_summary",
    "scripts.rag_revisore_qualita_testuale_v35g.refine_cards",
    "scripts.rag_revisore_qualita_testuale_v35g.refine_study",

    "scripts.rag_revisore_naturalezza_antikeyword_v35i.improve_output",
    "scripts.rag_revisore_naturalezza_antikeyword_v35i.improve_summary",
    "scripts.rag_revisore_naturalezza_antikeyword_v35i.improve_cards",
    "scripts.rag_revisore_naturalezza_antikeyword_v35i.improve_study",

    "scripts.rag_revisore_accordo_pronomi_v35j.improve_output",
    "scripts.rag_revisore_accordo_pronomi_v35j.improve_summary",
    "scripts.rag_revisore_accordo_pronomi_v35j.improve_cards",
    "scripts.rag_revisore_accordo_pronomi_v35j.improve_study",

    "scripts.rag_cleaner_finale_universale_v35k.clean_output",

    "scripts.rag_motore_test_riutilizzabile_v35d.refine_output",
]


def _safe_error(exc: BaseException) -> str:
    return f"{exc.__class__.__name__}: {exc}"


def _safe_json(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    except Exception:
        return repr(value)


def _walk_strings(value: Any) -> list[str]:
    out: list[str] = []

    if isinstance(value, str):
        out.append(value)

    elif isinstance(value, dict):
        for child in value.values():
            out.extend(_walk_strings(child))

    elif isinstance(value, list):
        for child in value:
            out.extend(_walk_strings(child))

    return out


def count_known_text_defects(value: Any) -> int:
    text = "\n".join(_walk_strings(value)).lower()

    patterns = [
        r"\bnon\s+non\b",
        r"\bcos e\b",
        r"\bqual e\b",
        r"\s+([,.!?;:])",
        r"\s{2,}",
        r"\buna\s+una\b",
        r"\bun\s+un\b",
        r"\bil\s+il\b",
        r"\bla\s+la\b",
        r"\bperchè\b",
    ]

    return sum(
        len(re.findall(pattern, text, flags=re.IGNORECASE))
        for pattern in patterns
    )


def _import_function(function_id: str):
    module_name, function_name = function_id.rsplit(".", 1)

    module = importlib.import_module(module_name)
    fn = getattr(module, function_name)

    if not callable(fn):
        raise TypeError(f"{function_id} non è callable")

    return fn


def _can_try_single_arg(fn: Any) -> tuple[bool, str]:
    try:
        sig = inspect.signature(fn)
    except Exception:
        return True, "signature_unavailable_trying_single_arg"

    params = list(sig.parameters.values())

    required = [
        p for p in params
        if p.default is inspect.Parameter.empty
        and p.kind in {
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        }
    ]

    has_varargs = any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in params)

    if len(required) <= 1:
        return True, str(sig)

    if has_varargs:
        return True, str(sig)

    return False, str(sig)


def _base_phase5_output() -> dict[str, Any]:
    return {
        "document_id": "compatibilita_batch_motori_legacy_v1",
        "phase_name": "QUALITY_STUDY_QUIZ",
        "approved": True,
        "status": "APPROVED",
        "riassunto_qualita": {
            "titolo": "Riassunto di qualità",
            "paragrafi": [
                "Il controllo degli accessi limita l'utilizzo dei sistemi interni  .",
                "Le credenziali non non devono essere condivise tra più operatori.",
                "La revisione periodica degli accessi riduce il rischio perchè evita permessi attivi non autorizzati.",
            ],
            "testo_completo": (
                "Il controllo degli accessi limita l'utilizzo dei sistemi interni  . "
                "Le credenziali non non devono essere condivise tra più operatori. "
                "La revisione periodica degli accessi riduce il rischio perchè evita permessi attivi non autorizzati."
            ),
            "fonte_pagine": [1, 2],
        },
        "card_concettuali": [
            {
                "card_id": "phase5_card_001",
                "titolo": "Controllo accessi",
                "contenuto_esplicativo": "Il controllo degli accessi limita l'utilizzo dei sistemi interni  .",
                "micro_concetti": ["controllo accessi", "account utente"],
                "fonte_pagine": [1, 2],
            },
            {
                "card_id": "phase5_card_002",
                "titolo": "Protezione credenziali",
                "contenuto_esplicativo": "Le credenziali non non devono essere condivise tra più operatori.",
                "micro_concetti": ["credenziali", "operatori"],
                "fonte_pagine": [1, 2],
            },
        ],
        "domande_studio": [
            {
                "question_id": "study_question_001",
                "domanda": "Perchè il controllo accessi è importante ?",
                "risposta_guida": "Il controllo degli accessi limita l'utilizzo dei sistemi interni.",
                "fonte_pagine": [1, 2],
            },
            {
                "question_id": "study_question_002",
                "domanda": "Qual e il rischio delle credenziali condivise?",
                "risposta_guida": "Le credenziali non non devono essere condivise tra più operatori.",
                "fonte_pagine": [1, 2],
            },
        ],
        "test_quiz": [
            {
                "question_id": "phase5_quiz_question_001",
                "domanda": "Quale affermazione descrive correttamente la protezione credenziali?",
                "opzioni": [
                    {
                        "option_id": "A",
                        "testo": "Le credenziali possono essere condivise liberamente tra più operatori.",
                        "is_correct": False,
                    },
                    {
                        "option_id": "B",
                        "testo": "Le credenziali non non devono essere condivise tra più operatori.",
                        "is_correct": True,
                    },
                    {
                        "option_id": "C",
                        "testo": "Le credenziali devono essere scritte in chiaro nei documenti condivisi.",
                        "is_correct": False,
                    },
                    {
                        "option_id": "D",
                        "testo": "Gli account anonimi sono sempre preferibili.",
                        "is_correct": False,
                    },
                ],
                "correct_option_id": "B",
                "spiegazione": "La risposta corretta riprende il fatto verificato dal documento.",
            }
        ],
        "warnings": [],
        "errors": [],
    }


def _payloads() -> dict[str, Any]:
    full = _base_phase5_output()

    return {
        "plain_text": (
            "Le credenziali non non devono essere condivise tra più operatori. "
            "Qual e il rischio ?"
        ),
        "summary_dict": copy.deepcopy(full["riassunto_qualita"]),
        "cards_list": copy.deepcopy(full["card_concettuali"]),
        "study_list": copy.deepcopy(full["domande_studio"]),
        "quiz_list": copy.deepcopy(full["test_quiz"]),
        "phase5_full_output": copy.deepcopy(full),
    }


def _result_status(before: Any, after: Any, error: str | None) -> str:
    if error:
        return "exception"

    if after is None:
        return "none_output"

    before_json = _safe_json(before)
    after_json = _safe_json(after)

    defects_before = count_known_text_defects(before)
    defects_after = count_known_text_defects(after)

    if defects_after > defects_before:
        return "worsened"

    if before_json != after_json:
        return "changed_no_worse"

    return "unchanged_no_worse"


def _test_function(function_id: str) -> dict[str, Any]:
    item: dict[str, Any] = {
        "function_id": function_id,
        "status": "pending",
        "signature": None,
        "payload_tests": [],
        "best_status": "none",
        "accepted": False,
    }

    try:
        fn = _import_function(function_id)
    except Exception as exc:
        item["status"] = "import_failed"
        item["error"] = _safe_error(exc)
        return item

    can_try, signature = _can_try_single_arg(fn)
    item["signature"] = signature

    if not can_try:
        item["status"] = "skipped_signature"
        return item

    best_rank = -1

    ranks = {
        "changed_no_worse": 4,
        "unchanged_no_worse": 3,
        "none_output": 1,
        "exception": 0,
        "worsened": -2,
    }

    for payload_name, payload in _payloads().items():
        before = copy.deepcopy(payload)
        error = None
        output = None

        try:
            output = fn(copy.deepcopy(payload))
        except Exception as exc:
            error = _safe_error(exc)

        status = _result_status(before, output, error)

        defects_before = count_known_text_defects(before)
        defects_after = count_known_text_defects(output) if error is None and output is not None else None

        changed = False

        if error is None and output is not None:
            changed = _safe_json(before) != _safe_json(output)

        test_record = {
            "payload": payload_name,
            "status": status,
            "changed": changed,
            "known_text_defects_before": defects_before,
            "known_text_defects_after": defects_after,
            "error": error,
            "output_type": type(output).__name__ if output is not None else None,
        }

        item["payload_tests"].append(test_record)

        rank = ranks.get(status, 0)

        if rank > best_rank:
            best_rank = rank
            item["best_status"] = status
            item["best_payload"] = payload_name

    item["accepted"] = item["best_status"] in {"changed_no_worse", "unchanged_no_worse"}

    if any(test["status"] == "worsened" for test in item["payload_tests"]):
        item["has_worsening_case"] = True
    else:
        item["has_worsening_case"] = False

    if item["accepted"]:
        item["status"] = "accepted_for_adapter_study"
    else:
        item["status"] = "not_accepted"

    return item


def main() -> int:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)

    results = []

    for function_id in CANDIDATE_FUNCTIONS:
        print(f"▶ Testo {function_id}")
        result = _test_function(function_id)
        results.append(result)

        print(
            f"  - status={result.get('status')} | "
            f"best={result.get('best_status')} | "
            f"payload={result.get('best_payload')}"
        )

    accepted = [
        item for item in results
        if item.get("accepted") is True
    ]

    changed_no_worse = [
        item for item in results
        if item.get("best_status") == "changed_no_worse"
    ]

    report = {
        "report_name": "compatibilita_batch_motori_legacy_v1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "total_tested": len(results),
        "accepted_count": len(accepted),
        "changed_no_worse_count": len(changed_no_worse),
        "results": results,
        "notes": [
            "Diagnostico: non collega motori al registry.",
            "accepted_for_adapter_study significa solo che il motore merita studio adapter.",
            "changed_no_worse è il candidato più interessante.",
            "I motori che peggiorano vanno protetti da guardia anti-peggioramento o esclusi.",
        ],
    }

    REPORT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = []
    lines.append("# Compatibilità batch motori legacy V1\n")
    lines.append(f"- Creato: `{report['created_at']}`")
    lines.append(f"- Totale testati: `{report['total_tested']}`")
    lines.append(f"- Accettati per studio adapter: `{report['accepted_count']}`")
    lines.append(f"- Cambiano senza peggiorare: `{report['changed_no_worse_count']}`")
    lines.append("")
    lines.append("| Accettato | Best | Payload | Peggiora in qualche caso | Funzione |")
    lines.append("|---|---|---|---|---|")

    for item in results:
        lines.append(
            f"| {'✅' if item.get('accepted') else ''} "
            f"| `{item.get('best_status')}` "
            f"| `{item.get('best_payload')}` "
            f"| {'⚠️' if item.get('has_worsening_case') else ''} "
            f"| `{item.get('function_id')}` |"
        )

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("\n✅ COMPATIBILITÀ BATCH MOTORI LEGACY V1 COMPLETATA")
    print(f"Testati: {len(results)}")
    print(f"Accettati: {len(accepted)}")
    print(f"Changed no worse: {len(changed_no_worse)}")
    print(f"Report JSON: {REPORT_JSON}")
    print(f"Report MD:   {REPORT_MD}")

    print("\nCANDIDATI MIGLIORI:")
    for item in changed_no_worse:
        print(
            f"- {item.get('function_id')} | "
            f"payload={item.get('best_payload')} | "
            f"best={item.get('best_status')}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
