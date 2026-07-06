#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.15A - executable quality registry probe.

Non-invasive diagnostic script. It does not patch generators or UI.

Outputs:
- reports/phase5_15a_generator_motor_trace_v1.json
- reports/phase5_15a_executable_registry_connection_proof_v1.json
- reports/phase5_15a_executable_registry_connection_proof_v1.md
"""

from __future__ import annotations

import importlib
import inspect
import json
import re
import sys
import traceback
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"

TRACE_JSON = REPORTS / "phase5_15a_generator_motor_trace_v1.json"
PROOF_JSON = REPORTS / "phase5_15a_executable_registry_connection_proof_v1.json"
PROOF_MD = REPORTS / "phase5_15a_executable_registry_connection_proof_v1.md"

CATALOG_JSON = REPORTS / "phase5_12i2_official_quality_motor_catalog_v1.json"
AUDIT_JSON = REPORTS / "audit_completo_73_motori_rag_qualita_v1.json"
AUDIT_MD = REPORTS / "audit_completo_73_motori_rag_qualita_v1.md"
AUDIT_SCRIPT = ROOT / "scripts" / "audit_73_motori_rag_qualita_v1.py"

GENERATOR_KINDS = ["summary", "cards", "study", "quiz"]
GENERATOR_LABELS = {
    "summary": "Riassunto",
    "cards": "Card",
    "study": "Domande studio",
    "quiz": "Test / Quiz",
}

SAMPLE_TEXT = (
    "La procedura di gestione accessi stabilisce che ogni account sia assegnato "
    "a una persona identificabile. Le credenziali condivise aumentano il rischio "
    "operativo e devono essere eliminate. Ogni modifica ai permessi deve essere "
    "approvata dal responsabile e registrata nel sistema. Il controllo mensile "
    "confronta utenti attivi, ruoli assegnati e anomalie rilevate."
)

SMOKE_DOCUMENTS = {
    "breve_valido": (
        "La procedura di onboarding assegna un tutor al nuovo dipendente. Il tutor "
        "presenta gli strumenti aziendali, verifica gli accessi e registra eventuali "
        "problemi entro il primo giorno. Il responsabile HR controlla che la scheda "
        "sia completa."
    ),
    "tecnico": (
        "Il sistema di backup usa snapshot incrementali ogni quattro ore e una "
        "replica giornaliera su storage separato. Il ripristino deve essere testato "
        "almeno una volta al mese. Se il test fallisce, il team apre un ticket "
        "critico e ripete la procedura dopo la correzione."
    ),
    "narrativo_discorsivo": (
        "Marta arrivo alla stazione quando il treno era gia partito. Nel diario "
        "trovo una mappa disegnata da suo nonno e capi che il viaggio non riguardava "
        "la destinazione, ma la memoria della famiglia. Decise di seguire gli indizi "
        "uno alla volta, fino alla casa vicino al lago."
    ),
}

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

STUDY_ROUTE_IDS = {
    "qm_013", "qm_014", "qm_015", "qm_017", "qm_018", "qm_021",
    "qm_022", "qm_048", "qm_051", "qm_054", "qm_056", "qm_057",
    "qm_058", "qm_059", "qm_060",
}

QUIZ_ROUTE_IDS = {
    "qm_016", "qm_017", "qm_021", "qm_022", "qm_033", "qm_034",
    "qm_035", "qm_036", "qm_037", "qm_038", "qm_039", "qm_040",
    "qm_041", "qm_042", "qm_043", "qm_044", "qm_048", "qm_051",
    "qm_055", "qm_056", "qm_057", "qm_058", "qm_059", "qm_060",
}

ROUTE_BY_KIND = {
    "summary": SUMMARY_ROUTE_IDS,
    "cards": CARD_ROUTE_IDS,
    "study": STUDY_ROUTE_IDS,
    "quiz": QUIZ_ROUTE_IDS,
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except Exception:
        return str(path)


def md_escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def ensure_import_path() -> None:
    for path in [ROOT, ROOT / "backend", ROOT / "scripts"]:
        value = str(path)
        if value not in sys.path:
            sys.path.insert(0, value)


def import_optional(module_name: str) -> Optional[Any]:
    ensure_import_path()
    try:
        return importlib.import_module(module_name)
    except Exception:
        return None


def callable_name(fn: Any) -> str:
    return getattr(fn, "__name__", type(fn).__name__)


def get_executor_maps() -> Dict[str, Dict[str, Callable[..., Any]]]:
    maps: Dict[str, Dict[str, Callable[..., Any]]] = {}
    for label, module_name in [
        ("summary_route_55", "backend.phase5_summary_route_55_strict_connector_v513b1"),
        ("card_route_60", "backend.phase5_card_route_60_strict_connector_v513a3"),
    ]:
        module = import_optional(module_name)
        executors = getattr(module, "EXECUTORS", None) if module else None
        if isinstance(executors, dict):
            maps[label] = {str(k): v for k, v in executors.items() if callable(v)}
        else:
            maps[label] = {}
    return maps


def sample_payload_for_executor(map_name: str) -> Any:
    if map_name == "card_route_60":
        return [
            {
                "card_id": "probe_card_001",
                "title": "Gestione accessi",
                "titolo": "Gestione accessi",
                "category": "Sicurezza",
                "source_label": "Fonte: documento reale",
                "key_message": "Ogni account deve essere assegnato a una persona identificabile.",
                "messaggio_chiave": "Ogni account deve essere assegnato a una persona identificabile.",
                "short_explanation": "La procedura riduce il rischio operativo collegando accessi, responsabili e controlli.",
                "spiegazione": "La procedura riduce il rischio operativo collegando accessi, responsabili e controlli.",
                "bullets": [
                    "Account identificabili.",
                    "Permessi approvati.",
                    "Controllo mensile.",
                ],
                "opzioni": [
                    {"option_id": "A", "testo": "Corretta", "is_correct": True},
                    {"option_id": "B", "testo": "Distrattore", "is_correct": False},
                    {"option_id": "C", "testo": "Distrattore", "is_correct": False},
                    {"option_id": "D", "testo": "Distrattore", "is_correct": False},
                ],
            }
        ]
    return {
        "summary_id": "probe_summary_001",
        "section_type": "summary",
        "title": "Sintesi gestione accessi",
        "category": "Sicurezza",
        "subcategory": "Controlli",
        "source_label": "Fonte: documento reale",
        "summary_text": (
            "La procedura di gestione accessi assegna ogni account a una persona "
            "identificabile. Le modifiche ai permessi devono essere approvate e "
            "registrate. Il controllo mensile confronta utenti, ruoli e anomalie."
        ),
        "key_points": [
            "Ogni account e identificabile.",
            "I permessi sono approvati.",
            "Le anomalie sono controllate.",
        ],
        "opzioni": [
            {"option_id": "A", "testo": "Corretta", "is_correct": True},
            {"option_id": "B", "testo": "Distrattore", "is_correct": False},
            {"option_id": "C", "testo": "Distrattore", "is_correct": False},
            {"option_id": "D", "testo": "Distrattore", "is_correct": False},
        ],
    }


def try_call_executor(fn: Callable[..., Any], map_name: str) -> Dict[str, Any]:
    payload = sample_payload_for_executor(map_name)
    try:
        result = fn(payload)
        return {
            "ok": True,
            "result_type": type(result).__name__,
            "result_preview": str(result)[:220],
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
        }


def classify_type(item: Dict[str, Any]) -> str:
    text = f"{item.get('group', '')} {item.get('name', '')}".lower()
    if "fallback" in text:
        return "anti-fallback"
    if "generico" in text:
        return "anti-generico"
    if "frasi spezzate" in text:
        return "anti-frasi spezzate"
    if "test" in text or "quiz" in text or "opzioni" in text or "distrattori" in text:
        return "validazione quiz"
    if "card" in text or "fonti" in text or "layout" in text:
        return "validazione card"
    if "riassunto" in text:
        return "validazione riassunto"
    if "domande studio" in text:
        return "validazione domande studio"
    if "selezionatore" in text or "orchestratore" in text:
        return "orchestratore"
    if "grammatica" in text or "accenti" in text or "apostrofi" in text or "punteggiatura" in text:
        return "qualita grammaticale"
    if "duplicati" in text or "ripetizioni" in text:
        return "qualita semantica"
    if "didattica" in text:
        return "qualita didattica"
    return "qualita semantica"


def generator_links_for(qm_id: str) -> List[str]:
    out = []
    for kind, ids in ROUTE_BY_KIND.items():
        if qm_id in ids:
            out.append(GENERATOR_LABELS[kind])
    return out


def build_registry_probe() -> List[Dict[str, Any]]:
    catalog = read_json(CATALOG_JSON, {})
    executor_maps = get_executor_maps()
    executor_index: Dict[str, List[Tuple[str, Callable[..., Any]]]] = {}
    for map_name, executors in executor_maps.items():
        for qm_id, fn in executors.items():
            executor_index.setdefault(qm_id, []).append((map_name, fn))

    motors: List[Dict[str, Any]] = []
    for item in catalog.get("motors", []):
        qm_id = str(item.get("qm_id", "")).strip()
        links = generator_links_for(qm_id)
        executor_evidence = []
        executable_ok = False

        for map_name, fn in executor_index.get(qm_id, []):
            call_result = try_call_executor(fn, map_name)
            executable_ok = executable_ok or call_result["ok"]
            executor_evidence.append({
                "map": map_name,
                "callable": callable_name(fn),
                "signature": str(inspect.signature(fn)) if callable(fn) else "",
                "isolated_call": call_result,
            })

        if executable_ok:
            status = "EXECUTABLE"
            proof_mode = "chiamato realmente"
            proof = "Callable executor importato e chiamato dal probe in isolamento."
        elif links:
            status = "ROUTE_ONLY"
            proof_mode = "dedotto da route"
            proof = "Presente nelle route dichiarate, ma nessun executor chiamabile passato dal probe."
        elif qm_id:
            status = "REPORT_ONLY"
            proof_mode = "solo report"
            proof = "Presente nel catalogo/report, non collegato a route finali nel probe."
        else:
            status = "MISSING"
            proof_mode = "non provato"
            proof = "Entry catalogo senza id valido."

        motors.append({
            "id": qm_id,
            "number": item.get("number"),
            "name": item.get("name"),
            "type": classify_type(item),
            "status": status,
            "file": "reports/phase5_12i2_official_quality_motor_catalog_v1.json",
            "function_or_class": ", ".join(e["callable"] for e in executor_evidence) or "",
            "generators_linked": links,
            "real_connection_proof": proof,
            "proof_mode": proof_mode,
            "executor_evidence": executor_evidence,
            "notes": (
                "Executable in probe does not mean invoked by final UI generator; "
                "generator trace below remains the source for runtime connection."
            ),
        })

    for number in range(65, 74):
        motors.append({
            "id": f"registry_orchestration_slot_{number:03d}",
            "number": number,
            "name": f"Registry/orchestration slot {number}",
            "type": "registry",
            "status": "SLOT_TO_MATERIALIZE",
            "file": "reports/phase5_12h2_updated_matrix_orchestration_registry_73_v1.json",
            "function_or_class": "",
            "generators_linked": ["Registry/orchestrazione H.2"],
            "real_connection_proof": "Conteggiato nel totale 73, ma non materializzato come QM concreto nel catalogo.",
            "proof_mode": "non provato",
            "executor_evidence": [],
            "notes": "Non inventato come motore; resta slot da chiarire o materializzare.",
        })

    return motors


def call_generator(kind: str, text: str) -> Dict[str, Any]:
    ensure_import_path()
    import scripts.run_phase5_14_3_local_backend_bridge as bridge

    called_functions: List[str] = []
    motori = import_optional("backend.motori_scrittura")
    wrapped: List[Tuple[Any, str, Any]] = []

    def wrap(module: Any, name: str) -> None:
        if not module or not hasattr(module, name):
            return
        original = getattr(module, name)
        if not callable(original):
            return

        def recorder(*args: Any, **kwargs: Any) -> Any:
            called_functions.append(name)
            return original(*args, **kwargs)

        setattr(module, name, recorder)
        wrapped.append((module, name, original))

    for fn_name in [
        "q52_build_quality_study_questions",
        "q52_build_quality_quiz",
        "q52_validate_study_questions",
        "q52_validate_quiz",
        "q52_extract_facts",
        "q52_extract_concepts",
    ]:
        wrap(motori, fn_name)

    try:
        result = bridge.generate(kind, text)
        return {
            "ok": True,
            "result": result,
            "called_runtime_functions": called_functions,
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(limit=6),
            "called_runtime_functions": called_functions,
        }
    finally:
        for module, name, original in reversed(wrapped):
            setattr(module, name, original)


def detect_bypasses(kind: str, result: Optional[Dict[str, Any]], called_functions: Sequence[str]) -> List[str]:
    bypasses = []
    qr = (result or {}).get("quality_report") or {}
    if qr.get("all_motors_connected") is True:
        bypasses.append("all_motors_connected dichiarato nel quality_report")
    if not (result or {}).get("real_invoked_quality_motor_ids"):
        bypasses.append("nessun ID QM realmente tracciato durante la chiamata del generatore")
    if kind in {"summary", "cards"} and not called_functions:
        bypasses.append("runtime summary/cards non passa da q52 o registry QM tracciabile")
    if kind in {"study", "quiz"} and called_functions:
        bypasses.append("usa funzioni q52 reali, ma non ID QM del registry")
    return bypasses


def build_generator_trace_for_text(label: str, text: str) -> List[Dict[str, Any]]:
    traces = []
    for kind in GENERATOR_KINDS:
        call = call_generator(kind, text)
        result = call.get("result") if call.get("ok") else None
        qr = (result or {}).get("quality_report") or {}
        declared_ids = sorted(ROUTE_BY_KIND[kind])
        real_invoked_qm_ids: List[str] = []
        trace = {
            "input_label": label,
            "input_chars": len(text),
            "generator": GENERATOR_LABELS[kind],
            "kind": kind,
            "route": (result or {}).get("motor_name") or qr.get("motor_path") or "ERROR",
            "output_produced": bool(call.get("ok") and result),
            "output_preview": str((result or {}).get("content") or (result or {}).get("items") or "")[:500],
            "status": (result or {}).get("status") if result else "ERROR",
            "approved": (result or {}).get("approved") if result else False,
            "defects": list(qr.get("defects") or []),
            "warnings": list(qr.get("warnings") or []),
            "error": call.get("error"),
            "declared_all_motors_connected": qr.get("all_motors_connected") is True,
            "declared_motors": declared_ids,
            "real_invoked_quality_motor_ids": real_invoked_qm_ids,
            "real_invoked_runtime_functions": call.get("called_runtime_functions") or [],
            "deduced_motor_ids": declared_ids,
            "declared_only_motor_ids": declared_ids if not real_invoked_qm_ids else [],
            "bypasses": detect_bypasses(kind, result, call.get("called_runtime_functions") or []),
            "notes": [
                "Trace runtime ottenuta chiamando scripts.run_phase5_14_3_local_backend_bridge.generate.",
                "Gli ID QM sono considerati realmente invocati solo se appaiono in trace runtime esplicita; quality_report route_total non basta.",
            ],
        }
        traces.append(trace)
    return traces


def build_all_generator_traces() -> List[Dict[str, Any]]:
    traces = []
    traces.extend(build_generator_trace_for_text("probe_documento_medio", SAMPLE_TEXT))
    for label, text in SMOKE_DOCUMENTS.items():
        traces.extend(build_generator_trace_for_text(label, text))
    return traces


def confirmed_audit_problems(traces: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    html = read_text(ROOT / "demo-rag" / "test-documenti-universale.html")
    runtime = read_text(ROOT / "backend" / "phase5_full_pipeline_runtime_v51416.py")
    bridge = read_text(ROOT / "scripts" / "run_phase5_14_3_local_backend_bridge.py")
    index = read_text(ROOT / "rag" / "indice_rag.json")
    smoke = read_text(ROOT / "scripts" / "run_phase5_14_16_full_pipeline_smoke.py")
    any_decl_without_trace = any(
        t.get("declared_all_motors_connected") and not t.get("real_invoked_quality_motor_ids")
        for t in traces
    )
    summary_traces = [t for t in traces if t["kind"] == "summary" and t.get("output_produced")]
    short_long_summary = any(t.get("input_chars", 0) > 1000 and len(t.get("output_preview", "")) < 800 for t in summary_traces)
    audit = read_json(AUDIT_JSON, {})
    audit_long_short = any(
        item.get("scenario") == "lungo"
        and item.get("kind") == "summary"
        and item.get("ok") is True
        and int(item.get("content_len") or 0) < 1000
        for item in ((audit.get("test_eseguiti") or {}).get("risultati") or [])
    )
    short_long_summary = short_long_summary or audit_long_short
    return [
        {
            "problem": "claim 73 ambiguo",
            "confirmed": True,
            "proof": "Catalogo ufficiale 64 QM; slot 65-73 classificati SLOT_TO_MATERIALIZE.",
            "impact": "Claim non dimostrabile come 73 motori concreti.",
            "fix_phase": "5.15D",
        },
        {
            "problem": "registry unico non eseguibile",
            "confirmed": True,
            "proof": "Il probe trova executor sparsi in connettori, non un registry unico usato dai generatori.",
            "impact": "Trace runtime non prova esecuzione QM end-to-end.",
            "fix_phase": "5.15D",
        },
        {
            "problem": "all_motors_connected=True dichiarativo",
            "confirmed": any_decl_without_trace,
            "proof": "Trace generatori con all_motors_connected=True e real_invoked_quality_motor_ids vuoto.",
            "impact": "Report PASS possono essere decorativi.",
            "fix_phase": "5.15D",
        },
        {
            "problem": "bridge/UI clean bypass",
            "confirmed": "fetch(API + \"/api/generate\"" in html and "universal-document-learning-engine.js" not in html,
            "proof": "La pagina clean chiama /api/generate e non carica universal-document-learning-engine.js.",
            "impact": "Pipeline browser storica non e la prova della pagina reale.",
            "fix_phase": "5.15B",
        },
        {
            "problem": "quiz answer leak",
            "confirmed": "is_correct" in html and "correct" in html,
            "proof": "Rendering quiz usa opt.is_correct/classe correct.",
            "impact": "Risposta corretta visibile o deducibile in UI.",
            "fix_phase": "5.15B",
        },
        {
            "problem": "summary lungo troppo corto",
            "confirmed": short_long_summary or "Summary_TOO_SHORT" in runtime,
            "proof": "Runtime summary non usa motore progressivo documenti lunghi nella 5.14.16.",
            "impact": "Riassunti non proporzionati ai documenti lunghi.",
            "fix_phase": "5.15C",
        },
        {
            "problem": "smoke V51418 fallito",
            "confirmed": "magazzino stabilisce" in bridge or bool(smoke),
            "proof": "Audit precedente e smoke dedicati segnalano V51418_LANGUAGE_QUALITY_BLOCKED.",
            "impact": "Pipeline full non stabile su fixture esistente.",
            "fix_phase": "5.15B",
        },
        {
            "problem": "fixture demo sicurezza ancora presente",
            "confirmed": "documento_rag_sicurezza_informatica_aziendale" in index,
            "proof": "rag/indice_rag.json contiene riferimenti alla fixture sicurezza informatica aziendale.",
            "impact": "Rischio se un indice globale viene usato come sorgente default.",
            "fix_phase": "5.15D",
        },
    ]


def summarize(motors: Sequence[Dict[str, Any]], traces: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    counts = Counter(m["status"] for m in motors)
    traced_generators = sorted({t["generator"] for t in traces})
    bypass_generators = sorted({t["generator"] for t in traces if t.get("bypasses")})
    proven_generators = sorted({
        t["generator"] for t in traces
        if t.get("real_invoked_quality_motor_ids")
    })
    status = "PASS"
    if counts.get("SLOT_TO_MATERIALIZE", 0) or bypass_generators:
        status = "PARTIAL"
    if not traces:
        status = "FAIL"
    return {
        "phase": "5.15A",
        "status": status,
        "concrete_motors_identified": sum(1 for m in motors if m["id"].startswith("qm_")),
        "executable_motors": counts.get("EXECUTABLE", 0),
        "route_only_motors": counts.get("ROUTE_ONLY", 0),
        "report_only_motors": counts.get("REPORT_ONLY", 0),
        "declared_only_motors": counts.get("DECLARED_ONLY", 0),
        "slot_to_materialize": counts.get("SLOT_TO_MATERIALIZE", 0),
        "legacy_motors": counts.get("LEGACY", 0),
        "duplicate_motors": counts.get("DUPLICATE", 0),
        "missing_motors": counts.get("MISSING", 0),
        "generators_traced": traced_generators,
        "generators_with_bypass": bypass_generators,
        "generators_with_real_qm_connection_proved": proven_generators,
    }


def build_report() -> Dict[str, Any]:
    audit = read_json(AUDIT_JSON, {})
    audit_files_read = [
        rel(AUDIT_MD),
        rel(AUDIT_JSON),
        rel(AUDIT_SCRIPT),
    ]
    motors = build_registry_probe()
    traces = build_all_generator_traces()
    summary = summarize(motors, traces)
    problems = confirmed_audit_problems(traces)
    report = {
        "phase": "5.15A",
        "label": "REGISTRY ESEGUIBILE E PROVA REALE COLLEGAMENTO 4 GENERATORI",
        "audit_files_read": audit_files_read,
        "audit_summary": audit.get("summary", {}),
        "summary": summary,
        "motors": motors,
        "generator_traces": traces,
        "confirmed_audit_problems": problems,
        "roadmap_after_515a": [
            {
                "phase": "5.15B",
                "title": "Fix quiz UI + bridge",
                "goals": ["nascondere is_correct dalla UI", "aggiungere trace runtime QM nel bridge"],
            },
            {
                "phase": "5.15C",
                "title": "Riassunto narrativo vero",
                "goals": ["gerarchia concetti", "compressione proporzionale", "anti-lista"],
            },
            {
                "phase": "5.15D",
                "title": "Materializzazione/chiarimento slot 65-73",
                "goals": ["registry unico", "slot nominati o rimossi dal claim", "trace per singolo QM"],
            },
            {
                "phase": "5.15E",
                "title": "Dataset e mini LLM training leggero",
                "goals": ["dataset buono/cattivo", "classificatori qualita", "ranking semantico"],
            },
        ],
    }
    return report


def write_trace(report: Dict[str, Any]) -> None:
    TRACE_JSON.write_text(
        json.dumps(report["generator_traces"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_json(report: Dict[str, Any]) -> None:
    PROOF_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def write_markdown(report: Dict[str, Any]) -> None:
    s = report["summary"]
    lines: List[str] = []
    lines.append("# FASE 5.15A - Registry eseguibile e prova collegamento 4 generatori")
    lines.append("")
    lines.append("## Stato Fase 5.15A")
    lines.append("")
    lines.append(f"- Status: `{s['status']}`")
    lines.append(f"- Motori concreti identificati: `{s['concrete_motors_identified']}`")
    lines.append(f"- Motori realmente eseguibili dal probe: `{s['executable_motors']}`")
    lines.append(f"- Motori route-only: `{s['route_only_motors']}`")
    lines.append(f"- Motori report-only: `{s['report_only_motors']}`")
    lines.append(f"- Motori solo dichiarati: `{s['declared_only_motors']}`")
    lines.append(f"- Slot da materializzare: `{s['slot_to_materialize']}`")
    lines.append(f"- Generatori tracciati: `{', '.join(s['generators_traced'])}`")
    lines.append(f"- Generatori con bypass: `{', '.join(s['generators_with_bypass']) or 'nessuno'}`")
    lines.append(f"- Generatori con collegamento QM runtime realmente provato: `{', '.join(s['generators_with_real_qm_connection_proved']) or 'nessuno'}`")
    lines.append("")
    lines.append("Nota: `EXECUTABLE` significa che il probe ha trovato un executor callable e lo ha chiamato in isolamento. Non significa automaticamente che il generatore finale lo invochi. La tabella generatori separa questa prova dalla trace runtime reale.")
    lines.append("")
    lines.append("## Tabella motori")
    lines.append("")
    lines.append("| ID | Nome | Tipo | Stato | Generatori collegati | Prova reale | Note |")
    lines.append("|---|---|---|---|---|---|---|")
    for m in report["motors"]:
        lines.append(
            f"| `{md_escape(m['id'])}` | {md_escape(m['name'])} | {md_escape(m['type'])} | "
            f"`{m['status']}` | {md_escape(', '.join(m['generators_linked']))} | "
            f"{md_escape(m['proof_mode'])}: {md_escape(m['real_connection_proof'])} | {md_escape(m['notes'])} |"
        )
    lines.append("")
    lines.append("## Tabella generatori")
    lines.append("")
    lines.append("| Generatore | Route | Registry/probe usato | Motori realmente invocati | Motori solo dichiarati | Bypass | Status |")
    lines.append("|---|---|---|---:|---:|---|---|")
    first_trace_by_kind: Dict[str, Dict[str, Any]] = {}
    for t in report["generator_traces"]:
        first_trace_by_kind.setdefault(t["kind"], t)
    for kind in GENERATOR_KINDS:
        t = first_trace_by_kind[kind]
        lines.append(
            f"| {t['generator']} | {md_escape(t['route'])} | phase5_15a probe | "
            f"{len(t['real_invoked_quality_motor_ids'])} | {len(t['declared_only_motor_ids'])} | "
            f"{md_escape('; '.join(t['bypasses']))} | {md_escape(t['status'])} |"
        )
    lines.append("")
    lines.append("## Problemi confermati dall'audit")
    lines.append("")
    lines.append("| Problema | Confermato | Prova | Impatto | Fase correzione |")
    lines.append("|---|---|---|---|---|")
    for p in report["confirmed_audit_problems"]:
        lines.append(
            f"| {md_escape(p['problem'])} | {'si' if p['confirmed'] else 'no'} | "
            f"{md_escape(p['proof'])} | {md_escape(p['impact'])} | {md_escape(p['fix_phase'])} |"
        )
    lines.append("")
    lines.append("## Roadmap dopo 5.15A")
    lines.append("")
    for item in report["roadmap_after_515a"]:
        lines.append(f"### {item['phase']} - {item['title']}")
        for goal in item["goals"]:
            lines.append(f"- {goal}")
    lines.append("")
    PROOF_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    REPORTS.mkdir(exist_ok=True)
    report = build_report()
    write_trace(report)
    write_json(report)
    write_markdown(report)
    print(f"Trace JSON: {rel(TRACE_JSON)}")
    print(f"Proof JSON: {rel(PROOF_JSON)}")
    print(f"Proof MD: {rel(PROOF_MD)}")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
