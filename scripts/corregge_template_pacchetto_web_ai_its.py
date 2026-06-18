from pathlib import Path
import re

TARGET = Path("scripts/create_quiz_package.py")
REPORT = Path("reports/correzione_template_pacchetto_web_ai_its.md")

MARKER = "# === BLINDATURA INTERFACCIA WEB AI ITS ==="

HELPER = r"""
# === BLINDATURA INTERFACCIA WEB AI ITS ===
def blinda_interfaccia_web_generata_ai_its(output_dir):
    from pathlib import Path as _Path
    import json as _json
    import re as _re

    output_dir = _Path(output_dir)

    possibili_database = [
        output_dir / "database_quiz.json",
        output_dir / "SOLO_FILE_DA_COPIARE_WEB" / "database_quiz.json",
    ]

    database_path = None

    for candidato in possibili_database:
        if candidato.exists():
            database_path = candidato
            break

    if database_path is None:
        return

    try:
        dati = _json.loads(database_path.read_text(encoding="utf-8"))
    except Exception:
        return

    if isinstance(dati, list):
        domande = dati
    elif isinstance(dati, dict):
        domande = []
        for chiave in ["domande", "questions", "quiz", "items", "data"]:
            valore = dati.get(chiave)
            if isinstance(valore, list):
                domande = valore
                break
    else:
        domande = []

    if not domande:
        return

    def categoria_da_id(domanda):
        qid = str(domanda.get("id", "")).upper()

        if qid.startswith("AI-"):
            return "ai"
        if qid.startswith("INF-"):
            return "informatica"
        if qid.startswith("ING-"):
            return "inglese"
        if qid.startswith("MAT-"):
            return "matematica"
        if qid.startswith("LOG-VIS-"):
            return "logica_visiva"
        if qid.startswith(("LOG-NUM-", "LOG-VER-", "LOG-AST-", "LOG-CRI-")):
            return "logica"
        if qid.startswith(("SCI-", "BIO-", "CHI-", "FIS-", "FQ-")):
            return "scienze"

        return "altro"

    categorie = {categoria_da_id(domanda) for domanda in domande}
    categorie.discard("altro")

    categorie_ai_its = {
        "ai",
        "informatica",
        "matematica",
        "inglese",
        "logica",
        "logica_visiva",
    }

    if "scienze" in categorie:
        return

    if not categorie or not categorie.issubset(categorie_ai_its):
        return

    if categorie == {"ai"}:
        titolo = "Quiz AI"
        etichetta_materia = "AI"
    elif categorie == {"informatica"}:
        titolo = "Quiz Informatica"
        etichetta_materia = "Informatica"
    elif categorie == {"matematica"}:
        titolo = "Quiz Matematica"
        etichetta_materia = "Matematica"
    elif categorie == {"inglese"}:
        titolo = "Quiz Inglese"
        etichetta_materia = "Inglese"
    elif categorie == {"logica"}:
        titolo = "Quiz Logica"
        etichetta_materia = "Logica"
    elif categorie == {"logica_visiva"}:
        titolo = "Quiz Logica visiva"
        etichetta_materia = "Logica visiva"
    else:
        titolo = "Quiz AI ITS"
        etichetta_materia = "Materie AI ITS - tutte"

    nuova_descrizione = (
        "Scegli numero di domande e difficoltà. "
        "Il pacchetto contiene domande AI ITS e il quiz parte solo con le domande selezionate."
    )

    nuova_opzione = f'<option value="tutte" selected>{etichetta_materia}</option>'

    html_files = []

    for nome in ["index.html", "1_APRI_QUIZ.html"]:
        html_files.extend(output_dir.rglob(nome))

    for html_file in sorted(set(html_files)):
        testo = html_file.read_text(encoding="utf-8", errors="ignore")
        originale = testo

        testo = _re.sub(
            r"<title>.*?</title>",
            f"<title>{titolo}</title>",
            testo,
            count=1,
            flags=_re.IGNORECASE | _re.DOTALL,
        )

        testo = _re.sub(
            r"<h1[^>]*>.*?</h1>",
            f"<h1>{titolo}</h1>",
            testo,
            count=1,
            flags=_re.IGNORECASE | _re.DOTALL,
        )

        testo = testo.replace(
            "Scegli materia scientifica, numero di domande e difficoltà. "
            "Il pacchetto contiene il database completo, ma il quiz parte solo "
            "con le domande che scegli.",
            nuova_descrizione,
        )

        testo = testo.replace(
            "Scegli materia scientifica, numero di domande e difficoltà.",
            nuova_descrizione,
        )

        blocco_scienze = _re.compile(
            r'\s*<option\s+value=["\']materie_scientifiche["\'][^>]*>.*?</option>'
            r'\s*<option\s+value=["\']scienze_generali["\'][^>]*>.*?</option>'
            r'\s*<option\s+value=["\']fisica["\'][^>]*>.*?</option>'
            r'\s*<option\s+value=["\']chimica["\'][^>]*>.*?</option>'
            r'\s*<option\s+value=["\']biologia["\'][^>]*>.*?</option>'
            r'(?:\s*<option\s+value=["\']fisica_quantistica["\'][^>]*>.*?</option>)?',
            flags=_re.IGNORECASE | _re.DOTALL,
        )

        testo = blocco_scienze.sub("\n            " + nuova_opzione, testo)

        testo = testo.replace("Quiz Scienze", titolo)
        testo = testo.replace("Materie scientifiche - tutte", etichetta_materia)
        testo = testo.replace("Scienze generali", etichetta_materia)

        if testo != originale:
            html_file.write_text(testo, encoding="utf-8")
"""


def main():
    if not TARGET.exists():
        raise SystemExit(f"ERRORE: file non trovato: {TARGET}")

    testo = TARGET.read_text(encoding="utf-8")
    originale = testo

    helper_inserito = False
    call_inserita = False

    if MARKER not in testo:
        posizione = testo.find("\ndef ")

        if posizione == -1:
            raise SystemExit("ERRORE: non trovo dove inserire la funzione helper.")

        testo = testo[:posizione] + "\n\n" + HELPER + "\n" + testo[posizione:]
        helper_inserito = True

    if "blinda_interfaccia_web_generata_ai_its(output_dir)" not in testo:
        pattern = re.compile(
            r'(?m)^([ \t]*)zip_path = output_dir\.with_suffix\(["\']\.zip["\']\)'
        )

        match = pattern.search(testo)

        if not match:
            raise SystemExit("ERRORE: non trovo la riga zip_path = output_dir.with_suffix('.zip').")

        indent = match.group(1)
        riga_originale = match.group(0)

        testo = pattern.sub(
            indent + "blinda_interfaccia_web_generata_ai_its(output_dir)\n" + riga_originale,
            testo,
            count=1,
        )

        call_inserita = True

    TARGET.write_text(testo, encoding="utf-8")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "\n".join([
            "# Correzione template pacchetto web AI ITS",
            "",
            f"File corretto: `{TARGET}`",
            "",
            f"Helper inserito: {helper_inserito}",
            f"Chiamata prima dello zip inserita: {call_inserita}",
            f"File modificato: {testo != originale}",
            "",
            "Obiettivo:",
            "",
            "- se il pacchetto web generato contiene solo domande AI ITS, l'interfaccia non deve più mostrare Quiz Scienze;",
            "- se il pacchetto contiene solo AI, il titolo deve diventare Quiz AI;",
            "- il menu non deve più mostrare Materie scientifiche, Fisica, Chimica o Biologia.",
            "",
        ]),
        encoding="utf-8",
    )

    print("===== CORREZIONE TEMPLATE PACCHETTO WEB AI ITS =====")
    print(f"Helper inserito: {helper_inserito}")
    print(f"Chiamata prima dello zip inserita: {call_inserita}")
    print(f"File modificato: {testo != originale}")
    print(f"Report: {REPORT}")
    print("OK: create_quiz_package.py corretto.")


if __name__ == "__main__":
    main()
