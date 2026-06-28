#!/usr/bin/env python3
"""
RAG Cleaner Finale Universale V3.5K

Scopo:
- NON corregge singole frasi viste nei test.
- Applica regole generali a tutti i campi visibili finali.
- Funziona su riassunto, card, domande studio, test, completo e futuri output web/PDF/app
  che usano la stessa struttura JSON.

Cosa fa:
1. Normalizza punteggiatura e spazi.
2. Chiude correttamente frasi e domande.
3. Blocca/corregge frasi tagliate con finali sospetti.
4. Corregge contrazioni italiane generali: "di il" -> "del", "a il" -> "al", ecc.
5. Evita pronomi fragili generali: "senza copiarlo" -> "senza copiare il testo".
6. Evita strutture fragili: "«X» viene presentato/presentata..." -> formula neutra.
7. Corregge accordi generali dei plurali con "è" quando preceduti da articolo plurale.
8. Capitalizza opzioni quiz visibili.
9. Riallinea risposta corretta visibile, opzioni visibili e mappa opzioni.
10. Registra copertura campo per campo e fallisce se una sezione visibile non passa dal cleaner.
"""

from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

CONTROL_KEY = "cleaner_finale_universale_v35k"
CONTROL_NAME = "Controllo finale universale testi visibili"

SUSPICIOUS_FINAL_WORDS = {
    "e", "o", "ma", "che", "di", "a", "da", "in", "con", "su", "per", "tra", "fra",
    "del", "della", "dello", "dei", "degli", "delle", "il", "lo", "la", "gli", "le",
    "un", "una", "uno", "come", "quando", "dove", "perché", "poiché", "quindi",
}

VISIBLE_FIELD_SPEC = [
    "riassunto.titolo",
    "riassunto.testo_breve",
    "riassunto.conclusione",
    "riassunto.punti_chiave[].titolo",
    "riassunto.punti_chiave[].testo",
    "card[].titolo",
    "card[].testo",
    "card[].messaggio_chiave",
    "domande_studio[].domanda",
    "domande_studio[].risposta_guida",
    "test[].domanda_visibile",
    "test[].opzioni_visibili[]",
    "test[].risposta_corretta_visibile",
    "test[].spiegazione",
    "test[].mappa_opzioni_v35d[].opzione_visibile",
]

CONTRACTIONS = [
    (r"\bdi\s+il\b", "del"),
    (r"\bdi\s+lo\b", "dello"),
    (r"\bdi\s+la\b", "della"),
    (r"\bdi\s+i\b", "dei"),
    (r"\bdi\s+gli\b", "degli"),
    (r"\bdi\s+le\b", "delle"),
    (r"\ba\s+il\b", "al"),
    (r"\ba\s+lo\b", "allo"),
    (r"\ba\s+la\b", "alla"),
    (r"\ba\s+i\b", "ai"),
    (r"\ba\s+gli\b", "agli"),
    (r"\ba\s+le\b", "alle"),
    (r"\bda\s+il\b", "dal"),
    (r"\bda\s+lo\b", "dallo"),
    (r"\bda\s+la\b", "dalla"),
    (r"\bda\s+i\b", "dai"),
    (r"\bda\s+gli\b", "dagli"),
    (r"\bda\s+le\b", "dalle"),
    (r"\bin\s+il\b", "nel"),
    (r"\bin\s+lo\b", "nello"),
    (r"\bin\s+la\b", "nella"),
    (r"\bin\s+i\b", "nei"),
    (r"\bin\s+gli\b", "negli"),
    (r"\bin\s+le\b", "nelle"),
    (r"\bsu\s+il\b", "sul"),
    (r"\bsu\s+lo\b", "sullo"),
    (r"\bsu\s+la\b", "sulla"),
    (r"\bsu\s+i\b", "sui"),
    (r"\bsu\s+gli\b", "sugli"),
    (r"\bsu\s+le\b", "sulle"),
]


def normalize_spaces(text: str) -> str:
    text = str(text or "")
    text = text.replace("\u00a0", " ")
    text = text.replace("’", "'")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([,.;:!?])([^\s»”\")\]])", r"\1 \2", text)
    text = re.sub(r"\s+»,", "»,", text)
    return text.strip()


def normalize_punctuation(text: str) -> str:
    text = normalize_spaces(text)
    text = re.sub(r"\?\s*\?+", "?", text)
    text = re.sub(r"!\s*!+", "!", text)
    text = re.sub(r"\.\s*\.\s*\.+", ".", text)
    text = text.replace(",.", ".").replace(";.", ".").replace(":.", ".")
    text = text.replace(",?", "?").replace(";?", "?").replace(":?", "?")
    text = text.replace(".!", "!").replace(".?", "?").replace("?.", "?").replace("!.", "!")
    text = re.sub(r"[,;:]\s*$", ".", text)
    text = normalize_spaces(text)
    return text


def apply_contractions(text: str) -> str:
    text = normalize_punctuation(text)
    for pattern, replacement in CONTRACTIONS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return normalize_spaces(text)


def remove_fragile_pronouns(text: str) -> str:
    text = apply_contractions(text)

    # Regola generale: evita il pronome oggetto quando il referente può cambiare genere/numero.
    text = re.sub(r"\bsenza\s+copiar(?:lo|la|li|le)\b", "senza copiare il testo", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(e|poi|quindi)\s+(?:lo|la|li|le)\s+collega\b", r"\1 collega il concetto", text, flags=re.IGNORECASE)
    text = re.sub(r"\bche\s+(?:lo|la|li|le)\s+collega\b", "che collega il concetto", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(?:lo|la|li|le)\s+collega\b", "collega il concetto", text, flags=re.IGNORECASE)

    return normalize_spaces(text)


def neutralize_fragile_constructs(text: str) -> str:
    text = remove_fragile_pronouns(text)

    # Evita accordi con il titolo fra virgolette: usa una formula neutra.
    text = re.sub(
        r"«([^»]+)»\s+viene\s+presentat[oaie]\s+come",
        r"Il contenuto su «\1» viene descritto come",
        text,
        flags=re.IGNORECASE,
    )

    # Evita accordi plurali sbagliati con articolo plurale + è.
    # Esempio generale: "gli obiettivi principali è" -> "gli obiettivi principali sono".
    plural_subject = r"\b(gli|i|le)\s+([A-Za-zÀ-ÖØ-öø-ÿ0-9'\-]+(?:\s+[A-Za-zÀ-ÖØ-öø-ÿ0-9'\-]+){0,5})\s+è\b"
    text = re.sub(plural_subject, lambda m: f"{m.group(1)} {m.group(2)} sono", text, flags=re.IGNORECASE)

    # Accordi generali molto frequenti con participio dopo articolo.
    text = re.sub(r"\b(la|questa)\s+([^,.!?]{2,80})\s+viene\s+spiegato\b", r"\1 \2 viene spiegata", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(gli|i)\s+([^,.!?]{2,80})\s+viene\s+spiegato\b", r"\1 \2 vengono spiegati", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(le)\s+([^,.!?]{2,80})\s+viene\s+spiegato\b", r"\1 \2 vengono spiegate", text, flags=re.IGNORECASE)

    return normalize_punctuation(text)


def trim_suspicious_final(text: str) -> str:
    text = neutralize_fragile_constructs(text)
    if not text:
        return ""

    # Se termina con parola sospetta, la rimuove una volta. Se rimane ancora sospetta, valida fallirà.
    words = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ']+", " ", text).strip().split()
    if words and words[-1].lower() in SUSPICIOUS_FINAL_WORDS:
        parts = text.split()
        text = " ".join(parts[:-1]).rstrip(" ,;:.")

    text = normalize_punctuation(text)
    return text


def clean_text(value: Any, *, question: bool = False, option: bool = False) -> Any:
    if not isinstance(value, str):
        return value

    text = trim_suspicious_final(value)
    if not text:
        return ""

    if question:
        text = text.rstrip(" .!?") + "?"
    elif text[-1] not in ".!?»”":
        text += "."

    text = normalize_punctuation(text)

    if option:
        text = capitalize_first_alpha(text)

    return text


def capitalize_first_alpha(text: str) -> str:
    text = normalize_punctuation(text)
    for idx, ch in enumerate(text):
        if ch.isalpha():
            return text[:idx] + ch.upper() + text[idx + 1:]
    return text


def mark(coverage: dict[str, int], field_name: str) -> None:
    coverage[field_name] = coverage.get(field_name, 0) + 1


def clean_dict_field(obj: dict[str, Any], key: str, field_name: str, coverage: dict[str, int], *, question: bool = False, option: bool = False) -> None:
    if isinstance(obj.get(key), str):
        obj[key] = clean_text(obj[key], question=question, option=option)
        mark(coverage, field_name)


def clean_output(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int]]:
    cleaned = deepcopy(data)
    coverage: dict[str, int] = {}

    summary = cleaned.get("riassunto")
    if isinstance(summary, dict):
        clean_dict_field(summary, "titolo", "riassunto.titolo", coverage)
        clean_dict_field(summary, "testo_breve", "riassunto.testo_breve", coverage)
        clean_dict_field(summary, "conclusione", "riassunto.conclusione", coverage)
        for point in summary.get("punti_chiave", []) or []:
            if isinstance(point, dict):
                clean_dict_field(point, "titolo", "riassunto.punti_chiave[].titolo", coverage)
                clean_dict_field(point, "testo", "riassunto.punti_chiave[].testo", coverage)

    for card in cleaned.get("card", []) or []:
        if isinstance(card, dict):
            clean_dict_field(card, "titolo", "card[].titolo", coverage)
            clean_dict_field(card, "testo", "card[].testo", coverage)
            clean_dict_field(card, "messaggio_chiave", "card[].messaggio_chiave", coverage)

    for item in cleaned.get("domande_studio", []) or []:
        if isinstance(item, dict):
            clean_dict_field(item, "domanda", "domande_studio[].domanda", coverage, question=True)
            clean_dict_field(item, "risposta_guida", "domande_studio[].risposta_guida", coverage)

    for item in cleaned.get("test", []) or []:
        if not isinstance(item, dict):
            continue

        clean_dict_field(item, "domanda_visibile", "test[].domanda_visibile", coverage, question=True)
        clean_dict_field(item, "spiegazione", "test[].spiegazione", coverage)

        old_options = item.get("opzioni_visibili", []) or []
        option_map: dict[str, str] = {}
        new_options: list[Any] = []
        for option in old_options:
            if isinstance(option, str):
                new_option = clean_text(option, option=True)
                option_map[option] = new_option
                new_options.append(new_option)
                mark(coverage, "test[].opzioni_visibili[]")
            else:
                new_options.append(option)
        if new_options:
            item["opzioni_visibili"] = new_options

        if isinstance(item.get("risposta_corretta_visibile"), str):
            old_correct = item["risposta_corretta_visibile"]
            item["risposta_corretta_visibile"] = option_map.get(old_correct, clean_text(old_correct, option=True))
            mark(coverage, "test[].risposta_corretta_visibile")

        for row in item.get("mappa_opzioni_v35d", []) or []:
            if isinstance(row, dict) and isinstance(row.get("opzione_visibile"), str):
                old_visible = row["opzione_visibile"]
                row["opzione_visibile"] = option_map.get(old_visible, clean_text(old_visible, option=True))
                mark(coverage, "test[].mappa_opzioni_v35d[].opzione_visibile")

        # Riallinea la risposta corretta visibile alla mappa se necessario.
        options = item.get("opzioni_visibili", []) or []
        correct = item.get("risposta_corretta_visibile", "")
        if correct not in options:
            for row in item.get("mappa_opzioni_v35d", []) or []:
                if isinstance(row, dict) and row.get("corretta") and row.get("opzione_visibile") in options:
                    item["risposta_corretta_visibile"] = row["opzione_visibile"]
                    break

    quality = validate_output(cleaned, coverage)
    controls = dict(cleaned.get("controlli_qualita", {}))
    controls[CONTROL_KEY] = quality

    # Il controllo V3.5J precedente può essere diventato obsoleto dopo la pulizia finale.
    # Lo riallineiamo al gate universale per evitare qualità finale NO con errori già rimossi.
    if isinstance(controls.get("accordo_pronomi_v35j"), dict):
        controls["accordo_pronomi_v35j"] = dict(controls["accordo_pronomi_v35j"])
        controls["accordo_pronomi_v35j"]["ok"] = quality["ok"]
        controls["accordo_pronomi_v35j"]["errori"] = list(quality["errori"])
        controls["accordo_pronomi_v35j"]["riallineato_da"] = CONTROL_KEY

    # La qualità finale considera i controlli strutturali già presenti + il gate universale.
    controls["ok"] = bool(controls.get("qualita_testuale_v35g", {}).get("ok", True)) \
        and bool(controls.get("naturalezza_antikeyword_v35i", {}).get("ok", True)) \
        and bool(quality["ok"])
    cleaned["controlli_qualita"] = controls

    cleaned["revisione_cleaner_finale_universale_v35k"] = {
        "ok": quality["ok"],
        "nome": CONTROL_NAME,
        "copre": [
            "tutti_i_campi_visibili",
            "punteggiatura_sporca",
            "domande_chiuse_bene",
            "frasi_tagliate",
            "finali_sospetti",
            "contrazioni_italiane",
            "pronomi_fragili",
            "accordi_plurali_generali",
            "opzioni_quiz_visibili",
            "risposta_corretta_visibile_allineata",
            "mappa_opzioni_visibile_allineata",
            "riutilizzabile_per_web_pdf_app",
        ],
    }

    return cleaned, coverage


def visible_texts(data: dict[str, Any]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []

    summary = data.get("riassunto")
    if isinstance(summary, dict):
        for key in ["titolo", "testo_breve", "conclusione"]:
            if isinstance(summary.get(key), str):
                out.append((f"riassunto.{key}", summary[key]))
        for idx, point in enumerate(summary.get("punti_chiave", []) or [], start=1):
            if isinstance(point, dict):
                for key in ["titolo", "testo"]:
                    if isinstance(point.get(key), str):
                        out.append((f"riassunto.punti_chiave[{idx}].{key}", point[key]))

    for idx, card in enumerate(data.get("card", []) or [], start=1):
        if isinstance(card, dict):
            for key in ["titolo", "testo", "messaggio_chiave"]:
                if isinstance(card.get(key), str):
                    out.append((f"card[{idx}].{key}", card[key]))

    for idx, item in enumerate(data.get("domande_studio", []) or [], start=1):
        if isinstance(item, dict):
            for key in ["domanda", "risposta_guida"]:
                if isinstance(item.get(key), str):
                    out.append((f"domande_studio[{idx}].{key}", item[key]))

    for idx, item in enumerate(data.get("test", []) or [], start=1):
        if isinstance(item, dict):
            for key in ["domanda_visibile", "risposta_corretta_visibile", "spiegazione"]:
                if isinstance(item.get(key), str):
                    out.append((f"test[{idx}].{key}", item[key]))
            for opt_idx, opt in enumerate(item.get("opzioni_visibili", []) or [], start=1):
                if isinstance(opt, str):
                    out.append((f"test[{idx}].opzioni_visibili[{opt_idx}]", opt))
            for map_idx, row in enumerate(item.get("mappa_opzioni_v35d", []) or [], start=1):
                if isinstance(row, dict) and isinstance(row.get("opzione_visibile"), str):
                    out.append((f"test[{idx}].mappa_opzioni_v35d[{map_idx}].opzione_visibile", row["opzione_visibile"]))

    return out


def validate_output(data: dict[str, Any], coverage: dict[str, int]) -> dict[str, Any]:
    errors: list[str] = []
    texts = visible_texts(data)

    # Copertura: se una sezione esiste, i suoi campi visibili devono essere passati dal cleaner.
    if isinstance(data.get("riassunto"), dict):
        for field in ["riassunto.titolo", "riassunto.testo_breve", "riassunto.conclusione"]:
            if field not in coverage:
                errors.append(f"campo visibile non pulito: {field}")
    if data.get("card"):
        for field in ["card[].titolo", "card[].testo", "card[].messaggio_chiave"]:
            if field not in coverage:
                errors.append(f"campo visibile non pulito: {field}")
    if data.get("domande_studio"):
        for field in ["domande_studio[].domanda", "domande_studio[].risposta_guida"]:
            if field not in coverage:
                errors.append(f"campo visibile non pulito: {field}")
    if data.get("test"):
        for field in ["test[].domanda_visibile", "test[].opzioni_visibili[]", "test[].risposta_corretta_visibile", "test[].spiegazione"]:
            if field not in coverage:
                errors.append(f"campo visibile non pulito: {field}")

    for field, text in texts:
        if re.search(r"\?\s*\?+", text):
            errors.append(f"{field}: doppio punto interrogativo")
        if re.search(r"[,;:]\s*[.!?]", text):
            errors.append(f"{field}: punteggiatura sporca")
        if re.search(r"\b(?:di|a|da|in|su)\s+(?:il|lo|la|i|gli|le)\b", text, flags=re.IGNORECASE):
            errors.append(f"{field}: contrazione italiana non risolta")
        if re.search(r"\b(?:copiarlo|copiarla|copiarli|copiarle)\b", text, flags=re.IGNORECASE):
            errors.append(f"{field}: pronome fragile dopo copiare")
        if re.search(r"\b(?:lo|la|li|le)\s+collega\b", text, flags=re.IGNORECASE):
            errors.append(f"{field}: pronome fragile con collega")
        if re.search(r"«[^»]+»\s+viene\s+presentat[oaie]\s+come", text, flags=re.IGNORECASE):
            errors.append(f"{field}: accordo fragile con titolo tra virgolette")
        if re.search(r"\b(?:gli|i|le)\s+[A-Za-zÀ-ÖØ-öø-ÿ0-9'\-]+(?:\s+[A-Za-zÀ-ÖØ-öø-ÿ0-9'\-]+){0,5}\s+è\b", text, flags=re.IGNORECASE):
            errors.append(f"{field}: plurale con verbo singolare")

        stripped = text.strip()
        if stripped:
            words = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ']+", " ", stripped).strip().split()
            if words and words[-1].lower() in SUSPICIOUS_FINAL_WORDS:
                errors.append(f"{field}: finale sospetto -> {words[-1]}")
            if stripped[-1] in ",;:":
                errors.append(f"{field}: frase termina con punteggiatura sospesa")

    for idx, item in enumerate(data.get("test", []) or [], start=1):
        if not isinstance(item, dict):
            continue
        options = item.get("opzioni_visibili", []) or []
        correct = item.get("risposta_corretta_visibile", "")
        if len(options) != 4:
            errors.append(f"test[{idx}]: numero opzioni visibili diverso da 4")
        if len(set(options)) != len(options):
            errors.append(f"test[{idx}]: opzioni visibili duplicate")
        if correct not in options:
            errors.append(f"test[{idx}]: risposta corretta visibile assente dalle opzioni")
        for opt_idx, opt in enumerate(options, start=1):
            if isinstance(opt, str):
                first_alpha = next((ch for ch in opt if ch.isalpha()), "")
                if first_alpha and first_alpha.islower():
                    errors.append(f"test[{idx}].opzione[{opt_idx}]: iniziale minuscola")

    return {
        "ok": not errors,
        "errori": errors,
        "testi_controllati": len(texts),
        "campi_puliti": coverage,
        "nome_controllo": CONTROL_NAME,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    data = json.loads(input_path.read_text(encoding="utf-8"))
    cleaned, _coverage = clean_output(data)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")

    quality = cleaned.get("controlli_qualita", {}).get(CONTROL_KEY, {})

    print("=== RAG CLEANER FINALE UNIVERSALE V3.5K ===")
    print("Input:", input_path)
    print("Output:", output_path)
    print("OK:", quality.get("ok"))
    print("Testi controllati:", quality.get("testi_controllati"))
    print("Errori:", len(quality.get("errori", [])))

    for error in quality.get("errori", []):
        print("-", error)

    return 0 if quality.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
