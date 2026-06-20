from __future__ import annotations

import json
from pathlib import Path

from .chunker import dividi_testo_in_chunk


ESTENSIONI_SUPPORTATE = {".txt", ".md", ".json"}


def leggi_documento(percorso_file: Path) -> str:
    """
    Legge documenti testuali.

    Versione iniziale:
    - TXT
    - Markdown
    - JSON

    In seguito potremo aggiungere PDF, DOCX e slide.
    """

    estensione = percorso_file.suffix.lower()

    if estensione not in ESTENSIONI_SUPPORTATE:
        return ""

    try:
        contenuto = percorso_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        contenuto = percorso_file.read_text(encoding="latin-1")

    if estensione == ".json":
        try:
            dati = json.loads(contenuto)
            return json.dumps(dati, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            return contenuto

    return contenuto


def crea_indice_rag(
    cartella_documenti: str = "rag/documenti",
    file_indice: str = "rag/indice_rag.json",
) -> dict:
    """
    Crea l'indice RAG locale.

    1. Legge i documenti.
    2. Divide i testi in chunk.
    3. Salva l'indice in rag/indice_rag.json.
    """

    percorso_cartella = Path(cartella_documenti)
    percorso_indice = Path(file_indice)

    percorso_cartella.mkdir(parents=True, exist_ok=True)
    percorso_indice.parent.mkdir(parents=True, exist_ok=True)

    tutti_i_chunk = []
    documenti_letti = 0

    for percorso_file in sorted(percorso_cartella.rglob("*")):
        if not percorso_file.is_file():
            continue

        if percorso_file.suffix.lower() not in ESTENSIONI_SUPPORTATE:
            continue

        testo_documento = leggi_documento(percorso_file)

        if not testo_documento.strip():
            continue

        documenti_letti += 1

        chunks = dividi_testo_in_chunk(
            nome_documento=str(percorso_file),
            testo_originale=testo_documento,
        )

        for chunk in chunks:
            tutti_i_chunk.append(
                {
                    "documento": chunk.documento,
                    "numero_chunk": chunk.numero_chunk,
                    "testo": chunk.testo,
                }
            )

    indice = {
        "versione": "1.0",
        "tipo": "rag_locale_riutilizzabile",
        "documenti_letti": documenti_letti,
        "numero_chunk": len(tutti_i_chunk),
        "chunk": tutti_i_chunk,
    }

    percorso_indice.write_text(
        json.dumps(indice, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return indice
