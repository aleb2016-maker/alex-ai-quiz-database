# Blindatura creatore pacchetto personalizzato AI ITS

Obiettivo:

- impedire che il pacchetto personalizzato parta da Scienze quando viene scelta AI;
- mettere AI come prima materia e default del selettore;
- mantenere Scienze solo come scelta esplicita, non come fallback;
- verificare una simulazione AI da 10 domande con soli ID `AI-`.

## File trattati

- `demo/app.js` — esiste: True, modificato: False, select_id: 0, blocchi_option: 1, fallback: False, versione: False
- `demo/index.html` — esiste: True, modificato: False, select_id: 0, blocchi_option: 0, fallback: False, versione: False
- `scripts/rigenera_demo_separate.py` — esiste: True, modificato: False, select_id: 0, blocchi_option: 0, fallback: False, versione: False

## Verifica

ESITO: OK
- fallback non punta più a Scienze;
- AI è presente e selezionata come default;
- Scienze non precede AI nel selettore;
- simulazione AI da 10 domande contiene solo domande AI.