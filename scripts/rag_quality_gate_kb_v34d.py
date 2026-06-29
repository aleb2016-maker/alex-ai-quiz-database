#!/usr/bin/env python3
"""
RAG Quality Gate Knowledge Base V3.4D

Questo modulo non genera pagine e non corregge frasi a valle.
Fa un controllo prima dei generatori:

KB grezza V3.4B
↓
Quality Gate V3.4D
↓
KB pulita, con concetti approvati e testo utente pronto
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


STOPWORDS = {
    "della", "delle", "degli", "dello", "dalla", "dalle", "dagli", "agli", "alle",
    "alla", "allo", "nella", "nelle", "negli", "nello", "sulla", "sulle", "sugli",
    "con", "per", "tra", "fra", "che", "una", "uno", "gli", "le", "il", "lo", "la",
    "un", "di", "da", "in", "su", "e", "o", "ma", "anche", "solo", "come", "quando",
    "quale", "quali", "cosa", "questo", "questa", "questi", "queste", "essere",
    "avere", "sono", "viene", "vengono", "deve", "devono", "può", "possono",
    "più", "meno", "molto", "molti", "ogni", "del", "dei", "nel", "nei", "sul",
    "sui", "dal", "dai", "al", "ai", "ed", "ad",
}

META_MARKERS = [
    "domanda:",
    "risposta:",
    "risposta corretta:",
    "risposta corretta",
    "la risposta corretta è",
    "distrattore:",
    "distrattore forte:",
    "distrattore debole:",
    "esempio di domanda",
    "domanda possibile",
    "opzione corretta",
    "opzione sbagliata",
    "scopo del documento",
    "documento rag di test",
    "## scopo",
    "questo documento è stato creato",
    "fonte di prova",
    "motore rag",
    "progetto quiz",
    "può essere inserito",
    "cartella rag",
    "rag/documenti",
    "generare quiz",
    "generare test",
    "generare mini",
    "fallback",
    "prompt",
]

TITOLI_GREZZI_MARKERS = [
    "indica punti",
    "perché rischioso",
    "software autorizzato allegati",
    "malware allegati pericolosi",
    "dati dispositivi account",
]


def normalizza_spazi(value: str) -> str:
    text = " ".join(str(value or "").split()).strip()
    text = text.replace("..", ".")
    text = text.replace("?.", "?")
    text = text.replace("!.", "!")
    text = text.replace(" ,", ",")
    text = text.replace(" .", ".")
    text = text.replace(" ;", ";")
    return text


def finalizza_frase(value: str) -> str:
    text = normalizza_spazi(value)
    if text and text[-1] not in ".!?":
        text += "."
    return text


def rimuovi_markdown(value: str) -> str:
    text = str(value or "")
    text = re.sub(r"^#{1,6}\s+", "", text.strip())
    text = re.sub(r"\s+#{1,6}\s+", ". ", text)
    text = text.replace("**", "")
    text = text.replace("__", "")
    return normalizza_spazi(text)


def rimuovi_prefissi_meta(value: str) -> str:
    text = normalizza_spazi(rimuovi_markdown(value))
    low = text.lower()

    for marker in [
        "domanda:",
        "risposta:",
        "risposta corretta:",
    "risposta corretta",
    "la risposta corretta è",
        "distrattore forte:",
        "distrattore debole:",
        "esempio:",
    ]:
        if low.startswith(marker):
            return normalizza_spazi(text[len(marker):])

    return text


def e_testo_meta(value: str) -> bool:
    text = normalizza_spazi(value)
    low = text.lower()

    if not text:
        return True

    if text.strip().startswith("#"):
        return True

    if len(text) < 35:
        return True

    for marker in META_MARKERS:
        if marker in low:
            return True

    if re.search(r"\b[\w.-]+\.(py|js|json|html|md|txt|zip)\b", low):
        return True

    if re.search(r"\b[a-z0-9_-]+/[a-z0-9_./-]+\b", low):
        return True

    return False


def spezza_testo(value: str) -> list[str]:
    text = rimuovi_prefissi_meta(value)
    text = text.replace("; - ", "; ")
    text = text.replace(". - ", ". ")
    text = re.sub(r"(^|\s)-\s+", r"\1", text)

    parts = [normalizza_spazi(p).strip(" .;:-") for p in re.split(r";|\n", text)]
    parts = [p for p in parts if len(p) >= 12]

    return parts


def pulisci_testo_utente(value: str) -> str:
    text = rimuovi_prefissi_meta(value)

    if text.count(";") >= 2:
        parts = spezza_testo(text)
        if parts:
            text = ". ".join(parts[:4])

    text = re.sub(
        r"^Cos['’]è\s+[A-Za-zÀ-ÿ0-9'’ ]{4,90}\s+(La|Il|Le|Gli|I|Lo|L'|Un|Una)\s+",
        r"\1 ",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"^([A-ZÀ-Ý][A-Za-zÀ-ÿ0-9'’ ]{4,80})\s+(Gli|Le|La|Il|I|Lo|L'|Un|Una|Nel|Nella)\s+",
        r"\2 ",
        text,
    )

    text = normalizza_spazi(text)

    if len(text) > 260:
        text = text[:260].rsplit(" ", 1)[0].strip()

    return finalizza_frase(text)


def parole_utili(value: str) -> list[str]:
    raw = re.findall(r"[A-Za-zÀ-ÿ0-9'’]{4,}", str(value or "").lower())
    result = []

    for token in raw:
        token = token.strip("'’")

        if not token:
            continue

        if token in STOPWORDS:
            continue

        if token in {
            "documento", "testo", "punto", "punti", "spiega", "indica",
            "bisogna", "devono", "possono", "viene", "vengono",
            "usare", "avere", "fare", "essere",
        }:
            continue

        if token not in result:
            result.append(token)

    return result


def titolo_utente_da_testo(value: str) -> str:
    text = pulisci_testo_utente(value)

    soggetto = re.match(
        r"^(La|Il|Le|Gli|I|Lo|L'|Un|Una)\s+(.+?)\s+(è|sono|serve|aiuta|riduce|migliora|prepara|consente|permette|ha|hanno)\b",
        text,
        flags=re.IGNORECASE,
    )

    if soggetto:
        candidate = normalizza_spazi(soggetto.group(2))
        if 6 <= len(candidate) <= 70:
            return candidate[0].upper() + candidate[1:]

    # Frasi operative: prende una forma breve ma non spezzata.
    if text.lower().startswith(("bisogna ", "occorre ", "è necessario ")):
        cleaned = re.sub(r"^(bisogna|occorre|è necessario)\s+", "", text, flags=re.IGNORECASE)
        cleaned = cleaned.split(",")[0].strip(" .")
        words = cleaned.split()
        if len(words) >= 3:
            return " ".join(words[:7]).capitalize()

    words = parole_utili(text)

    if len(words) >= 3:
        return " ".join(words[:4]).capitalize()

    if words:
        return " ".join(words).capitalize()

    return "Punto del documento"


def motivo_scarto(concept: dict[str, Any]) -> str | None:
    titolo = normalizza_spazi(concept.get("titolo", ""))
    descrizione = normalizza_spazi(concept.get("descrizione", ""))
    frasi = concept.get("frasi_origine", [])

    testi = [titolo, descrizione]
    if isinstance(frasi, list):
        testi.extend(str(f) for f in frasi)

    combinato = " ".join(testi)
    low = combinato.lower()

    if e_testo_meta(combinato):
        return "testo meta/non didattico"

    for marker in TITOLI_GREZZI_MARKERS:
        if marker in low:
            return f"titolo grezzo vietato: {marker}"

    pulito = pulisci_testo_utente(descrizione)
    if len(pulito) < 45:
        return "testo utente troppo povero"

    titolo_utente = titolo_utente_da_testo(pulito)

    testi_puliti = [pulito, titolo_utente]
    if isinstance(frasi, list):
        testi_puliti.extend(pulisci_testo_utente(f) for f in frasi)

    combinato_pulito = " ".join(testi_puliti)
    if e_testo_meta(combinato_pulito):
        return "testo utente pulito ancora meta/non didattico"

    if titolo_utente.lower() in {"punto del documento", "documento", "testo", "risposta corretta"}:
        return "titolo utente non informativo"

    return None


def pulisci_concetto(concept: dict[str, Any]) -> dict[str, Any] | None:
    reason = motivo_scarto(concept)
    if reason:
        return None

    descrizione_pulita = pulisci_testo_utente(concept.get("descrizione", ""))
    titolo_utente = titolo_utente_da_testo(descrizione_pulita)

    frasi = concept.get("frasi_origine", [])
    frasi_pulite = []

    if isinstance(frasi, list):
        for frase in frasi:
            if e_testo_meta(frase):
                continue
            cleaned = pulisci_testo_utente(frase)
            if cleaned and cleaned not in frasi_pulite:
                frasi_pulite.append(cleaned)

    if not frasi_pulite:
        frasi_pulite = [descrizione_pulita]

    parole = concept.get("parole_chiave", [])
    parole_pulite = []
    if isinstance(parole, list):
        for p in parole:
            token = normalizza_spazi(p).lower()
            if not token or token in STOPWORDS:
                continue
            if any(marker in token for marker in META_MARKERS):
                continue
            if token not in parole_pulite:
                parole_pulite.append(token)

    nuovo = dict(concept)
    nuovo["titolo_originale"] = concept.get("titolo", "")
    nuovo["descrizione_originale"] = concept.get("descrizione", "")
    nuovo["titolo"] = titolo_utente
    nuovo["descrizione"] = descrizione_pulita
    nuovo["titolo_utente"] = titolo_utente
    nuovo["testo_utente"] = descrizione_pulita
    nuovo["frasi_origine"] = frasi_pulite
    nuovo["parole_chiave"] = parole_pulite[:12]
    nuovo["quality_gate_v34d"] = {
        "approvato": True,
        "motivo": "contenuto didattico pulito",
    }

    return nuovo


def pulisci_frasi_importanti(kb: dict[str, Any]) -> list[str]:
    result = []

    for frase in kb.get("frasi_importanti", []):
        if e_testo_meta(frase):
            continue

        cleaned = pulisci_testo_utente(frase)
        if cleaned and cleaned not in result:
            result.append(cleaned)

    return result


def applica_quality_gate(kb: dict[str, Any]) -> dict[str, Any]:
    concetti_originali = kb.get("concetti", [])
    concetti_puliti = []
    scartati = []

    for concept in concetti_originali:
        cleaned = pulisci_concetto(concept)
        if cleaned:
            concetti_puliti.append(cleaned)
        else:
            scartati.append({
                "id": concept.get("id"),
                "titolo": concept.get("titolo"),
                "motivo": motivo_scarto(concept) or "non approvato",
            })

    ids_validi = {c.get("id") for c in concetti_puliti if c.get("id")}

    relazioni_pulite = []
    for rel in kb.get("relazioni_tra_concetti", []):
        if rel.get("da") in ids_validi and rel.get("a") in ids_validi:
            relazioni_pulite.append(rel)

    nuova = dict(kb)
    nuova["concetti_originali_count"] = len(concetti_originali)
    nuova["concetti"] = concetti_puliti
    nuova["frasi_importanti"] = pulisci_frasi_importanti(kb)
    nuova["relazioni_tra_concetti"] = relazioni_pulite

    errori = []
    avvisi = []

    if len(concetti_puliti) < 4:
        errori.append("meno di 4 concetti puliti approvati")

    if len(nuova["frasi_importanti"]) < 3:
        avvisi.append("meno di 3 frasi importanti pulite")

    nuova["quality_gate_v34d"] = {
        "ok": not errori,
        "errori": errori,
        "avvisi": avvisi,
        "concetti_originali": len(concetti_originali),
        "concetti_approvati": len(concetti_puliti),
        "concetti_scartati": len(scartati),
        "scartati": scartati,
    }

    nuova["controlli_qualita"] = dict(kb.get("controlli_qualita", {}))
    nuova["controlli_qualita"]["quality_gate_v34d"] = nuova["quality_gate_v34d"]
    nuova["controlli_qualita"]["ok"] = nuova["controlli_qualita"].get("ok", True) and not errori

    return nuova


def carica_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def scrivi_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kb", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    kb_path = Path(args.kb)
    output_path = Path(args.output)

    kb = carica_json(kb_path)
    pulita = applica_quality_gate(kb)

    scrivi_json(output_path, pulita)

    gate = pulita["quality_gate_v34d"]

    print("=== RAG QUALITY GATE KB V3.4D ===")
    print("Input KB:", kb_path)
    print("Output KB pulita:", output_path)
    print("Concetti originali:", gate["concetti_originali"])
    print("Concetti approvati:", gate["concetti_approvati"])
    print("Concetti scartati:", gate["concetti_scartati"])
    print("Qualità OK:", gate["ok"])

    if gate["errori"]:
        print("ERRORI:")
        for e in gate["errori"]:
            print("-", e)

    if gate["avvisi"]:
        print("AVVISI:")
        for a in gate["avvisi"]:
            print("-", a)

    return 0 if gate["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
