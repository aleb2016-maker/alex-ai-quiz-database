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
Sei un generatore professionale di quiz formativi basati su documenti RAG.

Devi creare un file JSON basato SOLO sul contesto RAG fornito.

OBIETTIVO:
Generare {numero_domande} domande per un quiz riutilizzabile.

DATI QUIZ:
- argomento: {argomento}
- categoria: {categoria}
- livello: {livello}

REGOLE OBBLIGATORIE SULLE FONTI:
- usa solo informazioni presenti nel contesto RAG
- non inventare contenuti esterni
- ogni domanda deve essere collegata al contesto recuperato
- la spiegazione deve essere coerente con il documento
- inserisci in fonte_rag il riferimento alla fonte usata, per esempio "[Fonte 1]"

REGOLE OBBLIGATORIE SULLE DOMANDE:
- crea esattamente {numero_domande} domande
- ogni domanda deve avere 4 opzioni
- 1 sola opzione deve essere corretta
- 3 opzioni devono essere distrattori forti
- non usare risposte palesemente assurde
- non usare opzioni completamente fuori tema
- non usare "tutte le precedenti" o "nessuna delle precedenti"
- non rendere la risposta corretta più lunga, più tecnica o più completa delle altre in modo evidente
- tutte le opzioni devono avere lunghezza, stile e livello tecnico simili

REGOLA FONDAMENTALE SUI 3 DISTRAttORI FORTI:
Ogni distrattore deve partire da un'idea plausibile e vicina alla risposta corretta,
ma deve diventare sbagliato per un dettaglio preciso.

NON creare distrattori come:
- affermazioni positive quando la domanda chiede un rischio
- frasi completamente scollegate dal tema
- opzioni che si eliminano subito
- opzioni ridicole o impossibili
- frasi troppo generiche

CREA invece distrattori di questo tipo:
- stesso concetto della risposta corretta, ma con una conseguenza sbagliata
- stessa premessa, ma con una limitazione errata
- stessa area tecnica, ma con un dettaglio invertito
- stessa funzione, ma applicata nel momento sbagliato
- stessa misura di sicurezza, ma con un effetto esagerato o falso

ESEMPIO DI QUALITÀ ATTESA:

Domanda:
Perché è rischioso usare la stessa password su più servizi?

Risposta corretta:
Perché se un servizio viene violato, la stessa password può essere provata anche su altri account.

Distrattore forte 1:
Perché usare la stessa password impedisce alla 2FA di generare codici temporanei.

Distrattore forte 2:
Perché una password riutilizzata viene automaticamente salvata in chiaro da tutti i siti.

Distrattore forte 3:
Perché il riutilizzo della password elimina sempre la possibilità di cambiarla in futuro.

Nota:
I tre distrattori sono vicini al tema password/account/sicurezza,
ma sono sbagliati per un dettaglio specifico.

ESEMPIO SU BACKUP:

Risposta corretta:
Il backup serve a recuperare dati dopo perdita, guasto o attacco ransomware.

Distrattore forte 1:
Il backup serve a impedire direttamente l'esecuzione di un ransomware prima dell'attacco.

Distrattore forte 2:
Il backup serve a recuperare i dati, ma solo se rimane sempre collegato alla stessa rete principale.

Distrattore forte 3:
Il backup serve a ripristinare i dati senza bisogno di verificare mai il recupero.

ESEMPIO SU PHISHING:

Risposta corretta:
Il phishing cerca di ingannare l'utente per ottenere credenziali, dati sensibili o pagamenti.

Distrattore forte 1:
Il phishing protegge le credenziali chiedendo all'utente di confermarle su un sito esterno.

Distrattore forte 2:
Il phishing si riconosce sempre solo dalla presenza di errori grammaticali evidenti.

Distrattore forte 3:
Il phishing riguarda solo allegati infetti e non può usare link o messaggi urgenti.

REGOLE SULLA SPIEGAZIONE:
- spiega perché la risposta corretta è corretta
- indica il dettaglio centrale della regola
- non limitarti a dire "le altre risposte sono sbagliate"
- non fare spiegazioni troppo brevi
- non inventare informazioni non presenti nel contesto

FORMATO JSON OBBLIGATORIO:
Restituisci solo JSON valido.
Non aggiungere markdown, commenti, testo prima o dopo.

{{
  "metadati": {{
    "origine": "rag",
    "argomento": "{argomento}",
    "categoria": "{categoria}",
    "livello": "{livello}",
    "numero_domande_richieste": {numero_domande},
    "regola_distrattori": "tre_distrattori_forti_vicini"
  }},
  "domande": [
    {{
      "id": "RAG-0001",
      "categoria": "{categoria}",
      "livello": "{livello}",
      "domanda": "Testo della domanda",
      "opzioni": [
        "Risposta corretta",
        "Distrattore forte vicino 1",
        "Distrattore forte vicino 2",
        "Distrattore forte vicino 3"
      ],
      "risposta_corretta": "Risposta corretta",
      "spiegazione": "Spiegazione chiara basata sul contesto RAG.",
      "fonte_rag": "[Fonte 1]",
      "regola_distrattori": "tre_distrattori_forti_vicini"
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
