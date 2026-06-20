from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


STOPWORDS = {
    "a", "ad", "al", "allo", "alla", "ai", "agli", "alle",
    "che", "chi", "ci", "come", "con", "cosa", "da", "dal",
    "dalla", "dei", "del", "della", "di", "e", "è", "ed",
    "gli", "ha", "hai", "ho", "il", "in", "la", "le", "lo",
    "ma", "mi", "ne", "nel", "nella", "non", "o", "per",
    "più", "quale", "quando", "se", "si", "sono", "su",
    "tra", "un", "una", "uno", "dati", "sistema", "sistemi",
    "aziendale", "aziendali",
}

FRASI_DEBOLI = [
    "tutte le precedenti",
    "nessuna delle precedenti",
    "non so",
    "non riguarda",
    "completamente diverso",
]

PAROLE_GENERICHE_FUORI_TEMA = {
    "velocizzare",
    "velocità",
    "prestazioni",
    "memoria",
    "comprimere",
    "compressione",
    "condivisione",
    "condividere",
    "innovazione",
    "ultima",
    "generazione",
    "facilitare",
    "semplificare",
}


def tokenizza(testo: str) -> set[str]:
    parole = re.findall(r"[a-zA-ZÀ-ÿ0-9]+", testo.lower())
    return {
        parola
        for parola in parole
        if len(parola) > 3 and parola not in STOPWORDS
    }


def similarita_jaccard(testo_a: str, testo_b: str) -> float:
    parole_a = tokenizza(testo_a)
    parole_b = tokenizza(testo_b)

    if not parole_a or not parole_b:
        return 0.0

    parole_comuni = parole_a & parole_b
    parole_totali = parole_a | parole_b

    return len(parole_comuni) / len(parole_totali)


def carica_domande(percorso: Path) -> list[dict]:
    if not percorso.exists():
        raise SystemExit(f"File non trovato: {percorso}")

    dati = json.loads(percorso.read_text(encoding="utf-8"))

    if isinstance(dati, list):
        return [
            domanda
            for domanda in dati
            if isinstance(domanda, dict)
        ]

    if isinstance(dati, dict):
        if isinstance(dati.get("domande"), list):
            return [
                domanda
                for domanda in dati["domande"]
                if isinstance(domanda, dict)
            ]

        if isinstance(dati.get("domande_da_revisionare"), list):
            return [
                domanda
                for domanda in dati["domande_da_revisionare"]
                if isinstance(domanda, dict)
            ]

    raise SystemExit("Formato JSON non supportato per la validazione distrattori.")


def descrivi_opzione(indice: int) -> str:
    lettere = ["A", "B", "C", "D"]
    if 0 <= indice < len(lettere):
        return lettere[indice]
    return str(indice + 1)


def valuta_domanda_distrattori_forti(domanda: dict, posizione: int) -> list[dict]:
    avvisi: list[dict] = []

    testo_domanda = str(domanda.get("domanda", "")).strip()
    risposta_corretta = str(domanda.get("risposta_corretta", "")).strip()
    opzioni = domanda.get("opzioni", [])

    if not isinstance(opzioni, list) or len(opzioni) != 4 or not risposta_corretta:
        return avvisi

    opzioni_pulite = [
        str(opzione).strip()
        for opzione in opzioni
    ]

    if risposta_corretta not in opzioni_pulite:
        return avvisi

    distrattori = [
        (indice, opzione)
        for indice, opzione in enumerate(opzioni_pulite)
        if opzione != risposta_corretta
    ]

    similarita_distrattori = []

    for indice, distrattore in distrattori:
        similarita = similarita_jaccard(risposta_corretta, distrattore)
        similarita_distrattori.append(similarita)

        lettera = descrivi_opzione(indice)
        distrattore_lower = distrattore.lower()

        if similarita < 0.10:
            avvisi.append(
                {
                    "posizione": posizione,
                    "tipo": "distrattore_poco_vicino",
                    "opzione": lettera,
                    "similarita": round(similarita, 4),
                    "messaggio": (
                        f"opzione {lettera}: distrattore troppo lontano dalla risposta corretta "
                        f"(similarità {similarita:.2f})."
                    ),
                }
            )

        if any(frase in distrattore_lower for frase in FRASI_DEBOLI):
            avvisi.append(
                {
                    "posizione": posizione,
                    "tipo": "frase_debole",
                    "opzione": lettera,
                    "similarita": round(similarita, 4),
                    "messaggio": (
                        f"opzione {lettera}: contiene una formula debole o non professionale."
                    ),
                }
            )

        parole_distrattore = tokenizza(distrattore)
        parole_generiche = parole_distrattore & PAROLE_GENERICHE_FUORI_TEMA

        if parole_generiche and similarita < 0.18:
            avvisi.append(
                {
                    "posizione": posizione,
                    "tipo": "fuori_tema_probabile",
                    "opzione": lettera,
                    "similarita": round(similarita, 4),
                    "messaggio": (
                        f"opzione {lettera}: sembra generica o fuori tema "
                        f"({', '.join(sorted(parole_generiche))})."
                    ),
                }
            )

    if similarita_distrattori:
        distrattori_troppo_lontani = [
            valore
            for valore in similarita_distrattori
            if valore < 0.10
        ]

        if len(distrattori_troppo_lontani) >= 2:
            avvisi.append(
                {
                    "posizione": posizione,
                    "tipo": "domanda_facile_per_eliminazione",
                    "opzione": "-",
                    "similarita": round(max(similarita_distrattori), 4),
                    "messaggio": (
                        "almeno due distrattori sembrano troppo lontani: "
                        "la risposta corretta potrebbe essere individuabile per eliminazione."
                    ),
                }
            )

    lunghezze = [
        len(opzione)
        for opzione in opzioni_pulite
        if opzione
    ]

    if lunghezze:
        lunghezza_minima = min(lunghezze)
        lunghezza_massima = max(lunghezze)

        if lunghezza_minima > 0 and lunghezza_massima / lunghezza_minima > 2.8:
            avvisi.append(
                {
                    "posizione": posizione,
                    "tipo": "lunghezze_sbilanciate",
                    "opzione": "-",
                    "similarita": 0,
                    "messaggio": (
                        "le opzioni hanno lunghezze molto diverse: "
                        "la risposta corretta potrebbe risaltare."
                    ),
                }
            )

    parole_domanda = tokenizza(testo_domanda)

    if parole_domanda:
        for indice, distrattore in distrattori:
            similarita_domanda = len(parole_domanda & tokenizza(distrattore)) / max(
                1,
                len(parole_domanda | tokenizza(distrattore)),
            )

            if similarita_domanda < 0.04:
                lettera = descrivi_opzione(indice)
                avvisi.append(
                    {
                        "posizione": posizione,
                        "tipo": "distrattore_poco_collegato_domanda",
                        "opzione": lettera,
                        "similarita": round(similarita_domanda, 4),
                        "messaggio": (
                            f"opzione {lettera}: distrattore poco collegato al testo della domanda."
                        ),
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
            righe.append(
                f"- Domanda {avviso['posizione']}: {avviso['messaggio']}"
            )

        righe.append("")
    else:
        righe.append("## Risultato")
        righe.append("")
        righe.append("Nessun distrattore debole rilevato dai controlli automatici.")
        righe.append("")

    righe.append("## Nota")
    righe.append("")
    righe.append(
        "Questo controllo non approva automaticamente le domande. "
        "Serve a rendere la review più severa prima di qualsiasi import nei database ufficiali."
    )
    righe.append("")

    return "\n".join(righe)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Valida la forza dei distrattori generati dal RAG."
    )

    parser.add_argument(
        "file",
        nargs="?",
        default="dist/generated/rag_quiz_generato.json",
    )
    parser.add_argument(
        "--report",
        default="reports/rag_validazione_distrattori_forti.md",
    )
    parser.add_argument(
        "--fail-on-weak",
        action="store_true",
        help="Termina con errore se trova distrattori deboli.",
    )

    args = parser.parse_args()

    percorso = Path(args.file)
    domande = carica_domande(percorso)

    avvisi: list[dict] = []

    for posizione, domanda in enumerate(domande, start=1):
        avvisi.extend(
            valuta_domanda_distrattori_forti(
                domanda=domanda,
                posizione=posizione,
            )
        )

    percorso_report = Path(args.report)
    percorso_report.parent.mkdir(parents=True, exist_ok=True)
    percorso_report.write_text(
        crea_report(
            percorso=percorso,
            domande=domande,
            avvisi=avvisi,
        ),
        encoding="utf-8",
    )

    print("✅ Validazione distrattori forti RAG completata")
    print(f"📌 Domande controllate: {len(domande)}")
    print(f"📌 Avvisi trovati: {len(avvisi)}")
    print(f"📌 Report: {percorso_report}")

    if avvisi and args.fail_on_weak:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
