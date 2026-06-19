# Correzione validatore core per simboli matematici

Corretto `scripts/validatore_core_database.py` per non confondere espressioni matematiche come `x² + C` e `x + C`.

Aggiornato `scripts/validate_questions.py` come wrapper pulito sul validatore core ufficiale.

Il vecchio validatore storico resta conservato in `scripts/validate_questions_base.py`, ma non viene più eseguito dal comando principale perché scansionava anche file non ufficiali.

