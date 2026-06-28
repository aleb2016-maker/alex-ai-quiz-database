#!/usr/bin/env python3
"""
RAG Motore Didattico Riutilizzabile V3.5C

Questo modulo NON sostituisce i motori quiz.
Lavora dopo la generazione RAG e prima della UI/PDF/app.

Scopo:
- naturalezza domande studio
- stile card
- fonti visibili umane
- rimozione frasi riempitive
- tono didattico finale
- layout grafico riutilizzabile
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


FILLER_PHRASES = [
    "Questo punto aiuta a riconoscere una informazione centrale del documento e a collegarla agli altri contenuti generati.",
    "Questo punto aiuta a riconoscere un'informazione centrale del documento e a collegarla agli altri contenuti generati.",
    "Documento analizzato.",
    "Fonte: knowledge_base_json.",
    "Fonte: knowledge base json.",
]

BAD_VISIBLE_PREFIXES = [
    "Concetto:",
    "Aspetto:",
    "Focus:",
    "Punto del documento:",
    "Informazione:",
    "Riepilogo:",
]


CARD_ICONS = ["🛡️", "⚠️", "✅", "🔧", "🎯", "📌", "🧠", "📚"]


def normalizza_spazi(value: str) -> str:
    text = " ".join(str(value or "").split()).strip()
    text = text.replace(" .", ".")
    text = text.replace(" ,", ",")
    text = text.replace(" ;", ";")
    text = text.replace(" :", ":")
    text = text.replace("..", ".")
    return text


def frase(value: str) -> str:
    text = normalizza_spazi(value)
    if text and text[-1] not in ".!?":
        text += "."
    return text


def remove_fillers(value: str) -> str:
    text = str(value or "")

    for filler in FILLER_PHRASES:
        text = text.replace(filler, "")

    text = text.replace("  ", " ")
    return frase(text.strip()) if text.strip() else ""


def remove_option_prefix(value: str) -> str:
    text = normalizza_spazi(value)

    for prefix in BAD_VISIBLE_PREFIXES:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()

    return frase(text)


def short_source(title: str = "") -> str:
    title = normalizza_spazi(title)
    if title:
        return f"Fonte: sezione “{title}”."
    return "Fonte: sezione del documento."


def build_card_style(index: int, title: str) -> dict[str, Any]:
    return {
        "layout": "card-studio-bilanciata",
        "icona": CARD_ICONS[(index - 1) % len(CARD_ICONS)],
        "densita": "media",
        "titolo_breve": title,
        "mostra_fonte": True,
        "mostra_punto_chiave": True,
    }


def refine_summary(summary: dict[str, Any]) -> dict[str, Any]:
    new = dict(summary)

    new["titolo"] = normalizza_spazi(new.get("titolo", "Riassunto"))
    new["testo_breve"] = remove_fillers(new.get("testo_breve", ""))
    new["conclusione"] = remove_fillers(
        new.get("conclusione")
        or "Il documento viene trasformato in materiale ordinato per capire, ripassare e verificare i punti principali."
    )

    punti = []
    for point in new.get("punti_chiave", []) or []:
        p = dict(point)
        p["titolo"] = normalizza_spazi(p.get("titolo", "Punto chiave"))
        p["testo"] = remove_fillers(p.get("testo", ""))
        p["fonte_visibile"] = short_source(p["titolo"])
        punti.append(p)

    new["punti_chiave"] = punti
    return new


def refine_cards(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    refined = []

    for index, card in enumerate(cards, start=1):
        c = dict(card)

        title = normalizza_spazi(c.get("titolo", f"Card {index}"))
        text = remove_fillers(c.get("testo", ""))
        key = remove_fillers(c.get("messaggio_chiave", ""))

        if key.lower().startswith("punto chiave:"):
            key = "Punto chiave: " + normalizza_spazi(key.split(":", 1)[1])

        c["titolo"] = title
        c["testo"] = text
        c["messaggio_chiave"] = key
        c["fonte_visibile"] = short_source(title)
        c["stile_card"] = build_card_style(index, title)

        refined.append(c)

    return refined




def refine_tests(tests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Mantiene intatti i campi tecnici validati dal bridge quiz:
    - opzioni
    - risposta_corretta

    Aggiunge campi puliti per UI/PDF/app:
    - opzioni_visibili
    - risposta_corretta_visibile

    Così i motori quiz continuano a controllare il test,
    ma l'utente vede opzioni senza prefissi brutti.
    """
    refined = []

    for item in tests:
        t = dict(item)

        raw_options = list(t.get("opzioni", []) or [])
        raw_correct = t.get("risposta_corretta", "")

        visible_options = [remove_option_prefix(opt) for opt in raw_options]

        visible_correct = ""
        for raw, visible in zip(raw_options, visible_options):
            if raw == raw_correct:
                visible_correct = visible
                break

        if not visible_correct and visible_options:
            visible_correct = visible_options[0]

        # Campi interni: NON toccati, servono ai motori quiz.
        t["opzioni"] = raw_options
        t["risposta_corretta"] = raw_correct

        # Campi visibili: usati da pagina/PDF/app.
        t["opzioni_visibili"] = visible_options
        t["risposta_corretta_visibile"] = visible_correct

        t["spiegazione"] = remove_fillers(t.get("spiegazione", ""))
        t["fonte_visibile"] = short_source("test")

        refined.append(t)

    return refined

def study_question_template(index: int, title: str) -> str:
    templates = [
        "Che cosa devi ricordare su «{title}»?",
        "Perché «{title}» è importante nel documento?",
        "Come spiegheresti «{title}» con parole semplici?",
        "Quale collegamento puoi fare partendo da «{title}»?",
        "Qual è l’idea essenziale di «{title}»?",
    ]

    return templates[(index - 1) % len(templates)].format(title=title)


def refine_study_questions(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    refined = []

    for index, item in enumerate(items, start=1):
        s = dict(item)

        raw_question = normalizza_spazi(s.get("domanda", ""))
        title_match = re.search(r"«([^»]+)»", raw_question)
        title = title_match.group(1) if title_match else f"Punto {index}"

        answer = remove_fillers(s.get("risposta_guida", ""))

        if not answer or len(answer) < 30:
            answer = f"Devi ricordare il significato di «{title}» e collegarlo al contenuto principale del documento."

        s["domanda"] = study_question_template(index, title)
        s["risposta_guida"] = answer
        s["fonte_visibile"] = short_source(title)

        refined.append(s)

    return refined


def build_ui_layout(output: dict[str, Any]) -> dict[str, Any]:
    card_count = len(output.get("card", []) or [])
    test_count = len(output.get("test", []) or [])
    study_count = len(output.get("domande_studio", []) or [])

    return {
        "versione": "rag-layout-didattico-v35c",
        "pagina": {
            "max_width": 1180,
            "tema": "studio-professionale",
            "densita": "leggibile",
        },
        "card": {
            "layout": "griglia-responsive",
            "min_width": 260,
            "max_per_row": 3 if card_count >= 5 else 4,
            "equal_height": False,
            "evita_testo_compresso": True,
        },
        "test": {
            "layout": "lista-interattiva",
            "opzioni": "bottoni-larghi",
            "feedback": "immediato",
            "numero_domande": test_count,
        },
        "domande_studio": {
            "layout": "schede-lunghe",
            "tono": "ripasso-guidato",
            "numero_domande": study_count,
        },
    }


def visible_texts(output: dict[str, Any]) -> list[str]:
    texts = []

    r = output.get("riassunto", {})
    texts.extend([r.get("titolo", ""), r.get("testo_breve", ""), r.get("conclusione", "")])

    for p in r.get("punti_chiave", []) or []:
        texts.extend([p.get("titolo", ""), p.get("testo", ""), p.get("fonte_visibile", "")])

    for c in output.get("card", []) or []:
        texts.extend([c.get("titolo", ""), c.get("testo", ""), c.get("messaggio_chiave", ""), c.get("fonte_visibile", "")])

    for t in output.get("test", []) or []:
        texts.append(t.get("domanda_visibile") or t.get("domanda", ""))
        texts.extend(t.get("opzioni_visibili") or t.get("opzioni", []) or [])
        texts.extend([
            t.get("risposta_corretta_visibile") or t.get("risposta_corretta", ""),
            t.get("spiegazione", ""),
            t.get("fonte_visibile", ""),
        ])

    for s in output.get("domande_studio", []) or []:
        texts.extend([s.get("domanda", ""), s.get("risposta_guida", ""), s.get("fonte_visibile", "")])

    return [normalizza_spazi(t) for t in texts if normalizza_spazi(t)]


def validate_didactic_output(output: dict[str, Any]) -> dict[str, Any]:
    errors = []
    warnings = []

    texts = visible_texts(output)
    joined = "\n".join(texts)

    for filler in FILLER_PHRASES:
        if filler in joined:
            errors.append(f"frase riempitiva ancora visibile: {filler}")

    for prefix in BAD_VISIBLE_PREFIXES:
        if prefix in joined:
            errors.append(f"prefisso didattico brutto ancora visibile: {prefix}")

    if "ui_layout" not in output:
        errors.append("layout grafico riutilizzabile mancante")

    for idx, item in enumerate(output.get("domande_studio", []) or [], start=1):
        domanda = item.get("domanda", "")
        risposta = item.get("risposta_guida", "")

        if len(domanda) < 20:
            errors.append(f"domanda studio {idx}: domanda troppo corta")

        if len(risposta) < 30:
            errors.append(f"domanda studio {idx}: risposta guida troppo debole")

        if "Questo punto aiuta" in risposta:
            errors.append(f"domanda studio {idx}: risposta contiene frase riempitiva")

    for idx, card in enumerate(output.get("card", []) or [], start=1):
        if "stile_card" not in card:
            errors.append(f"card {idx}: stile_card mancante")

        if "Documento analizzato" in card.get("fonte_visibile", ""):
            errors.append(f"card {idx}: fonte povera")

    return {
        "ok": not errors,
        "errori": errors,
        "avvisi": warnings,
        "testi_visibili": len(texts),
    }


def refine_output(output: dict[str, Any]) -> dict[str, Any]:
    new = dict(output)

    new["riassunto"] = refine_summary(new.get("riassunto", {}))
    new["card"] = refine_cards(new.get("card", []) or [])
    new["test"] = refine_tests(new.get("test", []) or [])
    new["domande_studio"] = refine_study_questions(new.get("domande_studio", []) or [])
    new["ui_layout"] = build_ui_layout(new)

    didactic_quality = validate_didactic_output(new)

    quality = dict(new.get("controlli_qualita", {}))
    quality["motore_didattico_v35c"] = didactic_quality
    quality["ok"] = bool(quality.get("ok", True)) and didactic_quality["ok"]

    new["controlli_qualita"] = quality
    new["motori_riutilizzabili"] = {
        "didattico": "rag_motore_didattico_riutilizzabile_v35c",
        "copre": [
            "naturalezza_domande_studio",
            "stile_card",
            "fonti_visibili",
            "rimozione_frasi_riempitive",
            "tono_didattico_finale",
            "layout_grafico",
        ],
    }

    return new


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    data = json.loads(input_path.read_text(encoding="utf-8"))
    refined = refine_output(data)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(refined, ensure_ascii=False, indent=2), encoding="utf-8")

    q = refined["controlli_qualita"]["motore_didattico_v35c"]

    print("=== RAG MOTORE DIDATTICO RIUTILIZZABILE V3.5C ===")
    print("Input:", input_path)
    print("Output:", output_path)
    print("Qualità didattica OK:", q["ok"])
    print("Testi visibili:", q["testi_visibili"])

    if q["errori"]:
        print("ERRORI:")
        for e in q["errori"]:
            print("-", e)

    return 0 if q["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
