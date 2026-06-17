import json
from pathlib import Path

FILE_AI = Path("data/ai.json")
BACKUP = Path("data/ai.backup_prima_secondo_blocco_distrattori_forti.json")
REPORT = Path("reports/migliora_ai_secondo_blocco_distrattori_forti.md")

PATCH = {
    "AI-AV-0008": {
        "opzioni": [
            "Per rendere più controllabile ogni fase e individuare meglio dove nasce un errore",
            "Per rendere più controllabile ogni fase, ma correggendo gli errori soltanto alla fine della pipeline",
            "Per separare recupero, generazione e verifica, ma trattando ogni fase come indipendente dalle altre",
            "Per distinguere retrieval, generazione e controllo, ma usando il controllo finale principalmente per salvare la risposta prodotta"
        ],
        "spiegazione": (
            "Separare recupero, generazione e controllo finale rende la pipeline più osservabile e permette di capire meglio dove nasce un errore. "
            "Non basta correggere alla fine, perché un errore nel recupero può influenzare la generazione; inoltre le fasi non sono indipendenti e il controllo finale non serve solo a salvare la risposta."
        )
    },

    "AI-FAC-0201": {
        "opzioni": [
            "Un sistema capace di produrre nuovi contenuti, come testo, immagini o codice, partendo da dati e istruzioni",
            "Un sistema capace di produrre contenuti nuovi, ma limitato a ricombinare esempi già presenti senza adattarsi davvero all'istruzione",
            "Un sistema che genera testo, immagini o codice partendo da istruzioni, ma senza usare pattern appresi dai dati",
            "Un sistema che produce contenuti a partire da dati e istruzioni, ma con risposte fissate prima dello specifico input dell'utente"
        ],
        "spiegazione": (
            "Un modello di AI generativa produce nuovi contenuti a partire da dati, istruzioni e pattern appresi. "
            "Non si limita a ricombinare esempi già presenti, non genera senza usare ciò che ha appreso dai dati e non usa risposte fissate prima dello specifico input."
        )
    },

    "AI-AV-0211": {
        "opzioni": [
            "Per limitare comportamenti rischiosi, applicare regole e gestire richieste non adatte",
            "Per limitare comportamenti rischiosi, ma applicando le regole dopo che la risposta è già stata mostrata all'utente",
            "Per applicare regole di sicurezza, ma senza distinguere tra richieste lecite, ambigue e non adatte",
            "Per gestire richieste non adatte, ma sostituendo la progettazione del comportamento con un blocco generico"
        ],
        "spiegazione": (
            "Le guardrail servono a limitare comportamenti rischiosi, applicare regole e gestire richieste non adatte prima o durante la produzione della risposta. "
            "Non devono intervenire solo dopo la risposta, non devono bloccare senza distinguere il tipo di richiesta e non sostituiscono una buona progettazione del sistema."
        )
    },

    "AI-FAC-0001": {
        "opzioni": [
            "Prevedere e generare testo in base al contesto ricevuto",
            "Prevedere testo in base al contesto, ma scegliendo la continuazione più frequente senza adattarsi al significato della richiesta",
            "Generare testo coerente con il contesto, ma funzionando come un archivio di frasi già salvate",
            "Comprendere e produrre linguaggio naturale, ma usando il recupero di documenti come meccanismo principale di generazione"
        ],
        "spiegazione": (
            "Un LLM prevede e genera testo in base al contesto ricevuto, producendo linguaggio naturale coerente con la richiesta. "
            "Non sceglie semplicemente la continuazione più frequente, non funziona come archivio di frasi già salvate e non coincide con un sistema di recupero documentale."
        )
    },

    "AI-FAC-0007": {
        "opzioni": [
            "Lavora con il linguaggio per comprendere o generare testo",
            "Lavora con il linguaggio per generare testo, ma senza tenere conto del contesto fornito dall'utente",
            "Elabora testo naturale, ma lo usa principalmente per assegnare etichette fisse invece di generare risposte",
            "Comprende e produce testo, ma basandosi su un elenco statico di regole scritte a mano"
        ],
        "spiegazione": (
            "Un modello linguistico lavora con il linguaggio naturale per comprendere, completare, riassumere o generare testo. "
            "Non ignora il contesto, non è principalmente un classificatore a etichette fisse e non si basa solo su regole statiche scritte a mano."
        )
    },

    "AI-FAC-0206": {
        "opzioni": [
            "Unità di testo, come parole o parti di parole, che il modello usa per elaborare il linguaggio",
            "Unità di testo usate dal modello, ma trattate come parole intere senza suddivisioni interne",
            "Parti di testo convertite in elementi gestibili dal modello, ma usate per valutare direttamente la qualità della risposta",
            "Segmenti di linguaggio elaborati dal modello, ma creati dopo la generazione per correggere il testo finale"
        ],
        "spiegazione": (
            "I token sono unità di testo, come parole o parti di parole, che il modello usa per elaborare il linguaggio. "
            "Non corrispondono necessariamente a parole intere, non sono punteggi di qualità e non vengono creati dopo la generazione per correggere il testo."
        )
    },

    "AI-FAC-0209": {
        "opzioni": [
            "A rappresentare testi, immagini o altri dati come vettori numerici confrontabili",
            "A rappresentare testi, immagini o dati come vettori confrontabili quando condividono parole o caratteristiche identiche",
            "A trasformare contenuti in vettori numerici confrontabili, ma usandoli principalmente come compressione dei dati",
            "A creare vettori per confrontare contenuti, ma senza conservare relazioni di vicinanza semantica tra elementi simili"
        ],
        "spiegazione": (
            "Gli embedding rappresentano testi, immagini o altri dati come vettori numerici confrontabili, così contenuti simili possono risultare vicini anche senza parole identiche. "
            "Non servono principalmente a comprimere dati e non eliminano le relazioni semantiche: quelle relazioni sono una parte centrale della loro utilità."
        )
    },

    "AI-INT-0201": {
        "opzioni": [
            "Può recuperare informazioni da fonti esterne e usarle per rendere la risposta più ancorata ai dati disponibili",
            "Può recuperare informazioni esterne e usarle nel contesto, ma addestrando di nuovo il modello sul dominio a ogni richiesta",
            "Può ancorare la risposta a fonti disponibili, ma senza verificare se le fonti recuperate sono davvero pertinenti",
            "Può combinare recupero e generazione, ma sostituisce la valutazione della risposta con la semplice presenza di documenti"
        ],
        "spiegazione": (
            "Una pipeline RAG recupera informazioni da fonti esterne e le usa per rendere la risposta più ancorata ai dati disponibili. "
            "Non riaddestra il modello a ogni richiesta, non basta recuperare fonti senza verificarne la pertinenza e la presenza di documenti non sostituisce la valutazione della risposta."
        )
    },

    "AI-INT-0209": {
        "opzioni": [
            "Per misurare il comportamento del modello su esempi non usati direttamente per addestrarlo",
            "Per misurare il comportamento su esempi separati, ma scegliendoli tra casi troppo simili a quelli già appresi",
            "Per stimare la generalizzazione del modello, ma aggiornando il training set con gli errori durante la valutazione",
            "Per valutare il modello su dati separati, ma senza confrontare le previsioni con risultati attesi o metriche definite"
        ],
        "spiegazione": (
            "Un set di valutazione separato serve a misurare il comportamento del modello su esempi non usati direttamente per addestrarlo. "
            "Se gli esempi sono troppo simili a quelli già appresi, se la valutazione modifica il training set o se mancano risultati attesi e metriche, la stima della generalizzazione diventa meno affidabile."
        )
    },

    "AI-AV-0201": {
        "opzioni": [
            "Pesare l'importanza relativa di diverse parti della sequenza durante l'elaborazione",
            "Pesare parti della sequenza, ma mantenendo quasi lo stesso peso per token con ruoli diversi",
            "Individuare relazioni tra token della sequenza, ma usando una posizione fissa invece del contenuto corrente",
            "Dare contesto alla generazione, ma dopo aver ridotto la sequenza a un riassunto unico non confrontabile"
        ],
        "spiegazione": (
            "Il meccanismo di attention pesa l'importanza relativa di diverse parti della sequenza durante l'elaborazione. "
            "Non assegna lo stesso peso a token con ruoli diversi, non usa solo una posizione fissa e non riduce la sequenza a un unico riassunto prima di considerare le relazioni tra token."
        )
    },

    "AI-AV-0202": {
        "opzioni": [
            "La quantità massima di token che il modello può considerare in una singola interazione",
            "La quantità di token gestibile dal modello, ma riferita al prompt iniziale ed escludendo la risposta generata",
            "Il limite di contesto usabile in una conversazione, ma espresso come numero di frasi invece che di token",
            "La porzione di testo che il modello considera, ma ampliabile durante la stessa richiesta senza vincoli tecnici"
        ],
        "spiegazione": (
            "La finestra di contesto indica la quantità massima di token che il modello può considerare in una singola interazione, includendo il contesto utile per produrre la risposta. "
            "Non riguarda solo il prompt iniziale, non si misura semplicemente in frasi e non può essere ampliata senza vincoli tecnici durante la stessa richiesta."
        )
    },

    "AI-AV-0203": {
        "opzioni": [
            "Permette di addestrare piccoli adattatori a basso rango invece di aggiornare tutti i pesi del modello",
            "Permette di addestrare adattatori leggeri, ma richiede comunque l'aggiornamento completo dei pesi principali del modello",
            "Riduce il costo del fine-tuning usando moduli aggiuntivi, ma elimina il bisogno di esempi specifici del dominio",
            "Usa componenti a basso rango per adattare il modello, ma cambia l'architettura base del Transformer a ogni addestramento"
        ],
        "spiegazione": (
            "LoRA è utile perché permette di addestrare piccoli adattatori a basso rango invece di aggiornare tutti i pesi del modello. "
            "Non richiede l'aggiornamento completo dei pesi principali, non elimina il bisogno di dati specifici e non cambia l'architettura base del Transformer a ogni addestramento."
        )
    }
}


def carica_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def salva_json(path, contenuto):
    path.write_text(
        json.dumps(contenuto, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def estrai_domande(contenuto):
    if isinstance(contenuto, list):
        return contenuto

    for chiave in ["domande", "questions", "quiz", "items"]:
        if isinstance(contenuto.get(chiave), list):
            return contenuto[chiave]

    raise ValueError("Formato JSON non riconosciuto: non trovo la lista delle domande.")


def aggiorna_opzioni(domanda, nuove_opzioni):
    for chiave in ["opzioni", "options", "risposte", "answers"]:
        if chiave in domanda:
            domanda[chiave] = nuove_opzioni
            return

    domanda["opzioni"] = nuove_opzioni


def aggiorna_risposta_corretta(domanda, testo_corretta):
    for chiave in ["risposta_corretta", "correct_answer", "correct", "answer", "soluzione"]:
        if chiave in domanda:
            valore = str(domanda.get(chiave, "")).strip().upper()

            if valore in ["A", "B", "C", "D"]:
                domanda[chiave] = "A"
            else:
                domanda[chiave] = testo_corretta

            return

    domanda["risposta_corretta"] = testo_corretta


def main():
    if not FILE_AI.exists():
        raise SystemExit("ERRORE: data/ai.json non trovato.")

    if not BACKUP.exists():
        BACKUP.write_text(FILE_AI.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Backup creato: {BACKUP}")
    else:
        print(f"Backup già presente: {BACKUP}")

    contenuto = carica_json(FILE_AI)
    domande = estrai_domande(contenuto)

    indice_per_id = {
        str(domanda.get("id", "")).strip(): domanda
        for domanda in domande
    }

    aggiornate = []
    non_trovate = []

    for id_domanda, dati in PATCH.items():
        domanda = indice_per_id.get(id_domanda)

        if domanda is None:
            non_trovate.append(id_domanda)
            continue

        nuove_opzioni = dati["opzioni"]

        aggiorna_opzioni(domanda, nuove_opzioni)
        aggiorna_risposta_corretta(domanda, nuove_opzioni[0])
        domanda["spiegazione"] = dati["spiegazione"]
        domanda["regola_distrattori"] = "tre_distrattori_forti"
        domanda["criterio_distrattori"] = (
            "Ogni risposta errata deve condividere il concetto centrale della corretta "
            "e diventare sbagliata per un dettaglio tecnico, logico o pratico."
        )

        aggiornate.append(id_domanda)

    salva_json(FILE_AI, contenuto)

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    righe = []
    righe.append("# Miglioramento AI - secondo blocco distrattori forti")
    righe.append("")
    righe.append("Regola applicata: 1 risposta corretta + 3 distrattori forti.")
    righe.append("")
    righe.append("Metodo: stessa area concettuale della risposta corretta, ma errore preciso in un dettaglio.")
    righe.append("")
    righe.append(f"Domande aggiornate: {len(aggiornate)}")
    righe.append("")

    for id_domanda in aggiornate:
        righe.append(f"- {id_domanda}")

    if non_trovate:
        righe.append("")
        righe.append("## ID non trovati")
        righe.append("")
        for id_domanda in non_trovate:
            righe.append(f"- {id_domanda}")

    REPORT.write_text("\n".join(righe), encoding="utf-8")

    print("===== MIGLIORAMENTO AI - SECONDO BLOCCO =====")
    print(f"Domande aggiornate: {len(aggiornate)}")

    for id_domanda in aggiornate:
        print(f"- {id_domanda}")

    if non_trovate:
        print()
        print("ID non trovati:")
        for id_domanda in non_trovate:
            print(f"- {id_domanda}")

    print()
    print(f"Report creato: {REPORT}")
    print("OK: secondo blocco AI aggiornato con tre distrattori forti.")


if __name__ == "__main__":
    main()
