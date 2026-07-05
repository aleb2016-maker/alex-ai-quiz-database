#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.11 — PIPELINE OUTPUT READY GATE

Obiettivo:
- eseguire la pipeline 5 fasi esistente
- intercettare i report/output finali generati
- controllare registry completo
- verificare summary/card/quiz/study dopo tutti i motori
- produrre report finale "pipeline output ready"

Questo script NON crea nuovi motori.
Questo script NON modifica UI/CSS/PDF/grafica.
Questo script è un gate finale di controllo/report.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"

OUT_JSON = REPORTS_DIR / "phase5_11_pipeline_output_ready_report.json"
OUT_MD = REPORTS_DIR / "phase5_11_pipeline_output_ready_report.md"

PHASE = "5.11"
READY_LABEL = "PIPELINE_OUTPUT_READY"

MIN_EXPECTED_REGISTRY_MOTORS = int(os.getenv("PHASE5_11_MIN_REGISTRY_MOTORS", "11"))

OUTPUT_AREAS = {
    "summary": [
        "summary",
        "riassunto",
        "sintesi",
        "panoramica",
        "overview",
    ],
    "card": [
        "card",
        "cards",
        "scheda",
        "schede",
        "flashcard",
    ],
    "quiz": [
        "quiz",
        "test",
        "question",
        "questions",
        "domanda",
        "domande",
        "opzioni",
        "options",
        "risposta_corretta",
        "correct_answer",
    ],
    "study": [
        "study",
        "study_questions",
        "domande studio",
        "domande_studio",
        "risposte guida",
        "guida allo studio",
        "studio",
    ],
}

BAD_OUTPUT_PATTERNS = [
    r"\bfallback\b",
    r"\bdemo\b",
    r"\blorem ipsum\b",
    r"\btodo\b",
    r"\bplaceholder\b",
    r"\bknowledge_base_json\b",
    r"\bdocumento analizzato\b",
    r"\boutput non disponibile\b",
    r"\bnessun contenuto\b",
    r"\btesto di esempio\b",
    r"\bsicurezza informatica aziendale\b",
    r"\bl['’]azienda ha cominciato\b",
    r"\bquesta azienda\b",
    r"\bha cominciato nel\b",
]


@dataclass
class CommandResult:
    command: List[str]
    returncode: int
    duration_seconds: float
    stdout_tail: str
    stderr_tail: str


@dataclass
class AreaCheck:
    area: str
    status: str
    evidence_files: List[str]
    defects: List[str]
    warnings: List[str]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except Exception:
        return str(path)


def safe_read_text(path: Path, limit: int = 600_000) -> str:
    try:
        data = path.read_text(encoding="utf-8", errors="replace")
        if len(data) > limit:
            return data[:limit] + "\n...[TRUNCATED_FOR_PHASE5_11]..."
        return data
    except Exception:
        return ""


def safe_load_json(path: Path) -> Optional[Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def list_report_files() -> List[Path]:
    if not REPORTS_DIR.exists():
        return []
    files: List[Path] = []
    for ext in ("*.json", "*.md", "*.txt"):
        files.extend(REPORTS_DIR.rglob(ext))
    return sorted(set(files), key=lambda p: p.stat().st_mtime if p.exists() else 0)


def snapshot_files(files: List[Path]) -> Dict[str, Tuple[int, int]]:
    snap: Dict[str, Tuple[int, int]] = {}
    for p in files:
        try:
            st = p.stat()
            snap[str(p)] = (st.st_mtime_ns, st.st_size)
        except Exception:
            continue
    return snap


def changed_files(before: Dict[str, Tuple[int, int]], after_files: List[Path]) -> List[Path]:
    changed: List[Path] = []
    for p in after_files:
        key = str(p)
        try:
            st = p.stat()
            current = (st.st_mtime_ns, st.st_size)
            if key not in before or before[key] != current:
                changed.append(p)
        except Exception:
            continue
    return sorted(changed, key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)


def tail(text: str, max_chars: int = 6000) -> str:
    text = text or ""
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]


def discover_pipeline_command() -> Tuple[Optional[List[str]], List[Dict[str, Any]]]:
    env_cmd = os.getenv("PHASE5_PIPELINE_CMD", "").strip()
    if env_cmd:
        return shlex.split(env_cmd), [{"source": "PHASE5_PIPELINE_CMD", "command": env_cmd, "score": 9999}]

    exact_candidates = [
        "scripts/test_phase5_pipeline_5_fasi.py",
        "scripts/test_phase5_pipeline_regression.py",
        "scripts/run_phase5_pipeline_5_fasi.py",
        "scripts/run_phase5_pipeline.py",
        "scripts/verifica_phase5_pipeline_5_fasi.py",
        "scripts/verifica_phase5_pipeline.py",
        "backend/test_phase5_pipeline_5_fasi.py",
        "backend/test_phase5_pipeline.py",
        "backend/test_pipeline_5_fasi.py",
    ]

    scored: List[Dict[str, Any]] = []

    for candidate in exact_candidates:
        p = ROOT / candidate
        if p.exists():
            content = safe_read_text(p, limit=80_000).lower()
            score = 100
            if "pipeline" in candidate.lower():
                score += 30
            if "5_fasi" in candidate.lower() or "5 fasi" in content:
                score += 40
            if "registry" in content:
                score += 15
            if "summary" in content or "riassunto" in content:
                score += 10
            if "quiz" in content:
                score += 10
            scored.append({"path": candidate, "score": score, "reason": "exact_candidate"})

    for base in (ROOT / "scripts", ROOT / "backend"):
        if not base.exists():
            continue

        for p in base.rglob("*.py"):
            if p.name == Path(__file__).name:
                continue

            lower_path = rel(p).lower()

            if any(x in lower_path for x in [
                "patch_",
                "installa",
                "install",
                "backup",
                ".bak",
                "__pycache__",
            ]):
                continue

            content = safe_read_text(p, limit=90_000).lower()

            score = 0

            if "phase5" in lower_path or "phase_5" in lower_path or "fase5" in lower_path or "fase_5" in lower_path:
                score += 35
            if "pipeline" in lower_path:
                score += 35
            if "5_fasi" in lower_path or "5 fasi" in content or "cinque fasi" in content:
                score += 40
            if "registry" in lower_path or "registry" in content:
                score += 20
            if "regression" in lower_path or "regressione" in lower_path:
                score += 15
            if "summary" in content or "riassunto" in content:
                score += 8
            if "card" in content:
                score += 8
            if "quiz" in content:
                score += 8
            if "study" in content or "domande studio" in content:
                score += 8
            if "pass" in content:
                score += 3

            if score >= 65:
                scored.append({"path": rel(p), "score": score, "reason": "discovered"})

    scored = sorted(scored, key=lambda x: x["score"], reverse=True)

    if not scored:
        return None, []

    selected = scored[0]["path"]
    return [sys.executable, str(ROOT / selected)], scored[:10]


def run_command(cmd: List[str]) -> CommandResult:
    started = time.time()
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=int(os.getenv("PHASE5_11_TIMEOUT_SECONDS", "240")),
    )
    duration = time.time() - started
    return CommandResult(
        command=cmd,
        returncode=proc.returncode,
        duration_seconds=round(duration, 3),
        stdout_tail=tail(proc.stdout),
        stderr_tail=tail(proc.stderr),
    )


def flatten_json_text(obj: Any, limit_items: int = 40000) -> str:
    chunks: List[str] = []
    seen = 0

    def walk(value: Any) -> None:
        nonlocal seen
        if seen >= limit_items:
            return
        seen += 1

        if isinstance(value, dict):
            for k, v in value.items():
                chunks.append(str(k))
                walk(v)
        elif isinstance(value, list):
            for item in value:
                walk(item)
        elif value is not None:
            chunks.append(str(value))

    walk(obj)
    return "\n".join(chunks)


def score_final_output_candidate(path: Path) -> int:
    name = rel(path).lower()
    text = safe_read_text(path, limit=250_000).lower()

    score = 0
    if "phase5" in name or "phase_5" in name or "fase5" in name or "fase_5" in name:
        score += 20
    if "pipeline" in name:
        score += 25
    if "final" in name or "ready" in name or "output" in name:
        score += 20
    if "registry" in name:
        score += 8
    if "quality" in name or "qualita" in name:
        score += 8

    for area, keywords in OUTPUT_AREAS.items():
        if any(k.lower() in text for k in keywords):
            score += 15

    if "pass" in text:
        score += 4
    if "fail" in text:
        score -= 2

    return score


def latest_output_candidates(changed: List[Path], all_reports: List[Path]) -> List[Path]:
    pool = list(dict.fromkeys(changed + sorted(all_reports, key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)[:40]))
    scored = [(score_final_output_candidate(p), p) for p in pool]
    scored = sorted(scored, key=lambda x: x[0], reverse=True)
    return [p for score, p in scored if score > 0][:10]


def find_registry_files(all_reports: List[Path]) -> List[Path]:
    candidates: List[Path] = []
    for p in all_reports:
        name = rel(p).lower()
        if p.suffix.lower() != ".json":
            continue
        if "registry" in name or "quality_snapshot" in name or "qualita" in name:
            candidates.append(p)

    candidates = sorted(
        set(candidates),
        key=lambda p: p.stat().st_mtime if p.exists() else 0,
        reverse=True,
    )
    return list(candidates)[:20]


def recursive_registry_count(obj: Any) -> int:
    explicit_counts: List[int] = []
    structural_counts: List[int] = []

    def walk(value: Any, parent_key: str = "") -> None:
        if isinstance(value, dict):
            for k, v in value.items():
                lk = str(k).lower()

                if lk in {
                    "registry_motors_count",
                    "motors_count",
                    "engines_count",
                    "validators_count",
                    "connected_motors",
                    "registry_count",
                }:
                    if isinstance(v, int):
                        explicit_counts.append(v)

                if lk in {
                    "motors",
                    "registry_motors",
                    "engines",
                    "validators",
                    "checks",
                    "quality_motors",
                    "motori",
                    "motori_registry",
                }:
                    if isinstance(v, list):
                        structural_counts.append(len(v))
                    elif isinstance(v, dict):
                        structural_counts.append(len(v.keys()))

                walk(v, lk)

        elif isinstance(value, list):
            for item in value:
                walk(item, parent_key)

    walk(obj)

    if explicit_counts:
        return max(explicit_counts)
    if structural_counts:
        return max(structural_counts)
    return 0


def check_registry(registry_files: List[Path]) -> Dict[str, Any]:
    loaded: List[Tuple[Path, Any, str]] = []
    combined_text_parts: List[str] = []

    for p in registry_files:
        obj = safe_load_json(p)
        if obj is None:
            continue
        txt = flatten_json_text(obj).lower()
        loaded.append((p, obj, txt))
        combined_text_parts.append(txt)

    combined = "\n".join(combined_text_parts)
    max_count = 0

    for _, obj, _ in loaded:
        max_count = max(max_count, recursive_registry_count(obj))

    area_presence = {}
    for area, keywords in OUTPUT_AREAS.items():
        area_presence[area] = any(k.lower() in combined for k in keywords)

    defects: List[str] = []
    warnings: List[str] = []

    if not loaded:
        defects.append("registry_json_not_found_or_not_readable")

    if max_count < MIN_EXPECTED_REGISTRY_MOTORS:
        defects.append(f"registry_motors_count_too_low:{max_count}<expected:{MIN_EXPECTED_REGISTRY_MOTORS}")

    missing_areas = [a for a, ok in area_presence.items() if not ok]
    if missing_areas:
        warnings.append("registry_area_keywords_not_all_detected:" + ",".join(missing_areas))

    status = "PASS" if not defects else "FAIL"

    return {
        "status": status,
        "registry_files": [rel(p) for p, _, _ in loaded],
        "registry_motors_count_detected": max_count,
        "min_expected_registry_motors": MIN_EXPECTED_REGISTRY_MOTORS,
        "area_presence": area_presence,
        "defects": defects,
        "warnings": warnings,
    }


def area_check(area: str, candidates: List[Path]) -> AreaCheck:
    keywords = [k.lower() for k in OUTPUT_AREAS[area]]

    evidence: List[str] = []
    defects: List[str] = []
    warnings: List[str] = []

    combined = ""

    for p in candidates:
        txt = safe_read_text(p, limit=400_000)
        low = txt.lower()

        if any(k in low for k in keywords):
            evidence.append(rel(p))
            combined += "\n" + txt

    low_combined = combined.lower()

    if not evidence:
        defects.append(f"{area}_not_detected_in_final_reports")
        return AreaCheck(area=area, status="FAIL", evidence_files=[], defects=defects, warnings=warnings)

    for pattern in BAD_OUTPUT_PATTERNS:
        if re.search(pattern, low_combined, flags=re.IGNORECASE):
            defects.append(f"bad_pattern_detected:{pattern}")

    useful_chars = len(re.sub(r"\s+", "", combined))
    if useful_chars < 120:
        defects.append(f"{area}_content_too_short:{useful_chars}")

    if area == "quiz":
        question_marks = combined.count("?")
        option_hits = len(re.findall(r"\b[A-D][\).\]]|\bopzioni\b|\boptions\b", combined, flags=re.IGNORECASE))
        if question_marks < 1:
            warnings.append("quiz_question_mark_not_detected")
        if option_hits < 1:
            warnings.append("quiz_options_not_clearly_detected")

    if area == "study":
        question_hits = len(re.findall(r"\?|domanda|domande|spiega|descrivi|confronta", combined, flags=re.IGNORECASE))
        if question_hits < 1:
            warnings.append("study_question_structure_not_clearly_detected")

    if area == "summary":
        if len(combined.split()) < 20:
            warnings.append("summary_word_count_low")

    if area == "card":
        card_hits = len(re.findall(r"\bcard\b|\bscheda\b|\btitolo\b|\btitle\b", combined, flags=re.IGNORECASE))
        if card_hits < 1:
            warnings.append("card_structure_not_clearly_detected")

    status = "PASS" if not defects else "FAIL"

    return AreaCheck(
        area=area,
        status=status,
        evidence_files=sorted(set(evidence)),
        defects=defects,
        warnings=warnings,
    )


def write_reports(report: Dict[str, Any]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    checks = report.get("output_checks", {})
    registry = report.get("registry_check", {})
    pipeline = report.get("pipeline_run", {})

    lines: List[str] = []
    lines.append("# Fase 5.11 — Pipeline Output Ready Report")
    lines.append("")
    lines.append(f"- Status: **{report.get('status')}**")
    lines.append(f"- Ready label: `{report.get('ready_label')}`")
    lines.append(f"- Pipeline output ready: `{report.get('pipeline_output_ready')}`")
    lines.append(f"- Generated at: `{report.get('generated_at')}`")
    lines.append("")
    lines.append("## Pipeline")
    lines.append("")
    lines.append(f"- Command: `{ ' '.join(pipeline.get('command', [])) }`")
    lines.append(f"- Return code: `{pipeline.get('returncode')}`")
    lines.append(f"- Duration seconds: `{pipeline.get('duration_seconds')}`")
    lines.append("")
    lines.append("## Registry")
    lines.append("")
    lines.append(f"- Status: **{registry.get('status')}**")
    lines.append(f"- Motors detected: `{registry.get('registry_motors_count_detected')}`")
    lines.append(f"- Minimum expected: `{registry.get('min_expected_registry_motors')}`")
    lines.append(f"- Registry files: `{registry.get('registry_files')}`")
    lines.append(f"- Defects: `{registry.get('defects')}`")
    lines.append(f"- Warnings: `{registry.get('warnings')}`")
    lines.append("")
    lines.append("## Output areas")
    lines.append("")

    for area in ["summary", "card", "quiz", "study"]:
        item = checks.get(area, {})
        lines.append(f"### {area}")
        lines.append("")
        lines.append(f"- Status: **{item.get('status')}**")
        lines.append(f"- Evidence files: `{item.get('evidence_files')}`")
        lines.append(f"- Defects: `{item.get('defects')}`")
        lines.append(f"- Warnings: `{item.get('warnings')}`")
        lines.append("")

    lines.append("## Final output candidates")
    lines.append("")
    for p in report.get("final_output_candidates", []):
        lines.append(f"- `{p}`")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    before = snapshot_files(list_report_files())

    command, discovered = discover_pipeline_command()

    if not command:
        report = {
            "phase": PHASE,
            "generated_at": now_iso(),
            "status": "FAIL",
            "pipeline_output_ready": False,
            "ready_label": None,
            "objective": [
                "execute_5_phase_pipeline",
                "intercept_final_output",
                "check_complete_registry",
                "verify_summary_card_quiz_study_after_all_motors",
                "produce_pipeline_output_ready_report",
            ],
            "pipeline_run": {
                "command": None,
                "returncode": None,
                "duration_seconds": 0,
                "stdout_tail": "",
                "stderr_tail": "No existing 5-phase pipeline command discovered. Set PHASE5_PIPELINE_CMD.",
            },
            "pipeline_discovery": discovered,
            "registry_check": {
                "status": "FAIL",
                "defects": ["pipeline_not_executed"],
                "warnings": [],
            },
            "output_checks": {},
            "final_output_candidates": [],
        }
        write_reports(report)
        print(f"FAIL - Fase 5.11: pipeline command not discovered. Report: {rel(OUT_JSON)}")
        return 1

    pipeline_result = run_command(command)

    all_reports = list_report_files()
    changed = changed_files(before, all_reports)
    candidates = latest_output_candidates(changed, all_reports)

    registry_files = find_registry_files(all_reports)
    registry_check = check_registry(registry_files)

    output_checks_obj: Dict[str, AreaCheck] = {}
    for area in ["summary", "card", "quiz", "study"]:
        output_checks_obj[area] = area_check(area, candidates)

    output_checks = {area: asdict(check) for area, check in output_checks_obj.items()}

    failures: List[str] = []

    if pipeline_result.returncode != 0:
        failures.append("pipeline_returncode_non_zero")

    if registry_check.get("status") != "PASS":
        failures.append("registry_check_failed")

    for area, check in output_checks.items():
        if check.get("status") != "PASS":
            failures.append(f"{area}_check_failed")

    if not candidates:
        failures.append("final_output_candidates_not_found")

    pipeline_output_ready = not failures

    report = {
        "phase": PHASE,
        "generated_at": now_iso(),
        "status": "PASS" if pipeline_output_ready else "FAIL",
        "pipeline_output_ready": pipeline_output_ready,
        "ready_label": READY_LABEL if pipeline_output_ready else None,
        "objective": [
            "execute_5_phase_pipeline",
            "intercept_final_output",
            "check_complete_registry",
            "verify_summary_card_quiz_study_after_all_motors",
            "produce_pipeline_output_ready_report",
        ],
        "failures": failures,
        "pipeline_discovery": discovered,
        "pipeline_run": asdict(pipeline_result),
        "changed_reports": [rel(p) for p in changed],
        "final_output_candidates": [rel(p) for p in candidates],
        "registry_check": registry_check,
        "output_checks": output_checks,
        "report_files": {
            "json": rel(OUT_JSON),
            "markdown": rel(OUT_MD),
        },
        "scope_guard": {
            "ui_css_pdf_graphics_touched": False,
            "new_generation_motors_created": False,
            "purpose": "final_quality_gate_and_report_only",
        },
    }

    write_reports(report)

    if pipeline_output_ready:
        print(f"PASS - Fase 5.11: {READY_LABEL}")
        print(f"Report JSON: {rel(OUT_JSON)}")
        print(f"Report MD:   {rel(OUT_MD)}")
        return 0

    print("FAIL - Fase 5.11: pipeline output not ready")
    print(f"Report JSON: {rel(OUT_JSON)}")
    print(f"Report MD:   {rel(OUT_MD)}")
    print("Failures:", ", ".join(failures))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
