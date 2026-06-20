# Riparatore distrattori RAG guidato

Il riparatore è stato potenziato.

Prima versione:
- chiedeva al modello di migliorare i distrattori;
- non sempre otteneva miglioramenti.

Nuova versione:
- riconosce temi come backup, ransomware, phishing, 2FA, Wi-Fi pubblico, password, malware, aggiornamenti e permessi;
- riscrive direttamente i distrattori con regole guidate;
- produce opzioni vicine al tema ma sbagliate per un dettaglio preciso;
- lavora solo sul JSON temporaneo RAG.

Questo rende il sistema più automatico e meno dipendente dalla qualità del modello locale.
