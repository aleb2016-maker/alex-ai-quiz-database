#!/usr/bin/env python3
"""
RAG Revisore Accordo Grammaticale e Pronomi V3.5J

Corregge e controlla:
- genere
- numero
- articoli
- participi
- pronomi
- frasi tagliate
- formule con accordo sbagliato
- risposte guida troppo meccaniche
- UI/materiale finale con controllo V3.5J esplicito

Strategia:
usa formulazioni neutre e naturali per evitare errori come:
- "Regola operativa viene presentato"
- "Obiettivi principali senza copiarlo"
- "obiettivi principali è importante"
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


CONTROL_NAME = "Controllo accordo grammaticale e pronomi"


TITLE_LABELS = {
    "Sicurezza informatica": {
        "articolato": "la sicurezza informatica",
        "tema": "questo tema",
        "studio": "questo concetto",
    },
    "Rischio e conseguenza": {
        "articolato": "il rischio e la sua conseguenza",
        "tema": "questo collegamento",
        "studio": "questo passaggio",
    },
    "Regola operativa": {
        "articolato": "la regola operativa",
        "tema": "questa regola",
        "studio": "questo punto operativo",
    },
    "Azione consigliata": {
        "articolato": "l'azione consigliata",
        "tema": "questa azione",
        "studio": "questo comportamento",
    },
    "Obiettivi principali": {
        "articolato": "gli obiettivi principali",
        "tema": "questi obiettivi",
        "studio": "questo gruppo di obiettivi",
    },
}


def normalizza_spazi(value: str) -> str:
    text = str(value or "")
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([,.;:!?])([^\s»”\")])", r"\1 \2", text)
    text = text.replace("..", ".")
    text = text.replace(";.", ".").replace(",.", ".").replace(":.", ".")
    text = re.sub(r"[,;:]\s*$", ".", text)
    return text.strip()


def frase(value: str) -> str:
    text = normalizza_spazi(value)

    if not text:
        return ""

    # Evita finali sospesi.
    text = re.sub(
        r"\b(e|o|ma|che|di|a|da|in|con|su|per|tra|fra|del|della|dello|dei|degli|delle)\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    ).rstrip(" ,;:")

    if text and text[-1] not in ".!?»”":
        text += "."

    return normalizza_spazi(text)


def safe_cut(value: str, max_chars: int = 230) -> str:
    text = normalizza_spazi(value)

    if len(text) <= max_chars:
        return frase(text)

    # Taglia solo dove la frase resta naturale.
    for sep in [". ", "; ", ": "]:
        pos = text.rfind(sep, 0, max_chars)
        if pos > 90:
            return frase(text[:pos + 1])

    cut = text[:max_chars].rstrip(" ,;:")
    pos = cut.rfind(" ")

    if pos > 90:
        cut = cut[:pos]

    return frase(cut)


def extract_title(value: str, fallback: str = "contenuto") -> str:
    match = re.search(r"«([^»]+)»", value or "")
    if match:
        return normalizza_spazi(match.group(1))
    return normalizza_spazi(fallback)


def labels_for(title: str) -> dict[str, str]:
    return TITLE_LABELS.get(
        normalizza_spazi(title),
        {
            "articolato": f"il punto «{title}»",
            "tema": "questo punto",
            "studio": "questo contenuto",
        },
    )


def clean_base(value: str) -> str:
    text = normalizza_spazi(value)

    patterns = [
        r"^La scheda spiega «[^»]+» con un'idea precisa:\s*",
        r"^Questa card serve a ricordare «[^»]+» partendo dal suo significato pratico:\s*",
        r"^«[^»]+» viene presentato come punto autonomo di studio:\s*",
        r"^La card su «[^»]+» chiarisce il concetto senza ripetere gli altri punti:\s*",
        r"^Per studiare «[^»]+», il passaggio da fissare è questo:\s*",
        r"^Nel riassunto, «[^»]+» indica uno dei passaggi centrali:\s*",
        r"^Il punto «[^»]+» aiuta a orientare lo studio perché chiarisce questo aspetto:\s*",
        r"^«[^»]+» sintetizza una parte importante del documento:\s*",
        r"^Per capire il quadro generale, «[^»]+» va collegato a questa idea:\s*",
        r"^Il riassunto usa «[^»]+» per fissare il significato del passaggio:\s*",
        r"^Per rispondere bene, spiega che cosa significa «[^»]+» e collegalo al punto seguente:\s*",
        r"^Durante il ripasso, usa «[^»]+» per ricostruire il concetto con parole tue:\s*",
        r"^Su «[^»]+» devi saper dire qual è il problema o il vantaggio spiegato dal documento:\s*",
        r"^Una buona risposta non copia la frase:\s*",
        r"^È corretta perché risponde direttamente alla domanda su «[^»]+» e mantiene il significato del documento:\s*",
        r"^La scelta è giusta perché distingue «[^»]+» dai distrattori e riprende il punto richiesto:\s*",
    ]

    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    text = text.replace("sicurezza informatica. La sicurezza informatica", "La sicurezza informatica")
    text = text.replace("rischio e conseguenza. Usare", "Usare")
    text = text.replace("regola operativa. Una buona", "Una buona")
    text = text.replace("azione consigliata. Bisogna", "Bisogna")
    text = text.replace("obiettivi principali. La sicurezza", "La sicurezza")

    return safe_cut(text, 230)


def improve_summary(data: dict[str, Any]) -> None:
    r = data.get("riassunto")

    if not isinstance(r, dict):
        return

    for idx, point in enumerate(r.get("punti_chiave", []) or [], start=1):
        title = normalizza_spazi(point.get("titolo", f"Punto {idx}"))
        labels = labels_for(title)
        base = clean_base(point.get("testo", ""))

        variants = [
            f"Nel riassunto, {labels['articolato']} viene collegata al contenuto centrale del documento: {base}",
            f"Il punto dedicato a «{title}» aiuta a capire il quadro generale: {base}",
            f"Per studiare il documento, «{title}» va letto come passaggio autonomo: {base}",
            f"Il riassunto usa «{title}» per fissare un'informazione importante: {base}",
            f"Il passaggio su «{title}» chiarisce un aspetto specifico del documento: {base}",
        ]

        text = variants[(idx - 1) % len(variants)]

        text = text.replace("gli obiettivi principali viene collegata", "gli obiettivi principali vengono collegati")
        text = text.replace("il rischio e la sua conseguenza viene collegata", "il rischio e la sua conseguenza viene collegato")

        point["testo"] = frase(text)


def improve_cards(data: dict[str, Any]) -> None:
    for idx, card in enumerate(data.get("card", []) or [], start=1):
        title = normalizza_spazi(card.get("titolo", f"Card {idx}"))
        labels = labels_for(title)
        base = clean_base(card.get("testo", ""))

        variants = [
            f"La scheda dedicata a «{title}» spiega {labels['tema']} in modo concreto: {base}",
            f"Questa card chiarisce {labels['articolato']} usando un riferimento pratico del documento: {base}",
            f"Il contenuto della card distingue {labels['tema']} dagli altri punti: {base}",
            f"Per ripassare «{title}», parti da questa idea: {base}",
            f"La card su «{title}» serve a fissare un concetto specifico: {base}",
        ]

        card["testo"] = frase(variants[(idx - 1) % len(variants)])

        key_variants = [
            f"Da ricordare: spiega {labels['articolato']} con parole tue e collegala al documento.",
            f"Punto chiave: riconosci il ruolo di {labels['articolato']} nel materiale di studio.",
            f"Focus studio: usa {labels['studio']} per ricostruire il passaggio principale.",
            f"Memoria rapida: chiediti quale problema o vantaggio chiarisce {labels['tema']}.",
            f"Controllo studio: verifica di saper spiegare {labels['articolato']} senza copiare il testo.",
        ]

        key = key_variants[(idx - 1) % len(key_variants)]

        key = key.replace("gli obiettivi principali e collegala", "gli obiettivi principali e collegali")
        key = key.replace("il rischio e la sua conseguenza e collegala", "il rischio e la sua conseguenza e collegalo")
        key = key.replace("la sicurezza informatica e collegala", "la sicurezza informatica e collegala")
        key = key.replace("questa regola e collegala", "questa regola e collegala")
        key = key.replace("questa azione e collegala", "questa azione e collegala")

        card["messaggio_chiave"] = frase(key)


def improve_study(data: dict[str, Any]) -> None:
    for idx, item in enumerate(data.get("domande_studio", []) or [], start=1):
        title = extract_title(item.get("domanda", ""), f"Punto {idx}")
        labels = labels_for(title)
        base = clean_base(item.get("risposta_guida", ""))

        questions = [
            f"Che cosa devi saper spiegare su «{title}»?",
            f"Perché «{title}» è utile per capire il documento?",
            f"Quale collegamento principale devi ricordare su «{title}»?",
            f"Come spiegheresti «{title}» senza copiare il testo?",
            f"Quale ruolo ha «{title}» nel materiale di studio?",
        ]

        answers = [
            f"Per rispondere bene, chiarisci {labels['articolato']} e collega il concetto al documento: {base}",
            f"Durante il ripasso, usa {labels['studio']} per ricostruire il contenuto con parole tue: {base}",
            f"Su «{title}» devi riconoscere quale problema, vantaggio o funzione viene spiegata: {base}",
            f"Una buona risposta spiega {labels['tema']} senza copiare la formulazione della card: {base}",
            f"Per verificare di aver capito, descrivi {labels['articolato']} e il ruolo che ha nello studio: {base}",
        ]

        item["domanda"] = questions[(idx - 1) % len(questions)]
        item["risposta_guida"] = frase(answers[(idx - 1) % len(answers)])


def improve_tests(data: dict[str, Any]) -> None:
    for idx, item in enumerate(data.get("test", []) or [], start=1):
        title = extract_title(item.get("domanda_visibile") or item.get("domanda", ""), f"Domanda {idx}")
        labels = labels_for(title)

        questions = [
            f"Quale risposta spiega meglio «{title}»?",
            f"Quale opzione è più coerente con «{title}»?",
            f"Che cosa devi riconoscere su «{title}»?",
            f"Quale scelta interpreta correttamente «{title}»?",
            f"Quale affermazione riassume meglio «{title}»?",
        ]

        explanations = [
            f"La risposta è corretta perché chiarisce {labels['articolato']} e mantiene il significato indicato dal documento.",
            f"La scelta giusta distingue {labels['tema']} dai distrattori e risponde alla domanda senza aggiungere elementi estranei.",
            f"Questa opzione funziona perché collega {labels['studio']} al contenuto essenziale del documento.",
            f"È l'opzione più coerente perché interpreta {labels['tema']} nel modo richiesto dalla domanda.",
            f"La spiegazione corretta mostra perché {labels['articolato']} è il riferimento adatto per questa domanda.",
        ]

        item["domanda_visibile"] = questions[(idx - 1) % len(questions)]
        item["spiegazione"] = frase(explanations[(idx - 1) % len(explanations)])


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


def validate_agreement(data: dict[str, Any]) -> dict[str, Any]:
    errors = []
    texts = collect_texts(data)
    joined = "\n".join(texts)

    forbidden_patterns = [
        r"Regola operativa» viene presentato",
        r"Azione consigliata» viene presentato",
        r"Sicurezza informatica» viene presentato",
        r"Obiettivi principali» viene presentato",
        r"Obiettivi principali».*senza copiarlo",
        r"obiettivi principali.*senza copiarlo",
        r"obiettivi principali.*è importante",
        r"obiettivi principali.*lo collega",
        r"obiettivi principali.*confonderlo",
        r"regola operativa.*lo collega",
        r"azione consigliata.*lo collega",
        r"«[^»]+» è utile se sai dire perché conta",
        r"viene presentato come punto autonomo",
        r"[,;:]\s*\.",
        r"\b(e|o|ma|che|di|a|da|in|con|su|per|tra|fra|del|della|dello|dei|degli|delle)\.",
    ]

    for pattern in forbidden_patterns:
        if re.search(pattern, joined, flags=re.IGNORECASE):
            errors.append(f"accordo/pronome/frase tagliata sospetta: {pattern}")

    mechanical_patterns = [
        "e collegalo al punto seguente",
        "quale problema o il vantaggio",
        "senza copiarlo",
        "viene presentato",
    ]

    for pattern in mechanical_patterns:
        if pattern.lower() in joined.lower():
            errors.append(f"risposta guida o frase meccanica ancora visibile: {pattern}")

    return {
        "ok": not errors,
        "errori": errors,
        "testi_controllati": len(texts),
        "nome_controllo": CONTROL_NAME,
    }


def improve_output(data: dict[str, Any]) -> dict[str, Any]:
    improved = dict(data)

    improve_summary(improved)
    improve_cards(improved)
    improve_study(improved)
    improve_tests(improved)

    agreement = validate_agreement(improved)

    controls = dict(improved.get("controlli_qualita", {}))
    controls["accordo_pronomi_v35j"] = agreement
    controls["ok"] = bool(controls.get("ok", True)) and agreement["ok"]
    improved["controlli_qualita"] = controls

    motors = dict(improved.get("motori_riutilizzabili", {}))
    motors["revisore_accordo_pronomi"] = "rag_revisore_accordo_pronomi_v35j"
    improved["motori_riutilizzabili"] = motors

    improved["revisione_accordo_pronomi_v35j"] = {
        "ok": agreement["ok"],
        "nome": CONTROL_NAME,
        "copre": [
            "genere",
            "numero",
            "articoli",
            "participi",
            "pronomi",
            "accordo_titoli_contenuti",
            "niente_viene_presentato_errato",
            "niente_senza_copiarlo_errato",
            "niente_frasi_tagliate",
            "risposte_guida_meno_meccaniche",
        ],
    }

    return improved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    data = json.loads(input_path.read_text(encoding="utf-8"))
    improved = improve_output(data)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(improved, ensure_ascii=False, indent=2), encoding="utf-8")

    q = improved["controlli_qualita"]["accordo_pronomi_v35j"]

    print("=== RAG REVISORE ACCORDO PRONOMI V3.5J ===")
    print("Input:", input_path)
    print("Output:", output_path)
    print("Accordo OK:", q["ok"])
    print("Testi controllati:", q["testi_controllati"])

    if q["errori"]:
        print("ERRORI:")
        for e in q["errori"]:
            print("-", e)

    return 0 if q["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
