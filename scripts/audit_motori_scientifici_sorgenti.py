from pathlib import Path
import json
import re
from collections import Counter
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parents[1]

MOTORI = {
    "scienze_generali": ROOT / "data" / "scienze.json",
    "biologia": ROOT / "data" / "biologia.json",
    "fisica": ROOT / "data" / "fisica.json",
    "chimica": ROOT / "data" / "chimica.json",
    "fisica_quantistica": ROOT / "data" / "fisica_quantistica.json",
}

CAMPI_DOMANDA = ["domanda", "question", "testo", "text"]
CAMPI_OPZIONI = ["opzioni", "options", "risposte", "answers"]
CAMPI_RISPOSTA = [
    "risposta_corretta",
    "correct_answer",
    "correctAnswer",
    "answer",
    "correct",
]
CAMPI_SPIEGAZIONE = [
    "spiegazione",
    "explanation",
    "spiegazione_finale",
    "explanation_final",
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

        if opzioni:
            return [opzione for opzione in opzioni if opzione]

        return [
            str(valore).strip()
            for valore in opzioni_grezze.values()
            if str(valore).strip()
        ]

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


def trova_posizione_corretta(risposta, opzioni):
    if risposta in opzioni:
        return ["A", "B", "C", "D"][opzioni.index(risposta)]
    return None


def valuta_domanda(domanda):
    problemi_tecnici = []
    avvisi_qualita = []

    testo_domanda = str(prendi(domanda, CAMPI_DOMANDA) or "").strip()
    opzioni = normalizza_opzioni(prendi(domanda, CAMPI_OPZIONI))
    risposta = normalizza_risposta(prendi(domanda, CAMPI_RISPOSTA), opzioni)
    spiegazione = str(prendi(domanda, CAMPI_SPIEGAZIONE) or "").strip()
    livello = str(prendi(domanda, CAMPI_LIVELLO) or "senza_livello").strip()

    if len(testo_domanda) < 12:
        problemi_tecnici.append("domanda mancante o troppo corta")

    if len(opzioni) != 4:
        problemi_tecnici.append(f"opzioni non sono 4: {len(opzioni)}")

    if len(opzioni) == 4:
        opzioni_norm = [normalizza_testo(opzione) for opzione in opzioni]

        if len(set(opzioni_norm)) < 4:
            problemi_tecnici.append("opzioni duplicate")

    if not risposta:
        problemi_tecnici.append("risposta corretta mancante")
    elif opzioni and risposta not in opzioni:
        problemi_tecnici.append("risposta corretta non presente nelle opzioni")

    if len(spiegazione) < 25:
        problemi_tecnici.append("spiegazione mancante o troppo breve")

    parole_deboli = [
        "tutte le precedenti",
        "nessuna delle precedenti",
        "non lo so",
        "sempre",
        "mai",
    ]

    for opzione in opzioni:
        opzione_norm = normalizza_testo(opzione)

        for parola in parole_deboli:
            if parola in opzione_norm:
                avvisi_qualita.append(f"possibile opzione debole: {parola}")

    if len(opzioni) == 4:
        lunghezze = [len(opzione) for opzione in opzioni if len(opzione) > 0]

        if lunghezze and max(lunghezze) / min(lunghezze) >= 3:
            avvisi_qualita.append("opzioni con lunghezze molto sbilanciate")

    posizione = trova_posizione_corretta(risposta, opzioni)

    return {
        "id": domanda.get("id", ""),
        "testo": testo_domanda,
        "opzioni": opzioni,
        "risposta": risposta,
        "posizione": posizione,
        "livello": livello,
        "problemi_tecnici": problemi_tecnici,
        "avvisi_qualita": avvisi_qualita,
    }


def controlla_motore(nome_motore, percorso):
    print("")
    print(f"===== {nome_motore.upper()} =====")

    if not percorso.exists():
        print(f"ERRORE: file mancante: {percorso.relative_to(ROOT)}")
        return {
            "domande": 0,
            "problemi_tecnici": 0,
            "avvisi_qualita": 0,
        }

    domande = carica_domande(percorso)
    risultati = [
        valuta_domanda(domanda)
        for domanda in domande
        if isinstance(domanda, dict)
    ]

    print(f"File: {percorso.relative_to(ROOT)}")
    print(f"Domande sorgente: {len(risultati)}")

    livelli = Counter(r["livello"] for r in risultati)
    posizioni = Counter(r["posizione"] for r in risultati if r["posizione"])

    print(f"Livelli: {dict(livelli)}")
    print(f"Posizione risposta corretta nel file sorgente: {dict(posizioni)}")

    problemi = [
        r
        for r in risultati
        if r["problemi_tecnici"]
    ]

    avvisi = [
        r
        for r in risultati
        if r["avvisi_qualita"]
    ]

    print(f"Problemi tecnici veri: {len(problemi)}")
    print(f"Avvisi qualità da rivedere: {len(avvisi)}")

    testi = [
        normalizza_testo(r["testo"])
        for r in risultati
        if r["testo"]
    ]

    duplicati_esatti = [
        testo
        for testo, quantita in Counter(testi).items()
        if quantita > 1
    ]

    print(f"Domande duplicate identiche nel sorgente: {len(duplicati_esatti)}")

    simili = []

    for i in range(len(risultati)):
        testo_a = normalizza_testo(risultati[i]["testo"])

        if not testo_a:
            continue

        for j in range(i + 1, len(risultati)):
            testo_b = normalizza_testo(risultati[j]["testo"])

            if not testo_b:
                continue

            similarita = SequenceMatcher(None, testo_a, testo_b).ratio()

            if similarita >= 0.88 and testo_a != testo_b:
                simili.append((similarita, risultati[i], risultati[j]))

    print(f"Domande molto simili nel sorgente: {len(simili)}")

    if problemi:
        print("")
        print("Primi problemi tecnici:")

        for item in problemi[:8]:
            print(f"- {item['id']} | {item['testo'][:120]}")
            print(f"  Problemi: {', '.join(item['problemi_tecnici'])}")

    if avvisi:
        print("")
        print("Primi avvisi qualità:")

        for item in avvisi[:8]:
            print(f"- {item['id']} | {item['testo'][:120]}")
            print(f"  Avvisi: {', '.join(item['avvisi_qualita'][:3])}")

    if simili:
        print("")
        print("Prime domande troppo simili:")

        for similarita, a, b in simili[:5]:
            print(f"- Similarità {similarita:.2f}")
            print(f"  A: {a['id']} | {a['testo'][:100]}")
            print(f"  B: {b['id']} | {b['testo'][:100]}")

    return {
        "domande": len(risultati),
        "problemi_tecnici": len(problemi),
        "avvisi_qualita": len(avvisi),
        "duplicati": len(duplicati_esatti),
        "simili": len(simili),
    }


def main():
    print("----- AUDIT MOTORI SCIENTIFICI SORGENTI -----")
    print("Controllo solo i file data/*.json, senza copie generate in dist o downloads.")

    riepilogo = {}

    for nome, percorso in MOTORI.items():
        riepilogo[nome] = controlla_motore(nome, percorso)

    print("")
    print("----- RIEPILOGO SORGENTI -----")

    for nome, dati in riepilogo.items():
        print(
            f"{nome}: "
            f"{dati['domande']} domande, "
            f"{dati['problemi_tecnici']} problemi tecnici, "
            f"{dati['avvisi_qualita']} avvisi qualità, "
            f"{dati.get('duplicati', 0)} duplicati, "
            f"{dati.get('simili', 0)} simili"
        )

    problemi_totali = sum(dati["problemi_tecnici"] for dati in riepilogo.values())

    if problemi_totali == 0:
        print("")
        print("OK: i sorgenti non hanno problemi tecnici bloccanti.")
        print("Ora si può passare alla revisione qualitativa dei distrattori.")
    else:
        print("")
        print("ATTENZIONE: prima bisogna correggere i problemi tecnici bloccanti.")


if __name__ == "__main__":
    main()
