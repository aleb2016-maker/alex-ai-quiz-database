from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


SOSTITUZIONI = {
    "perche'": "perché",
    "perchè": "perché",
    "poiche'": "poiché",
    "finche'": "finché",
    "affinche'": "affinché",
    "qualita'": "qualità",
    "attivita'": "attività",
    "possibilita'": "possibilità",
    "velocita'": "velocità",
    "puntegiatura": "punteggiatura",
    "puntegiatutìra": "punteggiatura",
    "distrattori fori": "distrattori forti",
    "ho il test": "o il test",
}


def leggi_pdf(percorso: Path) -> str:
    errori = []

    try:
        from pypdf import PdfReader
        reader = PdfReader(str(percorso))
        return "\n\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as errore:
        errori.append(f"pypdf: {errore}")

    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(str(percorso))
        return "\n\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as errore:
        errori.append(f"PyPDF2: {errore}")

    raise SystemExit("PDF non leggibile. Installa pypdf oppure usa TXT/MD.\n" + "\n".join(errori))


def leggi_json(percorso: Path) -> str:
    dati = json.loads(percorso.read_text(encoding="utf-8"))
    righe = []

    def visita(valore):
        if isinstance(valore, dict):
            for chiave, contenuto in valore.items():
                if isinstance(contenuto, (dict, list)):
                    visita(contenuto)
                else:
                    righe.append(f"{chiave}: {contenuto}")
        elif isinstance(valore, list):
            for elemento in valore:
                visita(elemento)
        else:
            righe.append(str(valore))

    visita(dati)
    return "\n".join(righe)


def leggi_file(percorso: Path) -> str:
    estensione = percorso.suffix.lower()

    if estensione in {".txt", ".md", ".csv"}:
        return percorso.read_text(encoding="utf-8", errors="ignore")

    if estensione == ".json":
        return leggi_json(percorso)

    if estensione == ".pdf":
        return leggi_pdf(percorso)

    raise SystemExit(f"Formato non supportato: {estensione}")


def normalizza_testo(testo: str) -> str:
    testo = testo.replace("\r\n", "\n").replace("\r", "\n")
    testo = testo.replace("’", "'")

    for errato, corretto in SOSTITUZIONI.items():
        testo = re.sub(re.escape(errato), corretto, testo, flags=re.IGNORECASE)

    testo = re.sub(r"[ \t]+", " ", testo)
    testo = re.sub(r" +([,.;:!?])", r"\1", testo)
    testo = re.sub(r"([,.;:!?])([^\s\n])", r"\1 \2", testo)
    testo = re.sub(r"\.{2,}", ".", testo)
    testo = re.sub(r"!{2,}", "!", testo)
    testo = re.sub(r"\?{2,}", "?", testo)

    righe = [riga.strip() for riga in testo.splitlines()]
    testo = "\n".join(righe)
    testo = re.sub(r"\n{3,}", "\n\n", testo)

    return testo.strip() + "\n"


def valida_documento(testo: str) -> list[str]:
    avvisi = []

    if len(testo.strip()) < 300:
        avvisi.append("Documento corto: potrebbe non bastare per un corso o quiz ricco.")

    if re.search(r" +[,.;:!?]", testo):
        avvisi.append("Trovati spazi prima della punteggiatura.")

    if re.search(r"[A-Za-zÀ-ÿ],[A-Za-zÀ-ÿ]", testo):
        avvisi.append("Possibile virgola senza spazio.")

    for parola in ["perche'", "qualita'", "attivita'", "puntegiatura", "distrattori fori"]:
        if parola in testo.lower():
            avvisi.append(f"Possibile errore ancora presente: {parola}")

    righe_lunghe = [riga for riga in testo.splitlines() if len(riga) > 280]

    if righe_lunghe:
        avvisi.append(f"Trovate {len(righe_lunghe)} righe molto lunghe.")

    return avvisi


def crea_blocchi_minicorso(testo: str, massimo: int = 8) -> list[str]:
    paragrafi = [p.strip() for p in re.split(r"\n\s*\n", testo) if len(p.strip()) > 70]

    if not paragrafi:
        paragrafi = [testo.strip()]

    return [paragrafo[:900].strip() for paragrafo in paragrafi[:massimo]]


def crea_html_minicorso(titolo: str, cards: list[dict]) -> str:
    titolo_html = html.escape(titolo)
    cards_json = json.dumps(cards, ensure_ascii=False)

    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<title>{titolo_html}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {{
  margin: 0;
  font-family: Arial, sans-serif;
  background: #101522;
  color: #f5f7fb;
}}
.app {{
  max-width: 900px;
  margin: 0 auto;
  padding: 28px;
}}
.card {{
  background: #182033;
  border: 1px solid #2d3a5c;
  border-radius: 22px;
  padding: 28px;
  box-shadow: 0 18px 45px rgba(0,0,0,.28);
}}
.badge {{
  display: inline-block;
  padding: 7px 12px;
  border-radius: 999px;
  background: #26375f;
  margin-bottom: 16px;
}}
p {{
  line-height: 1.65;
  font-size: 18px;
}}
button {{
  border: 0;
  border-radius: 14px;
  padding: 13px 18px;
  font-weight: 700;
  cursor: pointer;
  margin-right: 10px;
}}
.primary {{
  background: #7c9cff;
  color: #091020;
}}
.secondary {{
  background: #2b3654;
  color: #f5f7fb;
}}
.progress {{
  margin: 18px 0;
  height: 10px;
  background: #26314d;
  border-radius: 999px;
  overflow: hidden;
}}
.bar {{
  height: 100%;
  width: 0%;
  background: #7c9cff;
}}
</style>
</head>
<body>
<div class="app">
  <h1>{titolo_html}</h1>
  <div class="progress"><div id="bar" class="bar"></div></div>
  <div class="card">
    <div id="badge" class="badge"></div>
    <h2 id="cardTitle"></h2>
    <p id="cardText"></p>
    <button class="secondary" onclick="prevCard()">Indietro</button>
    <button class="primary" onclick="nextCard()">Avanti</button>
  </div>
</div>
<script>
const cards = {cards_json};
let index = 0;

function render() {{
  const card = cards[index];
  document.getElementById("badge").textContent = `Card ${{index + 1}} / ${{cards.length}}`;
  document.getElementById("cardTitle").textContent = card.titolo;
  document.getElementById("cardText").textContent = card.testo;
  document.getElementById("bar").style.width = `${{((index + 1) / cards.length) * 100}}%`;
}}

function nextCard() {{
  if (index < cards.length - 1) {{
    index++;
    render();
  }}
}}

function prevCard() {{
  if (index > 0) {{
    index--;
    render();
  }}
}}

render();
</script>
</body>
</html>
"""


def slugify(testo: str) -> str:
    testo = testo.lower()
    testo = re.sub(r"[^a-z0-9àèéìòù]+", "-", testo)
    return testo.strip("-") or "materiale-formativo"


def scrivi_report(percorso: Path, contenuto: str) -> None:
    percorso.parent.mkdir(parents=True, exist_ok=True)
    percorso.write_text(contenuto, encoding="utf-8")


def aggiungi_zip(zip_file: zipfile.ZipFile, percorso: Path, nome: str) -> None:
    if percorso.exists():
        zip_file.write(percorso, nome)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pipeline finale: file -> documento corretto -> mini-corso -> pacchetto ZIP."
    )
    parser.add_argument("file")
    parser.add_argument("--titolo", default="Materiale formativo")
    parser.add_argument("--salta-qualita-progetto", action="store_true")

    args = parser.parse_args()

    file_sorgente = Path(args.file)

    if not file_sorgente.exists():
        raise SystemExit(f"File non trovato: {file_sorgente}")

    out_dir = Path("dist/formazione")
    out_dir.mkdir(parents=True, exist_ok=True)

    testo_estratto_path = out_dir / "testo_estratto.md"
    documento_corretto_path = out_dir / "documento_corretto.md"
    minicorso_json_path = out_dir / "minicorso_interattivo.json"
    minicorso_html_path = out_dir / "minicorso_interattivo.html"

    testo = leggi_file(file_sorgente)
    testo_corretto = normalizza_testo(testo)
    avvisi = valida_documento(testo_corretto)

    testo_estratto_path.write_text(testo, encoding="utf-8")
    documento_corretto_path.write_text(testo_corretto, encoding="utf-8")

    blocchi = crea_blocchi_minicorso(testo_corretto)

    cards = [
        {
            "id": f"CARD-{indice:03d}",
            "titolo": f"Passaggio {indice}",
            "testo": blocco,
            "tipo": "lezione",
        }
        for indice, blocco in enumerate(blocchi, start=1)
    ]

    minicorso_json_path.write_text(
        json.dumps(
            {
                "titolo": args.titolo,
                "numero_card": len(cards),
                "cards": cards,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    minicorso_html_path.write_text(
        crea_html_minicorso(args.titolo, cards),
        encoding="utf-8",
    )

    zip_path = Path("downloads") / f"pacchetto-formazione-{slugify(args.titolo)}.zip"
    zip_path.parent.mkdir(parents=True, exist_ok=True)

    readme_pacchetto = out_dir / "README_PACCHETTO.json"
    readme_pacchetto.write_text(
        json.dumps(
            {
                "titolo": args.titolo,
                "uso": "Pacchetto riutilizzabile in demo web, app Android o altri progetti.",
                "contenuto": [
                    "documento_corretto.md",
                    "minicorso_interattivo.html",
                    "minicorso_interattivo.json",
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        aggiungi_zip(zip_file, documento_corretto_path, "documento_corretto.md")
        aggiungi_zip(zip_file, minicorso_json_path, "minicorso_interattivo.json")
        aggiungi_zip(zip_file, minicorso_html_path, "minicorso_interattivo.html")
        aggiungi_zip(zip_file, readme_pacchetto, "README_PACCHETTO.json")

    stato_documento = "OK" if not avvisi else "DA RIVEDERE"

    scrivi_report(
        Path("reports/pipeline_formazione_completa.md"),
        f"""# Pipeline formazione completa

- File sorgente: `{file_sorgente}`
- Titolo: {args.titolo}
- Testo estratto: `{testo_estratto_path}`
- Documento corretto: `{documento_corretto_path}`
- Mini-corso JSON: `{minicorso_json_path}`
- Mini-corso HTML: `{minicorso_html_path}`
- Pacchetto ZIP: `{zip_path}`
- Card create: {len(cards)}
- Stato documento: {stato_documento}
- Avvisi documento: {len(avvisi)}

## Avvisi

{chr(10).join("- " + avviso for avviso in avvisi) if avvisi else "Nessun avviso automatico rilevato."}

## Stato

OK: pipeline file -> documento corretto -> mini-corso -> export completata.
""",
    )

    if not args.salta_qualita_progetto and Path("scripts/controllo_qualita_completo.py").exists():
        subprocess.run(
            [sys.executable, "scripts/controllo_qualita_completo.py"],
            cwd=PROJECT_ROOT,
            check=True,
        )

    print("✅ Pipeline formazione completa terminata")
    print(f"📌 Documento corretto: {documento_corretto_path}")
    print(f"📌 Mini-corso HTML: {minicorso_html_path}")
    print(f"📌 Pacchetto ZIP: {zip_path}")
    print("📌 Report: reports/pipeline_formazione_completa.md")


if __name__ == "__main__":
    main()
