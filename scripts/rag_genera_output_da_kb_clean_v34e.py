#!/usr/bin/env python3
"""
RAG Output Generator V3.4E

Genera materiale leggibile da Knowledge Base pulita V3.4D:
- riassunto
- card
- test
- domande studio

Regola: i titoli sono etichette didattiche brevi;
il testo completo resta nel corpo delle card, nelle opzioni e nelle risposte.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from rag_quality_gate_kb_v34d import applica_quality_gate, normalizza_spazi, finalizza_frase  # noqa: E402


STOPWORDS_TITOLO = {
    "della", "delle", "degli", "dello", "dalla", "dalle", "dagli",
    "alla", "alle", "agli", "nella", "nelle", "negli", "nello",
    "sulla", "sulle", "sugli", "con", "per", "tra", "fra",
    "che", "una", "uno", "gli", "le", "il", "lo", "la",
    "un", "di", "da", "in", "su", "e", "o", "ma", "anche",
    "come", "quando", "questo", "questa", "questi", "queste",
    "essere", "avere", "sono", "viene", "vengono", "deve",
    "devono", "può", "possono", "più", "meno", "molto",
    "documento", "testo", "punto", "punti",
}

VIETATI_VISIBILI = [
    "concept_id",
    "chunk_id",
    "origine_kb",
    "tracciabilita",
    "secondo la knowledge base",
    "risposta corretta:",
    "la risposta corretta è",
    "distrattore",
    "esempio di domanda",
    "rag/documenti",
    "scopo del documento",
    "questo documento è stato creato",
    "fonte di prova",
    "motore rag",
    "progetto quiz",
    "# documento",
    "perché «",
    "è importante nel documento",
    "che rapporto c",
]


def carica_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def scrivi_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def ripara_punteggiatura(value: str) -> str:
    text = normalizza_spazi(value)

    text = re.sub(r"\. ([a-zà-ÿ])", lambda m: "; " + m.group(1), text)
    text = text.replace(" ;", ";")
    text = text.replace(" ,", ",")
    text = text.replace(" .", ".")

    return normalizza_spazi(text)


def frase(value: str, max_chars: int = 270) -> str:
    text = ripara_punteggiatura(value)

    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0].strip()

    return finalizza_frase(text)


def senza_punto(value: str, max_chars: int = 140) -> str:
    text = ripara_punteggiatura(value).strip(" .!?")

    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0].strip(" .!?")

    return text


def parole_utili(value: str) -> list[str]:
    raw = re.findall(r"[A-Za-zÀ-ÿ0-9'’]{4,}", str(value or "").lower())
    result = []

    for token in raw:
        token = token.strip("'’")

        if not token:
            continue

        if token in STOPWORDS_TITOLO:
            continue

        if token in {
            "usare", "usato", "usata", "usati", "usate",
            "bisogna", "occorre", "necessario", "mantenere",
            "aggiornati", "aggiornare", "spiegato", "indica",
            "principali", "pratica", "regola",
        }:
            continue

        if token not in result:
            result.append(token)

    return result


def titolo_da_soggetto(text: str) -> str:
    match = re.match(
        r"^(La|Il|Le|Gli|I|Lo|L'|Un|Una)\s+(.+?)\s+"
        r"(è|sono|ha|hanno|deve|devono|prepara|aiuta|consente|permette|crea|creano|accompagna|collega|collegano)\b",
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        return ""

    candidate = normalizza_spazi(match.group(2)).strip(" .,:;")
    words = parole_utili(candidate)

    if words:
        title = " ".join(words[:4]).capitalize()
    else:
        title = candidate.capitalize()

    if len(title) <= 45 and len(title.split()) <= 5:
        return title

    return ""


def titolo_didattico(value: str, index: int) -> str:
    text = ripara_punteggiatura(value).strip(" .!?")
    low = text.lower()

    if "obiettiv" in low:
        return "Obiettivi principali"

    if "riduce" in low and "risch" in low:
        return "Riduzione del rischio"

    if "rischio" in low or "rischioso" in low:
        return "Rischio e conseguenza"

    if "regola" in low:
        return "Regola operativa"

    if low.startswith(("bisogna ", "occorre ", "è necessario ", "deve ", "devono ")):
        return "Azione consigliata"

    if low.startswith("quando "):
        return "Situazione da valutare"

    subject = titolo_da_soggetto(text)
    if subject:
        return subject

    words = parole_utili(text)
    if len(words) >= 2:
        title = " ".join(words[:3]).capitalize()
        if len(title) <= 45 and len(title.split()) <= 5:
            return title

    return f"Punto chiave {index}"


def concetti_puliti(kb: dict[str, Any]) -> list[dict[str, Any]]:
    gate = kb.get("quality_gate_v34d")

    if not gate:
        kb = applica_quality_gate(kb)
        gate = kb.get("quality_gate_v34d")

    if not gate or not gate.get("ok"):
        raise ValueError(f"Knowledge Base non approvata dal Quality Gate V3.4D: {gate}")

    result = []
    seen_texts = set()
    seen_titles = {}

    for c in kb.get("concetti", []):
        raw_text = normalizza_spazi(c.get("testo_utente") or c.get("descrizione") or "")
        clean_text = frase(raw_text, 270)

        if len(clean_text) < 45:
            continue

        if clean_text.lower() in seen_texts:
            continue

        base_title = titolo_didattico(clean_text, len(result) + 1)
        count = seen_titles.get(base_title.lower(), 0) + 1
        seen_titles[base_title.lower()] = count

        title = base_title if count == 1 else f"{base_title} {count}"

        item = dict(c)
        item["titolo_utente"] = title
        item["testo_utente"] = clean_text

        result.append(item)
        seen_texts.add(clean_text.lower())

    if len(result) < 4:
        raise ValueError("Servono almeno 4 concetti puliti per generare output serio.")

    return result



def pulisci_titolo_documento_visibile(value: str) -> str:
    title = normalizza_spazi(value or "Documento analizzato")
    title = title.strip(" -:.")

    import re
    title = re.sub(r"^Documento\s+RAG\s+di\s+test\s*:\s*", "", title, flags=re.IGNORECASE)
    title = re.sub(r"^Documento\s+di\s+test\s*:\s*", "", title, flags=re.IGNORECASE)
    title = re.sub(r"^Test\s*:\s*", "", title, flags=re.IGNORECASE)

    title = title.strip(" -:.")
    if not title:
        title = "Documento analizzato"

    return title[:1].upper() + title[1:]


def crea_riassunto(kb: dict[str, Any], concepts: list[dict[str, Any]]) -> dict[str, Any]:
    titolo_doc = pulisci_titolo_documento_visibile(kb.get("titolo_documento", "Documento analizzato"))
    tipo_doc = normalizza_spazi(kb.get("tipo_documento", "documento"))

    top = concepts[:5]
    punti = [{"titolo": c["titolo_utente"], "testo": c["testo_utente"]} for c in top]

    intro = (
        f"Il documento presenta {len(top)} punti principali e li organizza "
        "in contenuti utili per studio, ripasso e verifica."
    )

    sviluppo = " ".join(c["testo_utente"] for c in top[:3])

    conclusione = (
        "Il materiale generato mette in evidenza i concetti centrali, "
        "separando le etichette didattiche dal contenuto completo."
    )

    return {
        "titolo": f"Riassunto - {titolo_doc}",
        "tipo_documento": tipo_doc,
        "testo_breve": frase(intro + " " + sviluppo, 760),
        "punti_chiave": punti,
        "conclusione": conclusione,
    }


FINALI_DEBOLI_OUTPUT = {
    "e", "di", "da", "con", "per", "su", "tra", "fra",
    "della", "delle", "degli", "dello", "alla", "alle", "agli",
    "nella", "nelle", "negli", "sulla", "sulle", "dei", "del",
    "nel", "nei", "al", "ai",
}


def finisce_male_output(value: str) -> bool:
    text = normalizza_spazi(value).strip(" .!?;:,")
    if not text:
        return True

    last = text.split()[-1].lower().strip(" .!?;:,")
    return last in FINALI_DEBOLI_OUTPUT


def testo_completo_breve(value: str, max_chars: int = 220) -> str:
    text = ripara_punteggiatura(value).strip()

    if len(text) <= max_chars and not finisce_male_output(text):
        return frase(text, max_chars + 20)

    # Prima prova: frase o segmento completo.
    import re
    parts = re.split(r"(?<=[.!?])\s+|;\s+", text)

    for part in parts:
        candidate = normalizza_spazi(part).strip(" ;")
        if len(candidate) >= 24 and len(candidate) <= max_chars and not finisce_male_output(candidate):
            return frase(candidate, max_chars + 20)

    # Seconda prova: taglio a parole, ma mai su preposizioni/connettivi.
    words = text.split()
    selected = []

    for word in words:
        candidate = " ".join(selected + [word])
        if len(candidate) > max_chars:
            break
        selected.append(word)

    while selected and selected[-1].lower().strip(" .!?;:,") in FINALI_DEBOLI_OUTPUT:
        selected.pop()

    candidate = " ".join(selected).strip(" .!?;:,")

    if len(candidate) < 24:
        candidate = " ".join(words[: min(len(words), 12)]).strip(" .!?;:,")

    return frase(candidate, max_chars + 20)


def opzione_da_concetto(concept: dict[str, Any], variante: int) -> str:
    titolo = normalizza_spazi(concept.get("titolo_utente") or concept.get("titolo") or "Punto")
    testo = testo_completo_breve(concept.get("testo_utente") or concept.get("descrizione") or "", 175)

    templates = [
        "Concetto: {titolo}. {testo}",
        "Aspetto: {titolo}. {testo}",
        "Focus: {titolo}. {testo}",
        "Punto del documento: {titolo}. {testo}",
        "Informazione: {titolo}. {testo}",
        "Riepilogo: {titolo}. {testo}",
    ]

    template = templates[variante % len(templates)]
    return frase(template.format(titolo=titolo, testo=testo), 260)


def crea_card(concepts: list[dict[str, Any]], numero: int) -> list[dict[str, Any]]:
    cards = []

    for index, c in enumerate(concepts[:numero], start=1):
        titolo = c["titolo_utente"]
        testo = c["testo_utente"]
        chiave = testo_completo_breve(testo, 220)

        cards.append({
            "id": f"card-clean-v34e-{index}",
            "titolo": titolo,
            "testo": testo,
            "messaggio_chiave": f"Punto chiave: {chiave}",
            "fonte_visibile": "Fonte: sezione del documento.",
        })

    return cards

def similarita(a: str, b: str) -> float:
    wa = set(re.findall(r"[A-Za-zÀ-ÿ0-9'’]{4,}", a.lower()))
    wb = set(re.findall(r"[A-Za-zÀ-ÿ0-9'’]{4,}", b.lower()))

    if not wa or not wb:
        return 0.0

    return len(wa & wb) / len(wa | wb)



def scegli_distrattori(target: dict[str, Any], concepts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    target_text = target["titolo_utente"] + " " + target["testo_utente"]

    candidates = []

    for c in concepts:
        if c.get("id") == target.get("id"):
            continue

        sim = similarita(target_text, c["titolo_utente"] + " " + c["testo_utente"])

        if sim >= 0.92:
            continue

        candidates.append((sim, c))

    candidates.sort(key=lambda x: x[0], reverse=True)

    result = []
    seen = set()

    for _, concept in candidates:
        key = (concept.get("titolo_utente", "") + concept.get("testo_utente", "")).lower()
        if key in seen:
            continue

        seen.add(key)
        result.append(concept)

        if len(result) == 3:
            break

    return result


def crea_test(concepts: list[dict[str, Any]], numero: int) -> list[dict[str, Any]]:
    tests = []

    templates = [
        "Quale affermazione descrive meglio «{titolo}»?",
        "Quale frase è più coerente con «{titolo}»?",
        "Quale opzione riprende correttamente «{titolo}»?",
        "Quale risposta rappresenta meglio «{titolo}»?",
    ]

    for index, c in enumerate(concepts[:numero], start=1):
        titolo = c["titolo_utente"]
        distrattori = scegli_distrattori(c, concepts)

        if len(distrattori) < 3:
            continue

        # Variante diversa per ogni domanda:
        # così lo stesso concetto non ricompare identico come opzione in più domande.
        variante = index - 1

        corretta = opzione_da_concetto(c, variante)
        opzioni = [corretta] + [opzione_da_concetto(d, variante) for d in distrattori]

        # Mantiene opzioni distinte nella singola domanda.
        opzioni_uniche = []
        viste = set()
        for opt in opzioni:
            key = normalizza_spazi(opt).lower()
            if key in viste:
                continue
            viste.add(key)
            opzioni_uniche.append(opt)

        if len(opzioni_uniche) != 4:
            continue

        random.Random(7300 + index).shuffle(opzioni_uniche)

        domanda = templates[(index - 1) % len(templates)].format(titolo=titolo)

        tests.append({
            "id": f"test-clean-v34e-{index}",
            "domanda": domanda,
            "opzioni": opzioni_uniche,
            "risposta_corretta": corretta,
            "spiegazione": f"Il contenuto collegato a «{titolo}» dice: {c['testo_utente']}",
            "fonte_visibile": "Fonte: sezione del documento.",
        })

    return tests

def crea_domande_studio(concepts: list[dict[str, Any]], numero: int) -> list[dict[str, Any]]:
    result = []

    templates = [
        "Spiega in modo chiaro «{titolo}».",
        "Qual è l'informazione centrale di «{titolo}»?",
        "Come useresti «{titolo}» per ripassare il documento?",
        "Quale idea principale devi ricordare da «{titolo}»?",
    ]

    for index, c in enumerate(concepts[:numero], start=1):
        titolo = c["titolo_utente"]
        testo = c["testo_utente"]
        domanda = templates[(index - 1) % len(templates)].format(titolo=titolo)

        risposta = (
            f"{testo} "
            "Questo punto aiuta a riconoscere una informazione centrale del documento "
            "e a collegarla agli altri contenuti generati."
        )

        result.append({
            "id": f"studio-clean-v34e-{index}",
            "domanda": domanda,
            "risposta_guida": frase(risposta, 430),
            "fonte_visibile": "Documento analizzato.",
        })

    return result


def titoli_visibili(output: dict[str, Any]) -> list[str]:
    titles = []

    for card in output.get("card", []):
        titles.append(str(card.get("titolo", "")))

    for test in output.get("test", []):
        titles.extend(re.findall(r"«([^»]+)»", str(test.get("domanda", ""))))

    for studio in output.get("domande_studio", []):
        titles.extend(re.findall(r"«([^»]+)»", str(studio.get("domanda", ""))))

    return titles


def testi_visibili(output: dict[str, Any]) -> list[str]:
    fields = []

    riassunto = output.get("riassunto", {})
    fields.append(str(riassunto.get("titolo", "")))
    fields.append(str(riassunto.get("testo_breve", "")))
    fields.append(str(riassunto.get("conclusione", "")))

    for p in riassunto.get("punti_chiave", []):
        fields.append(str(p.get("titolo", "")))
        fields.append(str(p.get("testo", "")))

    for card in output.get("card", []):
        fields.append(str(card.get("titolo", "")))
        fields.append(str(card.get("testo", "")))
        fields.append(str(card.get("messaggio_chiave", "")))
        fields.append(str(card.get("fonte_visibile", "")))

    for test in output.get("test", []):
        fields.append(str(test.get("domanda", "")))
        fields.extend(str(x) for x in test.get("opzioni", []))
        fields.append(str(test.get("spiegazione", "")))
        fields.append(str(test.get("fonte_visibile", "")))

    for studio in output.get("domande_studio", []):
        fields.append(str(studio.get("domanda", "")))
        fields.append(str(studio.get("risposta_guida", "")))
        fields.append(str(studio.get("fonte_visibile", "")))

    return fields


def valida_output(output: dict[str, Any], numero: int) -> dict[str, Any]:
    errori = []
    avvisi = []

    if not output.get("riassunto", {}).get("testo_breve"):
        errori.append("riassunto mancante")

    if len(output.get("card", [])) < min(3, numero):
        errori.append("card insufficienti")

    if len(output.get("test", [])) < min(3, numero):
        errori.append("test insufficienti")

    if len(output.get("domande_studio", [])) < min(3, numero):
        errori.append("domande studio insufficienti")

    titles = titoli_visibili(output)

    # Lo stesso titolo può comparire correttamente in card, test e domande studio.
    # Il duplicato è un problema solo dentro la stessa sezione.
    card_titles = [str(c.get("titolo", "")).lower() for c in output.get("card", [])] if "output" in locals() else [str(c.get("titolo", "")).lower() for c in data.get("card", [])]
    if len(card_titles) != len(set(card_titles)):
        errori.append("titoli card duplicati")

    titoli_brutti = [
        "la sicurezza informatica è l'insieme",
        "una buona regola aziendale è attivare",
        "bisogna mantenere aggiornati anche",
        "stessa password siti rischioso",
        "mantenere aggiornati anche browser",
        "riduce rischio account venga",
    ]

    for title in titles:
        low_title = title.lower()

        if len(title) > 52 or len(title.split()) > 6:
            errori.append(f"titolo visibile troppo lungo: {title}")

        for banned in titoli_brutti:
            if banned in low_title:
                errori.append(f"titolo visibile brutto: {banned}")

    for field in testi_visibili(output):
        low = field.lower()

        for banned in VIETATI_VISIBILI:
            if banned in low:
                errori.append(f"testo visibile contiene vietato: {banned}")

        if ".." in field:
            errori.append("testo visibile contiene doppio punto")

        if ". garantire" in low or ". mantenere" in low:
            errori.append("punteggiatura lista spezzata male")

        if len(field) > 620:
            avvisi.append("testo visibile lungo")

    for idx, item in enumerate(output.get("test", []), start=1):
        opzioni = item.get("opzioni", [])
        corretta = item.get("risposta_corretta")

        if len(opzioni) != 4:
            errori.append(f"test {idx}: opzioni diverse da 4")

        if corretta not in opzioni:
            errori.append(f"test {idx}: risposta corretta assente dalle opzioni")

        if len(set(opzioni)) != len(opzioni):
            errori.append(f"test {idx}: opzioni duplicate")

    return {
        "ok": not errori,
        "errori": errori,
        "avvisi": avvisi,
        "riassunto": bool(output.get("riassunto")),
        "card": len(output.get("card", [])),
        "test": len(output.get("test", [])),
        "domande_studio": len(output.get("domande_studio", [])),
    }


def genera(kb_raw: dict[str, Any], numero: int) -> dict[str, Any]:
    kb_clean = applica_quality_gate(kb_raw)
    concepts = concetti_puliti(kb_clean)

    output = {
        "versione": "rag-output-kb-clean-v34e",
        "fonte": "knowledge_base_clean_v34d",
        "titolo_documento": kb_clean.get("titolo_documento"),
        "tipo_documento": kb_clean.get("tipo_documento"),
        "riassunto": crea_riassunto(kb_clean, concepts),
        "card": crea_card(concepts, numero),
        "test": crea_test(concepts, numero),
        "domande_studio": crea_domande_studio(concepts, numero),
        "quality_gate_v34d": kb_clean.get("quality_gate_v34d"),
    }

    output["controlli_qualita"] = valida_output(output, numero)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kb", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--numero", type=int, default=5)
    args = parser.parse_args()

    kb_path = Path(args.kb)
    outdir = Path(args.outdir)

    kb = carica_json(kb_path)
    output = genera(kb, args.numero)

    scrivi_json(outdir / "rag_output_kb_clean_v34e.json", output)

    q = output["controlli_qualita"]

    print("=== RAG OUTPUT DA KB CLEAN V3.4E ===")
    print("KB:", kb_path)
    print("Outdir:", outdir)
    print("Riassunto:", q["riassunto"])
    print("Card:", q["card"])
    print("Test:", q["test"])
    print("Domande studio:", q["domande_studio"])
    print("Qualità OK:", q["ok"])

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
