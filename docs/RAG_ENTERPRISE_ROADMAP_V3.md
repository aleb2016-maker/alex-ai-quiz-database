# RAG Enterprise Roadmap V3

## Decisione tecnica

Il progetto RAG viene diviso in due livelli:

1. **Versione locale / concept**
   - usa Ollama e modelli locali;
   - serve per demo offline e prototipo concettuale;
   - non è la versione aziendale finale;
   - utile per dimostrare chunking, interfaccia, card, test, sinossi, riassunti e PDF.

2. **Versione enterprise / server**
   - usa backend server;
   - usa AI via API professionali;
   - punta a qualità più alta, tempi migliori e maggiore affidabilità;
   - gestisce documenti lunghi, cache, code di lavoro, utenti, costi e report.

## Conclusione sui modelli locali

I modelli locali testati sono utili per prototipazione, ma non sono sufficienti come motore principale per una vera app aziendale.

Risultato dei test locali:

- `llama3.1:8b`: migliore qualità tra i modelli locali provati, ma non abbastanza veloce per documenti molto lunghi.
- `qwen2.5:7b`: più veloce, adatto a sinossi e concetti sintetici, ma troppo corto come motore principale.
- `mistral:7b`: discreto, ma non rispetta sempre bene le istruzioni.
- `llama3.2:3b`: troppo prolisso e non conveniente.
- `deepseek-r1:8b` e `gemma3:4b`: non scelti come base finale.

## Regola output definitiva

Il vecchio obiettivo 15-25% viene eliminato per i documenti grandi.

La nuova regola è:

- **Sinossi / panoramica sintetica:** 1% delle pagine totali.
- **Riassunto qualità:** 10% delle pagine totali.

Esempi:

- 100 pagine → 1 pagina di sinossi + 10 pagine di riassunto qualità.
- 300 pagine → 3 pagine di sinossi + 30 pagine di riassunto qualità.
- 500 pagine → 5 pagine di sinossi + 50 pagine di riassunto qualità.

Il 20% non deve essere previsto nella pipeline con modelli locali.

## Architettura target

La piattaforma deve usare un'architettura a provider intercambiabile.

Flusso generale:

1. caricamento documento;
2. estrazione testo;
3. riconoscimento tipo documento;
4. chunking intelligente;
5. mappa concetti;
6. sinossi 1%;
7. riassunto qualità 10%;
8. card;
9. domande studio;
10. test;
11. PDF/export;
12. quality gate finale.

## Provider AI

La piattaforma deve supportare più motori:

### Provider locale

- Ollama;
- utile per demo offline;
- qualità media/buona;
- tempi limitati;
- nessun costo API.

### Provider enterprise

- API AI professionali;
- qualità superiore;
- tempi migliori;
- gestione documenti lunghi;
- possibilità di usare modelli diversi per compiti diversi;
- controllo costi;
- cache;
- code di lavoro.

## Modelli logici

La piattaforma non deve dipendere da un solo modello.

I ruoli devono essere separati:

- modello per sinossi;
- modello per riassunto lungo;
- modello per estrazione concetti;
- modello per domande studio;
- modello per test;
- modello per revisione qualità;
- modello per riscrittura finale.

## Requisiti enterprise

La versione server deve includere:

- backend API;
- autenticazione utenti;
- gestione documenti;
- cache dei chunk;
- job asincroni;
- avanzamento lavorazione;
- salvataggio parziale;
- controllo costi;
- logging;
- quality gate;
- download output;
- possibile integrazione con storage cloud;
- configurazione provider AI.

## Stato attuale del progetto

Il progetto possiede già una base importante:

- interfaccia RAG;
- caricamento documenti;
- motori browser;
- riconoscimento tipo documento;
- generazione card;
- riassunti sperimentali;
- test;
- domande studio;
- PDF/export;
- confronti modelli locali.

La parte da migliorare non è l'idea del progetto, ma il motore AI finale e l'architettura server.

## Strategia successiva

1. Fermare le patch sperimentali sul browser.
2. Salvare i risultati utili dei test Ollama.
3. Separare versione locale concept e versione enterprise.
4. Creare interfaccia provider AI.
5. Preparare backend server.
6. Collegare in futuro API AI professionali.
7. Mantenere Ollama solo come modalità demo/offline.
