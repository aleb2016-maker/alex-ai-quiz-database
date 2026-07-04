from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TEST = ROOT / "backend" / "test_phase5_live_quality_bridge_v1.py"
PATCH = ROOT / "scripts" / "patch_phase5_live_quality_bridge_v1.py"

SYS_PATH_BLOCK = '''import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
'''


def patch_test_file() -> None:
    text = TEST.read_text(encoding="utf-8")

    if "sys.path.insert(0, str(ROOT))" in text:
        print("ℹ️ Test già corretto: sys.path presente.")
        return

    old = '''import json
from pathlib import Path

from backend.phase5_live_quality_bridge_v1 import apply_phase5_live_quality_bridge_v1
'''

    new = f'''import json
{SYS_PATH_BLOCK}
from backend.phase5_live_quality_bridge_v1 import apply_phase5_live_quality_bridge_v1
'''

    if old not in text:
        raise RuntimeError("Pattern import non trovato nel test 5.3.")

    TEST.write_text(text.replace(old, new), encoding="utf-8")
    print(f"✅ Corretto import nel test: {TEST}")


def patch_generator_file() -> None:
    if not PATCH.exists():
        print("ℹ️ Patch generator non trovato, salto.")
        return

    text = PATCH.read_text(encoding="utf-8")

    if "sys.path.insert(0, str(ROOT))" in text:
        print("ℹ️ Patch generator già corretto: sys.path presente.")
        return

    old = '''import json
from pathlib import Path

from backend.phase5_live_quality_bridge_v1 import apply_phase5_live_quality_bridge_v1
'''

    new = f'''import json
{SYS_PATH_BLOCK}
from backend.phase5_live_quality_bridge_v1 import apply_phase5_live_quality_bridge_v1
'''

    if old not in text:
        print("⚠️ Pattern import non trovato nel patch generator. Corretto solo il test esistente.")
        return

    PATCH.write_text(text.replace(old, new), encoding="utf-8")
    print(f"✅ Corretto anche il generator patch: {PATCH}")


def main() -> int:
    if not TEST.exists():
        raise FileNotFoundError(f"Test non trovato: {TEST}")

    patch_test_file()
    patch_generator_file()

    print("✅ FIX IMPORT TEST FASE 5.3 COMPLETATO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
