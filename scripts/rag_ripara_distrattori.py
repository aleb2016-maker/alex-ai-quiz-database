from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from rag_valida_distrattori_forti import valuta_domanda_distrattori_forti


def carica_quiz(percorso: Path) -> dict:
    dati = json.loads(percorso.read_text(encoding="utf-8"))

    if isinstance(dati, list):
        return {"metadati": {"origine": "rag"}, "domande": dati}

    if not isinstance(dati, dict):
        raise SystemExit("Il quiz deve essere un oggetto JSON.")

    if not isinstance(dati.get("domande"), list):
        raise SystemExit("Il quiz deve contenere una lista `domande`.")

    return dati


def testo_completo(domanda: dict) -> str:
    pezzi = [
        str(domanda.get("domanda", "")),
        str(domanda.get("risposta_corretta", "")),
        str(domanda.get("spiegazione", "")),
    ]
    return " ".join(pezzi).lower()


def crea_distrattori_per_tema(domanda: dict) -> list[str]:
    testo = testo_completo(domanda)
    risposta = str(domanda.get("risposta_corretta", "")).strip()

    if "backup" in testo or "ransomware" in testo or "ripristin" in testo:
        return [
            "Per recuperare i dati dopo un incidente, ma lasciando l’unica copia sempre collegata alla rete principale.",
            "Per evitare direttamente che ransomware o guasti possano verificarsi, invece di preparare il ripristino.",
            "Per conservare una copia dei dati, ma senza verificare mai se il ripristino funziona davvero.",
        ]

    if "phishing" in testo or "credenzial" in testo or "messaggi" in testo:
        return [
            "Serve a proteggere le credenziali chiedendo all’utente di confermarle su un sito esterno.",
            "Si riconosce sempre solo dagli errori grammaticali evidenti, senza controllare mittente e link.",
            "Riguarda solo allegati infetti e non può usare link, urgenza o pagine simili a quelle reali.",
        ]

    if "2fa" in testo or "due fattori" in testo or "autenticazione" in testo:
        return [
            "Aggiunge un secondo controllo, ma rende inutile cambiare una password già compromessa.",
            "Richiede due passaggi di accesso, ma funziona solo tramite SMS perché sono sempre più sicuri delle app.",
            "Sostituisce completamente la password e quindi elimina la necessità di gestire credenziali robuste.",
        ]

    if "wi-fi" in testo or "wifi" in testo or "rete pubblica" in testo or "intercett" in testo:
        return [
            "Espone i dati solo quando la rete pubblica è lenta, perché la lentezza indica sempre un attacco.",
            "Protegge il traffico aziendale se il nome della rete assomiglia a quello di un bar o di un hotel.",
            "È sicura per attività aziendali se consente accesso rapido ai servizi cloud senza controlli aggiuntivi.",
        ]

    if "password" in testo:
        return [
            "È sicura se viene riutilizzata su pochi servizi, purché sia abbastanza lunga e facile da ricordare.",
            "Protegge meglio gli account quando contiene dati personali noti solo al dipendente.",
            "Riduce il rischio se viene condivisa solo con colleghi fidati dello stesso reparto.",
        ]

    if "aggiornament" in testo or "vulnerabilità" in testo:
        return [
            "Gli aggiornamenti servono solo ad aggiungere funzioni e non incidono sulle vulnerabilità già note.",
            "Rimandare gli aggiornamenti è sicuro se il sistema continua a funzionare senza errori visibili.",
            "Una vulnerabilità pubblicata diventa meno rischiosa perché gli attaccanti non possono più sfruttarla.",
        ]

    if "malware" in testo or "virus" in testo:
        return [
            "Il malware è pericoloso solo se rallenta subito il computer in modo evidente.",
            "Un allegato inatteso è sicuro se proviene da un contatto già conosciuto dall’azienda.",
            "Un antivirus elimina ogni rischio e rende inutili controlli su link, allegati e permessi.",
        ]

    if "permessi" in testo or "accesso" in testo:
        return [
            "Ogni dipendente dovrebbe avere accesso a tutti i dati, così può intervenire più rapidamente.",
            "I permessi sono sicuri quando restano invariati anche se cambia il ruolo della persona.",
            "Limitare gli accessi serve solo a semplificare il lavoro degli amministratori, non a ridurre rischi.",
        ]

    parole_risposta = risposta.rstrip(".")
    return [
        f"{parole_risposta}, ma solo se viene applicato senza controlli successivi.",
        f"{parole_risposta}, ma garantendo sempre protezione totale in ogni situazione.",
        f"{parole_risposta}, ma senza verificare se la misura funziona nel caso reale.",
    ]


def ripara_domanda(domanda: dict) -> dict:
    nuova = dict(domanda)

    risposta = str(nuova.get("risposta_corretta", "")).strip()
    if not risposta:
        return nuova

    distrattori = crea_distrattori_per_tema(nuova)

    opzioni = [risposta] + distrattori[:3]

    nuova["opzioni"] = opzioni
    nuova["risposta_corretta"] = risposta
    nuova["regola_distrattori"] = "tre_distrattori_forti_riparati"

    spiegazione = str(nuova.get("spiegazione", "")).strip()
    if len(spiegazione) < 80:
        nuova["spiegazione"] = (
            f"La risposta corretta è: {risposta} "
            "Le altre opzioni restano vicine al tema, ma introducono dettagli sbagliati, "
            "assoluti o non coerenti con una buona pratica di sicurezza."
        )

    return nuova


def conta_avvisi(dati: dict) -> list[dict]:
    avvisi: list[dict] = []

    for posizione, domanda in enumerate(dati.get("domande", []), start=1):
        if isinstance(domanda, dict):
            avvisi.extend(valuta_domanda_distrattori_forti(domanda, posizione))

    return avvisi


def main() -> None:
    parser = argparse.ArgumentParser(description="Ripara automaticamente i distrattori RAG.")
    parser.add_argument("input", nargs="?", default="dist/generated/rag_quiz_generato.json")
    parser.add_argument("--output", default="dist/generated/rag_quiz_generato.json")
    parser.add_argument("--modello", default="gemma3:4b")
    parser.add_argument("--cicli", type=int, default=2)
    parser.add_argument("--report", default="reports/rag_riparazione_distrattori.md")
    parser.add_argument("--prompt-output", default="reports/rag_prompt_riparazione_distrattori.md")

    args = parser.parse_args()

    file_input = Path(args.input)
    file_output = Path(args.output)

    dati = carica_quiz(file_input)
    avvisi_iniziali = conta_avvisi(dati)

    print("🛠️ Riparatore distrattori RAG guidato")
    print(f"📌 Avvisi iniziali: {len(avvisi_iniziali)}")

    domande_riparate = []

    for domanda in dati.get("domande", []):
        if isinstance(domanda, dict):
            domande_riparate.append(ripara_domanda(domanda))

    dati_riparati = dict(dati)
    dati_riparati["domande"] = domande_riparate

    metadati = dict(dati_riparati.get("metadati", {}))
    metadati["riparazione_distrattori"] = "automatica_guidata"
    dati_riparati["metadati"] = metadati

    avvisi_finali = conta_avvisi(dati_riparati)

    file_output.parent.mkdir(parents=True, exist_ok=True)
    file_output.write_text(
        json.dumps(dati_riparati, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    Path(args.prompt_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.prompt_output).write_text(
        "Riparazione guidata deterministica: non è stato necessario usare prompt Ollama.",
        encoding="utf-8",
    )

    stato = "MIGLIORATO" if len(avvisi_finali) < len(avvisi_iniziali) else "DA_REVISIONARE"

    report = f"""# Riparazione automatica distrattori RAG

- File input: `{file_input}`
- File output: `{file_output}`
- Avvisi iniziali: {len(avvisi_iniziali)}
- Avvisi finali: {len(avvisi_finali)}
- Stato: {stato}

## Metodo

Il riparatore usa regole guidate per tema.
Non si limita a chiedere al modello di correggere: riscrive direttamente i distrattori usando schemi vicini alla risposta corretta.

## Sicurezza

Il riparatore lavora solo sul JSON temporaneo RAG.
Non modifica i database ufficiali dentro `data/`.
"""

    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(report, encoding="utf-8")

    print("✅ Riparazione distrattori completata")
    print(f"📌 Avvisi iniziali: {len(avvisi_iniziali)}")
    print(f"📌 Avvisi finali: {len(avvisi_finali)}")
    print(f"📌 Report: {args.report}")


if __name__ == "__main__":
    main()
