#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.14.0 — UI BUTTONS PROBE

Scopo:
- analizzare la pagina demo-rag/test-documenti-universale.html;
- trovare i 4 pulsanti principali;
- trovare gli script JS caricati;
- cercare handler/funzioni esistenti collegate a:
  - riassunto
  - card
  - test/quiz
  - domande studio
- produrre report JSON + MD.

Non modifica motori, UI, PDF o app.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "demo-rag" / "test-documenti-universale.html"
REPORT_JSON = ROOT / "reports" / "phase5_14_ui_buttons_probe_v1.json"
REPORT_MD = ROOT / "reports" / "phase5_14_ui_buttons_probe_v1.md"


BUTTON_TARGETS = {
    "summary": ["genera riassunto", "riassunto"],
    "cards": ["genera card", "card"],
    "quiz": ["genera test", "test", "quiz"],
    "study": ["genera domande studio", "domande studio"],
}

FORBIDDEN_UI_FRAGMENTS = [
    "fallback",
    "demo output",
    "testo di esempio",
    "sicurezza informatica aziendale",
    "knowledge_base_json",
    "documento analizzato",
    "placeholder",
]


@dataclass
class ButtonProbe:
    key: str
    expected_labels: List[str]
    found: bool
    matched_fragments: List[str]


@dataclass
class ScriptProbe:
    path: str
    exists: bool
    size: int
    matched_keywords: List[str]
    forbidden_fragments: List[str]


@dataclass
class UIProbeReport:
    phase: str
    status: str
    page: str
    page_exists: bool
    buttons: List[Dict]
    scripts: List[Dict]
    defects: List[str]
    warnings: List[str]


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def extract_script_sources(html: str) -> List[str]:
    srcs = re.findall(r"<script[^>]+src=[\"']([^\"']+)[\"']", html, flags=re.I)
    return [src.strip() for src in srcs if src.strip()]


def resolve_script(src: str) -> Path:
    clean = src.split("?", 1)[0].split("#", 1)[0]
    if clean.startswith("/"):
        return ROOT / clean.lstrip("/")
    return PAGE.parent / clean


def probe_buttons(html: str) -> List[ButtonProbe]:
    low = normalize(html)
    results: List[ButtonProbe] = []

    for key, labels in BUTTON_TARGETS.items():
        matched = [label for label in labels if label in low]
        results.append(ButtonProbe(
            key=key,
            expected_labels=labels,
            found=bool(matched),
            matched_fragments=matched,
        ))

    return results


def probe_scripts(html: str) -> List[ScriptProbe]:
    scripts: List[ScriptProbe] = []
    sources = extract_script_sources(html)

    keywords = [
        "riassunto",
        "summary",
        "card",
        "quiz",
        "test",
        "domande",
        "studio",
        "generate",
        "genera",
        "onclick",
        "addeventlistener",
    ]

    for src in sources:
        path = resolve_script(src)
        if not path.exists():
            scripts.append(ScriptProbe(
                path=src,
                exists=False,
                size=0,
                matched_keywords=[],
                forbidden_fragments=[],
            ))
            continue

        text = read(path)
        low = normalize(text)

        matched = [keyword for keyword in keywords if keyword in low]
        forbidden = [fragment for fragment in FORBIDDEN_UI_FRAGMENTS if fragment in low]

        scripts.append(ScriptProbe(
            path=str(path.relative_to(ROOT)),
            exists=True,
            size=len(text),
            matched_keywords=matched,
            forbidden_fragments=forbidden,
        ))

    return scripts


def render_md(report: UIProbeReport) -> str:
    lines = [
        "# FASE 5.14.0 — UI BUTTONS PROBE",
        "",
        f"Status: `{report.status}`",
        "",
        f"- Pagina: `{report.page}`",
        f"- Pagina esiste: `{report.page_exists}`",
        "",
        "## Pulsanti",
        "",
        "| Key | Found | Match |",
        "|---|---:|---|",
    ]

    for item in report.buttons:
        lines.append(
            f"| `{item['key']}` | `{item['found']}` | `{', '.join(item['matched_fragments'])}` |"
        )

    lines.extend([
        "",
        "## Script caricati",
        "",
        "| Script | Exists | Size | Keywords | Forbidden |",
        "|---|---:|---:|---|---|",
    ])

    for script in report.scripts:
        lines.append(
            f"| `{script['path']}` | `{script['exists']}` | `{script['size']}` | "
            f"`{', '.join(script['matched_keywords'])}` | "
            f"`{', '.join(script['forbidden_fragments'])}` |"
        )

    lines.extend(["", "## Defects", ""])
    lines.append("- Nessuno" if not report.defects else "\n".join(f"- `{d}`" for d in report.defects))

    lines.extend(["", "## Warnings", ""])
    lines.append("- Nessuno" if not report.warnings else "\n".join(f"- `{w}`" for w in report.warnings))

    lines.extend([
        "",
        "## Note",
        "",
        "- Questa fase non collega ancora i motori.",
        "- Serve a mappare pagina, pulsanti e script reali prima della patch UI.",
        "- Nessuna UI/PDF/app viene modificata.",
    ])

    return "\n".join(lines) + "\n"


def main() -> int:
    defects: List[str] = []
    warnings: List[str] = []

    if not PAGE.exists():
        defects.append(f"Pagina non trovata: {PAGE}")
        html = ""
    else:
        html = read(PAGE)

    buttons = probe_buttons(html) if html else []
    scripts = probe_scripts(html) if html else []

    for button in buttons:
        if not button.found:
            defects.append(f"Pulsante non trovato: {button.key}")

    if not scripts:
        warnings.append("Nessuno script JS esterno trovato nella pagina.")

    for script in scripts:
        if script.forbidden_fragments:
            warnings.append(
                f"Possibili frammenti demo/fallback in {script.path}: {script.forbidden_fragments}"
            )

    status = (
        "PASS - Fase 5.14.0: UI_BUTTONS_PROBE_READY"
        if not defects
        else "FAIL - Fase 5.14.0: UI_BUTTONS_PROBE_NOT_READY"
    )

    report = UIProbeReport(
        phase="5.14.0",
        status=status,
        page=str(PAGE.relative_to(ROOT)),
        page_exists=PAGE.exists(),
        buttons=[asdict(item) for item in buttons],
        scripts=[asdict(item) for item in scripts],
        defects=defects,
        warnings=warnings,
    )

    REPORT_JSON.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_MD.write_text(render_md(report), encoding="utf-8")

    print(status)
    print(f"Page: {report.page}")
    print(f"Buttons found: {sum(1 for b in buttons if b.found)}/{len(BUTTON_TARGETS)}")
    print(f"Scripts: {len(scripts)}")
    print(f"Defects: {len(defects)}")
    print(f"Warnings: {len(warnings)}")
    print(f"JSON report: {REPORT_JSON}")
    print(f"Markdown report: {REPORT_MD}")

    if defects:
        print("Defects:")
        for defect in defects:
            print(f"- {defect}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
