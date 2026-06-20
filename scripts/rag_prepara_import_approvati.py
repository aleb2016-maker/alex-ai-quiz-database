from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path


CAMPI_DATABASE = [
    "id",
    "categoria",
    "livello",
    "domanda",
    "opzioni",
    "risposta_corretta",
    "spiegazione",
]

MAPPA_CATEGORIA_FILE = {
    "ai": "data/ai.json",
    "informatica": "data/informatica.json",
    "matematica": "data/matematica.json",
    "inglese": "data/inglese.json",
    "scienze": "data/scienze.json",
    "biologia": "data/biologia.json",
    "chimica": "data/chimica.json",
    "fisica": "data/fisica.json",
    "fisica_quantistica": "data/fisica_quantistica.json",
    "logica_numerica": "data/logica/logica_numerica.json",
    "logica_verbale": "data/logica/logica_verbale.json",
    "ragionamento_astratto": "data/logica/ragionamento_astratto.json",
    "ragionamento_critico": "data/logica/ragionamento_critico.json",
}


def carica_json(percorso: Path) -> dict:
    if not percorso.exists():
        raise SystemExit(f"File non trovato: {percorso}")

    dati = json.loads(percorso.read_text(encoding="utf-8"))

    if not isinstance(dati, dict):
        raise SystemExit("Il file review deve contenere un oggetto JSON.")

    return dati


def estrai_domande_review(dati: dict) -> list[dict]:
    if isinstance(dati.get("domande_da_revisionare"), list):
        return dati["domande_da_revisionare"]

    if isinstance(dati.get("domande"), list):
        return dati["domande"]

    raise SystemExit(
        "Nel file review non trovo `domande_da_revisionare` o `domande`."
    )


def domanda_approvata(domanda: dict) -> bool:
    checklist = domanda.get("checklist_review", {})

    if not isinstance(checklist, dict):
        return False

    return checklist.get("approvata_per_database_ufficiale") is True


def valida_domanda_approvata(domanda: dict, posizione: int) -> list[str]:
    problemi = []

    domanda_testo = str(domanda.get("domanda", "")).strip()
    risposta_corretta = str(domanda.get("risposta_corretta", "")).strip()
    spiegazione = str(domanda.get("spiegazione", "")).strip()
    opzioni = domanda.get("opzioni", [])

    if not domanda_testo:
        problemi.append(f"Domanda approvata {posizione}: testo domanda vuoto.")

    if not risposta_corretta:
        problemi.append(f"Domanda approvata {posizione}: risposta corretta vuota.")

    if not spiegazione:
        problemi.append(f"Domanda approvata {posizione}: spiegazione vuota.")

    if not isinstance(opzioni, list):
        problemi.append(f"Domanda approvata {posizione}: opzioni non è una lista.")
        return problemi

    if len(opzioni) != 4:
        problemi.append(
            f"Domanda approvata {posizione}: deve avere esattamente 4 opzioni."
        )

    opzioni_pulite = [
        str(opzione).strip()
        for opzione in opzioni
    ]

    if any(not opzione for opzione in opzioni_pulite):
        problemi.append(
            f"Domanda approvata {posizione}: una o più opzioni sono vuote."
        )

    if len(set(opzioni_pulite)) != len(opzioni_pulite):
        problemi.append(
            f"Domanda approvata {posizione}: ci sono opzioni duplicate."
        )

    if risposta_corretta and risposta_corretta not in opzioni_pulite:
        problemi.append(
            f"Domanda approvata {posizione}: risposta corretta non presente tra le opzioni."
        )

    checklist = domanda.get("checklist_review", {})

    controlli_obbligatori = [
        "fonte_rag_verificata",
        "domanda_chiara",
        "risposta_corretta_verificata",
        "tre_distrattori_forti",
        "spiegazione_didattica",
        "lingua_controllata",
        "approvata_per_database_ufficiale",
    ]

    for controllo in controlli_obbligatori:
        if checklist.get(controllo) is not True:
            problemi.append(
                f"Domanda approvata {posizione}: checklist non completata: {controllo}."
            )

    return problemi


def normalizza_per_database(domanda: dict, posizione: int) -> dict:
    id_finale = (
        str(domanda.get("id_finale", "")).strip()
        or str(domanda.get("id_originale", "")).strip()
        or str(domanda.get("id_review", "")).strip()
        or f"RAG-IMPORT-{posizione:04d}"
    )

    return {
        "id": id_finale,
        "categoria": str(domanda.get("categoria", "rag_generato")).strip(),
        "livello": str(domanda.get("livello", "intermedio")).strip(),
        "domanda": str(domanda.get("domanda", "")).strip(),
        "opzioni": [
            str(opzione).strip()
            for opzione in domanda.get("opzioni", [])
        ],
        "risposta_corretta": str(domanda.get("risposta_corretta", "")).strip(),
        "spiegazione": str(domanda.get("spiegazione", "")).strip(),
    }


def carica_database_ufficiale(percorso: Path) -> tuple[object, list[dict]]:
    if not percorso.exists():
        raise SystemExit(f"Database ufficiale non trovato: {percorso}")

    dati = json.loads(percorso.read_text(encoding="utf-8"))

    if isinstance(dati, list):
        return dati, dati

    if isinstance(dati, dict) and isinstance(dati.get("domande"), list):
        return dati, dati["domande"]

    raise SystemExit(
        f"Formato database non supportato per import automatico: {percorso}"
    )


def salva_database_ufficiale(percorso: Path, struttura_originale: object) -> None:
    percorso.write_text(
        json.dumps(struttura_originale, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def scegli_file_target(domande: list[dict], target_file: str | None) -> Path:
    if target_file:
        return Path(target_file)

    categorie = {
        str(domanda.get("categoria", "")).strip()
        for domanda in domande
        if str(domanda.get("categoria", "")).strip()
    }

    if len(categorie) != 1:
        raise SystemExit(
            "Per importare nel database ufficiale serve una sola categoria oppure --target-file."
        )

    categoria = next(iter(categorie))

    if categoria not in MAPPA_CATEGORIA_FILE:
        raise SystemExit(
            f"Categoria non mappata automaticamente: {categoria}. Usa --target-file."
        )

    return Path(MAPPA_CATEGORIA_FILE[categoria])


def crea_report(
    sorgente: Path,
    output: Path,
    approvate: list[dict],
    problemi: list[str],
    ha_scritto_database: bool,
    file_database: Path | None,
) -> str:
    stato = "BLOCCATO" if problemi else "OK"

    righe = [
        "# Import controllato domande RAG approvate",
        "",
        f"- File review sorgente: `{sorgente}`",
        f"- File preparazione import: `{output}`",
        f"- Domande approvate trovate: {len(approvate)}",
        f"- Stato: {stato}",
        f"- Scrittura database ufficiale: {'sì' if ha_scritto_database else 'no'}",
        "",
    ]

    if file_database:
        righe.append(f"- Database target: `{file_database}`")
        righe.append("")

    if problemi:
        righe.append("## Problemi")
        righe.append("")
        for problema in problemi:
            righe.append(f"- {problema}")
        righe.append("")

    if not approvate:
        righe.append("## Nota")
        righe.append("")
        righe.append(
            "Non ci sono ancora domande approvate. Questo è normale se la pipeline è stata eseguita in modalità sicura."
        )
        righe.append("")

    righe.append("## Regola di sicurezza")
    righe.append("")
    righe.append(
        "Questo script prepara l'importazione ma non scrive nei database ufficiali, salvo uso esplicito di `--scrivi-database --confermo-scrittura-data`."
    )
    righe.append("")

    return "\n".join(righe)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepara l'import controllato delle domande RAG approvate."
    )

    parser.add_argument(
        "--input",
        default="review/rag/quiz_da_revisionare.json",
    )
    parser.add_argument(
        "--output",
        default="review/rag/domande_approvate_pronte_per_import.json",
    )
    parser.add_argument(
        "--report",
        default="reports/rag_import_approvati.md",
    )
    parser.add_argument(
        "--target-file",
        default=None,
        help="File database ufficiale target. Esempio: data/ai.json",
    )
    parser.add_argument(
        "--scrivi-database",
        action="store_true",
        help="Scrive davvero nel database ufficiale. Da usare solo dopo review.",
    )
    parser.add_argument(
        "--confermo-scrittura-data",
        action="store_true",
        help="Conferma esplicita richiesta insieme a --scrivi-database.",
    )

    args = parser.parse_args()

    percorso_input = Path(args.input)
    percorso_output = Path(args.output)
    percorso_report = Path(args.report)

    dati_review = carica_json(percorso_input)
    domande_review = estrai_domande_review(dati_review)

    domande_approvate_raw = [
        domanda
        for domanda in domande_review
        if isinstance(domanda, dict) and domanda_approvata(domanda)
    ]

    problemi = []

    domande_pronte = []

    for posizione, domanda in enumerate(domande_approvate_raw, start=1):
        problemi.extend(
            valida_domanda_approvata(
                domanda=domanda,
                posizione=posizione,
            )
        )

        domande_pronte.append(
            normalizza_per_database(
                domanda=domanda,
                posizione=posizione,
            )
        )

    pacchetto_import = {
        "metadati": {
            "origine": "rag_review_approvata",
            "tipo": "preparazione_import_controllato",
            "file_review_sorgente": str(percorso_input),
            "numero_domande_approvate": len(domande_pronte),
            "scrittura_database_ufficiale": False,
            "regola": (
                "Solo le domande con checklist_review.approvata_per_database_ufficiale = true "
                "vengono preparate per l'import."
            ),
        },
        "domande_approvate": domande_pronte,
    }

    percorso_output.parent.mkdir(parents=True, exist_ok=True)
    percorso_output.write_text(
        json.dumps(pacchetto_import, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    file_database: Path | None = None
    ha_scritto_database = False

    if args.scrivi_database:
        if not args.confermo_scrittura_data:
            problemi.append(
                "Hai usato --scrivi-database ma manca --confermo-scrittura-data."
            )
        elif problemi:
            pass
        elif not domande_pronte:
            print("ℹ️ Nessuna domanda approvata da scrivere nel database.")
        else:
            file_database = scegli_file_target(
                domande=domande_pronte,
                target_file=args.target_file,
            )

            struttura_database, lista_domande_database = carica_database_ufficiale(
                file_database
            )

            ids_esistenti = {
                str(domanda.get("id", "")).strip()
                for domanda in lista_domande_database
                if isinstance(domanda, dict)
            }

            for domanda in domande_pronte:
                if domanda["id"] in ids_esistenti:
                    problemi.append(
                        f"ID già presente nel database ufficiale: {domanda['id']}."
                    )

            if not problemi:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                cartella_backup = Path("backups/rag_import")
                cartella_backup.mkdir(parents=True, exist_ok=True)

                backup = cartella_backup / f"{file_database.name}.{timestamp}.backup.json"
                shutil.copy2(file_database, backup)

                lista_domande_database.extend(domande_pronte)
                salva_database_ufficiale(file_database, struttura_database)

                ha_scritto_database = True
                print(f"✅ Database aggiornato: {file_database}")
                print(f"🛡️ Backup creato: {backup}")

    percorso_report.parent.mkdir(parents=True, exist_ok=True)
    percorso_report.write_text(
        crea_report(
            sorgente=percorso_input,
            output=percorso_output,
            approvate=domande_pronte,
            problemi=problemi,
            ha_scritto_database=ha_scritto_database,
            file_database=file_database,
        ),
        encoding="utf-8",
    )

    print("✅ Preparazione import approvati completata")
    print(f"📌 Domande approvate trovate: {len(domande_pronte)}")
    print(f"📌 File locale: {percorso_output}")
    print(f"📌 Report: {percorso_report}")

    if problemi:
        print("❌ Problemi trovati. Import bloccato.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
