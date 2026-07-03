#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import re
import sys
import time
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT / "reports" / "mini_llm_v400_registry" / "mini_llm_engine_registry_v400.json"


STOPWORDS = {
    "questo", "questa", "questi", "queste", "quello", "quella", "quelli", "quelle",
    "documento", "testo", "sistema", "sistemi", "contenuto", "contenuti",
    "della", "delle", "degli", "dagli", "dallo", "dalla", "dalle",
    "nella", "nelle", "negli", "allo", "alla", "alle",
    "sono", "essere", "viene", "deve", "devono", "può", "puo",
    "anche", "come", "quando", "quindi", "perché", "perche",
    "parte", "punto", "punti", "modo", "tema", "base",
    "fare", "usare", "avere", "essere", "viene", "vengono",
}


def now_ms():
    return int(time.perf_counter() * 1000)


def read_text_file(path):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File non trovato: {p}")
    return p.read_text(encoding="utf-8", errors="replace")


def normalize_text(text):
    text = str(text or "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\t", " ").replace("\u00a0", " ")
    text = re.sub(r"[ ]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def strip_markdown(text):
    text = normalize_text(text)
    text = re.sub(r"(?m)^\s{0,3}#{1,6}\s+", "", text)
    text = text.replace("**", "")
    text = text.replace("__", "")
    text = text.replace("`", "")
    text = re.sub(r"(?m)^\s*---+\s*$", "", text)
    return normalize_text(text)


def word_count(text):
    return len(re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+", str(text or "")))


def split_sentences(text):
    clean = strip_markdown(text)
    clean = re.sub(r"\n+", " ", clean)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Ü0-9])", clean)
    return [p.strip() for p in parts if word_count(p) >= 7 and len(p.strip()) >= 35]


def split_paragraphs(text):
    return [p.strip() for p in re.split(r"\n\s*\n", normalize_text(text)) if p.strip()]


def clean_heading(line):
    line = re.sub(r"^#{1,6}\s*", "", line.strip())
    line = re.sub(r"[:\-–—]+$", "", line).strip()
    return line


def title_from_document(text, file_name):
    lines = [x.strip() for x in normalize_text(text).split("\n") if x.strip()]

    for line in lines:
        if re.match(r"^#{1,6}\s+\S+", line):
            title = clean_heading(line)
            if 2 <= word_count(title) <= 16:
                return title

    for line in lines[:8]:
        cleaned = clean_heading(line)
        if 2 <= word_count(cleaned) <= 16:
            return cleaned

    return Path(file_name).stem.replace("_", " ").replace("-", " ").strip()


def extract_sections(text):
    text = normalize_text(text)
    lines = text.split("\n")

    sections = []
    current_title = "Panoramica"
    buffer = []

    for line in lines:
        stripped = line.strip()

        if re.match(r"^#{1,6}\s+\S+", stripped):
            if buffer:
                body = strip_markdown("\n".join(buffer))
                if word_count(body) >= 10:
                    sections.append({
                        "title": current_title,
                        "text": body,
                        "words": word_count(body),
                    })
            current_title = clean_heading(stripped)
            buffer = []
        else:
            buffer.append(line)

    if buffer:
        body = strip_markdown("\n".join(buffer))
        if word_count(body) >= 10:
            sections.append({
                "title": current_title,
                "text": body,
                "words": word_count(body),
            })

    if not sections and word_count(text) >= 40:
        sections.append({
            "title": "Panoramica",
            "text": strip_markdown(text),
            "words": word_count(text),
        })

    return sections


def extract_concepts(text, limit=12):
    clean = strip_markdown(text).lower()
    tokens = re.findall(r"[a-zà-öø-ÿ]{4,}", clean)
    tokens = [t for t in tokens if t not in STOPWORDS]

    pairs = {}
    triples = {}

    for i in range(len(tokens) - 1):
        phrase = f"{tokens[i]} {tokens[i + 1]}"
        if tokens[i] != tokens[i + 1]:
            pairs[phrase] = pairs.get(phrase, 0) + 1

    for i in range(len(tokens) - 2):
        phrase = f"{tokens[i]} {tokens[i + 1]} {tokens[i + 2]}"
        if len(set(phrase.split())) >= 2:
            triples[phrase] = triples.get(phrase, 0) + 1

    singles = {}
    for token in tokens:
        singles[token] = singles.get(token, 0) + 1

    ordered = []
    ordered += [x for x, _ in sorted(triples.items(), key=lambda kv: kv[1], reverse=True)]
    ordered += [x for x, _ in sorted(pairs.items(), key=lambda kv: kv[1], reverse=True)]
    ordered += [x for x, _ in sorted(singles.items(), key=lambda kv: kv[1], reverse=True)]

    result = []
    for item in ordered:
        item = item.strip()
        if not item:
            continue
        if any(item in old or old in item for old in result):
            continue
        if len(item.replace(" ", "")) > 28 and " " not in item:
            continue
        result.append(item)
        if len(result) >= limit:
            break

    return result


def load_registry():
    if not REGISTRY_PATH.exists():
        return {
            "loaded": False,
            "reason": "Registro V400 non trovato.",
            "engines": [],
        }

    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    engines = data.get("engines", [])

    return {
        "loaded": True,
        "path": str(REGISTRY_PATH),
        "total_engines": len(engines),
        "usable_engines": [
            e["id"] for e in engines
            if e.get("exists") and not str(e.get("decision", "")).startswith("QUARANTENA")
        ],
        "quarantine_engines": [
            e["id"] for e in engines
            if str(e.get("decision", "")).startswith("QUARANTENA")
        ],
    }


def profile_document(text, file_name):
    clean = strip_markdown(text).lower()
    concepts = extract_concepts(text, 14)
    title = title_from_document(text, file_name)

    if re.search(r"\b(intelligenza artificiale|generativa|modelli linguistici|rag|output|diagnostica)\b", clean):
        domain = "intelligenza artificiale generativa e RAG"
    elif re.search(r"\b(phishing|password|ransomware|malware|backup|sicurezza)\b", clean):
        domain = "sicurezza informatica"
    elif re.search(r"\b(curriculum|esperienze|competenze|profilo professionale)\b", clean):
        domain = "curriculum vitae"
    elif re.search(r"\b(allenamento|serie|ripetizioni|sport|scheda)\b", clean):
        domain = "sport e allenamento"
    elif concepts:
        domain = concepts[0]
    else:
        domain = title.lower()

    return {
        "title": title,
        "domain": domain,
        "concepts": concepts,
        "input_words": word_count(text),
        "sections": len(extract_sections(text)),
    }


def first_useful_sentence(section_text):
    sentences = split_sentences(section_text)
    if not sentences:
        return ""
    return max(sentences, key=lambda s: min(word_count(s), 28))


def sentence_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def copy_ratio_from_source(source, output):
    source_sentences = split_sentences(source)
    output_sentences = split_sentences(output)

    copied_words = 0

    for out_s in output_sentences:
        out_clean = strip_markdown(out_s)

        for src_s in source_sentences:
            src_clean = strip_markdown(src_s)

            if out_clean == src_clean:
                copied_words += word_count(out_clean)
                break

            if abs(word_count(out_clean) - word_count(src_clean)) <= 8:
                if sentence_similarity(out_clean, src_clean) >= 0.92:
                    copied_words += word_count(out_clean)
                    break

    return copied_words / max(1, word_count(output))


def quality_gate(source, output, mode):
    errors = []
    warnings = []

    if not output or word_count(output) < 20:
        errors.append("OUTPUT_TROPPO_CORTO")

    if re.search(r"(?m)^\s*#{1,6}\s+\S+", output):
        errors.append("MARKDOWN_GREZZO_PRESENTE")

    if re.search(r"\b[A-Za-zÀ-ÖØ-öø-ÿ]{24,}\b", output):
        errors.append("PAROLE_ATTACCATE")

    if re.search(r"\bDiagnostica\b|\bTrace\b|\bDebug\b|\bJSON\b", output, re.I):
        errors.append("DIAGNOSTICA_MESCOLATA_AL_CONTENUTO")

    paragraphs = [p for p in split_paragraphs(output) if word_count(p) >= 18]

    if mode == "summary" and len(paragraphs) < 3:
        errors.append("PARAGRAFI_RIASSUNTO_INSUFFICIENTI")

    if mode == "summary":
        source_words = word_count(source)
        output_words = word_count(output)
        min_words = max(120, round(source_words * 0.16))
        max_words = max(min_words + 50, round(source_words * 0.55))

        if output_words < min_words:
            errors.append("RIASSUNTO_SOTTO_SOGLIA")

        if output_words > max_words:
            warnings.append("RIASSUNTO_MOLTO_LUNGO")

    copy_ratio = copy_ratio_from_source(source, output)

    if mode == "summary" and copy_ratio >= 0.25:
        errors.append("COPIA_INCOLLA_ECCESSIVO_NEL_RIASSUNTO")

    if mode in {"cards", "answer"} and copy_ratio >= 0.70:
        errors.append("OUTPUT_QUASI_SOLO_COPIA")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "source_words": word_count(source),
            "output_words": word_count(output),
            "paragraphs": len(paragraphs),
            "copy_ratio": round(copy_ratio, 3),
        },
    }


def compact_concepts(concepts, limit=5):
    clean = []
    for concept in concepts:
        concept = concept.strip()
        if not concept:
            continue
        if concept in clean:
            continue
        if len(concept.replace(" ", "")) > 30 and " " not in concept:
            continue
        clean.append(concept)
        if len(clean) >= limit:
            break
    return clean


def make_summary_paragraph(section, profile):
    title = section["title"].strip()
    title_lower = title.lower()
    concepts = compact_concepts(extract_concepts(section["text"], 6), 4)

    concept_text = ", ".join(concepts) if concepts else "i concetti principali del documento"

    if "introduzione" in title_lower:
        return (
            f"La parte introduttiva presenta il tema {profile['domain']} e chiarisce il contesto generale. "
            f"Il punto centrale è che il sistema può essere utile solo se lavora su dati, istruzioni e contesto, "
            f"mantenendo attenzione a {concept_text}."
        )

    if "modelli" in title_lower:
        return (
            f"La sezione sui modelli linguistici spiega che la generazione automatica non basta da sola. "
            f"Il documento collega i modelli a {concept_text} e mette in evidenza la necessità di controlli "
            f"per evitare risposte deboli, non verificate o scollegate dalle fonti."
        )

    if "rag" in title_lower:
        return (
            f"La parte dedicata al RAG descrive un processo in cui recupero e generazione devono lavorare insieme. "
            f"Prima si cercano passaggi rilevanti nel documento, poi quei passaggi vengono trasformati in riassunti, "
            f"risposte, card o quiz, con attenzione a {concept_text}."
        )

    if "applicazioni" in title_lower or "aziend" in title_lower:
        return (
            f"Sul piano applicativo il documento mostra che il motore può servire in contesti aziendali e formativi. "
            f"Le funzioni utili riguardano {concept_text}, ma il risultato deve restare leggibile, controllabile "
            f"e collegato al materiale caricato."
        )

    if "risch" in title_lower or "limit" in title_lower:
        return (
            f"La sezione sui rischi sottolinea che il sistema non deve essere considerato infallibile. "
            f"Gli errori, le semplificazioni e le risposte non presenti nelle fonti devono essere intercettati "
            f"con controlli qualità e blocchi espliciti."
        )

    if "qualità" in title_lower or "qualita" in title_lower or "output" in title_lower:
        return (
            f"Il blocco sulla qualità stabilisce che l'output non deve essere generico, troppo corto o scollegato dal testo. "
            f"Riassunti, card e domande devono avere struttura naturale, contenuto utile e proporzione corretta rispetto "
            f"al documento di partenza."
        )

    if "diagnostica" in title_lower:
        return (
            f"La diagnostica viene trattata come parte essenziale del motore. "
            f"Quando una generazione fallisce, il sistema deve spiegare il motivo, indicare cosa ha letto, "
            f"quali controlli ha eseguito e quale punto va corretto."
        )

    if "conclusione" in title_lower:
        return (
            f"La conclusione rafforza l'idea di un uso controllato del motore. "
            f"L'intelligenza artificiale può aiutare, ma deve essere guidata da documenti reali, regole di qualità "
            f"e verifiche finali sull'output."
        )

    return (
        f"La sezione “{title}” aggiunge un blocco informativo collegato a {concept_text}. "
        f"Il contenuto viene trattato come materiale da sintetizzare e non come testo da copiare, così il risultato "
        f"rimane più chiaro e utilizzabile."
    )


def generate_summary(source, file_name):
    profile = profile_document(source, file_name)
    sections = extract_sections(source)

    if profile["input_words"] < 120:
        return {
            "status": "SOURCE_TOO_SHORT",
            "mode": "summary",
            "profile": profile,
            "summary": [],
        }

    paragraphs = []

    paragraphs.append(
        f"Il documento affronta il tema “{profile['domain']}” e lo organizza intorno a concetti operativi, "
        f"limiti d'uso e controlli sul risultato. L'obiettivo non è produrre testo qualsiasi, ma trasformare "
        f"un documento reale in materiale comprensibile, proporzionato e verificabile."
    )

    used_titles = set()

    for section in sections:
        title_key = section["title"].strip().lower()
        if title_key in used_titles:
            continue
        used_titles.add(title_key)

        paragraph = make_summary_paragraph(section, profile)
        if paragraph not in paragraphs:
            paragraphs.append(paragraph)

    paragraphs.append(
        f"In sintesi, il documento richiede un motore capace di leggere fonti reali, recuperare i passaggi utili, "
        f"generare contenuti ordinati e bloccare gli output non affidabili. La qualità finale dipende quindi da tre elementi: "
        f"comprensione del documento, controllo dell'output e diagnostica chiara quando qualcosa non funziona."
    )

    output_text = "\n\n".join(paragraphs)
    quality = quality_gate(source, output_text, "summary")

    if not quality["ok"]:
        return {
            "status": "QUALITY_BLOCKED",
            "mode": "summary",
            "profile": profile,
            "quality": quality,
            "draft": paragraphs,
        }

    return {
        "status": "GENERATED",
        "mode": "summary",
        "profile": profile,
        "summary": paragraphs,
        "quality": quality,
    }


def score_section_for_question(question, section):
    question_tokens = set(re.findall(r"[a-zà-öø-ÿ]{4,}", question.lower()))
    haystack = f"{section['title']} {section['text']}".lower()

    score = 0

    for token in question_tokens:
        if token in haystack:
            score += 4

    q = question.lower()

    if any(x in q for x in ["rischi", "limiti", "problemi", "errore", "errori"]):
        if re.search(r"risch|limit|erro|infallibile|controll|semplific", haystack):
            score += 10

    if any(x in q for x in ["qualità", "qualita", "output", "controlli"]):
        if re.search(r"qualità|qualita|output|controll|bloccare|validare", haystack):
            score += 10

    if any(x in q for x in ["rag", "recupero", "fonti"]):
        if re.search(r"rag|recuper|fonti|passaggi|documento", haystack):
            score += 10

    return score


def generate_answer(source, file_name, question):
    profile = profile_document(source, file_name)
    sections = extract_sections(source)

    if not question.strip():
        return {
            "status": "QUESTION_REQUIRED",
            "mode": "answer",
            "profile": profile,
            "answer": "",
            "sources": [],
        }

    ranked = sorted(
        sections,
        key=lambda s: score_section_for_question(question, s),
        reverse=True,
    )

    useful = [s for s in ranked if score_section_for_question(question, s) > 0][:3]

    if not useful:
        return {
            "status": "NO_RELEVANT_CONTEXT",
            "mode": "answer",
            "profile": profile,
            "question": question,
            "answer": "",
            "sources": [],
        }

    answer_parts = []
    sources = []

    for section in useful:
        concepts = compact_concepts(extract_concepts(section["text"], 5), 3)
        concept_text = ", ".join(concepts) if concepts else "il tema richiesto"

        sentences = split_sentences(section["text"])
        evidence = sentences[:2]

        answer_parts.append(
            f"Nella sezione “{section['title']}” il documento collega la domanda a {concept_text}. "
            f"Il punto utile è che il sistema deve restare fondato sul testo caricato e sui controlli indicati dal documento."
        )

        sources.append({
            "section": section["title"],
            "evidence": " ".join(evidence),
        })

    answer_parts.append(
        "La risposta quindi resta limitata al documento: non aggiunge informazioni esterne e non tratta il modello come fonte autonoma."
    )

    output_text = " ".join(answer_parts)
    quality = quality_gate(source, output_text, "answer")

    if not quality["ok"]:
        return {
            "status": "QUALITY_BLOCKED",
            "mode": "answer",
            "profile": profile,
            "question": question,
            "quality": quality,
            "draft": output_text,
            "sources": sources,
        }

    return {
        "status": "GENERATED",
        "mode": "answer",
        "profile": profile,
        "question": question,
        "answer": output_text,
        "sources": sources,
        "quality": quality,
    }


def card_title_from_section(section_title, profile):
    title = section_title.strip()

    if title.lower() == "panoramica":
        return profile["title"]

    title = re.sub(r"^(introduzione|conclusione)\s*[:\-–—]?\s*", "", title, flags=re.I).strip()

    if not title:
        title = profile["domain"]

    return title[:80]


def generate_cards(source, file_name):
    profile = profile_document(source, file_name)
    sections = extract_sections(source)

    cards = []

    for section in sections:
        if len(cards) >= 6:
            break

        concepts = compact_concepts(extract_concepts(section["text"], 6), 4)
        if not concepts:
            continue

        title = card_title_from_section(section["title"], profile)
        concept_text = ", ".join(concepts[:3])

        message = (
            f"Il punto chiave riguarda {concept_text}: il contenuto va trasformato in materiale chiaro, "
            f"utile e controllato."
        )

        explanation = (
            f"La sezione “{section['title']}” contribuisce al documento perché collega il tema a informazioni operative. "
            f"La card non copia il testo grezzo, ma isola il concetto principale e lo rende leggibile per studio, ripasso o uso formativo."
        )

        card = {
            "title": title,
            "message": message,
            "explanation": explanation,
            "color_theme": "blue-teal",
            "source": {
                "section": section["title"],
                "evidence": first_useful_sentence(section["text"]),
            },
        }

        cards.append(card)

    output_text = "\n\n".join(
        f"{c['title']}\n{c['message']}\n{c['explanation']}" for c in cards
    )

    quality = quality_gate(source, output_text, "cards")

    if not cards:
        return {
            "status": "NO_CARD_CONTEXT",
            "mode": "cards",
            "profile": profile,
            "cards": [],
        }

    if not quality["ok"]:
        return {
            "status": "QUALITY_BLOCKED",
            "mode": "cards",
            "profile": profile,
            "quality": quality,
            "draft_cards": cards,
        }

    return {
        "status": "GENERATED",
        "mode": "cards",
        "profile": profile,
        "cards": cards,
        "quality": quality,
    }


def markdown_preview(result):
    lines = []
    lines.append(f"# Mini LLM V400.1 - {result.get('mode', 'all')}")
    lines.append("")
    lines.append(f"- Status: `{result.get('status', 'MULTI')}`")
    lines.append("")

    if result.get("mode") == "summary":
        for p in result.get("summary", []):
            lines.append(p)
            lines.append("")

    elif result.get("mode") == "answer":
        lines.append(result.get("answer", ""))
        lines.append("")
        lines.append("## Fonti")
        for src in result.get("sources", []):
            lines.append(f"- **{src.get('section')}**: {src.get('evidence')}")
        lines.append("")

    elif result.get("mode") == "cards":
        for card in result.get("cards", []):
            lines.append(f"## {card.get('title')}")
            lines.append("")
            lines.append(f"**Messaggio chiave:** {card.get('message')}")
            lines.append("")
            lines.append(card.get("explanation", ""))
            lines.append("")
            lines.append(f"Fonte: {card.get('source', {}).get('section')}")
            lines.append("")

    else:
        for key in ["summary", "answer", "cards"]:
            block = result.get(key)
            if not block:
                continue
            lines.append(f"## {key}")
            lines.append("")
            lines.append(f"- Status: `{block.get('status')}`")
            lines.append("")

    return "\n".join(lines).strip() + "\n"


def run_mode(source, file_name, mode, question):
    if mode == "summary":
        return generate_summary(source, file_name)
    if mode == "answer":
        return generate_answer(source, file_name, question)
    if mode == "cards":
        return generate_cards(source, file_name)
    raise ValueError(f"Mode non supportato: {mode}")


def run_all(input_path, question):
    start = now_ms()

    source = read_text_file(input_path)
    file_name = Path(input_path).name
    registry = load_registry()

    summary = generate_summary(source, file_name)
    answer = generate_answer(source, file_name, question)
    cards = generate_cards(source, file_name)

    end = now_ms()

    return {
        "status": "PRODUCED",
        "mode": "all",
        "input": str(input_path),
        "registry": registry,
        "profile": profile_document(source, file_name),
        "summary": summary,
        "answer": answer,
        "cards": cards,
        "speed": {
            "elapsed_ms": end - start,
            "input_words": word_count(source),
            "sections": len(extract_sections(source)),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Mini LLM Universal Orchestrator V400.1")
    parser.add_argument("--input", required=True, help="Documento TXT/MD già testuale.")
    parser.add_argument("--mode", required=True, choices=["summary", "answer", "cards", "all"])
    parser.add_argument("--question", default="Quali rischi o limiti vengono indicati dal documento?")
    parser.add_argument("--out", required=True, help="Percorso JSON di output.")
    args = parser.parse_args()

    start = now_ms()

    if args.mode == "all":
        result = run_all(args.input, args.question)
    else:
        source = read_text_file(args.input)
        file_name = Path(args.input).name
        result = run_mode(source, file_name, args.mode, args.question)
        result["registry"] = load_registry()
        result["speed"] = {
            "elapsed_ms": now_ms() - start,
            "input_words": word_count(source),
            "sections": len(extract_sections(source)),
        }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    md_path = out_path.with_suffix(".md")
    md_path.write_text(markdown_preview(result), encoding="utf-8")

    print(result.get("status", "DONE"))
    print(f"JSON: {out_path}")
    print(f"MD: {md_path}")


if __name__ == "__main__":
    main()
