from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag import RagEngine


def crea_prompt_quiz_json(
    argomento: str,
    categoria: str,
    livello: str,
    numero_domande: int,
) -> str:
    rag = RagEngine()

    domanda_rag = (
        f"Materiale utile per creare {numero_domande} domande quiz "
        f"sull'argomento {argomento}, categoria {categoria}, livello {livello}."
    )

    contesto = rag.crea_contesto(
        domanda=domanda_rag,
        massimo_risultati=6,
    )

    return f"""
Sei un generatore professionale di quiz formativi.

Devi creare un file JSON basato SOLO sul contesto RAG fornito.

OBIETTIVO:
Generare {numero_domande} domande per un quiz riutilizzabile.

DATI QUIZ:
- argomento: {argomento}
- categoria: {categoria}
- livello: {livello}

REGOLE OBBLIGATORIE:
- usa solo informazioni presenti nel contesto RAG
- non inventare contenuti esterni
- ogni domanda deve avere 4 opzioni
- 1 opzione corretta
- 3 distrattori forti, plausibili e vicini alla risposta corretta
- le opzioni devono essere simili per lunghezza, stile e livello tecnico
- nessuna opzione deve essere assurda o eliminabile subito
- la spiegazione deve essere chiara, didattica e collegata al contesto
- lingua italiana corretta
- niente markdown fuori dal JSON
- restituisci solo JSON valido

FORMATO JSON OBBLIGATORIO:

{{
  "metadati": {{
    "origine": "rag",
    "argomento": "{argomento}",
    "categoria": "{categoria}",
    "livello": "{livello}",
    "numero_domande_richieste": {numero_domande}
  }},
  "domande": [
    {{
      "id": "RAG-0001",
      "categoria": "{categoria}",
      "livello": "{livello}",
      "domanda": "Testo della domanda",
      "opzioni": [
        "Risposta corretta",
        "Distrattore forte 1",
        "Distrattore forte 2",
        "Distrattore forte 3"
      ],
      "risposta_corretta": "Risposta corretta",
      "spiegazione": "Spiegazione chiara basata sul contesto RAG.",
      "fonte_rag": "Documento o chunk usato come fonte",
      "regola_distrattori": "tre_distrattori_forti"
    }}
  ]
}}

CONTESTO RAG:

{contesto}
""".strip()


def salva_file_testo(percorso: Path, contenuto: str) -> None:
    percorso.parent.mkdir(parents=True, exist_ok=True)
    percorso.write_text(contenuto, encoding="utf-8")


def chiama_ollama(
    prompt: str,
    modello: str,
    timeout_secondi: int = 300,
) -> str:
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": modello,
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }

    richiesta = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(richiesta, timeout=timeout_secondi) as risposta:
            dati = json.loads(risposta.read().decode("utf-8"))
    except urllib.error.URLError as errore:
        raise RuntimeError(
            "Ollama non risponde. Avvia Ollama oppure usa lo script senza --usa-ollama."
        ) from errore

    testo_generato = dati.get("response", "").strip()

    if not testo_generato:
        raise RuntimeError("Ollama ha risposto, ma non ha generato contenuto.")

    return testo_generato


def estrai_json_da_testo(testo: str) -> dict:
    testo_pulito = testo.strip()

    try:
        dati = json.loads(testo_pulito)
    except json.JSONDecodeError:
        inizio = testo_pulito.find("{")
        fine = testo_pulito.rfind("}")

        if inizio == -1 or fine == -1 or fine <= inizio:
            raise ValueError("Non è stato trovato un JSON valido nella risposta.")

        dati = json.loads(testo_pulito[inizio:fine + 1])

    if isinstance(dati, list):
        return {
            "metadati": {
                "origine": "rag",
                "nota": "Il modello ha restituito una lista; normalizzata dal motore.",
            },
            "domande": dati,
        }

    if not isinstance(dati, dict):
        raise ValueError("Il JSON generato deve essere un oggetto o una lista.")

    if "domande" not in dati:
        dati = {
            "metadati": {
                "origine": "rag",
                "nota": "JSON normalizzato perché mancava la chiave domande.",
            },
            "domande": [dati],
        }

    return dati


def crea_file_vuoto_controllato(
    argomento: str,
    categoria: str,
    livello: str,
    numero_domande: int,
) -> dict:
    return {
        "metadati": {
            "origine": "rag",
            "stato": "solo_prompt_creato",
            "argomento": argomento,
            "categoria": categoria,
            "livello": livello,
            "numero_domande_richieste": numero_domande,
            "nota": (
                "Questo file è un contenitore temporaneo. "
                "Per generare domande reali usa --usa-ollama oppure collega un modello AI."
            ),
        },
        "domande": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera un quiz JSON temporaneo partendo dal contesto RAG."
    )

    parser.add_argument("argomento", help="Argomento del quiz da generare.")
    parser.add_argument("--categoria", default="rag_generato")
    parser.add_argument("--livello", default="intermedio")
    parser.add_argument("--numero-domande", type=int, default=10)
    parser.add_argument(
        "--output",
        default="dist/generated/rag_quiz_generato.json",
    )
    parser.add_argument(
        "--prompt-output",
        default="reports/rag_prompt_generazione_quiz_json.md",
    )
    parser.add_argument(
        "--usa-ollama",
        action="store_true",
        help="Usa Ollama locale per generare il JSON reale.",
    )
    parser.add_argument(
        "--modello",
        default=os.environ.get("OLLAMA_MODEL", "gemma3:4b"),
        help="Nome modello Ollama. Default: gemma3:4b oppure variabile OLLAMA_MODEL.",
    )

    args = parser.parse_args()

    if args.numero_domande <= 0:
        raise SystemExit("Il numero di domande deve essere maggiore di zero.")

    prompt = crea_prompt_quiz_json(
        argomento=args.argomento,
        categoria=args.categoria,
        livello=args.livello,
        numero_domande=args.numero_domande,
    )

    percorso_prompt = Path(args.prompt_output)
    percorso_output = Path(args.output)

    salva_file_testo(percorso_prompt, prompt)

    if args.usa_ollama:
        print(f"🤖 Generazione quiz con Ollama: {args.modello}")
        risposta = chiama_ollama(
            prompt=prompt,
            modello=args.modello,
        )
        dati_quiz = estrai_json_da_testo(risposta)
    else:
        print("📝 Modalità sicura: creo solo prompt e contenitore JSON temporaneo.")
        print("   Per generare domande reali usa: --usa-ollama")
        dati_quiz = crea_file_vuoto_controllato(
            argomento=args.argomento,
            categoria=args.categoria,
            livello=args.livello,
            numero_domande=args.numero_domande,
        )

    percorso_output.parent.mkdir(parents=True, exist_ok=True)
    percorso_output.write_text(
        json.dumps(dati_quiz, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("✅ Pipeline RAG → quiz JSON completata")
    print(f"📌 Prompt: {percorso_prompt}")
    print(f"📌 JSON temporaneo: {percorso_output}")


if __name__ == "__main__":
    main()
