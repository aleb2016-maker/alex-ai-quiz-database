#!/usr/bin/env python3
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

ITALIAN_STOPWORDS = {
    "a", "ad", "al", "alla", "allo", "ai", "agli", "alle", "anche", "avere",
    "che", "chi", "ci", "con", "come", "da", "dal", "dalla", "dallo", "dei",
    "degli", "delle", "del", "dell", "di", "e", "ed", "è", "essere", "fa",
    "fra", "gli", "ha", "hai", "hanno", "ho", "i", "il", "in", "io", "la",
    "le", "li", "lo", "ma", "mi", "nel", "nella", "nelle", "negli", "non",
    "o", "per", "più", "può", "quale", "quando", "quella", "quelli",
    "quello", "questa", "queste", "questi", "questo", "se", "si", "sono",
    "su", "sui", "sul", "sulla", "tra", "un", "una", "uno", "va", "viene",
    "verso", "dai", "dagli", "dalle", "perché", "poi", "quindi", "molto",
    "meno", "dove", "cosa", "ogni", "tutti", "tutte", "suo", "sua", "suoi",
    "sue", "loro", "nello", "nei", "come", "solo", "puo"
}


def safe_slug(text: str, fallback: str = "documento") -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text).strip("-").lower()
    return slug or fallback


def fix_mojibake_text(text: str) -> str:
    if not text:
        return text

    replacements = {
        "Ã¨": "è",
        "Ã©": "é",
        "Ã ": "à",
        "Ã²": "ò",
        "Ã¹": "ù",
        "Ã¬": "ì",
        "Ã€": "À",
        "Ãˆ": "È",
        "Ã‰": "É",
        "Ã’": "Ò",
        "Ã™": "Ù",
        "piÃ¹": "più",
        "perchÃ©": "perché",
        "qualitÃ ": "qualità",
        "vulnerabilitÃ ": "vulnerabilità",
        "puÃ²": "può",
        "giÃ ": "già",
        "Â": "",
        "â€™": "'",
        "â€œ": "“",
        "â€": "”",
        "â€“": "–",
    }

    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)

    return text


def read_text_with_fallback(path: Path) -> str:
    raw = path.read_bytes()

    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return fix_mojibake_text(raw.decode(encoding))
        except UnicodeDecodeError:
            continue

    return fix_mojibake_text(raw.decode("utf-8", errors="replace"))


def read_pdf_text(path: Path) -> str:
    errors: list[str] = []

    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(path))
        pages_text = []

        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages_text.append(f"\n\n[Pagina {page_number}]\n{page_text}")

        extracted = "\n".join(pages_text).strip()
        if extracted:
            return fix_mojibake_text(extracted)

        errors.append("pypdf: nessun testo estratto")
    except Exception as error:
        errors.append(f"pypdf: {error}")

    try:
        from PyPDF2 import PdfReader  # type: ignore

        reader = PdfReader(str(path))
        pages_text = []

        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages_text.append(f"\n\n[Pagina {page_number}]\n{page_text}")

        extracted = "\n".join(pages_text).strip()
        if extracted:
            return fix_mojibake_text(extracted)

        errors.append("PyPDF2: nessun testo estratto")
    except Exception as error:
        errors.append(f"PyPDF2: {error}")

    raise RuntimeError(
        "PDF non leggibile in automatico. "
        "Il file può essere una scansione fotografica oppure manca una libreria PDF. "
        "Prova: python3 -m pip install pypdf. "
        f"Dettagli: {' | '.join(errors)}"
    )


def read_document(path: Path) -> str:
    extension = path.suffix.lower()

    if extension in {".txt", ".md", ".markdown"}:
        return read_text_with_fallback(path)

    if extension == ".pdf":
        return read_pdf_text(path)

    raise RuntimeError(f"Formato non supportato: {path.suffix}. Usa TXT, Markdown o PDF.")


def strip_markdown_for_analysis(text: str) -> str:
    cleaned_lines = []
    inside_code_block = False

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if line.startswith("```"):
            inside_code_block = not inside_code_block
            continue

        if inside_code_block:
            continue

        if not line:
            cleaned_lines.append("")
            continue

        if line.startswith("#"):
            continue

        if line.startswith((">", "---", "***")):
            continue

        line = re.sub(r"^[-*+]\s+", "", line)
        line = re.sub(r"^\d+[.)]\s+", "", line)
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
        line = re.sub(r"`([^`]+)`", r"\1", line)
        line = line.replace("**", "").replace("__", "").replace("*", "")

        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_text(raw_text: str) -> str:
    text = fix_mojibake_text(raw_text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = strip_markdown_for_analysis(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    paragraphs = []
    for paragraph in text.split("\n\n"):
        compact = re.sub(r"\n+", " ", paragraph).strip()
        if compact:
            paragraphs.append(compact)

    return "\n\n".join(paragraphs).strip()


def split_sentences(text: str) -> list[str]:
    compact = re.sub(r"\s+", " ", text).strip()

    if not compact:
        return []

    rough_sentences = re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Ü0-9])", compact)
    cleaned = []

    for sentence in rough_sentences:
        sentence = sentence.strip(" -•\t\n")
        if len(sentence) >= 35:
            cleaned.append(sentence)

    if cleaned:
        return cleaned

    return [part.strip() for part in re.split(r"[\n.;:]+", text) if len(part.strip()) >= 35]


def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if len(p.strip()) >= 60]


def tokenize_words(text: str) -> list[str]:
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]{3,}", text.lower())
    return [word for word in words if word not in ITALIAN_STOPWORDS and not word.isdigit()]


def extract_keywords(text: str, limit: int = 24) -> list[dict[str, Any]]:
    counts = Counter(tokenize_words(text))
    return [{"parola": word, "frequenza": count} for word, count in counts.most_common(limit)]


def score_sentence(sentence: str, keyword_weights: dict[str, int]) -> float:
    words = tokenize_words(sentence)

    if not words:
        return 0.0

    base_score = sum(keyword_weights.get(word, 0) for word in words)
    length_penalty = 1 + abs(len(words) - 28) / 65

    return base_score / length_penalty


def make_summary(sentences: list[str], keywords: list[dict[str, Any]], max_sentences: int) -> list[str]:
    if not sentences:
        return []

    keyword_weights = {item["parola"]: int(item["frequenza"]) for item in keywords}
    scored = []

    for index, sentence in enumerate(sentences):
        scored.append((score_sentence(sentence, keyword_weights), index, sentence))

    selected = sorted(scored, reverse=True)[:max_sentences]
    selected_in_order = sorted(selected, key=lambda item: item[1])

    return [fix_mojibake_text(sentence) for _, _, sentence in selected_in_order]


def find_best_context_sentence(keyword: str, sentences: list[str]) -> str:
    keyword_lower = keyword.lower()

    for sentence in sentences:
        if keyword_lower in sentence.lower():
            return sentence

    return sentences[0] if sentences else ""


def shorten(text: str, limit: int = 240) -> str:
    text = fix_mojibake_text(re.sub(r"\s+", " ", str(text)).strip())

    if len(text) <= limit:
        return text

    return text[:limit].rsplit(" ", 1)[0].strip() + "..."


def make_concept_rows(
    keywords: list[dict[str, Any]],
    sentences: list[str],
    limit: int = 14,
) -> list[dict[str, Any]]:
    if not keywords or not sentences:
        return []

    max_frequency = max(int(item["frequenza"]) for item in keywords) or 1
    rows = []

    for item in keywords[:limit]:
        keyword = str(item["parola"])
        frequency = int(item["frequenza"])
        context = find_best_context_sentence(keyword, sentences)
        importance = max(1, min(5, math.ceil((frequency / max_frequency) * 5)))

        rows.append(
            {
                "concetto": keyword,
                "frequenza": frequency,
                "importanza": importance,
                "spiegazione": shorten(context, 260),
            }
        )

    return rows


def make_cards(concept_rows: list[dict[str, Any]], max_cards: int) -> list[dict[str, Any]]:
    cards = []

    for index, row in enumerate(concept_rows[:max_cards], start=1):
        concept = str(row["concetto"])
        explanation = str(row["spiegazione"])

        cards.append(
            {
                "id": f"RAG-CARD-{index:04d}",
                "fronte": f"Concetto chiave: {concept}",
                "retro": explanation,
                "uso": "Ripassa questo punto e prova a rispiegarlo con parole tue.",
            }
        )

    return cards


def make_distractors(correct_answer: str, all_contexts: list[str], concept: str) -> list[str]:
    clean_contexts = [
        shorten(context, 180)
        for context in all_contexts
        if context and shorten(context, 180) != correct_answer
    ]

    fallback = [
        f"Il documento cita {concept}, ma lo presenta come dettaglio secondario senza collegarlo al processo principale.",
        f"Il documento collega {concept} solo a un esempio isolato, non alla regola generale descritta nel contenuto.",
        f"Il documento usa {concept} come termine generico, senza indicare una funzione o una conseguenza pratica.",
    ]

    distractors = []

    for candidate in clean_contexts + fallback:
        candidate = shorten(candidate, 180)

        if candidate != correct_answer and candidate not in distractors:
            distractors.append(candidate)

        if len(distractors) == 3:
            break

    while len(distractors) < 3:
        distractors.append(f"Il concetto di {concept} viene citato, ma con una relazione diversa da quella corretta.")

    return distractors[:3]


def make_quiz(concept_rows: list[dict[str, Any]], max_questions: int) -> list[dict[str, Any]]:
    quiz = []
    contexts = [str(row["spiegazione"]) for row in concept_rows]

    for index, row in enumerate(concept_rows[:max_questions], start=1):
        concept = str(row["concetto"])
        correct_answer = shorten(str(row["spiegazione"]), 180)
        distractors = make_distractors(correct_answer, contexts, concept)
        correct_index = (index - 1) % 4
        options = distractors[:]
        options.insert(correct_index, correct_answer)

        quiz.append(
            {
                "id": f"RAG-QUIZ-{index:04d}",
                "categoria": "rag",
                "livello": "intermedio",
                "domanda": f"Quale affermazione descrive meglio il concetto “{concept}” secondo il documento?",
                "opzioni": options,
                "risposta_corretta": correct_answer,
                "indice_risposta_corretta": correct_index,
                "spiegazione": f"La risposta corretta riprende il modo in cui il documento collega “{concept}” al contenuto principale.",
            }
        )

    return quiz


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    header_line = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = []

    for row in rows:
        body.append("| " + " | ".join(str(value).replace("|", "\\|") for value in row) + " |")

    return "\n".join([header_line, separator] + body)


def write_csv(path: Path, headers: list[str], rows: list[list[Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)
        writer.writerows(rows)


def make_keyword_svg(keywords: list[dict[str, Any]], title: str) -> str:
    selected = keywords[:10]
    width = 900
    row_height = 42
    height = 120 + len(selected) * row_height
    max_frequency = max([int(item.get("frequenza", 0)) for item in selected], default=1)
    bars = []

    for index, item in enumerate(selected):
        word = html.escape(str(item.get("parola", "")))
        frequency = int(item.get("frequenza", 0))
        bar_width = int((frequency / max_frequency) * 560) if max_frequency else 0
        y = 86 + index * row_height

        bars.append(
            f'''
            <text x="32" y="{y + 22}" font-size="17" fill="#e5e7eb">{word}</text>
            <rect x="220" y="{y}" width="{bar_width}" height="26" rx="8" fill="#7c3aed"/>
            <text x="{235 + bar_width}" y="{y + 20}" font-size="15" fill="#f9fafb">{frequency}</text>
            '''
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <rect width="100%" height="100%" rx="28" fill="#0f172a"/>
    <text x="32" y="44" font-size="26" fill="#ffffff" font-family="Arial, sans-serif">Parole chiave - {html.escape(title)}</text>
    <text x="32" y="68" font-size="14" fill="#cbd5e1" font-family="Arial, sans-serif">Frequenza dei concetti principali estratti dal documento</text>
    {''.join(bars)}
</svg>'''


def make_summary_html(summary: list[str], title: str) -> str:
    items = "\n".join(f"<li>{html.escape(fix_mojibake_text(str(sentence)))}</li>" for sentence in summary)

    return f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Riassunto RAG - {html.escape(title)}</title>
<style>
body {{
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    background: radial-gradient(circle at top left, rgba(124,58,237,.24), transparent 34rem), #0f172a;
    color: #f8fafc;
}}
main {{
    max-width: 920px;
    margin: 0 auto;
    padding: 42px 20px;
}}
section {{
    border: 1px solid rgba(255,255,255,.14);
    border-radius: 28px;
    background: rgba(15,23,42,.88);
    padding: 30px;
    box-shadow: 0 24px 80px rgba(0,0,0,.34);
}}
h1 {{
    font-size: clamp(32px, 5vw, 52px);
    line-height: 1.05;
    margin-top: 0;
}}
li {{
    margin: 16px 0;
    line-height: 1.65;
    font-size: 18px;
}}
a {{
    color: #93c5fd;
    font-weight: 900;
}}
</style>
</head>
<body>
<main>
<section>
<h1>Riassunto - {html.escape(title)}</h1>
<ol>
{items}
</ol>
<p><a href="index.html">Torna agli output</a></p>
</section>
</main>
</body>
</html>'''


def make_cards_html(cards: list[dict[str, Any]], title: str) -> str:
    cards_html = []

    for card in cards:
        cards_html.append(
            f'''
            <article class="card">
                <h2>{html.escape(str(card.get("fronte", "")))}</h2>
                <p>{html.escape(str(card.get("retro", "")))}</p>
                <small>{html.escape(str(card.get("uso", "")))}</small>
            </article>
            '''
        )

    return f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Card RAG - {html.escape(title)}</title>
<style>
body {{
    margin: 0;
    font-family: Arial, sans-serif;
    background: #0f172a;
    color: #f8fafc;
}}
main {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 36px 20px;
}}
.grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 18px;
}}
.card {{
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 22px;
    background: linear-gradient(145deg, rgba(124,58,237,.22), rgba(15,23,42,.94));
    padding: 22px;
    box-shadow: 0 20px 60px rgba(0,0,0,.28);
}}
.card h2 {{
    font-size: 20px;
    margin: 0 0 12px;
}}
.card p {{
    line-height: 1.55;
}}
.card small {{
    color: #cbd5e1;
    font-weight: 700;
}}
a {{
    color: #93c5fd;
    font-weight: 900;
}}
</style>
</head>
<body>
<main>
<h1>Card di ripasso - {html.escape(title)}</h1>
<section class="grid">
{''.join(cards_html)}
</section>
<p><a href="index.html">Torna agli output</a></p>
</main>
</body>
</html>'''


def make_quiz_html(quiz: list[dict[str, Any]], title: str) -> str:
    quiz_json = json.dumps(quiz, ensure_ascii=False)

    return f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Quiz RAG - {html.escape(title)}</title>
<style>
body {{
    margin: 0;
    font-family: Arial, sans-serif;
    background: #111827;
    color: #f9fafb;
}}
main {{
    max-width: 980px;
    margin: 0 auto;
    padding: 34px 20px;
}}
.question {{
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 22px;
    padding: 22px;
    margin: 18px 0;
    background: rgba(255,255,255,.06);
}}
button {{
    display: block;
    width: 100%;
    margin: 10px 0;
    padding: 14px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,.16);
    background: #1f2937;
    color: #fff;
    cursor: pointer;
    font-weight: 800;
    text-align: left;
}}
button.correct {{
    background: #166534;
}}
button.wrong {{
    background: #7f1d1d;
}}
.explanation {{
    display: none;
    margin-top: 12px;
    color: #d1d5db;
}}
a {{
    color: #93c5fd;
    font-weight: 900;
}}
</style>
</head>
<body>
<main>
<h1>Quiz generato dal documento - {html.escape(title)}</h1>
<div id="quiz"></div>
<p><a href="index.html">Torna agli output</a></p>
</main>
<script>
const quiz = {quiz_json};
const container = document.getElementById("quiz");

quiz.forEach((item, questionIndex) => {{
    const box = document.createElement("section");
    box.className = "question";

    const title = document.createElement("h2");
    title.textContent = `${{questionIndex + 1}}. ${{item.domanda}}`;
    box.appendChild(title);

    const explanation = document.createElement("p");
    explanation.className = "explanation";
    explanation.textContent = item.spiegazione;

    item.opzioni.forEach((option, optionIndex) => {{
        const button = document.createElement("button");
        button.textContent = `${{String.fromCharCode(65 + optionIndex)}}. ${{option}}`;

        button.addEventListener("click", () => {{
            const allButtons = box.querySelectorAll("button");
            allButtons.forEach(btn => btn.disabled = true);

            if (option === item.risposta_corretta) {{
                button.classList.add("correct");
            }} else {{
                button.classList.add("wrong");
                allButtons[item.indice_risposta_corretta].classList.add("correct");
            }}

            explanation.style.display = "block";
        }});

        box.appendChild(button);
    }});

    box.appendChild(explanation);
    container.appendChild(box);
}});
</script>
</body>
</html>'''


def make_minicourse_html(
    summary: list[str],
    cards: list[dict[str, Any]],
    quiz: list[dict[str, Any]],
    title: str,
) -> str:
    slides = []

    for index, sentence in enumerate(summary[:5], start=1):
        slides.append(
            f'''
            <section class="slide">
                <span>Step {index}</span>
                <h2>Punto chiave</h2>
                <p>{html.escape(str(sentence))}</p>
            </section>
            '''
        )

    for card in cards[:4]:
        slides.append(
            f'''
            <section class="slide">
                <span>Ripasso</span>
                <h2>{html.escape(str(card.get("fronte", "")))}</h2>
                <p>{html.escape(str(card.get("retro", "")))}</p>
            </section>
            '''
        )

    if quiz:
        first_question = str(quiz[0].get("domanda", "Domanda finale"))
        slides.append(
            f'''
            <section class="slide">
                <span>Test finale</span>
                <h2>{html.escape(first_question)}</h2>
                <p>Apri il file quiz_interattivo.html per svolgere tutte le domande.</p>
            </section>
            '''
        )

    return f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Minicorso RAG - {html.escape(title)}</title>
<style>
body {{
    margin: 0;
    background: radial-gradient(circle at top, #312e81, #020617 65%);
    color: #f8fafc;
    font-family: Arial, sans-serif;
}}
main {{
    max-width: 1040px;
    margin: 0 auto;
    padding: 42px 20px;
}}
.slide {{
    min-height: 210px;
    margin: 22px 0;
    border-radius: 28px;
    padding: 30px;
    background: rgba(255,255,255,.08);
    border: 1px solid rgba(255,255,255,.16);
    box-shadow: 0 24px 70px rgba(0,0,0,.35);
}}
.slide span {{
    color: #a5b4fc;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: .08em;
}}
.slide h2 {{
    font-size: 30px;
}}
.slide p {{
    font-size: 19px;
    line-height: 1.6;
}}
a {{
    color: #93c5fd;
    font-weight: 900;
}}
</style>
</head>
<body>
<main>
<h1>Minicorso interattivo generato dal documento</h1>
<p>{html.escape(title)}</p>
{''.join(slides)}
<p><a href="index.html">Torna agli output</a></p>
</main>
</body>
</html>'''


def make_index_html(title: str, generated_files: list[str]) -> str:
    priority = [
        ("riassunto.html", "Riassunto leggibile"),
        ("quiz_interattivo.html", "Quiz interattivo"),
        ("minicorso_interattivo.html", "Minicorso interattivo"),
        ("cards.html", "Card di ripasso"),
        ("grafico_parole_chiave.svg", "Grafico parole chiave"),
        ("tabelle_concetti.md", "Tabella concetti"),
        ("report_rag.md", "Report tecnico"),
        ("analisi_completa.json", "Analisi completa JSON"),
    ]

    priority_names = {item[0] for item in priority}
    cards = []

    for filename, label in priority:
        if filename in generated_files:
            cards.append(
                f'''<a class="card" href="{html.escape(filename)}">
                    <strong>{html.escape(label)}</strong>
                    <span>{html.escape(filename)}</span>
                </a>'''
            )

    for filename in generated_files:
        if filename not in priority_names:
            cards.append(
                f'''<a class="card secondary" href="{html.escape(filename)}">
                    <strong>{html.escape(filename)}</strong>
                    <span>File generato</span>
                </a>'''
            )

    return f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Output RAG - {html.escape(title)}</title>
<style>
body {{
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    background: radial-gradient(circle at top left, rgba(185,28,28,.22), transparent 30rem),
                radial-gradient(circle at top right, rgba(124,58,237,.26), transparent 32rem),
                #020617;
    color: #f8fafc;
}}
main {{
    max-width: 1080px;
    margin: 0 auto;
    padding: 42px 20px 70px;
}}
.hero {{
    border: 1px solid rgba(255,255,255,.14);
    border-radius: 30px;
    background: rgba(15,23,42,.88);
    padding: 32px;
    box-shadow: 0 24px 80px rgba(0,0,0,.34);
    margin-bottom: 22px;
}}
h1 {{
    margin: 0 0 12px;
    font-size: clamp(34px, 5vw, 56px);
    line-height: 1.04;
}}
p {{
    color: #cbd5e1;
    line-height: 1.6;
}}
.grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(235px, 1fr));
    gap: 16px;
}}
.card {{
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 22px;
    border-radius: 24px;
    border: 1px solid rgba(255,255,255,.14);
    background: linear-gradient(145deg, rgba(124,58,237,.26), rgba(15,23,42,.95));
    color: #fff;
    text-decoration: none;
    min-height: 126px;
}}
.card strong {{
    font-size: 20px;
}}
.card span {{
    color: #cbd5e1;
    font-weight: 800;
}}
.card.secondary {{
    background: rgba(15,23,42,.76);
}}
</style>
</head>
<body>
<main>
<section class="hero">
<h1>Output generati dal motore RAG</h1>
<p>Documento: <strong>{html.escape(title)}</strong></p>
<p>Apri prima il riassunto leggibile, poi quiz, minicorso e card. I file JSON/MD/CSV restano disponibili come dati tecnici esportabili.</p>
</section>
<section class="grid">
{''.join(cards)}
</section>
</main>
</body>
</html>'''


def analyze_document(
    text: str,
    title: str,
    max_summary_sentences: int,
    max_cards: int,
    max_quiz: int,
) -> dict[str, Any]:
    cleaned_text = clean_text(text)
    sentences = split_sentences(cleaned_text)
    paragraphs = split_paragraphs(cleaned_text)
    keywords = extract_keywords(cleaned_text)
    summary = make_summary(sentences, keywords, max_summary_sentences)
    concept_rows = make_concept_rows(keywords, sentences)
    cards = make_cards(concept_rows, max_cards)
    quiz = make_quiz(concept_rows, max_quiz)

    return {
        "titolo": title,
        "generato_il": datetime.now().isoformat(timespec="seconds"),
        "statistiche": {
            "caratteri": len(cleaned_text),
            "parole": len(tokenize_words(cleaned_text)),
            "frasi": len(sentences),
            "paragrafi": len(paragraphs),
            "parole_chiave": len(keywords),
            "card": len(cards),
            "quiz": len(quiz),
        },
        "testo_estratto": cleaned_text,
        "frasi": sentences,
        "paragrafi": paragraphs,
        "parole_chiave": keywords,
        "riassunto": summary,
        "tabella_concetti": concept_rows,
        "cards": cards,
        "quiz": quiz,
    }


def write_outputs(analysis: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    title = str(analysis["titolo"])
    generated_files: list[str] = []

    extracted_text = fix_mojibake_text(str(analysis["testo_estratto"]))
    (output_dir / "testo_estratto.md").write_text(extracted_text, encoding="utf-8")
    generated_files.append("testo_estratto.md")

    summary_lines = [f"# Riassunto - {title}", ""]
    for index, sentence in enumerate(analysis["riassunto"], start=1):
        summary_lines.append(f"{index}. {fix_mojibake_text(str(sentence))}")

    (output_dir / "riassunto.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    generated_files.append("riassunto.md")

    (output_dir / "riassunto.html").write_text(make_summary_html(analysis["riassunto"], title), encoding="utf-8")
    generated_files.append("riassunto.html")

    table_headers = ["Concetto", "Frequenza", "Importanza", "Spiegazione"]
    table_rows = [
        [
            fix_mojibake_text(str(row["concetto"])),
            row["frequenza"],
            row["importanza"],
            fix_mojibake_text(str(row["spiegazione"])),
        ]
        for row in analysis["tabella_concetti"]
    ]

    tables_md = f"# Tabelle concetti - {title}\n\n"
    tables_md += markdown_table(table_headers, table_rows)
    tables_md += "\n"

    (output_dir / "tabelle_concetti.md").write_text(tables_md, encoding="utf-8")
    generated_files.append("tabelle_concetti.md")

    write_csv(output_dir / "tabelle_concetti.csv", table_headers, table_rows)
    generated_files.append("tabelle_concetti.csv")

    (output_dir / "cards.json").write_text(json.dumps(analysis["cards"], ensure_ascii=False, indent=2), encoding="utf-8")
    generated_files.append("cards.json")

    (output_dir / "cards.html").write_text(make_cards_html(analysis["cards"], title), encoding="utf-8")
    generated_files.append("cards.html")

    (output_dir / "quiz.json").write_text(json.dumps(analysis["quiz"], ensure_ascii=False, indent=2), encoding="utf-8")
    generated_files.append("quiz.json")

    (output_dir / "quiz_interattivo.html").write_text(make_quiz_html(analysis["quiz"], title), encoding="utf-8")
    generated_files.append("quiz_interattivo.html")

    (output_dir / "minicorso_interattivo.html").write_text(
        make_minicourse_html(analysis["riassunto"], analysis["cards"], analysis["quiz"], title),
        encoding="utf-8",
    )
    generated_files.append("minicorso_interattivo.html")

    (output_dir / "grafico_parole_chiave.svg").write_text(make_keyword_svg(analysis["parole_chiave"], title), encoding="utf-8")
    generated_files.append("grafico_parole_chiave.svg")

    (output_dir / "statistiche.json").write_text(json.dumps(analysis["statistiche"], ensure_ascii=False, indent=2), encoding="utf-8")
    generated_files.append("statistiche.json")

    full_analysis = {key: value for key, value in analysis.items() if key not in {"frasi", "paragrafi"}}
    (output_dir / "analisi_completa.json").write_text(json.dumps(full_analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    generated_files.append("analisi_completa.json")

    report_lines = [
        f"# Report RAG - {title}",
        "",
        f"- Generato il: {analysis['generato_il']}",
        f"- Caratteri estratti: {analysis['statistiche']['caratteri']}",
        f"- Parole utili: {analysis['statistiche']['parole']}",
        f"- Frasi analizzate: {analysis['statistiche']['frasi']}",
        f"- Paragrafi analizzati: {analysis['statistiche']['paragrafi']}",
        f"- Card generate: {analysis['statistiche']['card']}",
        f"- Domande quiz generate: {analysis['statistiche']['quiz']}",
        "",
        "## File prodotti",
        "",
    ]

    for file_name in generated_files:
        report_lines.append(f"- `{file_name}`")

    report_lines.extend(
        [
            "",
            "## Nota qualità",
            "",
            "Il riassunto HTML usa UTF-8 esplicito e testo già pulito dai marcatori Markdown.",
            "I file JSON/MD/CSV restano output tecnici esportabili.",
        ]
    )

    (output_dir / "report_rag.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    generated_files.append("report_rag.md")

    (output_dir / "index.html").write_text(make_index_html(title, generated_files), encoding="utf-8")


def process_single_file(
    input_file: Path,
    output_base_dir: Path,
    title: str | None,
    max_summary_sentences: int,
    max_cards: int,
    max_quiz: int,
) -> Path:
    if not input_file.exists():
        raise RuntimeError(f"File non trovato: {input_file}")

    if input_file.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise RuntimeError(f"Formato non supportato: {input_file.name}. Usa TXT, Markdown o PDF.")

    document_title = title or input_file.stem.replace("_", " ").replace("-", " ").strip()
    slug = safe_slug(document_title, fallback=input_file.stem)
    output_dir = output_base_dir / slug

    raw_text = read_document(input_file)
    cleaned_text = clean_text(raw_text)

    if len(cleaned_text) < 120:
        raise RuntimeError(
            f"Il testo estratto da {input_file.name} è troppo corto. "
            "Il file potrebbe essere vuoto o il PDF potrebbe essere scansionato come immagine."
        )

    analysis = analyze_document(
        cleaned_text,
        document_title,
        max_summary_sentences=max_summary_sentences,
        max_cards=max_cards,
        max_quiz=max_quiz,
    )

    write_outputs(analysis, output_dir)

    return output_dir


def collect_input_files(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]

    if input_path.is_dir():
        files = []

        for extension in SUPPORTED_EXTENSIONS:
            files.extend(input_path.rglob(f"*{extension}"))

        return sorted(files)

    raise RuntimeError(f"Percorso non trovato: {input_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Motore RAG locale non bloccante: legge TXT, Markdown o PDF e genera "
            "riassunto, tabelle, card, quiz, grafico, report e minicorso HTML."
        )
    )

    parser.add_argument("input", help="File o cartella da analizzare. Formati: .txt, .md, .markdown, .pdf")
    parser.add_argument("--titolo", default=None, help="Titolo leggibile da usare negli output.")
    parser.add_argument("--output", default="output_generati", help="Cartella base dove salvare gli output.")
    parser.add_argument("--max-riassunto", type=int, default=8, help="Numero massimo di frasi nel riassunto.")
    parser.add_argument("--max-card", type=int, default=12, help="Numero massimo di card generate.")
    parser.add_argument("--max-quiz", type=int, default=10, help="Numero massimo di domande quiz generate.")

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_base_dir = Path(args.output).expanduser().resolve()
    input_files = collect_input_files(input_path)

    if not input_files:
        raise RuntimeError("Nessun file TXT, Markdown o PDF trovato nel percorso indicato.")

    generated_dirs = []

    for input_file in input_files:
        print(f"📄 Analisi file: {input_file.name}")

        output_dir = process_single_file(
            input_file=input_file,
            output_base_dir=output_base_dir,
            title=args.titolo if len(input_files) == 1 else None,
            max_summary_sentences=args.max_riassunto,
            max_cards=args.max_card,
            max_quiz=args.max_quiz,
        )

        generated_dirs.append(output_dir)
        print(f"✅ Output generati in: {output_dir}")

    print()
    print("✅ Motore RAG completato. Nessun server avviato, terminale libero.")
    for generated_dir in generated_dirs:
        print(f"   - {generated_dir}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"❌ Errore: {error}")
        raise SystemExit(1)
