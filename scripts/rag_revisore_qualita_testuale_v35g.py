#!/usr/bin/env python3
"""
RAG Revisore Qualità Testuale V3.5G

Controlla e rifinisce la qualità finale dei testi visibili.

Obiettivi:
- grammatica italiana
- accenti e apostrofi comuni
- domande studio naturali
- spiegazioni test utili
- fonti visibili belle
- categorie e sottocategorie
- assenza frasi riempitive
- separazione test interni / test visibili

Non modifica:
- opzioni interne
- risposta_corretta interna
- mappa tecnica usata dal bridge quiz
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


BAD_FILLERS = [
    "Documento analizzato.",
    "Questo punto aiuta a riconoscere una informazione centrale",
    "Questo punto aiuta a riconoscere un'informazione centrale",
    "contenuti generati",
    "knowledge_base_json",
]

BAD_PREFIXES_VISIBLE = [
    "Concetto:",
    "Aspetto:",
    "Focus:",
    "Punto del documento:",
    "Informazione:",
]


ACCENT_REPLACEMENTS = [
    (r"\bperche\b", "perché"),
    (r"\bpoiche\b", "poiché"),
    (r"\baffinche\b", "affinché"),
    (r"\bfinche\b", "finché"),
    (r"\bpuo\b", "può"),
    (r"\bpiu\b", "più"),
    (r"\bgia\b", "già"),
    (r"\bcioe\b", "cioè"),
    (r"\bcosi\b", "così"),
    (r"\bpero\b", "però"),
    (r"\bsara\b", "sarà"),
    (r"\bavra\b", "avrà"),
    (r"\bdovra\b", "dovrà"),
    (r"\bverra\b", "verrà"),
    (r"\bqual e\b", "qual è"),
    (r"\bE'\b", "È"),
    (r"\be'\b", "è"),
    (r"\buna informazione\b", "un'informazione"),
    (r"\buna esperienza\b", "un'esperienza"),
    (r"\buna azione\b", "un'azione"),
    (r"\buna idea\b", "un'idea"),
    (r"\bun altra\b", "un'altra"),
    (r"\bun applicazione\b", "un'applicazione"),
]


def normalizza_spazi(value: str) -> str:
    text = str(value or "")
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([,.;:!?])([^\s»”\")])", r"\1 \2", text)
    text = text.replace("..", ".")
    return text.strip()


def frase(value: str) -> str:
    text = normalizza_spazi(value)
    if text and text[-1] not in ".!?":
        text += "."
    return text


def domanda(value: str) -> str:
    text = normalizza_spazi(value)
    if text and text[-1] != "?":
        text = text.rstrip(".!") + "?"
    return text


def correggi_italiano(value: str) -> str:
    text = normalizza_spazi(value)

    for pattern, replacement in ACCENT_REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    text = text.replace("l utente", "l'utente")
    text = text.replace("d accordo", "d'accordo")
    text = text.replace("po ", "po' ")
    text = text.replace("un po ", "un po' ")

    return normalizza_spazi(text)


def pulisci_visibile(value: str) -> str:
    text = correggi_italiano(value)

    for filler in BAD_FILLERS:
        text = text.replace(filler, "")

    text = normalizza_spazi(text)
    return text


def titolo_da_domanda(value: str, fallback: str = "contenuto") -> str:
    match = re.search(r"«([^»]+)»", value or "")
    if match:
        return normalizza_spazi(match.group(1))
    return fallback


def ensure_fonte(title: str | None = None) -> str:
    title = normalizza_spazi(title or "")
    if title:
        return f"Fonte: sezione “{title}”."
    return "Fonte: sezione del documento."


def categoria(sub: str, tipo: str) -> dict[str, str]:
    mapping = {
        "riassunto": "Comprensione generale",
        "card": "Memorizzazione visuale",
        "domande_studio": "Ripasso guidato",
        "test": "Verifica interattiva",
        "layout": "Presentazione grafica",
    }

    return {
        "categoria": mapping.get(tipo, "Materiale didattico"),
        "sottocategoria": normalizza_spazi(sub or tipo),
    }


def refine_summary(data: dict[str, Any]) -> dict[str, Any]:
    if "riassunto" not in data:
        return data

    r = dict(data.get("riassunto") or {})

    r["titolo"] = frase(pulisci_visibile(r.get("titolo", "Riassunto"))).rstrip(".")
    r["testo_breve"] = frase(pulisci_visibile(r.get("testo_breve", "")))
    r["conclusione"] = frase(pulisci_visibile(r.get("conclusione", "")))

    punti = []
    for p in r.get("punti_chiave", []) or []:
        item = dict(p)
        title = pulisci_visibile(item.get("titolo", "Punto chiave")).rstrip(".")
        item["titolo"] = title
        item["testo"] = frase(pulisci_visibile(item.get("testo", "")))
        item["fonte_visibile"] = ensure_fonte(title)
        item["categoria_v35g"] = categoria(title, "riassunto")
        punti.append(item)

    r["punti_chiave"] = punti
    r["categoria_v35g"] = categoria("sintesi del documento", "riassunto")

    data["riassunto"] = r
    return data


def refine_cards(data: dict[str, Any]) -> dict[str, Any]:
    cards = []

    for idx, card in enumerate(data.get("card", []) or [], start=1):
        c = dict(card)
        title = pulisci_visibile(c.get("titolo", f"Card {idx}")).rstrip(".")

        c["titolo"] = title
        c["testo"] = frase(pulisci_visibile(c.get("testo", "")))
        c["messaggio_chiave"] = frase(pulisci_visibile(c.get("messaggio_chiave", "")))
        c["fonte_visibile"] = ensure_fonte(title)
        c["categoria_v35g"] = categoria(title, "card")

        cards.append(c)

    if cards:
        data["card"] = cards

    return data


def refine_study(data: dict[str, Any]) -> dict[str, Any]:
    items = []

    for idx, item in enumerate(data.get("domande_studio", []) or [], start=1):
        s = dict(item)

        q = domanda(pulisci_visibile(s.get("domanda", "")))
        title = titolo_da_domanda(q, f"Punto {idx}")

        answer = frase(pulisci_visibile(s.get("risposta_guida", "")))

        if len(answer) < 45:
            answer = frase(
                f"Devi ricordare il significato di «{title}» e collegarlo al punto principale spiegato nel documento."
            )

        s["domanda"] = q
        s["risposta_guida"] = answer
        s["fonte_visibile"] = ensure_fonte(title)
        s["categoria_v35g"] = categoria(title, "domande_studio")

        items.append(s)

    if items:
        data["domande_studio"] = items

    return data


def build_explanation(question: str, correct: str) -> str:
    title = titolo_da_domanda(question, "questo punto")
    correct_clean = correct.rstrip(".")
    return frase(
        f"La risposta corretta è «{correct_clean}» perché descrive in modo diretto il contenuto richiesto su «{title}»."
    )


def refine_tests(data: dict[str, Any]) -> dict[str, Any]:
    tests = []

    for idx, item in enumerate(data.get("test", []) or [], start=1):
        t = dict(item)

        question = domanda(pulisci_visibile(t.get("domanda_visibile") or t.get("domanda", "")))
        visible_options = [
            frase(pulisci_visibile(opt))
            for opt in (t.get("opzioni_visibili") or t.get("opzioni") or [])
        ]

        visible_correct = pulisci_visibile(
            t.get("risposta_corretta_visibile") or t.get("risposta_corretta", "")
        )

        if visible_correct:
            visible_correct = frase(visible_correct)

        if visible_correct not in visible_options:
            # prova ad allineare la corretta dalla mappa tecnica, senza cambiare campi interni
            for row in t.get("mappa_opzioni_v35d", []) or []:
                if row.get("corretta"):
                    mapped = frase(pulisci_visibile(row.get("opzione_visibile", "")))
                    if mapped in visible_options:
                        visible_correct = mapped
                    break

        explanation = frase(pulisci_visibile(t.get("spiegazione", "")))

        if len(explanation) < 45:
            explanation = build_explanation(question, visible_correct or "risposta corretta")

        title = titolo_da_domanda(question, f"Domanda {idx}")

        t["domanda_visibile"] = question
        t["opzioni_visibili"] = visible_options
        t["risposta_corretta_visibile"] = visible_correct
        t["spiegazione"] = explanation
        t["fonte_visibile"] = ensure_fonte(title)
        t["categoria_v35g"] = categoria(title, "test")

        # Non tocchiamo:
        # - opzioni interne
        # - risposta_corretta interna
        # - mappa_opzioni_v35d
        tests.append(t)

    if tests:
        data["test"] = tests

    return data


def add_categories(data: dict[str, Any]) -> dict[str, Any]:
    cats = []

    if "riassunto" in data:
        cats.append(categoria("sintesi", "riassunto"))

    if "card" in data:
        cats.append(categoria("schede visuali", "card"))

    if "domande_studio" in data:
        cats.append(categoria("ripasso guidato", "domande_studio"))

    if "test" in data:
        cats.append(categoria("risposte multiple", "test"))

    if "ui_layout" in data:
        cats.append(categoria("layout output", "layout"))

    data["categorie_didattiche_v35g"] = cats
    return data


def collect_visible_texts(data: dict[str, Any]) -> list[str]:
    texts = []

    r = data.get("riassunto")
    if isinstance(r, dict):
        texts.extend([r.get("titolo", ""), r.get("testo_breve", ""), r.get("conclusione", "")])
        for p in r.get("punti_chiave", []) or []:
            texts.extend([p.get("titolo", ""), p.get("testo", ""), p.get("fonte_visibile", "")])

    for c in data.get("card", []) or []:
        texts.extend([c.get("titolo", ""), c.get("testo", ""), c.get("messaggio_chiave", ""), c.get("fonte_visibile", "")])

    for s in data.get("domande_studio", []) or []:
        texts.extend([s.get("domanda", ""), s.get("risposta_guida", ""), s.get("fonte_visibile", "")])

    for t in data.get("test", []) or []:
        texts.extend([
            t.get("domanda_visibile", ""),
            t.get("risposta_corretta_visibile", ""),
            t.get("spiegazione", ""),
            t.get("fonte_visibile", ""),
        ])
        texts.extend(t.get("opzioni_visibili", []) or [])

    return [normalizza_spazi(t) for t in texts if normalizza_spazi(t)]


def validate_quality(data: dict[str, Any]) -> dict[str, Any]:
    errors = []
    warnings = []

    texts = collect_visible_texts(data)
    joined = "\n".join(texts)

    bad_tokens = [
        " e'",
        "E'",
        "perche",
        "puo",
        "piu",
        "gia",
        "cioe",
        "cosi",
        "pero",
        "qual e",
        "una informazione",
    ]

    for token in bad_tokens:
        if re.search(rf"\b{re.escape(token.strip())}\b", joined, flags=re.IGNORECASE):
            errors.append(f"accento/apostrofo sospetto ancora visibile: {token.strip()}")

    for filler in BAD_FILLERS:
        if filler in joined:
            errors.append(f"frase riempitiva ancora visibile: {filler}")

    for prefix in BAD_PREFIXES_VISIBLE:
        for text in texts:
            if text.startswith(prefix):
                errors.append(f"prefisso brutto visibile: {prefix}")

    for text in texts:
        if re.search(r"\s+[,.!?;:]", text):
            errors.append("spazio errato prima della punteggiatura")
            break
        if "  " in text:
            errors.append("doppio spazio visibile")
            break

    if "categorie_didattiche_v35g" not in data:
        errors.append("categorie didattiche V3.5G mancanti")

    for idx, card in enumerate(data.get("card", []) or [], start=1):
        if len(card.get("testo", "")) < 35:
            errors.append(f"card {idx}: testo troppo corto")
        if not card.get("fonte_visibile", "").startswith("Fonte: sezione"):
            errors.append(f"card {idx}: fonte visibile debole")
        if "categoria_v35g" not in card:
            errors.append(f"card {idx}: categoria mancante")

    for idx, item in enumerate(data.get("domande_studio", []) or [], start=1):
        if not item.get("domanda", "").endswith("?"):
            errors.append(f"domanda studio {idx}: non finisce con punto interrogativo")
        if len(item.get("risposta_guida", "")) < 45:
            errors.append(f"domanda studio {idx}: risposta guida troppo corta")
        if "categoria_v35g" not in item:
            errors.append(f"domanda studio {idx}: categoria mancante")

    for idx, item in enumerate(data.get("test", []) or [], start=1):
        options = item.get("opzioni_visibili", []) or []
        correct = item.get("risposta_corretta_visibile", "")

        if not item.get("domanda_visibile", "").endswith("?"):
            errors.append(f"test {idx}: domanda visibile non interrogativa")

        if len(options) != 4:
            errors.append(f"test {idx}: opzioni visibili diverse da 4")

        if correct not in options:
            errors.append(f"test {idx}: risposta corretta visibile assente dalle opzioni")

        if len(item.get("spiegazione", "")) < 45:
            errors.append(f"test {idx}: spiegazione troppo debole")

        if "categoria_v35g" not in item:
            errors.append(f"test {idx}: categoria mancante")

    return {
        "ok": not errors,
        "errori": errors,
        "avvisi": warnings,
        "testi_controllati": len(texts),
        "categorie": len(data.get("categorie_didattiche_v35g", []) or []),
    }


def refine_output(data: dict[str, Any]) -> dict[str, Any]:
    refined = dict(data)

    refined = refine_summary(refined)
    refined = refine_cards(refined)
    refined = refine_study(refined)
    refined = refine_tests(refined)
    refined = add_categories(refined)

    quality = validate_quality(refined)

    controls = dict(refined.get("controlli_qualita", {}))
    controls["qualita_testuale_v35g"] = quality
    controls["ok"] = bool(controls.get("ok", True)) and quality["ok"]

    refined["controlli_qualita"] = controls

    motors = dict(refined.get("motori_riutilizzabili", {}))
    motors["revisore_qualita_testuale"] = "rag_revisore_qualita_testuale_v35g"
    refined["motori_riutilizzabili"] = motors

    refined["revisione_qualita_testuale_v35g"] = {
        "ok": quality["ok"],
        "copre": [
            "grammatica_italiana",
            "accenti",
            "apostrofi",
            "domande_naturali",
            "spiegazioni_test",
            "fonti_visibili",
            "categorie",
            "sottocategorie",
            "assenza_frasi_riempitive",
        ],
    }

    return refined


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

    q = refined["controlli_qualita"]["qualita_testuale_v35g"]

    print("=== RAG REVISORE QUALITÀ TESTUALE V3.5G ===")
    print("Input:", input_path)
    print("Output:", output_path)
    print("Qualità OK:", q["ok"])
    print("Testi controllati:", q["testi_controllati"])
    print("Categorie:", q["categorie"])

    if q["errori"]:
        print("ERRORI:")
        for e in q["errori"]:
            print("-", e)

    if q["avvisi"]:
        print("AVVISI:")
        for a in q["avvisi"]:
            print("-", a)

    return 0 if q["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
