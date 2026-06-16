import re


ERRORI_ACCENTI_SICURI = {
    "perche": "perché",
    "poiche": "poiché",
    "affinche": "affinché",
    "benche": "benché",
    "cioe": "cioè",
    "puo": "può",
    "piu": "più",
    "gia": "già",
    "cosi": "così",
    "qual'è": "qual è",
    "un'altro": "un altro",
    "un altra": "un'altra",
}

FORME_APOSTROFO_SOSPETTE = {
    "e'": "è",
    "E'": "È",
    "perche'": "perché",
    "puo'": "può",
    "piu'": "più",
    "cioe'": "cioè",
    "gia'": "già",
    "cosi'": "così",
}

PAROLE_INTERROGATIVE = [
    "quale",
    "quali",
    "che cosa",
    "cosa",
    "perché",
    "perche",
    "come",
    "quando",
    "dove",
    "quanto",
    "quanta",
    "quanti",
    "quante",
]


def normalizza_spazi(testo):
    if testo is None:
        return ""

    return str(testo).strip()


def parole(testo):
    return re.findall(r"\b[\wàèéìòù']+\b", testo.lower())


def contiene_interrogativa(testo):
    testo_basso = testo.strip().lower()

    return any(
        testo_basso.startswith(parola)
        for parola in PAROLE_INTERROGATIVE
    )


def finisce_con_placeholder_domanda(testo):
    """
    Riconosce casi in cui il punto interrogativo finale non è punteggiatura,
    ma il posto vuoto da completare.

    Esempi validi:
    - 4, 7, 10, 13, ?
    - EF → ?
    - forbici stanno a ?
    """
    testo = testo.strip()

    pattern = r"([:→,]|\bsta\s+a|\bstanno\s+a)\s+\?$"

    return re.search(pattern, testo, flags=re.IGNORECASE) is not None


def prepara_testo_per_controllo_punteggiatura(testo):
    """
    Se il testo termina con un placeholder tipo ' ?',
    lo togliamo dal controllo della punteggiatura.
    Così non viene scambiato per uno spazio scritto male.
    """
    if finisce_con_placeholder_domanda(testo):
        return re.sub(r"\s+\?$", "", testo.strip())

    return testo


def controlla_lingua_testo(testo, contesto="testo"):
    """
    Restituisce due liste:
    - errori_linguistici: problemi abbastanza sicuri da correggere
    - note_linguistiche: cose da controllare ma non bloccanti
    """
    errori = []
    note = []

    testo = normalizza_spazi(testo)

    if not testo:
        errori.append(f"{contesto}: testo vuoto")
        return errori, note

    testo_basso = testo.lower()
    testo_punteggiatura = prepara_testo_per_controllo_punteggiatura(testo)

    if "  " in testo:
        errori.append(f"{contesto}: contiene doppi spazi")

    if re.search(r"\s+[,.!?;:]", testo_punteggiatura):
        errori.append(f"{contesto}: contiene spazio prima della punteggiatura")

    if re.search(r"[,.!?;:][^\s\d\)\]»”'\"]", testo_punteggiatura):
        errori.append(f"{contesto}: manca spazio dopo la punteggiatura")

    for forma_errata, forma_corretta in ERRORI_ACCENTI_SICURI.items():
        pattern = r"\b" + re.escape(forma_errata) + r"\b"

        if re.search(pattern, testo_basso):
            errori.append(
                f"{contesto}: possibile errore ortografico “{forma_errata}”, meglio “{forma_corretta}”"
            )

    for forma_errata, forma_corretta in FORME_APOSTROFO_SOSPETTE.items():
        # Evita falsi positivi dentro parole inglesi tra apici, per esempio 'she'.
        # Deve segnalare e' solo quando è davvero una parola isolata scritta al posto di è.
        pattern = r"(?<![A-Za-zÀ-ÿ])" + re.escape(forma_errata) + r"(?![A-Za-zÀ-ÿ])"

        if re.search(pattern, testo):
            errori.append(
                f"{contesto}: apostrofo usato al posto dell’accento “{forma_errata}”, meglio “{forma_corretta}”"
            )

    if testo.count("(") != testo.count(")"):
        errori.append(f"{contesto}: parentesi non bilanciate")

    if testo.count('"') % 2 != 0:
        note.append(f"{contesto}: virgolette doppie forse non bilanciate")

    if testo.count("“") != testo.count("”"):
        note.append(f"{contesto}: virgolette tipografiche forse non bilanciate")

    numero_parole = len(parole(testo))

    if numero_parole > 45 and "," not in testo and ";" not in testo and "." not in testo:
        note.append(f"{contesto}: frase molto lunga senza punteggiatura interna")

    if len(testo) > 260:
        note.append(f"{contesto}: testo molto lungo, controllare leggibilità")

    # Il punto interrogativo obbligatorio vale solo per il testo della domanda.
    # Opzioni e spiegazioni possono iniziare con parole come "come", "quando", "perché"
    # senza essere domande vere.
    if (
        contesto == "domanda"
        and contiene_interrogativa(testo)
        and not testo.rstrip().endswith("?")
    ):
        errori.append(f"{contesto}: domanda interrogativa senza punto interrogativo finale")

    if testo.rstrip().endswith(".."):
        errori.append(f"{contesto}: punteggiatura finale anomala")

    if re.search(r"\b[aeiou]\s+[aeiou]\b", testo_basso):
        note.append(f"{contesto}: possibile frase poco fluida, controllare gli incontri vocalici")

    return sorted(set(errori)), sorted(set(note))


def controlla_lingua_domanda(domanda, opzioni, spiegazione=""):
    errori_totali = []
    note_totali = []

    errori, note = controlla_lingua_testo(domanda, "domanda")
    errori_totali.extend(errori)
    note_totali.extend(note)

    for indice, opzione in enumerate(opzioni):
        lettera = "ABCD"[indice] if indice < 4 else str(indice + 1)
        errori, note = controlla_lingua_testo(opzione, f"opzione {lettera}")
        errori_totali.extend(errori)
        note_totali.extend(note)

    if spiegazione:
        errori, note = controlla_lingua_testo(spiegazione, "spiegazione")
        errori_totali.extend(errori)
        note_totali.extend(note)

        if len(parole(spiegazione)) < 8:
            note_totali.append("spiegazione: forse troppo corta per essere davvero utile")

    return sorted(set(errori_totali)), sorted(set(note_totali))
