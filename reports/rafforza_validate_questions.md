# Rafforzamento validate_questions.py

Creato backup operativo `scripts/validate_questions_base.py`.

`scripts/validate_questions.py` ora è un wrapper che esegue:

1. `scripts/validate_questions_base.py`
2. `scripts/validatore_core_database.py`

Il comando ora deve fallire se il validatore core trova errori bloccanti.

