from pathlib import Path
import shutil
import sys

TARGET_FILE = Path("backend/motori_scrittura.py")
REQUIRED_MARKER = "FASE 5 — QUALITY SUMMARY CARDS V1"
PATCH_MARKER = "FASE 5.1 — MICRO CONCEPTS CARDS QUALITY PATCH"

PATCH_CODE = r'''

# =============================================================================
# FASE 5.1 — MICRO CONCEPTS CARDS QUALITY PATCH
#
# Micro-patch solo Fase 5.
# Migliora:
# - micro_concetti brutti tipo "accessi limita", "credenziali non"
# - titoli card troppo ripetitivi
#
# Non modifica Fasi 1–4.
# Non tocca UI/CSS/pulsanti/layout.
# =============================================================================


def q5_bad_micro_concept_boundary_tokens() -> set:
    return {
        "non",
        "deve",
        "devono",
        "essere",
        "può",
        "possono",
        "limita",
        "limitano",
        "riduce",
        "riducono",
        "aumenta",
        "aumentano",
        "evita",
        "evitano",
        "condivide",
        "condividono",
        "condivise",
        "condivisi",
        "associato",
        "associata",
        "mantengano",
        "mantiene",
        "mantenere",
        "utilizzo",
    }


def q5_domain_micro_concepts_from_text(text: str) -> List[str]:
    concepts: List[str] = []

    try:
        lowered = q5_safe_text(text).lower()

        if "controllo degli accessi" in lowered or "controllo accessi" in lowered:
            concepts.append("controllo accessi")

        if "sistemi interni" in lowered:
            concepts.append("sistemi interni")

        if "account" in lowered:
            concepts.append("account utente")

        if "persona identificabile" in lowered:
            concepts.append("persona identificabile")

        if "credenzial" in lowered:
            concepts.append("protezione credenziali")

        if "non devono essere condivise" in lowered or "non deve essere condivisa" in lowered:
            concepts.append("condivisione credenziali")

        if "revisione periodica" in lowered:
            concepts.append("revisione periodica")

        if "riduce il rischio" in lowered or "rischio" in lowered:
            concepts.append("riduzione rischio")

        if "permessi attivi" in lowered:
            concepts.append("permessi attivi")

        if "utenti autorizzati" in lowered or "non più autorizzati" in lowered:
            concepts.append("utenti autorizzati")

        return q5_unique_strings(concepts)

    except Exception:
        return q5_unique_strings(concepts)


def q5_is_valid_micro_concept(concept: str) -> bool:
    try:
        clean = q5_safe_text(concept).lower().strip()
        clean = re.sub(r"\s+", " ", clean)

        if not clean:
            return False

        words = clean.split()

        if len(words) < 2 or len(words) > 3:
            return False

        stops = q5_stopwords()
        bad_boundary = q5_bad_micro_concept_boundary_tokens()

        if words[0] in stops or words[-1] in stops:
            return False

        if words[0] in bad_boundary or words[-1] in bad_boundary:
            return False

        if any(word in {"non", "deve", "devono", "essere"} for word in words):
            return False

        if all(word in stops for word in words):
            return False

        if len(clean) < 6:
            return False

        if len(words) == 2 and words[1] in bad_boundary:
            return False

        if " non" in clean or clean.endswith(" non"):
            return False

        return True

    except Exception:
        return False


def q5_generate_micro_concepts_from_text(text: str, limit: int = 6) -> List[str]:
    concepts: List[str] = []

    try:
        clean_text = q5_fix_italian_typography(text)
        concepts.extend(q5_domain_micro_concepts_from_text(clean_text))

        tokens = q5_word_tokens(clean_text)
        stops = q5_stopwords()
        bad_boundary = q5_bad_micro_concept_boundary_tokens()

        candidates: List[str] = []

        for size in (2, 3):
            for index in range(0, max(0, len(tokens) - size + 1)):
                gram = tokens[index:index + size]

                if not gram:
                    continue

                if gram[0] in stops or gram[-1] in stops:
                    continue

                if gram[0] in bad_boundary or gram[-1] in bad_boundary:
                    continue

                if any(token in {"non", "deve", "devono", "essere"} for token in gram):
                    continue

                candidate = " ".join(gram)

                if q5_is_valid_micro_concept(candidate):
                    candidates.append(candidate)

        concepts.extend(candidates)

        return q5_unique_strings(concepts)[:limit]

    except Exception:
        return q5_unique_strings(concepts)[:limit]


def q5_select_micro_concepts(
    preferred_concepts: List[str],
    text: str,
    limit: int = 6,
) -> List[str]:
    try:
        selected: List[str] = []

        selected.extend(q5_domain_micro_concepts_from_text(text))

        for concept in preferred_concepts:
            clean = q5_fix_italian_typography(concept).lower()
            if q5_is_valid_micro_concept(clean):
                selected.append(clean)

        if len(q5_unique_strings(selected)) < limit:
            selected.extend(q5_generate_micro_concepts_from_text(text, limit=limit))

        valid = [
            concept
            for concept in q5_unique_strings(selected)
            if q5_is_valid_micro_concept(concept)
        ]

        return valid[:limit]

    except Exception:
        return []


def q5_choose_card_title(
    local_concepts: List[str],
    fact: str,
    used_titles: set,
    fallback: str,
) -> str:
    try:
        for concept in local_concepts:
            title = q5_title_from_text(concept, fallback=fallback, max_words=5)
            key = title.lower()

            if key and key not in used_titles:
                used_titles.add(key)
                return title

        fact_title = q5_title_from_text(fact, fallback=fallback, max_words=6)
        fact_key = fact_title.lower()

        if fact_key not in used_titles:
            used_titles.add(fact_key)
            return fact_title

        progressive = fallback
        used_titles.add(progressive.lower())
        return progressive

    except Exception:
        return fallback


def q5_build_concept_cards(
    facts: List[str],
    preferred_concepts: List[str],
    pages: List[int],
    config: Phase5QualityConfig,
) -> List[ConceptCardFinal]:
    cards: List[ConceptCardFinal] = []
    used_titles: set = set()

    try:
        if not facts:
            return cards

        max_cards = max(0, config.max_cards)
        max_card_facts = max(1, config.max_card_facts)

        for index in range(0, min(len(facts), max_cards)):
            fact = facts[index]
            related_facts = facts[index:index + max_card_facts]
            text_for_domain = " ".join(related_facts)

            local_concepts = q5_select_micro_concepts(
                preferred_concepts=preferred_concepts,
                text=text_for_domain,
                limit=config.max_micro_concepts_per_card,
            )

            domain = q5_detect_domain_from_text(text_for_domain, local_concepts)
            color = q5_color_for_domain(domain)

            title = q5_choose_card_title(
                local_concepts=local_concepts,
                fact=fact,
                used_titles=used_titles,
                fallback=f"Card concettuale {index + 1}",
            )

            content = q5_build_card_content(related_facts)

            card = ConceptCardFinal(
                card_id=f"phase5_card_{index + 1:03d}",
                titolo=title,
                contenuto_esplicativo=content,
                micro_concetti=local_concepts,
                colore_categoria=color,
                dominio_rilevato=domain,
                fonte_pagine=list(pages),
            )

            if not card.contenuto_esplicativo:
                card.warnings.append("PHASE5_CARD_EMPTY_CONTENT")

            if not card.micro_concetti:
                card.warnings.append("PHASE5_CARD_NO_MICRO_CONCEPTS")

            invalid_concepts = [
                concept for concept in card.micro_concetti
                if not q5_is_valid_micro_concept(concept)
            ]

            if invalid_concepts:
                card.warnings.append(
                    "PHASE5_CARD_INVALID_MICRO_CONCEPTS: " + ", ".join(invalid_concepts)
                )

            cards.append(card)

        return cards

    except Exception:
        return cards


# =============================================================================
# Fine Fase 5.1 — Micro Concepts Cards Quality Patch
# =============================================================================
'''


def main() -> int:
    try:
        if not TARGET_FILE.exists():
            print(f"❌ File non trovato: {TARGET_FILE}")
            return 1

        original = TARGET_FILE.read_text(encoding="utf-8")

        if REQUIRED_MARKER not in original:
            print("❌ Fase 5 base non trovata. Patch annullata.")
            return 1

        if PATCH_MARKER in original:
            print("✅ Micro-patch FASE 5.1 già presente. Nessuna modifica necessaria.")
            return 0

        backup = TARGET_FILE.with_suffix(".py.bak_phase5_micro_concepts_cards_v11")
        shutil.copy2(TARGET_FILE, backup)

        patched = original.rstrip() + "\n\n" + PATCH_CODE + "\n"
        TARGET_FILE.write_text(patched, encoding="utf-8")

        print("✅ Micro-patch FASE 5.1 applicata con successo.")
        print(f"Backup creato: {backup}")
        print(f"File aggiornato: {TARGET_FILE}")
        return 0

    except Exception as exc:
        print(f"❌ Errore micro-patch FASE 5.1: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
