#!/usr/bin/env python3
"""
RAG Revisore Naturalezza Anti-keyword V3.5I

Scopo:
migliorare i testi finali che tecnicamente passano la qualità,
ma sembrano ancora costruiti da liste di parole chiave.

Controlla e corregge:
- frasi robotiche
- liste grezze di keyword
- formule tipo "mette a fuoco parola, parola"
- formule tipo "elementi centrali come parola, parola"
- formule tipo "entra nel ragionamento generale"
- messaggi poveri tipo "Da ricordare: X"
- card senza spiegazione naturale
- spiegazioni test troppo meccaniche

Non modifica:
- opzioni interne
- risposta_corretta interna
- mappa tecnica del test
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


BANNED_NATURALNESS = [
    "mette a fuoco",
    "concetti chiave:",
    "elementi centrali come",
    "entra nel ragionamento generale",
    "Questa card evidenzia",
    "Il punto su",
    "lista di parole chiave",
]


def normalizza_spazi(value: str) -> str:
    text = str(value or "")
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([,.;:!?])([^\s»”\")])", r"\1 \2", text)
    text = text.replace("..", ".")
    return text.strip()


def pulisci_finale_frase(value: str) -> str:
    text = normalizza_spazi(value)

    # Evita finali brutti: ",.", ";.", ":.", ".,"
    text = re.sub(r"[,;:]\s*\.$", ".", text)
    text = re.sub(r"[,;:]\s*$", ".", text)
    text = text.replace(";.", ".").replace(",.", ".").replace(":.", ".")

    # Evita finali tagliati con articoli, preposizioni o congiunzioni.
    parole_finali_sospette = {
        "e", "o", "ma", "che", "di", "a", "da", "in", "con", "su", "per",
        "tra", "fra", "del", "della", "dello", "dei", "degli", "delle",
        "un", "una", "uno", "il", "lo", "la", "gli", "le"
    }

    words = re.sub(r"[^a-zA-ZàèéìòùÀÈÉÌÒÙ']+", " ", text).strip().lower().split()

    if words and words[-1] in parole_finali_sospette:
        text = " ".join(text.split()[:-1]).rstrip(" ,;:.") + "."

    return normalizza_spazi(text)


def frase(value: str) -> str:
    text = pulisci_finale_frase(value)
    if text and text[-1] not in ".!?»”":
        text += "."
    text = pulisci_finale_frase(text)
    return text


def domanda(value: str) -> str:
    text = normalizza_spazi(value)
    if text and text[-1] != "?":
        text = text.rstrip(".!") + "?"
    return text


def lower_first(value: str) -> str:
    text = normalizza_spazi(value)
    if not text:
        return text
    return text[0].lower() + text[1:]


def titolo_key(value: str) -> str:
    text = str(value or "").lower()
    text = re.sub(r"[^a-z0-9àèéìòù]+", " ", text)
    return " ".join(text.split())


def cut_sentence(value: str, max_chars: int = 190) -> str:
    text = normalizza_spazi(value)

    if len(text) <= max_chars:
        return frase(text)

    # Preferisce tagli naturali. Non taglia mai sulla virgola,
    # perché produce frasi tipo "account amministrativi,."
    for sep in [". ", "; ", ": "]:
        pos = text.rfind(sep, 0, max_chars)
        if pos > 80:
            return frase(text[:pos + 1].strip())

    cut = text[:max_chars].rstrip(" ,;:")
    space = cut.rfind(" ")

    if space > 80:
        cut = cut[:space]

    return frase(cut)


def clean_source_text(value: str) -> str:
    text = normalizza_spazi(value)

    text = re.sub(r"^Concetto:\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^Aspetto:\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^Focus:\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^Nel contesto di «[^»]+»,\s*", "", text, flags=re.IGNORECASE)

    # elimina formule già create dai revisori precedenti
    text = re.sub(r"^Questa card evidenzia «[^»]+» attraverso i concetti chiave:\s*", "", text)
    text = re.sub(r"^Questa card collega «[^»]+» a\s*", "", text)
    text = re.sub(r"^Il valore didattico di «[^»]+» sta nel riconoscere\s*", "", text)
    text = re.sub(r"^Per ricordare «[^»]+», concentrati su\s*", "", text)
    text = re.sub(r"^«[^»]+» completa il quadro mostrando come\s*", "", text)
    text = re.sub(r"^«[^»]+» introduce il nucleo della scheda e\s*", "", text)

    text = text.replace(" entra nel ragionamento generale", "")
    text = text.replace(" così il punto resta distinto dagli altri", "")

    return frase(text)


def build_raw_maps(raw: dict[str, Any]) -> dict[str, dict[str, str]]:
    maps = {
        "card": {},
        "summary_points": {},
        "study": {},
        "test_correct": {},
    }

    for card in raw.get("card", []) or []:
        title = card.get("titolo", "")
        maps["card"][titolo_key(title)] = card.get("testo", "") or card.get("messaggio_chiave", "")

    r = raw.get("riassunto") or {}
    for point in r.get("punti_chiave", []) or []:
        title = point.get("titolo", "")
        maps["summary_points"][titolo_key(title)] = point.get("testo", "")

    for item in raw.get("domande_studio", []) or []:
        title = extract_title(item.get("domanda", ""), fallback=item.get("titolo", ""))
        maps["study"][titolo_key(title)] = item.get("risposta_guida", "")

    for item in raw.get("test", []) or []:
        title = extract_title(item.get("domanda_visibile") or item.get("domanda", ""))
        maps["test_correct"][titolo_key(title)] = item.get("risposta_corretta_visibile") or item.get("risposta_corretta", "")

    return maps


def extract_title(value: str, fallback: str = "") -> str:
    match = re.search(r"«([^»]+)»", value or "")
    if match:
        return normalizza_spazi(match.group(1))
    return normalizza_spazi(fallback or value or "contenuto")


def natural_card_text(title: str, raw_text: str, idx: int) -> str:
    base = cut_sentence(clean_source_text(raw_text), 170)

    variants = [
        f"La scheda spiega «{title}» con un'idea precisa: {lower_first(base)}",
        f"Questa card serve a ricordare «{title}» partendo dal suo significato pratico: {lower_first(base)}",
        f"«{title}» viene presentato come punto autonomo di studio: {lower_first(base)}",
        f"La card su «{title}» chiarisce il concetto senza ripetere gli altri punti: {lower_first(base)}",
        f"Per studiare «{title}», il passaggio da fissare è questo: {lower_first(base)}",
    ]

    return frase(variants[(idx - 1) % len(variants)])


def natural_card_key(title: str, idx: int) -> str:
    variants = [
        f"Da ricordare: spiega «{title}» con parole tue e collegalo al documento.",
        f"Punto chiave: «{title}» deve restare distinto dagli altri concetti.",
        f"Focus studio: usa «{title}» per ricostruire il passaggio principale.",
        f"Memoria rapida: «{title}» è utile se sai dire perché conta.",
        f"Controllo studio: verifica di saper spiegare «{title}» senza copiarlo.",
    ]
    return frase(variants[(idx - 1) % len(variants)])


def natural_summary_point(title: str, raw_text: str, idx: int) -> str:
    base = cut_sentence(clean_source_text(raw_text), 155)

    variants = [
        f"Nel riassunto, «{title}» indica uno dei passaggi centrali: {lower_first(base)}",
        f"Il punto «{title}» aiuta a orientare lo studio perché chiarisce questo aspetto: {lower_first(base)}",
        f"«{title}» sintetizza una parte importante del documento: {lower_first(base)}",
        f"Per capire il quadro generale, «{title}» va collegato a questa idea: {lower_first(base)}",
        f"Il riassunto usa «{title}» per fissare il significato del passaggio: {lower_first(base)}",
    ]

    return frase(variants[(idx - 1) % len(variants)])


def natural_study_answer(title: str, raw_text: str, idx: int) -> str:
    base = cut_sentence(clean_source_text(raw_text), 150)

    variants = [
        f"Per rispondere bene, spiega che cosa significa «{title}» e collegalo al punto seguente: {lower_first(base)}",
        f"Durante il ripasso, usa «{title}» per ricostruire il concetto con parole tue: {lower_first(base)}",
        f"Su «{title}» devi saper dire qual è il problema o il vantaggio spiegato dal documento: {lower_first(base)}",
        f"Una buona risposta non copia la frase: chiarisce «{title}» e poi lo collega al contenuto: {lower_first(base)}",
        f"Per verificare di aver capito «{title}», prova a spiegare perché questo punto è utile nello studio: {lower_first(base)}",
    ]

    return frase(variants[(idx - 1) % len(variants)])


def natural_test_explanation(title: str, correct: str, idx: int) -> str:
    base = cut_sentence(clean_source_text(correct), 145)

    variants = [
        f"È corretta perché risponde direttamente alla domanda su «{title}» e mantiene il significato del documento: {lower_first(base)}",
        f"La scelta è giusta perché distingue «{title}» dai distrattori e riprende il punto richiesto: {lower_first(base)}",
        f"Questa opzione funziona perché collega «{title}» al contenuto essenziale, senza aggiungere informazioni estranee.",
        f"È la risposta più coerente perché interpreta «{title}» nel modo richiesto dalla domanda.",
        f"La spiegazione corretta non copia la card: chiarisce perché «{title}» è il riferimento giusto per questa domanda.",
    ]

    return frase(variants[(idx - 1) % len(variants)])


def improve_summary(data: dict[str, Any], raw_maps: dict[str, dict[str, str]]) -> None:
    r = data.get("riassunto")
    if not isinstance(r, dict):
        return

    r["testo_breve"] = frase(cut_sentence(clean_source_text(r.get("testo_breve", "")), 320))
    r["conclusione"] = frase(cut_sentence(clean_source_text(r.get("conclusione", "")), 220))

    for idx, point in enumerate(r.get("punti_chiave", []) or [], start=1):
        title = point.get("titolo", f"Punto {idx}")
        raw_text = raw_maps["summary_points"].get(titolo_key(title)) or point.get("testo", "")
        point["testo"] = natural_summary_point(title, raw_text, idx)


def improve_cards(data: dict[str, Any], raw_maps: dict[str, dict[str, str]]) -> None:
    for idx, card in enumerate(data.get("card", []) or [], start=1):
        title = card.get("titolo", f"Card {idx}")
        raw_text = raw_maps["card"].get(titolo_key(title)) or card.get("testo", "")

        card["testo"] = natural_card_text(title, raw_text, idx)
        card["messaggio_chiave"] = natural_card_key(title, idx)


def improve_study(data: dict[str, Any], raw_maps: dict[str, dict[str, str]]) -> None:
    for idx, item in enumerate(data.get("domande_studio", []) or [], start=1):
        title = extract_title(item.get("domanda", ""), f"Punto {idx}")
        raw_text = raw_maps["study"].get(titolo_key(title)) or item.get("risposta_guida", "")

        question_variants = [
            f"Che cosa devi saper spiegare su «{title}»?",
            f"Perché «{title}» è utile per capire il documento?",
            f"Qual è il collegamento principale da ricordare su «{title}»?",
            f"Come spiegheresti «{title}» senza copiare il testo?",
            f"Quale ruolo ha «{title}» nel materiale di studio?",
        ]

        item["domanda"] = domanda(question_variants[(idx - 1) % len(question_variants)])
        item["risposta_guida"] = natural_study_answer(title, raw_text, idx)


def improve_tests(data: dict[str, Any], raw_maps: dict[str, dict[str, str]]) -> None:
    for idx, item in enumerate(data.get("test", []) or [], start=1):
        title = extract_title(item.get("domanda_visibile") or item.get("domanda", ""), f"Domanda {idx}")
        correct = item.get("risposta_corretta_visibile") or raw_maps["test_correct"].get(titolo_key(title)) or ""

        question_variants = [
            f"Quale risposta spiega meglio «{title}»?",
            f"Quale opzione è più coerente con «{title}»?",
            f"Che cosa devi riconoscere su «{title}»?",
            f"Quale scelta interpreta correttamente «{title}»?",
            f"Quale affermazione riassume meglio «{title}»?",
        ]

        item["domanda_visibile"] = domanda(question_variants[(idx - 1) % len(question_variants)])
        item["spiegazione"] = natural_test_explanation(title, correct, idx)


def collect_texts(data: dict[str, Any]) -> list[str]:
    texts = []

    r = data.get("riassunto")
    if isinstance(r, dict):
        texts.extend([r.get("titolo", ""), r.get("testo_breve", ""), r.get("conclusione", "")])
        for p in r.get("punti_chiave", []) or []:
            texts.extend([p.get("titolo", ""), p.get("testo", "")])

    for c in data.get("card", []) or []:
        texts.extend([c.get("titolo", ""), c.get("testo", ""), c.get("messaggio_chiave", "")])

    for s in data.get("domande_studio", []) or []:
        texts.extend([s.get("domanda", ""), s.get("risposta_guida", "")])

    for t in data.get("test", []) or []:
        texts.extend([t.get("domanda_visibile", ""), t.get("spiegazione", "")])

    return [normalizza_spazi(t) for t in texts if normalizza_spazi(t)]


def looks_like_keyword_list(text: str) -> bool:
    clean = normalizza_spazi(text)

    # Esempi brutti:
    # "a usare, stessa, password, rischioso"
    # "come sicurezza, informatica, obiettivi, principali"
    pattern = r"\b(?:a|come|su|con)\s+[a-zàèéìòù']{3,14},\s+[a-zàèéìòù']{3,14},\s+[a-zàèéìòù']{3,14}(?:,\s+[a-zàèéìòù']{3,14})?"
    if re.search(pattern, clean, flags=re.IGNORECASE):
        return True

    # Troppi frammenti brevi separati da virgola senza una vera frase.
    parts = [p.strip() for p in clean.split(",")]
    if len(parts) >= 4:
        short_parts = [p for p in parts if 2 <= len(p.split()) <= 2 and len(p) <= 24]
        if len(short_parts) >= 3 and " e " not in clean:
            return True

    return False


def validate_naturalness(data: dict[str, Any]) -> dict[str, Any]:
    errors = []
    texts = collect_texts(data)

    for text in texts:
        for banned in BANNED_NATURALNESS:
            if banned.lower() in text.lower():
                errors.append(f"frase anti-keyword vietata: {banned} -> {text[:120]}")

        if looks_like_keyword_list(text):
            errors.append(f"lista grezza di keyword nel testo visibile: {text[:140]}")

        if re.search(r"[,;:]\s*\.", text):
            errors.append(f"frase tagliata male con punteggiatura sporca: {text[:140]}")

        if re.search(r"\b(e|o|ma|che|di|a|da|in|con|su|per|tra|fra|del|della|dello|dei|degli|delle)\.$", text.lower()):
            errors.append(f"frase con finale sospetto: {text[:140]}")

    for idx, card in enumerate(data.get("card", []) or [], start=1):
        msg = normalizza_spazi(card.get("messaggio_chiave", ""))
        title = normalizza_spazi(card.get("titolo", ""))

        if msg in {f"Da ricordare: {title}.", title}:
            errors.append(f"card {idx}: messaggio chiave povero")

        if len(card.get("testo", "")) < 70:
            errors.append(f"card {idx}: testo troppo povero per card studio")

    return {
        "ok": not errors,
        "errori": errors,
        "testi_controllati": len(texts),
        "nome_controllo": "Controllo di naturalezza linguistica anti-keyword",
    }


def improve_output(data: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any]:
    improved = dict(data)
    raw_maps = build_raw_maps(raw or {})

    improve_summary(improved, raw_maps)
    improve_cards(improved, raw_maps)
    improve_study(improved, raw_maps)
    improve_tests(improved, raw_maps)

    naturalness = validate_naturalness(improved)

    controls = dict(improved.get("controlli_qualita", {}))
    controls["naturalezza_antikeyword_v35i"] = naturalness
    controls["ok"] = bool(controls.get("ok", True)) and naturalness["ok"]
    improved["controlli_qualita"] = controls

    motors = dict(improved.get("motori_riutilizzabili", {}))
    motors["revisore_naturalezza_antikeyword"] = "rag_revisore_naturalezza_antikeyword_v35i"
    improved["motori_riutilizzabili"] = motors

    improved["revisione_naturalezza_antikeyword_v35i"] = {
        "ok": naturalness["ok"],
        "nome": "Controllo di naturalezza linguistica anti-keyword",
        "copre": [
            "niente_liste_grezze_keyword",
            "niente_frasi_robotiche",
            "card_con_spiegazioni_naturali",
            "messaggi_chiave_utili",
            "riassunto_piu_studiabile",
            "domande_studio_umane",
            "spiegazioni_test_non_meccaniche",
        ],
    }

    return improved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--raw-input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    input_path = Path(args.input)
    raw_path = Path(args.raw_input)
    output_path = Path(args.output)

    data = json.loads(input_path.read_text(encoding="utf-8"))
    raw = json.loads(raw_path.read_text(encoding="utf-8"))

    improved = improve_output(data, raw)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(improved, ensure_ascii=False, indent=2), encoding="utf-8")

    q = improved["controlli_qualita"]["naturalezza_antikeyword_v35i"]

    print("=== RAG REVISORE NATURALEZZA ANTI-KEYWORD V3.5I ===")
    print("Input:", input_path)
    print("Raw input:", raw_path)
    print("Output:", output_path)
    print("Qualità naturalezza OK:", q["ok"])
    print("Testi controllati:", q["testi_controllati"])

    if q["errori"]:
        print("ERRORI:")
        for e in q["errori"]:
            print("-", e)

    return 0 if q["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
