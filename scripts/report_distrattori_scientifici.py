from pathlib import Path
import json
import re
from difflib import SequenceMatcher
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

MOTORI = {
    "Scienze generali": ROOT / "data" / "scienze.json",
    "Biologia": ROOT / "data" / "biologia.json",
    "Fisica": ROOT / "data" / "fisica.json",
    "Chimica": ROOT / "data" / "chimica.json",
    "Fisica quantistica": ROOT / "data" / "fisica_quantistica.json",
}

REPORT_MD = ROOT / "reports" / "report_distrattori_scientifici.md"

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
        return [
            str(opzione.get("testo") if isinstance(opzione, dict) else opzione).strip()
            for opzione in opzioni_grezze
            if str(opzione).strip()
        ]

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


def valuta_qualita_opzioni(opzioni, risposta):
    problemi_reali = []

    if len(opzioni) != 4:
        problemi_reali.append("La domanda non ha esattamente 4 opzioni.")
        return problemi_reali

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
                problemi_reali.append(
                    f"Possibile opzione debole/generica: contiene “{parola}”."
                )

    lunghezze = [len(opzione) for opzione in opzioni if opzione]

    if lunghezze and min(lunghezze) > 0:
        rapporto = max(lunghezze) / min(lunghezze)

        if rapporto >= 3:
            problemi_reali.append(
                "Opzioni con lunghezze molto sbilanciate: "
                "una risposta può risultare troppo riconoscibile."
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
            problemi_reali.append(
                "Manca un distrattore forte: nessuna risposta sbagliata "
                "sembra abbastanza vicina alla risposta corretta."
            )

    return problemi_reali


def analizza_motore(nome_motore, percorso):
    domande = carica_domande(percorso)
    domande_con_problemi_reali = []
    avvisi_posizione = []

    for domanda in domande:
        if not isinstance(domanda, dict):
            continue

        testo = str(prendi(domanda, CAMPI_DOMANDA) or "").strip()
        opzioni = normalizza_opzioni(prendi(domanda, CAMPI_OPZIONI))
        risposta = normalizza_risposta(prendi(domanda, CAMPI_RISPOSTA), opzioni)
        livello = str(prendi(domanda, CAMPI_LIVELLO) or "senza_livello").strip()
        posizione = posizione_risposta(risposta, opzioni)

        problemi_reali = valuta_qualita_opzioni(opzioni, risposta)

        item = {
            "id": domanda.get("id", ""),
            "livello": livello,
            "domanda": testo,
            "opzioni": opzioni,
            "risposta": risposta,
            "posizione": posizione,
            "problemi_reali": problemi_reali,
        }

        if problemi_reali:
            domande_con_problemi_reali.append(item)

        if posizione == "A":
            avvisi_posizione.append(item)

    return domande, domande_con_problemi_reali, avvisi_posizione


def scrivi_domanda_report(righe, item):
    righe.append(f"### {item['id']} — livello: {item['livello']}")
    righe.append("")
    righe.append(f"**Domanda:** {item['domanda']}")
    righe.append("")
    righe.append("**Opzioni attuali:**")

    lettere = ["A", "B", "C", "D"]

    for indice, opzione in enumerate(item["opzioni"]):
        lettera = lettere[indice] if indice < len(lettere) else "?"
        marker = " ✅" if opzione == item["risposta"] else ""
        righe.append(f"- {lettera}. {opzione}{marker}")

    righe.append("")
    righe.append(f"**Risposta corretta nel sorgente:** {item['posizione']}")
    righe.append("")
    righe.append("**Problemi reali:**")

    for problema in item["problemi_reali"]:
        righe.append(f"- {problema}")

    righe.append("")
    righe.append("**Regola di revisione:**")
    righe.append(
        "- Ogni domanda deve avere almeno un distrattore forte: "
        "una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso."
    )
    righe.append(
        "- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile."
    )
    righe.append(
        "- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico."
    )
    righe.append("")


def crea_report():
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)

    righe = []
    riepilogo = []

    righe.append("# Report qualità distrattori motori scientifici")
    righe.append("")
    righe.append(
        "Questo report separa i problemi qualitativi reali dagli avvisi non bloccanti "
        "sulla posizione della risposta corretta nel file sorgente."
    )
    righe.append("")

    dati = {}

    for nome_motore, percorso in MOTORI.items():
        domande, problemi_reali, avvisi_posizione = analizza_motore(nome_motore, percorso)
        dati[nome_motore] = (domande, problemi_reali, avvisi_posizione)
        riepilogo.append((nome_motore, len(domande), len(problemi_reali), len(avvisi_posizione)))

    righe.append("## Riepilogo")
    righe.append("")
    righe.append("| Motore | Domande | Problemi qualità reali | Risposta in A nel sorgente |")
    righe.append("|---|---:|---:|---:|")

    for nome_motore, totale, problemi, in_a in riepilogo:
        righe.append(f"| {nome_motore} | {totale} | {problemi} | {in_a} |")

    righe.append("")
    righe.append(
        "**Nota:** la risposta in A nel sorgente non è più bloccante, "
        "perché il runtime ora usa il mescolatore generale."
    )
    righe.append("")

    for nome_motore, (domande, problemi_reali, avvisi_posizione) in dati.items():
        righe.append(f"## {nome_motore}")
        righe.append("")
        righe.append(f"Domande sorgente: **{len(domande)}**")
        righe.append(f"Domande con problemi qualità reali: **{len(problemi_reali)}**")
        righe.append(f"Risposte corrette in A nel sorgente: **{len(avvisi_posizione)}**")
        righe.append("")

        posizioni = Counter()

        for domanda in domande:
            opzioni = normalizza_opzioni(prendi(domanda, CAMPI_OPZIONI))
            risposta = normalizza_risposta(prendi(domanda, CAMPI_RISPOSTA), opzioni)
            posizioni[posizione_risposta(risposta, opzioni)] += 1

        righe.append("Distribuzione risposta corretta nel sorgente:")
        righe.append("")
        righe.append(f"```text\n{dict(posizioni)}\n```")
        righe.append("")

        if problemi_reali:
            righe.append("### Domande da migliorare davvero")
            righe.append("")

            for item in problemi_reali:
                scrivi_domanda_report(righe, item)
        else:
            righe.append("Nessun problema qualitativo reale rilevato.")
            righe.append("")

    REPORT_MD.write_text("\n".join(righe), encoding="utf-8")

    print("----- REPORT QUALITÀ DISTRATTORI SCIENTIFICI -----")
    print(f"Creato: {REPORT_MD.relative_to(ROOT)}")
    print("")
    print("Riepilogo:")

    for nome_motore, totale, problemi, in_a in riepilogo:
        print(
            f"- {nome_motore}: "
            f"{problemi}/{totale} problemi qualità reali, "
            f"{in_a} risposte in A nel sorgente"
        )


if __name__ == "__main__":
    crea_report()
