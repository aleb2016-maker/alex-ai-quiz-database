from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"

FILE_LOGICA_VISIVA = ROOT / "data" / "logica" / "logica_visiva.json"
REPORT_JSON = ROOT / "reports" / "motore_qualita_logica_visiva.json"
OUTPUT_MD = ROOT / "reports" / "diagnosi_logica_visiva_dettagliata.md"


def leggi_json(percorso):
    return json.loads(percorso.read_text(encoding="utf-8"))


def estrai_domande(dati):
    if isinstance(dati, list):
        return dati

    for chiave in ["domande", "questions", "quiz", "items", "data", "database"]:
        valore = dati.get(chiave)
        if isinstance(valore, list):
            return valore

    return []


def testo(valore):
    if valore is None:
        return ""

    if isinstance(valore, str):
        return valore.strip()

    return json.dumps(valore, ensure_ascii=False)


def prendi(domanda, chiavi):
    for chiave in chiavi:
        if chiave in domanda:
            return domanda.get(chiave)

    return ""


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    dati_logica = leggi_json(FILE_LOGICA_VISIVA)
    domande = estrai_domande(dati_logica)

    dati_report = leggi_json(REPORT_JSON)
    risultato = dati_report[0]

    problemi_per_id = {}

    for domanda in risultato.get("domande_con_problemi_tecnici", []):
        problemi_per_id.setdefault(domanda["id"], {
            "problemi": [],
            "avvisi": [],
            "errori_linguistici": [],
        })

        problemi_per_id[domanda["id"]]["problemi"].extend(
            domanda.get("problemi_tecnici", [])
        )

    for domanda in risultato.get("domande_con_avvisi_qualita", []):
        problemi_per_id.setdefault(domanda["id"], {
            "problemi": [],
            "avvisi": [],
            "errori_linguistici": [],
        })

        problemi_per_id[domanda["id"]]["avvisi"].extend(
            domanda.get("avvisi_qualita", [])
        )

    for domanda in risultato.get("domande_con_errori_linguistici", []):
        problemi_per_id.setdefault(domanda["id"], {
            "problemi": [],
            "avvisi": [],
            "errori_linguistici": [],
        })

        problemi_per_id[domanda["id"]]["errori_linguistici"].extend(
            domanda.get("errori_linguistici", [])
        )

    righe = []

    righe.append("# Diagnosi dettagliata logica visiva")
    righe.append("")
    righe.append("Questo file serve per correggere i 33 avvisi della logica visiva senza andare a tentativi.")
    righe.append("")
    righe.append("## Riepilogo motore")
    righe.append("")
    righe.append(f"- Domande totali: **{risultato.get('totale_domande', 0)}**")
    righe.append(f"- Problemi tecnici: **{risultato.get('problemi_tecnici_totali', 0)}**")
    righe.append(f"- Avvisi qualità: **{risultato.get('avvisi_qualita_totali', 0)}**")
    righe.append(f"- Errori linguistici: **{risultato.get('errori_linguistici_totali', 0)}**")
    righe.append(f"- Immagini trovate: **{risultato.get('immagini_trovate_totali', 0)}**")
    righe.append(f"- Immagini mancanti: **{risultato.get('immagini_mancanti_totali', 0)}**")
    righe.append("")

    righe.append("## Domande con avvisi da correggere")
    righe.append("")

    totale_domande_con_avvisi = 0

    for indice, domanda in enumerate(domande, start=1):
        id_domanda = testo(
            domanda.get("id")
            or domanda.get("codice")
            or f"LV_{indice}"
        )

        if id_domanda not in problemi_per_id:
            continue

        totale_domande_con_avvisi += 1

        domanda_testo = testo(
            prendi(domanda, ["domanda", "question", "testo", "text", "prompt"])
        )

        risposta = testo(
            prendi(domanda, ["risposta_corretta", "correct_answer", "correct", "answer", "soluzione"])
        )

        spiegazione = testo(
            prendi(domanda, ["spiegazione", "explanation", "motivo"])
        )

        regola = prendi(domanda, ["regola_visiva", "visual_logic", "regola", "pattern", "logica", "trasformazione"])

        opzioni = prendi(domanda, ["opzioni", "options", "risposte", "answers"])

        righe.append(f"### {id_domanda}")
        righe.append("")
        righe.append(f"Domanda: {domanda_testo}")
        righe.append("")
        righe.append(f"Risposta corretta: `{risposta}`")
        righe.append("")

        if isinstance(opzioni, list):
            righe.append("Opzioni:")
            for numero, opzione in enumerate(opzioni, start=1):
                lettera = "ABCD"[numero - 1] if numero <= 4 else str(numero)
                righe.append(f"- {lettera}: {testo(opzione)}")
            righe.append("")

        righe.append("Avvisi/problemi trovati:")
        for problema in problemi_per_id[id_domanda]["problemi"]:
            righe.append(f"- PROBLEMA TECNICO: {problema}")

        for avviso in problemi_per_id[id_domanda]["avvisi"]:
            righe.append(f"- AVVISO QUALITÀ: {avviso}")

        for errore in problemi_per_id[id_domanda]["errori_linguistici"]:
            righe.append(f"- ERRORE LINGUISTICO: {errore}")

        righe.append("")

        righe.append("Regola visiva attuale:")
        if regola:
            righe.append("```json")
            righe.append(json.dumps(regola, ensure_ascii=False, indent=2))
            righe.append("```")
        else:
            righe.append("_Mancante_")

        righe.append("")

        righe.append("Spiegazione attuale:")
        if spiegazione:
            righe.append(spiegazione)
        else:
            righe.append("_Mancante_")

        righe.append("")
        righe.append("Campi presenti nel JSON:")
        righe.append("```text")
        righe.append(", ".join(sorted(domanda.keys())))
        righe.append("```")
        righe.append("")

    righe.insert(
        12,
        f"- Domande con almeno un avviso/problema: **{totale_domande_con_avvisi}**"
    )

    OUTPUT_MD.write_text("\n".join(righe) + "\n", encoding="utf-8")

    print("Creato report dettagliato:")
    print("- reports/diagnosi_logica_visiva_dettagliata.md")


if __name__ == "__main__":
    main()
