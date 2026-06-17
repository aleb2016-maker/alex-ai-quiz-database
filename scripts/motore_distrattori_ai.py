import json
import re
from difflib import SequenceMatcher
from pathlib import Path

FILE_AI = Path("data/ai.json")
REPORT_MD = Path("reports/motore_distrattori_ai.md")
REPORT_JSON = Path("reports/motore_distrattori_ai.json")

PAROLE_ASSOLUTE = [
    "sempre",
    "mai",
    "solo",
    "soltanto",
    "tutti",
    "nessuno",
    "qualsiasi",
    "completamente",
    "totalmente",
    "automaticamente",
    "impossibile",
    "a caso",
    "senza logica",
    "non serve",
]

STOPWORDS = {
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una",
    "di", "a", "da", "in", "con", "su", "per", "tra", "fra",
    "che", "è", "e", "o", "ma", "se", "del", "della", "dei",
    "degli", "delle", "al", "allo", "alla", "ai", "agli", "alle",
    "nel", "nello", "nella", "nei", "negli", "nelle", "come",
    "può", "sono", "essere", "viene", "vengono", "questo", "questa",
    "quello", "quella", "the", "a", "an", "of", "to", "and", "or",
    "is", "are", "be", "with", "that", "which", "this"
}


def pulisci_testo(testo):
    testo = str(testo or "").lower()
    testo = testo.replace("à", "a").replace("è", "e").replace("é", "e")
    testo = testo.replace("ì", "i").replace("ò", "o").replace("ù", "u")
    testo = re.sub(r"[^a-z0-9\s\+\-\*\/\=\<\>\.]", " ", testo)
    testo = re.sub(r"\s+", " ", testo).strip()
    return testo


def tokenizza(testo):
    testo = pulisci_testo(testo)
    return [
        token
        for token in testo.split()
        if token not in STOPWORDS and len(token) > 1
    ]


def similarita(testo_a, testo_b):
    a = pulisci_testo(testo_a)
    b = pulisci_testo(testo_b)

    if not a or not b:
        return 0.0

    sequenza = SequenceMatcher(None, a, b).ratio()

    token_a = set(tokenizza(a))
    token_b = set(tokenizza(b))

    if token_a or token_b:
        jaccard = len(token_a & token_b) / max(1, len(token_a | token_b))
    else:
        jaccard = 0.0

    bilanciamento_lunghezza = min(len(a), len(b)) / max(len(a), len(b), 1)

    punteggio = (
        sequenza * 0.40
        + jaccard * 0.40
        + bilanciamento_lunghezza * 0.20
    )

    return round(punteggio, 3)


def testo_opzione(opzione):
    if isinstance(opzione, dict):
        return str(
            opzione.get("testo")
            or opzione.get("text")
            or opzione.get("risposta")
            or opzione.get("value")
            or ""
        ).strip()

    return str(opzione or "").strip()


def estrai_opzioni(domanda):
    opzioni = (
        domanda.get("opzioni")
        or domanda.get("options")
        or domanda.get("risposte")
        or []
    )

    if isinstance(opzioni, list):
        return [testo_opzione(opzione) for opzione in opzioni]

    if isinstance(opzioni, dict):
        return [testo_opzione(opzione) for _, opzione in sorted(opzioni.items())]

    return []


def indice_corretta(domanda, opzioni):
    risposta = str(
        domanda.get("risposta_corretta")
        or domanda.get("correct_answer")
        or domanda.get("correct")
        or domanda.get("answer")
        or ""
    ).strip()

    if risposta.upper() in ["A", "B", "C", "D"]:
        indice = ord(risposta.upper()) - ord("A")
        if 0 <= indice < len(opzioni):
            return indice

    for indice, opzione in enumerate(opzioni):
        if risposta == opzione:
            return indice

    return None


def trova_parole_assolute(testo):
    testo_norm = pulisci_testo(testo)
    return [parola for parola in PAROLE_ASSOLUTE if parola in testo_norm]


def analizza_domanda(domanda, numero):
    id_domanda = domanda.get("id", f"AI-{numero:04d}")
    testo_domanda = domanda.get("domanda", domanda.get("question", ""))
    livello = domanda.get("livello", domanda.get("difficulty", "senza livello"))

    opzioni = estrai_opzioni(domanda)

    if len(opzioni) != 4:
        return {
            "id": id_domanda,
            "livello": livello,
            "domanda": testo_domanda,
            "opzioni": opzioni,
            "problemi": ["Numero opzioni diverso da 4."],
            "gravita": 100,
        }

    corretta_i = indice_corretta(domanda, opzioni)

    if corretta_i is None:
        return {
            "id": id_domanda,
            "livello": livello,
            "domanda": testo_domanda,
            "opzioni": opzioni,
            "problemi": ["Risposta corretta non individuata."],
            "gravita": 100,
        }

    corretta = opzioni[corretta_i]

    # Regola del progetto:
    # se A è corretta, B deve essere il distrattore principale forte.
    # se la corretta non è A, prendiamo comunque la prima errata come distrattore principale.
    if corretta_i == 0:
        distrattore_forte_i = 1
    else:
        distrattore_forte_i = next(i for i in range(4) if i != corretta_i)

    distrattore_forte = opzioni[distrattore_forte_i]

    problemi = []
    gravita = 0

    sim_forte = similarita(corretta, distrattore_forte)

    similarita_errate = []
    for indice, opzione in enumerate(opzioni):
        if indice == corretta_i:
            continue

        similarita_errate.append({
            "lettera": chr(65 + indice),
            "testo": opzione,
            "similarita": similarita(corretta, opzione),
        })

    migliore_errata = max(similarita_errate, key=lambda item: item["similarita"])

    lunghezze = [len(pulisci_testo(opzione)) for opzione in opzioni]
    lunghezza_corretta = lunghezze[corretta_i]
    lunghezza_forte = lunghezze[distrattore_forte_i]

    if sim_forte < 0.42:
        problemi.append(
            f"Distrattore principale {chr(65 + distrattore_forte_i)} troppo lontano dalla corretta. Similarità: {sim_forte}."
        )
        gravita += 35

    if migliore_errata["similarita"] < 0.42:
        problemi.append(
            f"Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: {migliore_errata['similarita']}."
        )
        gravita += 30

    if lunghezza_forte < lunghezza_corretta * 0.60:
        problemi.append(
            f"Distrattore principale troppo corto rispetto alla corretta: {lunghezza_forte} caratteri contro {lunghezza_corretta}."
        )
        gravita += 20

    if lunghezza_corretta == max(lunghezze) and max(lunghezze) - min(lunghezze) > 55:
        problemi.append(
            f"La risposta corretta spicca per lunghezza. Lunghezze opzioni: {lunghezze}."
        )
        gravita += 20

    for indice, opzione in enumerate(opzioni):
        if indice == corretta_i:
            continue

        parole = trova_parole_assolute(opzione)

        if parole:
            problemi.append(
                f"Opzione {chr(65 + indice)} eliminabile per parole troppo assolute: {', '.join(parole)}."
            )
            gravita += 15

    tokens_corretta = set(tokenizza(corretta))
    tokens_forte = set(tokenizza(distrattore_forte))

    if tokens_corretta:
        sovrapposizione = len(tokens_corretta & tokens_forte) / max(1, len(tokens_corretta))
    else:
        sovrapposizione = 0

    if sovrapposizione < 0.25:
        problemi.append(
            f"Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: {round(sovrapposizione, 2)}."
        )
        gravita += 20

    return {
        "id": id_domanda,
        "livello": livello,
        "domanda": testo_domanda,
        "opzioni": opzioni,
        "corretta": chr(65 + corretta_i),
        "distrattore_principale": chr(65 + distrattore_forte_i),
        "similarita_distrattore_principale": sim_forte,
        "migliore_errata": migliore_errata,
        "lunghezze": lunghezze,
        "problemi": problemi,
        "gravita": gravita,
    }


def main():
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)

    contenuto = json.loads(FILE_AI.read_text(encoding="utf-8"))

    if isinstance(contenuto, list):
        domande = contenuto
    else:
        domande = contenuto.get("domande", contenuto.get("questions", []))

    risultati = []

    for numero, domanda in enumerate(domande, start=1):
        risultato = analizza_domanda(domanda, numero)

        if risultato["problemi"]:
            risultati.append(risultato)

    risultati.sort(key=lambda item: item["gravita"], reverse=True)

    report_json = {
        "file": str(FILE_AI),
        "domande_controllate": len(domande),
        "domande_problematiche": len(risultati),
        "risultati": risultati,
    }

    REPORT_JSON.write_text(
        json.dumps(report_json, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    righe = []
    righe.append("# Motore distrattori AI")
    righe.append("")
    righe.append(f"File controllato: `{FILE_AI}`")
    righe.append("")
    righe.append(f"Domande controllate: {len(domande)}")
    righe.append(f"Domande problematiche: {len(risultati)}")
    righe.append("")

    righe.append("## Prime domande da correggere")
    righe.append("")

    for item in risultati[:25]:
        righe.append("---")
        righe.append("")
        righe.append(f"### {item['id']}")
        righe.append("")
        righe.append(f"Livello: `{item['livello']}`")
        righe.append("")
        righe.append(f"Gravità: `{item['gravita']}`")
        righe.append("")
        righe.append(f"Domanda: {item['domanda']}")
        righe.append("")
        righe.append("Opzioni:")
        righe.append("")
        for indice, opzione in enumerate(item["opzioni"]):
            lettera = chr(65 + indice)
            marker = " ✅" if item.get("corretta") == lettera else ""
            forte = " 🎯 distrattore principale" if item.get("distrattore_principale") == lettera else ""
            righe.append(f"- {lettera}. {opzione}{marker}{forte}")
        righe.append("")
        righe.append(f"Similarità distrattore principale: `{item.get('similarita_distrattore_principale')}`")
        righe.append("")
        righe.append("Problemi:")
        righe.append("")
        for problema in item["problemi"]:
            righe.append(f"- {problema}")
        righe.append("")

    REPORT_MD.write_text("\n".join(righe), encoding="utf-8")

    print("===== MOTORE DISTRATTORI AI =====")
    print(f"Domande controllate: {len(domande)}")
    print(f"Domande problematiche: {len(risultati)}")
    print()
    print("Report creati:")
    print(f"- {REPORT_MD}")
    print(f"- {REPORT_JSON}")
    print()
    print("Prime 10 domande più problematiche:")

    for item in risultati[:10]:
        print(f"- {item['id']} | gravità {item['gravita']} | problemi {len(item['problemi'])}")

    if not risultati:
        print("OK: nessun problema forte trovato sui distrattori AI.")


if __name__ == "__main__":
    main()
