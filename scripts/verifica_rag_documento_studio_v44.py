#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def ok(msg: str) -> None:
    print("OK -", msg)

def err(msg: str, errors: list[str]) -> None:
    print("ERRORE -", msg)
    errors.append(msg)

def contains(path: Path, text: str) -> bool:
    return path.exists() and text in path.read_text(encoding="utf-8", errors="replace")

def main() -> None:
    errors = []
    print("=== Verifica RAG Documento Studio V4.4 ===")

    files = [
        ROOT / "scripts/rag_adapter_documento_studio_v44.py",
        ROOT / "scripts/verifica_rag_documento_studio_v44.py",
        ROOT / "demo-rag/test-rag-documento-studio-v44.html",
        ROOT / "demo-rag/rag-documento-studio-v44.css",
        ROOT / "demo-rag/rag-documento-studio-v44.js",
        ROOT / "docs/RAG_DOCUMENTO_STUDIO_V44.md",
    ]
    for f in files:
        if f.exists():
            ok(f"presente {f.relative_to(ROOT)}")
        else:
            err(f"manca {f.relative_to(ROOT)}", errors)

    js = ROOT / "demo-rag/rag-documento-studio-v44.js"
    html = ROOT / "demo-rag/test-rag-documento-studio-v44.html"

    if contains(js, "window.print"):
        err("JS non deve usare window.print", errors)
    else:
        ok("nessun window.print")

    if contains(js, "AlexBrowserPdfExportV6.exportSectionsToPdf"):
        ok("PDF collegato a PDF browser V6")
    else:
        err("PDF V6 non collegato", errors)

    if contains(js, "RagCardGraphicEngine.renderGraphicCard") and contains(js, "RagCardGraphicEngine.buildCardObject"):
        ok("Card collegate al motore card esistente")
    else:
        err("motore card grafico non collegato", errors)

    if contains(html, "/runtime/web/card-graphic-engine.js"):
        ok("HTML carica runtime/web/card-graphic-engine.js")
    else:
        err("HTML non carica card engine runtime", errors)

    if contains(html, "/demo-rag/pdf-export-browser-v6.js"):
        ok("HTML carica pdf-export-browser-v6.js")
    else:
        err("HTML non carica PDF V6", errors)

    output = ROOT / "dist/generated/rag_documento_studio_v44.json"
    if output.exists():
        data = json.loads(output.read_text(encoding="utf-8"))
        for key in ["chunks", "riassunto", "cards", "qa_index", "qualita"]:
            if key in data:
                ok(f"output JSON contiene {key}")
            else:
                err(f"output JSON manca {key}", errors)
        blob = json.dumps(data, ensure_ascii=False)
        for bad in ["þ", "ÿ", "\\\\n"]:
            if bad in blob:
                err(f"output contiene simbolo/testo vietato: {bad}", errors)
        if len(data.get("cards", [])) < 4:
            err("output ha meno di 4 card", errors)
        if len(data.get("riassunto", {}).get("punti_chiave", [])) < 3:
            err("riassunto troppo povero", errors)
    else:
        print("AVVISO - output dist/generated/rag_documento_studio_v44.json non ancora generato")

    # Riusa validatori card già presenti, se disponibili.
    for validator in ["scripts/validatore_card_grafiche_completo.py", "scripts/validatore_concetti_card.py"]:
        p = ROOT / validator
        if p.exists():
            result = subprocess.run([sys.executable, str(p)], cwd=ROOT)
            if result.returncode == 0:
                ok(f"validatore esistente passato: {validator}")
            else:
                err(f"validatore esistente fallito: {validator}", errors)

    if errors:
        raise SystemExit(1)
    print("Verifica completata.")

if __name__ == "__main__":
    main()
