#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path.cwd()
PAGE = ROOT / "demo-rag/test-selezionatore-output-v35h.html"
BASE = ROOT / "dist/generated/rag_output_cleaner_finale_v35k"
REPORT = ROOT / "reports/rag_cleaner_finale_universale_v35k.md"

VISIBLE_BAD_PATTERNS = [
    ("doppio punto interrogativo", re.compile(r"\?\s*\?")),
    ("punteggiatura sporca", re.compile(r"[,;:]\s*[.!?]")),
    ("contrazione mancante", re.compile(r"\b(di|a|da|in|su)\s+il\b", re.I)),
    ("label UI vecchia nel testo visibile", re.compile(r"V3\.5J")),
    ("frase con finale sospetto", re.compile(r"\b(e|o|ma|che|di|a|da|in|con|su|per|tra|fra|del|della|dello|dei|degli|delle)\.$", re.I)),
]


def clean_page() -> list[str]:
    changes: list[str] = []
    if not PAGE.exists():
        return ["ERRORE: pagina V3.5H mancante"]

    text = PAGE.read_text(encoding="utf-8", errors="ignore")
    original = text

    # Fix generale: un precedente patcher poteva trasformare l'ultimo path in json();
    text = re.sub(
        r'(output:\s*"[^"]*output_cleaner_finale_v35k\.json)\(\);',
        r'\1"',
        text,
    )

    # Etichette UI obsolete. Non tocca le chiavi dati lowercase come accordo_pronomi_v35j.
    replacements = {
        "V3.5J": "V3.5K",
        "accordo grammaticale e pronomi": "cleaner finale universale",
        "accordo/pronomi": "cleaner finale universale",
        "output accordo/pronomi": "output cleaner finale universale",
    }
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)

    if text != original:
        PAGE.write_text(text, encoding="utf-8")
        changes.append("OK: pagina ripulita da label obsolete e path json();")
    else:
        changes.append("OK: pagina già pulita")

    return changes


def visible_texts(data: dict[str, Any]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []

    r = data.get("riassunto")
    if isinstance(r, dict):
        for key in ["titolo", "testo_breve", "conclusione"]:
            if isinstance(r.get(key), str):
                out.append((f"riassunto.{key}", r[key]))
        for i, p in enumerate(r.get("punti_chiave", []) or [], 1):
            if isinstance(p, dict):
                for key in ["titolo", "testo"]:
                    if isinstance(p.get(key), str):
                        out.append((f"riassunto.punti_chiave[{i}].{key}", p[key]))

    for i, c in enumerate(data.get("card", []) or [], 1):
        if isinstance(c, dict):
            for key in ["titolo", "testo", "messaggio_chiave"]:
                if isinstance(c.get(key), str):
                    out.append((f"card[{i}].{key}", c[key]))

    for i, s in enumerate(data.get("domande_studio", []) or [], 1):
        if isinstance(s, dict):
            for key in ["domanda", "risposta_guida"]:
                if isinstance(s.get(key), str):
                    out.append((f"domande_studio[{i}].{key}", s[key]))

    for i, t in enumerate(data.get("test", []) or [], 1):
        if isinstance(t, dict):
            for key in ["domanda_visibile", "risposta_corretta_visibile", "spiegazione"]:
                if isinstance(t.get(key), str):
                    out.append((f"test[{i}].{key}", t[key]))
            for j, opt in enumerate(t.get("opzioni_visibili", []) or [], 1):
                if isinstance(opt, str):
                    out.append((f"test[{i}].opzioni_visibili[{j}]", opt))
            for j, row in enumerate(t.get("mappa_opzioni_v35d", []) or [], 1):
                if isinstance(row, dict) and isinstance(row.get("opzione_visibile"), str):
                    out.append((f"test[{i}].mappa_opzioni_v35d[{j}].opzione_visibile", row["opzione_visibile"]))

    return out


def first_alpha(value: str) -> str:
    for ch in value.strip():
        if ch.isalpha():
            return ch
    return ""


def validate_output(path: Path) -> list[str]:
    errors: list[str] = []
    data = json.loads(path.read_text(encoding="utf-8"))

    for field, text in visible_texts(data):
        for label, pattern in VISIBLE_BAD_PATTERNS:
            if pattern.search(text):
                errors.append(f"{path.relative_to(ROOT)} :: {field} :: {label} :: {text}")

    for i, item in enumerate(data.get("test", []) or [], 1):
        if not isinstance(item, dict):
            continue
        options = item.get("opzioni_visibili", []) or []
        correct = item.get("risposta_corretta_visibile", "")
        if len(options) != 4:
            errors.append(f"{path.relative_to(ROOT)} :: test[{i}] :: opzioni visibili diverse da 4")
        if len(set(options)) != len(options):
            errors.append(f"{path.relative_to(ROOT)} :: test[{i}] :: opzioni duplicate")
        if correct not in options:
            errors.append(f"{path.relative_to(ROOT)} :: test[{i}] :: risposta corretta visibile non presente tra le opzioni")
        for opt in options:
            if isinstance(opt, str):
                ch = first_alpha(opt)
                if ch and ch.islower():
                    errors.append(f"{path.relative_to(ROOT)} :: test[{i}] :: opzione con iniziale minuscola :: {opt}")
    return errors


def validate_page() -> list[str]:
    errors: list[str] = []
    if not PAGE.exists():
        return ["pagina V3.5H mancante"]
    text = PAGE.read_text(encoding="utf-8", errors="ignore")

    if "rag_output_cleaner_finale_v35k" not in text:
        errors.append("pagina non collegata a rag_output_cleaner_finale_v35k")
    if "rag_output_accordo_pronomi_v35j" in text:
        errors.append("pagina ancora collegata a rag_output_accordo_pronomi_v35j")
    if "output_cleaner_finale_v35k.json();" in text:
        errors.append("pagina contiene path JSON corrotto con json();")
    if "V3.5J" in text:
        errors.append("pagina contiene ancora label V3.5J")
    return errors


def run_page_verifier() -> tuple[int, str]:
    verifier = ROOT / "scripts/verifica_rag_demo_selezionatore_output_v35h.py"
    if not verifier.exists():
        return 1, "verifier pagina mancante"
    result = subprocess.run(["python3", str(verifier)], cwd=ROOT, text=True, capture_output=True)
    return result.returncode, result.stdout + result.stderr


def main() -> int:
    results: list[str] = []
    errors: list[str] = []

    results.extend(clean_page())

    if not BASE.exists():
        errors.append(f"cartella output V3.5K mancante: {BASE.relative_to(ROOT)}")
    else:
        files = sorted(BASE.rglob("output_cleaner_finale_v35k.json"))
        if not files:
            errors.append("nessun output_cleaner_finale_v35k.json trovato")
        for path in files:
            local_errors = validate_output(path)
            if local_errors:
                errors.extend(local_errors)
            else:
                results.append(f"OK: visibile pulito {path.relative_to(ROOT)}")

    errors.extend(validate_page())

    code, verifier_log = run_page_verifier()
    if code == 0:
        results.append("OK: verifier pagina V3.5H")
    else:
        errors.append("verifier pagina V3.5H non OK")
        errors.append(verifier_log)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Report RAG Cleaner Finale Universale V3.5K",
        "",
        "Gate universale finale: controlla solo campi visibili e ignora metadati tecnici.",
        "",
        "## Risultati",
    ]
    lines.extend(f"- {r}" for r in results)
    lines.append("")
    lines.append(f"Errori totali: {len(errors)}")
    lines.append("")
    if errors:
        lines.append("## Errori")
        lines.extend(f"- {e}" for e in errors)
        lines.append("")
        lines.append("ESITO: DA CORREGGERE")
    else:
        lines.append("ESITO: OK")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("=== FIX GATE UNIVERSALE PAGINA V3.5K ===")
    for r in results:
        print(r)
    print("Errori totali:", len(errors))
    print("Report:", REPORT.relative_to(ROOT))
    print("ESITO:", "OK" if not errors else "DA CORREGGERE")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
