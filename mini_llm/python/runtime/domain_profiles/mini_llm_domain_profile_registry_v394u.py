from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Dict, List

PROFILE_FILES = [
    "mini_llm_domain_profile_informatics_v394u.py",
    "mini_llm_domain_profile_sport_v394u.py",
    "mini_llm_domain_profile_curriculum_v394u.py",
    "mini_llm_domain_profile_science_v394u.py",
    "mini_llm_domain_profile_business_v394u.py",
]

def _load_profile_file(filename: str) -> Dict[str, Any]:
    path = Path(__file__).resolve().with_name(filename)
    spec = importlib.util.spec_from_file_location(path.stem, path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare profilo: {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.get_profile()

def all_profiles() -> List[Dict[str, Any]]:
    return [_load_profile_file(filename) for filename in PROFILE_FILES]

def generic_profile() -> Dict[str, Any]:
    return _load_profile_file("mini_llm_domain_profile_generic_v394u.py")

def score_profile(text: str, profile: Dict[str, Any]) -> int:
    low = str(text or "").lower()
    return sum(1 for term in profile.get("detection_terms", []) or [] if str(term).lower() in low)

def detect_profile(text: str) -> Dict[str, Any]:
    candidates = [(score_profile(text, profile), profile) for profile in all_profiles()]
    candidates.sort(key=lambda item: item[0], reverse=True)

    if not candidates or candidates[0][0] <= 0:
        profile = generic_profile()
        profile["detection_score"] = 0
        return profile

    score, profile = candidates[0]
    profile = dict(profile)
    profile["detection_score"] = score
    return profile
