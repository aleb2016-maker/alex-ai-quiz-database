from pathlib import Path
import json
import re
import shutil
import datetime

ROOT = Path.cwd()
DATA_PATH = ROOT / "data/logica/logica_visiva.json"
BACKUP_DIR = ROOT / "backups"
REPORTS_DIR = ROOT / "reports"

BACKUP_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_PATH = BACKUP_DIR / f"logica_visiva.backup_prima_correzione_0019_0040_{STAMP}.json"
REPORT_PATH = REPORTS_DIR / "correzione_logica_visiva_0019_0040.md"

if not DATA_PATH.exists():
    raise FileNotFoundError(f"File non trovato: {DATA_PATH}")

shutil.copy2(DATA_PATH, BACKUP_PATH)

domande = json.loads(DATA_PATH.read_text(encoding="utf-8"))

ID_KEYS = ["id", "codice", "question_id", "uid"]

FORME_LATI = {
    "triangolo": 3,
    "quadrato": 4,
    "rettangolo": 4,
    "pentagono": 5,
    "esagono": 6,
    "ettagono": 7,
    "ottagono": 8,
    "cerchio": 0,
}

COLORI = [
    "rosso",
    "rossa",
    "blu",
    "verde",
    "giallo",
    "gialla",
    "viola",
    "arancione",
    "nero",
    "nera",
    "bianco",
    "bianca",
    "azzurro",
    "azzurra",
]

NUMERI_PAROLE = {
    "un": 1,
    "una": 1,
    "uno": 1,
    "due": 2,
    "tre": 3,
    "quattro": 4,
    "cinque": 5,
    "sei": 6,
    "sette": 7,
    "otto": 8,
}


def valore_id(domanda):
    for chiave in ID_KEYS:
        valore = domanda.get(chiave)
        if valore:
            return str(valore)
    return ""


def get_testo(domanda, chiavi):
    for chiave in chiavi:
        valore = domanda.get(chiave)
        if isinstance(valore, str) and valore.strip():
            return valore.strip()
    return ""


def set_spiegazione(domanda, testo):
    for chiave in ["spiegazione", "explanation", "motivazione"]:
        if chiave in domanda:
            domanda[chiave] = testo
            return
    domanda["spiegazione"] = testo


def get_spiegazione(domanda):
    return get_testo(domanda, ["spiegazione", "explanation", "motivazione"])


def get_risposta_corretta(domanda):
    return get_testo(
        domanda,
        ["risposta_corretta", "correct_answer", "answer", "corretta"]
    )


def get_domanda(domanda):
    return get_testo(domanda, ["domanda", "question", "testo"])


def normalizza_opzioni(opzioni):
    if isinstance(opzioni, dict):
        return {str(k): str(v) for k, v in opzioni.items()}

    if isinstance(opzioni, list):
        lettere = ["A", "B", "C", "D"]
        return {
            lettere[i] if i < len(lettere) else str(i + 1): str(valore)
            for i, valore in enumerate(opzioni)
        }

    return {}


def trova_forma(testo):
    testo_basso = testo.lower()
    for forma in FORME_LATI:
        if forma in testo_basso:
            return forma
    return ""


def trova_colore(testo):
    testo_basso = testo.lower()
    for colore in COLORI:
        if re.search(rf"\b{re.escape(colore)}\b", testo_basso):
            if colore == "rossa":
                return "rosso"
            if colore == "gialla":
                return "giallo"
            if colore == "nera":
                return "nero"
            if colore == "bianca":
                return "bianco"
            if colore == "azzurra":
                return "azzurro"
            return colore
    return ""


def trova_lati(testo, forma):
    testo_basso = testo.lower()

    match = re.search(r"(\d+)\s+lati", testo_basso)
    if match:
        return int(match.group(1))

    if forma in FORME_LATI:
        return FORME_LATI[forma]

    return None


def trova_oggetti_interni(testo):
    testo_basso = testo.lower()

    pattern = (
        r"(?:(\d+)|un|una|uno|due|tre|quattro|cinque|sei|sette|otto)"
        r"\s+"
        r"(triangoli?|pallini?|cerchi?|quadrati?|punti?)"
        r"\s+intern"
    )

    match = re.search(pattern, testo_basso)

    if not match:
        if "senza oggetti interni" in testo_basso:
            return "senza oggetti interni"
        if "triangolo interno" in testo_basso:
            return "1 triangolo interno"
        if "pallino interno" in testo_basso:
            return "1 pallino interno"
        return "oggetti interni coerenti con la sequenza"

    numero_testuale = match.group(1)

    if numero_testuale and numero_testuale.isdigit():
        numero = int(numero_testuale)
    else:
        parola = match.group(0).split()[0]
        numero = NUMERI_PAROLE.get(parola, 1)

    oggetto = match.group(2)

    if numero == 1:
        oggetto = (
            oggetto.replace("triangoli", "triangolo")
            .replace("pallini", "pallino")
            .replace("cerchi", "cerchio")
            .replace("quadrati", "quadrato")
            .replace("punti", "punto")
        )

    return f"{numero} {oggetto} interno" if numero == 1 else f"{numero} {oggetto} interni"


def analizza_risposta(risposta):
    forma = trova_forma(risposta)
    colore = trova_colore(risposta)
    lati = trova_lati(risposta, forma)
    oggetti = trova_oggetti_interni(risposta)

    return {
        "forma": forma,
        "colore": colore,
        "numero_lati": lati,
        "oggetti_interni": oggetti,
        "risposta_testuale": risposta,
    }


def costruisci_spiegazione(risposta, caratteristiche):
    forma = caratteristiche["forma"] or "figura corretta"
    colore = caratteristiche["colore"] or "colore richiesto"
    lati = caratteristiche["numero_lati"]
    oggetti = caratteristiche["oggetti_interni"]

    if lati is None:
        frase_lati = "il numero di lati richiesto"
    elif lati == 0:
        frase_lati = "la forma senza lati retti indicata dalla regola"
    else:
        frase_lati = f"{lati} lati"

    return (
        f"La risposta corretta è {risposta}. "
        f"La trasformazione porta a un {forma} {colore} con {frase_lati} "
        f"e {oggetti}. "
        f"Quindi la risposta mantiene insieme forma, colore, numero di lati "
        f"e oggetti interni richiesti dalla sequenza."
    )


def spiegazione_da_correggere(id_domanda, spiegazione):
    spiegazione_bassa = spiegazione.lower()

    ids_incompleti = {
        "LOG-VIS-0021",
        "LOG-VIS-0023",
        "LOG-VIS-0025",
        "LOG-VIS-0027",
        "LOG-VIS-0030",
        "LOG-VIS-0034",
        "LOG-VIS-0035",
        "LOG-VIS-0036",
        "LOG-VIS-0038",
        "LOG-VIS-0039",
    }

    if id_domanda == "LOG-VIS-0020":
        return True

    if id_domanda in ids_incompleti:
        return True

    parole_obbligatorie = ["forma", "colore"]

    if not all(parola in spiegazione_bassa for parola in parole_obbligatorie):
        return True

    if "lati" not in spiegazione_bassa and "cerchio" not in spiegazione_bassa:
        return True

    if "intern" not in spiegazione_bassa and "oggetti" not in spiegazione_bassa:
        return True

    return False


def domanda_target(id_domanda):
    if not id_domanda.startswith("LOG-VIS-"):
        return False

    match = re.search(r"LOG-VIS-(\d{4})$", id_domanda)

    if not match:
        return False

    numero = int(match.group(1))
    return 19 <= numero <= 40


modificate = []
spiegazioni_riscritte = []
visual_logic_riscritti = []
non_trovate = []

for domanda in domande:
    id_domanda = valore_id(domanda)

    if not domanda_target(id_domanda):
        continue

    risposta = get_risposta_corretta(domanda)
    testo_domanda = get_domanda(domanda)
    spiegazione = get_spiegazione(domanda)
    opzioni = normalizza_opzioni(domanda.get("opzioni"))

    if not risposta:
        non_trovate.append(f"{id_domanda}: manca risposta_corretta")
        continue

    caratteristiche = analizza_risposta(risposta)

    domanda["visual_logic"] = {
        "schema_version": "visual_logic_v2",
        "tipo_controllo": "coerenza_figura_finale",
        "domanda_id": id_domanda,
        "regola_dichiarata": testo_domanda,
        "risposta_attesa": risposta,
        "caratteristiche_attese": caratteristiche,
        "opzioni_testuali": opzioni,
        "controlli_obbligatori": [
            "forma",
            "colore",
            "numero_lati",
            "oggetti_interni",
        ],
        "nota_qualita": (
            "Contratto visual_logic ricostruito dalla risposta corretta reale. "
            "Non deve contenere riferimenti copiati da altri esercizi."
        ),
    }

    visual_logic_riscritti.append(id_domanda)

    if spiegazione_da_correggere(id_domanda, spiegazione):
        nuova_spiegazione = costruisci_spiegazione(risposta, caratteristiche)
        set_spiegazione(domanda, nuova_spiegazione)
        spiegazioni_riscritte.append(id_domanda)

    modificate.append(id_domanda)

DATA_PATH.write_text(
    json.dumps(domande, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

report = [
    "# Correzione Logica visiva LOG-VIS-0019 → LOG-VIS-0040",
    "",
    f"Backup creato fuori da `data/`: `{BACKUP_PATH.relative_to(ROOT)}`",
    "",
    "## Domande modificate",
    "",
]

for id_domanda in modificate:
    report.append(f"- `{id_domanda}`")

report.extend([
    "",
    "## visual_logic riscritti",
    "",
])

for id_domanda in visual_logic_riscritti:
    report.append(f"- `{id_domanda}`")

report.extend([
    "",
    "## Spiegazioni riscritte o completate",
    "",
])

for id_domanda in spiegazioni_riscritte:
    report.append(f"- `{id_domanda}`")

if non_trovate:
    report.extend(["", "## Avvisi", ""])
    for avviso in non_trovate:
        report.append(f"- {avviso}")

REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")

print("✅ Correzione LOG-VIS-0019 → LOG-VIS-0040 completata.")
print(f"Domande modificate: {len(modificate)}")
print(f"Spiegazioni riscritte/completate: {len(spiegazioni_riscritte)}")
print(f"Report: {REPORT_PATH}")
print(f"Backup: {BACKUP_PATH}")
