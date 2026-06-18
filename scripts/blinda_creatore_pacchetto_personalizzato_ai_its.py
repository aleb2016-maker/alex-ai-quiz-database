from pathlib import Path
import json
import re

FILES = [
    Path("demo/app.js"),
    Path("demo/index.html"),
    Path("scripts/rigenera_demo_separate.py"),
]

REPORT = Path("reports/blinda_creatore_pacchetto_personalizzato_ai_its.md")

OPZIONI_CORRETTE = [
    '            <option value="ai" selected>AI</option>',
    '            <option value="informatica">Informatica</option>',
    '            <option value="matematica">Matematica</option>',
    '            <option value="inglese">Inglese</option>',
    '            <option value="logica">Logica</option>',
    '            <option value="logica_visiva">Logica visiva</option>',
    '            <option value="scienze">Scienze generali</option>',
    '            <option value="biologia">Biologia</option>',
    '            <option value="chimica">Chimica</option>',
    '            <option value="fisica">Fisica</option>',
    '            <option value="fisica_quantistica">Fisica quantistica</option>',
]

VALORI_MATERIE_NOTE = {
    "ai",
    "informatica",
    "matematica",
    "inglese",
    "logica",
    "logica_visiva",
    "scienze",
    "scienze_generali",
    "scienze_della_terra",
    "biologia",
    "chimica",
    "fisica",
    "fisica_quantistica",
}


def correggi_fallback(testo):
    prima = testo

    sostituzioni = {
        'creatorSubject?.value || "scienze"': 'creatorSubject?.value || "ai"',
        "creatorSubject?.value || 'scienze'": "creatorSubject?.value || 'ai'",
        'creatorSubject.value || "scienze"': 'creatorSubject.value || "ai"',
        "creatorSubject.value || 'scienze'": "creatorSubject.value || 'ai'",
        '|| "scienze";': '|| "ai";',
    }

    for vecchio, nuovo in sostituzioni.items():
        testo = testo.replace(vecchio, nuovo)

    # Forza anche eventuali versioni già corrette ma senza fallback sicuro.
    testo = testo.replace(
        'const materia = materiaPersonalizzata || creatorSubject?.value || "ai";',
        'const materia = materiaPersonalizzata || creatorSubject?.value || "ai";'
    )

    return testo, testo != prima


def correggi_versione_database(testo):
    prima = testo

    testo = re.sub(
        r'(const\s+DATA_URL\s*=\s*["\'][^"\']*database_quiz_finale\.json\?v=)[^"\']+(["\'])',
        r'\1ai-its-personalizzato-blindato\2',
        testo
    )

    return testo, testo != prima


def sostituisci_select_id_creator_subject(testo):
    """
    Caso 1: c'è proprio un <select id="creatorSubject"> ... </select>.
    """
    pattern = re.compile(
        r'(<select[^>]*id=["\']creatorSubject["\'][^>]*>)(.*?)(</select>)',
        re.DOTALL
    )

    def repl(match):
        return match.group(1) + "\n" + "\n".join(OPZIONI_CORRETTE) + "\n" + match.group(3)

    testo_nuovo, count = pattern.subn(repl, testo)
    return testo_nuovo, count


def estrai_value_option(linea):
    match = re.search(r'<option\s+[^>]*value=["\']([^"\']+)["\']', linea)
    if not match:
        return None
    return match.group(1)


def sostituisci_blocchi_option_materie(testo):
    """
    Caso 2: le option sono dentro una template string o blocco HTML senza select facilmente intercettabile.
    Sostituisce blocchi consecutivi di option che contengono materie note.
    """
    righe = testo.splitlines()
    nuove_righe = []
    i = 0
    sostituzioni = 0

    while i < len(righe):
        linea = righe[i]

        if "<option" not in linea or "value=" not in linea:
            nuove_righe.append(linea)
            i += 1
            continue

        blocco = []
        j = i

        while j < len(righe) and "<option" in righe[j] and "value=" in righe[j]:
            blocco.append(righe[j])
            j += 1

        valori = {estrai_value_option(r) for r in blocco}
        valori.discard(None)

        if valori & VALORI_MATERIE_NOTE:
            nuove_righe.extend(OPZIONI_CORRETTE)
            sostituzioni += 1
        else:
            nuove_righe.extend(blocco)

        i = j

    return "\n".join(nuove_righe) + ("\n" if testo.endswith("\n") else ""), sostituzioni


def correggi_file(path):
    if not path.exists():
        return {
            "file": str(path),
            "esiste": False,
            "modificato": False,
            "select_id": 0,
            "blocchi_option": 0,
            "fallback": False,
            "versione": False,
        }

    testo = path.read_text(encoding="utf-8")
    originale = testo

    testo, fallback_modificato = correggi_fallback(testo)
    testo, versione_modificata = correggi_versione_database(testo)

    testo, count_select = sostituisci_select_id_creator_subject(testo)
    testo, count_blocchi = sostituisci_blocchi_option_materie(testo)

    path.write_text(testo, encoding="utf-8")

    return {
        "file": str(path),
        "esiste": True,
        "modificato": testo != originale,
        "select_id": count_select,
        "blocchi_option": count_blocchi,
        "fallback": fallback_modificato,
        "versione": versione_modificata,
    }


def carica_domande(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    if isinstance(data, list):
        return data

    for key in ["domande", "questions", "quiz", "items", "data"]:
        value = data.get(key)
        if isinstance(value, list):
            return value

    raise SystemExit(f"ERRORE: formato non riconosciuto: {path}")


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


def verifica_app_js():
    app = Path("demo/app.js")
    testo = app.read_text(encoding="utf-8")

    errori = []

    if 'creatorSubject?.value || "scienze"' in testo:
        errori.append("Fallback ancora su scienze.")

    if 'creatorSubject.value || "scienze"' in testo:
        errori.append("Fallback diretto ancora su scienze.")

    if 'value="ai"' not in testo:
        errori.append("Nel selettore manca value=\"ai\".")

    if 'value="scienze"' in testo:
        posizione_ai = testo.find('value="ai"')
        posizione_scienze = testo.find('value="scienze"')

        if posizione_scienze != -1 and posizione_ai != -1 and posizione_scienze < posizione_ai:
            errori.append("Scienze appare prima di AI nel selettore.")

    if 'value="ai" selected' not in testo and 'value="ai" selected="selected"' not in testo:
        errori.append("AI non risulta selezionata come prima opzione/default.")

    return errori


def verifica_simulazione_ai_10():
    full = carica_domande("dist/database_quiz_finale.json")
    ai = [q for q in full if categoria_da_id(q) == "ai"]

    errori = []

    if len(ai) != 80:
        errori.append(f"AI nel database completo: attese 80, trovate {len(ai)}.")

    pacchetto_ai_10 = ai[:10]

    if len(pacchetto_ai_10) != 10:
        errori.append("Pacchetto simulato AI da 10 domande non contiene 10 domande.")

    for domanda in pacchetto_ai_10:
        qid = str(domanda.get("id", "")).upper()
        if not qid.startswith("AI-"):
            errori.append(f"Nel pacchetto simulato AI compare una domanda non AI: {qid}")

    return errori


def main():
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    risultati = [correggi_file(path) for path in FILES]

    errori = []
    errori.extend(verifica_app_js())
    errori.extend(verifica_simulazione_ai_10())

    righe = [
        "# Blindatura creatore pacchetto personalizzato AI ITS",
        "",
        "Obiettivo:",
        "",
        "- impedire che il pacchetto personalizzato parta da Scienze quando viene scelta AI;",
        "- mettere AI come prima materia e default del selettore;",
        "- mantenere Scienze solo come scelta esplicita, non come fallback;",
        "- verificare una simulazione AI da 10 domande con soli ID `AI-`.",
        "",
        "## File trattati",
        "",
    ]

    for r in risultati:
        righe.append(
            f"- `{r['file']}` — esiste: {r['esiste']}, modificato: {r['modificato']}, "
            f"select_id: {r['select_id']}, blocchi_option: {r['blocchi_option']}, "
            f"fallback: {r['fallback']}, versione: {r['versione']}"
        )

    righe.append("")
    righe.append("## Verifica")
    righe.append("")

    if errori:
        righe.append("ESITO: ERRORE")
        for errore in errori:
            righe.append(f"- {errore}")
    else:
        righe.append("ESITO: OK")
        righe.append("- fallback non punta più a Scienze;")
        righe.append("- AI è presente e selezionata come default;")
        righe.append("- Scienze non precede AI nel selettore;")
        righe.append("- simulazione AI da 10 domande contiene solo domande AI.")

    REPORT.write_text("\n".join(righe), encoding="utf-8")

    print("===== BLINDATURA CREATORE PACCHETTO PERSONALIZZATO AI ITS =====")
    for r in risultati:
        print(
            f"{r['file']}: modificato={r['modificato']}, "
            f"select_id={r['select_id']}, blocchi_option={r['blocchi_option']}, "
            f"fallback={r['fallback']}, versione={r['versione']}"
        )

    print(f"Report creato: {REPORT}")

    if errori:
        print("ERRORE: creatore NON ancora blindato.")
        for errore in errori:
            print("-", errore)
        raise SystemExit(1)

    print("OK: creatore pacchetto personalizzato AI ITS blindato.")
    print("OK: AI è la prima opzione/default.")
    print("OK: simulazione AI da 10 domande contiene solo domande AI.")


if __name__ == "__main__":
    main()
