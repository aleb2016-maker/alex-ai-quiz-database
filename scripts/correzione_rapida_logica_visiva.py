import json
import re
from pathlib import Path

FILE = Path("data/logica/logica_visiva.json")

CORREZIONI_MANUALI = {
    "LOG-VIS-AV-0003": "La risposta corretta è il triangolo pieno perché la forma resta un triangolo e il riempimento passa dalla figura non piena alla figura piena.",
    "LOG-VIS-FAC-0008": "La risposta corretta è il triangolo verde con 3 pallini perché la forma resta un triangolo, il colore resta verde e gli oggetti interni aumentano fino a 3 pallini.",
    "LOG-VIS-INT-0005": "La risposta corretta è il triangolo verde con 3 pallini perché la forma finale è un triangolo, il colore finale è verde e gli oggetti interni sono 3 pallini.",
    "LOG-VIS-AV-0004": "La risposta corretta è il triangolo blu con 3 linee perché la forma resta un triangolo, il colore finale è blu e gli elementi interni aumentano fino a 3 linee.",
    "LOG-VIS-AV-0005": "La risposta corretta è l'esagono con 3 contorni e puntini perché la forma finale è un esagono con 6 lati, i contorni aumentano fino a 3 e sono presenti i puntini interni.",
    "LOG-VIS-AV-0007": "La risposta corretta è il triangolo verde con 4 stelle perché la forma finale è un triangolo, il colore finale è verde e gli oggetti interni arrivano a 4 stelle.",
}

PAROLE_VIETATE = [
    "riga",
    "righe",
    "colonna",
    "colonne",
    "le altre risposte",
    "le altre figure",
    "le altre opzioni",
]

FRASI_TAGLIO = [
    r"Le altre risposte[^.]*\.",
    r"Le altre figure[^.]*\.",
    r"Le altre opzioni[^.]*\.",
]

FORME = {
    "triangolo": 3,
    "quadrato": 4,
    "rettangolo": 4,
    "pentagono": 5,
    "esagono": 6,
    "cerchio": None,
    "ovale": None,
}

COLORI = [
    "azzurro",
    "blu",
    "rosso",
    "verde",
    "giallo",
    "arancione",
    "viola",
    "nero",
    "bianco",
    "grigio",
    "rosa",
]

OGGETTI = [
    "pallini",
    "pallino",
    "punti",
    "punto",
    "linee",
    "linea",
    "stelle",
    "stella",
    "cerchi",
    "cerchio",
    "triangoli",
    "triangolo",
    "quadrati",
    "quadrato",
    "contorni",
    "contorno",
    "puntini",
    "puntino",
]


def carica_domande():
    with open(FILE, "r", encoding="utf-8") as f:
        contenuto = json.load(f)

    if isinstance(contenuto, list):
        return contenuto, None, contenuto

    for chiave in ["domande", "questions", "items", "quiz"]:
        if isinstance(contenuto.get(chiave), list):
            return contenuto[chiave], chiave, contenuto

    raise SystemExit("Formato JSON non riconosciuto.")


def salva_domande(domande, chiave, contenuto):
    if chiave is None:
        dati = domande
    else:
        contenuto[chiave] = domande
        dati = contenuto

    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(dati, f, ensure_ascii=False, indent=2)


def testo_opzione(opzione):
    if isinstance(opzione, dict):
        return str(
            opzione.get("testo")
            or opzione.get("text")
            or opzione.get("risposta")
            or opzione.get("value")
            or opzione.get("label")
            or ""
        ).strip()

    return str(opzione).strip()


def opzioni(domanda):
    return (
        domanda.get("opzioni")
        or domanda.get("options")
        or domanda.get("risposte")
        or domanda.get("answers")
        or []
    )


def risposta_corretta(domanda):
    return str(
        domanda.get("risposta_corretta")
        or domanda.get("correct_answer")
        or domanda.get("correct")
        or domanda.get("answer")
        or domanda.get("soluzione")
        or ""
    ).strip()


def testo_risposta_corretta(domanda):
    risposta = risposta_corretta(domanda)
    lista_opzioni = opzioni(domanda)

    if isinstance(lista_opzioni, list):
        for indice, opzione in enumerate(lista_opzioni):
            lettera = chr(65 + indice)
            testo = testo_opzione(opzione)

            corretta_esplicita = False
            if isinstance(opzione, dict):
                corretta_esplicita = (
                    opzione.get("corretta") is True
                    or opzione.get("correct") is True
                    or opzione.get("is_correct") is True
                )

            if corretta_esplicita or risposta.upper() == lettera or risposta == testo:
                return testo

    if isinstance(lista_opzioni, dict):
        for lettera, opzione in lista_opzioni.items():
            testo = testo_opzione(opzione)

            corretta_esplicita = False
            if isinstance(opzione, dict):
                corretta_esplicita = (
                    opzione.get("corretta") is True
                    or opzione.get("correct") is True
                    or opzione.get("is_correct") is True
                )

            if corretta_esplicita or risposta.upper() == str(lettera).upper() or risposta == testo:
                return testo

    return risposta


def trova_forma(testo):
    testo = testo.lower()
    for forma in FORME:
        if forma in testo:
            return forma
    return ""


def trova_colore(testo):
    testo = testo.lower()
    for colore in COLORI:
        if colore in testo:
            return colore
    return ""


def trova_oggetti(testo):
    testo = testo.lower()

    match = re.search(
        r"\b(\d+)\s+(pallini|pallino|punti|punto|linee|linea|stelle|stella|cerchi|cerchio|triangoli|triangolo|quadrati|quadrato|contorni|contorno|puntini|puntino)\b",
        testo
    )

    if match:
        return match.group(1), match.group(2)

    return "", ""


def pulisci_frasi_inutili(testo):
    nuovo = testo

    for pattern in FRASI_TAGLIO:
        nuovo = re.sub(pattern, "", nuovo, flags=re.IGNORECASE)

    nuovo = re.sub(r"\s+", " ", nuovo).strip()

    return nuovo


def crea_spiegazione_da_opzione(domanda):
    testo_finale = testo_risposta_corretta(domanda)
    forma = trova_forma(testo_finale)
    colore = trova_colore(testo_finale)
    numero_oggetti, tipo_oggetti = trova_oggetti(testo_finale)

    parti = []

    if forma:
        lati = FORME.get(forma)
        if lati:
            parti.append(f"la forma finale è un {forma} con {lati} lati")
        else:
            parti.append(f"la forma finale è un {forma}")

    if colore:
        parti.append(f"il colore finale è {colore}")

    if numero_oggetti:
        parti.append(f"gli oggetti interni sono {numero_oggetti} {tipo_oggetti}")

    if parti:
        return f"La risposta corretta è {testo_finale} perché " + ", ".join(parti) + "."

    return f"La risposta corretta è {testo_finale} perché descrive in modo coerente la figura finale richiesta dalla trasformazione."


def contiene_vietate(testo):
    testo = testo.lower()
    return any(parola in testo for parola in PAROLE_VIETATE)


def spiegazione_debole(testo):
    testo_basso = testo.lower()

    if contiene_vietate(testo_basso):
        return True

    if "rispetta forma" in testo_basso:
        return True

    if "forma/colore" in testo_basso:
        return True

    if len(testo_basso.strip()) < 75:
        return True

    return False


def main():
    domande, chiave, contenuto = carica_domande()

    corrette = 0
    ids_corretti = []

    for indice, domanda in enumerate(domande, start=1):
        id_domanda = domanda.get("id", f"LOG-VIS-{indice:04d}")
        spiegazione = str(domanda.get("spiegazione", "")).strip()

        if id_domanda in CORREZIONI_MANUALI:
            domanda["spiegazione"] = CORREZIONI_MANUALI[id_domanda]
            corrette += 1
            ids_corretti.append(id_domanda)
            continue

        spiegazione_pulita = pulisci_frasi_inutili(spiegazione)

        if spiegazione_debole(spiegazione_pulita):
            domanda["spiegazione"] = crea_spiegazione_da_opzione(domanda)
            corrette += 1
            ids_corretti.append(id_domanda)
        elif spiegazione_pulita != spiegazione:
            domanda["spiegazione"] = spiegazione_pulita
            corrette += 1
            ids_corretti.append(id_domanda)

    salva_domande(domande, chiave, contenuto)

    print("===== CORREZIONE RAPIDA LOGICA VISIVA =====")
    print(f"Spiegazioni corrette: {corrette}")
    print("ID corretti:")
    for id_domanda in ids_corretti:
        print(f"- {id_domanda}")
    print()
    print("OK: corrette spiegazioni con riga/colonna, frasi generiche e frasi inutili.")


if __name__ == "__main__":
    main()
