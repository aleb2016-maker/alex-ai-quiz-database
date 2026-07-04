from pathlib import Path
import shutil
import sys

TARGET_FILE = Path("backend/motori_scrittura.py")
REQUIRED_MARKER = "FASE 5.2 — QUALITY STUDY QUESTIONS QUIZ V1"
PATCH_MARKER = "FASE 5.2.1 — ROBUST QUIZ DISTRACTORS PATCH"

PATCH_CODE = r'''

# =============================================================================
# FASE 5.2.1 — ROBUST QUIZ DISTRACTORS PATCH
#
# Micro-patch solo Fase 5.2.
#
# Problema corretto:
# - il quiz saltava alcuni facts quando non trovava almeno 3 distrattori.
#
# Obiettivo:
# - generare sempre 3 distrattori falsi/plausibili per ogni fact valido
# - non usare mai come distrattori altri facts veri del documento
# - mantenere esattamente 1 risposta corretta e 4 opzioni
#
# Non modifica Fasi 1–4.
# Non tocca UI/CSS/pulsanti/layout.
# =============================================================================


def q521_topic_from_fact(fact: str, concepts: Optional[List[str]] = None) -> str:
    """
    Ricava un'etichetta breve e leggibile per creare distrattori generici.
    """

    try:
        local_concepts = concepts or q52_domain_micro_concepts_from_text(fact)
        if local_concepts:
            return q52_clean(local_concepts[0]).lower()

        title = q5_title_from_text(fact, fallback="questo controllo", max_words=4)
        return q52_clean(title).lower()

    except Exception:
        return "questo controllo"


def q521_generic_false_distractors(fact: str, concepts: Optional[List[str]] = None) -> List[str]:
    """
    Distrattori generici ma plausibili.

    Sono volutamente falsi:
    - dicono che il controllo è facoltativo
    - negano l'obbligo
    - negano l'impatto sul rischio
    - spostano l'attenzione fuori dal documento
    """

    distractors: List[str] = []

    try:
        topic = q521_topic_from_fact(fact, concepts)

        templates = [
            f"Il documento indica che {topic} può essere ignorato senza conseguenze operative.",
            f"Il documento presenta {topic} come un elemento facoltativo e non necessario.",
            f"Il documento esclude che {topic} abbia effetti sui controlli interni.",
            f"Il documento afferma che {topic} riguarda solo attività esterne al sistema.",
            f"Il documento sostiene che {topic} non richiede alcuna verifica periodica.",
            f"Il documento considera {topic} irrilevante per la gestione del rischio.",
            f"Il documento permette di applicare {topic} solo quando l'operatore lo ritiene utile.",
            f"Il documento chiarisce che {topic} non è collegato alla sicurezza operativa.",
        ]

        for template in templates:
            distractors.append(q52_sentence(template))

        return q52_unique(distractors)

    except Exception:
        return q52_unique(distractors)


def q52_false_distractors_from_fact(fact: str) -> List[str]:
    """
    Override robusto Fase 5.2.1.

    Genera distrattori:
    1. con trasformazioni dirette del fact
    2. con distrattori generici falsi/plausibili
    3. con fallback sicuro se le trasformazioni non bastano
    """

    distractors: List[str] = []

    try:
        clean = q52_clean(fact).rstrip(".")
        lowered = clean.lower()

        replacements = [
            ("non devono essere condivise", "possono essere condivise liberamente"),
            ("non deve essere condivisa", "può essere condivisa liberamente"),
            ("non devono essere condivisi", "possono essere condivisi liberamente"),
            ("non deve essere condiviso", "può essere condiviso liberamente"),
            ("deve essere associato", "può rimanere non associato"),
            ("deve essere associata", "può rimanere non associata"),
            ("devono essere associati", "possono rimanere non associati"),
            ("devono essere associate", "possono rimanere non associate"),
            ("devono essere", "non devono essere necessariamente"),
            ("deve essere", "non deve essere necessariamente"),
            ("limita l'utilizzo", "consente l'utilizzo illimitato"),
            ("limita", "non limita"),
            ("riduce il rischio", "aumenta il rischio"),
            ("riduce", "aumenta"),
            ("evita", "favorisce"),
            ("previene", "favorisce"),
            ("persona identificabile", "persona non identificabile"),
            ("utenti non più autorizzati", "utenti sempre autorizzati"),
            ("utenti autorizzati", "qualsiasi utente"),
            ("permessi attivi", "permessi illimitati"),
            ("sistemi interni", "sistemi esterni non controllati"),
            ("operatori", "utenti anonimi"),
            ("accessi", "accessi non controllati"),
            ("credenziali", "credenziali condivise"),
            ("account", "account anonimo"),
        ]

        for old, new in replacements:
            if old in lowered:
                pattern = re.compile(re.escape(old), flags=re.IGNORECASE)
                candidate = pattern.sub(new, clean, count=1)
                candidate = q52_sentence(candidate)

                if candidate and qg_normalize_for_compare(candidate) != qg_normalize_for_compare(clean):
                    distractors.append(candidate)

        concepts = q52_domain_micro_concepts_from_text(clean)
        distractors.extend(q521_generic_false_distractors(clean, concepts))

        # Fallback extra: sempre falsi e sempre diversi dal fact.
        topic = q521_topic_from_fact(clean, concepts)

        fallback_extra = [
            f"{q52_clean(topic).capitalize()} non richiede controlli documentati.",
            f"{q52_clean(topic).capitalize()} può essere gestito senza regole operative.",
            f"{q52_clean(topic).capitalize()} non modifica il livello di rischio.",
            f"{q52_clean(topic).capitalize()} è indicato come scelta libera dell'utente.",
            f"{q52_clean(topic).capitalize()} non deve essere collegato agli account.",
        ]

        distractors.extend(q52_sentence(item) for item in fallback_extra)

        return q52_unique(distractors)

    except Exception:
        return q52_unique(distractors)


def q521_filter_distractors(
    candidates: List[str],
    correct_fact: str,
    source_facts: List[str],
    needed: int = 3,
) -> List[str]:
    """
    Filtra distrattori:
    - non vuoti
    - non uguali alla risposta corretta
    - non uguali a facts veri del documento
    - non duplicati
    """

    selected: List[str] = []

    try:
        source_keys = set(
            qg_normalize_for_compare(fact)
            for fact in source_facts
            if q52_clean(fact)
        )

        correct_key = qg_normalize_for_compare(correct_fact)

        for candidate in candidates:
            clean_candidate = q52_sentence(candidate)
            key = qg_normalize_for_compare(clean_candidate)

            if not key:
                continue

            if key == correct_key:
                continue

            if key in source_keys:
                continue

            if key in set(qg_normalize_for_compare(item) for item in selected):
                continue

            selected.append(clean_candidate)

            if len(selected) >= needed:
                break

        return selected

    except Exception:
        return selected


def q52_build_quality_quiz(
    facts: List[str],
    preferred_concepts: List[str],
    pages: List[int],
    config: Phase5StudyQuizConfig,
) -> List[QualityQuizQuestionFinal]:
    """
    Override robusto Fase 5.2.1.

    Non salta più facts validi se il generatore principale produce pochi distrattori.
    Usa fallback robusti, poi valida tutto.
    """

    quiz: List[QualityQuizQuestionFinal] = []

    try:
        option_ids = ["A", "B", "C", "D"]

        usable_facts = [
            q52_limit(fact, config.max_fact_chars)
            for fact in facts
            if q52_clean(fact)
        ]

        for index, fact in enumerate(usable_facts[: max(0, config.max_quiz_questions)], start=1):
            correct_fact = q52_sentence(fact)
            concepts = q52_local_concepts(
                correct_fact,
                preferred_concepts,
                limit=config.max_micro_concepts_per_item,
            )

            raw_candidates = q52_false_distractors_from_fact(correct_fact)

            distractors = q521_filter_distractors(
                candidates=raw_candidates,
                correct_fact=correct_fact,
                source_facts=usable_facts,
                needed=3,
            )

            # Ultimo fallback, se per qualsiasi motivo restano meno di 3.
            if len(distractors) < 3:
                topic = q521_topic_from_fact(correct_fact, concepts)
                emergency = [
                    f"Il documento dice che {topic} può essere ignorato.",
                    f"Il documento dice che {topic} non ha valore operativo.",
                    f"Il documento dice che {topic} non richiede controlli.",
                    f"Il documento dice che {topic} aumenta sempre la sicurezza senza verifiche.",
                    f"Il documento dice che {topic} riguarda solo informazioni esterne.",
                ]

                distractors = q521_filter_distractors(
                    candidates=distractors + emergency,
                    correct_fact=correct_fact,
                    source_facts=usable_facts,
                    needed=3,
                )

            if len(distractors) < 3:
                # Non dovrebbe più accadere, ma lasciamo warning e saltiamo solo casi impossibili.
                continue

            correct_position = (index - 1) % 4
            raw_options = distractors[:3]
            raw_options.insert(correct_position, correct_fact)

            options: List[QualityQuizOptionFinal] = []

            for option_index, option_text in enumerate(raw_options[:4]):
                options.append(
                    QualityQuizOptionFinal(
                        option_id=option_ids[option_index],
                        testo=q52_limit(option_text, config.max_fact_chars),
                        is_correct=(option_index == correct_position),
                    )
                )

            question = QualityQuizQuestionFinal(
                question_id=f"phase5_quiz_question_{index:03d}",
                domanda=q52_build_quiz_question_text(correct_fact, concepts, index),
                opzioni=options,
                correct_option_id=option_ids[correct_position],
                spiegazione=q52_clean(
                    "La risposta corretta è quella che riprende il fatto verificato dal documento: "
                    + q5_lower_first(q52_sentence(correct_fact))
                ),
                fatto_origine=correct_fact,
                micro_concetti=concepts,
                fonte_pagine=list(pages),
            )

            quiz.append(question)

        return quiz

    except Exception:
        return quiz


# =============================================================================
# Fine Fase 5.2.1 — Robust Quiz Distractors Patch
# =============================================================================
'''


def main() -> int:
    try:
        if not TARGET_FILE.exists():
            print(f"❌ File non trovato: {TARGET_FILE}")
            return 1

        original = TARGET_FILE.read_text(encoding="utf-8")

        if REQUIRED_MARKER not in original:
            print("❌ Fase 5.2 non trovata. Patch annullata.")
            return 1

        if PATCH_MARKER in original:
            print("✅ FASE 5.2.1 ROBUST QUIZ DISTRACTORS già presente. Nessuna modifica necessaria.")
            return 0

        backup = TARGET_FILE.with_suffix(".py.bak_phase5_quiz_distractors_v121")
        shutil.copy2(TARGET_FILE, backup)

        patched = original.rstrip() + "\n\n" + PATCH_CODE + "\n"
        TARGET_FILE.write_text(patched, encoding="utf-8")

        print("✅ Patch FASE 5.2.1 ROBUST QUIZ DISTRACTORS applicata con successo.")
        print(f"Backup creato: {backup}")
        print(f"File aggiornato: {TARGET_FILE}")
        return 0

    except Exception as exc:
        print(f"❌ Errore patch FASE 5.2.1: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
