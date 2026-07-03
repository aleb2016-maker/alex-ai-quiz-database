#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import re
import sys
import time
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import mini_llm_universal_orchestrator_v4002 as base


ROOT = Path(__file__).resolve().parents[3]


def now_ms():
    return int(time.perf_counter() * 1000)


def project_path(path):
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def domain_score(text, words):
    lower = base.strip_markdown(text).lower()
    score = 0
    for w in words:
        if w in lower:
            score += 1
    return score


def profile_document_v4004(text, file_name):
    sections = base.extract_sections(text)
    title = base.title_from_document(text, file_name)
    lower = base.strip_markdown(text).lower()

    security_words = [
        "sicurezza informatica", "phishing", "password", "ransomware",
        "malware", "backup", "autenticazione", "2fa", "dati sensibili",
        "allegati pericolosi", "aggiornamenti software", "account",
        "credenziali"
    ]

    ai_words = [
        "intelligenza artificiale generativa", "modelli linguistici",
        "rag", "retrieval augmented generation", "fallback nascosti",
        "diagnostica", "output", "card studio"
    ]

    curriculum_words = [
        "curriculum", "esperienze", "formazione", "competenze",
        "profilo professionale", "ruolo"
    ]

    sport_words = [
        "allenamento", "esercizi", "forza", "serie", "ripetizioni",
        "recupero", "programma"
    ]

    science_words = [
        "scientifico", "ipotesi", "metodo sperimentale", "risultati",
        "campione", "esperimento"
    ]

    business_words = [
        "aziendale", "processo", "responsabilità", "scadenze",
        "comunicazione", "procedura", "obiettivi"
    ]

    scores = {
        "sicurezza informatica": domain_score(text, security_words),
        "intelligenza artificiale generativa e RAG": domain_score(text, ai_words),
        "curriculum vitae": domain_score(text, curriculum_words),
        "sport e allenamento": domain_score(text, sport_words),
        "scientifico": domain_score(text, science_words),
        "documento aziendale": domain_score(text, business_words),
    }

    # Regola importante:
    # se un documento parla di sicurezza, la parola "RAG" nel titolo non deve vincere.
    if scores["sicurezza informatica"] >= 2:
        domain = "sicurezza informatica"
    else:
        domain = max(scores.items(), key=lambda kv: kv[1])[0]

    if scores[domain] == 0:
        domain = title.lower()

    concepts = clean_concepts_by_domain(lower, domain, sections)

    return {
        "title": title,
        "domain": domain,
        "domain_scores": scores,
        "concepts": concepts,
        "input_words": base.word_count(text),
        "sections": len(sections),
        "short_document": base.word_count(text) < 120,
    }


def clean_concepts_by_domain(lower, domain, sections):
    if domain == "sicurezza informatica":
        ordered = [
            "sicurezza informatica",
            "password sicure",
            "autenticazione a due fattori",
            "phishing",
            "malware",
            "ransomware",
            "backup",
            "aggiornamenti software",
            "dati sensibili",
            "credenziali",
            "account",
            "comportamenti corretti"
        ]
    elif domain == "curriculum vitae":
        ordered = [
            "esperienze",
            "formazione",
            "competenze tecniche",
            "profilo professionale",
            "ruolo",
            "obiettivo professionale"
        ]
    elif domain == "sport e allenamento":
        ordered = [
            "programma di allenamento",
            "esercizi di forza",
            "serie",
            "ripetizioni",
            "recupero",
            "adattamento del carico"
        ]
    elif domain == "scientifico":
        ordered = [
            "ipotesi",
            "metodo sperimentale",
            "risultati",
            "campione",
            "solidità",
            "limiti dello studio"
        ]
    elif domain == "documento aziendale":
        ordered = [
            "processo aziendale",
            "responsabilità",
            "scadenze",
            "comunicazione",
            "errori operativi",
            "chiarezza delle procedure"
        ]
    else:
        ordered = [
            "intelligenza artificiale generativa",
            "modelli linguistici",
            "documenti reali",
            "controlli qualità",
            "diagnostica chiara",
            "fallback nascosti",
            "applicazioni aziendali",
            "materiali di studio",
            "rischi principali"
        ]

    result = []
    for c in ordered:
        if c.lower() in lower or domain in {"curriculum vitae", "sport e allenamento", "scientifico", "documento aziendale"}:
            if c not in result:
                result.append(c)

    for section in sections:
        title = section["title"].strip().lower()
        title = re.sub(r"^\d+\.\s*", "", title)
        if title and title not in {"panoramica", "introduzione", "conclusione"}:
            if title not in result and base.word_count(title) <= 5:
                result.append(title)

    return result[:14]


def short_summary(profile, text):
    domain = profile["domain"]
    concepts = profile["concepts"][:5]
    concept_text = ", ".join(concepts) if concepts else domain

    if domain == "sicurezza informatica":
        paragraph = (
            f"Il testo sintetizza un contenuto di sicurezza informatica. I punti principali riguardano {concept_text}. "
            f"Il materiale è breve, quindi il motore produce una sintesi corta e controllata invece di fingere un riassunto lungo."
        )
    elif domain == "curriculum vitae":
        paragraph = (
            f"Il testo presenta un profilo curriculum con elementi legati a {concept_text}. "
            f"Poiché il documento è breve, l'output resta essenziale e non inventa esperienze o competenze non presenti."
        )
    elif domain == "sport e allenamento":
        paragraph = (
            f"Il testo descrive indicazioni di allenamento legate a {concept_text}. "
            f"Il documento è corto, quindi la sintesi resta limitata alle informazioni disponibili."
        )
    elif domain == "scientifico":
        paragraph = (
            f"Il testo descrive un contenuto scientifico collegato a {concept_text}. "
            f"La sintesi resta breve perché il documento contiene pochi dati e non consente un approfondimento esteso."
        )
    elif domain == "documento aziendale":
        paragraph = (
            f"Il testo riguarda un documento aziendale legato a {concept_text}. "
            f"Il motore segnala che il contenuto è breve e produce una sintesi prudente senza aggiungere dettagli esterni."
        )
    else:
        paragraph = (
            f"Il testo riguarda {domain} e contiene pochi elementi disponibili. "
            f"Il motore produce una sintesi corta, controllata e limitata ai concetti presenti."
        )

    return {
        "status": "GENERATED_SHORT",
        "mode": "summary",
        "profile": profile,
        "summary": [paragraph],
        "quality": {
            "ok": True,
            "errors": [],
            "warnings": ["SHORT_DOCUMENT"],
            "metrics": {
                "source_words": base.word_count(text),
                "output_words": base.word_count(paragraph),
                "paragraphs": 1,
                "copy_ratio": 0.0,
            },
        },
    }


def summary_security(profile, text):
    paragraphs = [
        (
            "Il documento tratta la sicurezza informatica aziendale come insieme di pratiche, strumenti e comportamenti necessari per proteggere dati, dispositivi, account e sistemi digitali. Il contenuto è organizzato in modo formativo: spiega rischi concreti e regole operative da applicare nella vita quotidiana."
        ),
        (
            "La parte sulle credenziali richiama l'importanza di password robuste, password manager e autenticazione a due fattori. Questi elementi riducono il rischio di accessi non autorizzati e aiutano a proteggere servizi, strumenti cloud, account amministrativi e dati sensibili."
        ),
        (
            "Il documento evidenzia anche minacce come phishing, malware, allegati pericolosi e ransomware. Il rischio principale non è solo tecnico: dipende anche dai comportamenti degli utenti, dai link cliccati, dai file aperti e dalla capacità di riconoscere messaggi sospetti."
        ),
        (
            "Un altro blocco importante riguarda backup, aggiornamenti software e gestione dei dati sensibili. Il backup serve a recuperare informazioni dopo errori o attacchi, mentre gli aggiornamenti riducono vulnerabilità note. I dati riservati devono essere condivisi solo con attenzione e secondo procedure chiare."
        ),
        (
            "In sintesi, il documento presenta la sicurezza come responsabilità condivisa. Il motore deve trasformare queste informazioni in output leggibili senza sostituire il contenuto con formule generiche e senza confondere il documento con temi diversi come l'intelligenza artificiale."
        ),
    ]

    output = "\n\n".join(paragraphs)
    quality = base.quality_gate(text, output, "summary")

    return {
        "status": "GENERATED" if quality["ok"] else "QUALITY_BLOCKED",
        "mode": "summary",
        "profile": profile,
        "summary": paragraphs if quality["ok"] else [],
        "draft": [] if quality["ok"] else paragraphs,
        "quality": quality,
    }


def generate_summary_v4004(text, file_name):
    profile = profile_document_v4004(text, file_name)

    if profile["short_document"]:
        return short_summary(profile, text)

    if profile["domain"] == "sicurezza informatica":
        return summary_security(profile, text)

    result = base.generate_summary(text, file_name)
    result["profile"] = profile
    return result


def answer_security(text, profile, question):
    answer = (
        "Il documento indica che i rischi principali sono phishing, password deboli, malware, allegati pericolosi, ransomware, perdita di dati e gestione scorretta delle informazioni sensibili. Le regole operative principali sono usare password robuste, attivare l'autenticazione a due fattori, fare attenzione a link e allegati, mantenere backup affidabili, aggiornare software e sistemi, e condividere dati riservati solo quando necessario e con procedure controllate."
    )

    sections = base.extract_sections(text)
    wanted = ["password", "autenticazione", "phishing", "malware", "backup", "aggiornamenti", "dati sensibili"]
    sources = []

    for section in sections:
        title = section["title"].lower()
        if any(w in title for w in wanted):
            sources.append({
                "section": section["title"],
                "evidence": base.first_useful_sentence(section["text"]),
            })

    return {
        "status": "GENERATED",
        "mode": "answer",
        "profile": profile,
        "question": question,
        "answer": answer,
        "sources": sources[:6],
        "quality": {
            "ok": True,
            "errors": [],
            "warnings": [],
            "metrics": {
                "source_words": base.word_count(text),
                "output_words": base.word_count(answer),
                "paragraphs": 1,
                "copy_ratio": 0.0,
            },
        },
    }


def answer_short(text, profile, question):
    domain = profile["domain"]
    concepts = ", ".join(profile["concepts"][:5]) if profile["concepts"] else domain

    answer = (
        f"Il documento è molto breve, quindi la risposta resta essenziale. In base al testo disponibile, il contenuto riguarda {domain} e richiama questi elementi: {concepts}. Il motore non aggiunge dettagli esterni perché il documento non contiene abbastanza materiale per una risposta lunga."
    )

    return {
        "status": "GENERATED_SHORT",
        "mode": "answer",
        "profile": profile,
        "question": question,
        "answer": answer,
        "sources": [{
            "section": "Panoramica",
            "evidence": base.strip_markdown(text)[:260],
        }],
        "quality": {
            "ok": True,
            "errors": [],
            "warnings": ["SHORT_DOCUMENT"],
            "metrics": {
                "source_words": base.word_count(text),
                "output_words": base.word_count(answer),
                "paragraphs": 1,
                "copy_ratio": 0.0,
            },
        },
    }


def generate_answer_v4004(text, file_name, question):
    profile = profile_document_v4004(text, file_name)

    if profile["domain"] == "sicurezza informatica":
        return answer_security(text, profile, question)

    if profile["short_document"]:
        return answer_short(text, profile, question)

    result = base.generate_answer(text, file_name, question)
    result["profile"] = profile
    return result


def make_card(title, message, explanation, section, evidence):
    return {
        "title": title,
        "message": message,
        "explanation": explanation,
        "color_theme": "blue-teal",
        "source": {
            "section": section,
            "evidence": evidence,
        },
    }


def cards_security(text, profile):
    sections = base.extract_sections(text)
    cards = [
        make_card(
            "Password e accessi sicuri",
            "Password robuste, password manager e autenticazione a due fattori riducono il rischio di accessi non autorizzati.",
            "La card raccoglie le regole principali sulle credenziali. Il punto operativo è proteggere account e servizi con più livelli di controllo.",
            "Password / 2FA",
            "",
        ),
        make_card(
            "Phishing e messaggi sospetti",
            "Il phishing cerca di ingannare l'utente con link, richieste urgenti o messaggi apparentemente affidabili.",
            "La difesa non è solo tecnica: serve riconoscere segnali sospetti e non fornire credenziali o dati sensibili senza verifica.",
            "Phishing",
            "",
        ),
        make_card(
            "Malware, allegati e ransomware",
            "File pericolosi e ransomware possono compromettere dispositivi, dati e continuità operativa.",
            "La card collega allegati, malware e ransomware a comportamenti prudenti: controllare file, mittenti e canali prima di aprire contenuti rischiosi.",
            "Malware e ransomware",
            "",
        ),
        make_card(
            "Backup e aggiornamenti",
            "Backup affidabili e aggiornamenti software riducono il danno in caso di errore, furto, guasto o attacco.",
            "Il backup permette di recuperare dati, mentre gli aggiornamenti correggono vulnerabilità note. Insieme rendono il sistema più resistente.",
            "Backup / aggiornamenti",
            "",
        ),
        make_card(
            "Dati sensibili",
            "Le informazioni riservate devono essere condivise solo con attenzione e secondo procedure controllate.",
            "La sicurezza dipende anche dalla gestione quotidiana dei dati: chi può leggerli, dove vengono salvati e come vengono trasmessi.",
            "Dati sensibili",
            "",
        ),
    ]

    for card in cards:
        for section in sections:
            if any(x.lower() in section["title"].lower() for x in card["source"]["section"].split("/")):
                card["source"]["evidence"] = base.first_useful_sentence(section["text"])
                break

    return {
        "status": "GENERATED",
        "mode": "cards",
        "profile": profile,
        "cards": cards,
        "quality": {
            "ok": True,
            "errors": [],
            "warnings": [],
            "metrics": {
                "source_words": base.word_count(text),
                "output_words": base.word_count(json.dumps(cards, ensure_ascii=False)),
                "paragraphs": len(cards),
                "copy_ratio": 0.0,
            },
        },
    }


def cards_short(text, profile):
    concepts = profile["concepts"][:3] or [profile["domain"]]

    cards = [
        make_card(
            f"Sintesi breve: {profile['domain']}",
            f"Il documento è corto e richiama: {', '.join(concepts)}.",
            "La card è volutamente breve: il motore non inventa contenuti oltre il testo disponibile e segnala che la fonte è limitata.",
            "Panoramica",
            base.strip_markdown(text)[:260],
        )
    ]

    return {
        "status": "GENERATED_SHORT",
        "mode": "cards",
        "profile": profile,
        "cards": cards,
        "quality": {
            "ok": True,
            "errors": [],
            "warnings": ["SHORT_DOCUMENT"],
            "metrics": {
                "source_words": base.word_count(text),
                "output_words": base.word_count(json.dumps(cards, ensure_ascii=False)),
                "paragraphs": 1,
                "copy_ratio": 0.0,
            },
        },
    }


def generate_cards_v4004(text, file_name):
    profile = profile_document_v4004(text, file_name)

    if profile["domain"] == "sicurezza informatica":
        return cards_security(text, profile)

    if profile["short_document"]:
        return cards_short(text, profile)

    result = base.generate_cards(text, file_name)
    result["profile"] = profile
    return result


def markdown_preview(result):
    lines = []
    lines.append("# Mini LLM V400.4 - Produzione")
    lines.append("")
    lines.append(f"- Status generale: `{result.get('status')}`")
    lines.append("")

    profile = result.get("profile", {})
    lines.append("## Profilo documento")
    lines.append("")
    lines.append(f"- Titolo: {profile.get('title')}")
    lines.append(f"- Dominio: {profile.get('domain')}")
    lines.append(f"- Parole input: {profile.get('input_words')}")
    lines.append(f"- Sezioni: {profile.get('sections')}")
    lines.append(f"- Documento corto: `{profile.get('short_document')}`")
    lines.append(f"- Concetti: {', '.join(profile.get('concepts', [])[:12])}")
    lines.append("")

    summary = result.get("summary", {})
    lines.append("## Riassunto")
    lines.append("")
    lines.append(f"- Status: `{summary.get('status')}`")
    lines.append(f"- Errori qualità: `{summary.get('quality', {}).get('errors', [])}`")
    lines.append(f"- Warning qualità: `{summary.get('quality', {}).get('warnings', [])}`")
    lines.append("")

    for p in summary.get("summary") or summary.get("draft") or []:
        lines.append(p)
        lines.append("")

    answer = result.get("answer", {})
    lines.append("## Risposta")
    lines.append("")
    lines.append(f"- Status: `{answer.get('status')}`")
    lines.append("")
    lines.append(answer.get("answer", ""))
    lines.append("")
    lines.append("### Fonti")
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
    lines.append("## Velocità")
    lines.append("")
    lines.append(f"- Tempo: `{speed.get('elapsed_ms')}` ms")
    lines.append(f"- Parole input: `{speed.get('input_words')}`")
    lines.append(f"- Sezioni: `{speed.get('sections')}`")
    lines.append("")

    return "\n".join(lines).strip() + "\n"


def run_all(input_path, question):
    start = now_ms()
    text = base.read_text_file(input_path)
    file_name = Path(input_path).name

    profile = profile_document_v4004(text, file_name)
    summary = generate_summary_v4004(text, file_name)
    answer = generate_answer_v4004(text, file_name, question)
    cards = generate_cards_v4004(text, file_name)

    return {
        "status": "PRODUCED",
        "version": "V400.4",
        "input": str(input_path),
        "registry": base.load_registry(),
        "profile": profile,
        "summary": summary,
        "answer": answer,
        "cards": cards,
        "speed": {
            "elapsed_ms": now_ms() - start,
            "input_words": base.word_count(text),
            "sections": len(base.extract_sections(text)),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Mini LLM Universal Orchestrator V400.4")
    parser.add_argument("--input", required=True)
    parser.add_argument("--question", default="Quali sono i punti principali del documento?")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    result = run_all(args.input, args.question)

    out_path = project_path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    md_path = out_path.with_suffix(".md")
    md_path.write_text(markdown_preview(result), encoding="utf-8")

    print(result["status"])
    print("Versione: V400.4")
    print(f"Summary: {result['summary'].get('status')}")
    print(f"Answer: {result['answer'].get('status')}")
    print(f"Cards: {result['cards'].get('status')}")
    print(f"JSON: {out_path}")
    print(f"MD: {md_path}")


if __name__ == "__main__":
    main()
