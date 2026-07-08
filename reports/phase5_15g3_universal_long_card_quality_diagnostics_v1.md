# FASE 5.15G.3 - Universal long-doc card quality diagnostics

Status: **PASS**

## synthetic_long_business_doc - PASS

- Filepath: `rag/documenti/test_documento_lungo_aziendale_120_pagine.txt`
- Tipo: `manuale_aziendale`
- Words: `93418`; long_doc: `True`; G.3 active: `True`
- Cards before/after: `12` -> `12`; QM cards count: `60`; approved: `True`
- Metrics: traceability `1.0`, generic `0`, template `0`, duplicate `0`, teaching `1.0`, specificity `1.0`, diversity `1.0`
- Defects: `[]`
- Examples:
  - `Riferimento attivita: Verifica trimestrale nella sequenza prevista` — Occorre una verifica trimestrale, una traccia scritta nel registro operativo e una conferma del responsabile di processo.
  - `Riferimento attivita nella sequenza prevista` — CTRL-011-1 rende verificabile il flusso e rende confrontabili i risultati tra reparti, sedi e fornitori.
  - `Continuità operativa: Verifica settimanale nella sequenza prevista` — Occorre una verifica settimanale, una traccia scritta nel registro operativo e una conferma del responsabile di processo.

## real_long_audit_doc - PASS

- Filepath: `reports/audit_effetti_premi_ai_its.md`
- Tipo: `documento_reale`
- Words: `106264`; long_doc: `True`; G.3 active: `True`
- Cards before/after: `12` -> `12`; QM cards count: `60`; approved: `True`
- Metrics: traceability `1.0`, generic `0`, template `0`, duplicate `0`, teaching `1.0`, specificity `1.0`, diversity `1.0`
- Defects: `[]`
- Examples:
  - `Risultati revisione nella sequenza prevista` — L18: `"risposta_corretta": "Perché interagisce con il campo magnetico terrestre e si orienta lungo le sue linee",`.
  - `Revisione domanda nella sequenza prevista` — L27: `"spiegazione": "Sommiamo prima le unità: 5 + 8 = 13, scriviamo 3 e riportiamo 1.
  - `Testo risultati nella sequenza prevista` — L13: `"Perché chiarisce obiettivo e formato, ma rende inutile il controllo finale sulla qualità della risposta",`.

## real_security_doc_if_long - WARNING

- Filepath: `rag/documenti/documento_rag_sicurezza_informatica_aziendale.md`
- Tipo: `documento_tecnico`
- Words: `1673`; long_doc: `False`; G.3 active: `False`
- Cards before/after: `0` -> `8`; QM cards count: `60`; approved: `False`
- Metrics: traceability `None`, generic `None`, template `None`, duplicate `None`, teaching `None`, specificity `None`, diversity `None`
- Defects: `[]`
- Examples:
  - `None` — 
  - `None` — 
  - `None` — 

## inline_school_university_handout - WARNING

- Filepath: `inline://dispensa_scolastica_universitaria`
- Tipo: `dispensa_scolastica_universitaria`
- Words: `602`; long_doc: `False`; G.3 active: `False`
- Cards before/after: `0` -> `8`; QM cards count: `60`; approved: `False`
- Metrics: traceability `None`, generic `None`, template `None`, duplicate `None`, teaching `None`, specificity `None`, diversity `None`
- Defects: `[]`
- Examples:
  - `None` — 
  - `None` — 
  - `None` — 

## inline_story_long_doc - WARNING

- Filepath: `inline://storia_racconto`
- Tipo: `storia_racconto`
- Words: `586`; long_doc: `False`; G.3 active: `False`
- Cards before/after: `0` -> `8`; QM cards count: `60`; approved: `False`
- Metrics: traceability `None`, generic `None`, template `None`, duplicate `None`, teaching `None`, specificity `None`, diversity `None`
- Defects: `[]`
- Examples:
  - `None` — 
  - `None` — 
  - `None` — 

## inline_technical_long_doc - WARNING

- Filepath: `inline://documento_tecnico`
- Tipo: `documento_tecnico`
- Words: `587`; long_doc: `False`; G.3 active: `False`
- Cards before/after: `0` -> `8`; QM cards count: `60`; approved: `False`
- Metrics: traceability `None`, generic `None`, template `None`, duplicate `None`, teaching `None`, specificity `None`, diversity `None`
- Defects: `[]`
- Examples:
  - `None` — 
  - `None` — 
  - `None` —
