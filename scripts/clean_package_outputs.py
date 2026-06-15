import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path


def nome_area_da_zip(nome_zip):
    nome = nome_zip.lower()

    if "ai-its" in nome or "ai_its" in nome or "ai-its" in nome:
        return "AI_ITS"

    if "scienze" in nome:
        return "SCIENZE"

    if "fisica_quantistica" in nome:
        return "FISICA_QUANTISTICA"

    if "fisica" in nome:
        return "FISICA"

    if "chimica" in nome:
        return "CHIMICA"

    if "biologia" in nome:
        return "BIOLOGIA"

    return "QUIZ"


def conta_domande(database_path):
    try:
        dati = json.loads(database_path.read_text(encoding="utf-8"))

        if isinstance(dati, list):
            return len(dati)

        if isinstance(dati, dict):
            for chiave in ["questions", "domande", "quiz"]:
                if isinstance(dati.get(chiave), list):
                    return len(dati[chiave])

    except Exception:
        pass

    return 0


def scrivi_leggimi_web(percorso, area, totale):
    html = f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <title>LEGGIMI - Pacchetto Web {area}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 40px auto;">
  <h1>Pacchetto Web {area}</h1>

  <p>Questo pacchetto contiene un quiz Web già pronto con <strong>{totale} domande</strong>.</p>

  <h2>Per provarlo subito</h2>
  <ol>
    <li>Apri il file <strong>APRI_QUIZ.html</strong>.</li>
    <li>Il quiz parte nel browser.</li>
  </ol>

  <h2>File da copiare per creare un nuovo progetto Web</h2>
  <p>Non copiare la cartella principale del pacchetto. Aprila e poi entra nella cartella:</p>

  <pre>SOLO_FILE_DA_COPIARE_WEB/</pre>

  <p>Dentro trovi i file principali:</p>

  <ul>
    <li><strong>index.html</strong> = pagina grafica del quiz</li>
    <li><strong>quiz-engine.js</strong> = motore JavaScript del quiz</li>
    <li><strong>database_quiz.json</strong> = database delle domande</li>
  </ul>

  <p>Per creare un nuovo quiz Web puoi copiare questa cartella nel tuo progetto e modificare grafica, domande o categorie.</p>
</body>
</html>
"""
    percorso.write_text(html, encoding="utf-8")


def scrivi_leggimi_android(percorso, area, totale):
    html = f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <title>LEGGIMI - Pacchetto Android {area}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 40px auto;">
  <h1>Pacchetto Android {area}</h1>

  <p>Questo pacchetto contiene il database e il motore Kotlin per un quiz Android con <strong>{totale} domande</strong>.</p>

  <h2>File da copiare in Android Studio</h2>

  <p>Non copiare la cartella principale del pacchetto. Aprila e poi entra nella cartella:</p>

  <pre>SOLO_FILE_DA_COPIARE_ANDROID/</pre>

  <h3>1. Database domande</h3>

  <p>Copia questo file:</p>

  <pre>database_quiz.json</pre>

  <p>Dentro questa cartella del tuo progetto Android:</p>

  <pre>app/src/main/assets/database_quiz.json</pre>

  <h3>2. Motore Kotlin</h3>

  <p>Copia tutta questa cartella:</p>

  <pre>quizengine/</pre>

  <p>Dentro questa cartella del tuo progetto Android:</p>

  <pre>app/src/main/java/com/alex/quizengine/</pre>

  <p>In questo modo puoi riutilizzare il motore quiz dentro una nuova app Android.</p>
</body>
</html>
"""
    percorso.write_text(html, encoding="utf-8")


def crea_apri_quiz(percorso):
    html = """<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url=SOLO_FILE_DA_COPIARE_WEB/index.html">
  <title>Apri Quiz</title>
</head>
<body style="font-family: Arial, sans-serif; text-align: center; margin-top: 80px;">
  <h1>Avvio del quiz...</h1>
  <p>
    Se il quiz non parte automaticamente,
    <a href="SOLO_FILE_DA_COPIARE_WEB/index.html">clicca qui</a>.
  </p>
</body>
</html>
"""
    percorso.write_text(html, encoding="utf-8")


def copia_file_web(cartella_sorgente, cartella_destinazione):
    cartella_destinazione.mkdir(parents=True, exist_ok=True)

    nomi_da_escludere = {
        "README.md",
        "README_LEGGIMI.html",
        "README_WEB_ENGINE.md",
        "1_APRI_QUIZ.html",
        "APRI_QUIZ.html",
        "LEGGIMI.html",
        ".DS_Store",
    }

    for elemento in cartella_sorgente.iterdir():
        if elemento.name in nomi_da_escludere:
            continue

        destinazione = cartella_destinazione / elemento.name

        if elemento.is_dir():
            shutil.copytree(elemento, destinazione, dirs_exist_ok=True)
        else:
            shutil.copy2(elemento, destinazione)


def pulisci_zip(zip_path):
    area = nome_area_da_zip(zip_path.name)

    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        estratta = tmp / "estratta"
        pulita = tmp / "pulita"

        estratta.mkdir()
        pulita.mkdir()

        with zipfile.ZipFile(zip_path, "r") as archivio:
            archivio.extractall(estratta)

        database_trovati = list(estratta.rglob("database_quiz.json"))
        kotlin_trovati = list(estratta.rglob("*.kt"))
        motori_web = list(estratta.rglob("quiz-engine.js"))
        pagine_index = [
            p for p in estratta.rglob("index.html")
            if not p.name.startswith("1_")
        ]

        if not database_trovati:
            print("Saltato, database non trovato:", zip_path)
            return

        database = database_trovati[0]
        totale = conta_domande(database)

        is_android = len(kotlin_trovati) > 0
        is_web = len(motori_web) > 0 and len(pagine_index) > 0

        if is_android:
            root = pulita / f"PACCHETTO_ANDROID_{area}_{totale}"
            file_da_copiare = root / "SOLO_FILE_DA_COPIARE_ANDROID"
            quizengine_dest = file_da_copiare / "quizengine"

            file_da_copiare.mkdir(parents=True)
            quizengine_dest.mkdir(parents=True)

            shutil.copy2(database, file_da_copiare / "database_quiz.json")

            for kt in kotlin_trovati:
                shutil.copy2(kt, quizengine_dest / kt.name)

            scrivi_leggimi_android(root / "LEGGIMI.html", area, totale)

        elif is_web:
            index = pagine_index[0]
            cartella_web = index.parent

            root = pulita / f"PACCHETTO_WEB_{area}_{totale}"
            file_da_copiare = root / "SOLO_FILE_DA_COPIARE_WEB"

            root.mkdir(parents=True)
            copia_file_web(cartella_web, file_da_copiare)

            crea_apri_quiz(root / "APRI_QUIZ.html")
            scrivi_leggimi_web(root / "LEGGIMI.html", area, totale)

        else:
            print("Saltato, tipo pacchetto non riconosciuto:", zip_path)
            return

        nuovo_zip = zip_path.with_suffix(".zip.tmp")

        with zipfile.ZipFile(nuovo_zip, "w", zipfile.ZIP_DEFLATED) as archivio:
            for file in pulita.rglob("*"):
                if file.is_file():
                    archivio.write(file, file.relative_to(pulita))

        nuovo_zip.replace(zip_path)
        print("Pulito:", zip_path)


def main():
    percorsi = [Path(arg) for arg in sys.argv[1:]]

    if not percorsi:
        percorsi = [Path("downloads"), Path("dist/generated")]

    zip_da_pulire = []

    for percorso in percorsi:
        if percorso.is_file() and percorso.suffix == ".zip":
            zip_da_pulire.append(percorso)
        elif percorso.is_dir():
            zip_da_pulire.extend(percorso.rglob("*.zip"))

    for zip_path in sorted(set(zip_da_pulire)):
        pulisci_zip(zip_path)


if __name__ == "__main__":
    main()
