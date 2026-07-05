from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from backend.legacy_quality_motor_registry_v1 import LEGACY_QUALITY_MOTORS


REPORT_JSON = ROOT / "reports" / "phase5_9_4_existing_quiz_quality_motors_v1.json"
REPORT_MD = ROOT / "reports" / "phase5_9_4_existing_quiz_quality_motors_v1.md"


PYTHON_SCAN_ROOTS = [
    ROOT / "backend",
    ROOT / "scripts",
]

FRONTEND_SCAN_ROOTS = [
    ROOT / "demo",
    ROOT / "demo-rag",
    ROOT / "runtime",
]


CAPABILITY_KEYWORDS = {
    "quiz_question_naturalness": [
        "naturalezza",
        "naturale",
        "domanda",
        "question",
        "meccanica",
        "ripetitiv",
        "quale affermazione",
        "supportata dal documento",
        "formula meccanica",
    ],
    "strong_distractors": [
        "distrattor",
        "opzioni",
        "options",
        "plausibil",
        "forti",
        "source_facts",
        "fatti veri",
        "true_fact",
        "is_correct",
    ],
    "grammar_accents_text_quality": [
        "grammatica",
        "accent",
        "apostrof",
        "punteggiatura",
        "spazi",
        "perchè",
        "perché",
        "qual e",
        "qual è",
        "non non",
    ],
    "quiz_explanation_quality": [
        "spiegazione",
        "explanation",
        "risposta",
        "answer",
        "chiar",
        "feedback",
    ],
    "interactive_quiz_frontend": [
        "punteggio",
        "score",
        "feedback",
        "onclick",
        "addEventListener",
        "correct_option",
        "is_correct",
        "mostra",
        "nascond",
        "risposta corretta",
    ],
}


NEGATIVE_NOISE = [
    ".bak",
    "__pycache__",
    ".venv",
    "node_modules",
    ".git",
]


def rel_module_from_path(path: Path) -> str:
    rel = path.relative_to(ROOT).with_suffix("")
    return ".".join(rel.parts)


def should_skip(path: Path) -> bool:
    path_text = str(path)
    return any(token in path_text for token in NEGATIVE_NOISE)


def keyword_hits(text: str, keywords: List[str]) -> int:
    lower = text.lower()
    total = 0

    for keyword in keywords:
        total += lower.count(keyword.lower())

    return total


def classify_capabilities(text: str) -> Dict[str, int]:
    return {
        capability: keyword_hits(text, keywords)
        for capability, keywords in CAPABILITY_KEYWORDS.items()
    }


def capability_score(capabilities: Dict[str, int]) -> int:
    return sum(capabilities.values())


def source_segment(lines: List[str], node: ast.AST) -> str:
    lineno = getattr(node, "lineno", 1)
    end_lineno = getattr(node, "end_lineno", lineno)

    start = max(lineno - 1, 0)
    end = min(end_lineno, len(lines))

    return "\n".join(lines[start:end])


def scan_python_functions() -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []

    for root in PYTHON_SCAN_ROOTS:
        if not root.exists():
            continue

        for path in root.rglob("*.py"):
            if should_skip(path):
                continue

            text = path.read_text(encoding="utf-8", errors="ignore")

            try:
                tree = ast.parse(text)
            except SyntaxError:
                continue

            lines = text.splitlines()
            module_name = rel_module_from_path(path)

            for node in ast.walk(tree):
                if not isinstance(node, ast.FunctionDef):
                    continue

                segment = source_segment(lines, node)
                combined = f"{node.name}\n{segment}"

                capabilities = classify_capabilities(combined)
                score = capability_score(capabilities)

                if score <= 0:
                    continue

                motor_id = f"{module_name}.{node.name}"

                candidates.append(
                    {
                        "kind": "python_function",
                        "path": str(path.relative_to(ROOT)),
                        "module_name": module_name,
                        "function_name": node.name,
                        "motor_id": motor_id,
                        "lineno": node.lineno,
                        "score": score,
                        "capabilities": capabilities,
                        "top_capabilities": [
                            name for name, count in sorted(
                                capabilities.items(),
                                key=lambda item: item[1],
                                reverse=True,
                            )
                            if count > 0
                        ],
                    }
                )

    candidates.sort(key=lambda item: item["score"], reverse=True)
    return candidates


def scan_frontend_files() -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []

    allowed_suffixes = {".html", ".js", ".css", ".ts", ".tsx", ".jsx"}

    for root in FRONTEND_SCAN_ROOTS:
        if not root.exists():
            continue

        for path in root.rglob("*"):
            if should_skip(path):
                continue

            if path.suffix.lower() not in allowed_suffixes:
                continue

            text = path.read_text(encoding="utf-8", errors="ignore")
            capabilities = classify_capabilities(text)
            score = capability_score(capabilities)

            if score <= 0:
                continue

            candidates.append(
                {
                    "kind": "frontend_file",
                    "path": str(path.relative_to(ROOT)),
                    "score": score,
                    "capabilities": capabilities,
                    "top_capabilities": [
                        name for name, count in sorted(
                            capabilities.items(),
                            key=lambda item: item[1],
                            reverse=True,
                        )
                        if count > 0
                    ],
                }
            )

    candidates.sort(key=lambda item: item["score"], reverse=True)
    return candidates


def registry_specs() -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}

    for spec in LEGACY_QUALITY_MOTORS:
        motor_id = getattr(spec, "motor_id", "")

        out[motor_id] = {
            "motor_id": motor_id,
            "module_name": getattr(spec, "module_name", ""),
            "function_name": getattr(spec, "function_name", ""),
            "adapter_name": getattr(spec, "adapter_name", ""),
            "target_kind": getattr(spec, "target_kind", ""),
        }

    return out


def summarize_by_capability(candidates: List[Dict[str, Any]], registered_ids: Set[str]) -> Dict[str, Dict[str, int]]:
    summary: Dict[str, Dict[str, int]] = {}

    for capability in CAPABILITY_KEYWORDS:
        summary[capability] = {
            "candidates": 0,
            "registered": 0,
            "unregistered": 0,
        }

    for item in candidates:
        motor_id = item.get("motor_id")
        is_registered = motor_id in registered_ids

        for capability, count in item.get("capabilities", {}).items():
            if count <= 0:
                continue

            summary[capability]["candidates"] += 1

            if is_registered:
                summary[capability]["registered"] += 1
            else:
                summary[capability]["unregistered"] += 1

    return summary


def build_recommendations(
    python_candidates: List[Dict[str, Any]],
    frontend_candidates: List[Dict[str, Any]],
    registered: Dict[str, Dict[str, Any]],
    capability_summary: Dict[str, Dict[str, int]],
) -> List[Dict[str, Any]]:
    recommendations: List[Dict[str, Any]] = []

    quiz_registered = [
        item for item in registered.values()
        if item.get("target_kind") == "quiz"
    ]

    recommendations.append(
        {
            "priority": 1,
            "area": "quiz_backend_mapping",
            "action": "Verificare quali motori quiz già esistenti sono candidati ma non ancora nel registry.",
            "why": (
                "Il registry ora corregge i distrattori veri, ma restano naturalezza domanda, "
                "ripetitività e spiegazioni."
            ),
            "registered_quiz_motors_count": len(quiz_registered),
        }
    )

    for capability, data in capability_summary.items():
        if data["unregistered"] > 0:
            recommendations.append(
                {
                    "priority": 2,
                    "area": capability,
                    "action": "Creare shortlist e test compatibilità per candidati non registrati.",
                    "why": (
                        f"Trovati {data['unregistered']} candidati non registrati "
                        f"per capability {capability}."
                    ),
                }
            )

    if frontend_candidates:
        recommendations.append(
            {
                "priority": 3,
                "area": "interactive_quiz_frontend",
                "action": "Trattare visibilità risposta corretta, click, feedback e punteggio come test frontend separato.",
                "why": (
                    "La comparsa della risposta corretta dopo il click non è un motore backend: "
                    "è comportamento UI/JS da validare nella pagina."
                ),
                "frontend_candidates_count": len(frontend_candidates),
            }
        )

    recommendations.sort(key=lambda item: item["priority"])
    return recommendations


def main() -> int:
    registered = registry_specs()
    registered_ids = set(registered.keys())

    python_candidates = scan_python_functions()
    frontend_candidates = scan_frontend_files()

    for item in python_candidates:
        motor_id = item.get("motor_id")
        item["registered_in_registry"] = motor_id in registered_ids
        item["registry_spec"] = registered.get(motor_id)

    capability_summary = summarize_by_capability(python_candidates, registered_ids)

    quiz_registered = [
        item for item in registered.values()
        if item.get("target_kind") == "quiz"
    ]

    quiz_related_registered = [
        item for item in python_candidates
        if item.get("registered_in_registry") is True
        and (
            item.get("registry_spec", {}).get("target_kind") == "quiz"
            or "quiz" in item.get("top_capabilities", [])
            or "strong_distractors" in item.get("top_capabilities", [])
        )
    ]

    top_unregistered = [
        item for item in python_candidates
        if item.get("registered_in_registry") is False
    ][:80]

    recommendations = build_recommendations(
        python_candidates=python_candidates,
        frontend_candidates=frontend_candidates,
        registered=registered,
        capability_summary=capability_summary,
    )

    report = {
        "report_name": "phase5_9_4_existing_quiz_quality_motors_v1",
        "status": "PASS_DIAGNOSTIC",
        "registry_motors_count": len(registered),
        "registry_quiz_motors_count": len(quiz_registered),
        "python_candidates_count": len(python_candidates),
        "frontend_candidates_count": len(frontend_candidates),
        "capability_summary": capability_summary,
        "registry_quiz_motors": quiz_registered,
        "quiz_related_registered_candidates": quiz_related_registered,
        "top_unregistered_python_candidates": top_unregistered,
        "top_frontend_candidates": frontend_candidates[:60],
        "recommendations": recommendations,
        "notes": [
            "Diagnostico: non modifica registry, motori o frontend.",
            "Serve a capire quali motori già esistenti possono migliorare domanda quiz, spiegazioni, grammatica, naturalezza e distrattori.",
            "La visibilità della risposta corretta dopo il click è comportamento frontend, non motore backend.",
        ],
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Fase 5.9.4 — Existing Quiz Quality Motors Map V1\n")
    lines.append(f"- Status: `{report['status']}`")
    lines.append(f"- Motori registry totali: `{len(registered)}`")
    lines.append(f"- Motori registry target quiz: `{len(quiz_registered)}`")
    lines.append(f"- Candidati Python trovati: `{len(python_candidates)}`")
    lines.append(f"- Candidati frontend trovati: `{len(frontend_candidates)}`")
    lines.append("")
    lines.append("## Capability summary Python\n")
    lines.append("| Capability | Candidati | Già registrati | Non registrati |")
    lines.append("|---|---:|---:|---:|")

    for capability, data in capability_summary.items():
        lines.append(
            f"| `{capability}` "
            f"| {data['candidates']} "
            f"| {data['registered']} "
            f"| {data['unregistered']} |"
        )

    lines.append("")
    lines.append("## Motori target quiz già nel registry\n")
    lines.append("| Motor ID | Adapter | Target kind |")
    lines.append("|---|---|---|")

    for item in quiz_registered:
        lines.append(
            f"| `{item['motor_id']}` "
            f"| `{item['adapter_name']}` "
            f"| `{item['target_kind']}` |"
        )

    lines.append("")
    lines.append("## Candidati Python non registrati più forti\n")
    lines.append("| Score | File | Funzione | Capability |")
    lines.append("|---:|---|---|---|")

    for item in top_unregistered[:40]:
        lines.append(
            f"| {item['score']} "
            f"| `{item['path']}:{item['lineno']}` "
            f"| `{item['function_name']}` "
            f"| `{', '.join(item['top_capabilities'])}` |"
        )

    lines.append("")
    lines.append("## Candidati frontend/interattività\n")
    lines.append("| Score | File | Capability |")
    lines.append("|---:|---|---|")

    for item in frontend_candidates[:30]:
        lines.append(
            f"| {item['score']} "
            f"| `{item['path']}` "
            f"| `{', '.join(item['top_capabilities'])}` |"
        )

    lines.append("")
    lines.append("## Raccomandazioni\n")

    for rec in recommendations:
        lines.append(
            f"- **Priorità {rec['priority']} — {rec['area']}**: {rec['action']} "
            f"Motivo: {rec['why']}"
        )

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("✅ FASE 5.9.4 MAPPA MOTORI QUIZ QUALITÀ COMPLETATA")
    print(f"Motori registry totali: {len(registered)}")
    print(f"Motori registry target quiz: {len(quiz_registered)}")
    print(f"Candidati Python: {len(python_candidates)}")
    print(f"Candidati frontend: {len(frontend_candidates)}")
    print(f"Report JSON: {REPORT_JSON}")
    print(f"Report MD:   {REPORT_MD}")
    print(json.dumps({
        "status": report["status"],
        "registry_quiz_motors_count": len(quiz_registered),
        "python_candidates_count": len(python_candidates),
        "frontend_candidates_count": len(frontend_candidates),
    }, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
