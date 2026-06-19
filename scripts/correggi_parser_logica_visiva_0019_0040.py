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
BACKUP_PATH = BACKUP_DIR / f"logica_visiva.backup_prima_fix_parser_0019_0040_{STAMP}.json"
REPORT_PATH = REPORTS_DIR / "fix_parser_logica_visiva_0019_0040.md"

shutil.copy2(DATA_PATH, BACKUP_PATH)

domande = json.loads(DATA_PATH.read_text(encoding="utf-8"))

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
    "blu",
    "verde",
    "giallo",
    "viola",
    "arancione",
    "nero",
    "bianco",
    "azzurro",
]

FORME_PATTERN = "|".join(FORME_LATI.keys())
COLORI_PATTERN = "|".join(COLORI)


def id_domanda(domanda):
    return str(domanda.get("id") or domanda.get("codice") or "")


def is_target(codice):
    match = re.fullmatch(r"LOG-VIS-(\d{4})", codice)
    return bool(match and 19 <= int(match.group(1)) <= 40)


def risposta_corretta(domanda):
    return str(domanda.get("risposta_corretta") or domanda.get("risposta_corretta_testo") or "").strip()


def normalizza_opzioni(opzioni):
    if isinstance(opzioni, dict):
        return {str(k): str(v) for k, v in opzioni.items()}

    if isinstance(opzioni, list):
        lettere = ["A", "B", "C", "D"]
        return {
            lettere[indice]: str(valore)
            for indice, valore in enumerate(opzioni)
            if indice < len(lettere)
        }

    return {}


def analizza_risposta(testo):
    testo_pulito = testo.strip()
    testo_basso = testo_pulito.lower()

    forma = ""
    colore = ""

    # Forma esterna: deve essere la prima forma della risposta,
    # non l'oggetto interno.
    match_inizio = re.match(
        rf"^\s*(?P<forma>{FORME_PATTERN})\s+(?P<colore>{COLORI_PATTERN})\b",
        testo_basso,
    )

    if match_inizio:
        forma = match_inizio.group("forma")
        colore = match_inizio.group("colore")
    else:
        for forma_possibile in FORME_LATI:
            if re.search(rf"\b{forma_possibile}\b", testo_basso):
                forma = forma_possibile
                break

        for colore_possibile in COLORI:
            if re.search(rf"\b{colore_possibile}\b", testo_basso):
                colore = colore_possibile
                break

    match_lati = re.search(r"\b(\d+)\s+lati\b", testo_basso)
    numero_lati = int(match_lati.group(1)) if match_lati else FORME_LATI.get(forma)

    oggetti_interni = "oggetti interni richiesti"

    match_oggetti = re.search(
        r"\be\s+(.+?\s+intern[oi])\b",
        testo_pulito,
        flags=re.IGNORECASE,
    )

    if match_oggetti:
        oggetti_interni = match_oggetti.group(1).strip()
    elif "senza oggetti interni" in testo_basso:
        oggetti_interni = "senza oggetti interni"

    return {
        "forma": forma,
        "colore": colore,
        "numero_lati": numero_lati,
        "oggetti_interni": oggetti_interni,
        "risposta_testuale": testo_pulito,
    }


def descrivi_lati(numero_lati):
    if numero_lati == 0:
        return "0 lati"
    return f"{numero_lati} lati"


def crea_spiegazione(risposta, caratteristiche):
    forma = caratteristiche["forma"]
    colore = caratteristiche["colore"]
    lati = descrivi_lati(caratteristiche["numero_lati"])
    oggetti = caratteristiche["oggetti_interni"]

    return (
        f"La risposta corretta è {risposta}. "
        f"La trasformazione richiede come figura finale un elemento di tipo {forma} "
        f"{colore} con {lati} e {oggetti}. "
        f"Quindi la risposta è coerente con forma, colore, numero di lati "
        f"e oggetti interni richiesti dalla sequenza."
    )


def differenze(opzione_caratteristiche, corrette):
    parti = []

    if opzione_caratteristiche["forma"] != corrette["forma"]:
        parti.append("forma")

    if opzione_caratteristiche["colore"] != corrette["colore"]:
        parti.append("colore")

    if opzione_caratteristiche["numero_lati"] != corrette["numero_lati"]:
        parti.append("numero di lati")

    if opzione_caratteristiche["oggetti_interni"] != corrette["oggetti_interni"]:
        parti.append("oggetti interni")

    return parti


def crea_spiegazioni_opzioni(opzioni, caratteristiche_corrette):
    spiegazioni = {}

    for lettera, testo_opzione in opzioni.items():
        caratteristiche_opzione = analizza_risposta(testo_opzione)
        diff = differenze(caratteristiche_opzione, caratteristiche_corrette)

        if not diff:
            spiegazioni[lettera] = (
                "Corretta: rispetta forma, colore, numero di lati "
                "e oggetti interni richiesti."
            )
        else:
            spiegazioni[lettera] = (
                "Non corretta: differisce per "
                + ", ".join(diff)
                + "."
            )

    return spiegazioni


modificate = []

for domanda in domande:
    codice = id_domanda(domanda)

    if not is_target(codice):
        continue

    risposta = risposta_corretta(domanda)
    opzioni = normalizza_opzioni(domanda.get("opzioni"))

    if not risposta:
        continue

    caratteristiche = analizza_risposta(risposta)

    domanda["spiegazione"] = crea_spiegazione(risposta, caratteristiche)

    domanda["visual_logic"] = {
        "schema_version": "visual_logic_v2",
        "tipo_controllo": "coerenza_figura_finale",
        "domanda_id": codice,
        "regola_dichiarata": str(domanda.get("domanda", "")).strip(),
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
            "Contratto visual_logic specifico della domanda. "
            "La forma esterna viene letta dall'inizio della risposta, "
            "non dagli oggetti interni."
        ),
    }

    if opzioni:
        domanda["spiegazioni_opzioni"] = crea_spiegazioni_opzioni(
            opzioni,
            caratteristiche,
        )

    domanda["motivo_distrattore_forte"] = (
        "I distrattori sono plausibili perché modificano uno o più dettagli "
        "vicini alla risposta corretta: forma, colore, numero di lati "
        "oppure oggetti interni."
    )

    modificate.append(codice)

DATA_PATH.write_text(
    json.dumps(domande, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

REPORT_PATH.write_text(
    "\n".join([
        "# Fix parser Logica visiva LOG-VIS-0019 → LOG-VIS-0040",
        "",
        f"Backup creato: `{BACKUP_PATH.relative_to(ROOT)}`",
        "",
        "Correzione applicata:",
        "",
        "- la forma esterna viene letta dall'inizio della risposta;",
        "- gli oggetti interni non vengono più scambiati per forma esterna;",
        "- spiegazioni riscritte per tutte le domande LOG-VIS-0019 → LOG-VIS-0040;",
        "- visual_logic ricostruito per tutte le 22 domande;",
        "- spiegazioni_opzioni riscritte per evitare residui cerchio/quadrato copiati.",
        "",
        "Domande modificate:",
        "",
        *[f"- `{codice}`" for codice in modificate],
        "",
    ]),
    encoding="utf-8",
)

print("✅ Fix parser Logica visiva completato.")
print(f"Domande modificate: {len(modificate)}")
print(f"Report: {REPORT_PATH}")
print(f"Backup: {BACKUP_PATH}")
