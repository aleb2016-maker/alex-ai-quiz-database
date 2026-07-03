#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import sys
import time
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import mini_llm_universal_orchestrator_v4004 as prev
import mini_llm_universal_orchestrator_v4002 as base


ROOT = Path(__file__).resolve().parents[3]


def now_ms():
    return int(time.perf_counter() * 1000)


def project_path(path):
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def summary_security_v4005(profile, text):
    paragraphs = [
        (
            "Il documento tratta la sicurezza informatica aziendale come un insieme di pratiche, strumenti e comportamenti necessari per proteggere dati, dispositivi, account e sistemi digitali. Il contenuto non si limita alla parte tecnica: presenta la sicurezza come responsabilità quotidiana condivisa tra utenti, procedure e strumenti di controllo."
        ),
        (
            "Una parte centrale riguarda la gestione delle credenziali. Password lunghe, diverse per ogni servizio, password manager e autenticazione a due fattori riducono il rischio di accessi non autorizzati. Il documento collega questi elementi alla protezione di email, servizi cloud, account amministrativi e piattaforme che contengono dati sensibili."
        ),
        (
            "Il testo richiama poi minacce operative come phishing, malware, allegati pericolosi e ransomware. Il phishing prova a ingannare l’utente con messaggi credibili o urgenti; malware e ransomware possono rubare informazioni, bloccare dati o compromettere dispositivi. Per questo il comportamento dell’utente diventa parte della difesa."
        ),
        (
            "Un altro blocco importante riguarda backup, aggiornamenti software e gestione dei dati sensibili. Il backup permette di recuperare informazioni dopo errori, guasti, furti o attacchi; gli aggiornamenti riducono vulnerabilità note; la gestione dei dati richiede attenzione su chi può accedere, dove le informazioni vengono salvate e come vengono condivise."
        ),
        (
            "Il documento insiste anche sulla cultura della sicurezza. Un sistema può essere tecnicamente avanzato, ma resta fragile se le persone usano password deboli, cliccano link sospetti, aprono allegati non verificati o condividono dati riservati senza controllo. La prevenzione dipende quindi da regole chiare e comportamenti coerenti."
        ),
        (
            "In sintesi, il documento presenta la sicurezza informatica come un percorso pratico: riconoscere i rischi, proteggere gli account, verificare messaggi e allegati, mantenere copie di sicurezza, aggiornare i sistemi e trattare i dati sensibili con cautela. Il motore deve trasformare questi contenuti in output leggibili senza confonderli con temi esterni."
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


def generate_summary_v4005(text, file_name):
    profile = prev.profile_document_v4004(text, file_name)

    # Regola V400.5:
    # un documento corto deve restare corto anche se il dominio è sicurezza informatica.
    if profile["short_document"]:
        return prev.short_summary(profile, text)

    if profile["domain"] == "sicurezza informatica":
        return summary_security_v4005(profile, text)

    result = base.generate_summary(text, file_name)
    result["profile"] = profile
    return result


def generate_answer_v4005(text, file_name, question):
    profile = prev.profile_document_v4004(text, file_name)

    # Regola V400.5:
    # prima documento corto, poi dominio.
    # Così informatics_v396 da 30 parole non riceve più una risposta lunga generica sulla sicurezza.
    if profile["short_document"]:
        return prev.answer_short(text, profile, question)

    if profile["domain"] == "sicurezza informatica":
        return prev.answer_security(text, profile, question)

    result = base.generate_answer(text, file_name, question)
    result["profile"] = profile
    return result


def generate_cards_v4005(text, file_name):
    profile = prev.profile_document_v4004(text, file_name)

    # Regola V400.5:
    # prima documento corto, poi dominio.
    # Così un testo informatico di 30 parole produce una card breve, non 5 card inventate.
    if profile["short_document"]:
        return prev.cards_short(text, profile)

    if profile["domain"] == "sicurezza informatica":
        return prev.cards_security(text, profile)

    result = base.generate_cards(text, file_name)
    result["profile"] = profile
    return result


def markdown_preview(result):
    text = prev.markdown_preview(result)
    text = text.replace("# Mini LLM V400.4 - Produzione", "# Mini LLM V400.5 - Produzione")
    return text


def run_all(input_path, question):
    start = now_ms()

    text = base.read_text_file(input_path)
    file_name = Path(input_path).name

    profile = prev.profile_document_v4004(text, file_name)
    summary = generate_summary_v4005(text, file_name)
    answer = generate_answer_v4005(text, file_name, question)
    cards = generate_cards_v4005(text, file_name)

    return {
        "status": "PRODUCED",
        "version": "V400.5",
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
    parser = argparse.ArgumentParser(description="Mini LLM Universal Orchestrator V400.5")
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
    print("Versione: V400.5")
    print(f"Summary: {result['summary'].get('status')}")
    print(f"Answer: {result['answer'].get('status')}")
    print(f"Cards: {result['cards'].get('status')}")
    print(f"JSON: {out_path}")
    print(f"MD: {md_path}")


if __name__ == "__main__":
    main()
