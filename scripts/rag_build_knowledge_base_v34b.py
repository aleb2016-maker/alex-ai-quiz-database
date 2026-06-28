#!/usr/bin/env python3
"""
RAG Knowledge Base Builder V3.4B

Questo script costruisce una Knowledge Base JSON generale.

Non genera ancora card, riassunto, test o domande studio finali.
Serve come base interna riutilizzabile per tutti i generatori futuri.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

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

TIPI_DOCUMENTO = {
    "sport_allenamento": {
        "allenamento", "recupero", "muscoli", "forza", "esercizi", "serie",
        "ripetizioni", "carico", "riscaldamento", "progressione",
    },
    "curriculum": {
        "curriculum", "esperienza", "competenze", "profilo", "candidato",
        "professionale", "formazione", "lavoro", "obiettivo", "selezionatore",
    },
    "poesia_racconto": {
        "poesia", "versi", "metafora", "ritmo", "racconto", "personaggio",
        "storia", "emozione", "narrazione", "immagini",
    },
    "documento_aziendale": {
        "azienda", "procedura", "processo", "regole", "dipendente",
        "organizzazione", "reparto", "attività", "responsabilità", "obiettivo",
    },
    "documento_tecnico_formativo": {
        "sistema", "sicurezza", "dati", "account", "software", "strumenti",
        "rischio", "protezione", "procedura", "formazione",
    },
}


def normalizza_spazi(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def leggi_input(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Input non trovato: {path}")

    text = normalizza_spazi(path.read_text(encoding="utf-8", errors="ignore"))

    if len(text) < 80:
        raise ValueError("Input troppo corto: impossibile costruire una Knowledge Base affidabile.")

    return text


def estrai_titolo(text: str, input_path: Path) -> str:
    for line in text.splitlines():
        clean = line.strip().strip("#").strip()
        if 8 <= len(clean) <= 120:
            return clean

    return input_path.stem.replace("_", " ").replace("-", " ").title()


def tokenizza(text: str) -> list[str]:
    raw = re.findall(r"[A-Za-zÀ-ÿ0-9']{4,}", text.lower())
    result = []

    for token in raw:
        token = token.strip("'’")
        if not token or token in STOPWORDS:
            continue
        result.append(token)

    return result


def estrai_frasi(text: str) -> list[str]:
    prepared = re.sub(r"\n+", " ", text)
    parts = re.split(r"(?<=[.!?])\s+", prepared)

    frasi = []
    for part in parts:
        clean = " ".join(part.split()).strip()
        if 35 <= len(clean) <= 260:
            frasi.append(clean)

    return frasi


def crea_chunk(text: str, max_chars: int = 1100) -> list[dict[str, Any]]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    chunks = []
    current = []
    current_len = 0

    for paragraph in paragraphs:
        if current and current_len + len(paragraph) > max_chars:
            chunks.append("\n\n".join(current))
            current = [paragraph]
            current_len = len(paragraph)
        else:
            current.append(paragraph)
            current_len += len(paragraph)

    if current:
        chunks.append("\n\n".join(current))

    result = []
    for idx, chunk_text in enumerate(chunks, start=1):
        result.append({
            "id": f"chunk-{idx}",
            "ordine": idx,
            "testo": chunk_text,
            "parole_chiave": [],
            "frasi_importanti": [],
            "fonte": {
                "pagina": None,
                "sezione": None,
                "origine": "input_testuale",
            },
        })

    return result


def parole_chiave_da_testo(text: str, limit: int = 18) -> list[str]:
    counts = Counter(tokenizza(text))
    return [word for word, _ in counts.most_common(limit)]


def score_frase(frase: str, keywords: list[str]) -> float:
    low = frase.lower()
    score = 0.0

    for kw in keywords:
        if kw in low:
            score += 2.0

    if any(marker in low for marker in ["perché", "serve", "riduce", "aumenta", "migliora", "evita", "consente"]):
        score += 2.5

    if any(marker in low for marker in ["deve", "devono", "è importante", "bisogna", "necessario"]):
        score += 1.5

    if 70 <= len(frase) <= 180:
        score += 1.0

    return score


def frasi_importanti(frasi: list[str], keywords: list[str], limit: int = 8) -> list[str]:
    ranked = sorted(frasi, key=lambda f: score_frase(f, keywords), reverse=True)

    result = []
    seen = set()

    for frase in ranked:
        key = frase.lower()
        if key in seen:
            continue

        seen.add(key)
        result.append(frase)

        if len(result) >= limit:
            break

    return result


def tipo_documento_da_keywords(keywords: list[str]) -> str:
    kw = set(keywords)
    scores = {}

    for tipo, parole in TIPI_DOCUMENTO.items():
        scores[tipo] = len(kw & parole)

    best_tipo, best_score = max(scores.items(), key=lambda item: item[1])

    if best_score <= 0:
        return "documento_generico"

    return best_tipo


def titolo_concetto_da_frase(frase: str, global_keywords: list[str]) -> str:
    frase_tokens = tokenizza(frase)
    selected = []

    for kw in global_keywords:
        if kw in frase_tokens and kw not in selected:
            selected.append(kw)

        if len(selected) >= 3:
            break

    if not selected:
        selected = frase_tokens[:3]

    if not selected:
        return "Concetto documento"

    return " ".join(selected).capitalize()


def crea_concetti(chunks: list[dict[str, Any]], global_keywords: list[str]) -> list[dict[str, Any]]:
    concetti = []
    used_titles = set()

    for chunk in chunks:
        for frase in chunk["frasi_importanti"]:
            title = titolo_concetto_da_frase(frase, global_keywords)
            key = title.lower()

            if key in used_titles:
                continue

            used_titles.add(key)

            concept_keywords = [
                kw for kw in global_keywords
                if kw in frase.lower()
            ][:8]

            concetti.append({
                "id": f"concept-{len(concetti) + 1}",
                "titolo": title,
                "descrizione": frase,
                "frasi_origine": [frase],
                "parole_chiave": concept_keywords,
                "chunk_origine": chunk["id"],
                "peso": round(score_frase(frase, global_keywords), 2),
                "relazioni": [],
            })

    concetti.sort(key=lambda item: item["peso"], reverse=True)
    return concetti[:12]


def crea_relazioni(concetti: list[dict[str, Any]]) -> list[dict[str, Any]]:
    relazioni = []

    for i, a in enumerate(concetti):
        set_a = set(a.get("parole_chiave", []))

        for b in concetti[i + 1:]:
            set_b = set(b.get("parole_chiave", []))
            comuni = sorted(set_a & set_b)

            stesso_chunk = a.get("chunk_origine") == b.get("chunk_origine")

            if comuni or stesso_chunk:
                rel = {
                    "id": f"rel-{len(relazioni) + 1}",
                    "da": a["id"],
                    "a": b["id"],
                    "tipo": "collegamento_concettuale",
                    "motivo": "parole chiave condivise" if comuni else "stesso chunk di origine",
                    "parole_condivise": comuni,
                }
                relazioni.append(rel)

                a["relazioni"].append(rel["id"])
                b["relazioni"].append(rel["id"])

    return relazioni


def controlli_qualita(kb: dict[str, Any]) -> dict[str, Any]:
    errori = []
    avvisi = []

    if not kb.get("input_reale_usato"):
        errori.append("input reale non confermato")

    if len(kb.get("chunk", [])) < 1:
        errori.append("nessun chunk generato")

    if len(kb.get("concetti", [])) < 3:
        errori.append("meno di 3 concetti: KB troppo povera")

    if len(kb.get("parole_chiave", [])) < 8:
        avvisi.append("poche parole chiave estratte")

    for concetto in kb.get("concetti", []):
        if not concetto.get("frasi_origine"):
            errori.append(f"concetto senza frase origine: {concetto.get('id')}")

        if not concetto.get("chunk_origine"):
            errori.append(f"concetto senza chunk origine: {concetto.get('id')}")

    return {
        "ok": not errori,
        "errori": errori,
        "avvisi": avvisi,
    }


def costruisci_kb(input_path: Path) -> dict[str, Any]:
    text = leggi_input(input_path)
    titolo = estrai_titolo(text, input_path)

    chunks = crea_chunk(text)
    global_keywords = parole_chiave_da_testo(text, limit=25)
    all_sentences = estrai_frasi(text)
    important_global = frasi_importanti(all_sentences, global_keywords, limit=12)

    for chunk in chunks:
        chunk_keywords = parole_chiave_da_testo(chunk["testo"], limit=12)
        chunk_sentences = estrai_frasi(chunk["testo"])
        chunk_important = frasi_importanti(chunk_sentences, global_keywords, limit=5)

        chunk["parole_chiave"] = chunk_keywords
        chunk["frasi_importanti"] = chunk_important

    concetti = crea_concetti(chunks, global_keywords)
    relazioni = crea_relazioni(concetti)

    kb = {
        "versione": "rag-knowledge-base-v34b",
        "titolo_documento": titolo,
        "tipo_documento": tipo_documento_da_keywords(global_keywords),
        "input_reale_usato": True,
        "file_input": str(input_path),
        "statistiche": {
            "caratteri": len(text),
            "chunk": len(chunks),
            "frasi": len(all_sentences),
            "concetti": len(concetti),
            "relazioni": len(relazioni),
        },
        "chunk": chunks,
        "concetti": concetti,
        "parole_chiave": global_keywords,
        "frasi_importanti": important_global,
        "relazioni_tra_concetti": relazioni,
        "fonti_pagine_sezioni": [
            {
                "chunk_id": c["id"],
                "pagina": c["fonte"]["pagina"],
                "sezione": c["fonte"]["sezione"],
                "origine": c["fonte"]["origine"],
            }
            for c in chunks
        ],
        "output_generati": {
            "riassunto": None,
            "card": [],
            "test": [],
            "domande_studio": [],
        },
        "controlli_qualita": {},
    }

    kb["controlli_qualita"] = controlli_qualita(kb)
    return kb


def scrivi_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="dist/generated/rag_knowledge_base_v34b/knowledge_base.json")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = ROOT / args.output if not Path(args.output).is_absolute() else Path(args.output)

    kb = costruisci_kb(input_path)
    scrivi_json(output_path, kb)

    print("=== RAG KNOWLEDGE BASE V3.4B ===")
    print("Input:", input_path)
    print("Output:", output_path)
    print("Titolo:", kb["titolo_documento"])
    print("Tipo:", kb["tipo_documento"])
    print("Chunk:", kb["statistiche"]["chunk"])
    print("Concetti:", kb["statistiche"]["concetti"])
    print("Relazioni:", kb["statistiche"]["relazioni"])
    print("Qualità OK:", kb["controlli_qualita"]["ok"])

    if kb["controlli_qualita"]["errori"]:
        print("ERRORI:")
        for err in kb["controlli_qualita"]["errori"]:
            print("-", err)

    if kb["controlli_qualita"]["avvisi"]:
        print("AVVISI:")
        for avviso in kb["controlli_qualita"]["avvisi"]:
            print("-", avviso)

    return 0 if kb["controlli_qualita"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
