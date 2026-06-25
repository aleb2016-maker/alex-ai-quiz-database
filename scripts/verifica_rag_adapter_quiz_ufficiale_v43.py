#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def fail(msg: str) -> None:
    print(f"ERRORE - {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"OK - {msg}")


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    adapter = root / "scripts" / "rag_adapter_quiz_ufficiale_v43.py"
    output = root / "dist" / "generated" / "rag_quiz_bridge_v43.json"
    report = root / "reports" / "rag_adapter_quiz_ufficiale_v43.md"

    print("=== Verifica RAG Adapter Quiz Ufficiale V4.3 ===")

    if not adapter.exists():
        fail("adapter mancante")
    ok("adapter presente")

    text = adapter.read_text(encoding="utf-8")
    forbidden = ["window.print", "jsPDF(", "new jsPDF", "html2canvas"]
    for bad in forbidden:
        if bad in text:
            fail(f"adapter contiene codice UI/PDF vietato: {bad}")
    ok("adapter non contiene motore PDF/UI inventato")

    required_refs = [
        "qualita_linguistica",
        "rag_valida_quiz_json.py",
        "rag_valida_distrattori_forti.py",
        "regola_distrattori",
        "criterio_distrattori",
        "tre_distrattori_forti",
    ]
    for ref in required_refs:
        if ref not in text:
            fail(f"manca riferimento a motore/regola esistente: {ref}")
    ok("adapter richiama regole e validatori esistenti")

    if output.exists():
        data = json.loads(output.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            fail("output ufficiale non è una lista di domande")
        if not data:
            fail("output ufficiale vuoto")
        required_keys = {
            "id", "categoria", "sottocategoria", "livello", "domanda",
            "opzioni", "risposta_corretta", "spiegazione", "tags",
            "difficolta", "regola_distrattori", "criterio_distrattori"
        }
        for index, item in enumerate(data, 1):
            missing = sorted(required_keys - set(item))
            if missing:
                fail(f"domanda {index}: mancano campi {missing}")
            if len(item.get("opzioni", [])) != 4:
                fail(f"domanda {index}: opzioni diverse da 4")
            if item.get("risposta_corretta") not in item.get("opzioni", []):
                fail(f"domanda {index}: risposta corretta non presente nelle opzioni")
            joined = json.dumps(item, ensure_ascii=False)
            if "þÿ" in joined or "\\\\n" in joined:
                fail(f"domanda {index}: simboli corrotti o newline visibili")
        ok("output ufficiale valido")
    else:
        print("INFO - output non ancora generato: esegui prima rag_adapter_quiz_ufficiale_v43.py")

    if report.exists():
        ok("report generato")
    else:
        print("INFO - report non ancora generato")

    print("Verifica completata.")


if __name__ == "__main__":
    main()
