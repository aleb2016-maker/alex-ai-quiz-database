from __future__ import annotations

import argparse
import csv
import html
import json
import math
import re
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown", ".pdf"}

STOPWORDS = {
    "a", "ad", "al", "alla", "allo", "ai", "agli", "alle", "anche", "avere",
    "che", "chi", "ci", "con", "come", "da", "dal", "dalla", "dallo", "dei",
    "degli", "delle", "del", "dell", "di", "e", "ed", "è", "essere", "fa",
    "fra", "gli", "ha", "hai", "hanno", "ho", "i", "il", "in", "io", "la",
    "le", "li", "lo", "ma", "mi", "nel", "nella", "nelle", "negli", "non",
    "o", "per", "più", "può", "puo", "quale", "quando", "quella", "quelli",
    "quello", "questa", "queste", "questi", "questo", "se", "si", "sono",
    "su", "sui", "sul", "sulla", "tra", "un", "una", "uno", "va", "viene",
    "verso", "dai", "dagli", "dalle", "perché", "perche", "poi", "quindi",
    "molto", "meno", "dove", "cosa", "ogni", "tutti", "tutte", "suo",
    "sua", "suoi", "sue", "loro", "nello", "nei", "siano", "stato", "stata"
}


def slugify(text: str, fallback: str = "documento") -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text).strip("-").lower()
    return slug or fallback


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise RuntimeError(f"Non riesco a leggere il file di testo: {path}")


def read_pdf(path: Path) -> str:
    errors: list[str] = []

    try:
        from pypdf import PdfReader  # type: ignore
        reader = PdfReader(str(path))
        parts = []
        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                parts.append(f"[Pagina {index}]\n{text}")
        result = "\n\n".join(parts).strip()
        if result:
            return result
        errors.append("pypdf non ha estratto testo utile")
    except Exception as error:
        errors.append(f"pypdf: {error}")

    try:
        from PyPDF2 import PdfReader  # type: ignore
        reader = PdfReader(str(path))
        parts = []
        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                parts.append(f"[Pagina {index}]\n{text}")
        result = "\n\n".join(parts).strip()
        if result:
            return result
        errors.append("PyPDF2 non ha estratto testo utile")
    except Exception as error:
        errors.append(f"PyPDF2: {error}")

    raise RuntimeError(
        "PDF non leggibile automaticamente. Potrebbe essere una scansione immagine "
        "oppure manca la libreria PDF. Installa pypdf con: python3 -m pip install pypdf. "
        f"Dettagli: {' | '.join(errors)}"
    )


def read_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".markdown"}:
        return read_text(path)
    if suffix == ".pdf":
        return read_pdf(path)
    raise RuntimeError(f"Formato non supportato: {suffix}. Usa TXT, Markdown o PDF.")


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    return text.strip()


def split_sentences(text: str) -> list[str]:
    compact = re.sub(r"\s+", " ", text).strip()
    if not compact:
        return []
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Ü0-9])", compact)
    result = [sentence.strip(" -•\t\n") for sentence in sentences if len(sentence.strip()) >= 35]
    if result:
        return result
    return [part.strip() for part in re.split(r"[\n.;:]+", text) if len(part.strip()) >= 35]


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]{3,}", text.lower())
    return [word for word in words if word not in STOPWORDS and not word.isdigit()]


def keywords(text: str, limit: int = 24) -> list[dict[str, Any]]:
    counter = Counter(tokenize(text))
    return [{"parola": word, "frequenza": count} for word, count in counter.most_common(limit)]


def score_sentence(sentence: str, weights: dict[str, int]) -> float:
    words = tokenize(sentence)
    if not words:
        return 0.0
    base = sum(weights.get(word, 0) for word in words)
    penalty = 1 + abs(len(words) - 28) / 65
    return base / penalty


def make_summary(sentences: list[str], key_items: list[dict[str, Any]], max_items: int) -> list[str]:
    weights = {str(item["parola"]): int(item["frequenza"]) for item in key_items}
    ranked = [(score_sentence(sentence, weights), index, sentence) for index, sentence in enumerate(sentences)]
    selected = sorted(ranked, reverse=True)[:max_items]
    return [sentence for _, _, sentence in sorted(selected, key=lambda item: item[1])]


def find_context(word: str, sentences: list[str]) -> str:
    low = word.lower()
    for sentence in sentences:
        if low in sentence.lower():
            return sentence
    return sentences[0] if sentences else ""


def shorten(text: str, limit: int = 240) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= limit:
        return compact
    return compact[:limit].rsplit(" ", 1)[0].strip() + "..."


def concept_table(key_items: list[dict[str, Any]], sentences: list[str], limit: int = 14) -> list[dict[str, Any]]:
    max_freq = max([int(item["frequenza"]) for item in key_items], default=1)
    rows = []
    for item in key_items[:limit]:
        word = str(item["parola"])
        freq = int(item["frequenza"])
        rows.append({
            "concetto": word,
            "frequenza": freq,
            "importanza": max(1, min(5, math.ceil((freq / max_freq) * 5))),
            "spiegazione": shorten(find_context(word, sentences), 260),
        })
    return rows


def make_cards(rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    cards = []
    for index, row in enumerate(rows[:limit], start=1):
        cards.append({
            "id": f"RAG-CARD-{index:04d}",
            "fronte": f"Concetto chiave: {row['concetto']}",
            "retro": row["spiegazione"],
            "uso": "Ripassa questo punto e prova a rispiegarlo con parole tue.",
        })
    return cards


def make_distractors(correct: str, contexts: list[str], concept: str) -> list[str]:
    candidates = [shorten(context, 180) for context in contexts if context and shorten(context, 180) != correct]
    candidates.extend([
        f"Il documento cita {concept}, ma lo presenta come dettaglio secondario senza collegarlo al processo principale.",
        f"Il documento collega {concept} solo a un esempio isolato, non alla regola generale descritta nel contenuto.",
        f"Il documento usa {concept} come termine generico, senza indicare una funzione o una conseguenza pratica.",
    ])
    result = []
    for candidate in candidates:
        candidate = shorten(candidate, 180)
        if candidate != correct and candidate not in result:
            result.append(candidate)
        if len(result) == 3:
            break
    while len(result) < 3:
        result.append(f"Il concetto di {concept} viene collegato a una conseguenza diversa da quella corretta.")
    return result[:3]


def make_quiz(rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    contexts = [str(row["spiegazione"]) for row in rows]
    quiz = []
    for index, row in enumerate(rows[:limit], start=1):
        concept = str(row["concetto"])
        correct = shorten(str(row["spiegazione"]), 180)
        options = make_distractors(correct, contexts, concept)
        correct_index = (index - 1) % 4
        options.insert(correct_index, correct)
        quiz.append({
            "id": f"RAG-QUIZ-{index:04d}",
            "categoria": "rag",
            "livello": "intermedio",
            "domanda": f"Quale affermazione descrive meglio il concetto “{concept}” secondo il documento?",
            "opzioni": options,
            "risposta_corretta": correct,
            "indice_risposta_corretta": correct_index,
            "spiegazione": f"La risposta corretta riprende il modo in cui il documento collega “{concept}” al contenuto principale.",
        })
    return quiz


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(value).replace("|", "\\|") for value in row) + " |")
    return "\n".join(lines)


def write_csv(path: Path, headers: list[str], rows: list[list[Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)


def keyword_svg(key_items: list[dict[str, Any]], title: str) -> str:
    selected = key_items[:10]
    width = 900
    row_height = 42
    height = 120 + len(selected) * row_height
    max_freq = max([int(item["frequenza"]) for item in selected], default=1)
    bars = []
    for index, item in enumerate(selected):
        word = html.escape(str(item["parola"]))
        freq = int(item["frequenza"])
        bar_width = int((freq / max_freq) * 560)
        y = 86 + index * row_height
        bars.append(f'<text x="32" y="{y + 22}" font-size="17" fill="#e5e7eb">{word}</text>')
        bars.append(f'<rect x="220" y="{y}" width="{bar_width}" height="26" rx="8" fill="#7c3aed"/>')
        bars.append(f'<text x="{235 + bar_width}" y="{y + 20}" font-size="15" fill="#f9fafb">{freq}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" rx="28" fill="#0f172a"/>
<text x="32" y="44" font-size="26" fill="#ffffff" font-family="Arial, sans-serif">Parole chiave - {html.escape(title)}</text>
<text x="32" y="68" font-size="14" fill="#cbd5e1" font-family="Arial, sans-serif">Frequenza dei concetti principali estratti dal documento</text>
{''.join(bars)}
</svg>'''


def cards_html(cards: list[dict[str, Any]], title: str) -> str:
    body = "".join(
        f'<article class="card"><h2>{html.escape(card["fronte"])}</h2><p>{html.escape(card["retro"])}</p><small>{html.escape(card["uso"])}</small></article>'
        for card in cards
    )
    return f'''<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Card RAG - {html.escape(title)}</title><style>
body{{margin:0;font-family:Arial,sans-serif;background:#0f172a;color:#f8fafc}}main{{max-width:1100px;margin:0 auto;padding:36px 20px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}}.card{{border:1px solid rgba(255,255,255,.12);border-radius:22px;background:linear-gradient(145deg,rgba(124,58,237,.22),rgba(15,23,42,.94));padding:22px;box-shadow:0 20px 60px rgba(0,0,0,.28)}}.card h2{{font-size:20px;margin:0 0 12px}}.card p{{line-height:1.55}}.card small{{color:#cbd5e1;font-weight:700}}
</style></head><body><main><h1>Card di ripasso - {html.escape(title)}</h1><section class="grid">{body}</section></main></body></html>'''


def quiz_html(quiz: list[dict[str, Any]], title: str) -> str:
    data = json.dumps(quiz, ensure_ascii=False)
    return f'''<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Quiz RAG - {html.escape(title)}</title><style>
body{{margin:0;font-family:Arial,sans-serif;background:#111827;color:#f9fafb}}main{{max-width:980px;margin:0 auto;padding:34px 20px}}.question{{border:1px solid rgba(255,255,255,.12);border-radius:22px;padding:22px;margin:18px 0;background:rgba(255,255,255,.06)}}button{{display:block;width:100%;margin:10px 0;padding:14px;border-radius:14px;border:1px solid rgba(255,255,255,.16);background:#1f2937;color:#fff;cursor:pointer;font-weight:800;text-align:left}}button.correct{{background:#166534}}button.wrong{{background:#7f1d1d}}.explanation{{display:none;margin-top:12px;color:#d1d5db}}
</style></head><body><main><h1>Quiz generato dal documento - {html.escape(title)}</h1><div id="quiz"></div></main><script>
const quiz = {data};
const container = document.getElementById('quiz');
quiz.forEach((item, questionIndex) => {{
  const box = document.createElement('section'); box.className = 'question';
  const h = document.createElement('h2'); h.textContent = `${{questionIndex + 1}}. ${{item.domanda}}`; box.appendChild(h);
  const explanation = document.createElement('p'); explanation.className = 'explanation'; explanation.textContent = item.spiegazione;
  item.opzioni.forEach((option, optionIndex) => {{
    const button = document.createElement('button'); button.textContent = `${{String.fromCharCode(65 + optionIndex)}}. ${{option}}`;
    button.addEventListener('click', () => {{
      const allButtons = box.querySelectorAll('button'); allButtons.forEach(btn => btn.disabled = true);
      if (option === item.risposta_corretta) button.classList.add('correct');
      else {{ button.classList.add('wrong'); allButtons[item.indice_risposta_corretta].classList.add('correct'); }}
      explanation.style.display = 'block';
    }});
    box.appendChild(button);
  }});
  box.appendChild(explanation); container.appendChild(box);
}});
</script></body></html>'''


def minicourse_html(summary: list[str], cards: list[dict[str, Any]], quiz: list[dict[str, Any]], title: str) -> str:
    slides = []
    for index, sentence in enumerate(summary[:5], start=1):
        slides.append(f'<section class="slide"><span>Step {index}</span><h2>Punto chiave</h2><p>{html.escape(sentence)}</p></section>')
    for card in cards[:4]:
        slides.append(f'<section class="slide"><span>Ripasso</span><h2>{html.escape(card["fronte"])}</h2><p>{html.escape(card["retro"])}</p></section>')
    if quiz:
        slides.append(f'<section class="slide"><span>Test finale</span><h2>{html.escape(quiz[0]["domanda"])}</h2><p>Apri quiz_interattivo.html per svolgere tutte le domande.</p></section>')
    return f'''<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Minicorso RAG - {html.escape(title)}</title><style>
body{{margin:0;background:radial-gradient(circle at top,#312e81,#020617 65%);color:#f8fafc;font-family:Arial,sans-serif}}main{{max-width:1040px;margin:0 auto;padding:42px 20px}}.slide{{min-height:210px;margin:22px 0;border-radius:28px;padding:30px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.16);box-shadow:0 24px 70px rgba(0,0,0,.35)}}.slide span{{color:#a5b4fc;font-weight:900;text-transform:uppercase;letter-spacing:.08em}}.slide h2{{font-size:30px}}.slide p{{font-size:19px;line-height:1.6}}
</style></head><body><main><h1>Minicorso interattivo generato dal documento</h1><p>{html.escape(title)}</p>{''.join(slides)}</main></body></html>'''


def index_html(title: str, files: list[str]) -> str:
    links = "".join(f'<li><a href="{html.escape(name)}">{html.escape(name)}</a></li>' for name in files)
    return f'''<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Output RAG - {html.escape(title)}</title><style>body{{font-family:Arial,sans-serif;background:#0f172a;color:#f8fafc;margin:0}}main{{max-width:900px;margin:0 auto;padding:40px 20px}}a{{color:#93c5fd;font-weight:800}}li{{margin:12px 0}}</style></head><body><main><h1>Output generati dal motore RAG</h1><p>Documento: <strong>{html.escape(title)}</strong></p><ul>{links}</ul></main></body></html>'''


def analyze(text: str, title: str, max_summary: int, max_cards: int, max_quiz: int) -> dict[str, Any]:
    cleaned = clean_text(text)
    sentences = split_sentences(cleaned)
    key_items = keywords(cleaned)
    rows = concept_table(key_items, sentences)
    cards = make_cards(rows, max_cards)
    quiz = make_quiz(rows, max_quiz)
    return {
        "titolo": title,
        "generato_il": datetime.now().isoformat(timespec="seconds"),
        "statistiche": {
            "caratteri": len(cleaned),
            "parole_utili": len(tokenize(cleaned)),
            "frasi": len(sentences),
            "parole_chiave": len(key_items),
            "card": len(cards),
            "quiz": len(quiz),
        },
        "testo_estratto": cleaned,
        "parole_chiave": key_items,
        "riassunto": make_summary(sentences, key_items, max_summary),
        "tabella_concetti": rows,
        "cards": cards,
        "quiz": quiz,
    }


def write_outputs(data: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    title = str(data["titolo"])
    files: list[str] = []

    def write(name: str, content: str) -> None:
        (output_dir / name).write_text(content, encoding="utf-8")
        files.append(name)

    write("testo_estratto.md", str(data["testo_estratto"]))
    write("riassunto.md", "# Riassunto - " + title + "\n\n" + "\n".join(f"{i}. {s}" for i, s in enumerate(data["riassunto"], 1)) + "\n")

    headers = ["Concetto", "Frequenza", "Importanza", "Spiegazione"]
    table_rows = [[r["concetto"], r["frequenza"], r["importanza"], r["spiegazione"]] for r in data["tabella_concetti"]]
    write("tabelle_concetti.md", "# Tabelle concetti - " + title + "\n\n" + markdown_table(headers, table_rows) + "\n")
    write_csv(output_dir / "tabelle_concetti.csv", headers, table_rows)
    files.append("tabelle_concetti.csv")

    write("cards.json", json.dumps(data["cards"], ensure_ascii=False, indent=2))
    write("cards.html", cards_html(data["cards"], title))
    write("quiz.json", json.dumps(data["quiz"], ensure_ascii=False, indent=2))
    write("quiz_interattivo.html", quiz_html(data["quiz"], title))
    write("minicorso_interattivo.html", minicourse_html(data["riassunto"], data["cards"], data["quiz"], title))
    write("grafico_parole_chiave.svg", keyword_svg(data["parole_chiave"], title))
    write("statistiche.json", json.dumps(data["statistiche"], ensure_ascii=False, indent=2))
    write("analisi_completa.json", json.dumps(data, ensure_ascii=False, indent=2))

    report = [
        f"# Report RAG - {title}",
        "",
        f"- Generato il: {data['generato_il']}",
        f"- Caratteri estratti: {data['statistiche']['caratteri']}",
        f"- Parole utili: {data['statistiche']['parole_utili']}",
        f"- Frasi analizzate: {data['statistiche']['frasi']}",
        f"- Card generate: {data['statistiche']['card']}",
        f"- Domande quiz generate: {data['statistiche']['quiz']}",
        "",
        "## File prodotti",
        "",
    ]
    report.extend(f"- `{name}`" for name in files)
    report.extend(["", "## Nota", "", "Le domande generate sono una base automatica da rivedere prima di entrare nel database ufficiale."])
    write("report_rag.md", "\n".join(report) + "\n")
    write("index.html", index_html(title, files))


def collect_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        result = []
        for extension in SUPPORTED_EXTENSIONS:
            result.extend(path.rglob(f"*{extension}"))
        return sorted(result)
    raise RuntimeError(f"Percorso non trovato: {path}")


def process_file(path: Path, output_base: Path, title: str | None, max_summary: int, max_cards: int, max_quiz: int) -> Path:
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise RuntimeError(f"Formato non supportato: {path.name}")
    doc_title = title or path.stem.replace("_", " ").replace("-", " ").strip()
    text = clean_text(read_document(path))
    if len(text) < 120:
        raise RuntimeError(f"Testo estratto da {path.name} troppo corto. Il PDF potrebbe essere una scansione immagine.")
    output_dir = output_base / slugify(doc_title, path.stem)
    data = analyze(text, doc_title, max_summary, max_cards, max_quiz)
    write_outputs(data, output_dir)
    return output_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Motore RAG locale non bloccante per TXT, Markdown e PDF.")
    parser.add_argument("input", help="File o cartella da analizzare")
    parser.add_argument("--titolo", default=None, help="Titolo leggibile del documento")
    parser.add_argument("--output", default="output_generati", help="Cartella output")
    parser.add_argument("--max-riassunto", type=int, default=8)
    parser.add_argument("--max-card", type=int, default=12)
    parser.add_argument("--max-quiz", type=int, default=10)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_base = Path(args.output).expanduser().resolve()
    files = collect_files(input_path)
    if not files:
        raise RuntimeError("Nessun file TXT, Markdown o PDF trovato.")
    generated = []
    for file in files:
        print(f"📄 Analisi file: {file.name}")
        generated_dir = process_file(file, output_base, args.titolo if len(files) == 1 else None, args.max_riassunto, args.max_card, args.max_quiz)
        generated.append(generated_dir)
        print(f"✅ Output generati in: {generated_dir}")
    print("\n✅ Motore RAG completato. Nessun server avviato, terminale libero.")
    for directory in generated:
        print(f"   - {directory}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"❌ Errore: {error}")
        raise SystemExit(1)
