#!/usr/bin/env python3
from pathlib import Path
import zipfile
import json
from datetime import datetime

ROOT = Path.cwd()
ZIP = ROOT / "downloads/pacchetto-rag-riutilizzabile.zip"
PREFIX = "pacchetto-rag-riutilizzabile"

INCLUDI = [
    "rag",
    "config/temi_grafici_formazione.json",
    "config/output_rag_formazione.json",
    "demo-rag",
    "docs/RAG_RIUTILIZZABILE.md",
    "docs/RAG_INSERIMENTO_DOCUMENTI.md",
    "docs/RAG_PIPELINE_COMPLETA.md",
    "docs/PIPELINE_MATERIALE_FORMATIVO.md",
    "docs/MOTORE_GRAFICO_RIUTILIZZABILE.md",
    "docs/RAG_PACCHETTO_RIUTILIZZABILE.md",
    "docs/RAG_DOCUMENTI_AZIENDALI.md",
    "scripts/rag_build_index.py",
    "scripts/rag_test_query.py",
    "scripts/rag_crea_prompt_quiz.py",
    "scripts/rag_crea_prompt_minicorso.py",
    "scripts/rag_documenti_aziendali.py",
    "scripts/rag_pipeline_completa_sicura.py",
    "scripts/pipeline_formazione_completa.py",
    "scripts/applica_tema_formazione.py",
    "scripts/validatore_rag_distrattori_forti_v2.py",
    "scripts/validate_questions.py",
    "scripts/build_database.py",
    "scripts/check_duplicates.py",
    "scripts/qualita_linguistica.py",
    "scripts/motore_qualita_generale.py",
    "scripts/controllo_qualita_completo.py",
    "dist/formazione",
]

def salta(p):
    return any(x in p.parts for x in [".git", ".venv", "__pycache__", "node_modules", ".DS_Store"])

def aggiungi(zf, p):
    if not p.exists():
        return 0
    if p.is_file() and not salta(p):
        zf.write(p, f"{PREFIX}/{p.relative_to(ROOT)}")
        return 1
    totale = 0
    if p.is_dir():
        for f in p.rglob("*"):
            if f.is_file() and not salta(f):
                zf.write(f, f"{PREFIX}/{f.relative_to(ROOT)}")
                totale += 1
    return totale

def main():
    ZIP.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "nome": "Pacchetto RAG riutilizzabile",
        "generato_il": datetime.now().isoformat(timespec="seconds"),
        "funzioni": ["lettura documenti", "correzione testo", "quiz", "riassunti", "report", "Q&A", "statistiche", "grafici", "card", "slide", "mini-corsi", "temi grafici", "controlli qualità"]
    }
    readme = """# Pacchetto RAG riutilizzabile

Questo ZIP contiene il motore RAG scaricabile e riutilizzabile.

Comando esempio:

    python3 scripts/rag_documenti_aziendali.py rag/documenti/esempio_documento_aziendale_formazione.md --titolo "Formazione aziendale" --output all

Per PDF/DOCX possono servire:

    pip install pypdf python-docx
"""
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        totale = 0
        zf.writestr(f"{PREFIX}/README_RAG.md", readme)
        zf.writestr(f"{PREFIX}/manifest_pacchetto_rag.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        totale += 2
        for rel in INCLUDI:
            totale += aggiungi(zf, ROOT / rel)
    print(f"✅ Creato: {ZIP}")
    print(f"📦 File inclusi: {totale}")

if __name__ == "__main__":
    main()
