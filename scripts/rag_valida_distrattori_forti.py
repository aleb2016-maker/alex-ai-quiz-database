from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


STOPWORDS = {
    "a", "ad", "al", "allo", "alla", "ai", "agli", "alle", "anche",
    "che", "chi", "ci", "come", "con", "cosa", "da", "dal", "dalla",
    "dei", "del", "della", "delle", "di", "e", "è", "ed", "gli",
    "ha", "hai", "ho", "il", "in", "la", "le", "lo", "ma", "mi",
    "ne", "nel", "nella", "nelle", "non", "o", "per", "più",
    "quale", "quando", "se", "si", "sono", "su", "tra", "un",
    "una", "uno", "dati", "sistema", "sistemi", "azienda",
    "aziendale", "aziendali", "utente", "utenti", "modo",
}

FRASI_DEBOLI = [
    "tutte le precedenti",
    "nessuna delle precedenti",
    "non so",
    "completamente diverso",
]

PAROLE_GENERICHE_FUORI_TEMA = {
    "velocizzare",
    "velocità",
    "prestazioni",
    "memoria",
    "comprimere",
    "compressione",
    "innovazione",
    "ultima",
    "generazione",
    "facilitare",
    "semplificare",
}

PAROLE_TECNICHE = {
    "backup", "ransomware", "phishing", "password", "credenziali",
    "account", "malware", "virus", "rete", "wi", "wifi", "fi",
    "autenticazione", "fattori", "2fa", "codici", "sms", "app",
    "dati", "sensibili", "accesso", "permessi", "cloud",
    "aggiornamenti", "vulnerabilità", "sicurezza", "intercettazioni",
    "ripristino", "copia", "copie", "attacco", "attacchi",
}


def tokenizza(testo: str) -> set[str]:
    parole = re.findall(r"[a-zA-ZÀ-ÿ0-9]+", testo.lower())
    return {
        parola
        for parola in parole
        if len(parola) > 2 and parola not in STOPWORDS
    }


def similarita_jaccard(testo_a: str, testo_b: str) -> float:
    parole_a = tokenizza(testo_a)
    parole_b = tokenizza(testo_b)

    if not parole_a or not parole_b:
        return 0.0

    return len(parole_a & parole_b) / len(parole_a | parole_b)


def carica_domande(percorso: Path) -> list[dict]:
    dati = json.loads(percorso.read_text(encoding="utf-8"))

    if isinstance(dati, list):
        return [d for d in dati if isinstance(d, dict)]

    if isinstance(dati, dict):
        if isinstance(dati.get("domande"), list):
            return [d for d in dati["domande"] if isinstance(d, dict)]

        if isinstance(dati.get("domande_da_revisionare"), list):
            return [d for d in dati["domande_da_revisionare"] if isinstance(d, dict)]

    raise SystemExit("Formato JSON non supportato.")


def descrivi_opzione(indice: int) -> str:
    return ["A", "B", "C", "D"][indice] if 0 <= indice < 4 else str(indice + 1)


def parole_tema(domanda: str, risposta: str, spiegazione: str) -> set[str]:
    base = tokenizza(domanda) | tokenizza(risposta) | tokenizza(spiegazione)
    tecniche = base & PAROLE_TECNICHE

    if tecniche:
        return tecniche | {p for p in base if len(p) > 6}

    return {p for p in base if len(p) > 5}


def valuta_domanda_distrattori_forti(domanda: dict, posizione: int) -> list[dict]:
    avvisi: list[dict] = []

    testo_domanda = str(domanda.get("domanda", "")).strip()
    risposta_corretta = str(domanda.get("risposta_corretta", "")).strip()
    spiegazione = str(domanda.get("spiegazione", "")).strip()
    opzioni = domanda.get("opzioni", [])

    if not isinstance(opzioni, list) or len(opzioni) != 4 or not risposta_corretta:
        return avvisi

    opzioni_pulite = [str(opzione).strip() for opzione in opzioni]

    if risposta_corretta not in opzioni_pulite:
        return avvisi

    tema = parole_tema(testo_domanda, risposta_corretta, spiegazione)

    distrattori = [
        (indice, opzione)
        for indice, opzione in enumerate(opzioni_pulite)
        if opzione != risposta_corretta
    ]

    distrattori_deboli = 0

    for indice, distrattore in distrattori:
        lettera = descrivi_opzione(indice)
        distrattore_lower = distrattore.lower()
        parole_distrattore = tokenizza(distrattore)

        sim_risposta = similarita_jaccard(risposta_corretta, distrattore)
        sim_domanda = similarita_jaccard(testo_domanda, distrattore)
        sim_spiegazione = similarita_jaccard(spiegazione, distrattore)
        aggancio_tema = len(parole_distrattore & tema)

        vicino = (
            sim_risposta >= 0.08
            or sim_domanda >= 0.08
            or sim_spiegazione >= 0.06
            or aggancio_tema >= 2
        )

        if not vicino:
            distrattori_deboli += 1
            avvisi.append(
                {
                    "posizione": posizione,
                    "tipo": "distrattore_poco_vicino",
                    "opzione": lettera,
                    "similarita": round(max(sim_risposta, sim_domanda, sim_spiegazione), 4),
                    "messaggio": (
                        f"opzione {lettera}: distrattore troppo lontano dal nucleo della domanda."
                    ),
                }
            )

        if any(frase in distrattore_lower for frase in FRASI_DEBOLI):
            avvisi.append(
                {
                    "posizione": posizione,
                    "tipo": "frase_debole",
                    "opzione": lettera,
                    "similarita": round(sim_risposta, 4),
                    "messaggio": f"opzione {lettera}: contiene una formula debole.",
                }
            )

        parole_generiche = parole_distrattore & PAROLE_GENERICHE_FUORI_TEMA

        if parole_generiche and aggancio_tema == 0:
            avvisi.append(
                {
                    "posizione": posizione,
                    "tipo": "fuori_tema_probabile",
                    "opzione": lettera,
                    "similarita": round(sim_risposta, 4),
                    "messaggio": (
                        f"opzione {lettera}: sembra generica o fuori tema "
                        f"({', '.join(sorted(parole_generiche))})."
                    ),
                }
            )

    if distrattori_deboli >= 2:
        avvisi.append(
            {
                "posizione": posizione,
                "tipo": "domanda_facile_per_eliminazione",
                "opzione": "-",
                "similarita": 0,
                "messaggio": (
                    "almeno due distrattori sembrano troppo lontani: "
                    "la risposta corretta potrebbe essere individuabile per eliminazione."
                ),
            }
        )

    lunghezze = [len(opzione) for opzione in opzioni_pulite if opzione]

    if lunghezze:
        minima = min(lunghezze)
        massima = max(lunghezze)

        if minima > 0 and massima / minima > 3.2:
            avvisi.append(
                {
                    "posizione": posizione,
                    "tipo": "lunghezze_sbilanciate",
                    "opzione": "-",
                    "similarita": 0,
                    "messaggio": "le opzioni hanno lunghezze troppo diverse.",
                }
            )

    return avvisi


def crea_report(percorso: Path, domande: list[dict], avvisi: list[dict]) -> str:
    righe = [
        "# Validazione distrattori forti RAG",
        "",
        f"- File controllato: `{percorso}`",
        f"- Domande controllate: {len(domande)}",
        f"- Avvisi trovati: {len(avvisi)}",
        "",
    ]

    if avvisi:
        righe.append("## Avvisi")
        righe.append("")
        for avviso in avvisi:
            righe.append(f"- Domanda {avviso['posizione']}: {avviso['messaggio']}")
        righe.append("")
    else:
        righe.append("## Risultato")
        righe.append("")
        righe.append("Nessun distrattore debole rilevato dai controlli automatici.")
        righe.append("")

    righe.append("## Nota")
    righe.append("")
    righe.append(
        "Il controllo usa agganci tecnici tra domanda, risposta, spiegazione e distrattori. "
        "Non si basa solo su parole identiche nella risposta corretta."
    )
    righe.append("")

    return "\n".join(righe)


def main() -> None:
    parser = argparse.ArgumentParser(description="Valida la forza dei distrattori RAG.")
    parser.add_argument("file", nargs="?", default="dist/generated/rag_quiz_generato.json")
    parser.add_argument("--report", default="reports/rag_validazione_distrattori_forti.md")
    parser.add_argument("--fail-on-weak", action="store_true")

    args = parser.parse_args()

    percorso = Path(args.file)
    domande = carica_domande(percorso)

    avvisi: list[dict] = []

    for posizione, domanda in enumerate(domande, start=1):
        avvisi.extend(valuta_domanda_distrattori_forti(domanda, posizione))

    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(
        crea_report(percorso, domande, avvisi),
        encoding="utf-8",
    )

    print("✅ Validazione distrattori forti RAG completata")
    print(f"📌 Domande controllate: {len(domande)}")
    print(f"📌 Avvisi trovati: {len(avvisi)}")
    print(f"📌 Report: {args.report}")

    if avvisi and args.fail_on_weak:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
