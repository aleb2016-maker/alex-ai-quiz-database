from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Chunk:
    documento: str
    numero_chunk: int
    testo: str


def dividi_testo_in_chunk(
    nome_documento: str,
    testo_originale: str,
    dimensione_chunk: int = 900,
    sovrapposizione: int = 150,
) -> list[Chunk]:
    """
    Divide un testo lungo in pezzi più piccoli.

    Il RAG non lavora bene passando tutto il documento insieme.
    Prima divide il materiale in blocchi, poi recupera solo quelli utili.
    """

    testo_pulito = " ".join(testo_originale.split())

    if not testo_pulito:
        return []

    if dimensione_chunk <= 0:
        raise ValueError("dimensione_chunk deve essere maggiore di 0")

    if sovrapposizione < 0:
        raise ValueError("sovrapposizione non può essere negativa")

    if sovrapposizione >= dimensione_chunk:
        raise ValueError("sovrapposizione deve essere minore della dimensione del chunk")

    chunks: list[Chunk] = []
    posizione_iniziale = 0
    numero_chunk = 1

    while posizione_iniziale < len(testo_pulito):
        posizione_finale = posizione_iniziale + dimensione_chunk
        testo_chunk = testo_pulito[posizione_iniziale:posizione_finale].strip()

        if testo_chunk:
            chunks.append(
                Chunk(
                    documento=nome_documento,
                    numero_chunk=numero_chunk,
                    testo=testo_chunk,
                )
            )

        numero_chunk += 1
        posizione_iniziale += dimensione_chunk - sovrapposizione

    return chunks
