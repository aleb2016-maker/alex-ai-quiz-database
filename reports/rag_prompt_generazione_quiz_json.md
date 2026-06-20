Sei un generatore professionale di quiz formativi.

Devi creare un file JSON basato SOLO sul contesto RAG fornito.

OBIETTIVO:
Generare 3 domande per un quiz riutilizzabile.

DATI QUIZ:
- argomento: motore RAG riutilizzabile
- categoria: ai
- livello: intermedio

REGOLE OBBLIGATORIE:
- usa solo informazioni presenti nel contesto RAG
- non inventare contenuti esterni
- ogni domanda deve avere 4 opzioni
- 1 opzione corretta
- 3 distrattori forti, plausibili e vicini alla risposta corretta
- le opzioni devono essere simili per lunghezza, stile e livello tecnico
- nessuna opzione deve essere assurda o eliminabile subito
- la spiegazione deve essere chiara, didattica e collegata al contesto
- lingua italiana corretta
- niente markdown fuori dal JSON
- restituisci solo JSON valido

FORMATO JSON OBBLIGATORIO:

{
  "metadati": {
    "origine": "rag",
    "argomento": "motore RAG riutilizzabile",
    "categoria": "ai",
    "livello": "intermedio",
    "numero_domande_richieste": 3
  },
  "domande": [
    {
      "id": "RAG-0001",
      "categoria": "ai",
      "livello": "intermedio",
      "domanda": "Testo della domanda",
      "opzioni": [
        "Risposta corretta",
        "Distrattore forte 1",
        "Distrattore forte 2",
        "Distrattore forte 3"
      ],
      "risposta_corretta": "Risposta corretta",
      "spiegazione": "Spiegazione chiara basata sul contesto RAG.",
      "fonte_rag": "Documento o chunk usato come fonte",
      "regola_distrattori": "tre_distrattori_forti"
    }
  ]
}

CONTESTO RAG:

CONTESTO RAG RECUPERATO DAI DOCUMENTI:

[Fonte 1]
Documento: rag/documenti/ESEMPIO_RAG_PROGETTO.md
Chunk: 1
Punteggio: 0.3026
Testo:
# Esempio documento RAG Il motore RAG del progetto serve a recuperare informazioni dai documenti caricati e a usarle come base per generare contenuti formativi. Un sistema RAG professionale può essere usato per creare quiz, test, mini-corsi, slide, percorsi aziendali, formazione interna e applicazioni educative. Nel progetto quiz, il RAG permette di generare domande partendo da materiale reale, riducendo il rischio di inventare contenuti non presenti nella fonte. Ogni domanda dovrebbe avere una risposta corretta e tre distrattori forti, plausibili e vicini alla risposta corretta. Il sistema può diventare riutilizzabile anche per applicazioni diverse dai quiz, per esempio assistenti formativi, motori di studio, generatori di corsi e strumenti aziendali.