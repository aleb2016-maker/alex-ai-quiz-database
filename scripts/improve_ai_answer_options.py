import json
from pathlib import Path


PERCORSO_DATA = Path("data")
PERCORSO_BATCH = Path("data/espansione/batch_100.json")
PERCORSO_SCRIPT_BATCH = Path("scripts/create_batch_100.py")


CORREZIONI_AI = {
    "AI-FAC-0001": {
        "opzioni": [
            "Prevedere e generare testo in base al contesto ricevuto",
            "Classificare testi in categorie fisse senza produrre nuove frasi",
            "Recuperare documenti esterni senza generare una risposta autonoma",
            "Tradurre parole usando solo un dizionario statico"
        ],
        "risposta_corretta": "Prevedere e generare testo in base al contesto ricevuto",
        "spiegazione": (
            "Un LLM lavora principalmente prevedendo e generando testo coerente con il contesto ricevuto. "
            "Può anche aiutare in classificazione, traduzione o recupero informazioni, ma il suo ruolo centrale è generare linguaggio naturale, "
            "non limitarsi a una singola funzione rigida."
        )
    },

    "AI-AV-0003": {
        "opzioni": [
            "A recuperare informazioni da fonti esterne e usarle per generare risposte più fondate",
            "A riaddestrare il modello sui documenti recuperati prima di ogni risposta",
            "A cercare documenti simili senza passarli al modello durante la generazione",
            "A sostituire il ragionamento del modello con una semplice ricerca per parole chiave"
        ],
        "risposta_corretta": "A recuperare informazioni da fonti esterne e usarle per generare risposte più fondate",
        "spiegazione": (
            "Un sistema RAG recupera informazioni da fonti esterne e le usa come contesto per generare risposte più fondate. "
            "Non riaddestra il modello a ogni domanda e non si limita a cercare parole chiave: il recupero deve servire davvero alla generazione della risposta."
        )
    },

    "AI-FAC-0007": {
        "opzioni": [
            "Lavora con il linguaggio per comprendere o generare testo",
            "Classifica contenuti testuali senza produrre nuove frasi",
            "Recupera pagine web pertinenti senza formulare una risposta",
            "Analizza solo dati numerici organizzati in tabelle"
        ],
        "risposta_corretta": "Lavora con il linguaggio per comprendere o generare testo",
        "spiegazione": (
            "Un modello linguistico lavora con il linguaggio naturale: può comprendere, completare, riassumere o generare testo. "
            "Le altre opzioni descrivono attività possibili nell'AI o nell'informatica, ma sono più limitate e non rappresentano il ruolo principale di un modello linguistico."
        )
    },

    "AI-INT-0002": {
        "opzioni": [
            "Perché fornisce più contesto e riduce le ambiguità della richiesta",
            "Perché modifica i parametri interni del modello durante la risposta",
            "Perché sostituisce il controllo finale sulla qualità della risposta",
            "Perché obbliga il modello a copiare solo frasi presenti nel prompt"
        ],
        "risposta_corretta": "Perché fornisce più contesto e riduce le ambiguità della richiesta",
        "spiegazione": (
            "Un prompt dettagliato aiuta perché chiarisce obiettivo, contesto, vincoli e formato desiderato. "
            "Non cambia i parametri interni del modello e non sostituisce il controllo finale: semplicemente riduce l'ambiguità della richiesta."
        )
    },

    "AI-INT-0005": {
        "opzioni": [
            "A rappresentare testi, immagini o dati come vettori confrontabili",
            "A recuperare documenti usando solo parole identiche alla domanda",
            "A generare direttamente una risposta senza confronto semantico",
            "A salvare il contenuto originale senza trasformarlo in rappresentazione numerica"
        ],
        "risposta_corretta": "A rappresentare testi, immagini o dati come vettori confrontabili",
        "spiegazione": (
            "Un embedding trasforma un contenuto in un vettore numerico, così contenuti simili possono essere confrontati anche se usano parole diverse. "
            "Non è una risposta finale e non è una semplice ricerca per parole identiche."
        )
    },

    "AI-INT-0006": {
        "opzioni": [
            "Per verificare se il modello generalizza anche su casi nuovi",
            "Per misurare quanto il modello ripete i dati già visti in addestramento",
            "Per scegliere nuovi esempi da aggiungere al training set",
            "Per controllare solo la velocità di risposta senza valutare l'accuratezza"
        ],
        "risposta_corretta": "Per verificare se il modello generalizza anche su casi nuovi",
        "spiegazione": (
            "Testare un modello su esempi diversi da quelli usati in addestramento serve a capire se generalizza su casi nuovi. "
            "Se funziona bene solo sui dati già visti, potrebbe aver memorizzato troppo il training set invece di imparare regole utili."
        )
    },

    "AI-INT-0008": {
        "opzioni": [
            "Il modello può imparare a favorire quella classe nelle previsioni",
            "Il modello può imparare automaticamente un peso identico per tutte le classi",
            "Il modello può migliorare sulle classi rare senza esempi sufficienti",
            "Il modello può rendere inutile ogni metrica diversa dall'accuratezza"
        ],
        "risposta_corretta": "Il modello può imparare a favorire quella classe nelle previsioni",
        "spiegazione": (
            "Se una classe è molto più presente delle altre, il modello può imparare a prevederla troppo spesso. "
            "Questo può dare un risultato apparentemente buono, ma peggiorare il riconoscimento delle classi meno rappresentate."
        )
    },

    "AI-INT-0009": {
        "opzioni": [
            "Uno strumento esterno che l'agente può usare per compiere un'azione",
            "Una memoria conversazionale che conserva informazioni tra più messaggi",
            "Un'istruzione di sistema che definisce il comportamento dell'agente",
            "Un modello linguistico usato per scegliere la risposta finale"
        ],
        "risposta_corretta": "Uno strumento esterno che l'agente può usare per compiere un'azione",
        "spiegazione": (
            "In un agente AI, un tool è uno strumento esterno che permette di compiere azioni, per esempio cercare dati, leggere file, chiamare API o fare calcoli. "
            "Memoria, istruzioni di sistema e modello linguistico sono componenti importanti, ma non sono tool."
        )
    },

    "AI-AV-0005": {
        "opzioni": [
            "Perché alcune risposte richiedono giudizi su completezza, coerenza, sicurezza e utilità",
            "Perché una risposta può essere corretta nei fatti ma incompleta rispetto alla richiesta",
            "Perché una risposta può rispettare il formato ma non essere abbastanza utile",
            "Perché una risposta può essere fluida ma contenere passaggi non verificati"
        ],
        "risposta_corretta": "Perché alcune risposte richiedono giudizi su completezza, coerenza, sicurezza e utilità",
        "spiegazione": (
            "Nei compiti generativi non basta sempre distinguere tra corretto e sbagliato. "
            "Una risposta può essere parzialmente corretta, incompleta, poco sicura, fuori contesto o poco utile. "
            "Per questo servono criteri più ricchi, come completezza, coerenza, sicurezza e utilità."
        )
    },

    "AI-AV-0006": {
        "opzioni": [
            "Il modello può essere spinto a ignorare istruzioni originali e usare strumenti in modo non previsto",
            "Il modello può ricevere istruzioni esterne che entrano in conflitto con quelle dell'applicazione",
            "Il modello può confondere contenuto dell'utente e istruzioni operative del sistema",
            "Il modello può usare informazioni recuperate come se fossero comandi da seguire"
        ],
        "risposta_corretta": "Il modello può essere spinto a ignorare istruzioni originali e usare strumenti in modo non previsto",
        "spiegazione": (
            "Una prompt injection tenta di manipolare il comportamento del modello, facendogli trattare contenuti esterni come istruzioni. "
            "Il rischio principale, soprattutto con tool esterni, è che il modello ignori le istruzioni originali e compia azioni non previste."
        )
    },

    "AI-AV-0008": {
        "opzioni": [
            "Per rendere più controllabile ogni fase e individuare meglio dove nasce un errore",
            "Per valutare separatamente se il problema nasce dal recupero dei documenti",
            "Per controllare se la generazione usa correttamente il contesto recuperato",
            "Per verificare se il controllo finale intercetta risposte deboli o rischiose"
        ],
        "risposta_corretta": "Per rendere più controllabile ogni fase e individuare meglio dove nasce un errore",
        "spiegazione": (
            "Separare recupero, generazione e controllo finale rende la pipeline più osservabile e più facile da correggere. "
            "Le altre opzioni descrivono vantaggi specifici della separazione, ma la risposta corretta è quella più completa: controllare ogni fase e capire dove nasce l'errore."
        )
    },

    "AI-AV-0009": {
        "opzioni": [
            "Perché i dati, gli obiettivi di addestramento o le metriche possono introdurre distorsioni",
            "Perché dati sbilanciati possono portare il modello a favorire certi gruppi o classi",
            "Perché una metrica scelta male può premiare comportamenti non desiderati",
            "Perché l'obiettivo di addestramento può non rappresentare bene l'uso reale"
        ],
        "risposta_corretta": "Perché i dati, gli obiettivi di addestramento o le metriche possono introdurre distorsioni",
        "spiegazione": (
            "Un modello può essere implementato correttamente ma produrre risultati distorti se dati, obiettivi o metriche sono sbilanciati. "
            "Le altre opzioni descrivono casi specifici, mentre la risposta corretta riassume il motivo generale."
        )
    }
}


def carica_json(percorso):
    with open(percorso, "r", encoding="utf-8") as file:
        return json.load(file)


def salva_json(percorso, contenuto):
    with open(percorso, "w", encoding="utf-8") as file:
        json.dump(
            contenuto,
            file,
            ensure_ascii=False,
            indent=2
        )


def aggiorna_file_json(percorso):
    domande = carica_json(percorso)

    modifiche = 0

    for domanda in domande:
        id_domanda = domanda.get("id")

        if id_domanda in CORREZIONI_AI:
            correzione = CORREZIONI_AI[id_domanda]

            domanda["opzioni"] = correzione["opzioni"]
            domanda["risposta_corretta"] = correzione["risposta_corretta"]
            domanda["spiegazione"] = correzione["spiegazione"]

            modifiche += 1

    if modifiche > 0:
        salva_json(percorso, domande)

    return modifiche


def aggiorna_script_create_batch():
    if not PERCORSO_BATCH.exists():
        return

    domande_batch = carica_json(PERCORSO_BATCH)

    contenuto_lista = json.dumps(
        domande_batch,
        ensure_ascii=False,
        indent=4
    )

    nuovo_contenuto = f'''import json
from pathlib import Path


# Questo script crea il primo batch di espansione.
# Obiettivo: portare il database da 27 a 100 domande totali.
# Le nuove domande vengono salvate in data/espansione/batch_100.json


PERCORSO_OUTPUT = Path("data/espansione/batch_100.json")


nuove_domande = {contenuto_lista}


def main():
    PERCORSO_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with open(PERCORSO_OUTPUT, "w", encoding="utf-8") as file:
        json.dump(
            nuove_domande,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("File creato correttamente:")
    print(PERCORSO_OUTPUT)
    print(f"Domande create: {{len(nuove_domande)}}")


main()
'''

    PERCORSO_SCRIPT_BATCH.write_text(nuovo_contenuto, encoding="utf-8")


def main():
    modifiche_totali = 0

    for percorso in sorted(PERCORSO_DATA.rglob("*.json")):
        modifiche_file = aggiorna_file_json(percorso)

        if modifiche_file > 0:
            modifiche_totali += modifiche_file
            print(f"Aggiornato {percorso}: {modifiche_file} domande")

    aggiorna_script_create_batch()

    print()
    print("Revisione AI completata.")
    print(f"Domande AI aggiornate: {modifiche_totali}")


main()