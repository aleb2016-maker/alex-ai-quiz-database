from pathlib import Path
import argparse
import json
import sys

from qualita_linguistica import controlla_lingua_domanda, controlla_lingua_testo


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"

CANDIDATI_LOGICA_VISIVA = [
    ROOT / "data" / "logica" / "logica_visiva.json",
    ROOT / "data" / "logica_visiva.json",
]

CHIAVI_LISTA_DOMANDE = [
    "domande",
    "questions",
    "quiz",
    "items",
    "data",
    "database",
]

CHIAVI_DOMANDA = [
    "domanda",
    "question",
    "testo",
    "text",
    "prompt",
]

CHIAVI_OPZIONI = [
    "opzioni",
    "options",
    "risposte",
    "answers",
]

CHIAVI_RISPOSTA = [
    "risposta_corretta",
    "correct_answer",
    "correct",
    "answer",
    "soluzione",
]

CHIAVI_REGOLA_VISIVA = [
    "regola_visiva",
    "visual_logic",
    "regola",
    "pattern",
    "logica",
    "trasformazione",
]

CHIAVI_SPIEGAZIONE = [
    "spiegazione",
    "explanation",
    "motivo",
]

ESTENSIONI_IMMAGINI = (
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".svg",
)


def normalizza_testo(valore):
    if valore is None:
        return ""

    if isinstance(valore, str):
        return valore.strip()

    if isinstance(valore, (int, float, bool)):
        return str(valore).strip()

    if isinstance(valore, dict):
        for chiave in ["testo", "text", "label", "answer", "opzione", "value"]:
            if chiave in valore:
                return normalizza_testo(valore.get(chiave))

    return json.dumps(valore, ensure_ascii=False).strip()


def primo_valore(dizionario, chiavi, default=""):
    if not isinstance(dizionario, dict):
        return default

    for chiave in chiavi:
        valore = dizionario.get(chiave)
        if valore is not None:
            return valore

    return default


def leggi_json(percorso):
    try:
        return json.loads(percorso.read_text(encoding="utf-8"))
    except Exception as errore:
        raise RuntimeError(f"JSON non leggibile: {errore}")


def estrai_lista_domande(dati):
    if isinstance(dati, list):
        return dati

    if isinstance(dati, dict):
        for chiave in CHIAVI_LISTA_DOMANDE:
            valore = dati.get(chiave)
            if isinstance(valore, list):
                return valore

    raise RuntimeError("struttura JSON non riconosciuta: non trovo la lista domande")


def estrai_opzioni(domanda):
    valore = primo_valore(domanda, CHIAVI_OPZIONI, default=[])

    if not isinstance(valore, list):
        return []

    return [
        normalizza_testo(opzione)
        for opzione in valore
    ]


def sembra_immagine(testo):
    testo = normalizza_testo(testo).lower()
    return testo.endswith(ESTENSIONI_IMMAGINI)


def raccogli_riferimenti_immagini(valore):
    immagini = []

    if isinstance(valore, str):
        if sembra_immagine(valore):
            immagini.append(valore.strip())
        return immagini

    if isinstance(valore, list):
        for elemento in valore:
            immagini.extend(raccogli_riferimenti_immagini(elemento))
        return immagini

    if isinstance(valore, dict):
        for sotto_valore in valore.values():
            immagini.extend(raccogli_riferimenti_immagini(sotto_valore))
        return immagini

    return immagini


def risolvi_percorso_immagine(riferimento):
    riferimento = normalizza_testo(riferimento)

    if not riferimento:
        return None

    candidato = Path(riferimento)

    if candidato.is_absolute() and candidato.exists():
        return candidato

    tentativi = [
        ROOT / riferimento,
        ROOT / "data" / riferimento,
        ROOT / "assets" / riferimento,
        ROOT / "demo" / riferimento,
    ]

    for tentativo in tentativi:
        if tentativo.exists():
            return tentativo

    return None


def contiene_parole_chiave_visive(testo):
    testo = normalizza_testo(testo).lower()

    parole_chiave = [
        # parole generali
        "forma",
        "colore",
        "colori",
        "lati",
        "lato",
        "oggetti",
        "oggetto",
        "interni",
        "interno",
        "trasformazione",
        "modello",
        "sequenza",
        "matrice",
        "griglia",

        # forme
        "cerchio",
        "cerchi",
        "quadrato",
        "quadrati",
        "triangolo",
        "triangoli",
        "esagono",
        "esagoni",
        "freccia",
        "frecce",
        "simbolo",
        "tassello",
        "casella",

        # elementi interni
        "pallino",
        "pallini",
        "linea",
        "linee",
        "riempimento",
        "pieno",
        "vuoto",

        # trasformazioni
        "alterna",
        "alternano",
        "alternanza",
        "aumenta",
        "aumentano",
        "diminuisce",
        "diminuiscono",
        "ruota",
        "rotazione",
        "orario",
        "antiorario",
        "speculare",
        "fisso",
        "fissa",
        "mantiene",
        "prosegue",
    ]

    return [
        parola
        for parola in parole_chiave
        if parola in testo
    ]


def analizza_domanda_visiva(indice, domanda):
    problemi_tecnici = []
    avvisi_qualita = []
    errori_linguistici = []
    note = []

    if not isinstance(domanda, dict):
        return {
            "id": f"LV_{indice + 1}",
            "domanda": "",
            "problemi_tecnici": ["Elemento domanda non è un oggetto JSON"],
            "avvisi_qualita": [],
            "errori_linguistici": [],
            "note": [],
            "immagini_trovate": [],
            "immagini_mancanti": [],
        }

    id_domanda = normalizza_testo(
        domanda.get("id")
        or domanda.get("codice")
        or f"LV_{indice + 1}"
    )

    testo_domanda = normalizza_testo(primo_valore(domanda, CHIAVI_DOMANDA))
    opzioni = estrai_opzioni(domanda)
    risposta = normalizza_testo(primo_valore(domanda, CHIAVI_RISPOSTA))
    regola_visiva = primo_valore(domanda, CHIAVI_REGOLA_VISIVA, default="")
    testo_regola_visiva = normalizza_testo(regola_visiva)
    spiegazione = normalizza_testo(primo_valore(domanda, CHIAVI_SPIEGAZIONE, default=""))

    # Per valutare se la spiegazione è completa, guardiamo sia la spiegazione
    # sia la regola strutturata visual_logic, quando esiste.
    testo_visivo_completo = f"{spiegazione} {testo_regola_visiva}".strip()

    if not id_domanda:
        problemi_tecnici.append("ID domanda mancante")

    if not testo_domanda:
        problemi_tecnici.append("Testo domanda mancante")

    if len(opzioni) != 4:
        problemi_tecnici.append(f"Numero opzioni non valido: trovate {len(opzioni)}, attese 4")

    if not risposta:
        problemi_tecnici.append("Risposta corretta mancante")

    if risposta and opzioni and risposta not in opzioni:
        problemi_tecnici.append("Risposta corretta non presente nelle opzioni testuali")

    riferimenti_immagini = sorted(set(raccogli_riferimenti_immagini(domanda)))

    immagini_trovate = []
    immagini_mancanti = []

    for riferimento in riferimenti_immagini:
        percorso = risolvi_percorso_immagine(riferimento)

        if percorso is None:
            immagini_mancanti.append(riferimento)
        else:
            immagini_trovate.append(str(percorso.relative_to(ROOT)))

    if not riferimenti_immagini:
        avvisi_qualita.append("Nessun riferimento immagine trovato nella domanda")

    if immagini_mancanti:
        problemi_tecnici.append(f"Immagini mancanti: {len(immagini_mancanti)}")

    if not testo_regola_visiva:
        avvisi_qualita.append("Regola visiva non dichiarata in modo strutturato")

    parole_spiegazione = contiene_parole_chiave_visive(testo_visivo_completo)

    if not spiegazione:
        avvisi_qualita.append("Spiegazione mancante")
    elif len(parole_spiegazione) < 2:
        avvisi_qualita.append(
            "Spiegazione visiva forse incompleta: dovrebbe citare forma, colore, lati, oggetti interni o trasformazione"
        )

    if "specular" in testo_domanda.lower() and "specular" not in spiegazione.lower():
        avvisi_qualita.append("Possibile domanda speculare: la logica deve essere spiegata chiaramente")

    errori_lingua, note_lingua = controlla_lingua_domanda(
        testo_domanda,
        opzioni,
        spiegazione,
    )

    errori_linguistici.extend(errori_lingua)
    note.extend(note_lingua)

    if regola_visiva:
        testo_regola = normalizza_testo(regola_visiva)
        errori_regola, note_regola = controlla_lingua_testo(testo_regola, "regola visiva")
        errori_linguistici.extend(errori_regola)
        note.extend(note_regola)

    return {
        "id": id_domanda,
        "domanda": testo_domanda,
        "problemi_tecnici": sorted(set(problemi_tecnici)),
        "avvisi_qualita": sorted(set(avvisi_qualita)),
        "errori_linguistici": sorted(set(errori_linguistici)),
        "note": sorted(set(note)),
        "immagini_trovate": immagini_trovate,
        "immagini_mancanti": immagini_mancanti,
    }


def trova_file_logica_visiva():
    trovati = []

    for percorso in CANDIDATI_LOGICA_VISIVA:
        if percorso.exists():
            trovati.append(percorso)

    return trovati


def analizza_file(percorso):
    risultato = {
        "nome": "Logica visiva",
        "percorso": str(percorso.relative_to(ROOT)),
        "file_esiste": percorso.exists(),
        "errore_file": "",
        "totale_domande": 0,
        "problemi_tecnici_totali": 0,
        "avvisi_qualita_totali": 0,
        "errori_linguistici_totali": 0,
        "note_totali": 0,
        "immagini_trovate_totali": 0,
        "immagini_mancanti_totali": 0,
        "domande_con_problemi_tecnici": [],
        "domande_con_avvisi_qualita": [],
        "domande_con_errori_linguistici": [],
    }

    try:
        dati = leggi_json(percorso)
        domande = estrai_lista_domande(dati)
    except Exception as errore:
        risultato["errore_file"] = str(errore)
        risultato["problemi_tecnici_totali"] = 1
        return risultato

    analizzate = [
        analizza_domanda_visiva(indice, domanda)
        for indice, domanda in enumerate(domande)
    ]

    risultato["totale_domande"] = len(analizzate)

    for domanda in analizzate:
        risultato["immagini_trovate_totali"] += len(domanda["immagini_trovate"])
        risultato["immagini_mancanti_totali"] += len(domanda["immagini_mancanti"])

        if domanda["problemi_tecnici"]:
            risultato["problemi_tecnici_totali"] += len(domanda["problemi_tecnici"])
            risultato["domande_con_problemi_tecnici"].append(domanda)

        if domanda["avvisi_qualita"]:
            risultato["avvisi_qualita_totali"] += len(domanda["avvisi_qualita"])
            risultato["domande_con_avvisi_qualita"].append(domanda)

        if domanda["errori_linguistici"]:
            risultato["errori_linguistici_totali"] += len(domanda["errori_linguistici"])
            risultato["domande_con_errori_linguistici"].append(domanda)

        if domanda["note"]:
            risultato["note_totali"] += len(domanda["note"])

    return risultato


def crea_report_markdown(risultati):
    righe = []

    righe.append("# Motore qualità logica visiva")
    righe.append("")
    righe.append("Questo report controlla struttura, immagini e qualità linguistica delle domande di logica visiva.")
    righe.append("")
    righe.append("Nota: questo è il motore visivo strutturale. In futuro può essere potenziato con analisi AI/Vision delle immagini.")
    righe.append("")

    totale_tecnici = sum(r["problemi_tecnici_totali"] for r in risultati)
    totale_avvisi = sum(r["avvisi_qualita_totali"] for r in risultati)
    totale_lingua = sum(r["errori_linguistici_totali"] for r in risultati)
    totale_note = sum(r["note_totali"] for r in risultati)
    totale_immagini_trovate = sum(r["immagini_trovate_totali"] for r in risultati)
    totale_immagini_mancanti = sum(r["immagini_mancanti_totali"] for r in risultati)

    righe.append("## Riepilogo")
    righe.append("")
    righe.append(f"- Problemi tecnici totali: **{totale_tecnici}**")
    righe.append(f"- Avvisi qualità totali: **{totale_avvisi}**")
    righe.append(f"- Errori linguistici totali: **{totale_lingua}**")
    righe.append(f"- Note linguistiche/informative totali: **{totale_note}**")
    righe.append(f"- Immagini trovate: **{totale_immagini_trovate}**")
    righe.append(f"- Immagini mancanti: **{totale_immagini_mancanti}**")
    righe.append("")

    for risultato in risultati:
        righe.append(f"## {risultato['nome']}")
        righe.append("")
        righe.append(f"File: `{risultato['percorso']}`")
        righe.append(f"Domande totali: **{risultato['totale_domande']}**")
        righe.append(f"Problemi tecnici: **{risultato['problemi_tecnici_totali']}**")
        righe.append(f"Avvisi qualità: **{risultato['avvisi_qualita_totali']}**")
        righe.append(f"Errori linguistici: **{risultato['errori_linguistici_totali']}**")
        righe.append(f"Note: **{risultato['note_totali']}**")
        righe.append(f"Immagini trovate: **{risultato['immagini_trovate_totali']}**")
        righe.append(f"Immagini mancanti: **{risultato['immagini_mancanti_totali']}**")
        righe.append("")

        if risultato["errore_file"]:
            righe.append(f"Errore file: **{risultato['errore_file']}**")
            righe.append("")
            continue

        if risultato["domande_con_problemi_tecnici"]:
            righe.append("### Problemi tecnici")
            righe.append("")

            for domanda in risultato["domande_con_problemi_tecnici"][:50]:
                righe.append(f"- **{domanda['id']}** — {domanda['domanda']}")
                for problema in domanda["problemi_tecnici"]:
                    righe.append(f"  - {problema}")

                for immagine in domanda["immagini_mancanti"][:10]:
                    righe.append(f"  - immagine mancante: `{immagine}`")

            righe.append("")

        if risultato["domande_con_avvisi_qualita"]:
            righe.append("### Avvisi qualità")
            righe.append("")

            for domanda in risultato["domande_con_avvisi_qualita"][:50]:
                righe.append(f"- **{domanda['id']}** — {domanda['domanda']}")
                for avviso in domanda["avvisi_qualita"]:
                    righe.append(f"  - {avviso}")

            righe.append("")

        if risultato["domande_con_errori_linguistici"]:
            righe.append("### Errori linguistici")
            righe.append("")

            for domanda in risultato["domande_con_errori_linguistici"][:50]:
                righe.append(f"- **{domanda['id']}** — {domanda['domanda']}")
                for errore in domanda["errori_linguistici"]:
                    righe.append(f"  - {errore}")

            righe.append("")

    return "\n".join(righe) + "\n"


def stampa_console(risultati):
    print("----- MOTORE QUALITÀ LOGICA VISIVA -----")

    for risultato in risultati:
        print()
        print(f"===== {risultato['nome']} =====")
        print(f"File: {risultato['percorso']}")

        if risultato["errore_file"]:
            print(f"ERRORE: {risultato['errore_file']}")

        print(f"Domande: {risultato['totale_domande']}")
        print(f"Problemi tecnici: {risultato['problemi_tecnici_totali']}")
        print(f"Avvisi qualità: {risultato['avvisi_qualita_totali']}")
        print(f"Errori linguistici: {risultato['errori_linguistici_totali']}")
        print(f"Note: {risultato['note_totali']}")
        print(f"Immagini trovate: {risultato['immagini_trovate_totali']}")
        print(f"Immagini mancanti: {risultato['immagini_mancanti_totali']}")

    print()
    print("Report creati:")
    print("- reports/motore_qualita_logica_visiva.md")
    print("- reports/motore_qualita_logica_visiva.json")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--fail-on-technical", action="store_true")
    parser.add_argument("--fail-on-quality", action="store_true")
    parser.add_argument("--fail-on-language", action="store_true")

    args = parser.parse_args()

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    file_logica_visiva = trova_file_logica_visiva()

    if not file_logica_visiva:
        risultati = [{
            "nome": "Logica visiva",
            "percorso": "NON_TROVATO",
            "file_esiste": False,
            "errore_file": "File logica visiva non trovato",
            "totale_domande": 0,
            "problemi_tecnici_totali": 1,
            "avvisi_qualita_totali": 0,
            "errori_linguistici_totali": 0,
            "note_totali": 0,
            "immagini_trovate_totali": 0,
            "immagini_mancanti_totali": 0,
            "domande_con_problemi_tecnici": [],
            "domande_con_avvisi_qualita": [],
            "domande_con_errori_linguistici": [],
        }]
    else:
        risultati = [
            analizza_file(percorso)
            for percorso in file_logica_visiva
        ]

    report_md = crea_report_markdown(risultati)

    (REPORTS_DIR / "motore_qualita_logica_visiva.md").write_text(report_md, encoding="utf-8")
    (REPORTS_DIR / "motore_qualita_logica_visiva.json").write_text(
        json.dumps(risultati, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    stampa_console(risultati)

    problemi_tecnici = sum(r["problemi_tecnici_totali"] for r in risultati)
    avvisi_qualita = sum(r["avvisi_qualita_totali"] for r in risultati)
    errori_lingua = sum(r["errori_linguistici_totali"] for r in risultati)

    if args.fail_on_technical and problemi_tecnici > 0:
        sys.exit(1)

    if args.fail_on_quality and avvisi_qualita > 0:
        sys.exit(1)

    if args.fail_on_language and errori_lingua > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
