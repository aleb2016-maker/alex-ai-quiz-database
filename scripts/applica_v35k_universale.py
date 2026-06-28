#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/rag_cleaner_finale_universale_v35k.md"
PAGE = ROOT / "demo-rag/test-selezionatore-output-v35h.html"
OUT_BASE = ROOT / "dist/generated/rag_output_cleaner_finale_v35k"

CASES = [
    ("solo_riassunto", "sicurezza_reale"),
    ("solo_card", "sicurezza_reale"),
    ("solo_domande_studio", "sicurezza_reale"),
    ("solo_test", "sicurezza_reale"),
    ("output_completo", "sicurezza_reale"),
]

INPUT_CANDIDATES = [
    ("rag_output_accordo_pronomi_v35j", "output_accordo_pronomi_v35j.json"),
    ("rag_output_naturalezza_antikeyword_v35i", "output_naturalezza_antikeyword_v35i.json"),
    ("rag_output_revisionato_qualita_v35g", "output_revisionato_qualita_v35g.json"),
]


def load_cleaner_module():
    path = ROOT / "scripts/rag_cleaner_finale_universale_v35k.py"
    spec = importlib.util.spec_from_file_location("rag_cleaner_finale_universale_v35k", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Impossibile caricare il cleaner universale V3.5K")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_input(case_name: str, doc_name: str) -> Path | None:
    for base, filename in INPUT_CANDIDATES:
        path = ROOT / f"dist/generated/{base}/{case_name}/{doc_name}/{filename}"
        if path.exists():
            return path
    return None


def patch_page() -> list[str]:
    results = []
    if not PAGE.exists():
        return ["ERRORE: pagina V3.5H mancante"]

    text = PAGE.read_text(encoding="utf-8")
    original = text

    # Path finali: la pagina deve caricare solo V3.5K.
    text = re.sub(
        r"../dist/generated/rag_output_[^/]+/([^/]+/sicurezza_reale)/output_[^/]+\.json",
        r"../dist/generated/rag_output_cleaner_finale_v35k/\1/output_cleaner_finale_v35k.json",
        text,
    )

    # Label UI: non deve restare ferma a V3.5J.
    text = text.replace("V3.5J · accordo grammaticale e pronomi", "V3.5K · cleaner finale universale")
    text = text.replace("Controllo V3.5J · accordo grammaticale e pronomi", "Controllo V3.5K · cleaner finale universale")
    text = text.replace("Testi V3.5J", "Testi V3.5K")
    text = text.replace("V3.5J: ${escapeHtml(e)}", "V3.5K: ${escapeHtml(e)}")
    text = text.replace("accordo_pronomi_v35j", "cleaner_finale_universale_v35k")
    text = text.replace("revisione_accordo_pronomi_v35j", "revisione_cleaner_finale_universale_v35k")
    text = text.replace("accordo/pronomi V3.5J", "cleaner finale V3.5K")
    text = text.replace("output accordo/pronomi", "output cleaner finale")

    PAGE.write_text(text, encoding="utf-8")

    if text != original:
        results.append("OK: pagina V3.5H patchata su V3.5K universale")
    else:
        results.append("OK: pagina V3.5H già su V3.5K universale")

    page_text = PAGE.read_text(encoding="utf-8", errors="ignore")
    if "rag_output_accordo_pronomi_v35j" in page_text:
        results.append("ERRORE: pagina contiene ancora rag_output_accordo_pronomi_v35j")
    if "rag_output_cleaner_finale_v35k" not in page_text:
        results.append("ERRORE: pagina non contiene rag_output_cleaner_finale_v35k")
    if "V3.5J" in page_text:
        results.append("ERRORE: pagina contiene ancora label V3.5J")

    return results


def write_page_verifier() -> None:
    verifier = ROOT / "scripts/verifica_rag_demo_selezionatore_output_v35h.py"
    verifier.write_text('''#!/usr/bin/env python3
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
    r"\\?\\s*\\?+",
    r"[,;:]\\s*[.!?]",
    r"\\b(?:di|a|da|in|su)\\s+(?:il|lo|la|i|gli|le)\\b",
    r"\\b(?:copiarlo|copiarla|copiarli|copiarle)\\b",
    r"\\b(?:lo|la|li|le)\\s+collega\\b",
    r"«[^»]+»\\s+viene\\s+presentat[oaie]\\s+come",
    r"\\b(?:gli|i|le)\\s+[A-Za-zÀ-ÖØ-öø-ÿ0-9'\\-]+(?:\\s+[A-Za-zÀ-ÖØ-öø-ÿ0-9'\\-]+){0,5}\\s+è\\b",
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
    REPORT.write_text("\\n".join(lines) + "\\n", encoding="utf-8")

    print("=== VERIFICA DEMO SELEZIONATORE OUTPUT V3.5H ===")
    for r in risultati:
        print(r)
    print("Errori totali:", len(errori))
    print("Report:", REPORT.relative_to(ROOT))
    print("ESITO:", "OK" if not errori else "DA CORREGGERE")
    return 0 if not errori else 1


if __name__ == "__main__":
    raise SystemExit(main())
''', encoding="utf-8")
    verifier.chmod(0o755)


def main() -> int:
    cleaner = load_cleaner_module()
    risultati: list[str] = []
    errori: list[str] = []

    for case_name, doc_name in CASES:
        src = find_input(case_name, doc_name)
        dst = OUT_BASE / case_name / doc_name / "output_cleaner_finale_v35k.json"
        if src is None:
            errori.append(f"{case_name}/{doc_name}: nessun input trovato")
            continue
        data = json.loads(src.read_text(encoding="utf-8"))
        cleaned, _coverage = cleaner.clean_output(data)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")
        control = cleaned.get("controlli_qualita", {}).get(cleaner.CONTROL_KEY, {})
        if control.get("ok"):
            risultati.append(f"OK: {case_name}/{doc_name} -> {dst.relative_to(ROOT)}")
        else:
            errori.append(f"{case_name}/{doc_name}: cleaner non OK -> {control.get('errori')}")

    risultati.extend(patch_page())
    write_page_verifier()

    # Verifica pagina dopo patch.
    verifier_result = subprocess.run(["python3", "scripts/verifica_rag_demo_selezionatore_output_v35h.py"], cwd=ROOT, text=True, capture_output=True)
    risultati.append(verifier_result.stdout.strip())
    if verifier_result.returncode != 0:
        errori.append("verifica pagina V3.5H non OK")
        errori.append(verifier_result.stderr.strip())

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Report RAG Cleaner Finale Universale V3.5K", "", "## Risultati"]
    for r in risultati:
        lines.append(f"- {r}")
    lines += ["", f"Errori totali: {len(errori)}", ""]
    if errori:
        lines.append("## Errori")
        for e in errori:
            lines.append(f"- {e}")
        lines += ["", "ESITO: DA CORREGGERE"]
    else:
        lines.append("ESITO: OK")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("=== APPLICA V3.5K UNIVERSALE ===")
    for r in risultati:
        print(r)
    print("Errori totali:", len(errori))
    print("Report:", REPORT.relative_to(ROOT))
    print("ESITO:", "OK" if not errori else "DA CORREGGERE")
    return 0 if not errori else 1


if __name__ == "__main__":
    raise SystemExit(main())
