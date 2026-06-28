#!/usr/bin/env python3
"""
RAG Generatori Test + Domande Studio da Knowledge Base V3.4C

Questo script NON legge direttamente il documento grezzo.
Legge SOLO la Knowledge Base JSON.

Regola:
- niente toppe per argomento singolo;
- niente if su password/phishing/malware/sport/curriculum;
- ogni output deve avere origine nella KB.
"""

from __future__ import annotations

import argparse
import json
import random
import re
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
    "sui", "dal", "dai", "al", "ai", "ed", "ad", "documento", "testo",
}


def normalizza_spazi(value: str) -> str:
    text = " ".join(str(value or "").split()).strip()
    text = text.replace("..", ".")
    text = text.replace("?.", "?")
    text = text.replace("!.", "!")
    text = text.replace(" ,", ",")
    text = text.replace(" .", ".")
    return text


def finalizza_frase(value: str) -> str:
    text = normalizza_spazi(value)
    if text and text[-1] not in ".!?":
        text += "."
    return text


def tokenizza(value: str) -> set[str]:
    raw = re.findall(r"[A-Za-zÀ-ÿ0-9']{4,}", str(value or "").lower())
    return {t.strip("'’") for t in raw if t.strip("'’") and t.strip("'’") not in STOPWORDS}


def similarita(a: str, b: str) -> float:
    ta = tokenizza(a)
    tb = tokenizza(b)

    if not ta or not tb:
        return 0.0

    return len(ta & tb) / len(ta | tb)


def taglia_testo(value: str, max_chars: int = 190) -> str:
    text = finalizza_frase(value)

    if len(text) <= max_chars:
        return text

    cut = text[:max_chars].rsplit(" ", 1)[0].strip()
    return finalizza_frase(cut)


def carica_kb(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Knowledge Base non trovata: {path}")

    kb = json.loads(path.read_text(encoding="utf-8"))

    required = [
        "titolo_documento",
        "tipo_documento",
        "chunk",
        "concetti",
        "parole_chiave",
        "frasi_importanti",
        "relazioni_tra_concetti",
        "output_generati",
        "controlli_qualita",
    ]

    missing = [field for field in required if field not in kb]
    if missing:
        raise ValueError(f"Knowledge Base incompleta. Campi mancanti: {missing}")

    quality = kb.get("controlli_qualita", {})
    if quality and quality.get("ok") is False:
        raise ValueError(f"Knowledge Base non valida: {quality.get('errori', [])}")

    return kb


def concetti_usabili(kb: dict[str, Any]) -> list[dict[str, Any]]:
    result = []

    for c in kb.get("concetti", []):
        titolo = normalizza_spazi(c.get("titolo", ""))
        descrizione = normalizza_spazi(c.get("descrizione", ""))
        frasi = c.get("frasi_origine", [])
        chunk = c.get("chunk_origine", "")

        if not titolo or len(titolo) < 3:
            continue

        if not descrizione or len(descrizione) < 35:
            continue

        if not frasi:
            continue

        if not chunk:
            continue

        result.append(c)

    result.sort(key=lambda item: float(item.get("peso", 0)), reverse=True)
    return result


def indice_concetti(kb: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        c.get("id"): c
        for c in kb.get("concetti", [])
        if c.get("id")
    }


def indice_relazioni(kb: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}

    for rel in kb.get("relazioni_tra_concetti", []):
        a = rel.get("da")
        b = rel.get("a")

        if a:
            result.setdefault(a, []).append(rel)

        if b:
            result.setdefault(b, []).append(rel)

    return result


def descrizione_concetto(c: dict[str, Any]) -> str:
    return taglia_testo(c.get("descrizione", ""), 190)


def titolo_concetto(c: dict[str, Any]) -> str:
    return normalizza_spazi(c.get("titolo", "concetto"))


def frase_origine(c: dict[str, Any]) -> str:
    frasi = c.get("frasi_origine", [])
    if isinstance(frasi, list) and frasi:
        return taglia_testo(frasi[0], 220)
    return descrizione_concetto(c)


def scegli_distrattori(target: dict[str, Any], concetti: list[dict[str, Any]], numero: int = 3) -> list[str]:
    corretta = descrizione_concetto(target)
    target_chunk = target.get("chunk_origine")
    target_text = " ".join([
        titolo_concetto(target),
        descrizione_concetto(target),
        " ".join(target.get("parole_chiave", [])),
    ])

    candidati = []

    for c in concetti:
        if c.get("id") == target.get("id"):
            continue

        opt = descrizione_concetto(c)

        if not opt:
            continue

        if opt.lower() == corretta.lower():
            continue

        sim = similarita(target_text, " ".join([
            titolo_concetto(c),
            descrizione_concetto(c),
            " ".join(c.get("parole_chiave", [])),
        ]))

        stessa_zona = 1 if c.get("chunk_origine") == target_chunk else 0

        # I distrattori migliori sono vicini al documento, ma non identici.
        if sim >= 0.95:
            continue

        candidati.append((stessa_zona, sim, opt))

    candidati.sort(key=lambda item: (item[0], item[1]), reverse=True)

    result = []
    seen = {corretta.lower()}

    for _, _, opt in candidati:
        key = opt.lower()
        if key in seen:
            continue

        seen.add(key)
        result.append(opt)

        if len(result) >= numero:
            break

    return result


def crea_domanda_test(target: dict[str, Any], concetti: list[dict[str, Any]], index: int) -> dict[str, Any] | None:
    titolo = titolo_concetto(target)
    corretta = descrizione_concetto(target)
    distrattori = scegli_distrattori(target, concetti, 3)

    if len(distrattori) < 3:
        return None

    opzioni = [corretta] + distrattori
    random.Random(3400 + index).shuffle(opzioni)

    domanda = f"Secondo la Knowledge Base, quale affermazione descrive correttamente «{titolo}»?"

    spiegazione = (
        f"La risposta corretta riprende una frase importante collegata al concetto «{titolo}». "
        f"Origine: {frase_origine(target)}"
    )

    return {
        "id": f"test-kb-{index}",
        "domanda": domanda,
        "opzioni": opzioni,
        "risposta_corretta": corretta,
        "spiegazione": finalizza_frase(spiegazione),
        "origine_kb": {
            "concept_id": target.get("id"),
            "chunk_id": target.get("chunk_origine"),
            "frase_origine": frase_origine(target),
            "parole_chiave": target.get("parole_chiave", []),
        },
    }


def trova_concetto_collegato(
    target: dict[str, Any],
    concept_by_id: dict[str, dict[str, Any]],
    rel_by_concept: dict[str, list[dict[str, Any]]],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    concept_id = target.get("id")

    for rel in rel_by_concept.get(concept_id, []):
        other_id = rel.get("a") if rel.get("da") == concept_id else rel.get("da")
        other = concept_by_id.get(other_id)

        if other and other.get("id") != concept_id:
            return other, rel

    return None, None


def crea_domanda_studio(
    target: dict[str, Any],
    concept_by_id: dict[str, dict[str, Any]],
    rel_by_concept: dict[str, list[dict[str, Any]]],
    index: int,
) -> dict[str, Any]:
    titolo = titolo_concetto(target)
    collegato, relazione = trova_concetto_collegato(target, concept_by_id, rel_by_concept)

    if collegato:
        titolo_altro = titolo_concetto(collegato)
        domanda = f"Come si collega «{titolo}» a «{titolo_altro}» nel documento?"

        motivo = normalizza_spazi(relazione.get("motivo", "collegamento concettuale")) if relazione else "collegamento concettuale"

        risposta = (
            f"Il documento collega «{titolo}» a «{titolo_altro}» attraverso un {motivo}. "
            f"Il primo punto dice: {descrizione_concetto(target)} "
            f"Il secondo punto dice: {descrizione_concetto(collegato)}"
        )

        origine = {
            "concept_id": target.get("id"),
            "concept_collegato_id": collegato.get("id"),
            "relation_id": relazione.get("id") if relazione else None,
            "chunk_id": target.get("chunk_origine"),
            "frase_origine": frase_origine(target),
        }
    else:
        domanda = f"Quale ruolo ha «{titolo}» nel documento?"

        risposta = (
            f"Nel documento «{titolo}» è un concetto rilevante perché viene spiegato così: "
            f"{descrizione_concetto(target)}"
        )

        origine = {
            "concept_id": target.get("id"),
            "concept_collegato_id": None,
            "relation_id": None,
            "chunk_id": target.get("chunk_origine"),
            "frase_origine": frase_origine(target),
        }

    return {
        "id": f"studio-kb-{index}",
        "domanda": normalizza_spazi(domanda),
        "risposta_guida": finalizza_frase(risposta),
        "origine_kb": origine,
    }


def valida_test(item: dict[str, Any], index: int) -> list[str]:
    problemi = []

    domanda = normalizza_spazi(item.get("domanda", ""))
    opzioni = item.get("opzioni", [])
    corretta = normalizza_spazi(item.get("risposta_corretta", ""))
    spiegazione = normalizza_spazi(item.get("spiegazione", ""))
    origine = item.get("origine_kb", {})

    if not domanda or len(domanda) < 30 or not domanda.endswith("?"):
        problemi.append(f"test {index}: domanda assente o non valida")

    if not isinstance(opzioni, list) or len(opzioni) != 4:
        problemi.append(f"test {index}: servono esattamente 4 opzioni")

    if corretta not in opzioni:
        problemi.append(f"test {index}: risposta corretta non presente nelle opzioni")

    normalized_options = [normalizza_spazi(o).lower() for o in opzioni]
    if len(set(normalized_options)) != len(normalized_options):
        problemi.append(f"test {index}: opzioni duplicate")

    if not spiegazione or len(spiegazione) < 50:
        problemi.append(f"test {index}: spiegazione troppo debole")

    if not origine.get("concept_id") or not origine.get("chunk_id"):
        problemi.append(f"test {index}: origine KB mancante")

    return problemi


def valida_studio(item: dict[str, Any], index: int) -> list[str]:
    problemi = []

    domanda = normalizza_spazi(item.get("domanda", ""))
    risposta = normalizza_spazi(item.get("risposta_guida", ""))
    origine = item.get("origine_kb", {})

    if not domanda or len(domanda) < 25 or not domanda.endswith("?"):
        problemi.append(f"studio {index}: domanda assente o non valida")

    if not risposta or len(risposta) < 70:
        problemi.append(f"studio {index}: risposta guida troppo debole")

    vietate = [
        "spiega il punto principale collegato a",
        "che cosa bisogna ricordare su documento",
        "concetto di documento",
    ]

    low = domanda.lower()
    for frase in vietate:
        if frase in low:
            problemi.append(f"studio {index}: frase generica vietata: {frase}")

    if ".." in risposta:
        problemi.append(f"studio {index}: doppio punto nella risposta")

    if not origine.get("concept_id") or not origine.get("chunk_id"):
        problemi.append(f"studio {index}: origine KB mancante")

    return problemi


def valida_output(test: list[dict[str, Any]], studio: list[dict[str, Any]]) -> dict[str, Any]:
    errori = []
    avvisi = []

    if len(test) < 3:
        errori.append("meno di 3 domande test generate")

    if len(studio) < 3:
        errori.append("meno di 3 domande studio generate")

    for index, item in enumerate(test, start=1):
        errori.extend(valida_test(item, index))

    for index, item in enumerate(studio, start=1):
        errori.extend(valida_studio(item, index))

    return {
        "ok": not errori,
        "errori": errori,
        "avvisi": avvisi,
        "test_generati": len(test),
        "domande_studio_generate": len(studio),
    }


def genera_da_kb(kb: dict[str, Any], numero: int) -> dict[str, Any]:
    concetti = concetti_usabili(kb)

    if len(concetti) < 4:
        raise ValueError("Knowledge Base troppo povera: servono almeno 4 concetti usabili.")

    concept_by_id = indice_concetti(kb)
    rel_by_concept = indice_relazioni(kb)

    selected = concetti[: max(numero, 3)]

    test = []
    studio = []

    for index, concept in enumerate(selected, start=1):
        q = crea_domanda_test(concept, concetti, index)
        if q:
            test.append(q)

        studio.append(crea_domanda_studio(concept, concept_by_id, rel_by_concept, index))

    test = test[:numero]
    studio = studio[:numero]

    qualita = valida_output(test, studio)

    output = {
        "versione": "rag-generatori-da-kb-v34c",
        "titolo_documento": kb.get("titolo_documento"),
        "tipo_documento": kb.get("tipo_documento"),
        "fonte": "knowledge_base_json",
        "test": test,
        "domande_studio": studio,
        "controlli_qualita": qualita,
    }

    return output


def scrivi_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def aggiorna_kb_con_output(kb: dict[str, Any], output: dict[str, Any]) -> dict[str, Any]:
    nuova = dict(kb)
    nuova["output_generati"] = dict(kb.get("output_generati", {}))
    nuova["output_generati"]["test"] = output.get("test", [])
    nuova["output_generati"]["domande_studio"] = output.get("domande_studio", [])

    nuova["controlli_qualita"] = dict(kb.get("controlli_qualita", {}))
    nuova["controlli_qualita"]["generatori_v34c"] = output.get("controlli_qualita", {})

    return nuova


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kb", required=True)
    parser.add_argument("--outdir", default="dist/generated/rag_generatori_da_kb_v34c")
    parser.add_argument("--numero", type=int, default=5)
    args = parser.parse_args()

    kb_path = Path(args.kb)
    outdir = ROOT / args.outdir if not Path(args.outdir).is_absolute() else Path(args.outdir)

    kb = carica_kb(kb_path)
    output = genera_da_kb(kb, args.numero)
    kb_con_output = aggiorna_kb_con_output(kb, output)

    scrivi_json(outdir / "rag_test_domande_studio_da_kb_v34c.json", output)
    scrivi_json(outdir / "knowledge_base_con_output_v34c.json", kb_con_output)

    qualita = output["controlli_qualita"]

    print("=== RAG GENERATORI DA KB V3.4C ===")
    print("KB:", kb_path)
    print("Outdir:", outdir)
    print("Titolo:", output["titolo_documento"])
    print("Tipo:", output["tipo_documento"])
    print("Test generati:", qualita["test_generati"])
    print("Domande studio generate:", qualita["domande_studio_generate"])
    print("Qualità OK:", qualita["ok"])

    if qualita["errori"]:
        print("ERRORI:")
        for e in qualita["errori"]:
            print("-", e)

    if qualita["avvisi"]:
        print("AVVISI:")
        for a in qualita["avvisi"]:
            print("-", a)

    return 0 if qualita["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
