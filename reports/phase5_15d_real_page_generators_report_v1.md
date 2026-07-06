# FASE 5.15D - Test pratico reale 4 generatori

Status: **PASS**

- URL usato: `http://localhost:8000/demo-rag/test-documenti-universale.html`
- Comandi di avvio:

  - `cd /Users/alessandrobarbarossa/alex-ai-workspace`
  - `backend/.venv/bin/python scripts/run_phase5_14_3_local_backend_bridge.py (fallback: python3 scripts/run_phase5_14_3_local_backend_bridge.py)`
  - `python3 -m http.server 8000`

## Esito generatori

| Generatore | Output visibile | QM attesi | QM pratici | Qualità minima | Esito |
| --- | --- | ---: | ---: | --- | --- |
| Riassunto | sì | 55 | 55 | PASS | PASS |
| Card | sì | 60 | 60 | PASS | PASS |
| Domande studio | sì | 51 | 51 | PASS | PASS |
| Test/Quiz | sì | 63 | 63 | PASS | PASS |

## Testo usato

La gestione degli ordini in un magazzino moderno richiede una procedura chiara per ricevere, controllare, registrare e spedire i prodotti. Quando arriva una nuova merce, l’operatore verifica il documento di trasporto, controlla quantità e integrità degli articoli e segnala eventuali differenze. I prodotti conformi vengono registrati nel sistema gestionale e assegnati a una posizione precisa nel magazzino.

Durante la preparazione degli ordini, il sistema genera una lista di prelievo con codice articolo, quantità richiesta e posizione. L’operatore raccoglie i prodotti, controlla che corrispondano all’ordine e li porta nell’area di imballaggio. Prima della spedizione, un secondo controllo riduce il rischio di errori, prodotti mancanti o articoli scambiati.

La tracciabilità è importante perché permette di sapere dove si trova ogni prodotto, chi ha eseguito le operazioni e quando sono avvenute. Un processo ben organizzato riduce ritardi, reclami e costi operativi. Inoltre, la formazione degli operatori aiuta a mantenere standard costanti e a gestire correttamente eccezioni come merce danneggiata, quantità errate o urgenze di spedizione.

## Fix applicati

- Card: messaggio_chiave reso specifico rispetto al fatto invece del testo generico ripetuto.
- Quiz: distrattori resi specifici per topic e posizione della risposta corretta ruotata.
- Quiz/UI: payload frontend sanificato da is_correct/correct_option_id/risposta_corretta; verifica click via hash.
- Summary: micro-correzione dei connettivi e punteggiatura tra fatti.

## Difetti trovati

- nessuno

## Difetti rimasti

- nessuno
