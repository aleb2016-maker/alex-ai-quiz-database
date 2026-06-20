# Motore grafico riutilizzabile

Il progetto ora contiene una base per scegliere lo stile grafico dei futuri pacchetti formativi.

## File principali

- `config/temi_grafici_formazione.json`
- `runtime/web/theme-engine.css`
- `runtime/web/theme-engine.js`
- `scripts/applica_tema_formazione.py`

## Temi disponibili

- `dark-tech`
- `light-clean`
- `neon-purple`
- `ocean-blue`

## Comando

```bash
python3 scripts/applica_tema_formazione.py dark-tech
```

Il comando genera:

- `dist/formazione/tema_selezionato.json`
- `dist/formazione/theme-selected.css`

Questa base serve per futuri pacchetti dove l'utente potrà scegliere colori, sfondi, stile delle card e atmosfera grafica senza riscrivere il codice del corso.
