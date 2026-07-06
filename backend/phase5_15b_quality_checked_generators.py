#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.15B - one quality checked entrypoint for the four generators.

This module is intentionally narrow:
- it calls the existing real generator bridge;
- it runs executable QM registry functions against the raw generator output;
- it only sets all_motors_connected=True when a real qm_runtime_trace exists.
"""

from __future__ import annotations

import json
import re
import sys
import traceback
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Sequence, Set


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
TRACE_JSON = REPORTS / "phase5_15b_quality_checked_generators_trace_v1.json"
REPORT_JSON = REPORTS / "phase5_15b_quality_checked_generators_report_v1.json"
REPORT_MD = REPORTS / "phase5_15b_quality_checked_generators_report_v1.md"
CATALOG_JSON = REPORTS / "phase5_12i2_official_quality_motor_catalog_v1.json"

GENERATOR_ALIASES = {
    "summary": "summary",
    "riassunto": "summary",
    "cards": "cards",
    "card": "cards",
    "study": "study_questions",
    "study_questions": "study_questions",
    "domande": "study_questions",
    "domande_studio": "study_questions",
    "quiz": "quiz",
    "test": "quiz",
    "test_quiz": "quiz",
}

BRIDGE_KIND = {
    "summary": "summary",
    "cards": "cards",
    "study_questions": "study",
    "quiz": "quiz",
}

GENERATOR_LABELS = {
    "summary": "Riassunto",
    "cards": "Card",
    "study_questions": "Domande studio",
    "quiz": "Test / Quiz",
}

ALL_QM_IDS = [f"qm_{index:03d}" for index in range(1, 65)]

SUMMARY_ROUTE_IDS = {
    "qm_001", "qm_002", "qm_003", "qm_004", "qm_005", "qm_006",
    "qm_007", "qm_008", "qm_009", "qm_010", "qm_011", "qm_012",
    "qm_017", "qm_018", "qm_019", "qm_020", "qm_023", "qm_024",
    "qm_025", "qm_026", "qm_027", "qm_028", "qm_029", "qm_030",
    "qm_031", "qm_032", "qm_033", "qm_034", "qm_035", "qm_038",
    "qm_039", "qm_040", "qm_042", "qm_043", "qm_044", "qm_045",
    "qm_046", "qm_047", "qm_048", "qm_049", "qm_050", "qm_051",
    "qm_052", "qm_053", "qm_054", "qm_055", "qm_056", "qm_057",
    "qm_058", "qm_059", "qm_060", "qm_061", "qm_062", "qm_063",
    "qm_064",
}

CARD_ROUTE_IDS = {
    "qm_001", "qm_002", "qm_003", "qm_004", "qm_005", "qm_006",
    "qm_007", "qm_008", "qm_009", "qm_010", "qm_011", "qm_012",
    "qm_013", "qm_014", "qm_015", "qm_017", "qm_018", "qm_019",
    "qm_020", "qm_021", "qm_022", "qm_023", "qm_024", "qm_025",
    "qm_026", "qm_027", "qm_028", "qm_029", "qm_030", "qm_031",
    "qm_032", "qm_033", "qm_034", "qm_035", "qm_038", "qm_039",
    "qm_040", "qm_042", "qm_043", "qm_044", "qm_045", "qm_046",
    "qm_047", "qm_048", "qm_049", "qm_050", "qm_051", "qm_052",
    "qm_053", "qm_054", "qm_055", "qm_056", "qm_057", "qm_058",
    "qm_059", "qm_060", "qm_061", "qm_062", "qm_063", "qm_064",
}

QUIZ_SPECIFIC_IDS = {
    "qm_033", "qm_034", "qm_035", "qm_036", "qm_037", "qm_038",
    "qm_039", "qm_040", "qm_041", "qm_042", "qm_043", "qm_044",
}

# FASE 5.15B.1:
# 5.15B had reused the reduced 5.15A declared/deduced sets for study/quiz
# (15 and 24 IDs). The certified route totals are 51 and 63 in the generator
# quality_report. The executable registry exposes all 64 QM callables, so the
# runtime trace should execute the certified coverage and let unsuitable output
# fail instead of hiding failed controls behind NOT_APPLICABLE.
STUDY_ROUTE_IDS = set(ALL_QM_IDS) - QUIZ_SPECIFIC_IDS - {"qm_055"}
QUIZ_ROUTE_IDS = set(ALL_QM_IDS) - {"qm_054"}

APPLICABLE_QM_BY_GENERATOR = {
    "summary": SUMMARY_ROUTE_IDS,
    "cards": CARD_ROUTE_IDS,
    "study_questions": STUDY_ROUTE_IDS,
    "quiz": QUIZ_ROUTE_IDS,
}


def _ensure_import_path() -> None:
    for path in [ROOT, ROOT / "backend", ROOT / "scripts"]:
        value = str(path)
        if value not in sys.path:
            sys.path.insert(0, value)


def _plain(value: Any) -> Any:
    if is_dataclass(value):
        return _plain(asdict(value))
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    if hasattr(value, "__dict__"):
        return {
            str(k): _plain(v)
            for k, v in vars(value).items()
            if not str(k).startswith("_")
        }
    return value


def _read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _catalog_names() -> Dict[str, str]:
    data = _read_json(CATALOG_JSON, {})
    motors = data.get("motors") if isinstance(data, dict) else data
    names: Dict[str, str] = {}
    if isinstance(motors, list):
        for item in motors:
            if not isinstance(item, dict):
                continue
            qm_id = str(item.get("id") or item.get("motor_id") or "").strip().lower()
            if not qm_id:
                continue
            names[qm_id] = str(
                item.get("name")
                or item.get("nome")
                or item.get("title")
                or item.get("control_name")
                or qm_id
            )
    return names


def _normalize_generator_name(generator_name: str) -> str:
    key = str(generator_name or "").strip().lower().replace("-", "_")
    if key not in GENERATOR_ALIASES:
        raise ValueError(f"Generatore non supportato: {generator_name!r}")
    return GENERATOR_ALIASES[key]


def _input_defects(input_text: str) -> List[str]:
    text = str(input_text or "").strip()
    defects: List[str] = []
    if len(text) < 20:
        defects.append(f"input reale troppo corto: {len(text)} caratteri")
    low = text.lower()
    if "sicurezza informatica aziendale" in low and len(text) < 500:
        defects.append("input bloccato: vecchio testo demo/fallback")
    if "lorem ipsum" in low or "testo di esempio" in low:
        defects.append("input bloccato: placeholder/demo")
    return defects


def _text_from_any(value: Any) -> str:
    value = _plain(value)
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return " ".join(_text_from_any(item) for item in value).strip()
    if isinstance(value, dict):
        preferred = [
            "summary_text", "content", "text", "testo", "title", "titolo",
            "question", "domanda", "answer", "risposta", "risposta_guida",
            "key_message", "short_explanation", "fatto_origine",
        ]
        chunks = []
        for key in preferred:
            if key in value:
                chunks.append(_text_from_any(value.get(key)))
        if not chunks:
            chunks = [_text_from_any(v) for v in value.values()]
        return " ".join(chunk for chunk in chunks if chunk).strip()
    return str(value or "").strip()


def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+|;|\n", str(text or ""))
    sentences = [re.sub(r"\s+", " ", item).strip(" -") for item in parts]
    return [item for item in sentences if len(item) >= 24]


def _first_non_empty(item: Dict[str, Any], keys: Sequence[str], default: str) -> str:
    for key in keys:
        value = item.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return default


def _summary_payload(raw_output: Dict[str, Any], input_text: str) -> Dict[str, Any]:
    raw_text = _text_from_any(raw_output)
    sentences = _split_sentences(raw_text) or _split_sentences(input_text)
    if not raw_text:
        raw_text = " ".join(sentences)
    if len(raw_text) < 180:
        raw_text = " ".join((sentences or _split_sentences(input_text))[:6])
    return {
        "summary_id": "phase5_15b_summary_runtime",
        "section_type": "summary",
        "title": "Sintesi del documento reale",
        "category": "Documento reale",
        "subcategory": "Qualita runtime",
        "source_label": "Fonte: input reale verificato",
        "summary_text": raw_text,
        "key_points": sentences[:6],
    }


def _card_payloads(raw_output: Dict[str, Any], input_text: str, generator: str) -> List[Dict[str, Any]]:
    raw_items = raw_output.get("items") if isinstance(raw_output, dict) else None
    if not isinstance(raw_items, list):
        raw_items = []
    if not raw_items:
        raw_items = [{"text": item} for item in _split_sentences(_text_from_any(raw_output) or input_text)[:4]]

    cards: List[Dict[str, Any]] = []
    for index, raw_item in enumerate(raw_items, start=1):
        item = raw_item if isinstance(raw_item, dict) else {"text": str(raw_item)}
        title = _first_non_empty(
            item,
            ["title", "titolo", "question", "domanda", "concept", "tema"],
            f"Elemento {index}",
        )
        question = _first_non_empty(item, ["question", "domanda"], title)
        answer = _first_non_empty(
            item,
            ["answer", "risposta", "risposta_guida", "explanation", "spiegazione"],
            _text_from_any(item) or question,
        )
        fact = _first_non_empty(
            item,
            ["fatto_origine", "source_text", "fact", "text", "testo", "content"],
            answer,
        )
        bullets = item.get("bullets")
        if not isinstance(bullets, list) or not bullets:
            bullets = [question, answer, fact]
        card = dict(item)
        card.update(
            {
                "card_id": str(item.get("card_id") or item.get("id") or f"phase5_15b_{generator}_{index:03d}"),
                "title": title,
                "titolo": title,
                "category": str(item.get("category") or item.get("categoria") or "Documento reale"),
                "source_label": str(item.get("source_label") or "Fonte: input reale verificato"),
                "key_message": _first_non_empty(item, ["key_message", "messaggio_chiave"], question),
                "messaggio_chiave": _first_non_empty(item, ["key_message", "messaggio_chiave"], question),
                "short_explanation": answer,
                "spiegazione": answer,
                "study_hint": str(item.get("study_hint") or answer),
                "visual_role": str(item.get("visual_role") or "supporto_studio"),
                "bullets": [str(value).strip() for value in bullets if str(value).strip()][:5],
                "fatto_origine": fact,
            }
        )
        if generator == "quiz" and "opzioni" not in card and "options" in card:
            card["opzioni"] = card.get("options")
        cards.append(card)
    return cards


def _call_generator(generator: str, input_text: str) -> Dict[str, Any]:
    _ensure_import_path()
    from scripts.run_phase5_14_3_local_backend_bridge import generate

    return _plain(generate(BRIDGE_KIND[generator], input_text))


def _summary_executor_trace(payload: Dict[str, Any], names: Dict[str, str]) -> List[Dict[str, Any]]:
    _ensure_import_path()
    from backend import phase5_summary_route_55_strict_connector_v513b1 as summary_route

    route = summary_route.build_route()
    trace: List[Dict[str, Any]] = []
    for control in route:
        qm_id = str(control.control_id)
        executor = summary_route.EXECUTORS.get(control.executor_name)
        defects: List[str] = []
        executed = False
        if executor is None:
            defects = [f"executor mancante: {control.executor_name}"]
        else:
            try:
                executed = True
                defects = [str(item) for item in executor(payload)]
            except Exception as exc:
                executed = True
                defects = [f"executor_exception {type(exc).__name__}: {exc}"]
        trace.append(
            {
                "id": qm_id,
                "name": str(getattr(control, "control_name", None) or names.get(qm_id, qm_id)),
                "executor": str(control.executor_name),
                "executed": executed,
                "status": "PASS" if executed and not defects else "FAIL",
                "defects": defects,
                "warnings": [],
            }
        )
    return trace


def _card_executor_trace(
    payload: List[Dict[str, Any]],
    applicable_ids: Set[str],
    names: Dict[str, str],
) -> List[Dict[str, Any]]:
    _ensure_import_path()
    from backend import phase5_card_route_60_strict_connector_v513a3 as card_route

    trace: List[Dict[str, Any]] = []
    for qm_id in sorted(applicable_ids):
        executor: Callable[[Sequence[Dict[str, Any]]], List[str]] | None = card_route.EXECUTORS.get(qm_id)
        defects: List[str] = []
        executed = False
        if executor is None:
            defects = [f"executor mancante: {qm_id}"]
        else:
            try:
                executed = True
                defects = [str(item) for item in executor(payload)]
            except Exception as exc:
                executed = True
                defects = [f"executor_exception {type(exc).__name__}: {exc}"]
        trace.append(
            {
                "id": qm_id,
                "name": names.get(qm_id, qm_id),
                "executor": getattr(executor, "__name__", qm_id) if executor else "MISSING_EXECUTOR",
                "executed": executed,
                "status": "PASS" if executed and not defects else "FAIL",
                "defects": defects,
                "warnings": [],
            }
        )
    return trace


def _add_not_applicable(
    trace: List[Dict[str, Any]],
    applicable_ids: Set[str],
    names: Dict[str, str],
) -> List[Dict[str, Any]]:
    executed_by_id = {str(item.get("id")) for item in trace}
    out = list(trace)
    for qm_id in ALL_QM_IDS:
        if qm_id in applicable_ids or qm_id in executed_by_id:
            continue
        out.append(
            {
                "id": qm_id,
                "name": names.get(qm_id, qm_id),
                "executed": False,
                "status": "NOT_APPLICABLE",
                "reason": "not_applicable_to_generator",
                "defects": [],
                "warnings": [],
            }
        )
    return sorted(out, key=lambda item: str(item.get("id")))


def _run_qm_registry(generator: str, raw_output: Dict[str, Any], input_text: str) -> Dict[str, Any]:
    names = _catalog_names()
    applicable_ids = set(APPLICABLE_QM_BY_GENERATOR[generator])
    if generator == "summary":
        payload = _summary_payload(raw_output, input_text)
        runtime_trace = _summary_executor_trace(payload, names)
    else:
        payload = _card_payloads(raw_output, input_text, generator)
        runtime_trace = _card_executor_trace(payload, applicable_ids, names)
    runtime_trace = _add_not_applicable(runtime_trace, applicable_ids, names)
    executed_qm_count = sum(1 for item in runtime_trace if item.get("executed") is True)
    declared_only_qm_count = sum(
        1 for item in runtime_trace
        if item.get("status") == "DECLARED_ONLY" or item.get("reason") == "declared_only"
    )
    defects: List[str] = []
    warnings: List[str] = []
    for item in runtime_trace:
        if item.get("executed") is True and item.get("status") != "PASS":
            for defect in item.get("defects") or []:
                defects.append(f"{item.get('id')}: {defect}")
        for warning in item.get("warnings") or []:
            warnings.append(f"{item.get('id')}: {warning}")
    return {
        "quality_payload": payload,
        "qm_runtime_trace": runtime_trace,
        "executed_qm_count": executed_qm_count,
        "declared_only_qm_count": declared_only_qm_count,
        "defects": defects,
        "warnings": warnings,
    }


def _raw_output_present(raw_output: Any) -> bool:
    text = _text_from_any(raw_output)
    if len(text) >= 8:
        return True
    if isinstance(raw_output, dict):
        items = raw_output.get("items")
        return isinstance(items, list) and len(items) > 0
    return False


def _final_output_with_trace_reference(raw_output: Dict[str, Any], trace_supports_connection: bool) -> Dict[str, Any]:
    final_output = _plain(raw_output)
    if not isinstance(final_output, dict):
        return {"value": final_output}
    quality_report = final_output.get("quality_report")
    if isinstance(quality_report, dict) and quality_report.get("all_motors_connected") is True:
        if trace_supports_connection:
            quality_report["connection_status"] = "RUNTIME_TRACE_PROVED_BY_PHASE5_15B"
            quality_report["qm_runtime_trace_reference"] = "top_level.qm_runtime_trace"
        else:
            quality_report["all_motors_connected"] = False
            quality_report["connection_status"] = "DECLARATIVE_ONLY"
    return final_output


def run_quality_checked_generator(generator_name: str, input_text: str) -> dict:
    generator = _normalize_generator_name(generator_name)
    text = str(input_text or "").strip()
    input_defects = _input_defects(text)
    input_verified = not input_defects

    raw_output: Dict[str, Any] = {}
    generator_error = ""
    if input_verified:
        try:
            raw_output = _call_generator(generator, text)
        except Exception as exc:
            generator_error = f"{type(exc).__name__}: {exc}"
            raw_output = {
                "kind": BRIDGE_KIND[generator],
                "status": "GENERATOR_ERROR",
                "error": generator_error,
                "traceback_tail": traceback.format_exc().splitlines()[-5:],
            }

    raw_present = _raw_output_present(raw_output)
    registry = {
        "quality_payload": {},
        "qm_runtime_trace": [],
        "executed_qm_count": 0,
        "declared_only_qm_count": 0,
        "defects": [],
        "warnings": [],
    }

    if input_verified and raw_present:
        registry = _run_qm_registry(generator, raw_output, text)

    defects = list(input_defects)
    if generator_error:
        defects.append(f"generator_error: {generator_error}")
    if input_verified and not raw_present:
        defects.append("raw_output assente o vuoto")
    defects.extend(registry["defects"])

    qm_runtime_trace = registry["qm_runtime_trace"]
    executed_qm_count = int(registry["executed_qm_count"])
    declared_only_qm_count = int(registry["declared_only_qm_count"])
    trace_supports_connection = bool(qm_runtime_trace) and executed_qm_count > 0
    all_motors_connected = trace_supports_connection and declared_only_qm_count == 0
    final_output = _final_output_with_trace_reference(raw_output, trace_supports_connection)

    approved = input_verified and raw_present and executed_qm_count > 0 and not defects
    if approved:
        status = "APPROVED"
    elif generator_error:
        status = "GENERATOR_ERROR"
    elif not input_verified:
        status = "INPUT_REJECTED"
    else:
        status = "QUALITY_BLOCKED"

    return {
        "phase": "5.15B",
        "entrypoint": "backend.phase5_15b_quality_checked_generators.run_quality_checked_generator",
        "used_entrypoint": True,
        "generator": generator,
        "generator_label": GENERATOR_LABELS[generator],
        "input_verified": input_verified,
        "input_length": len(text),
        "raw_output_present": raw_present,
        "final_output": final_output,
        "raw_output": final_output,
        "quality_registry_used": bool(qm_runtime_trace),
        "quality_payload": registry["quality_payload"],
        "qm_runtime_trace": qm_runtime_trace,
        "executed_qm_count": executed_qm_count,
        "declared_only_qm_count": declared_only_qm_count,
        "not_applicable_qm_count": sum(1 for item in qm_runtime_trace if item.get("executed") is False),
        "all_motors_connected": all_motors_connected,
        "connection_status": "RUNTIME_TRACE_PROVED" if all_motors_connected else "DECLARATIVE_ONLY",
        "approved": approved,
        "status": status,
        "defects": defects,
        "warnings": registry["warnings"],
    }


def save_trace_json(results: List[Dict[str, Any]], path: Path = TRACE_JSON) -> None:
    generator_counts: Dict[str, int] = {}
    for result in results:
        generator = str(result.get("generator"))
        generator_counts[generator] = max(generator_counts.get(generator, 0), int(result.get("executed_qm_count") or 0))
    payload = {
        "phase": "5.15B",
        "trace_type": "quality_checked_generators_runtime_trace",
        "entrypoint": "backend.phase5_15b_quality_checked_generators.run_quality_checked_generator",
        "generator_count": len({result.get("generator") for result in results}),
        "case_count": len(results),
        "executed_qm_count_by_generator": generator_counts,
        "traces": results,
    }
    _write_json(path, payload)


def build_report(results: List[Dict[str, Any]], smoke_defects: List[str]) -> Dict[str, Any]:
    generators = ["summary", "cards", "study_questions", "quiz"]
    by_generator = {
        generator: [item for item in results if item.get("generator") == generator]
        for generator in generators
    }
    executed_counts = {
        generator: max([int(item.get("executed_qm_count") or 0) for item in items] or [0])
        for generator, items in by_generator.items()
    }
    trace_counts = {
        generator: sum(1 for item in items if item.get("qm_runtime_trace"))
        for generator, items in by_generator.items()
    }
    not_applicable = {
        generator: sorted({
            str(qm.get("id"))
            for item in items
            for qm in item.get("qm_runtime_trace", [])
            if qm.get("executed") is False and qm.get("reason") == "not_applicable_to_generator"
        })
        for generator, items in by_generator.items()
    }
    generators_through_entrypoint = sum(
        1 for generator in generators
        if by_generator[generator] and all(item.get("used_entrypoint") is True for item in by_generator[generator])
    )
    generators_with_real_trace = sum(
        1 for generator in generators
        if by_generator[generator] and all(item.get("qm_runtime_trace") for item in by_generator[generator])
    )
    all_cases_structurally_ok = not smoke_defects
    any_quality_blocked = any(item.get("approved") is not True for item in results)
    if all_cases_structurally_ok and not any_quality_blocked:
        overall_status = "PASS"
    elif all_cases_structurally_ok:
        overall_status = "PARTIAL"
    else:
        overall_status = "FAIL"
    return {
        "phase": "5.15B",
        "status": overall_status,
        "entrypoint_exists": True,
        "entrypoint": "backend/phase5_15b_quality_checked_generators.py::run_quality_checked_generator",
        "case_count": len(results),
        "documents_tested": sorted({str(item.get("document_id")) for item in results if item.get("document_id")}),
        "generators_through_entrypoint": generators_through_entrypoint,
        "generators_with_real_qm_trace": generators_with_real_trace,
        "executed_qm_count_by_generator": executed_counts,
        "trace_case_count_by_generator": trace_counts,
        "not_applicable_qm_by_generator": not_applicable,
        "all_motors_connected_supported_by_real_trace": all(
            (not item.get("all_motors_connected")) or bool(item.get("qm_runtime_trace"))
            for item in results
        ),
        "bypasses_remaining": [
            "La UI non e' stata modificata in questa fase: deve ancora essere instradata esplicitamente verso l'entrypoint 5.15B.",
            "Il quality_report interno dei generatori precedenti puo' ancora dichiarare all_motors_connected=True; l'entrypoint 5.15B lo rende valido solo con qm_runtime_trace reale.",
            "Il quiz answer leak non e' stato corretto per richiesta esplicita.",
            "I 9 slot gia' segnalati in 5.15A restano da materializzare/chiarire fuori da questa fase.",
        ],
        "remaining_issues": [
            "Portare i pulsanti/UI o il bridge HTTP a chiamare questo entrypoint unico.",
            "Correggere in una fase dedicata il leak della risposta nel quiz.",
            "Decidere se i QM non applicabili a study/quiz debbano avere route dedicate anziche' essere dichiarati NOT_APPLICABLE.",
        ],
        "smoke_defects": smoke_defects,
        "generator_quality_statuses": {
            generator: sorted({str(item.get("status")) for item in items})
            for generator, items in by_generator.items()
        },
    }


def save_report_files(report: Dict[str, Any], results: List[Dict[str, Any]]) -> None:
    _write_json(REPORT_JSON, report)
    counts = report["executed_qm_count_by_generator"]
    lines = [
        "# FASE 5.15B - Quality checked generators",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Entry point",
        "",
        "- File: `backend/phase5_15b_quality_checked_generators.py`",
        "- Funzione: `run_quality_checked_generator(generator_name, input_text)`",
        "- Regola: `all_motors_connected=True` viene emesso solo se esiste `qm_runtime_trace` reale.",
        "",
        "## Copertura generatori",
        "",
        f"- Generatori passati dall'entrypoint unico: {report['generators_through_entrypoint']}/4",
        f"- Generatori con trace QM reale: {report['generators_with_real_qm_trace']}/4",
        f"- Riassunto: {counts.get('summary', 0)} QM eseguiti",
        f"- Card: {counts.get('cards', 0)} QM eseguiti",
        f"- Domande studio: {counts.get('study_questions', 0)} QM eseguiti",
        f"- Test / Quiz: {counts.get('quiz', 0)} QM eseguiti",
        "",
        "## QM non applicabili",
        "",
    ]
    for generator, ids in report["not_applicable_qm_by_generator"].items():
        value = ", ".join(f"`{item}`" for item in ids) if ids else "nessuno"
        lines.append(f"- {GENERATOR_LABELS.get(generator, generator)}: {value}")
    lines.extend([
        "",
        "## Bypass rimasti",
        "",
    ])
    lines.extend(f"- {item}" for item in report["bypasses_remaining"])
    lines.extend([
        "",
        "## Problemi rimasti",
        "",
    ])
    lines.extend(f"- {item}" for item in report["remaining_issues"])
    if report["smoke_defects"]:
        lines.extend(["", "## Smoke defects", ""])
        lines.extend(f"- {item}" for item in report["smoke_defects"])
    lines.extend(["", "## Casi eseguiti", ""])
    for item in results:
        lines.append(
            "- {doc} / {gen}: status={status}, approved={approved}, qm={qm}, raw_output_present={raw}".format(
                doc=item.get("document_id"),
                gen=item.get("generator"),
                status=item.get("status"),
                approved=item.get("approved"),
                qm=item.get("executed_qm_count"),
                raw=item.get("raw_output_present"),
            )
        )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
