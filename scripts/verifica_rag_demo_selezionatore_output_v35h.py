#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "demo-rag/test-selezionatore-output-v35h.html"
REPORT = ROOT / "reports/rag_demo_selezionatore_output_v35h.md"
OUTPUTS = [
    ROOT / "dist/generated/rag_output_cleaner_finale_v35k/solo_riassunto/sicurezza_reale/output_cleaner_finale_v35k.json",
    ROOT / "dist/generated/rag_output_cleaner_finale_v35k/solo_card/sicurezza_reale/output_cleaner_finale_v35k.json",
    ROOT / "dist/generated/rag_output_cleaner_finale_v35k/solo_domande_studio/sicurezza_reale/output_cleaner_finale_v35k.json",
    ROOT / "dist/generated/rag_output_cleaner_finale_v35k/solo_test/sicurezza_reale/output_cleaner_finale_v35k.json",
    ROOT / "dist/generated/rag_output_cleaner_finale_v35k/output_completo/sicurezza_reale/output_cleaner_finale_v35k.json",
]
BAD_PATTERNS = [
    r"\?\s*\?+",
    r"[,;:]\s*[.!?]",
    r"\b(?:di|a|da|in|su)\s+(?:il|lo|la|i|gli|le)\b",
    r"\b(?:copiarlo|copiarla|copiarli|copiarle)\b",
    r"\b(?:lo|la|li|le)\s+collega\b",
    r"«[^»]+»\s+viene\s+presentat[oaie]\s+come",
    r"\b(?:gli|i|le)\s+[A-Za-zÀ-ÖØ-öø-ÿ0-9'\-]+(?:\s+[A-Za-zÀ-ÖØ-öø-ÿ0-9'\-]+){0,5}\s+è\b",
]


def main() -> int:
    risultati = []
    errori = []

    if not PAGE.exists():
        errori.append("pagina V3.5H mancante")
    else:
        page_text = PAGE.read_text(encoding="utf-8", errors="ignore")
        if "rag_output_cleaner_finale_v35k" not in page_text:
            errori.append("pagina non collegata a rag_output_cleaner_finale_v35k")
        if "rag_output_accordo_pronomi_v35j" in page_text:
            errori.append("pagina ancora collegata a rag_output_accordo_pronomi_v35j")
        if "V3.5J" in page_text:
            errori.append("pagina contiene ancora label V3.5J")
        for marker in ["Solo riassunto", "Solo card", "Domande studio", "Test interattivo", "Completo", "renderQuality", "renderQuiz", "activateQuiz"]:
            if marker not in page_text:
                errori.append(f"marker pagina mancante: {marker}")
        if not errori:
            risultati.append("OK: pagina V3.5H carica solo V3.5K")

    for output in OUTPUTS:
        if not output.exists():
            errori.append(f"output V3.5K mancante: {output.relative_to(ROOT)}")
            continue
        data = json.loads(output.read_text(encoding="utf-8"))
        control = data.get("controlli_qualita", {}).get("cleaner_finale_universale_v35k", {})
        if not control.get("ok"):
            errori.append(f"cleaner finale V3.5K non OK in {output.relative_to(ROOT)}: {control.get('errori')}")
        text = output.read_text(encoding="utf-8", errors="ignore")
        for pattern in BAD_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                errori.append(f"pattern sporco in {output.relative_to(ROOT)}: {pattern}")
        if control.get("ok"):
            risultati.append(f"OK: output V3.5K {output.relative_to(ROOT)}")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Report Demo Selezionatore Output RAG V3.5H", "", "Verifica pagina su output finali V3.5K universali.", "", "## Risultati"]
    lines += [f"- {r}" for r in risultati]
    lines += ["", f"Errori totali: {len(errori)}", ""]
    if errori:
        lines.append("## Errori")
        lines += [f"- {e}" for e in errori]
        lines += ["", "ESITO: DA CORREGGERE"]
    else:
        lines.append("ESITO: OK")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("=== VERIFICA DEMO SELEZIONATORE OUTPUT V3.5H ===")
    for r in risultati:
        print(r)
    print("Errori totali:", len(errori))
    print("Report:", REPORT.relative_to(ROOT))
    print("ESITO:", "OK" if not errori else "DA CORREGGERE")
    return 0 if not errori else 1


if __name__ == "__main__":
    raise SystemExit(main())
