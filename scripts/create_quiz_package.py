import argparse
import json
import random
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "dist" / "database_quiz_finale.json"
OUTPUT_ROOT = ROOT / "dist" / "generated"
RUNTIME_ANDROID = ROOT / "runtime" / "android"
RUNTIME_WEB = ROOT / "runtime" / "web"



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


def slug(testo):
    return (
        str(testo or "")
        .strip()
        .lower()
        .replace("à", "a")
        .replace("è", "e")
        .replace("é", "e")
        .replace("ì", "i")
        .replace("ò", "o")
        .replace("ù", "u")
        .replace(" ", "_")
        .replace("-", "_")
    )

def carica_database():
    dati = json.loads(DATABASE_PATH.read_text(encoding="utf-8"))

    if isinstance(dati, list):
        return dati

    if isinstance(dati, dict):
        if isinstance(dati.get("quiz"), list):
            return dati["quiz"]
        if isinstance(dati.get("domande"), list):
            return dati["domande"]

    raise ValueError("Formato database non riconosciuto.")

def materia_ok(domanda, materia):
    if materia == "tutte":
        return True

    materia = slug(materia)
    categoria = slug(domanda.get("categoria", ""))
    sottocategoria = slug(domanda.get("sottocategoria", ""))
    tags = domanda.get("tags", [])

    if isinstance(tags, list):
        tags = [slug(tag) for tag in tags]
    else:
        tags = []

    if materia in [categoria, sottocategoria] or materia in tags:
        return True

    if materia == "fisica":
        return "fisica" in sottocategoria or any("fisica" in tag for tag in tags)

    if materia == "chimica":
        return "chimica" in sottocategoria or any("chimica" in tag for tag in tags)

    if materia == "biologia":
        return "biologia" in sottocategoria or any("biologia" in tag for tag in tags)

    return False

def prepara_domande(materia, livello, numero):
    database = carica_database()

    domande = [
        domanda for domanda in database
        if materia_ok(domanda, materia)
        and (livello == "tutti" or domanda.get("livello") == livello)
    ]

    if not domande:
        raise ValueError("Nessuna domanda trovata con questi filtri.")

    random.shuffle(domande)

    if numero != "all":
        domande = domande[:int(numero)]

    return domande



def crea_file_web_pronto(output_dir):
    file_principale = output_dir / "1_APRI_QUIZ.html"

    if not file_principale.exists():
        file_principale = output_dir / "index.html"

    if not file_principale.exists():
        raise FileNotFoundError("Non trovo il file HTML principale del quiz web.")

    file_facile = output_dir / "00_QUIZ_WEB_PRONTO.html"
    shutil.copy2(file_principale, file_facile)

    istruzioni = """<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <title>Leggimi prima - Quiz Web</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 850px;
      margin: 40px auto;
      padding: 24px;
      line-height: 1.6;
      background: #f7f9fc;
      color: #172033;
    }
    .box {
      background: white;
      border-radius: 18px;
      padding: 28px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    }
    code {
      background: #eef2ff;
      padding: 4px 8px;
      border-radius: 8px;
      font-weight: bold;
    }
    .start {
      display: inline-block;
      margin-top: 18px;
      padding: 14px 20px;
      background: #00c853;
      color: white;
      border-radius: 12px;
      text-decoration: none;
      font-weight: bold;
    }
  </style>
</head>
<body>
  <div class="box">
    <h1>Quiz Web pronto</h1>

    <p>Per provare subito il quiz, apri questo file:</p>

    <p><code>00_QUIZ_WEB_PRONTO.html</code></p>

    <p>Questo pacchetto contiene anche:</p>

    <ul>
      <li><code>database_quiz.json</code> - database delle domande</li>
      <li><code>quiz-engine.js</code> - motore web riutilizzabile</li>
      <li><code>README_WEB_ENGINE.md</code> - spiegazione tecnica per sviluppatori</li>
    </ul>

    <a class="start" href="00_QUIZ_WEB_PRONTO.html">Apri il quiz</a>
  </div>
</body>
</html>
"""
    (output_dir / "README_LEGGIMI.html").write_text(istruzioni, encoding="utf-8")


def crea_istruzioni_android(output_dir):
    from pathlib import Path
    import os
    import shutil

    output_dir = Path(output_dir)

    cartella_tecnica = output_dir / "3_FILE_TECNICI"

    if cartella_tecnica.exists():
        shutil.rmtree(cartella_tecnica)

    assets_dest = cartella_tecnica / "app/src/main/assets"
    kotlin_dest = cartella_tecnica / "app/src/main/java/com/alex/quizengine"

    assets_dest.mkdir(parents=True, exist_ok=True)
    kotlin_dest.mkdir(parents=True, exist_ok=True)

    database_sorgenti = [
        output_dir / "app/src/main/assets/database_quiz.json",
        output_dir / "database_quiz.json",
    ]

    for database_sorgente in database_sorgenti:
        if database_sorgente.exists():
            shutil.copy2(database_sorgente, assets_dest / "database_quiz.json")
            break
    else:
        raise FileNotFoundError("database_quiz.json non trovato")

    motore_sorgente = output_dir / "quiz_engine_android/kotlin/com/alex/quizengine"

    if not motore_sorgente.exists():
        raise FileNotFoundError("cartella Kotlin quizengine non trovata")

    for file_kt in motore_sorgente.glob("*.kt"):
        shutil.copy2(file_kt, kotlin_dest / file_kt.name)

    html = """<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <title>01 APRI PRIMA LE ISTRUZIONI</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 24px; line-height: 1.6; background: #f8fafc; color: #111827; }
    .box { background: white; border-radius: 18px; padding: 28px; box-shadow: 0 12px 30px rgba(0,0,0,0.10); }
    .alert { background: #fff7ed; border: 1px solid #fb923c; color: #9a3412; padding: 14px; border-radius: 12px; font-weight: bold; }
    .ok { background: #ecfdf5; border: 1px solid #10b981; color: #065f46; padding: 14px; border-radius: 12px; font-weight: bold; }
    code { background: #e5e7eb; padding: 3px 7px; border-radius: 6px; font-weight: bold; }
    li { margin-bottom: 12px; }
  </style>
</head>
<body>
  <div class="box">
    <h1>01 APRI PRIMA LE ISTRUZIONI</h1>

    <div class="alert">
      Questo pacchetto NON è un APK. Non si installa sul telefono. Serve per importare database e motore Kotlin dentro un progetto Android Studio.
    </div>

    <h2>Modo più semplice</h2>
    <div class="ok">
      Clicca il file numero 2:<br>
      <code>2_IMPORTA.command</code>
    </div>

    <p>Quando si apre il Terminale, trascina dentro la cartella principale del tuo progetto Android Studio e premi INVIO.</p>

    <h2>Cosa fa il file numero 2</h2>
    <ul>
      <li>Copia il database quiz nel tuo progetto Android.</li>
      <li>Copia i file Kotlin del motore quiz nel tuo progetto Android.</li>
      <li>Non crea la grafica dell'app: la grafica va costruita in Android Studio.</li>
    </ul>

    <h2>Dove prende i file</h2>
    <p>I file tecnici stanno nella cartella numero 3:</p>
    <p><code>3_FILE_TECNICI</code></p>

    <p>Quella cartella serve al pulsante numero 2. Non devi aprirla a caso.</p>

    <h2>Metodo manuale</h2>

    <h3>1. Database</h3>
    <p>Prendi:</p>
    <p><code>3_FILE_TECNICI/app/src/main/assets/database_quiz.json</code></p>
    <p>Mettilo nel tuo progetto Android qui:</p>
    <p><code>app/src/main/assets/database_quiz.json</code></p>

    <h3>2. Motore Kotlin</h3>
    <p>Prendi questa cartella:</p>
    <p><code>3_FILE_TECNICI/app/src/main/java/com/alex/quizengine/</code></p>
    <p>Mettila nel tuo progetto Android qui:</p>
    <p><code>app/src/main/java/com/alex/quizengine/</code></p>

    <h2>File Kotlin inclusi</h2>
    <ul>
      <li><code>QuizQuestion.kt</code></li>
      <li><code>QuizRepository.kt</code></li>
      <li><code>QuizEngine.kt</code></li>
      <li><code>QuizQualityValidator.kt</code></li>
      <li><code>ScoreEngine.kt</code></li>
    </ul>
  </div>
</body>
</html>
"""

    comando = """#!/bin/bash
clear
echo "02 - IMPORTA TUTTO NEL TUO PROGETTO ANDROID"
echo ""
echo "Trascina qui la cartella principale del tuo progetto Android Studio e premi INVIO:"
read PROJECT_DIR

PROJECT_DIR="${PROJECT_DIR//\\ / }"
PROJECT_DIR="${PROJECT_DIR%/}"

if [ ! -d "$PROJECT_DIR/app/src/main" ]; then
  echo ""
  echo "ERRORE: questa non sembra una cartella valida di progetto Android."
  echo "La cartella deve contenere: app/src/main"
  echo ""
  read -p "Premi INVIO per chiudere."
  exit 1
fi

DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE="$DIR/3_FILE_TECNICI"

mkdir -p "$PROJECT_DIR/app/src/main/assets"
cp "$SOURCE/app/src/main/assets/database_quiz.json" "$PROJECT_DIR/app/src/main/assets/database_quiz.json"

mkdir -p "$PROJECT_DIR/app/src/main/java/com/alex/quizengine"
cp "$SOURCE/app/src/main/java/com/alex/quizengine/"*.kt "$PROJECT_DIR/app/src/main/java/com/alex/quizengine/"

echo ""
echo "IMPORTAZIONE COMPLETATA."
echo ""
echo "Database copiato in:"
echo "$PROJECT_DIR/app/src/main/assets/database_quiz.json"
echo ""
echo "Motore Kotlin copiato in:"
echo "$PROJECT_DIR/app/src/main/java/com/alex/quizengine/"
echo ""
read -p "Vuoi aprire ora il progetto in Android Studio? scrivi s e premi INVIO: " RISPOSTA

if [ "$RISPOSTA" = "s" ] || [ "$RISPOSTA" = "S" ]; then
  open -a "Android Studio" "$PROJECT_DIR"
fi
"""

    (output_dir / "1_ISTRUZIONI.html").write_text(html, encoding="utf-8")
    (output_dir / "2_IMPORTA.command").write_text(comando, encoding="utf-8")
    os.chmod(output_dir / "2_IMPORTA.command", 0o755)

    for nome in [
        "README.md",
        "APRI LE ISTRUZIONI.html",
        "APRI LE ISTRUZIONI.command",
        "APRI LE ISTRUZIONI.txt",
        "IMPORTA IN ANDROID STUDIO.command",
        "IMPORTA TUTTO IN ANDROID STUDIO.command",
        "README_LEGGIMI_ANDROID.html",
        "00_LEGGIMI_PRIMA.txt",
        "database_quiz.json",
        "app",
        "quiz_engine_android",
        "FILE_DA_IMPORTARE",
    ]:
        elemento = output_dir / nome
        if elemento.is_dir():
            shutil.rmtree(elemento)
        elif elemento.exists():
            elemento.unlink()



def pulisci_android_pubblico(output_dir):
    from pathlib import Path
    import shutil

    output_dir = Path(output_dir)

    vecchia = output_dir / "3_FILE_TECNICI"
    nuova = output_dir / "2_FILE_DA_COPIARE"

    if nuova.exists():
        shutil.rmtree(nuova)

    if vecchia.exists():
        vecchia.rename(nuova)

    for nome in [
        "2_IMPORTA.command",
        "02_CLICCA_PER_IMPORTARE_NEL_TUO_PROGETTO_ANDROID.command",
        "IMPORTA TUTTO IN ANDROID STUDIO.command",
        "IMPORTA IN ANDROID STUDIO.command",
        "README.md",
        "database_quiz.json",
        "app",
        "quiz_engine_android",
    ]:
        elemento = output_dir / nome
        if elemento.is_dir():
            shutil.rmtree(elemento)
        elif elemento.exists():
            elemento.unlink()

    html = """<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <title>1 ISTRUZIONI</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 850px; margin: 40px auto; padding: 24px; line-height: 1.6; background: #f8fafc; color: #111827; }
    .box { background: white; border-radius: 18px; padding: 28px; box-shadow: 0 12px 30px rgba(0,0,0,0.10); }
    .alert { background: #fff7ed; border: 1px solid #fb923c; color: #9a3412; padding: 14px; border-radius: 12px; font-weight: bold; }
    code { background: #e5e7eb; padding: 3px 7px; border-radius: 6px; font-weight: bold; }
  </style>
</head>
<body>
  <div class="box">
    <h1>1 ISTRUZIONI</h1>

    <div class="alert">
      Questo pacchetto NON è un APK. Non si installa sul telefono.
      Serve per copiare database e motore Kotlin dentro un progetto Android Studio.
    </div>

    <h2>Cosa devi aprire</h2>
    <p>Apri solo la cartella:</p>
    <p><code>2_FILE_DA_COPIARE</code></p>

    <h2>1. Copia il database</h2>
    <p>Prendi:</p>
    <p><code>2_FILE_DA_COPIARE/app/src/main/assets/database_quiz.json</code></p>
    <p>Mettilo nel tuo progetto Android qui:</p>
    <p><code>app/src/main/assets/database_quiz.json</code></p>

    <h2>2. Copia il motore Kotlin</h2>
    <p>Prendi questa cartella:</p>
    <p><code>2_FILE_DA_COPIARE/app/src/main/java/com/alex/quizengine/</code></p>
    <p>Mettila nel tuo progetto Android qui:</p>
    <p><code>app/src/main/java/com/alex/quizengine/</code></p>

    <h2>File Kotlin inclusi</h2>
    <p>
      QuizQuestion.kt<br>
      QuizRepository.kt<br>
      QuizEngine.kt<br>
      QuizQualityValidator.kt<br>
      ScoreEngine.kt
    </p>
  </div>
</body>
</html>
"""

    (output_dir / "1_ISTRUZIONI.html").write_text(html, encoding="utf-8")

def copia_motore_android(output_dir):
    if not RUNTIME_ANDROID.exists():
        raise FileNotFoundError("Motore Android non trovato: runtime/android")

    target = output_dir / "quiz_engine_android"

    if target.exists():
        shutil.rmtree(target)

    shutil.copytree(RUNTIME_ANDROID, target)
    crea_istruzioni_android(output_dir)
    pulisci_android_pubblico(output_dir)


def copia_motore_web(output_dir):
    if not RUNTIME_WEB.exists():
        raise FileNotFoundError("Motore Web non trovato: runtime/web")

    shutil.copy2(RUNTIME_WEB / "quiz-engine.js", output_dir / "quiz-engine.js")
    shutil.copy2(RUNTIME_WEB / "README_WEB_ENGINE.md", output_dir / "README_WEB_ENGINE.md")

def crea_demo_web(percorso, domande):
    dati_json = json.dumps(domande, ensure_ascii=False)

    html_inizio = """<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <title>Quiz Web Interattivo</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: radial-gradient(circle at top left, #155e75, #020617 45%, #111827);
      color: #f8fafc;
    }
    .page {
      max-width: 980px;
      margin: 0 auto;
      padding: 28px 18px;
    }
    .card {
      background: rgba(15, 23, 42, 0.94);
      border: 1px solid rgba(148, 163, 184, 0.35);
      border-radius: 26px;
      padding: 26px;
      box-shadow: 0 22px 60px rgba(0, 0, 0, 0.35);
    }
    h1 {
      font-size: clamp(2rem, 5vw, 3.2rem);
      margin: 0 0 10px;
    }
    h2 {
      margin-top: 0;
    }
    p {
      color: #cbd5e1;
      line-height: 1.55;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px;
      margin: 22px 0;
    }
    label {
      display: block;
      font-weight: 900;
      margin-bottom: 8px;
      color: #e2e8f0;
    }
    select {
      width: 100%;
      padding: 14px 12px;
      border-radius: 14px;
      border: 1px solid rgba(148, 163, 184, 0.45);
      background: #020617;
      color: #f8fafc;
      font-weight: 800;
      font-size: 1rem;
    }
    button {
      cursor: pointer;
      border: 0;
      font-weight: 950;
    }
    .start {
      margin-top: 8px;
      padding: 17px 24px;
      border-radius: 18px;
      background: linear-gradient(135deg, #5eead4, #f0f9a8);
      color: #020617;
      font-size: 1.06rem;
    }
    .secondary {
      padding: 13px 18px;
      border-radius: 14px;
      background: rgba(148, 163, 184, 0.18);
      color: #f8fafc;
      border: 1px solid rgba(148, 163, 184, 0.35);
    }
    .quiz {
      display: none;
      margin-top: 20px;
    }
    .top {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      margin-bottom: 18px;
      color: #cbd5e1;
      font-weight: 850;
    }
    .pill {
      padding: 9px 13px;
      border-radius: 999px;
      background: rgba(34, 197, 94, 0.16);
      color: #bbf7d0;
      white-space: nowrap;
    }
    .question {
      font-size: 1.35rem;
      font-weight: 950;
      line-height: 1.45;
      margin: 16px 0 18px;
    }
    .option {
      width: 100%;
      text-align: left;
      margin: 8px 0;
      padding: 15px 17px;
      border-radius: 16px;
      background: #1e293b;
      color: #f8fafc;
      border: 1px solid rgba(148, 163, 184, 0.30);
      font-size: 1rem;
    }
    .option:hover:not(:disabled) {
      background: #334155;
    }
    .option:disabled {
      cursor: default;
      opacity: 0.96;
    }
    .correct {
      background: rgba(34, 197, 94, 0.28) !important;
      border-color: #22c55e !important;
    }
    .wrong {
      background: rgba(239, 68, 68, 0.28) !important;
      border-color: #ef4444 !important;
    }
    .feedback {
      display: none;
      margin-top: 16px;
      padding: 16px;
      border-radius: 18px;
      background: rgba(2, 6, 23, 0.55);
      border: 1px solid rgba(148, 163, 184, 0.28);
    }
    .actions {
      margin-top: 18px;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    .summary {
      display: none;
      margin-top: 18px;
      padding: 20px;
      border-radius: 20px;
      background: rgba(34, 197, 94, 0.13);
      border: 1px solid rgba(74, 222, 128, 0.35);
    }
    .small {
      font-size: 0.95rem;
      color: #94a3b8;
    }
    .warning {
      display: none;
      margin-top: 14px;
      padding: 14px;
      border-radius: 14px;
      background: rgba(239, 68, 68, 0.18);
      color: #fecaca;
      border: 1px solid rgba(239, 68, 68, 0.35);
      font-weight: 800;
    }
    @media (max-width: 760px) {
      .grid { grid-template-columns: 1fr; }
      .top { flex-direction: column; align-items: flex-start; }
    }
  </style>
</head>
<body>
  <main class="page">
    <section class="card" id="setup">
      <h1>Quiz Scienze</h1>
      <p>
        Scegli materia scientifica, numero di domande e difficoltà. Il pacchetto contiene il database completo,
        ma il quiz parte solo con le domande che scegli tu.
      </p>

      <div class="grid">
        <div>
          <label for="materia">Materia</label>
          <select id="materia">
            <option value="materie_scientifiche">Materie scientifiche - tutte</option>
            <option value="scienze_generali">Scienze generali</option>
            <option value="fisica">Fisica</option>
            <option value="chimica">Chimica</option>
            <option value="biologia">Biologia</option>
          </select>
        </div>

        <div>
          <label for="numero">Numero domande</label>
          <select id="numero">
            <option value="10">10 domande</option>
            <option value="20">20 domande</option>
            <option value="all">Tutte le domande</option>
          </select>
        </div>

        <div>
          <label for="livello">Difficoltà</label>
          <select id="livello">
            <option value="tutti">Tutti i livelli</option>
            <option value="facile">Facile</option>
            <option value="intermedio">Intermedio</option>
            <option value="avanzato">Avanzato</option>
          </select>
        </div>
      </div>

      <p class="small" id="anteprima"></p>
      <div class="warning" id="warning"></div>

      <button class="start" onclick="avviaQuiz()">Avvia quiz</button>
    </section>

    <section class="card quiz" id="quiz">
      <div class="top">
        <div id="progress">Domanda 0/0</div>
        <div class="pill" id="score">Punteggio: 0</div>
      </div>

      <div class="small" id="meta"></div>
      <div class="question" id="question"></div>
      <div id="options"></div>

      <div class="feedback" id="feedback"></div>

      <div class="actions">
        <button class="secondary" id="nextButton" onclick="prossimaDomanda()" style="display:none;">Prossima domanda</button>
        <button class="secondary" onclick="tornaAlMenu()">Nuovo quiz</button>
      </div>

      <div class="summary" id="summary"></div>
    </section>
  </main>

  <script>
const DATABASE_QUIZ = """

    html_fine = """;

    let domandeQuiz = [];
    let indiceDomanda = 0;
    let punteggio = 0;
    let rispostaData = false;
    let offsetRisposte = 0;

    const materiaEl = document.getElementById("materia");
    const numeroEl = document.getElementById("numero");
    const livelloEl = document.getElementById("livello");

    materiaEl.addEventListener("change", aggiornaAnteprima);
    numeroEl.addEventListener("change", aggiornaAnteprima);
    livelloEl.addEventListener("change", aggiornaAnteprima);

    aggiornaAnteprima();

    function slug(text) {
      return String(text || "")
        .trim()
        .toLowerCase()
        .replace(/[àá]/g, "a")
        .replace(/[èé]/g, "e")
        .replace(/[ìí]/g, "i")
        .replace(/[òó]/g, "o")
        .replace(/[ùú]/g, "u")
        .replace(/\\s+/g, "_")
        .replace(/-/g, "_");
    }

    function materiaOk(domanda, materia) {
      const scelta = slug(materia);
      const id = String(domanda.id || "").toUpperCase();

      // Nel pacchetto web Scienze, questa voce deve prendere tutto:
      // SCI_ + FIS_ + CHE_ + BIO_ = 160 domande.
      if (scelta === "materie_scientifiche" || scelta === "tutte") {
        return true;
      }

      // Scienze generali: solo le domande base del file scienze.json.
      if (scelta === "scienze_generali" || scelta === "scienze") {
        return id.startsWith("SCI_");
      }

      // Materie specifiche: solo i file dedicati.
      if (scelta === "fisica") {
        return id.startsWith("FIS_");
      }

      if (scelta === "chimica") {
        return id.startsWith("CHE_");
      }

      if (scelta === "biologia") {
        return id.startsWith("BIO_");
      }

      return false;
    }

    function livelloOk(domanda, livello) {
      const scelta = slug(livello);

      if (scelta === "tutti") {
        return true;
      }

      return slug(domanda.livello || domanda.difficulty) === scelta;
    }

    function opzioniDomanda(domanda) {
      if (Array.isArray(domanda.opzioni)) {
        return domanda.opzioni;
      }

      if (Array.isArray(domanda.options)) {
        return domanda.options;
      }

      return [];
    }

    function rispostaCorretta(domanda) {
      return domanda.risposta_corretta || domanda.correct_answer || domanda.answer || "";
    }

    function testoDomanda(domanda) {
      return domanda.domanda || domanda.question || "Domanda senza testo";
    }

    function filtraDomande() {
      const materia = materiaEl.value;
      const livello = livelloEl.value;

      return DATABASE_QUIZ.filter(domanda =>
        materiaOk(domanda, materia) &&
        livelloOk(domanda, livello)
      );
    }

    function aggiornaAnteprima() {
      const filtrate = filtraDomande();
      const numero = numeroEl.value;
      const quante = numero === "all"
        ? filtrate.length
        : Math.min(Number(numero), filtrate.length);

      document.getElementById("anteprima").textContent =
        "Domande disponibili con questi filtri: " + filtrate.length +
        " — Il quiz partirà con: " + quante + " domande.";

      document.getElementById("warning").style.display = filtrate.length ? "none" : "block";
      document.getElementById("warning").textContent = filtrate.length ? "" : "Nessuna domanda trovata con questi filtri.";
    }

    function mescola(array) {
      const copia = [...array];

      for (let i = copia.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [copia[i], copia[j]] = [copia[j], copia[i]];
      }

      return copia;
    }

    function avviaQuiz() {
      const filtrate = filtraDomande();

      if (!filtrate.length) {
        aggiornaAnteprima();
        return;
      }

      const numero = numeroEl.value;
      domandeQuiz = mescola(filtrate);

      if (numero !== "all") {
        domandeQuiz = domandeQuiz.slice(0, Number(numero));
      }

      indiceDomanda = 0;
      punteggio = 0;
      rispostaData = false;
      offsetRisposte = Math.floor(Math.random() * 4);

      document.getElementById("setup").style.display = "none";
      document.getElementById("quiz").style.display = "block";
      document.getElementById("summary").style.display = "none";

      mostraDomanda();
    }

    function opzioniBilanciate(domanda, indice) {
      const opzioniOriginali = opzioniDomanda(domanda);
      const corretta = rispostaCorretta(domanda);

      if (!Array.isArray(opzioniOriginali) || opzioniOriginali.length !== 4) {
        return opzioniOriginali;
      }

      const sbagliate = opzioniOriginali.filter(opzione => opzione !== corretta);

      if (sbagliate.length !== 3) {
        return mescola(opzioniOriginali);
      }

      const sbagliateMescolate = mescola(sbagliate);

      // Distribuisce la risposta corretta nelle 4 posizioni.
      // In questo modo non può finire quasi sempre al primo posto.
      const posizioneCorretta = (indice + offsetRisposte) % 4;

      const risultato = [];
      let indiceSbagliata = 0;

      for (let posizione = 0; posizione < 4; posizione++) {
        if (posizione === posizioneCorretta) {
          risultato.push(corretta);
        } else {
          risultato.push(sbagliateMescolate[indiceSbagliata]);
          indiceSbagliata += 1;
        }
      }

      return risultato;
    }

    function mostraDomanda() {
      rispostaData = false;

      const domanda = domandeQuiz[indiceDomanda];
      const opzioni = opzioniBilanciate(domanda, indiceDomanda);

      document.getElementById("progress").textContent =
        "Domanda " + (indiceDomanda + 1) + "/" + domandeQuiz.length;

      document.getElementById("score").textContent =
        "Punteggio: " + punteggio;

      document.getElementById("meta").textContent =
        "Materia: " + (domanda.sottocategoria || domanda.categoria || "non indicata") +
        " — Difficoltà: " + (domanda.livello || "non indicata");

      document.getElementById("question").textContent = testoDomanda(domanda);
      document.getElementById("feedback").style.display = "none";
      document.getElementById("feedback").innerHTML = "";
      document.getElementById("nextButton").style.display = "none";

      const optionsBox = document.getElementById("options");
      optionsBox.innerHTML = "";

      if (opzioni.length !== 4) {
        optionsBox.innerHTML =
          '<div class="warning" style="display:block;">Questa domanda non ha 4 opzioni valide.</div>';
        return;
      }

      opzioni.forEach(opzione => {
        const button = document.createElement("button");
        button.className = "option";
        button.textContent = opzione;
        button.onclick = () => rispondi(button, opzione);
        optionsBox.appendChild(button);
      });
    }

    function rispondi(buttonScelto, rispostaScelta) {
      if (rispostaData) {
        return;
      }

      rispostaData = true;

      const domanda = domandeQuiz[indiceDomanda];
      const corretta = rispostaCorretta(domanda);
      const buttons = document.querySelectorAll(".option");

      buttons.forEach(button => {
        button.disabled = true;

        if (button.textContent === corretta) {
          button.classList.add("correct");
        }

        if (button === buttonScelto && rispostaScelta !== corretta) {
          button.classList.add("wrong");
        }
      });

      const giusta = rispostaScelta === corretta;

      if (giusta) {
        punteggio += 1;
      }

      document.getElementById("score").textContent =
        "Punteggio: " + punteggio;

      const feedback = document.getElementById("feedback");
      feedback.style.display = "block";
      feedback.innerHTML =
        "<strong>" + (giusta ? "Risposta corretta." : "Risposta sbagliata.") + "</strong><br>" +
        "Risposta corretta: <strong>" + escapeHtml(corretta) + "</strong><br><br>" +
        escapeHtml(domanda.spiegazione || domanda.explanation || "Spiegazione non disponibile.");

      document.getElementById("nextButton").style.display = "inline-block";
      document.getElementById("nextButton").textContent =
        indiceDomanda >= domandeQuiz.length - 1 ? "Vedi risultato finale" : "Prossima domanda";
    }

    function prossimaDomanda() {
      if (indiceDomanda >= domandeQuiz.length - 1) {
        mostraRisultatoFinale();
        return;
      }

      indiceDomanda += 1;
      mostraDomanda();
    }

    function mostraRisultatoFinale() {
      document.getElementById("question").style.display = "none";
      document.getElementById("options").style.display = "none";
      document.getElementById("feedback").style.display = "none";
      document.getElementById("nextButton").style.display = "none";

      const percentuale = Math.round((punteggio / domandeQuiz.length) * 100);
      let giudizio = "Da ripassare";

      if (percentuale >= 95) giudizio = "Eccellente";
      else if (percentuale >= 90) giudizio = "Ottimo";
      else if (percentuale >= 80) giudizio = "Buono";
      else if (percentuale >= 70) giudizio = "Discreto";
      else if (percentuale >= 60) giudizio = "Sufficiente";

      const summary = document.getElementById("summary");
      summary.style.display = "block";
      summary.innerHTML =
        "<h2>Risultato finale</h2>" +
        "<p><strong>" + punteggio + "/" + domandeQuiz.length + "</strong> — " + percentuale + "%</p>" +
        "<p><strong>Giudizio:</strong> " + giudizio + "</p>";
    }

    function tornaAlMenu() {
      document.getElementById("setup").style.display = "block";
      document.getElementById("quiz").style.display = "none";
      document.getElementById("question").style.display = "block";
      document.getElementById("options").style.display = "block";
      aggiornaAnteprima();
    }

    function escapeHtml(text) {
      return String(text || "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }
  </script>
</body>
</html>
"""

    html = html_inizio + dati_json + html_fine

    readme_html = """<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <title>Leggimi pacchetto quiz web</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 850px; margin: 40px auto; padding: 24px; line-height: 1.6; }
    a { display: inline-block; margin-top: 18px; padding: 16px 22px; border-radius: 14px; background: #16a34a; color: white; font-weight: 900; text-decoration: none; }
    code { background: #e5e7eb; padding: 3px 6px; border-radius: 6px; }
  </style>
</head>
<body>
  <h1>Pacchetto quiz web interattivo</h1>
  <p>Apri il file:</p>
  <p><strong>1_APRI_QUIZ.html</strong></p>
  <p>Dentro il quiz puoi scegliere materia, numero di domande e difficoltà.</p>
  <a href="./1_APRI_QUIZ.html">▶️ APRI IL QUIZ</a>
  <h2>File inclusi</h2>
  <ul>
    <li><code>1_APRI_QUIZ.html</code> — quiz web con filtri interattivi</li>
    <li><code>database_quiz.json</code> — database riutilizzabile</li>
    <li><code>quiz-engine.js</code> — motore web riutilizzabile</li>
  </ul>
</body>
</html>
"""

    (percorso / "1_APRI_QUIZ.html").write_text(html, encoding="utf-8")
    (percorso / "index.html").write_text(html, encoding="utf-8")
    (percorso / "README_LEGGIMI.html").write_text(readme_html, encoding="utf-8")

def crea_readme_pacchetto(percorso, piattaforma, materia, livello, numero):
    testo = f"""# Pacchetto quiz generato

Piattaforma: {piattaforma}
Materia: {materia}
Livello: {livello}
Domande: {numero}

## Web

Apri:

1_APRI_QUIZ.html

## Android

Copia:

app/src/main/assets/database_quiz.json
"""
    (percorso / "README.md").write_text(testo, encoding="utf-8")

def crea_pacchetto(piattaforma, materia, livello, numero):
    domande = prepara_domande(materia, livello, numero)

    nome = f"{piattaforma}_{slug(materia)}_{slug(livello)}_{len(domande)}_domande"
    output_dir = OUTPUT_ROOT / nome

    if output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    if piattaforma == "android":
        assets = output_dir / "app" / "src" / "main" / "assets"
        assets.mkdir(parents=True, exist_ok=True)

        (assets / "database_quiz.json").write_text(
            json.dumps(domande, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        (output_dir / "database_quiz.json").write_text(
            json.dumps(domande, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        copia_motore_android(output_dir)

    else:
        (output_dir / "database_quiz.json").write_text(
            json.dumps(domande, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        crea_demo_web(output_dir, domande)
        copia_motore_web(output_dir)

    crea_readme_pacchetto(output_dir, piattaforma, materia, livello, len(domande))

    zip_path = output_dir.with_suffix(".zip")

    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archivio:
        for file_path in output_dir.rglob("*"):
            archivio.write(file_path, file_path.relative_to(output_dir.parent))

    print(f"Pacchetto creato: {zip_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", choices=["android", "web", "demo"], required=True)
    parser.add_argument("--subject", default="scienze")
    parser.add_argument("--level", default="tutti")
    parser.add_argument("--number", default="10")
    args = parser.parse_args()

    crea_pacchetto(args.platform, args.subject, args.level, args.number)

if __name__ == "__main__":
    main()
