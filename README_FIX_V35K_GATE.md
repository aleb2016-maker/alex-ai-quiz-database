# Fix gate universale pagina V3.5K

Questo fix non corregge frasi specifiche. Fa tre controlli generali:

1. ripulisce la pagina V3.5H da label vecchie `V3.5J` e path JSON corrotti `json();`;
2. verifica solo i campi visibili degli output V3.5K, ignorando metadati tecnici;
3. rigenera il report `reports/rag_cleaner_finale_universale_v35k.md` con esito reale.

Comando:

```bash
python3 scripts/fix_gate_universale_pagina_v35k.py
```
