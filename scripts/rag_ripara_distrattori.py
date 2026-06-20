from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from rag_valida_distrattori_forti import valuta_domanda_distrattori_forti


def carica_quiz(percorso: Path) -> dict:
    if not percorso.exists():
        raise SystemExit(f"File non trovato: {percorso}")

    dati = json.loads(percorso.read_text(encoding="utf-8"))

    if isinstance(dati, list):
        return {
            "metadati": {
                "origine": "rag",
                "nota": "Lista normalizzata dal riparatore distrattori.",
            },
            "domande": dati,
        }

    if not isinstance(dati, dict):
        raise SystemExit("Il quiz deve essere un oggetto JSON o una lista.")

    if "domande" not in dati:
        raise SystemExit("Il quiz deve contenere la chiave `domande`.")

    if not isinstance(dati["domande"], list):
        raise SystemExit("La chiave `domande` deve contenere una lista.")

    return dati


def conta_avvisi(dati_quiz: dict) -> list[dict]:
    avvisi: list[dict] = []

    for posizione, domanda in enumerate(dati_quiz.get("domande", []), start=1):
        if isinstance(domanda, dict):
            avvisi.extend(
                valuta_domanda_distrattori_forti(
                    domanda=domanda,
                    posizione=posizione,
                )
            )

    return avvisi


def crea_testo_avvisi(avvisi: list[dict]) -> str:
    if not avvisi:
        return "Nessun avviso."

    righe = []

    for avviso in avvisi:
        righe.append(
            f"- Domanda {avviso.get('posizione')}: {avviso.get('messaggio')}"
        )

    return "\n".join(righe)


def valida_struttura_minima(dati_quiz: dict) -> list[str]:
    problemi: list[str] = []

    if not isinstance(dati_quiz, dict):
        return ["Il risultato non è un oggetto JSON."]

    domande = dati_quiz.get("domande")

    if not isinstance(domande, list):
        return ["Manca la lista `domande`."]

    if not domande:
        return ["La lista `domande` è vuota."]

    for posizione, domanda in enumerate(domande, start=1):
        if not isinstance(domanda, dict):
            problemi.append(f"Domanda {posizione}: non è un oggetto.")
            continue

        for campo in [
            "id",
            "categoria",
            "livello",
            "domanda",
            "opzioni",
            "risposta_corretta",
            "spiegazione",
        ]:
            if campo not in domanda:
                problemi.append(f"Domanda {posizione}: campo mancante `{campo}`.")

        opzioni = domanda.get("opzioni", [])
        risposta = str(domanda.get("risposta_corretta", "")).strip()

        if not isinstance(opzioni, list) or len(opzioni) != 4:
            problemi.append(f"Domanda {posizione}: deve avere 4 opzioni.")
            continue

        opzioni_pulite = [
            str(opzione).strip()
            for opzione in opzioni
        ]

        if risposta not in opzioni_pulite:
            problemi.append(
                f"Domanda {posizione}: risposta corretta non presente tra le opzioni."
            )

        if len(set(opzioni_pulite)) != 4:
            problemi.append(f"Domanda {posizione}: opzioni duplicate.")

    return problemi


def chiama_ollama(prompt: str, modello: str, timeout_secondi: int = 300) -> str:
    payload = {
        "model": modello,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.25,
            "top_p": 0.85,
        },
    }

    richiesta = urllib.request.Request(
        url="http://localhost:11434/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(richiesta, timeout=timeout_secondi) as risposta:
            dati = json.loads(risposta.read().decode("utf-8"))
    except urllib.error.URLError as errore:
        raise RuntimeError("Ollama non risponde.") from errore

    testo = str(dati.get("response", "")).strip()

    if not testo:
        raise RuntimeError("Ollama ha risposto senza contenuto.")

    return testo


def estrai_json(testo: str) -> dict:
    testo = testo.strip()

    try:
        dati = json.loads(testo)
    except json.JSONDecodeError:
        inizio = testo.find("{")
        fine = testo.rfind("}")

        if inizio == -1 or fine == -1 or fine <= inizio:
            raise ValueError("Non è stato trovato un JSON valido.")

        dati = json.loads(testo[inizio:fine + 1])

    if isinstance(dati, list):
        return {
            "metadati": {
                "origine": "rag",
                "nota": "Lista normalizzata dal riparatore.",
            },
            "domande": dati,
        }

    if not isinstance(dati, dict):
        raise ValueError("Il risultato deve essere un oggetto JSON.")

    if "domande" not in dati:
        raise ValueError("Il risultato non contiene la chiave `domande`.")

    return dati


def crea_prompt_riparazione(
    dati_quiz: dict,
    avvisi: list[dict],
    ciclo: int,
) -> str:
    quiz_json = json.dumps(dati_quiz, ensure_ascii=False, indent=2)
    testo_avvisi = crea_testo_avvisi(avvisi)

    return f"""
Sei un motore di riparazione per quiz generati da RAG.

Devi correggere SOLO i distrattori deboli del quiz JSON.

CICLO DI RIPARAZIONE: {ciclo}

PROBLEMI RILEVATI DAL VALIDATORE:
{testo_avvisi}

REGOLE OBBLIGATORIE:
- restituisci solo JSON valido
- mantieni la struttura con `metadati` e `domande`
- mantieni lo stesso numero di domande
- non cancellare domande
- non aggiungere domande
- non cambiare categoria
- non cambiare livello
- non cambiare fonte_rag
- non cambiare il testo della risposta corretta
- la risposta corretta deve restare tra le 4 opzioni
- puoi riscrivere i 3 distrattori
- puoi migliorare la spiegazione se serve
- ogni domanda deve avere 1 risposta corretta e 3 distrattori forti

COME DEVONO ESSERE I DISTRAttORI FORTI:
- vicini alla risposta corretta
- stesso argomento tecnico
- stessa area concettuale
- plausibili
- sbagliati per un dettaglio preciso
- non assurdi
- non generici
- non fuori tema
- non troppo brevi rispetto alla risposta corretta
- non facilmente eliminabili

ESEMPIO:

Risposta corretta:
Il backup serve a recuperare dati dopo perdita, guasto o ransomware.

Distrattore debole:
Per velocizzare il computer.

Distrattore forte:
Il backup serve a recuperare dati dopo un ransomware, ma solo se rimane sempre collegato alla rete principale.

Il secondo è forte perché parla ancora di backup e ransomware, ma contiene un dettaglio sbagliato.

QUIZ DA RIPARARE:

{quiz_json}
""".strip()


def salva_report(
    percorso: Path,
    file_input: Path,
    file_output: Path,
    avvisi_iniziali: int,
    avvisi_finali: int,
    cicli_usati: int,
    migliorato: bool,
) -> None:
    percorso.parent.mkdir(parents=True, exist_ok=True)

    stato = "MIGLIORATO" if migliorato else "NESSUN MIGLIORAMENTO AUTOMATICO"

    testo = f"""# Riparazione automatica distrattori RAG

- File input: `{file_input}`
- File output: `{file_output}`
- Cicli usati: {cicli_usati}
- Avvisi iniziali: {avvisi_iniziali}
- Avvisi finali: {avvisi_finali}
- Stato: {stato}

## Nota

Il riparatore non importa nulla nei database ufficiali.
Corregge solo il JSON temporaneo generato dal RAG.

Dopo la riparazione restano comunque necessari:

- validazione struttura JSON
- validazione distrattori forti
- review sicura
- eventuale approvazione manuale
"""

    percorso.write_text(testo, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ripara automaticamente i distrattori deboli generati dal RAG."
    )

    parser.add_argument(
        "input",
        nargs="?",
        default="dist/generated/rag_quiz_generato.json",
    )
    parser.add_argument(
        "--output",
        default="dist/generated/rag_quiz_generato.json",
    )
    parser.add_argument(
        "--modello",
        default="gemma3:4b",
    )
    parser.add_argument(
        "--cicli",
        type=int,
        default=2,
    )
    parser.add_argument(
        "--report",
        default="reports/rag_riparazione_distrattori.md",
    )
    parser.add_argument(
        "--prompt-output",
        default="reports/rag_prompt_riparazione_distrattori.md",
    )

    args = parser.parse_args()

    if args.cicli <= 0:
        raise SystemExit("Il numero di cicli deve essere maggiore di zero.")

    file_input = Path(args.input)
    file_output = Path(args.output)

    dati_originali = carica_quiz(file_input)
    avvisi_originali = conta_avvisi(dati_originali)

    print("🛠️ Riparatore distrattori RAG")
    print(f"📌 Avvisi iniziali: {len(avvisi_originali)}")

    if not avvisi_originali:
        file_output.parent.mkdir(parents=True, exist_ok=True)
        file_output.write_text(
            json.dumps(dati_originali, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        salva_report(
            percorso=Path(args.report),
            file_input=file_input,
            file_output=file_output,
            avvisi_iniziali=0,
            avvisi_finali=0,
            cicli_usati=0,
            migliorato=False,
        )

        print("✅ Nessun distrattore da riparare")
        return

    migliore_quiz = dati_originali
    migliori_avvisi = avvisi_originali
    cicli_usati = 0

    for ciclo in range(1, args.cicli + 1):
        cicli_usati = ciclo

        print()
        print(f"🔧 Ciclo riparazione {ciclo}/{args.cicli}")

        prompt = crea_prompt_riparazione(
            dati_quiz=migliore_quiz,
            avvisi=migliori_avvisi,
            ciclo=ciclo,
        )

        Path(args.prompt_output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.prompt_output).write_text(prompt, encoding="utf-8")

        try:
            risposta = chiama_ollama(
                prompt=prompt,
                modello=args.modello,
            )

            quiz_riparato = estrai_json(risposta)
        except Exception as errore:
            print(f"⚠️ Riparazione non valida: {errore}")
            continue

        problemi_struttura = valida_struttura_minima(quiz_riparato)

        if problemi_struttura:
            print("⚠️ La riparazione ha prodotto una struttura non valida.")
            for problema in problemi_struttura:
                print(f"- {problema}")
            continue

        nuovi_avvisi = conta_avvisi(quiz_riparato)

        print(f"📌 Avvisi dopo ciclo {ciclo}: {len(nuovi_avvisi)}")

        if len(nuovi_avvisi) < len(migliori_avvisi):
            migliore_quiz = quiz_riparato
            migliori_avvisi = nuovi_avvisi
            print("✅ Miglioramento accettato")
        else:
            print("ℹ️ Nessun miglioramento rispetto alla versione migliore")

        if not migliori_avvisi:
            break

    file_output.parent.mkdir(parents=True, exist_ok=True)
    file_output.write_text(
        json.dumps(migliore_quiz, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    migliorato = len(migliori_avvisi) < len(avvisi_originali)

    salva_report(
        percorso=Path(args.report),
        file_input=file_input,
        file_output=file_output,
        avvisi_iniziali=len(avvisi_originali),
        avvisi_finali=len(migliori_avvisi),
        cicli_usati=cicli_usati,
        migliorato=migliorato,
    )

    print()
    print("✅ Riparazione distrattori completata")
    print(f"📌 Avvisi iniziali: {len(avvisi_originali)}")
    print(f"📌 Avvisi finali: {len(migliori_avvisi)}")
    print(f"📌 Report: {args.report}")


if __name__ == "__main__":
    main()
