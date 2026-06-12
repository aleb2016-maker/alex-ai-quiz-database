from pathlib import Path
import json
import re
import sys


JSON_FILE = Path("data/logica/logica_visiva.json")
REPORT_FILE = Path("dist/report_spiegazioni_logica_visiva.md")
ROOT = Path(".")


PAROLE_COLORE = [
    "colore", "colori", "rosso", "rossa", "blu", "verde",
    "giallo", "viola", "arancione", "alternanza cromatica"
]

PAROLE_PUNTI = [
    "punto", "punti",
    "puntino", "puntini",
    "cerchio", "cerchi",
    "pallino", "pallini",
    "elemento", "elementi",
    "stella", "stelle"
]

PAROLE_LINEE = [
    "linea", "linee",
    "segmento", "segmenti",
    "tratto", "tratti",
    "riga", "righe",
    "barra", "barre",
    "diagonale", "diagonali",
    "contorno", "contorni"
]

PAROLE_SPIEGAZIONE = [
    "perché", "quindi", "deve", "corretta", "regola",
    "schema", "sequenza", "dopo", "passaggio"
]


def contiene_parola(testo, parole):
    testo = testo.lower()

    for parola in parole:
        pattern = r"\b" + re.escape(parola.lower()) + r"\b"
        if re.search(pattern, testo):
            return True

    return False


def normalizza_hex(colore):
    colore = colore.lower()

    if len(colore) == 4:
        return "#" + "".join(carattere * 2 for carattere in colore[1:])

    return colore


def colore_non_neutro(colore):
    colore = normalizza_hex(colore)

    if not re.fullmatch(r"#[0-9a-f]{6}", colore):
        return False

    r = int(colore[1:3], 16)
    g = int(colore[3:5], 16)
    b = int(colore[5:7], 16)

    massimo = max(r, g, b)
    minimo = min(r, g, b)

    molto_chiaro = r > 225 and g > 225 and b > 225
    molto_scuro = r < 35 and g < 35 and b < 35
    quasi_grigio = massimo - minimo < 25

    return not (molto_chiaro or molto_scuro or quasi_grigio)


def estrai_percorsi_immagini(domanda):
    percorsi = []

    for campo in [
        "immagine_domanda",
        "immagine",
        "immagine_svg",
        "svg_domanda",
    ]:
        valore = domanda.get(campo)

        if isinstance(valore, str):
            percorsi.append(valore)

    immagini_opzioni = domanda.get("immagini_opzioni")

    if isinstance(immagini_opzioni, list):
        for valore in immagini_opzioni:
            if isinstance(valore, str):
                percorsi.append(valore)
            elif isinstance(valore, dict):
                for possibile_path in valore.values():
                    if isinstance(possibile_path, str):
                        percorsi.append(possibile_path)

    elif isinstance(immagini_opzioni, dict):
        for valore in immagini_opzioni.values():
            if isinstance(valore, str):
                percorsi.append(valore)

    return percorsi


def leggi_svg(percorso):
    path = Path(percorso)

    if not path.is_absolute():
        path = ROOT / path

    if not path.exists():
        return ""

    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def analizza_svg(domanda):
    svg_testi = []

    for percorso in estrai_percorsi_immagini(domanda):
        testo_svg = leggi_svg(percorso)

        if testo_svg:
            svg_testi.append(testo_svg)

    colori = set()
    conteggi_punti = []
    conteggi_linee = []

    for svg in svg_testi:
        for colore in re.findall(r"#[0-9a-fA-F]{3,6}", svg):
            colore = normalizza_hex(colore)

            if colore_non_neutro(colore):
                colori.add(colore)

        conteggi_punti.append(len(re.findall(r"<circle\b", svg)))
        conteggi_linee.append(
            len(re.findall(r"<line\b", svg))
            + len(re.findall(r"<polyline\b", svg))
        )

    return {
        "colori_non_neutri": colori,
        "conteggi_punti": conteggi_punti,
        "conteggi_linee": conteggi_linee,
    }


def crea_problemi(domanda):
    problemi_rossi = []
    problemi_gialli = []

    spiegazione = str(domanda.get("spiegazione", "")).strip()
    analisi_svg = analizza_svg(domanda)

    if len(spiegazione) < 120:
        problemi_rossi.append(
            "La spiegazione è troppo breve: rischia di non spiegare tutta la logica."
        )

    if not contiene_parola(spiegazione, PAROLE_SPIEGAZIONE):
        problemi_gialli.append(
            "La spiegazione non contiene parole che chiariscono bene il ragionamento."
        )

    colori = analisi_svg["colori_non_neutri"]

    if len(colori) >= 2 and not contiene_parola(spiegazione, PAROLE_COLORE):
        problemi_rossi.append(
            "Gli SVG usano più colori, ma la spiegazione non cita il colore."
        )

    conteggi_punti = analisi_svg["conteggi_punti"]

    if conteggi_punti and max(conteggi_punti) - min(conteggi_punti) >= 1:
        if not contiene_parola(spiegazione, PAROLE_PUNTI):
            problemi_rossi.append(
                "Le immagini usano punti/cerchi, ma la spiegazione non li cita."
            )

    conteggi_linee = analisi_svg["conteggi_linee"]

    if conteggi_linee and max(conteggi_linee) - min(conteggi_linee) >= 1:
        if not contiene_parola(spiegazione, PAROLE_LINEE):
            problemi_gialli.append(
                "Le immagini sembrano usare linee/segmenti, ma la spiegazione non li cita."
            )

    return problemi_rossi, problemi_gialli


def main():
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(JSON_FILE, "r", encoding="utf-8") as file:
        domande = json.load(file)

    risultati = []

    for domanda in domande:
        problemi_rossi, problemi_gialli = crea_problemi(domanda)

        stato = "OK"

        if problemi_rossi:
            stato = "ROSSO"
        elif problemi_gialli:
            stato = "GIALLO"

        risultati.append({
            "id": domanda.get("id", "ID_MANCANTE"),
            "domanda": domanda.get("domanda", ""),
            "risposta_corretta": domanda.get("risposta_corretta", ""),
            "spiegazione": domanda.get("spiegazione", ""),
            "stato": stato,
            "rossi": problemi_rossi,
            "gialli": problemi_gialli,
        })

    rossi = [r for r in risultati if r["stato"] == "ROSSO"]
    gialli = [r for r in risultati if r["stato"] == "GIALLO"]
    ok = [r for r in risultati if r["stato"] == "OK"]

    righe = []
    righe.append("# Report qualità spiegazioni logica visiva")
    righe.append("")
    righe.append("## Riepilogo")
    righe.append("")
    righe.append(f"Domande controllate: {len(risultati)}")
    righe.append(f"ROSSO - spiegazioni incomplete: {len(rossi)}")
    righe.append(f"GIALLO - spiegazioni da rafforzare: {len(gialli)}")
    righe.append(f"OK: {len(ok)}")
    righe.append("")

    for titolo, gruppo in [
        ("ROSSO - spiegazioni incomplete", rossi),
        ("GIALLO - spiegazioni da rafforzare", gialli),
    ]:
        righe.append(f"## {titolo}")
        righe.append("")

        if not gruppo:
            righe.append("Nessun problema trovato.")
            righe.append("")
            continue

        for risultato in gruppo:
            righe.append(f"### {risultato['id']}")
            righe.append("")
            righe.append(f"**Domanda:** {risultato['domanda']}")
            righe.append("")
            righe.append(f"**Risposta corretta:** {risultato['risposta_corretta']}")
            righe.append("")
            righe.append(f"**Spiegazione attuale:** {risultato['spiegazione']}")
            righe.append("")
            righe.append("**Problemi:**")

            for problema in risultato["rossi"] + risultato["gialli"]:
                righe.append(f"- {problema}")

            righe.append("")

    REPORT_FILE.write_text("\n".join(righe), encoding="utf-8")

    print("----- CONTROLLO SPIEGAZIONI LOGICA VISIVA -----")
    print("Domande controllate:", len(risultati))
    print("ROSSO - spiegazioni incomplete:", len(rossi))
    print("GIALLO - spiegazioni da rafforzare:", len(gialli))
    print("OK:", len(ok))
    print("Report creato:", REPORT_FILE)

    if rossi:
        print("")
        print("Prime spiegazioni da correggere:")

        for risultato in rossi[:8]:
            print("-", risultato["id"])

        sys.exit(1)


main()
