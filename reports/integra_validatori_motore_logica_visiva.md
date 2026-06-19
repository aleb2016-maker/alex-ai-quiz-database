# Integrazione validatori nel motore Logica visiva

Il file `scripts/motore_qualita_logica_visiva.py` è stato trasformato in wrapper obbligatorio.

Creato backup operativo: `scripts/motore_qualita_logica_visiva_base.py`

Ora il comando principale esegue:

1. `scripts/validatore_domande_non_suggerite_logica_visiva.py`
2. `scripts/validatore_coerenza_logica_visiva.py`
3. `scripts/motore_qualita_logica_visiva_base.py`

In questo modo il motore visuale non può più dichiarare 0 problemi ignorando:

- domande che contengono già la logica dell'esercizio;
- incoerenze tra risposta corretta, spiegazione e visual_logic.

