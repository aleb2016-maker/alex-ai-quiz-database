from pathlib import Path
import json
import re
from difflib import SequenceMatcher
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]

MATERIE_DA_CONTROLLARE = {
    "scienze_generali": [
        "scienze",
        "scienza",
        "scienze_generali",
        "generale",
    ],
    "biologia": [
        "biologia",
        "biology",
    ],
    "fisica": [
        "fisica",
        "physics",
    ],
    "chimica": [
        "chimica",
        "chemistry",
    ],
    "fisica_quantistica": [
        "fisica_quantistica",
        "quantistica",
        "quantum",
        "meccanica_quantistica",
    ],
}

CARTELLE_DA_SCANSIONARE = [
    ROOT / "data",
    ROOT / "dist",
    ROOT / "downloads",
    ROOT / "runtime",
    ROOT / "demo",
]

CARTELLE_DA_ESCLUDERE = {
    "node_modules",
    ".git",
    ".venv",
    "__pycache__",
}

CAMPI_DOMANDA = [
    "domanda",
    "question",
    "testo",
    "text",
]

CAMPI_OPZIONI = [
    "opzioni",
    "options",
    "risposte",
    "answers",
]

CAMPI_RISPOSTA_CORRETTA = [
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

CAMPI_CATEGORIA = [
    "categoria",
    "category",
    "materia",
    "subject",
    "argomento",
    "topic",
]


def normalizza_testo(testo):
    testo = str(testo or "").lower()
    testo = re.sub(r"\s+", " ", testo)
    testo = re.sub(r"[^\w\sàèéìòù]", "", testo)
    return testo.strip()


def contiene_alias(testo, alias):
    testo_norm = normalizza_testo(testo)
    return any(alias_norm in testo_norm for alias_norm in alias)


def prendi_primo_valore(dizionario, campi):
    for campo in campi:
        if campo in dizionario:
            return dizionario[campo]
    return None


def normalizza_opzioni(opzioni_grezze):
    if isinstance(opzioni_grezze, list):
        opzioni = []

        for opzione in opzioni_grezze:
            if isinstance(opzione, dict):
                valore = (
                    opzione.get("testo")
                    or opzione.get("text")
                    or opzione.get("risposta")
                    or opzione.get("answer")
                    or opzione.get("label")
                    or ""
                )
                opzioni.append(str(valore).strip())
            else:
                opzioni.append(str(opzione).strip())

        return [opzione for opzione in opzioni if opzione]

    if isinstance(opzioni_grezze, dict):
        opzioni = []

        for lettera in ["A", "B", "C", "D", "a", "b", "c", "d"]:
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


def normalizza_risposta_corretta(risposta_grezza, opzioni):
    risposta = str(risposta_grezza or "").strip()

    if not risposta:
        return ""

    lettera = risposta.upper()

    if lettera in ["A", "B", "C", "D"]:
        indice = ord(lettera) - ord("A")
        return opzioni[indice] if indice < len(opzioni) else ""

    if risposta.isdigit():
        indice = int(risposta) - 1
        return opzioni[indice] if 0 <= indice < len(opzioni) else ""

    risposta_norm = normalizza_testo(risposta)

    for opzione in opzioni:
        if normalizza_testo(opzione) == risposta_norm:
            return opzione

    return risposta


def estrai_domande_da_json(contenuto):
    if isinstance(contenuto, list):
        return contenuto

    if isinstance(contenuto, dict):
        for chiave in [
            "domande",
            "questions",
            "quiz",
            "items",
            "data",
            "database",
        ]:
            valore = contenuto.get(chiave)
            if isinstance(valore, list):
                return valore

        liste_trovate = []

        for valore in contenuto.values():
            if isinstance(valore, list):
                liste_trovate.extend([
                    elemento
                    for elemento in valore
                    if isinstance(elemento, dict)
                ])

        return liste_trovate

    return []


def trova_file_json():
    file_json = []

    for cartella in CARTELLE_DA_SCANSIONARE:
        if not cartella.exists():
            continue

        for percorso in cartella.rglob("*.json"):
            parti = set(percorso.parts)

            if parti.intersection(CARTELLE_DA_ESCLUDERE):
                continue

            file_json.append(percorso)

    return sorted(set(file_json))


def riconosci_materia(percorso, domanda):
    testo_ricerca = " ".join([
        str(percorso.name),
        str(percorso.parent),
        str(prendi_primo_valore(domanda, CAMPI_CATEGORIA) or ""),
        str(domanda.get("id", "")),
    ])

    materie_trovate = []

    for materia, alias in MATERIE_DA_CONTROLLARE.items():
        if contiene_alias(testo_ricerca, alias):
            materie_trovate.append(materia)

    return materie_trovate


def valuta_domanda(percorso, domanda):
    problemi = []

    testo_domanda = prendi_primo_valore(domanda, CAMPI_DOMANDA)
    opzioni = normalizza_opzioni(prendi_primo_valore(domanda, CAMPI_OPZIONI))
    risposta = normalizza_risposta_corretta(
        prendi_primo_valore(domanda, CAMPI_RISPOSTA_CORRETTA),
        opzioni
    )
    spiegazione = prendi_primo_valore(domanda, CAMPI_SPIEGAZIONE)

    if not testo_domanda or len(str(testo_domanda).strip()) < 12:
        problemi.append("domanda mancante o troppo corta")

    if len(opzioni) != 4:
        problemi.append(f"opzioni non sono 4: {len(opzioni)}")

    if len(opzioni) == 4 and len(set(normalizza_testo(opzione) for opzione in opzioni)) < 4:
        problemi.append("opzioni duplicate o quasi identiche")

    if not risposta:
        problemi.append("risposta corretta mancante")

    if risposta and opzioni and risposta not in opzioni:
        problemi.append("risposta corretta non presente nelle opzioni")

    if not spiegazione or len(str(spiegazione).strip()) < 25:
        problemi.append("spiegazione mancante o troppo breve")

    opzioni_norm = [normalizza_testo(opzione) for opzione in opzioni]

    risposte_deboli = [
        "tutte le precedenti",
        "nessuna delle precedenti",
        "non lo so",
        "impossibile stabilirlo",
        "sempre",
        "mai",
    ]

    for opzione in opzioni_norm:
        if any(frase in opzione for frase in risposte_deboli):
            problemi.append("possibile opzione debole/generica")

    if len(opzioni) == 4:
        lunghezze = [len(opzione) for opzione in opzioni]

        if max(lunghezze) > 0 and min(lunghezze) > 0:
            if max(lunghezze) / min(lunghezze) >= 3:
                problemi.append("opzioni con lunghezze troppo sbilanciate")

    posizione_corretta = None

    if risposta in opzioni:
        posizione_corretta = ["A", "B", "C", "D"][opzioni.index(risposta)]

    return {
        "file": str(percorso.relative_to(ROOT)),
        "id": domanda.get("id", ""),
        "testo": str(testo_domanda or "").strip(),
        "opzioni": opzioni,
        "risposta": risposta,
        "posizione_corretta": posizione_corretta,
        "problemi": problemi,
    }


def main():
    print("----- AUDIT MOTORI SCIENTIFICI -----")

    file_json = trova_file_json()

    print(f"File JSON trovati: {len(file_json)}")

    risultati_per_materia = defaultdict(list)
    domande_globali = []

    for percorso in file_json:
        try:
            contenuto = json.loads(percorso.read_text(encoding="utf-8"))
        except Exception:
            continue

        domande = estrai_domande_da_json(contenuto)

        for domanda in domande:
            if not isinstance(domanda, dict):
                continue

            materie = riconosci_materia(percorso, domanda)

            if not materie:
                continue

            risultato = valuta_domanda(percorso, domanda)

            for materia in materie:
                risultati_per_materia[materia].append(risultato)

            domande_globali.append((materie, risultato))

    print("")

    for materia in MATERIE_DA_CONTROLLARE:
        risultati = risultati_per_materia[materia]

        print(f"===== {materia.upper()} =====")
        print(f"Domande trovate: {len(risultati)}")

        if not risultati:
            print("ATTENZIONE: nessuna domanda/motore trovato per questa materia.")
            print("")
            continue

        file_coinvolti = sorted(set(r["file"] for r in risultati))
        print("File coinvolti:")

        for file in file_coinvolti[:12]:
            print(f"- {file}")

        if len(file_coinvolti) > 12:
            print(f"- ... altri {len(file_coinvolti) - 12} file")

        conteggio_posizioni = Counter(
            r["posizione_corretta"]
            for r in risultati
            if r["posizione_corretta"]
        )

        print("Distribuzione posizione corretta originale:")
        print(dict(conteggio_posizioni))

        problemi = [
            r
            for r in risultati
            if r["problemi"]
        ]

        print(f"Domande con problemi tecnici: {len(problemi)}")

        for problema in problemi[:10]:
            print("")
            print(f"- File: {problema['file']}")
            print(f"  ID: {problema['id']}")
            print(f"  Domanda: {problema['testo'][:140]}")
            print(f"  Problemi: {', '.join(problema['problemi'])}")

        testi = [
            normalizza_testo(r["testo"])
            for r in risultati
            if r["testo"]
        ]

        duplicati = [
            testo
            for testo, quantita in Counter(testi).items()
            if quantita > 1
        ]

        print(f"Domande duplicate identiche: {len(duplicati)}")

        troppo_simili = []

        for indice_a in range(len(risultati)):
            testo_a = normalizza_testo(risultati[indice_a]["testo"])

            if not testo_a:
                continue

            for indice_b in range(indice_a + 1, len(risultati)):
                testo_b = normalizza_testo(risultati[indice_b]["testo"])

                if not testo_b:
                    continue

                similarita = SequenceMatcher(None, testo_a, testo_b).ratio()

                if similarita >= 0.88 and testo_a != testo_b:
                    troppo_simili.append((
                        similarita,
                        risultati[indice_a],
                        risultati[indice_b],
                    ))

        print(f"Domande troppo simili: {len(troppo_simili)}")

        for similarita, domanda_a, domanda_b in troppo_simili[:5]:
            print("")
            print(f"- Similarità: {similarita:.2f}")
            print(f"  A: {domanda_a['testo'][:120]}")
            print(f"  B: {domanda_b['testo'][:120]}")

        print("")

    print("----- RIEPILOGO FINALE -----")

    totale_materie_trovate = sum(
        1
        for materia in MATERIE_DA_CONTROLLARE
        if risultati_per_materia[materia]
    )

    totale_domande = sum(
        len(risultati_per_materia[materia])
        for materia in MATERIE_DA_CONTROLLARE
    )

    totale_problemi = sum(
        1
        for materia in MATERIE_DA_CONTROLLARE
        for risultato in risultati_per_materia[materia]
        if risultato["problemi"]
    )

    print(f"Motori/materie trovati: {totale_materie_trovate}/{len(MATERIE_DA_CONTROLLARE)}")
    print(f"Domande scientifiche trovate: {totale_domande}")
    print(f"Domande con problemi tecnici: {totale_problemi}")

    if totale_problemi == 0 and totale_materie_trovate == len(MATERIE_DA_CONTROLLARE):
        print("OK: i motori scientifici risultano presenti e tecnicamente puliti.")
    else:
        print("ATTENZIONE: alcuni motori vanno controllati o migliorati.")

    print("")
    print("Nota: questo audit controlla struttura, duplicati e segnali di qualità.")
    print("La qualità concettuale profonda va poi revisionata materia per materia.")


if __name__ == "__main__":
    main()
