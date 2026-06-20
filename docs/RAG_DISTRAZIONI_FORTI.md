# Rafforzamento distrattori RAG

Questo aggiornamento rende più severo il prompt usato dal RAG per generare quiz.

## Problema emerso dal test reale

Il primo test con Ollama ha generato domande formalmente valide, ma il filtro review ha segnalato che i distrattori erano troppo lontani dalla risposta corretta.

## Correzione

Il prompt ora richiede che ogni domanda abbia:

- 1 risposta corretta
- 3 distrattori forti
- distrattori vicini alla risposta corretta
- distrattori sbagliati per un dettaglio preciso
- opzioni simili per lunghezza, stile e livello tecnico

## Regola

Un buon distrattore non deve essere assurdo.
Deve sembrare plausibile, ma deve contenere un errore specifico.

## Esempio

Risposta corretta:
Il backup serve a recuperare dati dopo perdita, guasto o attacco ransomware.

Distrattore forte:
Il backup serve a recuperare dati dopo un ransomware, ma solo se rimane sempre collegato alla stessa rete principale.

Questo distrattore è vicino al tema, ma sbagliato perché un backup sempre collegato alla stessa rete può essere colpito dal ransomware.
