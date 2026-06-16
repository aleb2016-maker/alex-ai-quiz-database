from pathlib import Path
from collections import Counter, defaultdict
from difflib import SequenceMatcher
import argparse
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"

MOTORI_SCIENZE = [
    ("Scienze generali", ROOT / "data" / "scienze.json"),
    ("Biologia", ROOT / "data" / "biologia.json"),
    ("Chimica", ROOT / "data" / "chimica.json"),
    ("Fisica", ROOT / "data" / "fisica.json"),
    ("Fisica quantistica", ROOT / "data" / "fisica_quantistica.json"),
]

MOTORI_AI = [
    ("AI", ROOT / "data" / "ai.json"),
]

# Queste sono parole davvero pericolose nei distrattori,
# perché spesso rendono l'opzione falsa troppo facile da eliminare.
PAROLE_DEBOLI_REALI = [
    "sempre",
    "mai",
]

# Queste parole possono essere sospette, ma non sono automaticamente errori.
# Per esempio "tutte le cellule" può essere una frase scientificamente corretta.
PAROLE_DA_NOTA_INFORMATIVA = [
    "tutti",
    "tutte",
    "nessuno",
    "nessuna",
    "qualsiasi",
    "completamente",
    "totalmente",
    "impossibile",
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

CHIAVI_LIVELLO = [
    "livello",
    "level",
    "difficulty",
]

CHIAVI_CATEGORIA = [
    "categoria",
    "category",
    "materia",
    "subject",
]


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


def primo_valore(domanda, chiavi, default=""):
    if not isinstance(domanda, dict):
        return default

    for chiave in chiavi:
        valore = domanda.get(chiave)
        if valore is not None:
            return valore

    return default


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


def estrai_opzioni(domanda):
    valore = primo_valore(domanda, CHIAVI_OPZIONI, default=[])

    if not isinstance(valore, list):
        return []

    return [
        normalizza_testo(opzione)
        for opzione in valore
    ]


def normalizza_per_confronto(testo):
    testo = normalizza_testo(testo).lower()
    testo = re.sub(r"[^\w\sàèéìòù]", " ", testo)
    testo = re.sub(r"\s+", " ", testo)
    return testo.strip()


def parole_presenti(testo, parole_da_cercare):
    testo_norm = normalizza_per_confronto(testo)
    parole = set(testo_norm.split())

    return [
        parola
        for parola in parole_da_cercare
        if parola in parole
    ]


def posizione_risposta(opzioni, risposta):
    for indice, opzione in enumerate(opzioni):
        if opzione == risposta:
            return "ABCD"[indice]

    return "NON_TROVATA"


def rapporto_similarita(a, b):
    return SequenceMatcher(
        None,
        normalizza_per_confronto(a),
        normalizza_per_confronto(b),
    ).ratio()


def opzioni_con_lunghezze_davvero_sbilanciate(opzioni):
    lunghezze = [
        len(opzione)
        for opzione in opzioni
        if opzione
    ]

    if len(lunghezze) != 4:
        return False

    lunghezza_minima = min(lunghezze)
    lunghezza_massima = max(lunghezze)

    if lunghezza_minima == 0:
        return False

    # Non segnaliamo le opzioni brevi quando sono tutte brevi.
    # Esempio scientifico valido: Newton / Joule / Watt / Pascal.
    if lunghezza_massima <= 25:
        return False

    # Segnaliamo solo squilibri forti, non differenze normali.
    rapporto = lunghezza_massima / lunghezza_minima

    return rapporto >= 4 and lunghezza_massima >= 70


def analizza_domanda(nome_motore, indice, domanda):
    problemi_tecnici = []
    avvisi_qualita_reali = []
    note_informative = []

    if not isinstance(domanda, dict):
        return {
            "id": f"indice_{indice}",
            "domanda": "",
            "categoria": "",
            "livello": "",
            "opzioni": [],
            "risposta_corretta": "",
            "posizione_risposta": "NON_TROVATA",
            "problemi_tecnici": ["Elemento domanda non è un oggetto JSON"],
            "avvisi_qualita_reali": [],
            "note_informative": [],
        }

    id_domanda = normalizza_testo(
        domanda.get("id")
        or domanda.get("codice")
        or f"{nome_motore}_{indice + 1}"
    )

    testo_domanda = normalizza_testo(primo_valore(domanda, CHIAVI_DOMANDA))
    categoria = normalizza_testo(primo_valore(domanda, CHIAVI_CATEGORIA))
    livello = normalizza_testo(primo_valore(domanda, CHIAVI_LIVELLO))
    opzioni = estrai_opzioni(domanda)
    risposta = normalizza_testo(primo_valore(domanda, CHIAVI_RISPOSTA))

    if not id_domanda:
        problemi_tecnici.append("ID domanda mancante")

    if not testo_domanda:
        problemi_tecnici.append("Testo domanda mancante")

    if not categoria:
        note_informative.append("Categoria mancante o vuota")

    if not livello:
        note_informative.append("Livello mancante o vuoto")

    if len(opzioni) != 4:
        problemi_tecnici.append(f"Numero opzioni non valido: trovate {len(opzioni)}, attese 4")

    opzioni_vuote = [
        numero + 1
        for numero, opzione in enumerate(opzioni)
        if not opzione
    ]

    if opzioni_vuote:
        problemi_tecnici.append(f"Opzioni vuote nelle posizioni: {opzioni_vuote}")

    if not risposta:
        problemi_tecnici.append("Risposta corretta mancante")

    if risposta and opzioni and risposta not in opzioni:
        problemi_tecnici.append("Risposta corretta non presente nelle opzioni")

    opzioni_normalizzate = [
        normalizza_per_confronto(opzione)
        for opzione in opzioni
    ]

    duplicati_opzioni = [
        opzione
        for opzione, conteggio in Counter(opzioni_normalizzate).items()
        if opzione and conteggio > 1
    ]

    if duplicati_opzioni:
        problemi_tecnici.append("Opzioni duplicate o identiche nello stesso quiz")

    posizione = posizione_risposta(opzioni, risposta)

    for opzione in opzioni:
        parole_deboli = parole_presenti(opzione, PAROLE_DEBOLI_REALI)

        if parole_deboli:
            avvisi_qualita_reali.append(
                "Possibile distrattore troppo assoluto: contiene "
                + ", ".join(f"“{parola}”" for parola in parole_deboli)
            )

        parole_da_nota = parole_presenti(opzione, PAROLE_DA_NOTA_INFORMATIVA)

        if parole_da_nota:
            note_informative.append(
                "Nota: contiene parola da controllare solo se rende l’opzione troppo facile: "
                + ", ".join(f"“{parola}”" for parola in parole_da_nota)
            )

    if opzioni_con_lunghezze_davvero_sbilanciate(opzioni):
        avvisi_qualita_reali.append("Opzioni con lunghezze davvero molto sbilanciate")

    return {
        "id": id_domanda,
        "domanda": testo_domanda,
        "categoria": categoria,
        "livello": livello,
        "opzioni": opzioni,
        "risposta_corretta": risposta,
        "posizione_risposta": posizione,
        "problemi_tecnici": problemi_tecnici,
        "avvisi_qualita_reali": sorted(set(avvisi_qualita_reali)),
        "note_informative": sorted(set(note_informative)),
    }


def trova_duplicati_e_simili(domande_analizzate, soglia_similarita):
    domande_per_testo = defaultdict(list)

    for domanda in domande_analizzate:
        testo = normalizza_per_confronto(domanda["domanda"])
        if testo:
            domande_per_testo[testo].append(domanda["id"])

    duplicati_identici = {
        testo: ids
        for testo, ids in domande_per_testo.items()
        if len(ids) > 1
    }

    domande_simili = []

    for indice_a, domanda_a in enumerate(domande_analizzate):
        for domanda_b in domande_analizzate[indice_a + 1:]:
            if not domanda_a["domanda"] or not domanda_b["domanda"]:
                continue

            testo_a = normalizza_per_confronto(domanda_a["domanda"])
            testo_b = normalizza_per_confronto(domanda_b["domanda"])

            if testo_a == testo_b:
                continue

            similarita = rapporto_similarita(domanda_a["domanda"], domanda_b["domanda"])

            if similarita >= soglia_similarita:
                domande_simili.append({
                    "id_1": domanda_a["id"],
                    "id_2": domanda_b["id"],
                    "similarita": round(similarita, 3),
                    "domanda_1": domanda_a["domanda"],
                    "domanda_2": domanda_b["domanda"],
                })

    return duplicati_identici, domande_simili


def analizza_motore(nome_motore, percorso, soglia_similarita):
    risultato = {
        "nome": nome_motore,
        "percorso": str(percorso.relative_to(ROOT)),
        "file_esiste": percorso.exists(),
        "errore_file": "",
        "totale_domande": 0,
        "livelli": {},
        "categorie": {},
        "posizioni_risposta": {},
        "problemi_tecnici_totali": 0,
        "avvisi_qualita_reali_totali": 0,
        "note_informative_totali": 0,
        "domande_con_problemi_tecnici": [],
        "domande_con_avvisi_qualita_reali": [],
        "domande_con_note_informative": [],
        "duplicati_identici": {},
        "domande_simili": [],
    }

    if not percorso.exists():
        risultato["errore_file"] = "File non trovato"
        risultato["problemi_tecnici_totali"] = 1
        return risultato

    try:
        dati = leggi_json(percorso)
        domande = estrai_lista_domande(dati)
    except Exception as errore:
        risultato["errore_file"] = str(errore)
        risultato["problemi_tecnici_totali"] = 1
        return risultato

    domande_analizzate = [
        analizza_domanda(nome_motore, indice, domanda)
        for indice, domanda in enumerate(domande)
    ]

    risultato["totale_domande"] = len(domande_analizzate)
    risultato["livelli"] = dict(Counter(domanda["livello"] for domanda in domande_analizzate))
    risultato["categorie"] = dict(Counter(domanda["categoria"] for domanda in domande_analizzate))
    risultato["posizioni_risposta"] = dict(Counter(domanda["posizione_risposta"] for domanda in domande_analizzate))

    for domanda in domande_analizzate:
        if domanda["problemi_tecnici"]:
            risultato["problemi_tecnici_totali"] += len(domanda["problemi_tecnici"])
            risultato["domande_con_problemi_tecnici"].append(domanda)

        if domanda["avvisi_qualita_reali"]:
            risultato["avvisi_qualita_reali_totali"] += len(domanda["avvisi_qualita_reali"])
            risultato["domande_con_avvisi_qualita_reali"].append(domanda)

        if domanda["note_informative"]:
            risultato["note_informative_totali"] += len(domanda["note_informative"])
            risultato["domande_con_note_informative"].append(domanda)

    duplicati_identici, domande_simili = trova_duplicati_e_simili(
        domande_analizzate,
        soglia_similarita,
    )

    risultato["duplicati_identici"] = duplicati_identici
    risultato["domande_simili"] = domande_simili

    return risultato


def motori_per_area(area):
    if area == "scienze":
        return MOTORI_SCIENZE

    if area == "ai":
        return MOTORI_AI

    if area == "tutto":
        return MOTORI_SCIENZE + MOTORI_AI

    raise ValueError(f"Area non riconosciuta: {area}")


def crea_report_markdown(risultati, area):
    righe = []

    righe.append("# Motore qualità generale quiz")
    righe.append("")
    righe.append(f"Area controllata: **{area}**")
    righe.append("")
    righe.append("Questo report distingue tra problemi tecnici veri, avvisi qualità reali e semplici note informative.")
    righe.append("")

    totale_tecnici = sum(r["problemi_tecnici_totali"] for r in risultati)
    totale_avvisi = sum(r["avvisi_qualita_reali_totali"] for r in risultati)
    totale_note = sum(r["note_informative_totali"] for r in risultati)
    totale_duplicati = sum(len(r["duplicati_identici"]) for r in risultati)
    totale_simili = sum(len(r["domande_simili"]) for r in risultati)

    righe.append("## Riepilogo generale")
    righe.append("")
    righe.append(f"- Problemi tecnici totali: **{totale_tecnici}**")
    righe.append(f"- Avvisi qualità reali totali: **{totale_avvisi}**")
    righe.append(f"- Note informative totali: **{totale_note}**")
    righe.append(f"- Gruppi di domande duplicate identiche: **{totale_duplicati}**")
    righe.append(f"- Coppie di domande molto simili: **{totale_simili}**")
    righe.append("")

    for risultato in risultati:
        righe.append(f"## {risultato['nome']}")
        righe.append("")
        righe.append(f"File: `{risultato['percorso']}`")
        righe.append(f"File trovato: **{risultato['file_esiste']}**")

        if risultato["errore_file"]:
            righe.append(f"Errore file: **{risultato['errore_file']}**")
            righe.append("")
            continue

        righe.append(f"Domande totali: **{risultato['totale_domande']}**")
        righe.append(f"Livelli: `{risultato['livelli']}`")
        righe.append(f"Categorie: `{risultato['categorie']}`")
        righe.append(f"Posizione risposta corretta nel sorgente: `{risultato['posizioni_risposta']}`")
        righe.append(f"Problemi tecnici: **{risultato['problemi_tecnici_totali']}**")
        righe.append(f"Avvisi qualità reali: **{risultato['avvisi_qualita_reali_totali']}**")
        righe.append(f"Note informative: **{risultato['note_informative_totali']}**")
        righe.append(f"Duplicati identici: **{len(risultato['duplicati_identici'])}**")
        righe.append(f"Domande molto simili: **{len(risultato['domande_simili'])}**")
        righe.append("")

        if risultato["domande_con_problemi_tecnici"]:
            righe.append("### Problemi tecnici")
            righe.append("")

            for domanda in risultato["domande_con_problemi_tecnici"][:40]:
                righe.append(f"- **{domanda['id']}** — {domanda['domanda']}")
                for problema in domanda["problemi_tecnici"]:
                    righe.append(f"  - {problema}")

            righe.append("")

        if risultato["domande_con_avvisi_qualita_reali"]:
            righe.append("### Avvisi qualità reali")
            righe.append("")

            for domanda in risultato["domande_con_avvisi_qualita_reali"][:40]:
                righe.append(f"- **{domanda['id']}** — {domanda['domanda']}")
                for avviso in domanda["avvisi_qualita_reali"]:
                    righe.append(f"  - {avviso}")

            righe.append("")

        if risultato["duplicati_identici"]:
            righe.append("### Domande duplicate identiche")
            righe.append("")

            for testo, ids in list(risultato["duplicati_identici"].items())[:20]:
                righe.append(f"- `{ids}` — {testo}")

            righe.append("")

        if risultato["domande_simili"]:
            righe.append("### Domande molto simili")
            righe.append("")

            for coppia in risultato["domande_simili"][:30]:
                righe.append(
                    f"- **{coppia['id_1']}** / **{coppia['id_2']}** "
                    f"— similarità `{coppia['similarita']}`"
                )
                righe.append(f"  - {coppia['domanda_1']}")
                righe.append(f"  - {coppia['domanda_2']}")

            righe.append("")

    return "\n".join(righe) + "\n"


def stampa_riepilogo_console(risultati):
    print("----- MOTORE QUALITÀ GENERALE -----")

    for risultato in risultati:
        print()
        print(f"===== {risultato['nome']} =====")
        print(f"File: {risultato['percorso']}")

        if risultato["errore_file"]:
            print(f"ERRORE: {risultato['errore_file']}")
            continue

        print(f"Domande: {risultato['totale_domande']}")
        print(f"Livelli: {risultato['livelli']}")
        print(f"Categorie: {risultato['categorie']}")
        print(f"Posizione risposta corretta: {risultato['posizioni_risposta']}")
        print(f"Problemi tecnici: {risultato['problemi_tecnici_totali']}")
        print(f"Avvisi qualità reali: {risultato['avvisi_qualita_reali_totali']}")
        print(f"Note informative: {risultato['note_informative_totali']}")
        print(f"Duplicati identici: {len(risultato['duplicati_identici'])}")
        print(f"Domande molto simili: {len(risultato['domande_simili'])}")

    print()
    print("Report creati:")
    print("- reports/motore_qualita_generale.md")
    print("- reports/motore_qualita_generale.json")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--area",
        choices=["scienze", "ai", "tutto"],
        default="tutto",
        help="Area da controllare: scienze, ai oppure tutto.",
    )

    parser.add_argument(
        "--soglia-similarita",
        type=float,
        default=0.88,
        help="Soglia per segnalare domande molto simili.",
    )

    parser.add_argument(
        "--fail-on-technical",
        action="store_true",
        help="Chiude con errore se trova problemi tecnici veri.",
    )

    parser.add_argument(
        "--fail-on-quality",
        action="store_true",
        help="Chiude con errore se trova avvisi qualità reali.",
    )

    args = parser.parse_args()

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    risultati = [
        analizza_motore(nome, percorso, args.soglia_similarita)
        for nome, percorso in motori_per_area(args.area)
    ]

    report_md = crea_report_markdown(risultati, args.area)

    report_md_path = REPORTS_DIR / "motore_qualita_generale.md"
    report_json_path = REPORTS_DIR / "motore_qualita_generale.json"

    report_md_path.write_text(report_md, encoding="utf-8")
    report_json_path.write_text(
        json.dumps(risultati, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    stampa_riepilogo_console(risultati)

    problemi_tecnici = sum(r["problemi_tecnici_totali"] for r in risultati)
    avvisi_qualita = sum(r["avvisi_qualita_reali_totali"] for r in risultati)

    if args.fail_on_technical and problemi_tecnici > 0:
        sys.exit(1)

    if args.fail_on_quality and avvisi_qualita > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
