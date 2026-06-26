#!/usr/bin/env python3
# RAG Documento Studio V4.4
# Obiettivo: documento grande -> riassunto, card studio, indice Q/A.
# Non genera quiz. Riusa i controlli qualità già presenti quando disponibili.

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
GENERATED = ROOT / "dist" / "generated"

STOPWORDS = {
    "il","lo","la","i","gli","le","un","una","uno","di","a","da","in","con","su","per","tra","fra",
    "che","e","o","ma","anche","come","più","meno","molto","nel","nella","nelle","nei","del","della",
    "delle","dei","al","alla","alle","ai","si","non","sono","essere","può","possono","deve","devono",
    "usare","fare","viene","vengono","questo","questa","questi","quelle","quelli","ogni","quando",
    "dopo","prima","sul","sulla","dati","informazioni", "documento"
}

BAD_CHARS = ["þ", "ÿ", "\ufffd"]
BAD_TITLES = {"deve", "devono", "usare", "fare", "dati", "sicurezza", "account", "cosa", "parte"}

def normalizza_testo(testo: str) -> str:
    testo = testo.replace("\r\n", "\n").replace("\r", "\n")
    testo = testo.replace("“", '"').replace("”", '"').replace("’", "'")
    testo = re.sub(r"[ \t]+", " ", testo)
    testo = re.sub(r"\n{3,}", "\n\n", testo)
    testo = re.sub(r" +([,.;:!?])", r"\1", testo)
    testo = re.sub(r"([,.;:!?])([A-Za-zÀ-ÿ])", r"\1 \2", testo)
    return testo.strip()

def iter_chunks_da_file(percorso: Path, target_chars: int = 2200, max_chunks: int = 120) -> Iterable[str]:
    buffer = []
    size = 0
    count = 0
    with percorso.open("r", encoding="utf-8", errors="replace") as f:
        for raw in f:
            line = normalizza_testo(raw)
            if not line:
                continue
            buffer.append(line)
            size += len(line) + 1
            if size >= target_chars:
                chunk = normalizza_testo(" ".join(buffer))
                if chunk:
                    yield chunk
                    count += 1
                buffer, size = [], 0
                if count >= max_chunks:
                    break
    if buffer and count < max_chunks:
        yield normalizza_testo(" ".join(buffer))

def frasi(testo: str) -> list[str]:
    pezzi = re.split(r"(?<=[.!?])\s+", testo)
    pulite = []
    for p in pezzi:
        p = normalizza_testo(p)
        if len(p.split()) >= 6:
            if not p.endswith((".", "!", "?")):
                p += "."
            pulite.append(p)
    return pulite

def tokenizza(testo: str) -> list[str]:
    return [
        t.lower()
        for t in re.findall(r"[A-Za-zÀ-ÿ0-9]{3,}", testo)
        if t.lower() not in STOPWORDS and not t.isdigit()
    ]

def parole_chiave(chunks: list[str], limite: int = 18) -> list[str]:
    c = Counter()
    for chunk in chunks:
        c.update(tokenizza(chunk))
    return [w for w, _ in c.most_common(limite) if w not in BAD_TITLES]

def scegli_frasi_chiave(chunks: list[str], keywords: list[str], limite: int = 10) -> list[str]:
    tutte = []
    kw = set(keywords)
    for chunk in chunks:
        for s in frasi(chunk):
            score = sum(1 for t in tokenizza(s) if t in kw)
            if score:
                tutte.append((score, len(s), s))
    tutte.sort(key=lambda x: (-x[0], x[1]))
    viste = set()
    out = []
    for _, _, s in tutte:
        sig = s.lower()[:90]
        if sig in viste:
            continue
        viste.add(sig)
        out.append(s)
        if len(out) >= limite:
            break
    return out

def titolo_da_keyword(k: str) -> str:
    k = k.replace("_", " ").strip()
    if not k or k.lower() in BAD_TITLES:
        return ""
    return k[:1].upper() + k[1:]

def sentence_for_keyword(chunks: list[str], keyword: str) -> str:
    key = keyword.lower()
    best = ""
    for chunk in chunks:
        for s in frasi(chunk):
            if key in s.lower():
                if not best or len(s) < len(best):
                    best = s
    return best

def crea_riassunto(chunks: list[str], titolo: str) -> dict:
    keys = parole_chiave(chunks, 16)
    frasi_top = scegli_frasi_chiave(chunks, keys, 12)
    punti = frasi_top[:7]
    dettagli = frasi_top[7:12] or frasi_top[:4]
    return {
        "titolo": titolo or "Riassunto del documento",
        "panoramica": "Il documento viene sintetizzato individuando i concetti più ricorrenti e i passaggi più informativi.",
        "punti_chiave": punti,
        "dettagli_utili": dettagli,
        "parole_chiave": keys,
    }

def crea_cards(chunks: list[str], max_cards: int = 10) -> list[dict]:
    keys = parole_chiave(chunks, max_cards * 2)
    cards = []
    for key in keys:
        titolo = titolo_da_keyword(key)
        if not titolo:
            continue
        frase = sentence_for_keyword(chunks, key)
        if not frase:
            continue
        cards.append({
            "titolo": titolo,
            "fronte": f"Concetto chiave: {titolo}",
            "retro": frase,
            "spiegazione": frase,
            "uso": "Ripassa il concetto e collegalo a un esempio concreto presente nel documento.",
            "tags": [key],
            "origine": "documento",
        })
        if len(cards) >= max_cards:
            break
    return cards

def crea_indice_qa(chunks: list[str]) -> list[dict]:
    indice = []
    for i, chunk in enumerate(chunks, start=1):
        indice.append({
            "id": f"chunk-{i:03d}",
            "testo": chunk,
            "keywords": parole_chiave([chunk], 10),
        })
    return indice

def controlli_linguistici(payload: dict) -> list[str]:
    avvisi = []
    try:
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from qualita_linguistica import controlla_lingua_testo
    except Exception as exc:
        return [f"Controllo linguistico non importato: {exc}"]

    testi = []
    riassunto = payload.get("riassunto", {})
    testi.extend(riassunto.get("punti_chiave", []))
    testi.extend(riassunto.get("dettagli_utili", []))
    for c in payload.get("cards", []):
        testi.append(c.get("titolo", ""))
        testi.append(c.get("spiegazione", ""))

    for i, testo in enumerate(testi, start=1):
        try:
            risultato = controlla_lingua_testo(testo, f"rag_documento_studio_v44_{i}")
            if risultato:
                avvisi.append(f"Testo {i}: {risultato}")
        except Exception as exc:
            avvisi.append(f"Testo {i}: controllo non eseguito: {exc}")
    return avvisi

def valida_payload(payload: dict) -> list[str]:
    problemi = []
    blob = json.dumps(payload, ensure_ascii=False)
    for ch in BAD_CHARS:
        if ch in blob:
            problemi.append(f"Simbolo corrotto trovato: {ch}")
    if not payload.get("chunks"):
        problemi.append("Nessun chunk generato.")
    if len(payload.get("riassunto", {}).get("punti_chiave", [])) < 3:
        problemi.append("Riassunto troppo debole: meno di 3 punti chiave.")
    if len(payload.get("cards", [])) < 4:
        problemi.append("Troppe poche card generate.")
    for i, card in enumerate(payload.get("cards", []), start=1):
        titolo = str(card.get("titolo", "")).strip().lower()
        if not titolo or titolo in BAD_TITLES:
            problemi.append(f"Card {i}: titolo debole o generico: {titolo}")
        if len(str(card.get("spiegazione", "")).split()) < 8:
            problemi.append(f"Card {i}: spiegazione troppo corta.")
    return problemi

def main() -> None:
    parser = argparse.ArgumentParser(description="Documento grande -> riassunto, card, indice Q/A.")
    parser.add_argument("--documento", required=True, help="File TXT/MD già estratto o scritto in UTF-8.")
    parser.add_argument("--titolo", default="Documento di studio")
    parser.add_argument("--max-chunks", type=int, default=120)
    parser.add_argument("--max-cards", type=int, default=10)
    parser.add_argument("--output", default="dist/generated/rag_documento_studio_v44.json")
    args = parser.parse_args()

    documento = Path(args.documento)
    if not documento.exists():
        raise SystemExit(f"ERRORE: documento non trovato: {documento}")

    chunks = list(iter_chunks_da_file(documento, max_chunks=args.max_chunks))
    payload = {
        "versione": "rag_documento_studio_v44",
        "titolo": args.titolo,
        "documento_origine": str(documento),
        "modalita": ["riassunto", "card", "interroga_documento"],
        "chunks": chunks,
        "riassunto": crea_riassunto(chunks, args.titolo),
        "cards": crea_cards(chunks, args.max_cards),
        "qa_index": crea_indice_qa(chunks),
        "qualita": {
            "regola": "riusa_motori_qualita_esistenti",
            "avvisi_linguistici": [],
            "problemi_bloccanti": [],
        }
    }

    payload["qualita"]["avvisi_linguistici"] = controlli_linguistici(payload)
    payload["qualita"]["problemi_bloccanti"] = valida_payload(payload)

    out = ROOT / args.output if not Path(args.output).is_absolute() else Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    REPORTS.mkdir(exist_ok=True)
    report = REPORTS / "rag_documento_studio_v44.md"
    report.write_text(
        "# RAG Documento Studio V4.4\n\n"
        f"- Documento: `{documento}`\n"
        f"- Output: `{out}`\n"
        f"- Chunk: {len(chunks)}\n"
        f"- Card: {len(payload['cards'])}\n"
        f"- Punti riassunto: {len(payload['riassunto']['punti_chiave'])}\n"
        f"- Avvisi linguistici: {len(payload['qualita']['avvisi_linguistici'])}\n"
        f"- Problemi bloccanti: {len(payload['qualita']['problemi_bloccanti'])}\n",
        encoding="utf-8"
    )

    if payload["qualita"]["problemi_bloccanti"]:
        print("ERRORE: problemi bloccanti nel documento studio")
        for p in payload["qualita"]["problemi_bloccanti"]:
            print("-", p)
        raise SystemExit(1)

    print("=== RAG Documento Studio V4.4 ===")
    print(f"Chunk: {len(chunks)}")
    print(f"Card: {len(payload['cards'])}")
    print(f"Output: {out}")
    print(f"Report: {report}")
    print("OK: riassunto/card/indice Q&A generati senza problemi bloccanti.")

if __name__ == "__main__":
    main()
