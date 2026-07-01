# Report Knowledge Dataset Builder V1

## Manifest
{
  "versione": "knowledge_dataset_builder_v1",
  "source_path": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/output/knowledge_engine_v14_semantic_output.json",
  "outputs": {
    "full": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/training/knowledge_dataset_v1.jsonl",
    "train": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/training/knowledge_dataset_v1_train.jsonl",
    "val": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/training/knowledge_dataset_v1_val.jsonl",
    "test": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/training/knowledge_dataset_v1_test.jsonl"
  },
  "counts": {
    "total_records": 144,
    "train_records": 116,
    "val_records": 14,
    "test_records": 14
  },
  "tasks": {
    "classificazione_documento": 1,
    "estrazione_aree_operative": 1,
    "normalizzazione_area_operativa": 14,
    "domanda_su_area_operativa": 14,
    "micro_informazione_operativa": 24,
    "riscrittura_per_riassunto": 24,
    "qa_micro_informazione": 24,
    "frase_rilevante": 10,
    "domanda_risposta_operativa": 10,
    "riassunto_frase_rilevante": 10,
    "relazione_operativa": 3,
    "training_item_originale_v14": 9
  },
  "format": "jsonl",
  "language": "it",
  "status": "generated"
}

## Esempi record
### ke-dataset-v1-00001 - classificazione_documento

**Istruzione:** Riconosci la categoria operativa del documento.

**Input:** Documento analizzato dal Knowledge Engine.

**Output:** documento_aziendale

---
### ke-dataset-v1-00002 - estrazione_aree_operative

**Istruzione:** Elenca le aree operative principali del documento.

**Input:** Categoria documento: documento_aziendale

**Output:** sicurezza informatica, password sicure, password manager, protezione dei dati, dati sensibili, autenticazione a due fattori, codici temporanei, account online, account amministrativi, phishing, malware, ransomware, backup regolari, aggiornamenti software

---
### ke-dataset-v1-00003 - normalizzazione_area_operativa

**Istruzione:** Trasforma l'area operativa in una voce pulita e riutilizzabile.

**Input:** sicurezza informatica

**Output:** sicurezza informatica

---
### ke-dataset-v1-00004 - domanda_su_area_operativa

**Istruzione:** Rispondi in modo sintetico indicando l'area operativa richiesta.

**Input:** Quale area operativa è collegata a: sicurezza informatica?

**Output:** sicurezza informatica

---
### ke-dataset-v1-00005 - normalizzazione_area_operativa

**Istruzione:** Trasforma l'area operativa in una voce pulita e riutilizzabile.

**Input:** password sicure

**Output:** password sicure

---
### ke-dataset-v1-00006 - domanda_su_area_operativa

**Istruzione:** Rispondi in modo sintetico indicando l'area operativa richiesta.

**Input:** Quale area operativa è collegata a: password sicure?

**Output:** password sicure

---
### ke-dataset-v1-00007 - normalizzazione_area_operativa

**Istruzione:** Trasforma l'area operativa in una voce pulita e riutilizzabile.

**Input:** password manager

**Output:** password manager

---
### ke-dataset-v1-00008 - domanda_su_area_operativa

**Istruzione:** Rispondi in modo sintetico indicando l'area operativa richiesta.

**Input:** Quale area operativa è collegata a: password manager?

**Output:** password manager

