# Correzione duplicati Logica visiva

Aggiornato `scripts/validatore_duplicati_database.py`.

Le domande `LOG-VIS` possono avere testo neutro identico, perché la distinzione reale è visuale:

- immagini;
- opzioni;
- risposta corretta;
- visual_logic.

Il validatore continua invece a bloccare:

- ID duplicati;
- opzioni duplicate nella stessa domanda;
- domande testuali identiche non visuali.

