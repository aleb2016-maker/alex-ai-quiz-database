#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "validatore_rag_distrattori_forti_v2.md"

STOPWORDS = {
    "che", "con", "del", "della", "dello", "dei", "degli", "delle", "per", "tra", "fra",
    "una", "uno", "gli", "alla", "alle", "allo", "sul", "sulla", "sulle", "nel", "nella",
    "nelle", "come", "cosa", "quando", "quale", "quali", "questo", "questa", "questi",
    "queste", "sono", "essere", "viene", "può", "più", "meno", "solo"
}

GENERICI = {
    "sempre", "mai", "tutto", "tutti", "nessuno", "qualsiasi", "automaticamente",
    "garantisce", "elimina completamente", "risolve sempre", "senza eccezioni",
    "in ogni caso", "al 100%"
}


def normalizza_testo(value):
    return re.sub(r"\s+", " ", str(value or "").strip())


def tokens(value):
    parole = re.findall(r"[a-zàèéìòù0-9]{4,}", normalizza_testo(value).lower())
    return {p for p in parole if p not in STOPWORDS}


def estrai_domande(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("domande", "questions", "quiz", "items"):
            if isinstance(data.get(key), list):
                return data[key]
    return []


def estrai_opzioni(domanda):
    raw = domanda.get("opzioni") or domanda.get("risposte") or domanda.get("answers") or []
    if isinstance(raw, dict):
        return [normalizza_testo(v) for _, v in sorted(raw.items())]
    if isinstance(raw, list):
        return [normalizza_testo(v) for v in raw]
    return []


def valuta_domanda(domanda, indice):
    warnings = []
    testo_domanda = normalizza_testo(domanda.get("domanda") or domanda.get("question") or domanda.get("testo"))
    corretta = normalizza_testo(domanda.get("risposta_corretta") or domanda.get("correct_answer") or domanda.get("corretta"))
    opzioni = estrai_opzioni(domanda)
    codice = domanda.get("id") or domanda.get("codice") or f"domanda_{indice}"

    if len(opzioni) != 4:
        warnings.append("la domanda non ha esattamente 4 opzioni")

    if corretta and corretta not in opzioni:
        warnings.append("la risposta corretta non è presente tra le opzioni")

    if len(set(opzioni)) != len(opzioni):
        warnings.append("ci sono opzioni duplicate")

    distrattori = [o for o in opzioni if o != corretta]

    if len(distrattori) != 3:
        warnings.append("non risultano 3 distrattori")

    token_domanda = tokens(testo_domanda)
    token_corretta = tokens(corretta)
    ancora = token_corretta or token_domanda
    lunghezza_corretta = max(len(corretta), 1)

    for numero, distrattore in enumerate(distrattori, start=1):
        lower = distrattore.lower()
        rapporto_lunghezza = len(distrattore) / lunghezza_corretta
        overlap_core = len(tokens(distrattore) & ancora)
        overlap_domanda = len(tokens(distrattore) & token_domanda)

        if len(distrattore) < 18:
            warnings.append(f"distrattore {numero} troppo corto")

        if rapporto_lunghezza < 0.55 or rapporto_lunghezza > 1.80:
            warnings.append(f"distrattore {numero} troppo diverso per lunghezza dalla risposta corretta")

        if overlap_core == 0 and overlap_domanda == 0:
            warnings.append(f"distrattore {numero} sembra fuori tema rispetto a domanda/risposta corretta")

        if any(termine in lower for termine in GENERICI):
            warnings.append(f"distrattore {numero} contiene formulazioni troppo assolute o generiche")

    return codice, warnings


def main():
    if len(sys.argv) > 1:
        input_path = Path(sys.argv[1])
        if not input_path.is_absolute():
            input_path = ROOT / input_path
    else:
        possibili = [
            ROOT / "review" / "rag" / "quiz_da_revisionare.json",
            ROOT / "dist" / "generated" / "rag_quiz_generato.json",
        ]
        input_path = next((p for p in possibili if p.exists()), None)

    if not input_path or not input_path.exists():
        raise SystemExit("Nessun file RAG da validare trovato. Passa un percorso JSON come argomento.")

    data = json.loads(input_path.read_text(encoding="utf-8"))
    domande = estrai_domande(data)

    try:
        nome_file = input_path.relative_to(ROOT)
    except ValueError:
        nome_file = input_path

    righe = [
        "# Validatore RAG distrattori forti v2",
        "",
        f"File analizzato: `{nome_file}`",
        f"Domande trovate: {len(domande)}",
        ""
    ]

    totale_warning = 0

    for i, domanda in enumerate(domande, start=1):
        codice, warnings = valuta_domanda(domanda, i)

        if warnings:
            totale_warning += len(warnings)
            righe.append(f"## {codice}")

            for warning in warnings:
                righe.append(f"- {warning}")

            righe.append("")

    if totale_warning == 0:
        righe.append("✅ Nessun avviso: i distrattori risultano tecnicamente coerenti con le regole base.")
    else:
        righe.append(f"⚠️ Avvisi totali: {totale_warning}")
        righe.append("")
        righe.append(
            "Nota: questo controllo non sostituisce la revisione umana, "
            "ma segnala le opzioni probabilmente troppo deboli, fuori tema o troppo diverse dalla risposta corretta."
        )

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(righe) + "\n", encoding="utf-8")

    print(f"📌 Report: {REPORT.relative_to(ROOT)}")

    if totale_warning:
        print(f"⚠️ Avvisi trovati: {totale_warning}")
    else:
        print("✅ Distrattori RAG senza avvisi tecnici")


if __name__ == "__main__":
    main()
