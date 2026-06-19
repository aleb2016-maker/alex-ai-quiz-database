# Correzione finale build_database e check_duplicates

Corretto `scripts/build_database.py` per non dipendere più dal vecchio `build_database_base.py`.

Il nuovo build legge solo i database ufficiali, genera `dist/database_quiz_finale.json`, poi esegue:

1. `scripts/validatore_core_database.py`
2. `scripts/validatore_database_finale.py`
3. `scripts/validatore_duplicati_database.py`

Corretto anche `scripts/validatore_duplicati_database.py`, sistemando la regex che generava errore sul trattino.
