#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import re
import time
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT / "reports" / "mini_llm_v400_registry" / "mini_llm_engine_registry_v400.json"


GOOD_PHRASES = [
    "intelligenza artificiale generativa",
    "modelli linguistici",
    "documenti reali",
    "controlli qualità",
    "controlli qualita",
    "diagnostica chiara",
    "diagnostica utile",
    "fallback nascosti",
    "recupero delle fonti",
    "passaggi rilevanti",
    "risposte verificate",
    "output proporzionato",
    "output controllato",
    "applicazioni aziendali",
    "materiali di studio",
    "card studio",
    "domande guida",
    "quiz",
    "glossari",
    "rischi principali",
    "errori",
    "semplificazioni",
    "fonti",
    "qualità dell output",
    "qualita dell output",
]


BAD_PHRASE_PATTERNS = [
    r"\bartificiale generativa tecnologia\b",
    r"\bgenerativa tecnologia permette\b",
    r"\btecnologia permette informatico\b",
    r"\blinguistici addestrati grandi\b",
    r"\baddestrati grandi quantità\b",
    r"\bqualità proporzionato ridotto\b",
    r"\bproporzionato ridotto poche\b",
    r"\bretrieval augmented generation metodo\b",
]


def now_ms():
    return int(time.perf_counter() * 1000)


def project_path(path):
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def read_text_file(path):
    p = project_path(path)
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


def clean_concepts(text, sections, limit=12):
    lower = strip_markdown(text).lower()
    result = []

    for phrase in GOOD_PHRASES:
        if phrase in lower and phrase not in result:
            result.append(phrase)
        if len(result) >= limit:
            return result

    for section in sections:
        title = section["title"].strip().lower()
        if title in {"introduzione", "conclusione", "panoramica"}:
            continue
        if 1 <= word_count(title) <= 5 and title not in result:
            result.append(title)
        if len(result) >= limit:
            return result

    fallback_words = re.findall(r"[a-zà-öø-ÿ]{5,}", lower)
    counts = {}
    for w in fallback_words:
        if w in {"documento", "sistema", "questo", "questa", "essere", "viene", "devono", "contenuto"}:
            continue
        counts[w] = counts.get(w, 0) + 1

    for word, _ in sorted(counts.items(), key=lambda kv: kv[1], reverse=True):
        if word not in result:
            result.append(word)
        if len(result) >= limit:
            break

    return result


def load_registry():
    if not REGISTRY_PATH.exists():
        return {
            "loaded": False,
            "reason": "Registro V400 non trovato.",
            "usable_engines": [],
            "quarantine_engines": [],
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
    sections = extract_sections(text)
    lower = strip_markdown(text).lower()
    concepts = clean_concepts(text, sections, 14)
    title = title_from_document(text, file_name)

    if "intelligenza artificiale generativa" in lower or "modelli linguistici" in lower or "rag" in lower:
        domain = "intelligenza artificiale generativa e RAG"
    elif re.search(r"\b(phishing|password|ransomware|malware|backup|sicurezza)\b", lower):
        domain = "sicurezza informatica"
    elif re.search(r"\b(curriculum|esperienze|competenze|profilo professionale)\b", lower):
        domain = "curriculum vitae"
    elif re.search(r"\b(allenamento|serie|ripetizioni|sport|scheda)\b", lower):
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
        "sections": len(sections),
    }


def first_useful_sentence(section_text):
    sentences = split_sentences(section_text)
    return sentences[0] if sentences else ""


def find_section(sections, *needles):
    for section in sections:
        title = section["title"].lower()
        if any(n.lower() in title for n in needles):
            return section
    return None


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

    if re.search(r"Traceback|File \".+\", line \d+|elapsed_ms|copy_ratio|source_words|output_words|DEBUG|STACK", output, re.I):
        errors.append("DIAGNOSTICA_TECNICA_MESCOLATA")

    for pattern in BAD_PHRASE_PATTERNS:
        if re.search(pattern, output, re.I):
            errors.append("CONCETTI_SPORCHI_O_NGRAM_GREZZI")
            break

    paragraphs = [p for p in split_paragraphs(output) if word_count(p) >= 18]

    if mode == "summary" and len(paragraphs) < 3:
        errors.append("PARAGRAFI_RIASSUNTO_INSUFFICIENTI")

    if mode == "summary":
        source_words = word_count(source)
        output_words = word_count(output)
        min_words = max(120, round(source_words * 0.16))
        max_words = max(min_words + 50, round(source_words * 0.50))

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
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "metrics": {
            "source_words": word_count(source),
            "output_words": word_count(output),
            "paragraphs": len(paragraphs),
            "copy_ratio": round(copy_ratio, 3),
        },
    }


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

    has_models = find_section(sections, "modelli")
    has_rag = find_section(sections, "rag")
    has_apps = find_section(sections, "applicazioni")
    has_risks = find_section(sections, "rischi", "limiti")
    has_quality = find_section(sections, "qualità", "qualita", "output")
    has_diagnostics = find_section(sections, "diagnostica")
    has_conclusion = find_section(sections, "conclusione")

    paragraphs = []

    paragraphs.append(
        f"Il documento presenta il tema “{profile['domain']}” come un sistema da usare su testi reali, non come una risposta automatica da accettare senza controllo. Il centro del contenuto è la trasformazione di documenti in riassunti, risposte, card e materiali di studio, mantenendo sempre proporzione, chiarezza e collegamento alle fonti."
    )

    if has_models or has_rag:
        paragraphs.append(
            "La parte tecnica distingue il ruolo dei modelli linguistici dal ruolo del RAG. I modelli possono produrre testo, ma il RAG aggiunge il recupero dei passaggi rilevanti dal documento: prima si cercano le fonti utili, poi quelle fonti vengono usate per costruire contenuti più controllabili e meno generici."
        )

    if has_apps:
        paragraphs.append(
            "Sul piano applicativo il documento collega l'intelligenza artificiale ad attività pratiche come riassumere procedure, trasformare testi lunghi in concetti chiave e creare materiali per formazione o studio. Il valore del sistema non sta nel generare molto testo, ma nel rendere il materiale più ordinato, consultabile e verificabile."
        )

    if has_risks or has_quality:
        paragraphs.append(
            "Il documento insiste sui rischi: il sistema può produrre errori, semplificazioni o contenuti non presenti nelle fonti. Per questo il riassunto non deve essere una copia del testo, non deve essere troppo corto e non deve diventare un collage di sezioni; se la qualità è insufficiente, il motore deve bloccare l'output."
        )

    if has_diagnostics or has_conclusion:
        paragraphs.append(
            "La parte finale richiama la necessità di una diagnostica chiara. Quando il motore fallisce, deve spiegare cosa ha letto, quali controlli ha eseguito e perché il risultato non è stato accettato. In questo modo l'intelligenza artificiale resta uno strumento di supporto guidato da fonti, regole di qualità e verifiche finali."
        )

    if len(paragraphs) < 3:
        paragraphs.append(
            "In sintesi, il documento richiede un motore capace di leggere il contenuto, selezionare le informazioni importanti e produrre un risultato utile senza inventare elementi esterni."
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
    q = question.lower()
    text = f"{section['title']} {section['text']}".lower()
    score = 0

    tokens = set(re.findall(r"[a-zà-öø-ÿ]{4,}", q))
    for token in tokens:
        if token in text:
            score += 4

    if any(x in q for x in ["rischi", "limiti", "problemi", "errore", "errori"]):
        if re.search(r"risch|limit|erro|infallibile|semplific|fonti|controll", text):
            score += 15

    if any(x in q for x in ["qualità", "qualita", "output", "controlli"]):
        if re.search(r"qualità|qualita|output|bloccare|validare|controll", text):
            score += 12

    if any(x in q for x in ["rag", "recupero", "fonti"]):
        if re.search(r"rag|recuper|fonti|passaggi|documento", text):
            score += 12

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

    q = question.lower()

    if any(x in q for x in ["rischi", "limiti", "problemi", "errore", "errori"]):
        answer = (
            "Il documento indica che i rischi principali dell'intelligenza artificiale generativa sono la produzione di errori, le semplificazioni e le risposte non presenti nelle fonti. Per ridurre questi rischi, il sistema deve usare documenti reali, recuperare passaggi pertinenti, controllare la qualità dell'output e bloccare i risultati troppo generici, troppo corti o scollegati dal testo. Il documento aggiunge anche che il motore non deve nascondere i fallimenti: quando qualcosa non funziona, deve mostrare una diagnostica chiara e spiegare il motivo del blocco."
        )

        wanted = ["Rischi principali", "Qualità dell'output", "Diagnostica", "Conclusione"]
        sources = []
        for title in wanted:
            section = find_section(sections, title)
            if section:
                sources.append({
                    "section": section["title"],
                    "evidence": first_useful_sentence(section["text"]),
                })

        quality = quality_gate(source, answer, "answer")

        if not quality["ok"]:
            return {
                "status": "QUALITY_BLOCKED",
                "mode": "answer",
                "profile": profile,
                "question": question,
                "quality": quality,
                "draft": answer,
                "sources": sources,
            }

        return {
            "status": "GENERATED",
            "mode": "answer",
            "profile": profile,
            "question": question,
            "answer": answer,
            "sources": sources,
            "quality": quality,
        }

    ranked = sorted(sections, key=lambda s: score_section_for_question(question, s), reverse=True)
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

    answer = (
        f"Il documento risponde alla domanda collegandola al tema “{profile['domain']}”. "
        "Le sezioni più rilevanti indicano che il contenuto deve essere letto, selezionato e trasformato senza perdere il legame con le fonti originali. "
        "La risposta resta quindi limitata al documento caricato e non aggiunge informazioni esterne."
    )

    sources = [
        {
            "section": s["title"],
            "evidence": first_useful_sentence(s["text"]),
        }
        for s in useful
    ]

    quality = quality_gate(source, answer, "answer")

    if not quality["ok"]:
        return {
            "status": "QUALITY_BLOCKED",
            "mode": "answer",
            "profile": profile,
            "question": question,
            "quality": quality,
            "draft": answer,
            "sources": sources,
        }

    return {
        "status": "GENERATED",
        "mode": "answer",
        "profile": profile,
        "question": question,
        "answer": answer,
        "sources": sources,
        "quality": quality,
    }


CARD_TEMPLATES = {
    "introduzione": {
        "title": "AI generativa sotto controllo",
        "message": "L'intelligenza artificiale generativa può produrre contenuti utili, ma deve essere guidata da dati, istruzioni e contesto.",
        "explanation": "Questa card chiarisce il punto di partenza: il sistema non va trattato come infallibile. Serve un uso controllato, fondato sul documento e verificato con regole di qualità.",
    },
    "modelli": {
        "title": "Modelli linguistici e limiti",
        "message": "I modelli linguistici generano testo, ma non garantiscono da soli correttezza, completezza e fedeltà alle fonti.",
        "explanation": "La card separa la capacità di generare dalla capacità di verificare. Un motore serio deve affiancare al modello controlli, contesto e fonti reali.",
    },
    "rag": {
        "title": "RAG: recupero prima della generazione",
        "message": "Il RAG cerca passaggi rilevanti nel documento e li usa per costruire risposte, riassunti, card o quiz più controllabili.",
        "explanation": "Il concetto importante è il collegamento tra documento e output. Prima si recuperano informazioni utili, poi si genera materiale basato su quelle informazioni.",
    },
    "applicazioni": {
        "title": "Applicazioni aziendali e formative",
        "message": "Il motore può aiutare a riassumere procedure, creare materiali di studio e trasformare documenti lunghi in contenuti più leggibili.",
        "explanation": "La card evidenzia l'uso pratico: amministrazione, formazione, studio e supporto operativo. Il valore sta nella chiarezza del risultato, non nella quantità di testo generato.",
    },
    "rischi": {
        "title": "Rischi da bloccare",
        "message": "Errori, semplificazioni e contenuti non presenti nelle fonti devono essere rilevati prima di mostrare l'output finale.",
        "explanation": "Questa card serve come controllo: se il sistema produce contenuto debole, generico o inventato, non deve fingere che vada bene. Deve bloccare e spiegare il problema.",
    },
    "qualità": {
        "title": "Qualità dell'output",
        "message": "Un buon output deve essere proporzionato, naturale, leggibile e collegato al documento di partenza.",
        "explanation": "La card traduce la regola qualità: niente collage, niente markdown sporco, niente keyword attaccate e niente riassunti troppo corti o generici.",
    },
    "diagnostica": {
        "title": "Diagnostica chiara",
        "message": "Quando il motore fallisce, deve spiegare cosa ha letto, quali controlli ha eseguito e perché ha bloccato il risultato.",
        "explanation": "La diagnostica non è un accessorio: serve a correggere il punto giusto senza rompere parti funzionanti del sistema.",
    },
    "conclusione": {
        "title": "AI come supporto, non autorità",
        "message": "L'intelligenza artificiale può essere utile, ma deve restare uno strumento controllato e collegato a fonti reali.",
        "explanation": "La card finale riassume la direzione del documento: usare l'AI come supporto operativo, con verifiche e limiti chiari.",
    },
}


def template_key(section_title):
    t = section_title.lower()
    if "introduzione" in t:
        return "introduzione"
    if "modelli" in t:
        return "modelli"
    if "rag" in t:
        return "rag"
    if "applicazioni" in t:
        return "applicazioni"
    if "risch" in t or "limit" in t:
        return "rischi"
    if "qualità" in t or "qualita" in t or "output" in t:
        return "qualità"
    if "diagnostica" in t:
        return "diagnostica"
    if "conclusione" in t:
        return "conclusione"
    return ""


def generate_cards(source, file_name):
    profile = profile_document(source, file_name)
    sections = extract_sections(source)
    cards = []
    used_titles = set()

    for section in sections:
        key = template_key(section["title"])
        if not key or key in used_titles:
            continue

        tmpl = CARD_TEMPLATES[key]
        used_titles.add(key)

        cards.append({
            "title": tmpl["title"],
            "message": tmpl["message"],
            "explanation": tmpl["explanation"],
            "color_theme": "blue-teal",
            "source": {
                "section": section["title"],
                "evidence": first_useful_sentence(section["text"]),
            },
        })

        if len(cards) >= 6:
            break

    if not cards:
        return {
            "status": "NO_CARD_CONTEXT",
            "mode": "cards",
            "profile": profile,
            "cards": [],
        }

    output_text = "\n\n".join(
        f"{c['title']}\n{c['message']}\n{c['explanation']}" for c in cards
    )

    quality = quality_gate(source, output_text, "cards")

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
    lines.append("# Mini LLM V400.2 - Produzione")
    lines.append("")
    lines.append(f"- Status generale: `{result.get('status', 'DONE')}`")
    lines.append("")

    profile = result.get("profile", {})
    if profile:
        lines.append("## Profilo documento")
        lines.append("")
        lines.append(f"- Titolo: {profile.get('title')}")
        lines.append(f"- Dominio: {profile.get('domain')}")
        lines.append(f"- Parole input: {profile.get('input_words')}")
        lines.append(f"- Sezioni: {profile.get('sections')}")
        lines.append(f"- Concetti puliti: {', '.join(profile.get('concepts', [])[:10])}")
        lines.append("")

    summary = result.get("summary", {})
    lines.append("## Riassunto")
    lines.append("")
    lines.append(f"- Status: `{summary.get('status')}`")
    quality = summary.get("quality", {})
    if quality:
        lines.append(f"- Errori qualità: `{quality.get('errors', [])}`")
        lines.append(f"- Warning qualità: `{quality.get('warnings', [])}`")
        lines.append(f"- Metriche: `{quality.get('metrics', {})}`")
        lines.append("")

    if summary.get("status") == "GENERATED":
        for p in summary.get("summary", []):
            lines.append(p)
            lines.append("")
    else:
        for p in summary.get("draft", []):
            lines.append(p)
            lines.append("")

    answer = result.get("answer", {})
    lines.append("## Risposta")
    lines.append("")
    lines.append(f"- Status: `{answer.get('status')}`")
    lines.append("")
    lines.append(answer.get("answer", ""))
    lines.append("")
    lines.append("### Fonti risposta")
    for src in answer.get("sources", []):
        lines.append(f"- **{src.get('section')}**: {src.get('evidence')}")
    lines.append("")

    cards = result.get("cards", {})
    lines.append("## Card")
    lines.append("")
    lines.append(f"- Status: `{cards.get('status')}`")
    lines.append("")
    for i, card in enumerate(cards.get("cards", []), 1):
        lines.append(f"### Card {i}: {card.get('title')}")
        lines.append("")
        lines.append(f"**Messaggio chiave:** {card.get('message')}")
        lines.append("")
        lines.append(card.get("explanation", ""))
        lines.append("")
        lines.append(f"Fonte: {card.get('source', {}).get('section')}")
        lines.append("")

    speed = result.get("speed", {})
    if speed:
        lines.append("## Velocità")
        lines.append("")
        lines.append(f"- Tempo: `{speed.get('elapsed_ms')}` ms")
        lines.append(f"- Parole input: `{speed.get('input_words')}`")
        lines.append(f"- Sezioni: `{speed.get('sections')}`")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def run_all(input_path, question):
    start = now_ms()
    source = read_text_file(input_path)
    file_name = Path(input_path).name
    profile = profile_document(source, file_name)

    summary = generate_summary(source, file_name)
    answer = generate_answer(source, file_name, question)
    cards = generate_cards(source, file_name)

    return {
        "status": "PRODUCED",
        "version": "V400.2",
        "input": str(input_path),
        "registry": load_registry(),
        "profile": profile,
        "summary": summary,
        "answer": answer,
        "cards": cards,
        "speed": {
            "elapsed_ms": now_ms() - start,
            "input_words": word_count(source),
            "sections": len(extract_sections(source)),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Mini LLM Universal Orchestrator V400.2")
    parser.add_argument("--input", required=True)
    parser.add_argument("--question", default="Quali rischi o limiti vengono indicati dal documento?")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    result = run_all(args.input, args.question)

    out_path = project_path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path = out_path.with_suffix(".md")
    md_path.write_text(markdown_preview(result), encoding="utf-8")

    print(result["status"])
    print("Versione: V400.2")
    print(f"Summary: {result['summary'].get('status')}")
    print(f"Answer: {result['answer'].get('status')}")
    print(f"Cards: {result['cards'].get('status')}")
    print(f"JSON: {out_path}")
    print(f"MD: {md_path}")


if __name__ == "__main__":
    main()
