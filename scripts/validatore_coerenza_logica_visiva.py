from pathlib import Path
import json
import re
import sys

DATA_PATH = Path("data/logica/logica_visiva.json")
REPORT_MD = Path("reports/validatore_coerenza_logica_visiva.md")
REPORT_JSON = Path("reports/validatore_coerenza_logica_visiva.json")

REPORT_MD.parent.mkdir(exist_ok=True)

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


def get_id(domanda):
    return str(
        domanda.get("id")
        or domanda.get("codice")
        or domanda.get("question_id")
        or domanda.get("uid")
        or ""
    )


def is_target(codice):
    match = re.fullmatch(r"LOG-VIS-(\d{4})", codice)
    return bool(match and 19 <= int(match.group(1)) <= 40)


def get_risposta(domanda):
    return str(
        domanda.get("risposta_corretta")
        or domanda.get("risposta_corretta_testo")
        or ""
    ).strip()


def get_spiegazione(domanda):
    return str(domanda.get("spiegazione") or "").strip()


def analizza_risposta(testo):
    testo_pulito = testo.strip()
    testo_basso = testo_pulito.lower()

    forma = ""
    colore = ""

    match = re.match(
        rf"^\s*(?P<forma>{FORME_PATTERN})\s+(?P<colore>{COLORI_PATTERN})\b",
        testo_basso,
    )

    if match:
        forma = match.group("forma")
        colore = match.group("colore")

    match_lati = re.search(r"\b(\d+)\s+lati\b", testo_basso)
    numero_lati = int(match_lati.group(1)) if match_lati else FORME_LATI.get(forma)

    oggetti_interni = ""

    match_oggetti = re.search(
        r"\be\s+([^.,;]+?\s+intern[oi])\b",
        testo_pulito,
        flags=re.IGNORECASE,
    )

    if match_oggetti:
        oggetti_interni = match_oggetti.group(1).lower().strip()
    elif "senza oggetti interni" in testo_basso:
        oggetti_interni = "senza oggetti interni"
    elif "0 oggetti interni" in testo_basso:
        oggetti_interni = "0 oggetti interni"

    return {
        "forma": forma,
        "colore": colore,
        "numero_lati": numero_lati,
        "oggetti_interni": oggetti_interni,
    }


def main():
    if not DATA_PATH.exists():
        print(f"❌ File non trovato: {DATA_PATH}")
        sys.exit(1)

    domande = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    problemi = []
    controllate = 0

    for domanda in domande:
        codice = get_id(domanda)

        if not is_target(codice):
            continue

        controllate += 1

        risposta = get_risposta(domanda)
        spiegazione = get_spiegazione(domanda)
        visual_logic = domanda.get("visual_logic")

        if not risposta:
            problemi.append((codice, "manca risposta_corretta"))
            continue

        if not spiegazione:
            problemi.append((codice, "manca spiegazione"))

        if not isinstance(visual_logic, dict):
            problemi.append((codice, "manca visual_logic strutturato"))
            continue

        if visual_logic.get("schema_version") != "visual_logic_v2":
            problemi.append((codice, "visual_logic non usa schema_version visual_logic_v2"))

        risposta_attesa = str(visual_logic.get("risposta_attesa") or "").strip()

        if risposta_attesa != risposta:
            problemi.append(
                (
                    codice,
                    f"risposta_attesa diversa da risposta_corretta: '{risposta_attesa}' != '{risposta}'",
                )
            )

        caratteristiche = visual_logic.get("caratteristiche_attese") or {}
        analisi = analizza_risposta(risposta)

        for campo in ["forma", "colore", "numero_lati", "oggetti_interni"]:
            valore_visual = str(caratteristiche.get(campo)).strip().lower()
            valore_reale = str(analisi.get(campo)).strip().lower()

            if valore_visual != valore_reale:
                problemi.append(
                    (
                        codice,
                        f"{campo} incoerente: visual_logic='{valore_visual}' risposta='{valore_reale}'",
                    )
                )

        if analisi["forma"] and analisi["forma"] not in spiegazione.lower():
            problemi.append((codice, f"spiegazione non cita forma: {analisi['forma']}"))

        if analisi["colore"] and analisi["colore"] not in spiegazione.lower():
            problemi.append((codice, f"spiegazione non cita colore: {analisi['colore']}"))

        if analisi["numero_lati"] is not None:
            frase_lati = f"{analisi['numero_lati']} lati"

            if frase_lati not in spiegazione.lower():
                problemi.append((codice, f"spiegazione non cita lati: {frase_lati}"))

        if analisi["oggetti_interni"] and analisi["oggetti_interni"] not in spiegazione.lower():
            problemi.append(
                (
                    codice,
                    f"spiegazione non cita oggetti interni: {analisi['oggetti_interni']}",
                )
            )

        testo_visual = json.dumps(visual_logic, ensure_ascii=False).lower()

        for residuo in [
            "cerchio/quadrato",
            "cerchio nero",
            "dopo il quadrato torna il cerchio",
            "outer_shape",
            "outer_color",
            "triangolo verde con 7 lati",
        ]:
            if residuo in testo_visual:
                problemi.append((codice, f"residuo vecchio in visual_logic: {residuo}"))

    report_json = {
        "file": str(DATA_PATH),
        "domande_controllate": controllate,
        "problemi": [
            {"id": codice, "problema": problema}
            for codice, problema in problemi
        ],
        "esito": "KO" if problemi else "OK",
    }

    REPORT_JSON.write_text(
        json.dumps(report_json, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    righe = [
        "# Validatore coerenza Logica visiva",
        "",
        f"Domande controllate: {controllate}",
        f"Problemi trovati: {len(problemi)}",
        "",
    ]

    if problemi:
        righe.append("## Problemi")
        righe.append("")

        for codice, problema in problemi:
            righe.append(f"- `{codice}`: {problema}")
    else:
        righe.append("✅ Nessuna incoerenza tra risposta, spiegazione e visual_logic.")

    REPORT_MD.write_text("\n".join(righe) + "\n", encoding="utf-8")

    if controllate != 22:
        print(f"❌ Numero domande controllate non corretto: {controllate}, attese 22.")
        sys.exit(1)

    if problemi:
        print("❌ Validatore coerenza Logica visiva fallito.")
        for codice, problema in problemi:
            print(f"- {codice}: {problema}")
        print(f"Report: {REPORT_MD}")
        sys.exit(1)

    print("✅ Validatore coerenza Logica visiva superato.")
    print(f"Domande controllate: {controllate}")
    print(f"Report: {REPORT_MD}")


if __name__ == "__main__":
    main()
