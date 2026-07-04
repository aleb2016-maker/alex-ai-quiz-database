# Compatibilità motori qualità Fase 5 V1

- Creato: `2026-07-05T00:34:37`
- Difetti input: `1`
- Shape input: `{'is_quiz_list': True, 'question_count': 1, 'option_count': 4, 'correct_markers': 1}`

## backend.main.pulisci_qualita_linguistica_quiz

- Import: `ok`
- Stato compatibilità: `compatible_with_adapter`
- Best adapter: `dict_test_quiz`
- Difetti: `1 -> 1`

| Adapter | Stato | Accepted | Difetti |
|---|---:|---:|---:|
| `direct_list` | `exception` | `False` | `- -> -` |
| `dict_test_quiz` | `unchanged_no_worse` | `True` | `1 -> 1` |
| `dict_quiz` | `unchanged_no_worse` | `True` | `1 -> 1` |
| `dict_tests` | `unchanged_no_worse` | `True` | `1 -> 1` |
| `dict_legacy_questions` | `unchanged_no_worse` | `True` | `1 -> 1` |
| `dict_full_phase5_output` | `unchanged_no_worse` | `True` | `1 -> 1` |

## scripts.rag_motore_didattico_riutilizzabile_v35c.refine_tests

- Import: `ok`
- Stato compatibilità: `not_compatible_yet`

| Adapter | Stato | Accepted | Difetti |
|---|---:|---:|---:|
| `direct_list` | `worsened` | `False` | `1 -> 3` |
| `dict_test_quiz` | `exception` | `False` | `- -> -` |
| `dict_quiz` | `exception` | `False` | `- -> -` |
| `dict_tests` | `exception` | `False` | `- -> -` |
| `dict_legacy_questions` | `exception` | `False` | `- -> -` |
| `dict_full_phase5_output` | `exception` | `False` | `- -> -` |
