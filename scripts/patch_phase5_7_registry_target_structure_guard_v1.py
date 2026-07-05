from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "backend" / "legacy_quality_motor_registry_v1.py"

MARKER = "# FASE 5.7.1 — REGISTRY TARGET STRUCTURE GUARD V1"


HELPERS = r'''

# FASE 5.7.1 — REGISTRY TARGET STRUCTURE GUARD V1
# Evita che un motore legacy cambi la struttura del target in modo da impedire
# ai motori successivi di trovare summary/cards/study/full_output.
# Inoltre preserva i metadata del registry quando un motore lavora sul full output.
def _looks_like_summary_dict(value: Any) -> bool:
    if not isinstance(value, dict):
        return False

    keys = {str(k).lower() for k in value.keys()}

    return bool(keys & {"titolo", "title", "paragrafi", "paragraphs", "testo_completo", "text", "summary"})


def _extract_nested_target_value(value: Any, label: str, target_kind: str) -> Any:
    if not isinstance(value, dict):
        return value

    preferred = [label]

    if target_kind == "summary":
        preferred.extend(["riassunto_qualita", "summary", "riassunto", "summary_dict"])

    elif target_kind == "cards":
        preferred.extend(["card_concettuali", "cards", "cards_list"])

    elif target_kind == "study":
        preferred.extend(["domande_studio", "study_questions", "study", "study_list", "card_concettuali", "cards"])

    elif target_kind == "quiz":
        preferred.extend(["test_quiz", "quiz", "tests", "domande_quiz"])

    for key in preferred:
        child = value.get(key)

        if isinstance(child, (dict, list, str)):
            return child

    return value


def _normalize_output_for_target_structure_v1(
    *,
    before_value: Any,
    candidate_value: Any,
    target_kind: str,
    label: str,
) -> tuple[Any, bool, str]:
    if candidate_value is None:
        return before_value, True, "none_output"

    candidate_value = _extract_nested_target_value(candidate_value, label, target_kind)

    if target_kind == "summary":
        if isinstance(before_value, dict):
            if isinstance(candidate_value, dict) and _looks_like_summary_dict(candidate_value):
                return candidate_value, False, ""

            return before_value, True, "summary_dict_structure_not_preserved"

        if isinstance(before_value, str):
            if isinstance(candidate_value, str):
                return candidate_value, False, ""

            return before_value, True, "summary_text_structure_not_preserved"

    if target_kind in {"cards", "study", "quiz"}:
        if isinstance(before_value, list):
            if isinstance(candidate_value, list):
                return candidate_value, False, ""

            return before_value, True, f"{target_kind}_list_structure_not_preserved"

        if isinstance(before_value, dict):
            if isinstance(candidate_value, dict):
                return candidate_value, False, ""

            return before_value, True, f"{target_kind}_dict_structure_not_preserved"

    if target_kind == "full_output":
        if isinstance(before_value, dict) and isinstance(candidate_value, dict):
            return candidate_value, False, ""

        return before_value, True, "full_output_structure_not_preserved"

    if type(candidate_value) is type(before_value):
        return candidate_value, False, ""

    return before_value, True, "generic_structure_not_preserved"


def _preserve_registry_meta_after_root_replace_v1(new_result: Any, previous_result: Any) -> Any:
    if not isinstance(new_result, dict) or not isinstance(previous_result, dict):
        return new_result

    previous_meta = previous_result.get("_legacy_quality_motor_registry_v1")

    if isinstance(previous_meta, dict):
        new_result["_legacy_quality_motor_registry_v1"] = previous_meta

    return new_result
'''


def main() -> int:
    if not REGISTRY.exists():
        raise FileNotFoundError(f"Registry non trovato: {REGISTRY}")

    text = REGISTRY.read_text(encoding="utf-8")

    if MARKER in text:
        print("ℹ️ Guard Fase 5.7.1 già presente: non duplico.")
        return 0

    anchor = '''def _looks_like_option_dict(value: Any) -> bool:
'''

    if anchor not in text:
        raise SystemExit("Anchor helper non trovato.")

    text = text.replace(anchor, HELPERS + "\n\n" + anchor, 1)

    old_block = '''            if new_value is None:
                new_value = value

            after_json = _safe_json(new_value)
            defects_after = count_known_text_defects_v1(new_value)

            guarded_rejected = False

            if defects_after > defects_before:
                guarded_rejected = True
                new_value = value
                after_json = before_json
                defects_after = defects_before
'''

    new_block = '''            structural_rejected = False
            structural_reject_reason = ""

            if new_value is None:
                new_value = value

            new_value, structural_rejected, structural_reject_reason = _normalize_output_for_target_structure_v1(
                before_value=value,
                candidate_value=new_value,
                target_kind=spec.target_kind,
                label=label,
            )

            after_json = _safe_json(new_value)
            defects_after = count_known_text_defects_v1(new_value)

            guarded_rejected = False

            if defects_after > defects_before:
                guarded_rejected = True
                new_value = value
                after_json = before_json
                defects_after = defects_before
'''

    if old_block not in text:
        raise SystemExit("Blocco guard difetti non trovato.")

    text = text.replace(old_block, new_block, 1)

    old_assign = '''            if parent is not None and key is not None:
                parent[key] = new_value
            else:
                result = new_value
'''

    new_assign = '''            if parent is not None and key is not None:
                parent[key] = new_value
            else:
                result = _preserve_registry_meta_after_root_replace_v1(new_value, result)
'''

    if old_assign not in text:
        raise SystemExit("Blocco assegnazione target non trovato.")

    text = text.replace(old_assign, new_assign, 1)

    old_target_meta = '''                    "guarded_rejected": guarded_rejected,
                    "known_text_defects_before": defects_before,
                    "known_text_defects_after": defects_after,
'''

    new_target_meta = '''                    "guarded_rejected": guarded_rejected,
                    "structural_rejected": structural_rejected,
                    "structural_reject_reason": structural_reject_reason,
                    "known_text_defects_before": defects_before,
                    "known_text_defects_after": defects_after,
'''

    if old_target_meta not in text:
        raise SystemExit("Blocco metadata target non trovato.")

    text = text.replace(old_target_meta, new_target_meta, 1)

    old_status_block = '''        if errors and motor_meta["applied"] == 0:
            motor_meta["status"] = "failed"
            motor_meta["errors"] = errors
        elif errors:
            motor_meta["status"] = "partial"
            motor_meta["errors"] = errors
        else:
            motor_meta["status"] = "ok"
'''

    new_status_block = '''        if errors and motor_meta["applied"] == 0:
            motor_meta["status"] = "failed"
            motor_meta["errors"] = errors
        elif errors:
            motor_meta["status"] = "partial"
            motor_meta["errors"] = errors
        else:
            motor_meta["status"] = "ok"

        meta = _ensure_registry_meta(result)

        if meta is not None:
            meta["motors"][spec.motor_id] = motor_meta
'''

    if old_status_block not in text:
        raise SystemExit("Blocco status motore non trovato.")

    text = text.replace(old_status_block, new_status_block, 1)

    REGISTRY.write_text(text, encoding="utf-8")

    print(f"✅ Guard struttura target Fase 5.7.1 aggiunta a: {REGISTRY}")
    print("✅ PATCH FASE 5.7.1 REGISTRY TARGET STRUCTURE GUARD COMPLETATA")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
