from pathlib import Path
import re

errors = []
warnings = []

engine = Path("demo-rag/universal-document-learning-engine.js")
pagina = Path("demo-rag/test-documenti-universale.html")

assert engine.exists(), "Manca demo-rag/universal-document-learning-engine.js"
assert pagina.exists(), "Manca demo-rag/test-documenti-universale.html"

engine_txt = engine.read_text(encoding="utf-8", errors="ignore")
pagina_txt = pagina.read_text(encoding="utf-8", errors="ignore")

motori_reali = {
    "V35B_bridge_qualita": "scripts/rag_bridge_motori_qualita_esistenti_v35b.py",
    "V35C_motore_didattico": "scripts/rag_motore_didattico_riutilizzabile_v35c.py",
    "V35D_motore_test": "scripts/rag_motore_test_riutilizzabile_v35d.py",
    "V35E_orchestratore": "scripts/rag_orchestratore_riutilizzabile_v35e.py",
    "V35F_selezionatore": "scripts/rag_selezionatore_motori_riutilizzabile_v35f.py",
    "V35G_qualita_testuale": "scripts/rag_revisore_qualita_testuale_v35g.py",
    "V35I_naturalezza_antikeyword": "scripts/rag_revisore_naturalezza_antikeyword_v35i.py",
    "V35J_accordo_pronomi": "scripts/rag_revisore_accordo_pronomi_v35j.py",
    "V35K_cleaner_finale": "scripts/rag_cleaner_finale_universale_v35k.py",
    "V35M_lucidatore_linguistico": "scripts/rag_lucidatore_linguistico_universale_v35m.py",
    "V35N_completatore_linguistico": "scripts/rag_completatore_linguistico_probabile_v35n.py",
    "V35O_contesto_semantico": "scripts/rag_contesto_semantico_universale_v35o.py",
}

# 1. I file motore devono esistere.
for nome, file in motori_reali.items():
    if not Path(file).exists():
        errors.append(f"Manca file motore reale {nome}: {file}")

# 2. I 4 pulsanti devono esistere.
# I pulsanti possono avere id diversi; il controllo forte è sulla funzione realmente collegata.
pulsanti_o_funzioni = {
    "riassunto": ["btnRiassunto", "generaRiassunto"],
    "card": ["btnCard", "generaCardVisive"],
    "test": ["btnTest", "generaTest"],
    "domande": ["btnDomande", "btnDomandeStudio", "btnStudio", "generaDomandeStudio"],
}

for azione, possibili in pulsanti_o_funzioni.items():
    if not any(x in pagina_txt or x in engine_txt for x in possibili):
        errors.append(f"Manca pulsante/funzione per {azione}: {possibili}")

# 3. Le funzioni dei pulsanti devono chiamare V2A16 e V2A17.
funzioni = {
    "riassunto": "generaRiassunto",
    "card": "generaCardVisive",
    "test": "generaTest",
    "domande": "generaDomandeStudio",
}

for azione, fn in funzioni.items():
    m = re.search(
        r"function\s+" + re.escape(fn) + r"\s*\([^)]*\)\s*\{(?P<body>.*?)(?=\n\s*function\s+[A-Za-z0-9_$]+\s*\(|\n\s*if\s*\(typeof\s+window|\Z)",
        engine_txt,
        flags=re.S,
    )

    if not m:
        errors.append(f"Non trovo funzione pulsante {fn} per {azione}")
        continue

    body = m.group("body")

    if f'verificaMotoriObbligatoriV2A16("{azione}")' not in body:
        errors.append(f"{fn} non chiama verificaMotoriObbligatoriV2A16({azione})")

    if f'verificaContrattoLinguisticoUniversaleV2A17("{azione}"' not in body:
        errors.append(f"{fn} non chiama verificaContrattoLinguisticoUniversaleV2A17({azione})")

# 4. Collegamento effettivo: non basta nominare il contratto.
# Deve esistere un registro/ponte che collega i motori reali V35 ai pulsanti.
indicatori_collegamento_reale = [
    "REGISTRO_MOTORI_INTELLIGENTI",
    "MOTORI_INTELLIGENTI_UNIVERSALI",
    "eseguiMotoriIntelligenti",
    "motoriEseguiti",
    "__ragMotoriEseguiti",
    "rag_pipeline_unica_ufficiale",
    "rag_orchestratore_riutilizzabile_v35e",
    "rag_selezionatore_motori_riutilizzabile_v35f",
    "rag_revisore_qualita_testuale_v35g",
    "rag_revisore_naturalezza_antikeyword_v35i",
    "rag_revisore_accordo_pronomi_v35j",
    "rag_cleaner_finale_universale_v35k",
    "rag_completatore_linguistico_probabile_v35n",
    "rag_contesto_semantico_universale_v35o",
]

presenti = [x for x in indicatori_collegamento_reale if x in engine_txt or x in pagina_txt]

if not presenti:
    errors.append(
        "Non risulta nessun registro/ponte runtime che esegua davvero i motori V35 dai 4 pulsanti. "
        "Il contratto V2A17 è presente, ma i motori reali non sono ancora collegati in modo dimostrabile."
    )

# 5. Ogni azione deve dichiarare quali motori reali esegue.
azioni_obbligatorie = {
    "riassunto": [
        "V35F", "V35C", "V35G", "V35I", "V35J", "V35K", "V35M", "V35N", "V35O"
    ],
    "card": [
        "V35F", "V35C", "V35G", "V35I", "V35J", "V35K", "V35M", "V35N", "V35O"
    ],
    "test": [
        "V35B", "V35C", "V35D", "V35F", "V35G", "V35I", "V35J", "V35K", "V35M"
    ],
    "domande": [
        "V35F", "V35C", "V35G", "V35I", "V35J", "V35K", "V35M", "V35N", "V35O"
    ],
}

for azione, codici in azioni_obbligatorie.items():
    for codice in codici:
        pattern1 = f'"{azione}"'
        pattern2 = codice
        if pattern1 in engine_txt and pattern2 in engine_txt:
            continue
        warnings.append(f"Non vedo dichiarazione chiara {azione} -> {codice}")



# Controllo diretto del registro runtime V2A18.
required_runtime = [
    "REGISTRO_MOTORI_INTELLIGENTI_UNIVERSALI_V2A18",
    "eseguiMotoriIntelligentiUniversaliV35V2A18",
    "eseguiSingoloMotoreV35V2A18",
    "__ragMotoriEseguitiV2A18",
    "V35B",
    "V35C",
    "V35D",
    "V35E",
    "V35F",
    "V35G",
    "V35I",
    "V35J",
    "V35K",
    "V35M",
    "V35N",
    "V35O",
]

for item in required_runtime:
    if item not in engine_txt:
        errors.append(f"Manca runtime/registro V2A18: {item}")

for azione in ["riassunto", "card", "test", "domande"]:
    call = f'eseguiMotoriIntelligentiUniversaliV35V2A18("{azione}"'
    if call not in engine_txt:
        errors.append(f"Il pulsante {azione} non esegue il registro motori V35 V2A18")

# 6. I controlli quiz devono restare solo nel test.
if 'if (azione === "test" && dati.quiz)' not in engine_txt:
    errors.append("verificaTestSeparatoV2A17 non è limitata chiaramente al solo ramo Test")

# 7. File vecchio V34A vietato.
if Path("demo-rag/rag-quality-summary-cards-v34a.js").exists():
    errors.append("Il vecchio file V34A esiste ancora")

if "rag-quality-summary-cards-v34a.js" in pagina_txt:
    errors.append("La pagina universale contiene ancora riferimento a V34A")

if errors:
    print("ERRORE V2A.18 COLLEGAMENTI EFFETTIVI:")
    for e in errors:
        print("-", e)

    if warnings:
        print("\nAvvisi:")
        for w in warnings[:30]:
            print("-", w)

    raise SystemExit(1)

print("OK V2A.18 COLLEGAMENTI EFFETTIVI:")
print("- i file motore V35 esistono")
print("- i 4 pulsanti esistono")
print("- i 4 pulsanti chiamano V2A16 e V2A17")
print("- esiste un registro/ponte runtime per i motori intelligenti")
print("- V34A non è più presente nella pagina universale")

if warnings:
    print("\nAVVISI DA CONTROLLARE:")
    for w in warnings[:30]:
        print("-", w)
