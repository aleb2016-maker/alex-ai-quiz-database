from pathlib import Path
import json
import re
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "biologia.json"
OUTPUT_JSON = ROOT / "data" / "revisioni" / "biologia_domande_da_migliorare.json"
OUTPUT_MD = ROOT / "reports" / "biologia_distrattori_da_migliorare.md"

CAMPI_DOMANDA = ["domanda", "question", "testo", "text"]
CAMPI_OPZIONI = ["opzioni", "options", "risposte", "answers"]
CAMPI_RISPOSTA = [
    "risposta_corretta",
    "correct_answer",
    "correctAnswer",
    "answer",
    "correct",
]
CAMPI_LIVELLO = ["livello", "level", "difficolta", "difficulty"]


def normalizza_testo(testo):
    testo = str(testo or "").lower()
    testo = re.sub(r"\s+", " ", testo)
    testo = re.sub(r"[^\w\sàèéìòù]", "", testo)
    return testo.strip()


def prendi(dizionario, campi):
    for campo in campi:
        if campo in dizionario:
            return dizionario[campo]
    return None


def carica_domande(percorso):
    dati = json.loads(percorso.read_text(encoding="utf-8"))

    if isinstance(dati, list):
        return dati

    if isinstance(dati, dict):
        for chiave in ["domande", "questions", "quiz", "items", "data", "database"]:
            valore = dati.get(chiave)

            if isinstance(valore, list):
                return valore

    return []


def normalizza_opzioni(opzioni_grezze):
    if isinstance(opzioni_grezze, list):
        opzioni = []

        for opzione in opzioni_grezze:
            if isinstance(opzione, dict):
                testo = (
                    opzione.get("testo")
                    or opzione.get("text")
                    or opzione.get("risposta")
                    or opzione.get("answer")
                    or ""
                )
                opzioni.append(str(testo).strip())
            else:
                opzioni.append(str(opzione).strip())

        return [opzione for opzione in opzioni if opzione]

    if isinstance(opzioni_grezze, dict):
        opzioni = []

        for lettera in ["A", "B", "C", "D"]:
            if lettera in opzioni_grezze:
                opzioni.append(str(opzioni_grezze[lettera]).strip())

        return [opzione for opzione in opzioni if opzione]

    return []


def normalizza_risposta(risposta_grezza, opzioni):
    risposta = str(risposta_grezza or "").strip()

    if not risposta:
        return ""

    lettera = risposta.upper()

    if lettera in ["A", "B", "C", "D"]:
        indice = ord(lettera) - ord("A")
        return opzioni[indice] if indice < len(opzioni) else ""

    risposta_norm = normalizza_testo(risposta)

    for opzione in opzioni:
        if normalizza_testo(opzione) == risposta_norm:
            return opzione

    return risposta


def posizione_risposta(risposta, opzioni):
    if risposta in opzioni:
        return ["A", "B", "C", "D"][opzioni.index(risposta)]

    return "?"


def similarita_testuale(a, b):
    return SequenceMatcher(None, normalizza_testo(a), normalizza_testo(b)).ratio()


def parole_comuni(a, b):
    parole_a = set(normalizza_testo(a).split())
    parole_b = set(normalizza_testo(b).split())

    if not parole_a or not parole_b:
        return 0

    return len(parole_a.intersection(parole_b))


def valuta_problemi_qualita(opzioni, risposta):
    problemi = []

    if len(opzioni) != 4:
        problemi.append("La domanda non ha esattamente 4 opzioni.")
        return problemi

    parole_deboli = [
        "sempre",
        "mai",
        "tutte le precedenti",
        "nessuna delle precedenti",
        "non lo so",
    ]

    for opzione in opzioni:
        opzione_norm = normalizza_testo(opzione)

        for parola in parole_deboli:
            if parola in opzione_norm:
                problemi.append(
                    f"Possibile opzione debole/generica: contiene “{parola}”."
                )

    lunghezze = [len(opzione) for opzione in opzioni if opzione]

    if lunghezze and min(lunghezze) > 0:
        rapporto = max(lunghezze) / min(lunghezze)

        if rapporto >= 3:
            problemi.append(
                "Opzioni con lunghezze molto sbilanciate."
            )

    opzioni_errate = [
        opzione
        for opzione in opzioni
        if opzione != risposta
    ]

    if risposta and opzioni_errate:
        punteggi = []

        for opzione_errata in opzioni_errate:
            similarita = similarita_testuale(risposta, opzione_errata)
            comuni = parole_comuni(risposta, opzione_errata)
            punteggi.append((similarita, comuni, opzione_errata))

        migliore = max(punteggi, key=lambda elemento: (elemento[0], elemento[1]))
        similarita_migliore, parole_comuni_migliori, _ = migliore

        if similarita_migliore < 0.22 and parole_comuni_migliori < 2:
            problemi.append(
                "Manca un distrattore forte vicino alla risposta corretta."
            )

    return problemi


def main():
    if not INPUT_FILE.exists():
        raise SystemExit(f"ERRORE: file mancante: {INPUT_FILE}")

    domande = carica_domande(INPUT_FILE)
    domande_da_migliorare = []

    for domanda in domande:
        if not isinstance(domanda, dict):
            continue

        testo = str(prendi(domanda, CAMPI_DOMANDA) or "").strip()
        opzioni = normalizza_opzioni(prendi(domanda, CAMPI_OPZIONI))
        risposta = normalizza_risposta(prendi(domanda, CAMPI_RISPOSTA), opzioni)
        livello = str(prendi(domanda, CAMPI_LIVELLO) or "senza_livello").strip()
        posizione = posizione_risposta(risposta, opzioni)
        problemi = valuta_problemi_qualita(opzioni, risposta)

        if not problemi:
            continue

        domande_da_migliorare.append({
            "id": domanda.get("id", ""),
            "livello": livello,
            "domanda": testo,
            "opzioni_attuali": opzioni,
            "risposta_corretta": risposta,
            "posizione_risposta_corretta": posizione,
            "problemi": problemi,
            "regola_revisione": [
                "Mantenere la risposta corretta concettualmente identica.",
                "Creare almeno un distrattore forte molto vicino alla risposta corretta.",
                "Evitare parole assolute come sempre/mai quando rendono l'opzione eliminabile.",
                "Rendere le 4 opzioni simili per lunghezza, struttura e livello tecnico."
            ],
            "proposta_revisione": {
                "opzioni": [],
                "risposta_corretta": "",
                "nota": "Da compilare nella fase successiva."
            }
        })

    OUTPUT_JSON.write_text(
        json.dumps(domande_da_migliorare, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    righe = []
    righe.append("# Biologia — distrattori da migliorare")
    righe.append("")
    righe.append(f"Domande totali in `data/biologia.json`: **{len(domande)}**")
    righe.append(f"Domande da migliorare: **{len(domande_da_migliorare)}**")
    righe.append("")
    righe.append(
        "Questo file non modifica il database originale. "
        "Serve come base di lavoro per migliorare i distrattori."
    )
    righe.append("")

    for item in domande_da_migliorare:
        righe.append(f"## {item['id']} — livello: {item['livello']}")
        righe.append("")
        righe.append(f"**Domanda:** {item['domanda']}")
        righe.append("")
        righe.append("**Opzioni attuali:**")

        lettere = ["A", "B", "C", "D"]

        for indice, opzione in enumerate(item["opzioni_attuali"]):
            marker = " ✅" if opzione == item["risposta_corretta"] else ""
            righe.append(f"- {lettere[indice]}. {opzione}{marker}")

        righe.append("")
        righe.append(f"**Risposta corretta nel sorgente:** {item['posizione_risposta_corretta']}")
        righe.append("")
        righe.append("**Problemi rilevati:**")

        for problema in item["problemi"]:
            righe.append(f"- {problema}")

        righe.append("")
        righe.append("**Regole per la revisione:**")
        righe.append("- Non cambiare il concetto della risposta corretta.")
        righe.append("- Inserire almeno un distrattore forte vicino alla risposta corretta.")
        righe.append("- Eliminare distrattori troppo assoluti o troppo facili.")
        righe.append("- Rendere le opzioni simili per lunghezza e forma.")
        righe.append("")

    OUTPUT_MD.write_text("\n".join(righe), encoding="utf-8")

    print("----- ESTRAZIONE BIOLOGIA DA MIGLIORARE -----")
    print(f"Domande totali Biologia: {len(domande)}")
    print(f"Domande da migliorare: {len(domande_da_migliorare)}")
    print(f"Creato JSON lavoro: {OUTPUT_JSON.relative_to(ROOT)}")
    print(f"Creato report lavoro: {OUTPUT_MD.relative_to(ROOT)}")

    if len(domande_da_migliorare) == 0:
        print("OK: nessuna domanda di Biologia da migliorare.")
    else:
        print("OK: file di lavoro Biologia creati.")


if __name__ == "__main__":
    main()
