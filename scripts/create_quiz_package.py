import argparse
import json
import random
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "dist" / "database_quiz_finale.json"
OUTPUT_ROOT = ROOT / "dist" / "generated"

def slug(testo):
    return (
        str(testo or "")
        .strip()
        .lower()
        .replace("à", "a")
        .replace("á", "a")
        .replace("è", "e")
        .replace("é", "e")
        .replace("ì", "i")
        .replace("í", "i")
        .replace("ò", "o")
        .replace("ó", "o")
        .replace("ù", "u")
        .replace("ú", "u")
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

def filtra_domande(database, materia, livello):
    risultato = []

    for domanda in database:
        if not materia_ok(domanda, materia):
            continue

        if livello != "tutti" and domanda.get("livello") != livello:
            continue

        risultato.append(domanda)

    return risultato

def normalizza_domanda(domanda):
    return {
        "id": domanda.get("id", ""),
        "categoria": domanda.get("categoria", ""),
        "sottocategoria": domanda.get("sottocategoria", ""),
        "livello": domanda.get("livello", ""),
        "domanda": domanda.get("domanda", ""),
        "opzioni": domanda.get("opzioni", []),
        "risposta_corretta": domanda.get("risposta_corretta", ""),
        "spiegazione": domanda.get("spiegazione", ""),
        "distrattore_forte": domanda.get("distrattore_forte", ""),
        "tags": domanda.get("tags", []),
    }

def crea_index_web(percorso):
    html = """<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <title>Quiz generato</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: system-ui, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; background: #0f172a; color: #f8fafc; }
    button { display: block; width: 100%; margin: 10px 0; padding: 14px; border-radius: 14px; border: 1px solid #334155; background: #1e293b; color: #f8fafc; cursor: pointer; text-align: left; }
    .card { background: #111827; padding: 24px; border-radius: 22px; }
    .ok { background: #14532d; padding: 14px; border-radius: 14px; }
    .ko { background: #7f1d1d; padding: 14px; border-radius: 14px; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Quiz generato</h1>
    <div id="app">Caricamento...</div>
  </div>

  <script>
    let quiz = [];
    let indice = 0;
    let punteggio = 0;
    let bloccato = false;

    async function start() {
      const response = await fetch("./database_quiz.json");
      quiz = await response.json();
      quiz = Array.isArray(quiz) ? quiz : (quiz.quiz || quiz.domande || []);
      mostra();
    }

    function mostra() {
      bloccato = false;
      const app = document.getElementById("app");
      const d = quiz[indice];

      if (!d) {
        app.innerHTML = `<h2>Risultato finale</h2><p>${punteggio}/${quiz.length}</p>`;
        return;
      }

      app.innerHTML = `
        <p>Domanda ${indice + 1}/${quiz.length} · ${d.categoria} · ${d.livello}</p>
        <h2>${d.domanda}</h2>
        ${d.opzioni.map((o, i) => `<button onclick="rispondi('${String(o).replaceAll("'", "\\'")}')">${String.fromCharCode(65 + i)}) ${o}</button>`).join("")}
        <div id="feedback"></div>
      `;
    }

    function rispondi(risposta) {
      if (bloccato) return;
      bloccato = true;

      const d = quiz[indice];
      const ok = risposta === d.risposta_corretta;

      if (ok) punteggio++;

      document.getElementById("feedback").innerHTML = `
        <p class="${ok ? "ok" : "ko"}">
          <strong>${ok ? "Corretto" : "Sbagliato"}</strong><br>
          Risposta corretta: ${d.risposta_corretta}<br>
          ${d.spiegazione || ""}
        </p>
        <button onclick="indice++; mostra()">Domanda successiva</button>
      `;
    }

    start();
  </script>
</body>
</html>
"""
    (percorso / "index.html").write_text(html, encoding="utf-8")

def crea_readme_pacchetto(percorso, piattaforma, materia, livello, numero):
    testo = f"""# Pacchetto quiz generato

Piattaforma: {piattaforma}
Materia: {materia}
Livello: {livello}
Domande: {numero}

File principale:
database_quiz.json

Android:
copia database_quiz.json dentro app/src/main/assets/

Web:
apri index.html oppure usa database_quiz.json nella tua app.
"""
    (percorso / "README.md").write_text(testo, encoding="utf-8")

def crea_pacchetto(piattaforma, materia, livello, numero):
    database = carica_database()
    domande = filtra_domande(database, materia, livello)

    if not domande:
        raise ValueError("Nessuna domanda trovata con questi filtri.")

    random.shuffle(domande)

    if numero != "all":
        domande = domande[:int(numero)]

    domande = [normalizza_domanda(domanda) for domanda in domande]

    nome = f"{piattaforma}_{slug(materia)}_{slug(livello)}_{len(domande)}_domande"
    output_dir = OUTPUT_ROOT / nome

    if output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    if piattaforma == "android":
        assets = output_dir / "app" / "src" / "main" / "assets"
        assets.mkdir(parents=True, exist_ok=True)
        destinazione_json = assets / "database_quiz.json"
    else:
        crea_index_web(output_dir)
        destinazione_json = output_dir / "database_quiz.json"

    destinazione_json.write_text(
        json.dumps(domande, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

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
