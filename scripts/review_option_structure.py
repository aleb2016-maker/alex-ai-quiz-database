import json
import re
from difflib import SequenceMatcher
from pathlib import Path


PERCORSO_DATABASE = Path("dist/database_quiz_finale.json")
PERCORSO_REPORT = Path("dist/report_struttura_opzioni.md")


STOPWORDS = {
    "per", "che", "con", "una", "uno", "gli", "del", "della", "delle",
    "dei", "nel", "nella", "nelle", "sul", "sulla", "sono", "essere",
    "viene", "vengono", "può", "possono", "come", "quando", "quale",
    "qual", "cosa", "serve", "principalmente", "normalmente", "sempre",
    "solo", "anche", "tra", "più", "meno", "non", "il", "lo", "la",
    "le", "i", "a", "e", "di", "da", "in", "su", "al", "ai",
    "the", "a", "an", "to", "of", "and", "or", "in", "on", "for",
    "with", "is", "are", "was", "were", "be", "been", "have", "has"
}


FRASI_TROPPO_DEBOLI = [
    "cambiare il colore",
    "cambia il colore",
    "spegnere il database",
    "cancellare il database",
    "cancella il database",
    "trasformare tutto in immagine",
    "trasforma tutto in immagine",
    "rendere la pagina più colorata",
    "impedire l'uso di immagini",
    "sostituire completamente la necessità di scrivere codice",
    "trasforma automaticamente ogni bug",
    "elimina sempre la necessità",
    "rende impossibile qualunque errore",
    "non ha nessun collegamento",
]


def normalizza_testo(testo):
    testo = str(testo).lower()
    testo = testo.replace("à", "a")
    testo = testo.replace("è", "e")
    testo = testo.replace("é", "e")
    testo = testo.replace("ì", "i")
    testo = testo.replace("ò", "o")
    testo = testo.replace("ù", "u")
    testo = re.sub(r"[^a-z0-9/%.,]+", " ", testo)
    testo = re.sub(r"\s+", " ", testo).strip()
    return testo


def estrai_token(testo):
    testo = normalizza_testo(testo)
    parole = re.findall(r"[a-z0-9]+", testo)

    return {
        parola
        for parola in parole
        if len(parola) > 2
        and parola not in STOPWORDS
    }


def somiglianza_testuale(testo_1, testo_2):
    testo_1_norm = normalizza_testo(testo_1)
    testo_2_norm = normalizza_testo(testo_2)

    sequenza = SequenceMatcher(
        None,
        testo_1_norm,
        testo_2_norm
    ).ratio()

    token_1 = estrai_token(testo_1)
    token_2 = estrai_token(testo_2)

    if token_1 or token_2:
        jaccard = len(token_1 & token_2) / len(token_1 | token_2)
    else:
        jaccard = 0

    return round((sequenza * 0.55) + (jaccard * 0.45), 3)


def estrai_numeri(testo):
    testo = str(testo).replace(",", ".")

    frazioni = re.findall(r"(\d+)\s*/\s*(\d+)", testo)
    numeri_frazione = []

    for numeratore, denominatore in frazioni:
        denominatore = float(denominatore)

        if denominatore != 0:
            numeri_frazione.append(float(numeratore) / denominatore)

    numeri_normali = re.findall(r"-?\d+(?:\.\d+)?", testo)
    numeri = [
        float(numero)
        for numero in numeri_normali
    ]

    return numeri_frazione + numeri


def distanza_numerica(risposta_corretta, opzione):
    numeri_corretti = estrai_numeri(risposta_corretta)
    numeri_opzione = estrai_numeri(opzione)

    if not numeri_corretti or not numeri_opzione:
        return None

    valore_corretto = numeri_corretti[0]
    valore_opzione = numeri_opzione[0]

    return abs(valore_corretto - valore_opzione)


def opzione_contiene_frase_debole(opzione):
    opzione_norm = normalizza_testo(opzione)

    for frase in FRASI_TROPPO_DEBOLI:
        if normalizza_testo(frase) in opzione_norm:
            return True

    return False


def analizza_domanda(domanda):
    problemi = []

    id_domanda = domanda.get("id", "ID_MANCANTE")
    categoria = domanda.get("categoria", "")
    testo_domanda = domanda.get("domanda", "")
    opzioni = domanda.get("opzioni", [])
    risposta_corretta = domanda.get("risposta_corretta", "")

    if len(opzioni) != 4:
        problemi.append("La domanda non ha esattamente 4 opzioni.")
        return problemi

    # Per la matematica non applichiamo il controllo A/B/C/D forte.
    # Le risposte numeriche vicine sono spesso già valide anche se non sono ordinate
    # esattamente come A corretta, B più vicina, C e D vicine tra loro.
    # La matematica resta controllata dagli altri script:
    # validazione, duplicati, somiglianze e opzioni duplicate.
    if categoria == "matematica":
        return problemi

    opzione_a = opzioni[0]
    opzione_b = opzioni[1]
    opzione_c = opzioni[2]
    opzione_d = opzioni[3]

    if opzione_a != risposta_corretta:
        problemi.append(
            "La risposta corretta non è in posizione A. "
            "La nuova struttura richiede A = risposta corretta."
        )

    opzioni_sbagliate = [
        opzione
        for opzione in opzioni
        if opzione != risposta_corretta
    ]

    for opzione in opzioni_sbagliate:
        if opzione_contiene_frase_debole(opzione):
            problemi.append(
                f"Possibile distrattore troppo debole o assurdo: {opzione}"
            )

    distanza_b = distanza_numerica(opzione_a, opzione_b)
    distanza_c = distanza_numerica(opzione_a, opzione_c)
    distanza_d = distanza_numerica(opzione_a, opzione_d)

    usa_controllo_numerico = (
        distanza_b is not None
        and distanza_c is not None
        and distanza_d is not None
    )

    if usa_controllo_numerico:
        distanza_minima = min(distanza_b, distanza_c, distanza_d)

        if distanza_b > distanza_minima:
            problemi.append(
                "Il distrattore B non sembra il più vicino numericamente alla risposta corretta."
            )

        if abs(distanza_c - distanza_d) > max(2, distanza_b * 4):
            problemi.append(
                "I distrattori C e D non sembrano abbastanza vicini tra loro sul piano numerico."
            )

    else:
        somiglianza_ab = somiglianza_testuale(opzione_a, opzione_b)
        somiglianza_ac = somiglianza_testuale(opzione_a, opzione_c)
        somiglianza_ad = somiglianza_testuale(opzione_a, opzione_d)
        somiglianza_cd = somiglianza_testuale(opzione_c, opzione_d)

        opzioni_molto_brevi = all(
            len(estrai_token(opzione)) <= 2
            for opzione in opzioni
        )

        if not opzioni_molto_brevi:
            if somiglianza_ab < 0.10:
                problemi.append(
                    f"Il distrattore B sembra poco vicino alla risposta corretta. Somiglianza A/B: {somiglianza_ab}"
                )

            if somiglianza_cd < 0.09:
                problemi.append(
                    f"I distrattori C e D sembrano poco vicini tra loro. Somiglianza C/D: {somiglianza_cd}"
                )

    return problemi


def carica_database():
    if not PERCORSO_DATABASE.exists():
        raise FileNotFoundError(
            f"Database non trovato: {PERCORSO_DATABASE}. "
            "Esegui prima: python scripts/build_database.py"
        )

    with open(PERCORSO_DATABASE, "r", encoding="utf-8") as file:
        return json.load(file)


def crea_report(domande):
    righe = []

    domande_da_sistemare = []

    righe.append("# Report struttura opzioni A/B/C/D")
    righe.append("")
    righe.append("Regola controllata:")
    righe.append("")
    righe.append("- A = risposta corretta")
    righe.append("- B = distrattore forte, molto vicino alla corretta")
    righe.append("- C = distrattore medio, stesso argomento ma più chiaramente sbagliato")
    righe.append("- D = distrattore medio, argomento vicinissimo al C")
    righe.append("")
    righe.append("---")
    righe.append("")

    for domanda in domande:
        problemi = analizza_domanda(domanda)

        if problemi:
            domande_da_sistemare.append(
                {
                    "domanda": domanda,
                    "problemi": problemi
                }
            )

    righe.append("## Riepilogo")
    righe.append("")
    righe.append(f"Domande controllate: {len(domande)}")
    righe.append(f"Domande da sistemare: {len(domande_da_sistemare)}")
    righe.append("")

    if not domande_da_sistemare:
        righe.append("Tutte le domande rispettano la struttura A/B/C/D secondo il controllo automatico.")
        righe.append("")
    else:
        righe.append("---")
        righe.append("")
        righe.append("## Domande da sistemare")
        righe.append("")

    for elemento in domande_da_sistemare:
        domanda = elemento["domanda"]
        problemi = elemento["problemi"]

        id_domanda = domanda.get("id", "ID_MANCANTE")
        categoria = domanda.get("categoria", "categoria_mancante")
        livello = domanda.get("livello", "livello_mancante")
        testo_domanda = domanda.get("domanda", "")
        opzioni = domanda.get("opzioni", [])
        risposta_corretta = domanda.get("risposta_corretta", "")

        righe.append(f"### {id_domanda} - DA SISTEMARE")
        righe.append("")
        righe.append(f"**Categoria:** {categoria}")
        righe.append("")
        righe.append(f"**Livello:** {livello}")
        righe.append("")
        righe.append(f"**Domanda:** {testo_domanda}")
        righe.append("")
        righe.append("**Opzioni:**")

        lettere = ["A", "B", "C", "D"]

        for indice, opzione in enumerate(opzioni):
            simbolo = "✅" if opzione == risposta_corretta else "❌"
            righe.append(f"- {lettere[indice]}. {simbolo} {opzione}")

        righe.append("")
        righe.append("**Problemi:**")

        for problema in problemi:
            righe.append(f"- {problema}")

        righe.append("")
        righe.append("---")
        righe.append("")

    PERCORSO_REPORT.parent.mkdir(parents=True, exist_ok=True)
    PERCORSO_REPORT.write_text(
        "\n".join(righe),
        encoding="utf-8"
    )

    return len(domande_da_sistemare)


def main():
    domande = carica_database()
    numero_da_sistemare = crea_report(domande)

    print("Report struttura opzioni creato correttamente:")
    print(PERCORSO_REPORT)
    print("Domande controllate:", len(domande))
    print("Domande da sistemare:", numero_da_sistemare)


main()