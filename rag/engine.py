from __future__ import annotations

from .indexer import crea_indice_rag
from .retriever import cerca_chunk_rilevanti


class RagEngine:
    """
    Motore RAG riutilizzabile del progetto.

    Può essere usato per:
    - quiz
    - test
    - mini-corsi
    - slide
    - percorsi formativi
    - demo aziendali
    """

    def __init__(
        self,
        cartella_documenti: str = "rag/documenti",
        file_indice: str = "rag/indice_rag.json",
    ) -> None:
        self.cartella_documenti = cartella_documenti
        self.file_indice = file_indice

    def crea_indice(self) -> dict:
        return crea_indice_rag(
            cartella_documenti=self.cartella_documenti,
            file_indice=self.file_indice,
        )

    def cerca(self, domanda: str, massimo_risultati: int = 5) -> list[dict]:
        return cerca_chunk_rilevanti(
            domanda=domanda,
            file_indice=self.file_indice,
            massimo_risultati=massimo_risultati,
        )

    def crea_contesto(self, domanda: str, massimo_risultati: int = 5) -> str:
        risultati = self.cerca(
            domanda=domanda,
            massimo_risultati=massimo_risultati,
        )

        if not risultati:
            return (
                "CONTESTO RAG:\n"
                "Nessun contenuto rilevante trovato nei documenti indicizzati.\n"
            )

        blocchi_contesto = ["CONTESTO RAG RECUPERATO DAI DOCUMENTI:\n"]

        for posizione, risultato in enumerate(risultati, start=1):
            blocchi_contesto.append(
                f"[Fonte {posizione}]\n"
                f"Documento: {risultato['documento']}\n"
                f"Chunk: {risultato['numero_chunk']}\n"
                f"Punteggio: {risultato['punteggio']}\n"
                f"Testo:\n{risultato['testo']}\n"
            )

        return "\n".join(blocchi_contesto)

    def crea_prompt_per_quiz(
        self,
        argomento: str,
        numero_domande: int = 10,
        livello: str = "intermedio",
    ) -> str:
        domanda_rag = (
            f"Materiale utile per creare {numero_domande} domande "
            f"di livello {livello} sull'argomento: {argomento}"
        )

        contesto = self.crea_contesto(domanda_rag, massimo_risultati=6)

        return f"""
Sei un generatore professionale di quiz formativi.

Devi creare domande basate SOLO sul contesto RAG fornito.

REGOLE QUALITÀ:
- crea {numero_domande} domande
- livello: {livello}
- argomento: {argomento}
- ogni domanda deve avere 4 risposte
- 1 risposta corretta
- 3 distrattori forti, plausibili e vicini alla risposta corretta
- nessuna risposta assurda o eliminabile facilmente
- spiegazione chiara e didattica
- linguaggio pulito e corretto
- non inventare informazioni non presenti nel contesto

{contesto}
""".strip()

    def crea_prompt_per_minicorso(
        self,
        argomento: str,
        numero_slide: int = 5,
        livello: str = "base",
    ) -> str:
        domanda_rag = (
            f"Materiale utile per creare un mini-corso di {numero_slide} slide "
            f"di livello {livello} sull'argomento: {argomento}"
        )

        contesto = self.crea_contesto(domanda_rag, massimo_risultati=6)

        return f"""
Sei un progettista di mini-corsi interattivi.

Devi creare un mini-corso basato SOLO sul contesto RAG fornito.

REGOLE:
- argomento: {argomento}
- livello: {livello}
- numero slide/card: {numero_slide}
- ogni slide deve avere titolo, spiegazione breve, esempio pratico
- stile chiaro, progressivo e formativo
- adatto a essere trasformato in demo web, quiz o app Android
- non inventare informazioni non presenti nel contesto

{contesto}
""".strip()
