from pathlib import Path
import sys

required = [
    Path('demo-rag/rag-knowledge-extractors-v1.js'),
    Path('demo-rag/rag-knowledge-linked-generator-v1.js'),
    Path('demo-rag/rag-general-validator-v1.js'),
]
errors = []
for path in required:
    if not path.exists():
        errors.append(f'manca {path}')

for path in required:
    if not path.exists():
        continue
    text = path.read_text(encoding='utf-8', errors='ignore')
    low = text.lower()
    # vietata solo la vecchia logica di censura, non i contenuti caricati dall'utente
    for bad in ['testo vietato', 'contenuto vietato', 'forbidden_demo_patterns', 'findforbiddenpattern', 'opzione_censura_errata']:
        if bad in low:
            errors.append(f'{path}: contiene ancora vecchia censura errata: {bad}')

checks = {
    Path('demo-rag/rag-knowledge-linked-generator-v1.js'): [
        'rag-knowledge-linked-generator-v33-final-polish',
        'friendlySubject',
        'isExampleOnlyConcept',
        'dynamicMax = topic === "password" ? 1',
        'cleanTopics = cleanTopics.filter((topic) => !/^generico$/i.test(topic.category));',
        'Quali caratteristiche deve avere una password sicura?',
    ],
    Path('demo-rag/rag-knowledge-extractors-v1.js'): [
        'rag-knowledge-extractors-v33-final-polish',
        'intercettare|verifica sistema',
        'topics = topics.filter((topic) => !/^generico$/i.test(topic.category));',
    ],
    Path('demo-rag/rag-general-validator-v1.js'): [
        'rag-general-validator-v33-final-polish',
        'metodo migliore|hotel aeroporto|intercettare traffico utenti',
    ],
}

for path, needles in checks.items():
    if not path.exists():
        continue
    text = path.read_text(encoding='utf-8', errors='ignore')
    for needle in needles:
        if needle not in text:
            errors.append(f'{path}: manca controllo V3.3: {needle}')

if errors:
    print('ERRORE: verifica qualità V3.3 fallita')
    for error in errors:
        print('-', error)
    sys.exit(1)

print('OK: Qualità RAG V3.3 installata.')
print('OK: nessuna censura contenuto.')
print('OK: filtro Generico, concetti esempio, domande studio e ripetizioni test migliorati.')
print('Pagina test: http://localhost:8000/demo-rag/test-rag-pipeline-intelligente-v1.html')
