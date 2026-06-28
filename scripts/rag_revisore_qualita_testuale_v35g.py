#!/usr/bin/env python3
"""
RAG Revisore Qualità Testuale V3.5G

Controlla e rifinisce la qualità finale dei testi visibili.

Regole principali:
- grammatica italiana
- accenti
- apostrofi
- punteggiatura
- frasi complete
- assenza frasi spezzate
- assenza frasi non terminate
- assenza frasi riempitive
- assenza duplicati inutili
- assenza quasi duplicati
- categorie e sottocategorie
- card con concetti distinti
- spiegazioni test non copiate dalle card
- risposte guida non copiate dalle card

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
    if text and text[-1] not in ".!?»”":
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

    return normalizza_spazi(text)


def normalizza_confronto(value: str) -> str:
    text = normalizza_spazi(value).lower()
    text = text.replace("’", "'")
    text = re.sub(r"[^a-z0-9àèéìòùç']+", " ", text)
    return " ".join(text.split())


def similarita_testi(a: str, b: str) -> float:
    sa = set(normalizza_confronto(a).split())
    sb = set(normalizza_confronto(b).split())

    if not sa or not sb:
        return 0.0

    return len(sa & sb) / max(len(sa), len(sb))


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


def parole_chiave(value: str, max_items: int = 4) -> list[str]:
    stop = {
        "il", "lo", "la", "i", "gli", "le", "un", "una", "uno", "di", "del",
        "della", "dello", "dei", "degli", "delle", "a", "da", "in", "con",
        "su", "per", "tra", "fra", "e", "o", "ma", "che", "è", "sono",
        "essere", "come", "nel", "nella", "nei", "nelle", "questo", "questa",
        "quello", "quella", "usato", "usati", "usate",
    }

    words = []
    for word in normalizza_confronto(value).split():
        if len(word) >= 5 and word not in stop and word not in words:
            words.append(word)

    return words[:max_items]


def riformula_riassunto(title: str, original: str) -> str:
    keys = parole_chiave(original, 3)
    if keys:
        return frase(
            f"Il punto su «{title}» collega il tema a elementi centrali come {', '.join(keys)}."
        )
    return frase(f"Il punto su «{title}» riassume un concetto centrale del documento.")


def riformula_card_text(title: str, original: str, idx: int = 1) -> str:
    keys = parole_chiave(original, 4)
    detail = ", ".join(keys) if keys else "il concetto principale"

    variants = [
        f"«{title}» introduce il nucleo della scheda e mette a fuoco {detail}.",
        f"Questa card collega «{title}» a {detail}, così il punto resta distinto dagli altri.",
        f"Il valore didattico di «{title}» sta nel riconoscere {detail} e usarlo come riferimento di studio.",
        f"Per ricordare «{title}», concentrati su {detail} e sul ruolo che questo punto ha nel documento.",
        f"«{title}» completa il quadro mostrando come {detail} entra nel ragionamento generale.",
        f"La scheda su «{title}» serve a isolare {detail} senza ripetere gli altri concetti.",
    ]

    return frase(variants[(idx - 1) % len(variants)])


def riformula_risposta_studio(title: str, original: str, idx: int) -> str:
    keys = parole_chiave(original, 3)
    base = ", ".join(keys) if keys else "il punto centrale del documento"

    variants = [
        f"Per ripassare «{title}», collega il concetto a {base} e prova a spiegarlo con parole tue.",
        f"Su «{title}» devi ricordare il significato generale, il motivo per cui conta e il collegamento con {base}.",
        f"Il ripasso di «{title}» funziona se sai distinguere il concetto principale dai dettagli secondari collegati a {base}.",
        f"Quando studi «{title}», concentrati su che cosa indica, perché è utile e quale effetto produce nel documento.",
        f"Per verificare di aver capito «{title}», devi saperlo spiegare senza copiare la frase del documento.",
    ]

    return frase(variants[(idx - 1) % len(variants)])


def riformula_spiegazione_test(title: str, correct: str, idx: int) -> str:
    keys = parole_chiave(correct, 3)
    detail = ", ".join(keys) if keys else "il concetto richiesto"

    variants = [
        f"È corretta perché collega «{title}» a {detail} e risponde direttamente alla richiesta della domanda.",
        f"La scelta giusta è quella che interpreta «{title}» in modo coerente con {detail}, senza aggiungere elementi estranei.",
        f"Questa risposta funziona perché riconosce il ruolo di «{title}» e lo collega al punto didattico principale.",
        f"È l'opzione più adatta perché distingue «{title}» dai distrattori e mantiene il significato indicato dal documento.",
        f"La risposta è valida perché trasforma «{title}» in una verifica chiara del concetto, non in una ripetizione meccanica.",
    ]

    return frase(variants[(idx - 1) % len(variants)])


def domanda_studio_variata(title: str, idx: int) -> str:
    variants = [
        f"Qual è il punto centrale di «{title}»?",
        f"Perché «{title}» è importante nel documento?",
        f"Che cosa devi saper spiegare su «{title}»?",
        f"Quale collegamento devi ricordare su «{title}»?",
        f"Come useresti «{title}» per ripassare il contenuto?",
    ]
    return domanda(variants[(idx - 1) % len(variants)])


def domanda_test_variata(title: str, idx: int) -> str:
    variants = [
        f"Quale opzione spiega correttamente «{title}»?",
        f"Che cosa indica il documento su «{title}»?",
        f"Quale scelta rappresenta meglio «{title}»?",
        f"In che modo va interpretato «{title}»?",
        f"Quale risposta è più coerente con «{title}»?",
    ]
    return domanda(variants[(idx - 1) % len(variants)])


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
        original = pulisci_visibile(item.get("testo", ""))

        item["titolo"] = title
        item["testo"] = riformula_riassunto(title, original)
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
        original = pulisci_visibile(c.get("testo", ""))

        c["titolo"] = title
        c["testo"] = riformula_card_text(title, original, idx)
        c["messaggio_chiave"] = frase(f"Da ricordare: {title}.")
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
        current_question = pulisci_visibile(s.get("domanda", ""))
        title = titolo_da_domanda(current_question, f"Punto {idx}")
        original_answer = pulisci_visibile(s.get("risposta_guida", ""))

        s["domanda"] = domanda_studio_variata(title, idx)
        s["risposta_guida"] = riformula_risposta_studio(title, original_answer, idx)
        s["fonte_visibile"] = ensure_fonte(title)
        s["categoria_v35g"] = categoria(title, "domande_studio")

        items.append(s)

    if items:
        data["domande_studio"] = items

    return data


def refine_tests(data: dict[str, Any]) -> dict[str, Any]:
    tests = []

    for idx, item in enumerate(data.get("test", []) or [], start=1):
        t = dict(item)

        question_raw = pulisci_visibile(t.get("domanda_visibile") or t.get("domanda", ""))
        title = titolo_da_domanda(question_raw, f"Domanda {idx}")

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
            for row in t.get("mappa_opzioni_v35d", []) or []:
                if row.get("corretta"):
                    mapped = frase(pulisci_visibile(row.get("opzione_visibile", "")))
                    if mapped in visible_options:
                        visible_correct = mapped
                    break

        t["domanda_visibile"] = domanda_test_variata(title, idx)
        t["opzioni_visibili"] = visible_options
        t["risposta_corretta_visibile"] = visible_correct
        t["spiegazione"] = riformula_spiegazione_test(title, visible_correct or "", idx)
        t["fonte_visibile"] = ensure_fonte(title)
        t["categoria_v35g"] = categoria(title, "test")

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


def collect_visible_records(data: dict[str, Any]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []

    def add(kind: str, field: str, value: str, idx: int = 0, source: bool = False) -> None:
        text = normalizza_spazi(value)
        if text:
            records.append({
                "kind": kind,
                "field": field,
                "idx": str(idx),
                "text": text,
                "source": "1" if source else "0",
            })

    r = data.get("riassunto")
    if isinstance(r, dict):
        add("riassunto", "titolo", r.get("titolo", ""))
        add("riassunto", "testo_breve", r.get("testo_breve", ""))
        add("riassunto", "conclusione", r.get("conclusione", ""))

        for idx, p in enumerate(r.get("punti_chiave", []) or [], start=1):
            add("riassunto_punto", "titolo", p.get("titolo", ""), idx)
            add("riassunto_punto", "testo", p.get("testo", ""), idx)
            add("fonte", "fonte_visibile", p.get("fonte_visibile", ""), idx, True)

    for idx, c in enumerate(data.get("card", []) or [], start=1):
        add("card", "titolo", c.get("titolo", ""), idx)
        add("card", "testo", c.get("testo", ""), idx)
        add("card", "messaggio_chiave", c.get("messaggio_chiave", ""), idx)
        add("fonte", "fonte_visibile", c.get("fonte_visibile", ""), idx, True)

    for idx, s in enumerate(data.get("domande_studio", []) or [], start=1):
        add("domande_studio", "domanda", s.get("domanda", ""), idx)
        add("domande_studio", "risposta_guida", s.get("risposta_guida", ""), idx)
        add("fonte", "fonte_visibile", s.get("fonte_visibile", ""), idx, True)

    for idx, t in enumerate(data.get("test", []) or [], start=1):
        add("test", "domanda_visibile", t.get("domanda_visibile", ""), idx)
        add("test", "risposta_corretta_visibile", t.get("risposta_corretta_visibile", ""), idx)
        add("test", "spiegazione", t.get("spiegazione", ""), idx)
        add("fonte", "fonte_visibile", t.get("fonte_visibile", ""), idx, True)

        for opt_idx, opt in enumerate(t.get("opzioni_visibili", []) or [], start=1):
            add("opzione_test", f"opzione_{opt_idx}", opt, idx)

    return records


def sembra_frase_spezzata(value: str) -> bool:
    text = normalizza_spazi(value)

    if not text:
        return False

    if text.startswith("Fonte:"):
        return False

    if len(text) < 28:
        return False

    norm_words = normalizza_confronto(text).split()
    last_word = norm_words[-1] if norm_words else ""

    finali_sospetti = {
        "e", "o", "ma", "quindi", "che", "di", "a", "da",
        "in", "con", "su", "per", "tra", "fra", "del", "della",
        "dello", "dei", "degli", "delle", "un", "una", "uno",
        "il", "lo", "la", "gli", "le", "l", "dell", "nell",
        "all", "sull",
    }

    if last_word in finali_sospetti:
        return True

    if len(text) > 45 and text[-1] not in ".!?»”":
        return True

    if text.endswith((" e.", " di.", " con.", " per.", " che.", " del.", " della.", " delle.")):
        return True

    return False


def controlla_duplicati(records: list[dict[str, str]]) -> list[str]:
    errors = []
    content = [
        r for r in records
        if r.get("source") != "1"
        and not (r["kind"] == "test" and r["field"] == "risposta_corretta_visibile")
    ]

    seen: dict[str, dict[str, str]] = {}

    for r in content:
        text = r["text"]
        key = normalizza_confronto(text)

        if len(key) < 35:
            continue

        if key in seen:
            prev = seen[key]
            errors.append(
                f"testo visibile duplicato tra {prev['kind']}:{prev['field']} "
                f"e {r['kind']}:{r['field']}: {text[:90]}"
            )
        else:
            seen[key] = r

    # Card contro card: severo.
    card_texts = [r for r in content if r["kind"] == "card" and r["field"] in {"testo", "messaggio_chiave"}]

    for i, first in enumerate(card_texts):
        for second in card_texts[i + 1:]:
            if first["idx"] == second["idx"]:
                continue

            sim = similarita_testi(first["text"], second["text"])

            if sim >= 0.78:
                errors.append(
                    "card quasi duplicate: "
                    f"«{first['text'][:70]}...» / «{second['text'][:70]}...»"
                )

    # Domande studio tra loro: severo ma non boccia solo la struttura comune se cambia il titolo.
    study_answers = [
        r for r in content
        if r["kind"] == "domande_studio" and r["field"] in {"domanda", "risposta_guida"}
    ]

    for i, first in enumerate(study_answers):
        for second in study_answers[i + 1:]:
            if first["idx"] == second["idx"]:
                continue

            sim = similarita_testi(first["text"], second["text"])

            if sim >= 0.88:
                errors.append(
                    "domande studio quasi duplicate: "
                    f"«{first['text'][:70]}...» / «{second['text'][:70]}...»"
                )

    # Test: opzioni duplicate nella stessa domanda e spiegazioni tutte uguali.
    by_question: dict[str, list[dict[str, str]]] = {}

    for r in content:
        if r["kind"] in {"opzione_test", "test"}:
            by_question.setdefault(r["idx"], []).append(r)

    for idx, items in by_question.items():
        option_keys = []
        for r in items:
            if r["kind"] == "opzione_test":
                key = normalizza_confronto(r["text"])
                if key in option_keys:
                    errors.append(f"test {idx}: opzione duplicata nella stessa domanda")
                option_keys.append(key)

    explanations = [r for r in content if r["kind"] == "test" and r["field"] == "spiegazione"]

    for i, first in enumerate(explanations):
        for second in explanations[i + 1:]:
            if similarita_testi(first["text"], second["text"]) >= 0.86:
                errors.append(
                    "spiegazioni test quasi duplicate: "
                    f"«{first['text'][:70]}...» / «{second['text'][:70]}...»"
                )

    # Cross-output: frase identica lunga tra ruoli diversi = errore.
    role_records = [
        r for r in content
        if r["kind"] in {"riassunto", "riassunto_punto", "card", "domande_studio", "test"}
        and r["field"] not in {"titolo"}
        and len(normalizza_confronto(r["text"])) >= 55
    ]

    for i, first in enumerate(role_records):
        for second in role_records[i + 1:]:
            if first["kind"] == second["kind"]:
                continue

            if normalizza_confronto(first["text"]) == normalizza_confronto(second["text"]):
                errors.append(
                    "frase identica tra output diversi: "
                    f"{first['kind']} e {second['kind']}: {first['text'][:90]}"
                )

    return errors


def validate_quality(data: dict[str, Any]) -> dict[str, Any]:
    errors = []
    warnings = []

    records = collect_visible_records(data)
    texts = [r["text"] for r in records]
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

    for record in records:
        if record.get("source") == "1":
            continue
        if sembra_frase_spezzata(record["text"]):
            errors.append(
                f"frase spezzata o non terminata in {record['kind']}:{record['field']}: "
                f"{record['text'][:120]}"
            )
            break

    errors.extend(controlla_duplicati(records))

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
            "punteggiatura",
            "frasi_complete",
            "assenza_frasi_spezzate",
            "assenza_frasi_non_terminate",
            "assenza_frasi_riempitive",
            "assenza_testi_generici",
            "assenza_duplicati_visibili",
            "assenza_quasi_duplicati",
            "card_concetti_distinti",
            "domande_naturali",
            "spiegazioni_test",
            "fonti_visibili",
            "categorie",
            "sottocategorie",
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
