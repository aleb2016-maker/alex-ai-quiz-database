import json
import random
import shutil
import tempfile
import zipfile
from collections import Counter
from pathlib import Path


OPTION_KEYS = [
    "opzioni",
    "options",
    "risposte",
    "answers",
    "choices",
]

CORRECT_KEYS = [
    "risposta_corretta",
    "correct_answer",
    "correctAnswer",
    "correct",
    "answer",
    "soluzione",
    "opzione_corretta",
    "correct_option",
    "correctOption",
    "indice_risposta_corretta",
    "correct_index",
    "correctIndex",
]

PARALLEL_LIST_KEYS = [
    "immagini_opzioni",
    "option_images",
    "images",
    "spiegazioni_opzioni",
]

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def trova_lista_domande(dati):
    if isinstance(dati, list):
        return dati

    if isinstance(dati, dict):
        for chiave in ["questions", "domande", "quiz", "items", "data"]:
            if isinstance(dati.get(chiave), list):
                return dati[chiave]

    return []


def trova_chiave_opzioni(domanda):
    for chiave in OPTION_KEYS:
        valore = domanda.get(chiave)
        if isinstance(valore, list) and len(valore) >= 2:
            return chiave

    return None


def trova_risposta_corretta(domanda, opzioni):
    numero_opzioni = len(opzioni)

    for chiave in CORRECT_KEYS:
        if chiave not in domanda:
            continue

        valore = domanda[chiave]

        if isinstance(valore, int):
            if 0 <= valore < numero_opzioni:
                return chiave, opzioni[valore], "indice_zero"

            if 1 <= valore <= numero_opzioni:
                return chiave, opzioni[valore - 1], "indice_uno"

        if isinstance(valore, str):
            testo = valore.strip()

            if testo in opzioni:
                return chiave, testo, "testo"

            if testo.upper() in LETTERS[:numero_opzioni]:
                indice = LETTERS.index(testo.upper())
                return chiave, opzioni[indice], "lettera"

            if testo.isdigit():
                numero = int(testo)

                if 0 <= numero < numero_opzioni:
                    return chiave, opzioni[numero], "indice_zero_stringa"

                if 1 <= numero <= numero_opzioni:
                    return chiave, opzioni[numero - 1], "indice_uno_stringa"

    return None, None, None


def aggiorna_risposta_corretta(domanda, chiave, tipo, nuovo_indice, testo_corretta):
    if tipo == "testo":
        domanda[chiave] = testo_corretta

    elif tipo == "lettera":
        domanda[chiave] = LETTERS[nuovo_indice]

    elif tipo == "indice_zero":
        domanda[chiave] = nuovo_indice

    elif tipo == "indice_uno":
        domanda[chiave] = nuovo_indice + 1

    elif tipo == "indice_zero_stringa":
        domanda[chiave] = str(nuovo_indice)

    elif tipo == "indice_uno_stringa":
        domanda[chiave] = str(nuovo_indice + 1)


def bilancia_database_json(json_path):
    dati = json.loads(json_path.read_text(encoding="utf-8"))
    domande = trova_lista_domande(dati)

    domande_valide = []

    for domanda in domande:
        if not isinstance(domanda, dict):
            continue

        chiave_opzioni = trova_chiave_opzioni(domanda)

        if not chiave_opzioni:
            continue

        opzioni = domanda[chiave_opzioni]

        if not all(isinstance(opzione, str) for opzione in opzioni):
            continue

        chiave_corretta, testo_corretta, tipo_corretta = trova_risposta_corretta(
            domanda,
            opzioni,
        )

        if not chiave_corretta:
            continue

        domande_valide.append({
            "domanda": domanda,
            "chiave_opzioni": chiave_opzioni,
            "chiave_corretta": chiave_corretta,
            "testo_corretta": testo_corretta,
            "tipo_corretta": tipo_corretta,
        })

    if not domande_valide:
        return Counter()

    rng = random.Random(20260616)

    posizioni = [indice % 4 for indice in range(len(domande_valide))]
    rng.shuffle(posizioni)

    distribuzione = Counter()

    for info, posizione_target in zip(domande_valide, posizioni):
        domanda = info["domanda"]
        chiave_opzioni = info["chiave_opzioni"]
        chiave_corretta = info["chiave_corretta"]
        testo_corretta = info["testo_corretta"]
        tipo_corretta = info["tipo_corretta"]

        opzioni_originali = list(domanda[chiave_opzioni])

        elementi = []

        for indice, opzione in enumerate(opzioni_originali):
            elemento = {
                "opzione": opzione,
                "indice_originale": indice,
                "paralleli": {},
            }

            for chiave_parallela in PARALLEL_LIST_KEYS:
                valore_parallelo = domanda.get(chiave_parallela)

                if isinstance(valore_parallelo, list) and len(valore_parallelo) == len(opzioni_originali):
                    elemento["paralleli"][chiave_parallela] = valore_parallelo[indice]

            elementi.append(elemento)

        corretta = None
        sbagliate = []

        for elemento in elementi:
            if elemento["opzione"] == testo_corretta and corretta is None:
                corretta = elemento
            else:
                sbagliate.append(elemento)

        if corretta is None:
            continue

        rng.shuffle(sbagliate)

        posizione_finale = min(posizione_target, len(elementi) - 1)

        nuove = list(sbagliate)
        nuove.insert(posizione_finale, corretta)

        domanda[chiave_opzioni] = [elemento["opzione"] for elemento in nuove]

        for chiave_parallela in PARALLEL_LIST_KEYS:
            valore_parallelo = domanda.get(chiave_parallela)

            if isinstance(valore_parallelo, list) and len(valore_parallelo) == len(elementi):
                domanda[chiave_parallela] = [
                    elemento["paralleli"].get(chiave_parallela)
                    for elemento in nuove
                ]

        nuovo_indice = domanda[chiave_opzioni].index(testo_corretta)

        aggiorna_risposta_corretta(
            domanda,
            chiave_corretta,
            tipo_corretta,
            nuovo_indice,
            testo_corretta,
        )

        distribuzione[LETTERS[nuovo_indice]] += 1

    json_path.write_text(
        json.dumps(dati, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return distribuzione


def bilancia_zip(zip_path):
    with tempfile.TemporaryDirectory() as tmp_nome:
        tmp = Path(tmp_nome)
        estratta = tmp / "estratta"
        nuovo_zip = tmp / "nuovo.zip"

        estratta.mkdir()

        with zipfile.ZipFile(zip_path, "r") as archivio:
            archivio.extractall(estratta)

        distribuzione_totale = Counter()

        for json_path in estratta.rglob("database_quiz.json"):
            distribuzione_totale.update(bilancia_database_json(json_path))

        if not distribuzione_totale:
            return Counter()

        with zipfile.ZipFile(nuovo_zip, "w", zipfile.ZIP_DEFLATED) as archivio:
            for file in estratta.rglob("*"):
                if file.is_file():
                    archivio.write(file, file.relative_to(estratta))

        shutil.copy2(nuovo_zip, zip_path)

        return distribuzione_totale


def main():
    import sys

    percorsi = [Path(arg) for arg in sys.argv[1:]]

    if not percorsi:
        percorsi = [Path("downloads")]

    distribuzione_finale = Counter()

    for percorso in percorsi:
        if not percorso.exists():
            continue

        if percorso.is_file() and percorso.suffix == ".zip":
            distribuzione = bilancia_zip(percorso)
            distribuzione_finale.update(distribuzione)

            if distribuzione:
                print(f"Bilanciato ZIP: {percorso} -> {dict(distribuzione)}")

        elif percorso.is_dir():
            for zip_path in sorted(percorso.rglob("*.zip")):
                distribuzione = bilancia_zip(zip_path)
                distribuzione_finale.update(distribuzione)

                if distribuzione:
                    print(f"Bilanciato ZIP: {zip_path} -> {dict(distribuzione)}")

    print()
    print("Distribuzione totale:", dict(distribuzione_finale))


if __name__ == "__main__":
    main()
