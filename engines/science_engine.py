import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path


CATEGORIA_PRINCIPALE = "scienze"

LIVELLI_VALIDI = ["facile", "intermedio", "avanzato"]

DIFFICOLTA_PER_LIVELLO = {
    "facile": 1,
    "intermedio": 2,
    "avanzato": 3,
}

SIGLA_LIVELLO = {
    "facile": "FAC",
    "intermedio": "INT",
    "avanzato": "AV",
}

SOTTOCATEGORIE_VALIDE = [
    "biologia",
    "chimica_base",
    "fisica_base",
    "astronomia",
    "scienze_della_terra",
    "metodo_scientifico",
    "ecologia",
    "corpo_umano",
    "fisica_quantistica_base",
]

PAROLE_CHIAVE_SOTTOCATEGORIE = {
    "biologia": [
        "cellula",
        "cellule",
        "dna",
        "rna",
        "gene",
        "geni",
        "proteina",
        "proteine",
        "evoluzione",
        "organismo",
        "organismi",
        "fotosintesi",
        "mitocondrio",
        "mitocondri",
        "membrana",
        "nucleo",
        "ribosoma",
        "cloroplasto",
    ],
    "chimica_base": [
        "atomo",
        "atomi",
        "molecola",
        "molecole",
        "ione",
        "ioni",
        "legame",
        "legami",
        "ph",
        "acido",
        "base",
        "reazione",
        "elettroni",
        "protoni",
        "neutroni",
        "elemento",
        "composto",
        "ossidazione",
        "riduzione",
    ],
    "fisica_base": [
        "forza",
        "energia",
        "massa",
        "velocità",
        "accelerazione",
        "lavoro",
        "potenza",
        "calore",
        "temperatura",
        "pressione",
        "newton",
        "joule",
        "watt",
        "moto",
        "gravità",
    ],
    "astronomia": [
        "pianeta",
        "pianeti",
        "stella",
        "stelle",
        "galassia",
        "galassie",
        "orbita",
        "satellite",
        "sole",
        "luna",
        "sistema solare",
        "asteroide",
        "cometa",
        "gravità",
        "anno luce",
    ],
    "scienze_della_terra": [
        "terra",
        "vulcano",
        "vulcani",
        "terremoto",
        "terremoti",
        "placche",
        "tettonica",
        "roccia",
        "rocce",
        "atmosfera",
        "clima",
        "erosione",
        "magma",
        "crosta",
        "mantello",
    ],
    "metodo_scientifico": [
        "ipotesi",
        "esperimento",
        "osservazione",
        "misura",
        "dati",
        "variabile",
        "controllo",
        "teoria",
        "legge",
        "verifica",
        "risultato",
        "conclusione",
    ],
    "ecologia": [
        "ecosistema",
        "ecosistemi",
        "habitat",
        "catena alimentare",
        "biodiversità",
        "specie",
        "popolazione",
        "produttori",
        "consumatori",
        "decompositori",
        "ambiente",
        "nicchia",
    ],
    "corpo_umano": [
        "cuore",
        "polmoni",
        "sangue",
        "cervello",
        "neuroni",
        "apparato",
        "digestione",
        "respirazione",
        "muscoli",
        "ossa",
        "organo",
        "organi",
        "intestino",
        "fegato",
    ],
    "fisica_quantistica_base": [
        "quanto",
        "quanti",
        "fotone",
        "fotoni",
        "elettrone",
        "elettroni",
        "orbitale",
        "probabilità",
        "indeterminazione",
        "sovrapposizione",
        "misura quantistica",
        "energia quantizzata",
        "dualismo",
    ],
}

# Gruppi di concetti vicini: servono per capire se un distrattore è veramente plausibile.
# Esempio: mitocondrio e cloroplasto sono entrambi organelli, quindi cloroplasto può essere
# un distrattore forte se la risposta corretta è mitocondrio.
FAMIGLIE_CONCETTUALI = [
    {
        "nome": "organelli_cellulari",
        "termini": [
            "mitocondrio",
            "mitocondri",
            "cloroplasto",
            "cloroplasti",
            "ribosoma",
            "ribosomi",
            "nucleo",
            "membrana cellulare",
            "apparato di golgi",
            "reticolo endoplasmatico",
        ],
    },
    {
        "nome": "molecole_biologiche",
        "termini": [
            "dna",
            "rna",
            "proteina",
            "proteine",
            "enzima",
            "enzimi",
            "glucosio",
            "lipide",
            "lipidi",
            "carboidrato",
            "carboidrati",
        ],
    },
    {
        "nome": "particelle_atomiche",
        "termini": [
            "protone",
            "protoni",
            "neutrone",
            "neutroni",
            "elettrone",
            "elettroni",
            "ione",
            "ioni",
            "isotopo",
            "isotopi",
        ],
    },
    {
        "nome": "grandezze_fisiche",
        "termini": [
            "forza",
            "energia",
            "lavoro",
            "potenza",
            "massa",
            "peso",
            "velocità",
            "accelerazione",
            "pressione",
            "temperatura",
            "calore",
        ],
    },
    {
        "nome": "unita_fisiche",
        "termini": [
            "newton",
            "joule",
            "watt",
            "pascal",
            "kelvin",
            "metro al secondo",
            "chilogrammo",
            "ampere",
            "volt",
        ],
    },
    {
        "nome": "corpi_celesti",
        "termini": [
            "pianeta",
            "stella",
            "satellite",
            "asteroide",
            "cometa",
            "galassia",
            "nebulosa",
            "buco nero",
        ],
    },
    {
        "nome": "struttura_terra",
        "termini": [
            "crosta",
            "mantello",
            "nucleo terrestre",
            "litosfera",
            "atmosfera",
            "idrosfera",
            "biosfera",
        ],
    },
    {
        "nome": "metodo_scientifico",
        "termini": [
            "ipotesi",
            "teoria",
            "legge scientifica",
            "esperimento",
            "osservazione",
            "variabile",
            "campione di controllo",
        ],
    },
]

RISPOSTE_VIETATE = [
    "tutte le precedenti",
    "nessuna delle precedenti",
    "tutte le risposte",
    "nessuna risposta",
]

PAROLE_ASSOLUTE_RISCHIOSE = [
    "sempre",
    "mai",
    "tutti",
    "nessuno",
    "qualsiasi",
    "impossibile",
    "garantisce",
    "garantito",
]

PAROLE_TROPPO_GENERICHE = [
    "cosa",
    "qualcosa",
    "elemento",
    "oggetto",
    "sostanza",
    "fenomeno",
    "processo",
]


def pulisci_testo(testo):
    return str(testo or "").strip()


def testo_minuscolo(testo):
    return pulisci_testo(testo).lower()


def normalizza_spazi(testo):
    return re.sub(r"\s+", " ", pulisci_testo(testo))


def rimuovi_prefisso_lettera(testo):
    return re.sub(r"^[A-D][\)\.\-:]\s*", "", pulisci_testo(testo), flags=re.I)


def normalizza_livello(livello):
    livello = testo_minuscolo(livello)

    conversioni = {
        "base": "facile",
        "principiante": "facile",
        "medio": "intermedio",
        "media": "intermedio",
        "difficile": "avanzato",
        "alto": "avanzato",
    }

    livello = conversioni.get(livello, livello)

    if livello not in LIVELLI_VALIDI:
        return "intermedio"

    return livello


def normalizza_sottocategoria(sottocategoria, testo_completo):
    sottocategoria = testo_minuscolo(sottocategoria)
    sottocategoria = sottocategoria.replace(" ", "_")
    sottocategoria = sottocategoria.replace("-", "_")

    alias = {
        "chimica": "chimica_base",
        "fisica": "fisica_base",
        "scienze_terra": "scienze_della_terra",
        "terra": "scienze_della_terra",
        "umano": "corpo_umano",
        "anatomia": "corpo_umano",
        "quantistica": "fisica_quantistica_base",
        "fisica_quantistica": "fisica_quantistica_base",
    }

    sottocategoria = alias.get(sottocategoria, sottocategoria)

    if sottocategoria in SOTTOCATEGORIE_VALIDE:
        return sottocategoria

    testo = testo_minuscolo(testo_completo)

    punteggi = {}

    for nome_sottocategoria, parole_chiave in PAROLE_CHIAVE_SOTTOCATEGORIE.items():
        punteggio = 0

        for parola in parole_chiave:
            if parola in testo:
                punteggio += 1

        if punteggio > 0:
            punteggi[nome_sottocategoria] = punteggio

    if punteggi:
        return max(punteggi, key=punteggi.get)

    return "metodo_scientifico"


def normalizza_opzioni(opzioni_grezze):
    if isinstance(opzioni_grezze, dict):
        opzioni = []

        for lettera in ["A", "B", "C", "D"]:
            valore = (
                opzioni_grezze.get(lettera)
                or opzioni_grezze.get(lettera.lower())
                or ""
            )

            testo = rimuovi_prefisso_lettera(valore)

            if testo:
                opzioni.append(testo)

        return opzioni

    if not isinstance(opzioni_grezze, list):
        return []

    opzioni = []

    for opzione in opzioni_grezze:
        if isinstance(opzione, str):
            testo = opzione
        elif isinstance(opzione, dict):
            testo = (
                opzione.get("testo")
                or opzione.get("risposta")
                or opzione.get("label")
                or opzione.get("value")
                or ""
            )
        else:
            testo = ""

        testo = rimuovi_prefisso_lettera(testo)

        if testo:
            opzioni.append(testo)

    return opzioni


def normalizza_risposta_corretta(risposta_grezza, opzioni):
    if isinstance(risposta_grezza, int):
        if 0 <= risposta_grezza <= 3:
            return opzioni[risposta_grezza]
        if 1 <= risposta_grezza <= 4:
            return opzioni[risposta_grezza - 1]

    if isinstance(risposta_grezza, dict):
        risposta_grezza = (
            risposta_grezza.get("testo")
            or risposta_grezza.get("risposta")
            or risposta_grezza.get("lettera")
            or ""
        )

    risposta = pulisci_testo(risposta_grezza)

    if re.fullmatch(r"[A-D]", risposta, flags=re.I):
        indice = ord(risposta.upper()) - ord("A")
        if 0 <= indice < len(opzioni):
            return opzioni[indice]

    match_lettera = re.match(r"^([A-D])[\)\.\-:]", risposta, flags=re.I)

    if match_lettera:
        indice = ord(match_lettera.group(1).upper()) - ord("A")
        if 0 <= indice < len(opzioni):
            return opzioni[indice]

    risposta_pulita = rimuovi_prefisso_lettera(risposta)

    for opzione in opzioni:
        if testo_minuscolo(opzione) == testo_minuscolo(risposta_pulita):
            return opzione

    return risposta_pulita


def crea_id_scienze(indice, livello):
    sigla = SIGLA_LIVELLO.get(livello, "INT")
    return f"SCI-{sigla}-{indice:04d}"


def similarita(testo_a, testo_b):
    return SequenceMatcher(
        None,
        testo_minuscolo(testo_a),
        testo_minuscolo(testo_b),
    ).ratio()


def contiene_termine(testo, termine):
    testo = testo_minuscolo(testo)
    termine = testo_minuscolo(termine)

    return re.search(rf"\b{re.escape(termine)}\b", testo) is not None


def trova_famiglie_concettuali(testo):
    famiglie = set()
    testo = testo_minuscolo(testo)

    for famiglia in FAMIGLIE_CONCETTUALI:
        for termine in famiglia["termini"]:
            if termine in testo:
                famiglie.add(famiglia["nome"])

    return famiglie


def punteggio_vicinanza_concettuale(opzione, risposta_corretta, domanda, spiegazione):
    """
    Restituisce un punteggio da 0 a 1.
    Più è alto, più l'opzione sbagliata sembra un distrattore forte.
    """
    opzione = pulisci_testo(opzione)
    risposta_corretta = pulisci_testo(risposta_corretta)

    if not opzione or not risposta_corretta:
        return 0.0

    if testo_minuscolo(opzione) == testo_minuscolo(risposta_corretta):
        return 0.0

    punteggio = 0.0

    # Somiglianza testuale: utile per risposte simili, ma non basta.
    punteggio += min(similarita(opzione, risposta_corretta), 0.45)

    famiglie_opzione = trova_famiglie_concettuali(opzione)
    famiglie_corretta = trova_famiglie_concettuali(risposta_corretta)

    if famiglie_opzione and famiglie_corretta:
        intersezione = famiglie_opzione.intersection(famiglie_corretta)

        if intersezione:
            punteggio += 0.35

    testo_contesto = testo_minuscolo(f"{domanda} {spiegazione}")

    # Se il distrattore appartiene allo stesso campo della domanda, è più plausibile.
    for sottocategoria, parole in PAROLE_CHIAVE_SOTTOCATEGORIE.items():
        parole_nel_contesto = any(parola in testo_contesto for parola in parole)
        parole_nell_opzione = any(parola in testo_minuscolo(opzione) for parola in parole)
        parole_nella_corretta = any(parola in testo_minuscolo(risposta_corretta) for parola in parole)

        if parole_nel_contesto and parole_nell_opzione and parole_nella_corretta:
            punteggio += 0.15
            break

    # Le opzioni con lunghezza simile sono spesso distrattori migliori.
    lunghezza_corretta = len(risposta_corretta)
    lunghezza_opzione = len(opzione)

    if lunghezza_corretta > 0:
        rapporto_lunghezza = min(lunghezza_opzione, lunghezza_corretta) / max(
            lunghezza_opzione,
            lunghezza_corretta,
        )

        if rapporto_lunghezza >= 0.55:
            punteggio += 0.10

    return min(punteggio, 1.0)


def scegli_distrattore_forte(domanda):
    opzioni = domanda.get("opzioni", [])
    risposta_corretta = domanda.get("risposta_corretta", "")
    testo_domanda = domanda.get("domanda", "")
    spiegazione = domanda.get("spiegazione", "")

    candidati = []

    for opzione in opzioni:
        if opzione == risposta_corretta:
            continue

        punteggio = punteggio_vicinanza_concettuale(
            opzione,
            risposta_corretta,
            testo_domanda,
            spiegazione,
        )

        candidati.append((punteggio, opzione))

    if not candidati:
        return "", 0.0

    candidati.sort(reverse=True, key=lambda elemento: elemento[0])

    return candidati[0][1], round(candidati[0][0], 2)


def genera_motivo_distrattore(distrattore, risposta_corretta):
    return (
        f"È un distrattore plausibile perché è collegato allo stesso argomento "
        f"della risposta corretta, ma non identifica precisamente il concetto richiesto. "
        f"La risposta corretta resta '{risposta_corretta}', non '{distrattore}'."
    )


def calcola_punteggio_qualita(domanda):
    punteggio = 100

    testo_domanda = pulisci_testo(domanda.get("domanda"))
    spiegazione = pulisci_testo(domanda.get("spiegazione"))
    opzioni = domanda.get("opzioni", [])
    risposta_corretta = domanda.get("risposta_corretta", "")
    distrattore_forte = domanda.get("distrattore_forte", "")
    punteggio_distrattore = float(domanda.get("punteggio_distrattore_forte", 0))

    if len(testo_domanda) < 35:
        punteggio -= 10

    if len(spiegazione) < 80:
        punteggio -= 15

    if not distrattore_forte:
        punteggio -= 20

    if punteggio_distrattore < 0.35:
        punteggio -= 20
    elif punteggio_distrattore < 0.50:
        punteggio -= 10

    lunghezze = [len(opzione) for opzione in opzioni if opzione]

    if lunghezze and max(lunghezze) > min(lunghezze) * 3:
        punteggio -= 10

    if any(testo_minuscolo(opzione) in RISPOSTE_VIETATE for opzione in opzioni):
        punteggio -= 25

    if risposta_corretta not in opzioni:
        punteggio -= 50

    return max(punteggio, 0)


def estrai_domande(dati):
    if isinstance(dati, list):
        return dati

    if isinstance(dati, dict):
        for chiave in ["quiz", "domande", "questions", "items"]:
            valore = dati.get(chiave)
            if isinstance(valore, list):
                return valore

    return []


def normalizza_domanda_scienze(domanda_grezza, indice):
    testo_domanda = normalizza_spazi(
        domanda_grezza.get("domanda")
        or domanda_grezza.get("question")
        or domanda_grezza.get("testo")
        or ""
    )

    livello = normalizza_livello(
        domanda_grezza.get("livello")
        or domanda_grezza.get("difficolta")
        or domanda_grezza.get("difficoltà")
        or "intermedio"
    )

    opzioni = normalizza_opzioni(
        domanda_grezza.get("opzioni")
        or domanda_grezza.get("risposte")
        or domanda_grezza.get("options")
        or []
    )

    risposta_corretta = normalizza_risposta_corretta(
        domanda_grezza.get("risposta_corretta")
        or domanda_grezza.get("rispostaCorretta")
        or domanda_grezza.get("correct_answer")
        or domanda_grezza.get("corretta")
        or domanda_grezza.get("correct"),
        opzioni,
    )

    spiegazione = normalizza_spazi(
        domanda_grezza.get("spiegazione")
        or domanda_grezza.get("explanation")
        or ""
    )

    testo_completo = " ".join(
        [testo_domanda, spiegazione] + opzioni
    )

    sottocategoria = normalizza_sottocategoria(
        domanda_grezza.get("sottocategoria")
        or domanda_grezza.get("sotto_argomento")
        or domanda_grezza.get("argomento")
        or "",
        testo_completo,
    )

    tags = domanda_grezza.get("tags")

    if not isinstance(tags, list):
        tags = [sottocategoria, "scienze"]

    distrattore_forte = normalizza_spazi(
        domanda_grezza.get("distrattore_forte")
        or domanda_grezza.get("strong_distractor")
        or ""
    )

    motivo_distrattore_forte = normalizza_spazi(
        domanda_grezza.get("motivo_distrattore_forte")
        or domanda_grezza.get("strong_distractor_reason")
        or ""
    )

    domanda_normalizzata = {
        "id": domanda_grezza.get("id") or crea_id_scienze(indice, livello),
        "categoria": CATEGORIA_PRINCIPALE,
        "sottocategoria": sottocategoria,
        "livello": livello,
        "domanda": testo_domanda,
        "opzioni": opzioni,
        "risposta_corretta": risposta_corretta,
        "spiegazione": spiegazione,
        "tags": tags,
        "difficolta": DIFFICOLTA_PER_LIVELLO[livello],
    }

    # Se il JSON non ha già il distrattore forte, il motore prova a individuarlo.
    if distrattore_forte:
        distrattore_forte = rimuovi_prefisso_lettera(distrattore_forte)
        punteggio_distrattore = punteggio_vicinanza_concettuale(
            distrattore_forte,
            risposta_corretta,
            testo_domanda,
            spiegazione,
        )
    else:
        distrattore_forte, punteggio_distrattore = scegli_distrattore_forte(
            domanda_normalizzata
        )

    if distrattore_forte:
        domanda_normalizzata["distrattore_forte"] = distrattore_forte
        domanda_normalizzata["punteggio_distrattore_forte"] = round(
            punteggio_distrattore,
            2,
        )

    if not motivo_distrattore_forte and distrattore_forte:
        motivo_distrattore_forte = genera_motivo_distrattore(
            distrattore_forte,
            risposta_corretta,
        )

    if motivo_distrattore_forte:
        domanda_normalizzata["motivo_distrattore_forte"] = motivo_distrattore_forte

    domanda_normalizzata["qualita"] = calcola_punteggio_qualita(
        domanda_normalizzata
    )

    return domanda_normalizzata


def valida_domanda_scienze(domanda, strict_distractors=False):
    errori = []
    avvisi = []

    id_domanda = domanda.get("id", "ID_MANCANTE")

    campi_obbligatori = [
        "id",
        "categoria",
        "sottocategoria",
        "livello",
        "domanda",
        "opzioni",
        "risposta_corretta",
        "spiegazione",
        "tags",
        "difficolta",
    ]

    for campo in campi_obbligatori:
        if campo not in domanda:
            errori.append(f"{id_domanda}: manca il campo '{campo}'.")

    if domanda.get("categoria") != CATEGORIA_PRINCIPALE:
        errori.append(
            f"{id_domanda}: categoria non valida. Deve essere 'scienze'."
        )

    if domanda.get("sottocategoria") not in SOTTOCATEGORIE_VALIDE:
        errori.append(
            f"{id_domanda}: sottocategoria non valida: {domanda.get('sottocategoria')}"
        )

    livello = domanda.get("livello")

    if livello not in LIVELLI_VALIDI:
        errori.append(f"{id_domanda}: livello non valido: {livello}")

    difficolta_attesa = DIFFICOLTA_PER_LIVELLO.get(livello)

    if domanda.get("difficolta") != difficolta_attesa:
        errori.append(
            f"{id_domanda}: difficoltà non coerente con il livello."
        )

    testo_domanda = pulisci_testo(domanda.get("domanda"))

    if len(testo_domanda) < 25:
        errori.append(f"{id_domanda}: domanda troppo corta o poco chiara.")

    if any(parola in testo_minuscolo(testo_domanda) for parola in PAROLE_TROPPO_GENERICHE):
        avvisi.append(
            f"{id_domanda}: la domanda usa parole generiche. Controlla se è abbastanza precisa."
        )

    opzioni = domanda.get("opzioni")

    if not isinstance(opzioni, list):
        errori.append(f"{id_domanda}: opzioni deve essere una lista.")
        return errori, avvisi

    if len(opzioni) != 4:
        errori.append(f"{id_domanda}: servono esattamente 4 opzioni.")

    opzioni_pulite = [pulisci_testo(opzione) for opzione in opzioni]

    if len(set(testo_minuscolo(opzione) for opzione in opzioni_pulite)) != len(opzioni_pulite):
        errori.append(f"{id_domanda}: ci sono opzioni duplicate.")

    for opzione in opzioni_pulite:
        if len(opzione) < 3:
            errori.append(f"{id_domanda}: una opzione è troppo corta.")

        if testo_minuscolo(opzione) in RISPOSTE_VIETATE:
            errori.append(
                f"{id_domanda}: evita risposte tipo 'tutte le precedenti' o 'nessuna'."
            )

    risposta_corretta = pulisci_testo(domanda.get("risposta_corretta"))

    if risposta_corretta not in opzioni_pulite:
        errori.append(
            f"{id_domanda}: risposta_corretta non è presente tra le opzioni."
        )

    spiegazione = pulisci_testo(domanda.get("spiegazione"))

    if len(spiegazione) < 50:
        errori.append(
            f"{id_domanda}: spiegazione troppo breve. Deve chiarire perché la risposta è corretta."
        )

    if len(spiegazione) < 90:
        avvisi.append(
            f"{id_domanda}: spiegazione un po' breve. Meglio aggiungere il perché scientifico."
        )

    distrattore_forte = pulisci_testo(domanda.get("distrattore_forte"))
    punteggio_distrattore = float(domanda.get("punteggio_distrattore_forte", 0))

    if not distrattore_forte:
        messaggio = f"{id_domanda}: manca il distrattore forte."

        if strict_distractors:
            errori.append(messaggio)
        else:
            avvisi.append(messaggio)

    else:
        if distrattore_forte not in opzioni_pulite:
            messaggio = (
                f"{id_domanda}: il distrattore forte deve essere una delle 4 opzioni."
            )

            if strict_distractors:
                errori.append(messaggio)
            else:
                avvisi.append(messaggio)

        if distrattore_forte == risposta_corretta:
            errori.append(
                f"{id_domanda}: il distrattore forte non può essere la risposta corretta."
            )

        if punteggio_distrattore < 0.30:
            messaggio = (
                f"{id_domanda}: distrattore forte debole "
                f"(punteggio {punteggio_distrattore})."
            )

            if strict_distractors:
                errori.append(messaggio)
            else:
                avvisi.append(messaggio)

        elif punteggio_distrattore < 0.50:
            avvisi.append(
                f"{id_domanda}: distrattore migliorabile "
                f"(punteggio {punteggio_distrattore})."
            )

    motivo = pulisci_testo(domanda.get("motivo_distrattore_forte"))

    if distrattore_forte and len(motivo) < 40:
        messaggio = (
            f"{id_domanda}: manca una spiegazione chiara del perché "
            f"il distrattore forte è vicino ma sbagliato."
        )

        if strict_distractors:
            errori.append(messaggio)
        else:
            avvisi.append(messaggio)

    lunghezze = [len(opzione) for opzione in opzioni_pulite if opzione]

    if lunghezze and min(lunghezze) > 0 and max(lunghezze) > min(lunghezze) * 3:
        avvisi.append(
            f"{id_domanda}: una risposta è molto più lunga delle altre."
        )

    testo_completo = testo_minuscolo(
        " ".join([testo_domanda, spiegazione] + opzioni_pulite)
    )

    parole_sottocategoria = PAROLE_CHIAVE_SOTTOCATEGORIE.get(
        domanda.get("sottocategoria"),
        [],
    )

    if parole_sottocategoria:
        contiene_parola_chiave = any(
            parola in testo_completo for parola in parole_sottocategoria
        )

        if not contiene_parola_chiave:
            avvisi.append(
                f"{id_domanda}: la domanda sembra poco collegata alla sottocategoria scelta."
            )

    usa_parole_assolute = any(
        parola in testo_minuscolo(testo_domanda)
        for parola in PAROLE_ASSOLUTE_RISCHIOSE
    )

    if usa_parole_assolute:
        avvisi.append(
            f"{id_domanda}: la domanda usa parole assolute. Controlla che non sia ambigua."
        )

    qualita = int(domanda.get("qualita", 0))

    if qualita < 60:
        messaggio = f"{id_domanda}: qualità bassa ({qualita}/100)."

        if strict_distractors:
            errori.append(messaggio)
        else:
            avvisi.append(messaggio)

    elif qualita < 75:
        avvisi.append(
            f"{id_domanda}: qualità migliorabile ({qualita}/100)."
        )

    return errori, avvisi


def normalizza_quiz_scienze(dati):
    domande_grezze = estrai_domande(dati)

    domande_normalizzate = []

    for indice, domanda in enumerate(domande_grezze, start=1):
        domande_normalizzate.append(
            normalizza_domanda_scienze(domanda, indice)
        )

    return domande_normalizzate


def valida_quiz_scienze(domande, strict_distractors=False):
    errori = []
    avvisi = []
    id_visti = set()

    for domanda in domande:
        id_domanda = domanda.get("id")

        if id_domanda in id_visti:
            errori.append(f"{id_domanda}: ID duplicato.")

        id_visti.add(id_domanda)

        errori_domanda, avvisi_domanda = valida_domanda_scienze(
            domanda,
            strict_distractors=strict_distractors,
        )
        errori.extend(errori_domanda)
        avvisi.extend(avvisi_domanda)

    qualita_media = 0

    if domande:
        qualita_media = round(
            sum(int(domanda.get("qualita", 0)) for domanda in domande) / len(domande),
            1,
        )

    return {
        "valid": len(errori) == 0,
        "errors": errori,
        "warnings": avvisi,
        "quiz": domande,
        "quality_average": qualita_media,
    }


def crea_prompt_gemma_scienze(categoria, argomento, livello, numero_domande):
    livello = normalizza_livello(livello)

    return f"""
Crea un quiz in italiano per il progetto Alex AI Quiz Database.

Categoria principale: scienze
Materia richiesta: {categoria}
Argomento: {argomento}
Livello: {livello}
Numero domande: {numero_domande}

REGOLE IMPORTANTI:
- Rispondi solo con JSON valido.
- Non usare markdown.
- Il JSON deve contenere una lista chiamata "quiz".
- La lista deve contenere esattamente {numero_domande} domande.
- Ogni domanda deve avere 4 opzioni.
- La risposta corretta deve essere il testo esatto di una delle 4 opzioni.
- Ogni domanda deve avere almeno un distrattore forte.
- Il distrattore forte deve essere sbagliato ma molto vicino alla risposta corretta.
- Scrivi anche "motivo_distrattore_forte".
- Le spiegazioni devono essere chiare e scientificamente corrette.
- Non usare risposte come "tutte le precedenti" o "nessuna delle precedenti".
- Evita domande troppo facili dove la risposta corretta si capisce per eliminazione.
- Le 4 risposte devono essere tutte plausibili e vicine allo stesso argomento.

FORMATO OBBLIGATORIO:
{{
  "quiz": [
    {{
      "id": "SCI-INT-0001",
      "categoria": "scienze",
      "sottocategoria": "biologia",
      "livello": "{livello}",
      "domanda": "Testo della domanda",
      "opzioni": [
        "Risposta corretta",
        "Distrattore forte molto vicino",
        "Distrattore medio plausibile",
        "Distrattore medio vicino al terzo"
      ],
      "risposta_corretta": "Risposta corretta",
      "spiegazione": "Spiegazione chiara.",
      "tags": ["scienze", "argomento"],
      "difficolta": {DIFFICOLTA_PER_LIVELLO[livello]},
      "distrattore_forte": "Distrattore forte molto vicino",
      "motivo_distrattore_forte": "Perché è vicino ma sbagliato."
    }}
  ]
}}

SOTTOCATEGORIE AMMESSE:
{", ".join(SOTTOCATEGORIE_VALIDE)}
""".strip()


def carica_json(percorso):
    with open(percorso, "r", encoding="utf-8") as file:
        return json.load(file)


def salva_json(percorso, dati):
    percorso = Path(percorso)
    percorso.parent.mkdir(parents=True, exist_ok=True)

    with open(percorso, "w", encoding="utf-8") as file:
        json.dump(dati, file, ensure_ascii=False, indent=2)


def stampa_report(risultato, percorso_input):
    print("----- MOTORE SCIENZE V2 -----")
    print(f"File controllato: {percorso_input}")
    print(f"Domande trovate: {len(risultato['quiz'])}")
    print(f"Qualità media: {risultato['quality_average']}/100")

    if risultato["errors"]:
        print("\nERRORI:")
        for errore in risultato["errors"]:
            print(f"- {errore}")

    if risultato["warnings"]:
        print("\nAVVISI:")
        for avviso in risultato["warnings"]:
            print(f"- {avviso}")

    if risultato["valid"]:
        print("\nRISULTATO: motore Scienze V2 OK.")
    else:
        print("\nRISULTATO: motore Scienze V2 NON valido.")


def main():
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python3 engines/science_engine.py data/scienze.json")
        print("  python3 engines/science_engine.py data/scienze.json --write-normalized data/scienze.json")
        print("  python3 engines/science_engine.py data/scienze.json --strict-distractors")
        print("  python3 engines/science_engine.py --prompt")
        sys.exit(1)

    if sys.argv[1] == "--prompt":
        prompt = crea_prompt_gemma_scienze(
            categoria="Scienze",
            argomento="cellule, energia, materia e metodo scientifico",
            livello="intermedio",
            numero_domande=10,
        )
        print(prompt)
        sys.exit(0)

    percorso_input = Path(sys.argv[1])
    strict_distractors = "--strict-distractors" in sys.argv

    dati = carica_json(percorso_input)
    domande = normalizza_quiz_scienze(dati)
    risultato = valida_quiz_scienze(
        domande,
        strict_distractors=strict_distractors,
    )

    stampa_report(risultato, percorso_input)

    if "--write-normalized" in sys.argv:
        indice = sys.argv.index("--write-normalized")
        percorso_output = Path(sys.argv[indice + 1])
        salva_json(percorso_output, domande)
        print(f"\nFile normalizzato salvato in: {percorso_output}")

    if not risultato["valid"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
