from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path


STOPWORDS_ITALIANE = {
    "a", "ad", "al", "allo", "alla", "ai", "agli", "alle",
    "che", "chi", "ci", "coi", "col", "come", "con", "cosa",
    "da", "dai", "dal", "dalla", "dei", "del", "della", "di",
    "e", "è", "ed", "gli", "ha", "hai", "ho", "il", "in",
    "io", "la", "le", "lo", "ma", "mi", "ne", "nel", "nella",
    "non", "o", "per", "più", "quale", "quando", "se", "si",
    "sono", "su", "tra", "un", "una", "uno",
}


def estrai_parole_chiave(testo: str) -> list[str]:
    parole = re.findall(r"[a-zA-ZÀ-ÿ0-9]+", testo.lower())

    return [
        parola
        for parola in parole
        if len(parola) > 2 and parola not in STOPWORDS_ITALIANE
    ]


def similarita_coseno(parole_domanda: list[str], parole_chunk: list[str]) -> float:
    """
    Calcola una somiglianza semplice tra domanda e chunk.

    Questa prima versione non usa embedding pesanti.
    È leggera, locale e senza API a pagamento.
    """

    if not parole_domanda or not parole_chunk:
        return 0.0

    vettore_domanda = Counter(parole_domanda)
    vettore_chunk = Counter(parole_chunk)

    parole_comuni = set(vettore_domanda) & set(vettore_chunk)

    prodotto_scalare = sum(
        vettore_domanda[parola] * vettore_chunk[parola]
        for parola in parole_comuni
    )

    norma_domanda = math.sqrt(sum(valore * valore for valore in vettore_domanda.values()))
    norma_chunk = math.sqrt(sum(valore * valore for valore in vettore_chunk.values()))

    if norma_domanda == 0 or norma_chunk == 0:
        return 0.0

    return prodotto_scalare / (norma_domanda * norma_chunk)


def cerca_chunk_rilevanti(
    domanda: str,
    file_indice: str = "rag/indice_rag.json",
    massimo_risultati: int = 5,
) -> list[dict]:
    """
    Recupera i chunk più vicini alla domanda.

    Questo è il cuore del RAG:
    cerca nei documenti e restituisce solo il contesto utile.
    """

    percorso_indice = Path(file_indice)

    if not percorso_indice.exists():
        raise FileNotFoundError(
            "Indice RAG non trovato. Esegui prima: python3 scripts/rag_build_index.py"
        )

    indice = json.loads(percorso_indice.read_text(encoding="utf-8"))

    parole_domanda = estrai_parole_chiave(domanda)

    risultati = []

    for chunk in indice.get("chunk", []):
        testo_chunk = chunk.get("testo", "")
        parole_chunk = estrai_parole_chiave(testo_chunk)

        punteggio = similarita_coseno(parole_domanda, parole_chunk)

        if punteggio > 0:
            risultati.append(
                {
                    "documento": chunk.get("documento", ""),
                    "numero_chunk": chunk.get("numero_chunk", 0),
                    "punteggio": round(punteggio, 4),
                    "testo": testo_chunk,
                }
            )

    risultati.sort(key=lambda elemento: elemento["punteggio"], reverse=True)

    return risultati[:massimo_risultati]
