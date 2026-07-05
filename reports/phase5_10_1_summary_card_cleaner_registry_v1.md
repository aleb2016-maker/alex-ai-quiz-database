# Fase 5.10.1 — Summary/Card Cleaner Registry V1

- Status: `PASS`
- Motore: `backend.phase5_universal_text_cleaner_summary_cards_v1.universal_text_cleaner_summary_cards_payload_target_v1`
- Raw bad pattern: `10`
- Baseline senza cleaner: `10`
- Final con cleaner: `0`
- Protected outputs same baseline/final: `True`
- Micro-concepts sentence punctuation after: `0`
- Motore status: `ok`
- Motore applied: `1`

## Modifiche osservate baseline -> final

| # | Baseline senza cleaner | Final con cleaner |
|---:|---|---|
| 0 | Riassunto di qualita | Riassunto di qualità |
| 1 | TESTO DA RIALLINEARE | Il documento evidenzia che il controllo degli accessi limita l'utilizzo dei sistemi interni.<br><br>Sul piano operativo emerge che le credenziali non devono essere condivise tra più operatori. La revisione periodica degli accessi riduce il rischio perché evita permessi attivi non autorizzati. |
| 2 | Il documento evidenzia che il controllo degli accessi limita l'utilizzo dei sistemi interni . | Il documento evidenzia che il controllo degli accessi limita l'utilizzo dei sistemi interni. |
| 3 | Sul piano operativo emerge che le credenziali non non devono essere condivise tra più operatori. Inoltre, sì, la revisione periodica degli accessi riduce il rischio perchè evita permessi attivi non autorizzati. | Sul piano operativo emerge che le credenziali non devono essere condivise tra più operatori. La revisione periodica degli accessi riduce il rischio perché evita permessi attivi non autorizzati. |
| 5 | Questo elemento si collega anche al fatto che sì, il controllo degli accessi limita l'utilizzo dei sistemi interni . | Il controllo degli accessi limita l'utilizzo dei sistemi interni. |
| 9 | Un punto rilevante riguarda la riduzione del rischio: sì, la revisione periodica degli accessi riduce il rischio perchè evita permessi attivi non autorizzati. | Un punto rilevante riguarda la riduzione del rischio: la revisione periodica degli accessi riduce il rischio perché evita permessi attivi non autorizzati. |