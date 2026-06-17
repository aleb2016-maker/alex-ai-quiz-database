import json
import re
from difflib import SequenceMatcher
from pathlib import Path

FILE_AI = Path("data/ai.json")
REPORT_MD = Path("reports/motore_distrattori_ai_tre_forti.md")
REPORT_JSON = Path("reports/motore_distrattori_ai_tre_forti.json")

PAROLE_TROPPO_FACILI = [
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
    "ignorando",
    "senza considerare",
    "non ha niente a che fare",
]

STOPWORDS = {
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una",
    "di", "a", "da", "in", "con", "su", "per", "tra", "fra",
    "che", "è", "e", "o", "ma", "se", "del", "della", "dei",
    "degli", "delle", "al", "allo", "alla", "ai", "agli", "alle",
    "nel", "nello", "nella", "nei", "negli", "nelle", "come",
    "può", "sono", "essere", "viene", "vengono", "questo", "questa",
    "quello", "quella", "perché", "quando", "dove", "quindi",
    "the", "a", "an", "of", "to", "and", "or", "is", "are", "be",
    "with", "that", "which", "this"
}


def normalizza(testo):
    testo = str(testo or "").lower()
    testo = testo.replace("à", "a").replace("è", "e").replace("é", "e")
    testo = testo.replace("ì", "i").replace("ò", "o").replace("ù", "u")
    testo = re.sub(r"[^a-z0-9\s]", " ", testo)
    testo = re.sub(r"\s+", " ", testo).strip()
    return testo


def tokenizza(testo):
    return [
        token
        for token in normalizza(testo).split()
        if token not in STOPWORDS and len(token) > 2
    ]


def similarita(a, b):
    a_norm = normalizza(a)
    b_norm = normalizza(b)

    if not a_norm or not b_norm:
        return 0.0

    sequenza = SequenceMatcher(None, a_norm, b_norm).ratio()

    token_a = set(tokenizza(a))
    token_b = set(tokenizza(b))

    if token_a or token_b:
        jaccard = len(token_a & token_b) / max(1, len(token_a | token_b))
    else:
        jaccard = 0.0

    bilanciamento = min(len(a_norm), len(b_norm)) / max(len(a_norm), len(b_norm), 1)

    return round(
        sequenza * 0.35 +
        jaccard * 0.45 +
        bilanciamento * 0.20,
        3
    )


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
    opzioni = domanda.get("opzioni") or domanda.get("options") or domanda.get("risposte") or []

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


def parole_facili(testo):
    testo_norm = normalizza(testo)
    return [parola for parola in PAROLE_TROPPO_FACILI if parola in testo_norm]


def analizza_domanda(domanda, numero):
    id_domanda = domanda.get("id", f"AI-{numero:04d}")
    livello = domanda.get("livello", "senza livello")
    testo_domanda = domanda.get("domanda", "")

    opzioni = estrai_opzioni(domanda)
    problemi = []

    if len(opzioni) != 4:
        return {
            "id": id_domanda,
            "livello": livello,
            "domanda": testo_domanda,
            "opzioni": opzioni,
            "problemi": ["La domanda non ha 4 opzioni."],
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
    token_corretta = set(tokenizza(corretta))

    lunghezze = [len(normalizza(opzione)) for opzione in opzioni]
    lunghezza_corretta = lunghezze[corretta_i]

    gravita = 0
    analisi_opzioni = []

    for indice, opzione in enumerate(opzioni):
        lettera = chr(65 + indice)

        if indice == corretta_i:
            continue

        sim = similarita(corretta, opzione)
        token_opzione = set(tokenizza(opzione))

        if token_corretta:
            sovrapposizione = len(token_corretta & token_opzione) / max(1, len(token_corretta))
        else:
            sovrapposizione = 0

        parole_eliminabili = parole_facili(opzione)
        lunghezza_opzione = lunghezze[indice]

        problemi_opzione = []

        if sim < 0.36:
            problemi_opzione.append(
                f"troppo lontana dalla corretta, similarità {sim}"
            )
            gravita += 25

        if sovrapposizione < 0.22:
            problemi_opzione.append(
                f"condivide pochi concetti chiave con la corretta, sovrapposizione {round(sovrapposizione, 2)}"
            )
            gravita += 20

        if lunghezza_opzione < lunghezza_corretta * 0.55:
            problemi_opzione.append(
                f"troppo corta rispetto alla corretta, {lunghezza_opzione} caratteri contro {lunghezza_corretta}"
            )
            gravita += 15

        if parole_eliminabili:
            problemi_opzione.append(
                f"contiene parole che la rendono eliminabile: {', '.join(parole_eliminabili)}"
            )
            gravita += 20

        analisi_opzioni.append({
            "lettera": lettera,
            "testo": opzione,
            "similarita": sim,
            "sovrapposizione": round(sovrapposizione, 2),
            "problemi": problemi_opzione,
        })

        for problema in problemi_opzione:
            problemi.append(f"Opzione {lettera}: {problema}.")

    if lunghezza_corretta == max(lunghezze) and max(lunghezze) - min(lunghezze) > 60:
        problemi.append(
            f"La corretta spicca per lunghezza. Lunghezze: {lunghezze}."
        )
        gravita += 25

    return {
        "id": id_domanda,
        "livello": livello,
        "domanda": testo_domanda,
        "opzioni": opzioni,
        "corretta": chr(65 + corretta_i),
        "analisi_opzioni": analisi_opzioni,
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
        analisi = analizza_domanda(domanda, numero)

        if analisi["problemi"]:
            risultati.append(analisi)

    risultati.sort(key=lambda item: item["gravita"], reverse=True)

    REPORT_JSON.write_text(
        json.dumps({
            "file": str(FILE_AI),
            "regola": "A corretta + tre distrattori forti",
            "domande_controllate": len(domande),
            "domande_problematiche": len(risultati),
            "risultati": risultati,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    righe = []
    righe.append("# Motore distrattori AI - tre distrattori forti")
    righe.append("")
    righe.append("Regola nuova: ogni domanda deve avere una risposta corretta e tre distrattori forti.")
    righe.append("")
    righe.append(f"Domande controllate: {len(domande)}")
    righe.append(f"Domande problematiche: {len(risultati)}")
    righe.append("")
    righe.append("## Prime domande da correggere")
    righe.append("")

    for item in risultati[:30]:
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
            marker = " ✅" if item["corretta"] == lettera else ""
            righe.append(f"- {lettera}. {opzione}{marker}")

        righe.append("")
        righe.append("Problemi:")
        righe.append("")

        for problema in item["problemi"]:
            righe.append(f"- {problema}")

        righe.append("")
        righe.append("Analisi distrattori:")
        righe.append("")

        for analisi in item["analisi_opzioni"]:
            righe.append(
                f"- {analisi['lettera']}: similarità `{analisi['similarita']}`, "
                f"sovrapposizione `{analisi['sovrapposizione']}`"
            )

        righe.append("")

    REPORT_MD.write_text("\n".join(righe), encoding="utf-8")

    print("===== MOTORE DISTRATTORI AI - TRE FORTI =====")
    print(f"Domande controllate: {len(domande)}")
    print(f"Domande problematiche: {len(risultati)}")
    print()
    print("Prime 10 domande più problematiche:")

    for item in risultati[:10]:
        print(f"- {item['id']} | gravità {item['gravita']} | problemi {len(item['problemi'])}")

    print()
    print("Report creati:")
    print(f"- {REPORT_MD}")
    print(f"- {REPORT_JSON}")


if __name__ == "__main__":
    main()
