# scripts/patch_map_prompt_coverage_v1.py
# =============================================================================
# PATCH MAP COVERAGE V1
#
# Modifica chirurgica SOLO backend:
# - file target: backend/motori_scrittura.py
# - obiettivo: rafforzare il prompt MAP
# - nessuna modifica a UI, CSS, pulsanti, grafica
#
# La patch aggiunge regole di copertura:
# - obblighi
# - divieti
# - rischi
# - causa-effetto
# - procedure
# - ultimo periodo del chunk
#
# =============================================================================

from __future__ import annotations

import shutil
import sys
from pathlib import Path


TARGET_FILE = Path("backend/motori_scrittura.py")
PATCH_MARKER = "MAP_COVERAGE_V1"


def main() -> int:
    try:
        if not TARGET_FILE.exists():
            print(f"❌ File non trovato: {TARGET_FILE}")
            return 1

        original = TARGET_FILE.read_text(encoding="utf-8")

        if PATCH_MARKER in original:
            print("✅ Patch MAP_COVERAGE_V1 già presente. Nessuna modifica necessaria.")
            return 0

        backup_file = TARGET_FILE.with_suffix(".py.bak_map_coverage_v1")
        shutil.copy2(TARGET_FILE, backup_file)

        old_block = """Devi estrarre SOLO dati grezzi.

Restituisci JSON valido con questa struttura esatta:"""

        new_block = """Devi estrarre SOLO dati grezzi.

Regole di copertura obbligatorie — MAP_COVERAGE_V1:
- Ogni obbligo espresso con parole come "deve", "devono", "è necessario", "è obbligatorio" deve diventare almeno un fact separato.
- Ogni divieto espresso con parole come "non deve", "non devono", "vietato", "evitare" deve diventare almeno un fact separato.
- Ogni rischio, riduzione del rischio, prevenzione, causa-effetto o conseguenza deve diventare almeno un fact separato e, se possibile, una relation.
- Ogni controllo, revisione, verifica, procedura, fase operativa o regola aziendale deve diventare almeno un fact separato.
- Non omettere l'ultimo periodo del chunk: spesso contiene conclusioni operative, rischi o condizioni importanti.
- Se una frase contiene due regole diverse, dividile in due facts distinti.
- I facts devono essere atomici: un solo fatto/regola per elemento.
- Le relations devono rappresentare legami reali presenti nel chunk: soggetto → azione/relazione → oggetto.
- Se nel chunk appare un rapporto tipo "X riduce Y", "X previene Y", "X causa Y", "X limita Y", crea una relation dedicata.
- Non comprimere più fatti in un'unica frase generale.

Restituisci JSON valido con questa struttura esatta:"""

        if old_block not in original:
            print("❌ Blocco prompt principale non trovato. Patch annullata.")
            print("Backup NON modificato creato in:", backup_file)
            return 1

        patched = original.replace(old_block, new_block, 1)

        old_divieti = """- vietato trasformare il chunk in testo elegante"""

        new_divieti = """- vietato trasformare il chunk in testo elegante
- vietato perdere obblighi, divieti, rischi, revisioni, controlli o causa-effetto presenti nel chunk
- vietato sostituire fatti specifici con frasi generiche tipo "il documento parla di"
- vietato fondere più regole operative in un solo fatto generico"""

        if old_divieti not in patched:
            print("❌ Blocco divieti non trovato. Patch annullata.")
            print("Backup creato in:", backup_file)
            return 1

        patched = patched.replace(old_divieti, new_divieti, 1)

        TARGET_FILE.write_text(patched, encoding="utf-8")

        print("✅ Patch MAP_COVERAGE_V1 applicata con successo.")
        print(f"Backup creato: {backup_file}")
        print(f"File aggiornato: {TARGET_FILE}")
        return 0

    except Exception as exc:
        print(f"❌ Errore durante patch MAP_COVERAGE_V1: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())