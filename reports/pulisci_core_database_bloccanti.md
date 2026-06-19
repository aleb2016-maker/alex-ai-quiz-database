# Pulizia blocchi validatore core

## Backup spostati fuori da data/

- `data/ai.backup_prima_correzione_avvisi_terzo_blocco.json` → `backups/spostati_da_data/20260619_115902/ai.backup_prima_correzione_avvisi_terzo_blocco.json`
- `data/ai.backup_prima_quarto_blocco_distrattori_forti.json` → `backups/spostati_da_data/20260619_115902/ai.backup_prima_quarto_blocco_distrattori_forti.json`
- `data/informatica.backup_prima_quarto_blocco_distrattori_forti.json` → `backups/spostati_da_data/20260619_115902/informatica.backup_prima_quarto_blocco_distrattori_forti.json`
- `data/ai.backup_prima_secondo_blocco_distrattori_forti.json` → `backups/spostati_da_data/20260619_115902/ai.backup_prima_secondo_blocco_distrattori_forti.json`
- `data/ai.backup_prima_terzo_blocco_distrattori_forti.json` → `backups/spostati_da_data/20260619_115902/ai.backup_prima_terzo_blocco_distrattori_forti.json`
- `data/informatica.backup_prima_primo_blocco_distrattori_forti.json` → `backups/spostati_da_data/20260619_115902/informatica.backup_prima_primo_blocco_distrattori_forti.json`
- `data/matematica.backup_prima_terzo_blocco_distrattori_forti.json` → `backups/spostati_da_data/20260619_115902/matematica.backup_prima_terzo_blocco_distrattori_forti.json`
- `data/inglese.backup_prima_primo_blocco_distrattori_forti.json` → `backups/spostati_da_data/20260619_115902/inglese.backup_prima_primo_blocco_distrattori_forti.json`
- `data/inglese.backup_prima_quarto_blocco_distrattori_forti.json` → `backups/spostati_da_data/20260619_115902/inglese.backup_prima_quarto_blocco_distrattori_forti.json`
- `data/matematica.backup_prima_quarto_blocco_distrattori_forti.json` → `backups/spostati_da_data/20260619_115902/matematica.backup_prima_quarto_blocco_distrattori_forti.json`
- `data/inglese.backup_prima_secondo_blocco_distrattori_forti.json` → `backups/spostati_da_data/20260619_115902/inglese.backup_prima_secondo_blocco_distrattori_forti.json`
- `data/ai.backup_prima_quinto_blocco_distrattori_forti.json` → `backups/spostati_da_data/20260619_115902/ai.backup_prima_quinto_blocco_distrattori_forti.json`
- `data/matematica.backup_prima_secondo_blocco_distrattori_forti.json` → `backups/spostati_da_data/20260619_115902/matematica.backup_prima_secondo_blocco_distrattori_forti.json`
- `data/informatica.backup_prima_secondo_blocco_distrattori_forti.json` → `backups/spostati_da_data/20260619_115902/informatica.backup_prima_secondo_blocco_distrattori_forti.json`
- `data/ai.backup_prima_distrattori_forti.json` → `backups/spostati_da_data/20260619_115902/ai.backup_prima_distrattori_forti.json`
- `data/informatica.backup_prima_terzo_blocco_distrattori_forti.json` → `backups/spostati_da_data/20260619_115902/informatica.backup_prima_terzo_blocco_distrattori_forti.json`
- `data/inglese.backup_prima_terzo_blocco_distrattori_forti.json` → `backups/spostati_da_data/20260619_115902/inglese.backup_prima_terzo_blocco_distrattori_forti.json`
- `data/matematica.backup_prima_primo_blocco_distrattori_forti.json` → `backups/spostati_da_data/20260619_115902/matematica.backup_prima_primo_blocco_distrattori_forti.json`

## Diagnosi MAT-AV-0203

```json
{
  "id": "MAT-AV-0203",
  "categoria": "matematica",
  "livello": "avanzato",
  "domanda": "Qual è un integrale indefinito di 2x rispetto a x?",
  "opzioni": [
    "x² + C",
    "2x² + C",
    "x + C",
    "2 + C"
  ],
  "risposta_corretta": "x² + C",
  "spiegazione": "Un integrale indefinito di 2x rispetto a x è x² + C, perché la derivata di x² è 2x. 2x² + C avrebbe derivata 4x, x + C avrebbe derivata 1, 2 + C avrebbe derivata 0.",
  "regola_distrattori": "tre_distrattori_forti",
  "criterio_distrattori": "Ogni risposta errata deve essere un errore matematico plausibile: calcolo vicino, passaggio saltato, formula invertita o interpretazione numerica quasi corretta."
}
```
