# Mini LLM Real Quality Gate V3.9.2

- Stato: **PASS**
- Errori validatore: `nessuno`

## Risultati

- Report brutto bocciato: `FAIL`
- Report pulito accettato: `PASS`

## Errori rilevati nel report brutto

- `answer_1:bad_fragment:# Documento`
- `answer_1:bad_fragment:## Scopo`
- `answer_1:bad_fragment:Documento RAG di test`
- `answer_1:bad_fragment:fonte di prova`
- `quality_summary:bad_fragment:al dominio reale`
- `quality_summary:bad_start:al dominio reale; - errori grammaticali o frasi insolite; - richiesta di password, codici o dati bancari.`
- `brief_summary:bad_fragment:da cui.`
- `brief_summary:bad_fragment:documento non è pensato come`
- `brief_summary:bad_ending:Il documento non è pensato come manuale tecnico avanzato, ma come materiale formativo chiaro da cui.`
- `study_pack_summary:bad_fragment:Documento RAG di test`
- `card_1_title:bad_fragment:al dominio reale`
- `card_1_title:bad_title_start:Al dominio reale - errori`
- `card_1_message:bad_fragment:al dominio reale`
- `card_1_message:bad_fragment:codici o dati.`
- `card_1_message:bad_start:al dominio reale; - errori grammaticali o frasi insolite; - richiesta di password, codici o dati.`
- `qa_1_question:bad_question_pattern:^Che cosa usa non riguarda:Che cosa usa non riguarda solo gli esperti informatici: ogni persona che?`
- `test_1_question:question_too_long:Che cosa può fare il documento non è pensato come manuale tecnico avanzato, ma come materiale formativo chiaro da cui un sistema RAG?`
- `test_1_question:bad_question_pattern:^Che cosa può fare il documento non:Che cosa può fare il documento non è pensato come manuale tecnico avanzato, ma come materiale formativo chiaro da cui un sistema RAG?`
- `test_1_question:bad_fragment:documento non è pensato come`
- `test_1_option_1:bad_fragment:al dominio reale`
- `test_1_option_1:bad_option_start:al dominio reale; - errori grammaticali o frasi insolite.`
- `test_1_option_2:bad_fragment:da cui.`
- `test_1_option_2:bad_fragment:documento non è pensato come`
- `test_1_option_2:truncated_option:Il documento non è pensato come manuale tecnico avanzato, ma come materiale formativo chiaro da cui.`
- `test_1_option_2:bad_option_ending:Il documento non è pensato come manuale tecnico avanzato, ma come materiale formativo chiaro da cui.`

## Cosa blocca

- Heading Markdown dentro output.
- Frammenti da elenco.
- Domande innaturali.
- Opzioni troncate.
- Metadati del documento usati come contenuto.

## Cosa non blocca più per errore

- Titoli card brevi e validi come `Sicurezza informatica`.
- Titoli card brevi e validi come `Backup regolari`.

## Limiti

- Gate diagnostico.
- Non è ancora un generatore migliore.
- Il prossimo step sarà collegarlo al test pratico reale come requisito obbligatorio.
